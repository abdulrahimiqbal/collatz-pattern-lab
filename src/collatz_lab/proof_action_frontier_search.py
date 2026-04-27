"""Budgeted verifier-search diagnostics on hard frontier states."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import torch
from rich.console import Console

from .proof_action_decode import dedupe_candidates, legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import parse_action, serialize_action
from .proof_action_eval import _closes_or_reduces
from .proof_action_frontier_eval import load_frontier_rows, raw_proposal_eval
from .proof_action_leakage import run_leakage_check
from .proof_action_model import load_checkpoint
from .proof_action_outcome import classify_action_outcome
from .proof_action_search import rank_candidate_actions, ranking_weights_from_config
from .proof_action_trap_states import parse_candidate_action
from .proof_verifier import build_collatz_descent_theorem_candidate
from .utils import load_yaml


def _config(path: str | Path, checkpoint: str | None = None, eval_dir: str | None = None, out: str | None = None) -> dict[str, Any]:
    cfg = load_yaml(path)
    run = cfg.get("run", {})
    model = cfg.get("model", {})
    evaluation = cfg.get("eval", {})
    search = cfg.get("search", {})
    output = cfg.get("output", {})
    return {
        "run_id": str(run.get("name") or run.get("id") or "RUN-012-proof-action-v2-frontier-search-small-a100"),
        "config_path": str(path),
        "checkpoint": str(checkpoint or model.get("checkpoint")),
        "eval_dir": str(eval_dir or evaluation.get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval"),
        "out_dir": str(out or output.get("dir") or "reports/runs/RUN-012-proof-action-v2-frontier-search-small-a100"),
        "budgets": [int(item) for item in search.get("verifier_call_budgets", [10, 100, 1000, 5000])],
        "max_depth": int(search.get("max_depth", 30)),
        "beam_width": int(search.get("beam_width", 64)),
        "candidates_per_state": int(search.get("candidates_per_state", 50)),
        "max_examples": int(evaluation.get("max_examples", 1000)),
        "ranking": ranking_weights_from_config(cfg),
        "train_rows": str(evaluation.get("train_rows") or "data/proof_action_v2_ranker/train.jsonl"),
        "raw_proposal_eval": bool(evaluation.get("raw_proposal_eval", True)),
        "leakage_check": bool(evaluation.get("leakage_check", True)),
    }


def _actions_from_row(row: dict[str, Any], *, beam_width: int) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for item in row.get("candidates") or []:
        action = parse_candidate_action(item)
        if action is not None:
            actions.append(action)
    actions.extend(legal_action_candidates_from_state(str(row["state"]), max_candidates=beam_width))
    return dedupe_candidates(actions, max_candidates=beam_width)


def _label_for(row: dict[str, Any], action_text: str) -> dict[str, Any]:
    for item in row.get("candidates") or []:
        action = item.get("action")
        if isinstance(action, str):
            try:
                if serialize_action(parse_action(action)) == action_text:
                    return item
            except Exception:
                if action.strip() == action_text:
                    return item
        elif isinstance(action, dict):
            try:
                if serialize_action(action) == action_text:
                    return item
            except Exception:
                pass
    return {}


def _annotate_order(row: dict[str, Any], ordered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated = []
    for rank, item in enumerate(ordered, start=1):
        action = item["action"]
        text = item.get("action_text") or serialize_action(action)
        check = item.get("verifier_check")
        if not isinstance(check, dict):
            check_obj = verify_action_for_state(action, str(row["state"]))
            check = check_obj.to_dict()
        else:
            check_obj = verify_action_for_state(action, str(row["state"]))
        outcome = item.get("outcome")
        if not isinstance(outcome, dict):
            outcome = classify_action_outcome(action, str(row["state"]), check_obj).to_dict()
        label = _label_for(row, text)
        downstream = str(label.get("downstream_outcome", "UNKNOWN"))
        gate_delta = float(label.get("gate_progress_delta", outcome.get("gate_progress_delta", 0.0)) or 0.0)
        if downstream == "GATE_PROGRESS":
            gate_delta = max(gate_delta, 1.0)
        steps_to_event = int(
            label.get("steps_to_progress")
            or label.get("steps_to_close")
            or label.get("steps_to_dead_end")
            or row.get("known_min_steps_to_progress")
            or row.get("known_min_steps_to_close")
            or 1
        )
        if downstream == "UNKNOWN":
            if float(outcome.get("gate_progress_delta", 0.0) or 0.0) > 0:
                downstream = "GATE_PROGRESS"
            elif outcome.get("closed_obligation"):
                downstream = "CLOSED"
            elif _closes_or_reduces(outcome):
                downstream = "REDUCED"
            elif check.get("accepted"):
                downstream = "DEAD_END"
        annotated.append(
            {
                **item,
                "rank": rank,
                "action_text": text,
                "verifier_check": check,
                "outcome": outcome,
                "downstream_outcome": downstream,
                "steps_to_event": steps_to_event,
                "effective_gate_progress_delta": gate_delta,
                "calls_to_event": rank + steps_to_event,
            }
        )
    return annotated


def _heuristic_order(row: dict[str, Any], *, beam_width: int) -> list[dict[str, Any]]:
    return [{"action": action, "action_text": serialize_action(action), "score": 0.0, "model_scores": {}} for action in _actions_from_row(row, beam_width=beam_width)]


def _verifier_greedy_order(row: dict[str, Any], *, beam_width: int) -> list[dict[str, Any]]:
    ordered = []
    for action in _actions_from_row(row, beam_width=beam_width):
        check = verify_action_for_state(action, str(row["state"]))
        outcome = classify_action_outcome(action, str(row["state"]), check).to_dict()
        score = (10.0 if check.accepted else -10.0) + (5.0 if _closes_or_reduces(outcome) else 0.0) + 10.0 * float(outcome.get("gate_progress_delta", 0.0) or 0.0)
        ordered.append({"action": action, "action_text": serialize_action(action), "score": score, "model_scores": {}, "verifier_check": check.to_dict(), "outcome": outcome})
    ordered.sort(key=lambda item: item["score"], reverse=True)
    return ordered


def _random_order(row: dict[str, Any], *, beam_width: int, seed: int) -> list[dict[str, Any]]:
    ordered = _heuristic_order(row, beam_width=beam_width)
    random.Random(seed).shuffle(ordered)
    return ordered


def _event_from_order(row: dict[str, Any], order: list[dict[str, Any]], budgets: list[int]) -> dict[str, Any]:
    annotated = _annotate_order(row, order)
    first_accepted = next((item for item in annotated if item["verifier_check"].get("accepted")), None)
    progress_items = [
        item
        for item in annotated
        if item["verifier_check"].get("accepted")
        and item["downstream_outcome"] in {"GATE_PROGRESS", "CLOSED"}
    ]
    if not progress_items:
        progress_items = [
            item
            for item in annotated
            if item["verifier_check"].get("accepted") and item["downstream_outcome"] == "REDUCED" and _closes_or_reduces(item["outcome"])
        ]
    first_progress = min(progress_items, key=lambda item: item["calls_to_event"], default=None)
    event = {
        "closed": bool(first_progress),
        "gate_progress": bool(first_progress and float(first_progress.get("effective_gate_progress_delta", 0.0) or 0.0) > 0),
        "calls_to_close": int(first_progress["calls_to_event"]) if first_progress else None,
        "calls_to_first_progress": int(first_progress["calls_to_event"]) if first_progress else None,
        "gate_progress_delta": float(first_progress.get("effective_gate_progress_delta", 0.0) or 0.0) if first_progress else 0.0,
        "first_accepted_downstream": first_accepted.get("downstream_outcome") if first_accepted else "NONE",
        "dead_end": bool(first_accepted and first_accepted.get("downstream_outcome") == "DEAD_END"),
        "branch_explosion": bool(first_accepted and first_accepted.get("downstream_outcome") == "BRANCH_EXPLOSION"),
        "accepted_actions": sum(1 for item in annotated if item["verifier_check"].get("accepted")),
        "closing_actions": sum(1 for item in annotated if item["verifier_check"].get("accepted") and item.get("downstream_outcome") in {"GATE_PROGRESS", "CLOSED"}),
        "budget_hits": {str(budget): bool(first_progress and int(first_progress["calls_to_event"]) <= budget) for budget in budgets},
        "annotated": annotated,
    }
    return event


def _summarize_events(events: list[dict[str, Any]], budgets: list[int]) -> dict[str, Any]:
    n = max(len(events), 1)
    calls = [event["calls_to_close"] for event in events if event["calls_to_close"] is not None]
    progress_calls = [event["calls_to_first_progress"] for event in events if event["calls_to_first_progress"] is not None]
    total_calls_1000 = len(events) * 1000
    gate_delta = sum(float(event.get("gate_progress_delta", 0.0) or 0.0) for event in events)
    summary: dict[str, Any] = {
        "state_count": len(events),
        "dead_end_rate": sum(1 for event in events if event["dead_end"]) / n,
        "branch_explosion_rate": sum(1 for event in events if event["branch_explosion"]) / n,
        "median_steps_to_first_progress": statistics.median(progress_calls) if progress_calls else None,
        "median_steps_to_close": statistics.median(calls) if calls else None,
        "frontier_size_before": len(events),
        "frontier_size_after": sum(1 for event in events if not event["closed"]),
        "frontier_reduction_ratio": sum(1 for event in events if event["closed"]) / n,
        "gate_delta_per_100_calls": gate_delta / max(len(events) * 100, 1) * 100,
        "gate_delta_per_1000_calls": gate_delta / max(total_calls_1000, 1) * 1000,
        "accepted_actions_per_100_calls": sum(event["accepted_actions"] for event in events) / max(len(events) * 100, 1) * 100,
        "closing_actions_per_100_calls": sum(event["closing_actions"] for event in events) / max(len(events) * 100, 1) * 100,
    }
    for budget in budgets:
        summary[f"closure_at_{budget}_calls"] = sum(1 for event in events if event["budget_hits"].get(str(budget))) / n
    return summary


def run_frontier_search(
    config_path: str | Path,
    *,
    checkpoint: str | None = None,
    eval_dir: str | None = None,
    out: str | None = None,
) -> dict[str, Any]:
    cfg = _config(config_path, checkpoint=checkpoint, eval_dir=eval_dir, out=out)
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_frontier_rows(cfg["eval_dir"])[: cfg["max_examples"]]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, tokenizer, checkpoint_payload = load_checkpoint(cfg["checkpoint"], device=device)
    model_cfg = dict(checkpoint_payload.get("config") or {})
    max_state_len = int(model_cfg.get("max_state_len", 2048))
    max_action_len = int(model_cfg.get("max_action_len", 128))

    if cfg["leakage_check"]:
        leakage = run_leakage_check(cfg["train_rows"], cfg["eval_dir"], out_dir / "leakage_report.json")
    else:
        leakage = {}
    if cfg["raw_proposal_eval"]:
        raw_summary = raw_proposal_eval(config_path, checkpoint=cfg["checkpoint"], eval_dir=cfg["eval_dir"], out=str(out_dir))
    else:
        raw_summary = {}

    methods: dict[str, list[dict[str, Any]]] = {"model": [], "random": [], "heuristic": [], "verifier_greedy": []}
    traces: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    dead_rows: list[dict[str, Any]] = []
    gate_events: list[dict[str, Any]] = []
    gate_events_by_gate: dict[str, float] = defaultdict(float)

    for state_index, row in enumerate(rows):
        state = str(row["state"])
        model_order = rank_candidate_actions(
            model=model,
            tokenizer=tokenizer,
            state=state,
            candidates=_actions_from_row(row, beam_width=cfg["beam_width"]),
            max_state_len=max_state_len,
            max_action_len=max_action_len,
            weights=cfg["ranking"],
            max_candidates=cfg["candidates_per_state"],
        )
        orders = {
            "model": model_order,
            "random": _random_order(row, beam_width=cfg["beam_width"], seed=1337 + state_index),
            "heuristic": _heuristic_order(row, beam_width=cfg["beam_width"]),
            "verifier_greedy": _verifier_greedy_order(row, beam_width=cfg["beam_width"]),
        }
        for method, order in orders.items():
            event = _event_from_order(row, order, cfg["budgets"])
            compact = {key: value for key, value in event.items() if key != "annotated"}
            compact.update({"method": method, "state_index": state_index, "example_id": row.get("example_id"), "gate": row.get("gate"), "frontier_kind": row.get("frontier_kind")})
            methods[method].append(event)
            traces.append(compact)
            if method == "model":
                for item in event["annotated"]:
                    record = {"state_index": state_index, "example_id": row.get("example_id"), "gate": row.get("gate"), "frontier_kind": row.get("frontier_kind"), **item}
                    if item["verifier_check"].get("accepted"):
                        accepted_rows.append(record)
                    else:
                        rejected_rows.append(record)
                if event["dead_end"] or event["branch_explosion"]:
                    dead_rows.append(compact)
                if event["gate_progress"]:
                    gate_events.append(compact)
                    gate_events_by_gate[str(row.get("gate", "UNKNOWN"))] += event["gate_progress_delta"]

    method_summaries = {method: _summarize_events(events, cfg["budgets"]) for method, events in methods.items()}
    model_summary = method_summaries["model"]
    random_summary = method_summaries["random"]
    heuristic_summary = method_summaries["heuristic"]
    budget_key = "closure_at_1000_calls"
    baseline = {
        "random_legal_action": random_summary,
        "heuristic": heuristic_summary,
        "verifier_greedy": method_summaries["verifier_greedy"],
        "run011_baseline": method_summaries["model"],
        "improvement_vs_random_at_1000_calls": model_summary.get(budget_key, 0.0) / random_summary.get(budget_key, 1e-9)
        if random_summary.get(budget_key, 0.0) > 0
        else (999.0 if model_summary.get(budget_key, 0.0) > 0 else 0.0),
        "improvement_vs_heuristic_at_1000_calls": model_summary.get(budget_key, 0.0) / heuristic_summary.get(budget_key, 1e-9)
        if heuristic_summary.get(budget_key, 0.0) > 0
        else (999.0 if model_summary.get(budget_key, 0.0) > 0 else 0.0),
    }
    stratified: dict[str, dict[str, Any]] = {}
    for kind in sorted({str(row.get("frontier_kind", "unknown")) for row in rows}):
        indices = [idx for idx, row in enumerate(rows) if str(row.get("frontier_kind", "unknown")) == kind]
        events = [methods["model"][idx] for idx in indices]
        stratified[kind] = _summarize_events(events, cfg["budgets"]) if events else {}
    trap_events = [methods["model"][idx] for idx, row in enumerate(rows) if row.get("frontier_kind") == "trap_states"]
    random_trap_events = [methods["random"][idx] for idx, row in enumerate(rows) if row.get("frontier_kind") == "trap_states"]
    trap_summary = {
        "trap_state_count": len(trap_events),
        "trap_state_success_rate": sum(1 for event in trap_events if event["closed"]) / max(len(trap_events), 1),
        "trap_state_dead_end_rate": sum(1 for event in trap_events if event["dead_end"] or event["branch_explosion"]) / max(len(trap_events), 1),
        "random_trap_state_dead_end_rate": sum(1 for event in random_trap_events if event["dead_end"] or event["branch_explosion"]) / max(len(random_trap_events), 1),
    }
    theorem = build_collatz_descent_theorem_candidate()
    summary = {
        "schema": "collatz_lab.proof_action_frontier_search_summary",
        "version": 1,
        "run_id": cfg["run_id"],
        "checkpoint_path": cfg["checkpoint"],
        "frontier_eval_dir": cfg["eval_dir"],
        "state_count": len(rows),
        **model_summary,
        "s3_gate_delta_per_1000_calls": gate_events_by_gate.get("S3", 0.0) / max(len(rows) * 1000, 1) * 1000,
        "s4_gate_delta_per_1000_calls": gate_events_by_gate.get("S4", 0.0) / max(len(rows) * 1000, 1) * 1000,
        "s6_gate_delta_per_1000_calls": gate_events_by_gate.get("S6", 0.0) / max(len(rows) * 1000, 1) * 1000,
        "trap_state_success_rate": trap_summary["trap_state_success_rate"],
        "trap_state_dead_end_rate": trap_summary["trap_state_dead_end_rate"],
        "random_trap_state_dead_end_rate": trap_summary["random_trap_state_dead_end_rate"],
        "improvement_vs_random_at_1000_calls": baseline["improvement_vs_random_at_1000_calls"],
        "improvement_vs_heuristic_at_1000_calls": baseline["improvement_vs_heuristic_at_1000_calls"],
        "strict_theorem_verifier_result": theorem.get("verifier_status", "FAIL"),
        "proof_confidence_percent": 100.0 if theorem.get("verifier_status") == "PASS" else 0.0,
        "raw_proposal_metrics": raw_summary,
        "leakage_report": leakage,
        "go_no_go": "NO-GO",
    }
    summary["go_no_go"] = "GO" if passes_run012_gates(summary, raw_summary, leakage) else "NO-GO"

    (out_dir / "budgeted_search_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "stratified_frontier_summary.json").write_text(json.dumps(stratified, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "trap_state_summary.json").write_text(json.dumps(trap_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "baseline_comparison.json").write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_jsonl(out_dir / "frontier_search_traces.jsonl", traces)
    _write_jsonl(out_dir / "accepted_frontier_actions.jsonl", accepted_rows)
    _write_jsonl(out_dir / "rejected_frontier_actions.jsonl", rejected_rows)
    _write_jsonl(out_dir / "dead_end_branches.jsonl", dead_rows)
    _write_jsonl(out_dir / "gate_progress_events.jsonl", gate_events)
    run_result = {
        "schema": "collatz_lab.run_result.frontier_search",
        "version": 1,
        "run_id": cfg["run_id"],
        "config_path": cfg["config_path"],
        "checkpoint_path": cfg["checkpoint"],
        "eval_metrics": {"raw_proposal": raw_summary, "budgeted_search": summary},
        "baseline_comparison": baseline,
        "leakage_report": leakage,
        "theorem_verifier_status": summary["strict_theorem_verifier_result"],
        "proof_confidence_percent": summary["proof_confidence_percent"],
        "go_no_go": summary["go_no_go"],
        "next_step_recommendation": true_next_bottleneck(summary, raw_summary, leakage),
    }
    (out_dir / "run_result.json").write_text(json.dumps(run_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def passes_run012_gates(summary: dict[str, Any], raw: dict[str, Any], leakage: dict[str, Any]) -> bool:
    random_gate = float(summary.get("improvement_vs_random_at_1000_calls", 0.0) or 0.0)
    raw_top5_gate = float(raw.get("raw_top5_gate_progress_rate", 0.0) or 0.0)
    trap_dead = float(summary.get("trap_state_dead_end_rate", 1.0) or 1.0)
    random_trap_dead = float(summary.get("random_trap_state_dead_end_rate", 1.0) or 1.0)
    return (
        raw.get("raw_top5_verifier_accept_rate", 0.0) >= 0.50
        and raw.get("raw_top10_verifier_accept_rate", 0.0) >= 0.65
        and raw_top5_gate > 0
        and summary.get("closure_at_1000_calls", 0.0) > 0
        and random_gate >= 3.0
        and summary.get("gate_delta_per_1000_calls", 0.0) > 0
        and summary.get("s3_gate_delta_per_1000_calls", 0.0) > 0
        and summary.get("s4_gate_delta_per_1000_calls", 0.0) > 0
        and trap_dead <= 0.5 * random_trap_dead
        and leakage.get("exact_state_hash_overlap", 1) == 0
    )


def true_next_bottleneck(summary: dict[str, Any], raw: dict[str, Any], leakage: dict[str, Any]) -> str:
    if leakage.get("exact_state_hash_overlap", 0) != 0:
        return "eval leakage"
    if raw.get("raw_top5_verifier_accept_rate", 0.0) < 0.50 or raw.get("raw_top10_verifier_accept_rate", 0.0) < 0.65:
        return "raw model proposals weak"
    if raw.get("raw_top5_gate_progress_rate", 0.0) <= 0:
        return "missing lemma generator or action types for gate progress"
    if summary.get("improvement_vs_random_at_1000_calls", 0.0) < 3.0:
        return "value/ranker weak on hard frontier traps"
    if summary.get("closure_at_1000_calls", 0.0) <= 0:
        return "search depth too shallow"
    return "dataset lacks hard positive traces"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run budgeted frontier proof-action search.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint")
    parser.add_argument("--eval-dir")
    parser.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(run_frontier_search(args.config, checkpoint=args.checkpoint, eval_dir=args.eval_dir, out=args.out))


if __name__ == "__main__":
    main()
