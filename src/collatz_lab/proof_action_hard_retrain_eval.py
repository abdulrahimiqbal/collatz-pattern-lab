"""RUN-014 hard-retrain evaluation and run-result assembly."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import torch
from rich.console import Console

from .proof_action_decode import dedupe_candidates, is_degenerate_output, legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import parse_action, serialize_action
from .proof_action_eval import _closes_or_reduces
from .proof_action_frontier_eval import load_frontier_rows
from .proof_action_frontier_search import _event_from_order, _summarize_events
from .proof_action_model import greedy_generate_action_text, load_checkpoint, score_action_components
from .proof_action_outcome import classify_action_outcome
from .proof_action_search import rank_candidate_actions, ranking_weights_from_config
from .proof_verifier import build_collatz_descent_theorem_candidate
from .utils import load_yaml


RUN012_BASELINE = {
    "raw_top5_gate_progress_rate": 0.655,
    "raw_mrr_first_gate_progress_action": 0.4778,
    "closure_at_1000_calls": 0.875,
    "gate_delta_per_1000_calls": 0.655,
    "s3_gate_delta_per_1000_calls": 0.354,
    "s4_gate_delta_per_1000_calls": 0.301,
}


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _config(path: str | Path, checkpoint: str | None = None, out: str | None = None) -> dict[str, Any]:
    cfg = load_yaml(path)
    output_dir = str(out or (cfg.get("output") or {}).get("dir") or "remote_reports/proof_action_v2/RUN-014-proof-action-v2-hard-retrain-small-a100")
    evaluation = cfg.get("evaluation", {})
    model = cfg.get("model", {})
    return {
        "raw": cfg,
        "config_path": str(path),
        "run_id": str((cfg.get("run") or {}).get("name") or (cfg.get("run") or {}).get("id") or "RUN-014-proof-action-v2-hard-retrain-small-a100"),
        "checkpoint": str(checkpoint or evaluation.get("checkpoint") or model.get("checkpoint") or Path(output_dir) / "final_checkpoint.pt"),
        "out_dir": output_dir,
        "original_rows": str(evaluation.get("original_rows") or "data/proof_action_v2_ranker/rows.jsonl"),
        "frontier_eval_dir": str(evaluation.get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval"),
        "hard_holdout": str(evaluation.get("hard_holdout") or "data/proof_action_v2_hard_mix/hard_challenge_holdout.jsonl"),
        "s6_holdout": str(evaluation.get("s6_holdout") or "data/proof_action_v2_hard_mix/s6_challenge_holdout.jsonl"),
        "train_pairs": str(evaluation.get("train_pairs") or "data/proof_action_v2_hard_mix/train_pairs.jsonl"),
        "max_examples": int(evaluation.get("max_examples", 512)),
        "budgets": [int(item) for item in (cfg.get("search") or {}).get("verifier_call_budgets", [10, 100, 1000, 5000])],
        "beam_width": int((cfg.get("search") or {}).get("beam_width", 64)),
        "candidates_per_state": int((cfg.get("search") or {}).get("candidates_per_state", 50)),
        "ranking": ranking_weights_from_config(cfg),
    }


def _select(rows: list[dict[str, Any]], *, max_examples: int, seed: int = 1337, accepted_only: bool = False) -> list[dict[str, Any]]:
    if accepted_only:
        rows = [row for row in rows if row.get("verifier_status") == "ACCEPT"] or rows
    by_gate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_gate[str(row.get("gate", "UNKNOWN"))].append(row)
    rng = random.Random(seed)
    out: list[dict[str, Any]] = []
    quota = max(1, max_examples // max(len(by_gate), 1))
    for gate_rows in by_gate.values():
        rng.shuffle(gate_rows)
        out.extend(gate_rows[:quota])
    remainder = [row for row in rows if row not in out]
    rng.shuffle(remainder)
    out.extend(remainder)
    return out[:max_examples]


def _actions_from_row(row: dict[str, Any], *, beam_width: int) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for item in row.get("candidates") or []:
        action = item.get("action")
        try:
            if isinstance(action, str):
                actions.append(parse_action(action))
            elif isinstance(action, dict):
                actions.append(parse_action(serialize_action(action)))
        except Exception:
            continue
    if isinstance(row.get("candidate_action"), dict):
        actions.append(row["candidate_action"])
    if isinstance(row.get("verify_action"), dict):
        actions.append(row["verify_action"])
    actions.extend(legal_action_candidates_from_state(str(row["state"]), max_candidates=beam_width))
    return dedupe_candidates(actions, max_candidates=beam_width)


def _mrr(rank: int | None) -> float:
    return 0.0 if rank is None else 1.0 / max(rank, 1)


def _mean(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)


def _raw_eval(
    *,
    model: Any,
    tokenizer: Any,
    rows: list[dict[str, Any]],
    max_state_len: int,
    max_action_len: int,
    beam_width: int,
    candidates_per_state: int,
    prefix: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidate_rows: list[dict[str, Any]] = []
    top5_accept = top5_gate = top5_close = top1_accept = top1_close = 0
    accepted_mrr: list[float] = []
    gate_mrr: list[float] = []
    for state_index, row in enumerate(rows):
        state = str(row["state"])
        actions = _actions_from_row(row, beam_width=beam_width)
        texts = [serialize_action(action) for action in actions]
        scores = score_action_components(model, tokenizer, state, texts, max_state_len=max_state_len, max_action_len=max_action_len)
        ordered = sorted(zip(actions, texts, scores, strict=True), key=lambda item: float(item[2].get("policy_score", 0.0)), reverse=True)[:candidates_per_state]
        first_accept = first_gate = None
        annotated = []
        for rank, (action, text, model_scores) in enumerate(ordered, start=1):
            check = verify_action_for_state(action, state)
            outcome = classify_action_outcome(action, state, check).to_dict()
            is_gate = float(outcome.get("gate_progress_delta", 0.0) or 0.0) > 0
            if check.accepted and first_accept is None:
                first_accept = rank
            if is_gate and first_gate is None:
                first_gate = rank
            record = {
                "eval_prefix": prefix,
                "state_index": state_index,
                "example_id": row.get("example_id"),
                "gate": row.get("gate"),
                "rank": rank,
                "action": action,
                "action_text": text,
                "model_scores": model_scores,
                "verifier_check": check.to_dict(),
                "outcome": outcome,
            }
            annotated.append(record)
            candidate_rows.append(record)
        head = annotated[:5]
        if head and head[0]["verifier_check"].get("accepted"):
            top1_accept += 1
        if head and _closes_or_reduces(head[0]["outcome"]):
            top1_close += 1
        if any(item["verifier_check"].get("accepted") for item in head):
            top5_accept += 1
        if any(_closes_or_reduces(item["outcome"]) for item in head):
            top5_close += 1
        if any(float(item["outcome"].get("gate_progress_delta", 0.0) or 0.0) > 0 for item in head):
            top5_gate += 1
        accepted_mrr.append(_mrr(first_accept))
        gate_mrr.append(_mrr(first_gate))
    n = max(len(rows), 1)
    return (
        {
            f"{prefix}_raw_top1_accept_rate": top1_accept / n,
            f"{prefix}_raw_top5_accept_rate": top5_accept / n,
            f"{prefix}_raw_top1_close_rate": top1_close / n,
            f"{prefix}_raw_top5_close_rate": top5_close / n,
            f"{prefix}_raw_top5_gate_progress_rate": top5_gate / n,
            f"{prefix}_raw_mrr_first_accepted_action": _mean(accepted_mrr),
            f"{prefix}_raw_mrr_first_gate_progress_action": _mean(gate_mrr),
            f"{prefix}_example_count": len(rows),
        },
        candidate_rows,
    )


def _budgeted_eval(
    *,
    model: Any,
    tokenizer: Any,
    rows: list[dict[str, Any]],
    max_state_len: int,
    max_action_len: int,
    beam_width: int,
    candidates_per_state: int,
    budgets: list[int],
    weights: dict[str, float],
    prefix: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    events = []
    random_events = []
    heuristic_events = []
    traces: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    gate_delta_by_gate: Counter[str] = Counter()
    for state_index, row in enumerate(rows):
        state = str(row["state"])
        actions = _actions_from_row(row, beam_width=beam_width)
        ranked = rank_candidate_actions(
            model=model,
            tokenizer=tokenizer,
            state=state,
            candidates=actions,
            max_state_len=max_state_len,
            max_action_len=max_action_len,
            weights=weights,
            max_candidates=candidates_per_state,
        )
        model_event = _event_from_order(row, ranked, budgets)
        events.append(model_event)
        if model_event.get("gate_progress"):
            gate_delta_by_gate[str(row.get("gate", "UNKNOWN"))] += float(model_event.get("gate_progress_delta", 0.0) or 0.0)
        random_order = [{"action": action, "action_text": serialize_action(action), "score": 0.0, "model_scores": {}} for action in actions]
        random.Random(1337 + state_index).shuffle(random_order)
        random_events.append(_event_from_order(row, random_order, budgets))
        heuristic_order = [{"action": action, "action_text": serialize_action(action), "score": 0.0, "model_scores": {}} for action in actions]
        heuristic_events.append(_event_from_order(row, heuristic_order, budgets))
        compact = {key: value for key, value in model_event.items() if key != "annotated"}
        compact.update({"eval_prefix": prefix, "state_index": state_index, "example_id": row.get("example_id"), "gate": row.get("gate")})
        traces.append(compact)
        for item in model_event["annotated"]:
            record = {"eval_prefix": prefix, "state_index": state_index, "example_id": row.get("example_id"), "gate": row.get("gate"), **item}
            if item["verifier_check"].get("accepted"):
                accepted.append(record)
            else:
                rejected.append(record)
    model_summary = _summarize_events(events, budgets)
    random_summary = _summarize_events(random_events, budgets)
    heuristic_summary = _summarize_events(heuristic_events, budgets)
    hard_random = random_summary.get("closure_at_1000_calls", 0.0) or 0.0
    hard_heuristic = heuristic_summary.get("closure_at_1000_calls", 0.0) or 0.0
    n = max(len(rows), 1)
    summary = {
        f"{prefix}_{key}": value for key, value in model_summary.items()
    }
    summary.update(
        {
            f"{prefix}_improvement_vs_random": (model_summary.get("closure_at_1000_calls", 0.0) / hard_random) if hard_random else (999.0 if model_summary.get("closure_at_1000_calls", 0.0) else 0.0),
            f"{prefix}_improvement_vs_heuristic": (model_summary.get("closure_at_1000_calls", 0.0) / hard_heuristic) if hard_heuristic else (999.0 if model_summary.get("closure_at_1000_calls", 0.0) else 0.0),
            f"{prefix}_s3_gate_delta_per_1000_calls": gate_delta_by_gate.get("S3", 0.0) / max(n * 1000, 1) * 1000,
            f"{prefix}_s4_gate_delta_per_1000_calls": gate_delta_by_gate.get("S4", 0.0) / max(n * 1000, 1) * 1000,
            f"{prefix}_s6_gate_delta_per_1000_calls": gate_delta_by_gate.get("S6", 0.0) / max(n * 1000, 1) * 1000,
            f"{prefix}_random_closure_at_1000_calls": random_summary.get("closure_at_1000_calls", 0.0),
            f"{prefix}_heuristic_closure_at_1000_calls": heuristic_summary.get("closure_at_1000_calls", 0.0),
        }
    )
    return summary, traces, accepted, rejected


def _original_regression_eval(
    *,
    model: Any,
    tokenizer: Any,
    rows: list[dict[str, Any]],
    max_state_len: int,
    max_action_len: int,
    beam_width: int,
    candidates_per_state: int,
    weights: dict[str, float],
) -> dict[str, Any]:
    syntax = parse = degenerate = top1_accept = top1_close = 0
    checked = 0
    selected = _select(rows, max_examples=512, accepted_only=True)
    for row in selected:
        state = str(row["state"])
        text = greedy_generate_action_text(model, tokenizer, state, max_state_len=max_state_len, max_action_len=max_action_len)
        if is_degenerate_output(text):
            degenerate += 1
        ranked = rank_candidate_actions(
            model=model,
            tokenizer=tokenizer,
            state=state,
            candidates=_actions_from_row(row, beam_width=beam_width),
            max_state_len=max_state_len,
            max_action_len=max_action_len,
            weights=weights,
            max_candidates=candidates_per_state,
        )
        if not ranked:
            continue
        checked += 1
        top = ranked[0]
        try:
            parse_action(top["action_text"])
            syntax += 1
            parse += 1
        except Exception:
            pass
        check = verify_action_for_state(top["action"], state)
        outcome = classify_action_outcome(top["action"], state, check).to_dict()
        top1_accept += 1 if check.accepted else 0
        top1_close += 1 if _closes_or_reduces(outcome) else 0
    n = max(checked, 1)
    top1_accept_rate = top1_accept / n
    regression = max(0.0, 1.0 - top1_accept_rate)
    return {
        "syntax_valid_rate": syntax / n,
        "action_parse_rate": parse / n,
        "degenerate_output_rate": degenerate / max(len(selected), 1),
        "top1_accept_rate": top1_accept_rate,
        "top1_close_rate": top1_close / n,
        "original_eval_regression_vs_RUN011": regression,
        "example_count": checked,
    }


def run_hard_retrain_eval(config_path: str | Path, *, checkpoint: str | None = None, out: str | None = None) -> dict[str, Any]:
    cfg = _config(config_path, checkpoint=checkpoint, out=out)
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, tokenizer, checkpoint_payload = load_checkpoint(cfg["checkpoint"], device=device)
    model_cfg = dict(checkpoint_payload.get("config") or {})
    max_state_len = int(model_cfg.get("max_state_len", 2048))
    max_action_len = int(model_cfg.get("max_action_len", 128))

    original_rows = _load_jsonl(cfg["original_rows"])
    frontier_rows = load_frontier_rows(cfg["frontier_eval_dir"])[: cfg["max_examples"]]
    hard_rows = _load_jsonl(cfg["hard_holdout"])[: cfg["max_examples"]]
    s6_rows = _load_jsonl(cfg["s6_holdout"])[: cfg["max_examples"]]
    train_pairs = _load_jsonl(cfg["train_pairs"])
    train_lemma_ids = {str(row.get("lemma_id")) for row in train_pairs if row.get("lemma_id")}
    for row in _load_jsonl("data/proof_action_v2_hard_mix/train_policy.jsonl"):
        if row.get("lemma_id"):
            train_lemma_ids.add(str(row.get("lemma_id")))

    original = _original_regression_eval(
        model=model,
        tokenizer=tokenizer,
        rows=original_rows,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
        beam_width=cfg["beam_width"],
        candidates_per_state=cfg["candidates_per_state"],
        weights=cfg["ranking"],
    )
    frontier_raw, frontier_candidates = _raw_eval(
        model=model,
        tokenizer=tokenizer,
        rows=frontier_rows,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
        beam_width=cfg["beam_width"],
        candidates_per_state=cfg["candidates_per_state"],
        prefix="frontier",
    )
    frontier_budget, frontier_traces, frontier_accepted, frontier_rejected = _budgeted_eval(
        model=model,
        tokenizer=tokenizer,
        rows=frontier_rows,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
        beam_width=cfg["beam_width"],
        candidates_per_state=cfg["candidates_per_state"],
        budgets=cfg["budgets"],
        weights=cfg["ranking"],
        prefix="frontier",
    )
    hard_raw, hard_candidates = _raw_eval(
        model=model,
        tokenizer=tokenizer,
        rows=hard_rows,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
        beam_width=cfg["beam_width"],
        candidates_per_state=cfg["candidates_per_state"],
        prefix="hard_holdout",
    )
    hard_budget, hard_traces, hard_accepted, hard_rejected = _budgeted_eval(
        model=model,
        tokenizer=tokenizer,
        rows=hard_rows,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
        beam_width=cfg["beam_width"],
        candidates_per_state=cfg["candidates_per_state"],
        budgets=cfg["budgets"],
        weights=cfg["ranking"],
        prefix="hard_holdout",
    )
    s6_raw, s6_candidates = _raw_eval(
        model=model,
        tokenizer=tokenizer,
        rows=s6_rows,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
        beam_width=cfg["beam_width"],
        candidates_per_state=cfg["candidates_per_state"],
        prefix="s6",
    )
    s6_budget, s6_traces, s6_accepted, s6_rejected = _budgeted_eval(
        model=model,
        tokenizer=tokenizer,
        rows=s6_rows,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
        beam_width=cfg["beam_width"],
        candidates_per_state=cfg["candidates_per_state"],
        budgets=cfg["budgets"],
        weights=cfg["ranking"],
        prefix="s6",
    )
    s6_lemma_actions = [
        row
        for row in s6_candidates
        if row["action"].get("type") in {"PROPOSE_S6_LEMMA", "VERIFY_S6_LEMMA", "CLOSE_STRICT_THEOREM_BLOCKER"}
    ]
    s6_accepted_lemmas = [
        row
        for row in s6_lemma_actions
        if row["verifier_check"].get("accepted")
        and str(row["action"].get("lemma_id", "")) not in train_lemma_ids
    ]
    s6_eval = {
        **s6_raw,
        **s6_budget,
        "s6_raw_top5_accept_rate": s6_raw.get("s6_raw_top5_accept_rate", 0.0),
        "s6_candidate_lemma_accept_rate": len([row for row in s6_lemma_actions if row["verifier_check"].get("accepted")]) / max(len(s6_lemma_actions), 1),
        "s6_gate_delta_per_1000_calls": s6_budget.get("s6_s6_gate_delta_per_1000_calls", 0.0),
        "s6_blockers_reduced": len([row for row in s6_accepted if row["action"].get("type") in {"CLOSE_STRICT_THEOREM_BLOCKER", "VERIFY_S6_LEMMA"}]),
        "s6_new_accepted_lemmas_not_in_train": len(s6_accepted_lemmas),
    }
    theorem = build_collatz_descent_theorem_candidate()
    strict = theorem.get("verifier_status", "FAIL")

    frontier_eval = {
        **frontier_raw,
        **frontier_budget,
        "raw_top5_gate_progress_rate": frontier_raw.get("frontier_raw_top5_gate_progress_rate", 0.0),
        "raw_mrr_first_gate_progress_action": frontier_raw.get("frontier_raw_mrr_first_gate_progress_action", 0.0),
        "closure_at_1000_calls": frontier_budget.get("frontier_closure_at_1000_calls", 0.0),
        "gate_delta_per_1000_calls": frontier_budget.get("frontier_gate_delta_per_1000_calls", 0.0),
        "s3_gate_delta_per_1000_calls": frontier_budget.get("frontier_s3_gate_delta_per_1000_calls", 0.0),
        "s4_gate_delta_per_1000_calls": frontier_budget.get("frontier_s4_gate_delta_per_1000_calls", 0.0),
        "s6_gate_delta_per_1000_calls": frontier_budget.get("frontier_s6_gate_delta_per_1000_calls", 0.0),
        "improvement_vs_random_at_1000_calls": frontier_budget.get("frontier_improvement_vs_random", 0.0),
        "improvement_vs_heuristic_at_1000_calls": frontier_budget.get("frontier_improvement_vs_heuristic", 0.0),
    }
    hard_eval = {
        **hard_raw,
        **hard_budget,
        "hard_holdout_raw_top5_accept_rate": hard_raw.get("hard_holdout_raw_top5_accept_rate", 0.0),
        "hard_holdout_raw_top5_gate_progress_rate": hard_raw.get("hard_holdout_raw_top5_gate_progress_rate", 0.0),
        "hard_holdout_closure_at_1000_calls": hard_budget.get("hard_holdout_closure_at_1000_calls", 0.0),
        "hard_holdout_gate_delta_per_1000_calls": hard_budget.get("hard_holdout_gate_delta_per_1000_calls", 0.0),
        "hard_holdout_dead_end_rate": hard_budget.get("hard_holdout_dead_end_rate", 0.0),
        "hard_holdout_improvement_vs_random": hard_budget.get("hard_holdout_improvement_vs_random", 0.0),
        "hard_holdout_improvement_vs_heuristic": hard_budget.get("hard_holdout_improvement_vs_heuristic", 0.0),
    }
    big_go = (
        original.get("syntax_valid_rate", 0.0) >= 0.995
        and original.get("action_parse_rate", 0.0) >= 0.99
        and original.get("degenerate_output_rate", 1.0) <= 0.01
        and original.get("original_eval_regression_vs_RUN011", 1.0) <= 0.05
        and frontier_eval["raw_top5_gate_progress_rate"] > RUN012_BASELINE["raw_top5_gate_progress_rate"]
        and frontier_eval["raw_mrr_first_gate_progress_action"] > RUN012_BASELINE["raw_mrr_first_gate_progress_action"]
        and frontier_eval["gate_delta_per_1000_calls"] > RUN012_BASELINE["gate_delta_per_1000_calls"]
        and frontier_eval["s3_gate_delta_per_1000_calls"] > RUN012_BASELINE["s3_gate_delta_per_1000_calls"]
        and frontier_eval["s4_gate_delta_per_1000_calls"] > RUN012_BASELINE["s4_gate_delta_per_1000_calls"]
        and frontier_eval["s6_gate_delta_per_1000_calls"] > 0
        and hard_eval["hard_holdout_improvement_vs_random"] >= 3.0
        and hard_eval["hard_holdout_improvement_vs_heuristic"] >= 2.0
        and s6_eval["s6_blockers_reduced"] >= 1
        and s6_eval["s6_new_accepted_lemmas_not_in_train"] >= 1
    )
    summary = {
        "schema": "collatz_lab.proof_action_hard_retrain_eval",
        "version": 1,
        "run_id": cfg["run_id"],
        "checkpoint_path": cfg["checkpoint"],
        "original_regression": original,
        "frontier_eval": frontier_eval,
        "hard_holdout_eval": hard_eval,
        "s6_eval": s6_eval,
        "strict_theorem_verifier_result": strict,
        "proof_confidence_percent": 100.0 if strict == "PASS" else 0.0,
        "go_no_go_big": "GO" if big_go else "NO-GO",
    }

    (out_dir / "original_regression_eval.json").write_text(json.dumps(original, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "frontier_eval_summary.json").write_text(json.dumps(frontier_eval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "hard_holdout_eval_summary.json").write_text(json.dumps(hard_eval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "s6_eval_summary.json").write_text(json.dumps(s6_eval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "budgeted_search_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "baseline_comparison.json").write_text(
        json.dumps(
            {
                "run012_baseline": RUN012_BASELINE,
                "frontier": frontier_eval,
                "hard_holdout_random": hard_eval.get("hard_holdout_random_closure_at_1000_calls"),
                "hard_holdout_heuristic": hard_eval.get("hard_holdout_heuristic_closure_at_1000_calls"),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_jsonl(out_dir / "generated_actions.jsonl", frontier_candidates + hard_candidates + s6_candidates)
    _write_jsonl(out_dir / "verifier_checked_actions.jsonl", frontier_accepted + frontier_rejected + hard_accepted + hard_rejected + s6_accepted + s6_rejected)
    _write_jsonl(out_dir / "accepted_frontier_actions.jsonl", frontier_accepted + hard_accepted)
    _write_jsonl(out_dir / "rejected_frontier_actions.jsonl", frontier_rejected + hard_rejected)
    _write_jsonl(out_dir / "s6_candidate_actions.jsonl", s6_lemma_actions)
    _write_jsonl(out_dir / "s6_accepted_lemmas.jsonl", s6_accepted_lemmas)
    run_result = {
        "schema": "collatz_lab.run_result.hard_retrain_eval",
        "version": 1,
        "run_id": cfg["run_id"],
        "config_path": cfg["config_path"],
        "checkpoint_path": cfg["checkpoint"],
        "eval_metrics": summary,
        "theorem_verifier_status": strict,
        "proof_confidence_percent": summary["proof_confidence_percent"],
        "go_no_go_big": summary["go_no_go_big"],
        "next_step_recommendation": next_bottleneck(summary),
    }
    (out_dir / "run_result.json").write_text(json.dumps(run_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def next_bottleneck(summary: dict[str, Any]) -> str:
    original = summary["original_regression"]
    frontier = summary["frontier_eval"]
    hard = summary["hard_holdout_eval"]
    s6 = summary["s6_eval"]
    if original.get("original_eval_regression_vs_RUN011", 1.0) > 0.05:
        return "catastrophic forgetting"
    if s6.get("s6_gate_delta_per_1000_calls", 0.0) <= 0 or s6.get("s6_blockers_reduced", 0) < 1:
        return "S6 action generator insufficient"
    if hard.get("hard_holdout_improvement_vs_random", 0.0) < 3.0:
        return "ranker/value not using hard traces"
    if frontier.get("raw_top5_gate_progress_rate", 0.0) <= RUN012_BASELINE["raw_top5_gate_progress_rate"]:
        return "raw model proposals weak on frontier progress"
    if frontier.get("gate_delta_per_1000_calls", 0.0) <= RUN012_BASELINE["gate_delta_per_1000_calls"]:
        return "search depth insufficient"
    return "RUN-015 bigger model may be prepared, but do not launch automatically"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate RUN-014 hard-curriculum retraining.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint")
    parser.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(run_hard_retrain_eval(args.config, checkpoint=args.checkpoint, out=args.out))


if __name__ == "__main__":
    main()
