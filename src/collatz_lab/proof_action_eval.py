"""Evaluate proof-action checkpoints with constrained decoding and verifier gates."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

import torch
from rich.console import Console

from .proof_action_decode import (
    is_degenerate_output,
    legal_action_candidates_from_state,
    verify_action_for_state,
)
from .proof_action_model import greedy_generate_action_text, load_checkpoint
from .proof_action_dsl import parse_action, serialize_action
from .proof_action_outcome import (
    VERIFIER_ACCEPTED_GATE_PROGRESS,
    VERIFIER_ACCEPTED_REDUCED,
    classify_action_outcome,
)
from .proof_action_search import rank_candidate_actions, ranking_weights_from_config
from .proof_verifier import build_collatz_descent_theorem_candidate
from .run_result import ProofScore, RunResult, save_run_result, utc_stamp, write_run_result_markdown
from .utils import load_yaml


PROOF_ACTION_EVAL_SCHEMA = "collatz_lab.proof_action_eval_summary"


def _load_rows(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _eval_config(path: str | Path) -> dict[str, Any]:
    cfg = load_yaml(path)
    data = cfg.get("data", {})
    output = cfg.get("output", {})
    evaluation = cfg.get("evaluation", {})
    search = cfg.get("search", {})
    rows = str(data.get("rows") or data.get("dataset") or Path(data.get("dir", "data/proof_action_v2")) / "rows.jsonl")
    output_dir = str(output.get("dir") or cfg.get("output_dir") or "reports/proof_action_v2/run")
    checkpoint = str(evaluation.get("checkpoint") or Path(output_dir) / "final_checkpoint.pt")
    return {
        "rows": rows,
        "output_dir": output_dir,
        "checkpoint": checkpoint,
        "splits": tuple(evaluation.get("splits", ["val", "test", "challenge"])),
        "max_examples": int(evaluation.get("max_examples", 512)),
        "beam_size": int(evaluation.get("beam_size", search.get("beam_width", search.get("beam_size", 20)))),
        "candidates_per_state": int(
            evaluation.get("candidates_per_state", search.get("candidates_per_state", evaluation.get("beam_size", 20)))
        ),
        "top_k": int(evaluation.get("top_k", 5)),
        "seed": int((cfg.get("training") or {}).get("seed", 1337)),
        "use_action_memory": bool(evaluation.get("use_action_memory", False)),
        "run_id": str((cfg.get("run") or {}).get("id", "RUN-010-proof-action-v2-small-a100")),
        "title": str((cfg.get("run") or {}).get("description", "Proof-action v2 evaluation")),
        "config_path": str(path),
        "stratified": bool(evaluation.get("stratified", cfg.get("eval", {}).get("stratified", False))),
        "ranking": ranking_weights_from_config(cfg),
    }


def _select_rows(
    rows: list[dict[str, Any]],
    splits: tuple[str, ...],
    max_examples: int,
    seed: int,
    *,
    stratified: bool = False,
) -> list[dict[str, Any]]:
    selected = [row for row in rows if row.get("split") in splits and row.get("verifier_status") == "ACCEPT"]
    if not selected:
        selected = [row for row in rows if row.get("verifier_status") == "ACCEPT"] or rows
    rng = random.Random(seed)
    if stratified:
        by_gate: dict[str, list[dict[str, Any]]] = {}
        for row in selected:
            by_gate.setdefault(str(row.get("gate", "UNKNOWN")), []).append(row)
        for gate_rows in by_gate.values():
            rng.shuffle(gate_rows)
        gates = sorted(by_gate)
        quota = max(1, max_examples // max(len(gates), 1))
        out: list[dict[str, Any]] = []
        used: set[str] = set()
        for gate in gates:
            for row in by_gate[gate][:quota]:
                out.append(row)
                used.add(str(row.get("example_id")))
        remainder = [row for row in selected if str(row.get("example_id")) not in used]
        rng.shuffle(remainder)
        out.extend(remainder)
        return out[:max_examples]
    rng.shuffle(selected)
    return selected[:max_examples]


def _percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
    return float(ordered[index])


def _closes_or_reduces(outcome: dict[str, Any]) -> bool:
    return bool(
        outcome.get("closed_obligation")
        or outcome.get("closed_branch")
        or outcome.get("strict_progress")
        or float(outcome.get("gate_progress_delta", 0.0) or 0.0) > 0
        or outcome.get("outcome_class") in {VERIFIER_ACCEPTED_REDUCED, VERIFIER_ACCEPTED_GATE_PROGRESS}
    )


def _bucket(counter: dict[str, dict[str, float]], key: str, *, accepted: bool, close: bool, gate_progress: bool) -> None:
    item = counter.setdefault(key or "UNKNOWN", {"count": 0.0, "accepted": 0.0, "close": 0.0, "gate_progress": 0.0})
    item["count"] += 1.0
    item["accepted"] += 1.0 if accepted else 0.0
    item["close"] += 1.0 if close else 0.0
    item["gate_progress"] += 1.0 if gate_progress else 0.0


def _finalize_buckets(counter: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for key, item in counter.items():
        count = max(item["count"], 1.0)
        out[key] = {
            "count": int(item["count"]),
            "accept_rate": item["accepted"] / count,
            "close_rate": item["close"] / count,
            "gate_progress_rate": item["gate_progress"] / count,
        }
    return out


def evaluate(config_path: str | Path) -> dict[str, Any]:
    cfg = _eval_config(config_path)
    out = Path(cfg["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    rows = _select_rows(
        _load_rows(cfg["rows"]),
        cfg["splits"],
        cfg["max_examples"],
        cfg["seed"],
        stratified=cfg["stratified"],
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, tokenizer, checkpoint = load_checkpoint(cfg["checkpoint"], device=device)
    model_cfg = dict(checkpoint.get("config") or {})
    max_state_len = int(model_cfg.get("max_state_len", 2048))
    max_action_len = int(model_cfg.get("max_action_len", 128))
    action_memory = dict(checkpoint.get("action_memory") or {}) if cfg["use_action_memory"] else {}

    generated_rows: list[dict[str, Any]] = []
    checked_rows: list[dict[str, Any]] = []
    syntax_valid = 0
    parse_valid = 0
    total_candidates = 0
    checked_candidates = 0
    top1_accept = 0
    top5_accept = 0
    top1_close = 0
    top5_close = 0
    top1_gate_progress = 0
    top5_gate_progress = 0
    degenerate = 0
    random_closed = 0
    heuristic_closed = 0
    gate_accepts: Counter[str] = Counter()
    gate_closures: Counter[str] = Counter()
    gate_progress_counts: Counter[str] = Counter()
    unique_counts: list[int] = []
    sample_actions: list[dict[str, Any]] = []
    ranked_rows: list[dict[str, Any]] = []
    stratified: dict[str, dict[str, dict[str, float]]] = {
        "gate": {},
        "outcome": {},
        "source": {},
        "difficulty": {},
        "modulus_bucket": {},
    }

    for index, row in enumerate(rows):
        state = str(row["state"])
        greedy_text = greedy_generate_action_text(
            model,
            tokenizer,
            state,
            max_state_len=max_state_len,
            max_action_len=max_action_len,
        )
        if is_degenerate_output(greedy_text):
            degenerate += 1
        candidates = legal_action_candidates_from_state(state, max_candidates=cfg["beam_size"])
        memory_text = action_memory.get(__import__("hashlib").sha256(state.encode("utf-8")).hexdigest())
        if memory_text:
            try:
                memory_action = parse_action(memory_text)
                candidates = [memory_action] + [candidate for candidate in candidates if serialize_action(candidate) != memory_text]
            except Exception:
                pass
        ranked = rank_candidate_actions(
            model=model,
            tokenizer=tokenizer,
            state=state,
            candidates=candidates,
            max_state_len=max_state_len,
            max_action_len=max_action_len,
            weights=cfg["ranking"],
            max_candidates=cfg["candidates_per_state"],
        )
        total_candidates += len(ranked)
        unique_counts.append(len(ranked))
        top_items = ranked[: max(cfg["top_k"], 1)]
        for rank, item in enumerate(top_items, start=1):
            checked_candidates += 1
            candidate = item["action"]
            text = item["action_text"]
            try:
                parse_action(text)
                syntax_valid += 1
                parse_valid += 1
            except Exception:
                pass
            check = verify_action_for_state(candidate, state)
            outcome = classify_action_outcome(candidate, state, check).to_dict()
            checked = {
                "example_id": row.get("example_id"),
                "split": row.get("split"),
                "gate": row.get("gate"),
                "source": row.get("source"),
                "difficulty": row.get("difficulty"),
                "modulus_bucket": row.get("modulus_bucket"),
                "rank": rank,
                "score": item["score"],
                "model_scores": item["model_scores"],
                "action": candidate,
                "action_text": text,
                "verifier_check": check.to_dict(),
                "outcome": outcome,
                "target_action_text": row.get("target_action_text"),
            }
            checked_rows.append(checked)
            ranked_rows.append(checked)
            if check.accepted:
                gate_accepts[str(row.get("gate", "UNKNOWN"))] += 1
            if _closes_or_reduces(outcome):
                gate_closures[str(row.get("gate", "UNKNOWN"))] += 1
            if float(outcome.get("gate_progress_delta", 0.0) or 0.0) > 0:
                gate_progress_counts[str(row.get("gate", "UNKNOWN"))] += 1
            if len(sample_actions) < 16:
                sample_actions.append(checked)
        top_outcomes = [item["outcome"] for item in ranked[: max(cfg["top_k"], 1)]]
        top_checks = [item["verifier_check"] for item in ranked[: max(cfg["top_k"], 1)]]
        first_check = top_checks[0] if top_checks else {}
        first_outcome = top_outcomes[0] if top_outcomes else {}
        if first_check and first_check.get("accepted"):
            top1_accept += 1
        if any(check.get("accepted") for check in top_checks[:5]):
            top5_accept += 1
        top1_close_hit = _closes_or_reduces(first_outcome) if first_outcome else False
        top5_close_hit = any(_closes_or_reduces(outcome) for outcome in top_outcomes[:5])
        if top1_close_hit:
            top1_close += 1
        if top5_close_hit:
            top5_close += 1
        if float(first_outcome.get("gate_progress_delta", 0.0) or 0.0) > 0:
            top1_gate_progress += 1
        if any(float(outcome.get("gate_progress_delta", 0.0) or 0.0) > 0 for outcome in top_outcomes[:5]):
            top5_gate_progress += 1
        if ranked:
            baseline_item = random.Random(cfg["seed"] + index).choice(ranked)
            if _closes_or_reduces(baseline_item["outcome"]):
                random_closed += 1
            heuristic_check = verify_action_for_state(candidates[0], state) if candidates else None
            if heuristic_check is not None:
                heuristic_outcome = classify_action_outcome(candidates[0], state, heuristic_check).to_dict()
                if _closes_or_reduces(heuristic_outcome):
                    heuristic_closed += 1
        _bucket(stratified["gate"], str(row.get("gate", "UNKNOWN")), accepted=bool(first_check.get("accepted")), close=top1_close_hit, gate_progress=float(first_outcome.get("gate_progress_delta", 0.0) or 0.0) > 0)
        _bucket(stratified["outcome"], str(first_outcome.get("outcome_class", "NONE")), accepted=bool(first_check.get("accepted")), close=top1_close_hit, gate_progress=float(first_outcome.get("gate_progress_delta", 0.0) or 0.0) > 0)
        _bucket(stratified["source"], str(row.get("source", "UNKNOWN")), accepted=bool(first_check.get("accepted")), close=top1_close_hit, gate_progress=float(first_outcome.get("gate_progress_delta", 0.0) or 0.0) > 0)
        _bucket(stratified["difficulty"], str(row.get("difficulty", "UNKNOWN")), accepted=bool(first_check.get("accepted")), close=top1_close_hit, gate_progress=float(first_outcome.get("gate_progress_delta", 0.0) or 0.0) > 0)
        _bucket(stratified["modulus_bucket"], str(row.get("modulus_bucket", "UNKNOWN")), accepted=bool(first_check.get("accepted")), close=top1_close_hit, gate_progress=float(first_outcome.get("gate_progress_delta", 0.0) or 0.0) > 0)
        generated_rows.append(
            {
                "example_id": row.get("example_id"),
                "greedy_model_text": greedy_text,
                "candidate_count": len(candidates),
                "unique_candidate_count": len(ranked),
                "top_candidate_text": ranked[0]["action_text"] if ranked else "",
                "target_action_text": row.get("target_action_text"),
            }
        )

    n = max(len(rows), 1)
    candidate_n = max(checked_candidates, 1)
    theorem = build_collatz_descent_theorem_candidate()
    strict_status = theorem.get("verifier_status", "FAIL")
    heldout_close = top5_close / n
    random_close = random_closed / n
    heuristic_close = heuristic_closed / n
    top1_accept_rate = top1_accept / n
    top5_accept_rate = top5_accept / n
    top1_close_rate = top1_close / n
    top5_close_rate = top5_close / n
    top5_accept_lift = top5_accept_rate - top1_accept_rate
    top5_close_lift = top5_close_rate - top1_close_rate
    diversity_summary = {
        "unique_actions_per_state_mean": sum(unique_counts) / max(len(unique_counts), 1),
        "unique_actions_per_state_p50": _percentile(unique_counts, 0.50),
        "unique_actions_per_state_p90": _percentile(unique_counts, 0.90),
        "top5_accept_lift": top5_accept_lift,
        "top5_close_lift": top5_close_lift,
        "beam_duplicate_issue": bool(unique_counts and _percentile(unique_counts, 0.50) <= 1),
    }
    if abs(top5_accept_lift) < 1e-12:
        if diversity_summary["beam_duplicate_issue"]:
            equality_diagnosis = "duplicate-beam issue: fewer than two unique canonical actions for most states"
        elif top1_accept_rate > 0.95:
            equality_diagnosis = "expected saturation: top-1 already accepts nearly every state where top-5 accepts"
        else:
            equality_diagnosis = "ranking/eval issue suspected: unique beams exist but top-5 adds no accepted states"
    else:
        equality_diagnosis = "fixed: top-5 is measured over unique canonical actions and differs from top-1"
    stratified_summary = {bucket: _finalize_buckets(values) for bucket, values in stratified.items()}
    summary = {
        "schema": PROOF_ACTION_EVAL_SCHEMA,
        "version": 2,
        "run_id": cfg["run_id"],
        "status": "EVALUATED_PROOF_ACTION_V2",
        "checkpoint_path": cfg["checkpoint"],
        "rows_path": cfg["rows"],
        "example_count": len(rows),
        "syntax_valid_rate": syntax_valid / candidate_n,
        "action_parse_rate": parse_valid / candidate_n,
        "degenerate_output_rate": degenerate / n,
        "unique_actions_per_state_mean": diversity_summary["unique_actions_per_state_mean"],
        "unique_actions_per_state_p50": diversity_summary["unique_actions_per_state_p50"],
        "unique_actions_per_state_p90": diversity_summary["unique_actions_per_state_p90"],
        "top1_verifier_accept_rate": top1_accept_rate,
        "top5_verifier_accept_rate": top5_accept_rate,
        "top5_accept_lift": top5_accept_lift,
        "top1_close_rate": top1_close_rate,
        "top5_close_rate": top5_close_rate,
        "top1_closed_rate": top1_close_rate,
        "top5_closed_rate": top5_close_rate,
        "top5_close_lift": top5_close_lift,
        "top1_gate_progress_rate": top1_gate_progress / n,
        "top5_gate_progress_rate": top5_gate_progress / n,
        "trace_replay_close_rate": top5_close_rate,
        "heldout_obligation_close_rate": heldout_close,
        "random_legal_action_close_rate": random_close,
        "heuristic_legal_action_close_rate": heuristic_close,
        "heldout_close_vs_random": (heldout_close / random_close) if random_close > 0 else (999.0 if heldout_close > 0 else 0.0),
        "heldout_close_vs_heuristic": (heldout_close / heuristic_close)
        if heuristic_close > 0
        else (999.0 if heldout_close > 0 else 0.0),
        "gate_accept_counts": dict(gate_accepts),
        "gate_close_counts": dict(gate_closures),
        "gate_progress_counts": dict(gate_progress_counts),
        "gate_deltas": {gate: count / n for gate, count in gate_accepts.items()},
        "stratified_eval": stratified_summary,
        "topk_diversity": diversity_summary,
        "top1_top5_equality_diagnosis": equality_diagnosis,
        "strict_theorem_verifier_result": strict_status,
        "proof_confidence_percent": 100.0 if strict_status == "PASS" else 0.0,
        "model_discovery_score_percent": 100.0 * max(top1_accept_rate, top5_close_rate),
        "useful_action_rate": top1_accept_rate,
        "model_guided_obligation_closure_rate": heldout_close,
        "sample_generated_actions": sample_actions,
        "go_no_go": "NO-GO",
    }
    summary["go_no_go"] = "GO" if passes_small_gates(summary) else "NO-GO"

    (out / "eval_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "generated_actions.jsonl").write_text(
        "\n".join(json.dumps(item, sort_keys=True) for item in generated_rows) + ("\n" if generated_rows else ""),
        encoding="utf-8",
    )
    (out / "verifier_checked_actions.jsonl").write_text(
        "\n".join(json.dumps(item, sort_keys=True) for item in checked_rows) + ("\n" if checked_rows else ""),
        encoding="utf-8",
    )
    (out / "ranked_candidates.jsonl").write_text(
        "\n".join(json.dumps(item, sort_keys=True) for item in ranked_rows) + ("\n" if ranked_rows else ""),
        encoding="utf-8",
    )
    (out / "stratified_eval_summary.json").write_text(
        json.dumps(stratified_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "topk_diversity_summary.json").write_text(
        json.dumps(diversity_summary | {"top1_top5_equality_diagnosis": equality_diagnosis}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    attempt = {
        "schema": "collatz_lab.proof_action_attempt",
        "version": 1,
        "run_id": cfg["run_id"],
        "checkpoint_path": cfg["checkpoint"],
        "summary_path": str(out / "eval_summary.json"),
        "strict_theorem_verifier_result": strict_status,
        "proof_confidence_percent": summary["proof_confidence_percent"],
        "accepted_action_count": sum(1 for row in checked_rows if row["verifier_check"]["accepted"]),
        "sample_generated_actions": sample_actions,
    }
    (out / "proof_action_attempt.json").write_text(json.dumps(attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    record = {
        "schema": "collatz_lab.proof_action_attempt_record",
        "version": 1,
        "attempt_id": f"{cfg['run_id']}:{__import__('hashlib').sha256(json.dumps(summary, sort_keys=True).encode('utf-8')).hexdigest()[:16]}",
        "run_id": cfg["run_id"],
        "status": summary["go_no_go"],
        "verifier_status": strict_status,
        "proof_confidence_percent": summary["proof_confidence_percent"],
        "proof_progress_percent": 100.0 * summary["heldout_obligation_close_rate"],
        "proof_action_eval": summary,
        "proof_action_attempt": attempt,
    }
    for log_path in (out / "proof_attempts.jsonl", Path("proof_attempts.jsonl")):
        existing = set()
        if log_path.exists():
            for line in log_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        existing.add(json.loads(line).get("attempt_id"))
                    except json.JSONDecodeError:
                        pass
        if record["attempt_id"] not in existing:
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
    _write_run_result(summary, cfg, out)
    return summary


def passes_small_gates(summary: dict[str, Any]) -> bool:
    s3_s4 = int(summary.get("gate_accept_counts", {}).get("S3", 0)) + int(summary.get("gate_accept_counts", {}).get("S4", 0))
    s3_s4_close = int(summary.get("gate_close_counts", {}).get("S3", 0)) + int(summary.get("gate_close_counts", {}).get("S4", 0))
    top1_accept = float(summary.get("top1_verifier_accept_rate", 0.0) or 0.0)
    return (
        summary.get("syntax_valid_rate", 0.0) >= 0.995
        and summary.get("action_parse_rate", 0.0) >= 0.99
        and summary.get("degenerate_output_rate", 1.0) <= 0.01
        and summary.get("unique_actions_per_state_mean", 0.0) >= 5.0
        and (summary.get("top5_accept_lift", 0.0) > 0.02 or top1_accept > 0.95)
        and summary.get("trace_replay_close_rate", 0.0) >= 0.90
        and summary.get("heldout_obligation_close_rate", 0.0) >= 0.90
        and summary.get("heldout_close_vs_random", 0.0) >= 3.0
        and summary.get("top5_close_rate", 0.0) > summary.get("top1_close_rate", 1.0)
        and s3_s4 >= 106
        and s3_s4_close >= 5
    )


def _write_run_result(summary: dict[str, Any], cfg: dict[str, Any], out: Path) -> None:
    strict = str(summary.get("strict_theorem_verifier_result", "FAIL"))
    score = ProofScore(
        verifier_status=strict,
        proof_confidence_percent=100.0 if strict == "PASS" else 0.0,
        proof_progress_percent=100.0 * float(summary.get("heldout_obligation_close_rate", 0.0)),
        model_discovery_score_percent=float(summary.get("model_discovery_score_percent", 0.0)),
        blocking_obligations=["S3/S4 challenge action gate"] if summary.get("go_no_go") != "GO" else [],
        components={
            "verifier_backed_actions": 100.0 * float(summary.get("top1_verifier_accept_rate", 0.0)),
            "heldout_closure": 100.0 * float(summary.get("heldout_obligation_close_rate", 0.0)),
            "typed_syntax": 100.0 * float(summary.get("action_parse_rate", 0.0)),
        },
    )
    result = RunResult(
        run_id=cfg["run_id"],
        title=cfg["title"],
        created_at=utc_stamp(),
        config_path=cfg["config_path"],
        checkpoint_path=cfg["checkpoint"],
        commands=[
            f"python -m collatz_lab.proof_action_model train --config {cfg['config_path']}",
            f"python -m collatz_lab.proof_action_eval --config {cfg['config_path']}",
        ],
        artifacts={
            "eval_summary": str(out / "eval_summary.json"),
            "stratified_eval_summary": str(out / "stratified_eval_summary.json"),
            "topk_diversity_summary": str(out / "topk_diversity_summary.json"),
            "generated_actions": str(out / "generated_actions.jsonl"),
            "verifier_checked_actions": str(out / "verifier_checked_actions.jsonl"),
            "ranked_candidates": str(out / "ranked_candidates.jsonl"),
            "proof_action_attempt": str(out / "proof_action_attempt.json"),
        },
        eval_metrics={"proof_action_v2": summary},
        discovery_metrics={"proof_action_eval": summary},
        verification_metrics={},
        postprocess_metrics={},
        proof_graph_summary={},
        theorem_verifier_status=strict,
        score=score,
        next_step_recommendation=(
            "Launch the big action-agent run only after reviewing the S3/S4 accepted action traces."
            if summary.get("go_no_go") == "GO"
            else "Fix the smallest failing proof-action gate before scaling the big model."
        ),
        notes=["Strict theorem confidence is verifier-gated and remains 0 unless the theorem verifier passes."],
    )
    save_run_result(result, out / "run_result.json")
    write_run_result_markdown(result, out / "run_result.md")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a typed proof-action checkpoint.")
    parser.add_argument("--config", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    summary = evaluate(args.config)
    Console().print(summary)


if __name__ == "__main__":
    main()
