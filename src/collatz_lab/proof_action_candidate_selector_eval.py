"""Evaluate a trained listwise proof-action candidate selector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_candidate_selector import candidate_utility, infer_target_objective, objective_threshold
from .proof_action_frontier_eval import add_normalized_selector_metrics, raw_proposal_eval
from .proof_action_frontier_search import passes_run015a_gates, run_frontier_search
from .utils import load_yaml


def _read_jsonl(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    data_path = Path(path)
    if not data_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in data_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def candidate_set_oracle_metrics(path: str | Path | None) -> dict[str, Any]:
    rows = _read_jsonl(path)
    by_objective: dict[str, dict[str, float]] = {}
    available = 0
    for row in rows:
        target_objective = str(row.get("target_objective") or infer_target_objective(row))
        threshold = objective_threshold(target_objective)
        bucket = by_objective.setdefault(target_objective, {"count": 0.0, "available": 0.0})
        bucket["count"] += 1.0
        row_available = any(
            candidate_utility(candidate, target_objective) >= threshold
            for candidate in row.get("candidates") or []
            if isinstance(candidate, dict)
        )
        if row_available:
            available += 1
            bucket["available"] += 1.0
    return {
        "candidate_set_count": len(rows),
        "oracle_available_rate": available / max(len(rows), 1),
        "oracle_available_rate_by_objective": {
            objective: values["available"] / max(values["count"], 1.0)
            for objective, values in by_objective.items()
        },
        "oracle_count_by_objective": {
            objective: int(values["count"])
            for objective, values in by_objective.items()
        },
    }


def selector_go_no_go(summary: dict[str, Any]) -> bool:
    raw = summary.get("raw_proposal_metrics") or {}
    return (
        float(summary.get("candidate_selector_hard_holdout_oracle_available_rate", 0.0) or 0.0) >= 0.95
        and passes_run015a_gates(summary, raw, summary.get("leakage_report", {}) or {})
    )


def evaluate_candidate_selector(
    config_path: str | Path,
    *,
    checkpoint: str | None = None,
    eval_dir: str | None = None,
    out: str | None = None,
) -> dict[str, Any]:
    out_dir = Path(out or "reports/runs/RUN-015A-proof-action-v2-listwise-selector-small-a100")
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_yaml(config_path)
    hard_holdout_metrics = candidate_set_oracle_metrics((cfg.get("data") or {}).get("hard_holdout_candidate_sets"))
    raw_summary = raw_proposal_eval(config_path, checkpoint=checkpoint, eval_dir=eval_dir, out=str(out_dir))
    add_normalized_selector_metrics(raw_summary)
    search_summary = run_frontier_search(config_path, checkpoint=checkpoint, eval_dir=eval_dir, out=str(out_dir))
    raw_objective_rates = raw_summary.get("oracle_available_rate_by_objective") or {}
    summary = {
        "schema": "collatz_lab.proof_action_candidate_selector_eval",
        "version": 1,
        "raw_proposal_metrics": raw_summary,
        "budgeted_search": search_summary,
        "leakage_report": search_summary.get("leakage_report", {}),
        "candidate_selector_hard_holdout_oracle": hard_holdout_metrics,
        "candidate_selector_hard_holdout_oracle_available_rate": hard_holdout_metrics["oracle_available_rate"],
        "candidate_selector_hard_holdout_oracle_available_rate_by_objective": hard_holdout_metrics[
            "oracle_available_rate_by_objective"
        ],
        "gate_progress_objective_oracle_available_rate": float(raw_objective_rates.get("GATE_PROGRESS", 0.0) or 0.0),
        "s6_objective_oracle_available_rate": float(raw_objective_rates.get("S6_BLOCKER_REDUCE", 0.0) or 0.0),
        "trap_avoidance_oracle_available_rate": float(raw_objective_rates.get("TRAP_AVOIDANCE", 0.0) or 0.0),
        **{
            key: value
            for key, value in raw_summary.items()
            if key
            in {
                "selector_top5_gate_progress_oracle_recall",
                "selector_mrr_gate_progress_oracle_normalized",
                "normalized_policy_regret",
            }
        },
        **{
            key: value
            for key, value in search_summary.items()
            if key.startswith(("closure_at_", "improvement_vs_", "s3_", "s4_", "s6_"))
            or key
            in {
                "model_budget_to_80pct_closure",
                "random_budget_to_80pct_closure",
                "heuristic_budget_to_80pct_closure",
                "speedup_to_80pct_vs_random",
                "speedup_to_80pct_vs_heuristic",
                "baseline_saturates_by_25_calls",
            }
        },
    }
    summary["go_no_go"] = "GO" if selector_go_no_go(summary) else "NO-GO"
    (out_dir / "candidate_selector_eval_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate proof-action listwise candidate selector.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint")
    parser.add_argument("--eval-dir")
    parser.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(evaluate_candidate_selector(args.config, checkpoint=args.checkpoint, eval_dir=args.eval_dir, out=args.out))


if __name__ == "__main__":
    main()
