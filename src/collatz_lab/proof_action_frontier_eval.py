"""Raw proposal evaluation for hard proof-action frontier states."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import torch
from rich.console import Console

from .proof_action_candidate_selector import (
    GATE_PROGRESS_OUTCOMES,
    candidate_utility,
    infer_target_objective,
    objective_threshold,
    selector_candidate_record,
)
from .proof_action_decode import dedupe_candidates, legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import parse_action, serialize_action
from .proof_action_eval import _closes_or_reduces
from .proof_action_model import (
    load_checkpoint,
    proposal_score_from_components,
    score_action_components,
    score_candidate_selector_components,
)
from .proof_action_outcome import classify_action_outcome
from .proof_action_trap_states import parse_candidate_action
from .utils import load_yaml


def load_frontier_rows(eval_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(eval_dir)
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                row.setdefault("eval_file", path.name)
                rows.append(row)
    return rows


def _config(path: str | Path, checkpoint: str | None = None, eval_dir: str | None = None, out: str | None = None) -> dict[str, Any]:
    cfg = load_yaml(path)
    run = cfg.get("run", {})
    model = cfg.get("model", {})
    evaluation = cfg.get("eval", cfg.get("evaluation", {}))
    output = cfg.get("output", {})
    return {
        "run_id": str(run.get("name") or run.get("id") or "RUN-012-proof-action-v2-frontier-search-small-a100"),
        "checkpoint": str(checkpoint or model.get("checkpoint") or evaluation.get("checkpoint")),
        "eval_dir": str(eval_dir or evaluation.get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval"),
        "out_dir": str(out or output.get("dir") or "reports/runs/RUN-012-proof-action-v2-frontier-search-small-a100"),
        "candidates_per_state": int((cfg.get("search") or {}).get("candidates_per_state", 50)),
        "beam_width": int((cfg.get("search") or {}).get("beam_width", 64)),
        "policy_mode": str((cfg.get("search") or {}).get("policy_mode", "proposal_score")),
        "max_candidate_pair_len": int((cfg.get("model") or {}).get("max_candidate_pair_len", 2176)),
        "max_examples": int(evaluation.get("max_examples", 1000)),
        "proposal_ranking": {
            "ranker_weight": float((cfg.get("proposal_ranking") or {}).get("ranker_weight", 1.0)),
            "value_weight": float((cfg.get("proposal_ranking") or {}).get("value_weight", 0.25)),
            "policy_weight": float((cfg.get("proposal_ranking") or {}).get("policy_weight", 0.05)),
        },
    }


def _actions_from_row(row: dict[str, Any], *, beam_width: int) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for item in row.get("candidates") or []:
        action = parse_candidate_action(item)
        if action is not None:
            actions.append(action)
    actions.extend(legal_action_candidates_from_state(str(row["state"]), max_candidates=beam_width))
    return dedupe_candidates(actions, max_candidates=beam_width)


def _candidate_label(row: dict[str, Any], action_text: str) -> dict[str, Any]:
    for item in row.get("candidates") or []:
        if str(item.get("action", "")).strip() == action_text:
            return item
        try:
            if serialize_action(parse_action(str(item.get("action", "")))) == action_text:
                return item
        except Exception:
            pass
    return {}


def _mrr(rank: int | None) -> float:
    return 0.0 if rank is None else 1.0 / max(rank, 1)


def _mean(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)


def _safe_div(num: float, den: float) -> float:
    return float(num / den) if den and den > 0 else 0.0


def add_normalized_selector_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    oracle_gate = float(summary.get("oracle_gate_progress_available_rate", 0.0) or 0.0)
    raw_top5_gate = float(
        summary.get("selector_raw_top5_gate_progress_rate", summary.get("raw_top5_gate_progress_rate", 0.0)) or 0.0
    )
    raw_mrr_gate = float(
        summary.get(
            "selector_raw_mrr_first_gate_progress_action",
            summary.get("raw_mrr_first_gate_progress_action", 0.0),
        )
        or 0.0
    )
    oracle_best_utility = float(summary.get("oracle_best_utility_mean", 0.0) or 0.0)
    mean_regret = float(summary.get("mean_policy_regret", 0.0) or 0.0)

    summary["selector_top5_gate_progress_oracle_recall"] = _safe_div(raw_top5_gate, oracle_gate)
    summary["selector_mrr_gate_progress_oracle_normalized"] = _safe_div(raw_mrr_gate, oracle_gate)
    summary["normalized_policy_regret"] = _safe_div(mean_regret, oracle_best_utility)
    return summary


def _raw_ordered_candidates(
    *,
    model: Any,
    tokenizer: Any,
    row: dict[str, Any],
    max_state_len: int,
    max_action_len: int,
    beam_width: int,
    candidates_per_state: int,
    proposal_weights: dict[str, float],
    policy_mode: str = "proposal_score",
    max_candidate_pair_len: int = 2176,
) -> list[dict[str, Any]]:
    state = str(row["state"])
    target_objective = str(row.get("target_objective") or infer_target_objective(row))
    actions = _actions_from_row(row, beam_width=beam_width)
    actions = dedupe_candidates(actions, max_candidates=candidates_per_state)
    texts = [serialize_action(action) for action in actions]
    if policy_mode == "listwise_selector":
        components = score_candidate_selector_components(
            model,
            tokenizer,
            state,
            texts,
            max_candidate_pair_len=max_candidate_pair_len,
        )
    else:
        components = score_action_components(
            model,
            tokenizer,
            state,
            texts,
            max_state_len=max_state_len,
            max_action_len=max_action_len,
        )
    ordered = []
    for action, text, model_scores in zip(actions, texts, components, strict=True):
        raw_score = (
            float(model_scores.get("selector_score", 0.0) or 0.0)
            if policy_mode == "listwise_selector"
            else proposal_score_from_components(model_scores, **proposal_weights)
        )
        ordered.append(
            {
                "action": action,
                "action_text": text,
                "model_scores": model_scores,
                "raw_score": raw_score,
                "target_objective": target_objective,
            }
        )
    ordered.sort(key=lambda item: item["raw_score"], reverse=True)

    for item in ordered:
        action = item["action"]
        text = item["action_text"]
        check = verify_action_for_state(action, state)
        outcome = classify_action_outcome(action, state, check).to_dict()
        label = _candidate_label(row, text)
        downstream = str(label.get("downstream_outcome", "UNKNOWN"))
        gate_progress = float(outcome.get("gate_progress_delta", 0.0) or 0.0)
        if downstream == "GATE_PROGRESS":
            gate_progress = max(gate_progress, float(label.get("gate_progress_delta", 1.0) or 1.0))
        item.update(
            {
                "verifier_check": check.to_dict(),
                "outcome": outcome,
                "downstream_outcome": downstream,
                "effective_gate_progress_delta": gate_progress,
            }
        )
        selector_record = selector_candidate_record(item, gate=str(row.get("gate", "")), target_objective=target_objective)
        item["selector_outcome_class"] = selector_record["outcome_class"]
        item["utility"] = selector_record["utility"]
    return ordered


def raw_proposal_eval(
    config_path: str | Path,
    *,
    checkpoint: str | None = None,
    eval_dir: str | None = None,
    out: str | None = None,
) -> dict[str, Any]:
    cfg = _config(config_path, checkpoint=checkpoint, eval_dir=eval_dir, out=out)
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, tokenizer, checkpoint_payload = load_checkpoint(cfg["checkpoint"], device=device)
    model_cfg = dict(checkpoint_payload.get("config") or {})
    max_state_len = int(model_cfg.get("max_state_len", 2048))
    max_action_len = int(model_cfg.get("max_action_len", 128))
    rows = load_frontier_rows(cfg["eval_dir"])[: cfg["max_examples"]]

    per_candidate: list[dict[str, Any]] = []
    accepted_mrr: list[float] = []
    close_mrr: list[float] = []
    gate_mrr: list[float] = []
    duplicate_rates: list[float] = []
    unique_counts: list[float] = []
    oracle_gate_available: list[float] = []
    oracle_top1_utilities: list[float] = []
    oracle_top5_gate_hits: list[float] = []
    oracle_best_utilities: list[float] = []
    model_policy_regrets: list[float] = []
    top_metrics = {k: Counter() for k in (1, 5, 10)}
    syntax_top1 = 0
    parse_top1 = 0
    stratified: dict[str, Counter[str]] = {}
    objective_stratified: dict[str, Counter[str]] = {}

    for state_index, row in enumerate(rows):
        ordered = _raw_ordered_candidates(
            model=model,
            tokenizer=tokenizer,
            row=row,
            max_state_len=max_state_len,
            max_action_len=max_action_len,
            beam_width=cfg["beam_width"],
            candidates_per_state=cfg["candidates_per_state"],
            proposal_weights=cfg["proposal_ranking"],
            policy_mode=cfg["policy_mode"],
            max_candidate_pair_len=cfg["max_candidate_pair_len"],
        )
        raw_texts = [item["action_text"] for item in ordered]
        unique_counts.append(float(len(set(raw_texts))))
        duplicate_rates.append(1.0 - (len(set(raw_texts)) / max(len(raw_texts), 1)))
        target_objective = str(row.get("target_objective") or infer_target_objective(row))
        threshold = objective_threshold(target_objective)
        objective_counter = objective_stratified.setdefault(target_objective, Counter())
        objective_counter["count"] += 1
        objective_available = any(
            candidate_utility(item, target_objective) >= threshold
            for item in ordered
        )
        objective_counter["oracle_available"] += 1 if objective_available else 0
        oracle_ordered = sorted(ordered, key=lambda item: float(item.get("utility", 0.0) or 0.0), reverse=True)
        oracle_best = oracle_ordered[0] if oracle_ordered else None
        model_best = ordered[0] if ordered else None
        if model_best is not None:
            objective_counter["model_top1_objective_good"] += (
                1 if candidate_utility(model_best, target_objective) >= threshold else 0
            )
        objective_counter["policy_regret_sum"] += (
            (float(oracle_best.get("utility", 0.0) or 0.0) - float(model_best.get("utility", 0.0) or 0.0))
            if oracle_best and model_best
            else 0.0
        )
        oracle_gate_available.append(
            1.0 if any(str(item.get("selector_outcome_class")) in GATE_PROGRESS_OUTCOMES for item in ordered) else 0.0
        )
        oracle_top1_utilities.append(float(oracle_best.get("utility", 0.0) or 0.0) if oracle_best else 0.0)
        oracle_best_utilities.append(float(oracle_best.get("utility", 0.0) or 0.0) if oracle_best else 0.0)
        oracle_top5_gate_hits.append(
            1.0 if any(str(item.get("selector_outcome_class")) in GATE_PROGRESS_OUTCOMES for item in oracle_ordered[:5]) else 0.0
        )
        model_policy_regrets.append(
            (float(oracle_best.get("utility", 0.0) or 0.0) - float(model_best.get("utility", 0.0) or 0.0))
            if oracle_best and model_best
            else 0.0
        )
        first_accept = first_close = first_gate = None
        for rank, item in enumerate(ordered, start=1):
            candidate_record = {
                "state_index": state_index,
                "example_id": row.get("example_id"),
                "eval_file": row.get("eval_file"),
                "frontier_kind": row.get("frontier_kind"),
                "gate": row.get("gate"),
                "target_objective": target_objective,
                "rank": rank,
                **item,
            }
            per_candidate.append(candidate_record)
            accepted = bool(item["verifier_check"].get("accepted"))
            close = _closes_or_reduces(item["outcome"])
            gate = float(item.get("effective_gate_progress_delta", 0.0) or 0.0) > 0
            if rank == 1:
                try:
                    parse_action(item["action_text"])
                    syntax_top1 += 1
                    parse_top1 += 1
                except Exception:
                    pass
            if accepted and first_accept is None:
                first_accept = rank
            if close and first_close is None:
                first_close = rank
            if gate and first_gate is None:
                first_gate = rank
        for top_k in (1, 5, 10):
            head = ordered[:top_k]
            top_metrics[top_k]["accepted"] += 1 if any(item["verifier_check"].get("accepted") for item in head) else 0
            top_metrics[top_k]["close"] += 1 if any(_closes_or_reduces(item["outcome"]) for item in head) else 0
            top_metrics[top_k]["gate"] += 1 if any(float(item.get("effective_gate_progress_delta", 0.0) or 0.0) > 0 for item in head) else 0
        accepted_mrr.append(_mrr(first_accept))
        close_mrr.append(_mrr(first_close))
        gate_mrr.append(_mrr(first_gate))
        bucket = str(row.get("frontier_kind", "unknown"))
        stratified.setdefault(bucket, Counter())["count"] += 1
        stratified[bucket]["top5_gate"] += 1 if any(float(item.get("effective_gate_progress_delta", 0.0) or 0.0) > 0 for item in ordered[:5]) else 0
        stratified[bucket]["top5_close"] += 1 if any(_closes_or_reduces(item["outcome"]) for item in ordered[:5]) else 0

    n = max(len(rows), 1)
    summary = {
        "schema": "collatz_lab.proof_action_raw_frontier_eval",
        "version": 1,
        "run_id": cfg["run_id"],
        "mode": "RAW_MODEL_PROPOSAL_EVAL",
        "checkpoint_path": cfg["checkpoint"],
        "frontier_eval_dir": cfg["eval_dir"],
        "example_count": len(rows),
        "raw_top1_syntax_valid_rate": syntax_top1 / n,
        "raw_top1_parse_rate": parse_top1 / n,
        "raw_top1_verifier_accept_rate": top_metrics[1]["accepted"] / n,
        "raw_top5_verifier_accept_rate": top_metrics[5]["accepted"] / n,
        "raw_top10_verifier_accept_rate": top_metrics[10]["accepted"] / n,
        "raw_top1_close_or_reduce_rate": top_metrics[1]["close"] / n,
        "raw_top5_close_or_reduce_rate": top_metrics[5]["close"] / n,
        "raw_top10_close_or_reduce_rate": top_metrics[10]["close"] / n,
        "raw_top1_gate_progress_rate": top_metrics[1]["gate"] / n,
        "raw_top5_gate_progress_rate": top_metrics[5]["gate"] / n,
        "raw_top10_gate_progress_rate": top_metrics[10]["gate"] / n,
        "raw_mrr_first_accepted_action": _mean(accepted_mrr),
        "raw_mrr_first_close_or_reduce_action": _mean(close_mrr),
        "raw_mrr_first_gate_progress_action": _mean(gate_mrr),
        "unique_raw_actions_per_state_mean": _mean(unique_counts),
        "duplicate_raw_action_rate": _mean(duplicate_rates),
        "oracle_gate_progress_available_rate": _mean(oracle_gate_available),
        "oracle_top1_utility": _mean(oracle_top1_utilities),
        "oracle_top5_gate_progress_rate": _mean(oracle_top5_gate_hits),
        "oracle_best_utility_mean": _mean(oracle_best_utilities),
        "oracle_policy_regret_current_model": _mean(model_policy_regrets),
        "mean_policy_regret": _mean(model_policy_regrets),
        "oracle_available_rate_by_objective": {
            key: counter["oracle_available"] / max(counter["count"], 1)
            for key, counter in objective_stratified.items()
        },
        "oracle_count_by_objective": {
            key: int(counter["count"])
            for key, counter in objective_stratified.items()
        },
        "model_top1_objective_hit_rate_by_objective": {
            key: counter["model_top1_objective_good"] / max(counter["count"], 1)
            for key, counter in objective_stratified.items()
        },
        "oracle_policy_regret_by_objective": {
            key: counter["policy_regret_sum"] / max(counter["count"], 1)
            for key, counter in objective_stratified.items()
        },
        "stratified_raw": {
            key: {
                "count": int(counter["count"]),
                "top5_gate_progress_rate": counter["top5_gate"] / max(counter["count"], 1),
                "top5_close_or_reduce_rate": counter["top5_close"] / max(counter["count"], 1),
            }
            for key, counter in stratified.items()
        },
    }
    add_normalized_selector_metrics(summary)
    (out_dir / "raw_proposal_eval_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "raw_proposal_candidates.jsonl").write_text(
        "\n".join(json.dumps(item, sort_keys=True) for item in per_candidate) + ("\n" if per_candidate else ""),
        encoding="utf-8",
    )
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate raw model proposal quality on frontier states.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint")
    parser.add_argument("--eval-dir")
    parser.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(raw_proposal_eval(args.config, checkpoint=args.checkpoint, eval_dir=args.eval_dir, out=args.out))


if __name__ == "__main__":
    main()
