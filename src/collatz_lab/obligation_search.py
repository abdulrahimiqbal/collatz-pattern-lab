"""Run obligation-conditioned proof search.

This is the proof-progress pivot: the search unit is an open proof obligation,
the action space is the proof-action DSL, and the reward comes from exact
verifier-backed action results.  Local Collatz certificates are useful only
when they close or reduce obligations in the persistent proof graph.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_controller import run_fixed_point_controller
from .proof_graph import graph_summary, write_graph_json, write_graph_markdown
from .proof_policy import open_obligations
from .proof_policy_model import build_training_report, save_policy_model, train_policy_from_traces
from .proof_schema import status_is_closed
from .proof_trace import ProofTrace, write_traces


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _normal_status(row: dict[str, Any]) -> str:
    return str(row.get("scc_status", row.get("status", "UNKNOWN")))


def _normal_obligation(row: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(row)
    normalized.setdefault("status", _normal_status(row))
    normalized.setdefault("scc_status", normalized["status"])
    normalized.setdefault("coverage", {})
    normalized.setdefault("scope", normalized.get("claim", ""))
    return normalized


def merge_obligation_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge obligation reports without duplicating obligation ids."""

    obligations: dict[str, dict[str, Any]] = {}
    for report in reports:
        for row in report.get("obligations", []):
            oid = str(row.get("obligation_id"))
            if not oid or oid == "None":
                continue
            candidate = _normal_obligation(row)
            existing = obligations.get(oid)
            if existing is None:
                obligations[oid] = candidate
                continue
            if status_is_closed(_normal_status(existing)) and not status_is_closed(_normal_status(candidate)):
                continue
            obligations[oid] = candidate
    rows = list(obligations.values())
    open_rows = [row for row in rows if _normal_status(row) in {"NEEDS_SPLIT", "UNKNOWN"}]
    return {
        "scope": "merged obligation-conditioned proof-search environment",
        "status": "INCOMPLETE_OPEN_OBLIGATIONS" if open_rows else "PASS",
        "obligation_count": len(rows),
        "open_obligation_count": len(open_rows),
        "closed_obligation_count": len(rows) - len(open_rows),
        "obligations": rows,
    }


def _closed_ids(graph: dict[str, Any]) -> set[str]:
    return {
        node_id
        for node_id, node in graph.get("nodes", {}).items()
        if status_is_closed(str(node.get("status")))
    }


def _open_ids(graph: dict[str, Any]) -> set[str]:
    return set(graph.get("nodes", {})) - _closed_ids(graph)


def compare_graphs(baseline_graph: dict[str, Any], candidate_graph: dict[str, Any]) -> dict[str, Any]:
    """Compare candidate closure against the existing persistent graph."""

    baseline_nodes = set(baseline_graph.get("nodes", {}))
    baseline_open = _open_ids(baseline_graph)
    candidate_closed = _closed_ids(candidate_graph)
    newly_closed_existing = sorted(baseline_open & candidate_closed)
    new_nodes = sorted(set(candidate_graph.get("nodes", {})) - baseline_nodes)
    new_closed_nodes = sorted(set(new_nodes) & candidate_closed)
    baseline_summary = graph_summary(baseline_graph)
    candidate_summary = graph_summary(candidate_graph)
    baseline_total = max(1, int(baseline_summary.get("node_count", 0)))
    return {
        "baseline_graph_summary": baseline_summary,
        "candidate_graph_summary": candidate_summary,
        "new_nodes": len(new_nodes),
        "new_closed_nodes": len(new_closed_nodes),
        "newly_closed_existing_obligations": newly_closed_existing,
        "newly_closed_existing_count": len(newly_closed_existing),
        "comparable_existing_graph_progress_delta_percent": 100.0 * len(newly_closed_existing) / baseline_total,
        "candidate_raw_progress_percent": (
            0.0
            if candidate_summary.get("node_count", 0) == 0
            else 100.0 * candidate_summary.get("closed_count", 0) / candidate_summary["node_count"]
        ),
        "baseline_raw_progress_percent": (
            0.0
            if baseline_summary.get("node_count", 0) == 0
            else 100.0 * baseline_summary.get("closed_count", 0) / baseline_summary["node_count"]
        ),
    }


def _trace_counts(traces: list[ProofTrace]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    proof_status_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    reward_total = 0
    for trace in traces:
        status_counts[trace.result.status] = status_counts.get(trace.result.status, 0) + 1
        proof_status_counts[trace.result.proof_status] = proof_status_counts.get(trace.result.proof_status, 0) + 1
        action_counts[trace.action.action] = action_counts.get(trace.action.action, 0) + 1
        reward_total += trace.result.reward
    useful = status_counts.get("CLOSED", 0) + status_counts.get("REDUCED", 0)
    return {
        "trace_count": len(traces),
        "action_counts": action_counts,
        "result_counts": status_counts,
        "proof_status_counts": proof_status_counts,
        "reward_total": reward_total,
        "useful_action_rate": 0.0 if not traces else useful / len(traces),
    }


def write_obligation_search_markdown(report: dict[str, Any], out: str | Path) -> None:
    comparison = report["graph_comparison"]
    lines = [
        "# Obligation-Conditioned Proof Search",
        "",
        f"- status: `{report['status']}`",
        f"- policy: `{report['policy']}`",
        f"- seed traces: `{report['seed_trace_summary']['trace_count']}`",
        f"- model-reranked traces: `{report['controller_report']['actions_tried']}`",
        f"- baseline proof progress: `{comparison['baseline_raw_progress_percent']:.4f}%`",
        f"- candidate raw graph progress: `{comparison['candidate_raw_progress_percent']:.4f}%`",
        f"- newly closed existing obligations: `{comparison['newly_closed_existing_count']}`",
        f"- comparable progress delta: `{comparison['comparable_existing_graph_progress_delta_percent']:.4f}%`",
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
        "## Next Step",
        "",
        report["next_step"],
        "",
    ]
    if comparison["newly_closed_existing_obligations"]:
        lines.extend(["## Closed Existing Obligations", ""])
        for oid in comparison["newly_closed_existing_obligations"]:
            lines.append(f"- `{oid}`")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_obligation_search(
    obligation_reports: list[dict[str, Any]],
    baseline_graph: dict[str, Any],
    out_dir: str | Path,
    beam_size: int = 8,
    max_rounds: int = 2,
    seed_rounds: int | None = None,
) -> dict[str, Any]:
    """Train a proof-action value model and run model-reranked proof search."""

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    merged = merge_obligation_reports(obligation_reports)
    (out / "merged_obligations.json").write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    seed_rounds = max_rounds if seed_rounds is None else seed_rounds
    seed_report, seed_traces, _seed_graph = run_fixed_point_controller(
        merged,
        beam_size=beam_size,
        max_rounds=seed_rounds,
    )
    write_traces(out / "seed_traces.jsonl", seed_traces)

    model_bundle = train_policy_from_traces(seed_traces)
    save_policy_model(out / "proof_policy_value_model.pkl", model_bundle)
    model_report = build_training_report(model_bundle)
    (out / "proof_policy_value_model.json").write_text(
        json.dumps(model_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    controller_report, traces, graph = run_fixed_point_controller(
        merged,
        beam_size=beam_size,
        max_rounds=max_rounds,
        value_model_bundle=model_bundle,
    )
    write_traces(out / "traces.jsonl", traces)
    write_graph_json(graph, out / "proof_graph_candidate.json")
    write_graph_markdown(graph, out / "proof_graph_candidate.md")

    comparison = compare_graphs(baseline_graph, graph)
    trace_summary = _trace_counts(traces)
    existing_closed = comparison["newly_closed_existing_count"]
    status = (
        "OBLIGATION_SEARCH_CLOSED_EXISTING_GRAPH_NODES"
        if existing_closed > 0
        else "OBLIGATION_SEARCH_NO_EXISTING_GRAPH_CLOSURE"
    )
    report = {
        "status": status,
        "policy": "seed_heuristic_then_value_model_rerank",
        "beam_size": beam_size,
        "max_rounds": max_rounds,
        "seed_rounds": seed_rounds,
        "input_obligation_count": merged["obligation_count"],
        "input_open_obligation_count": merged["open_obligation_count"],
        "seed_report": seed_report,
        "seed_trace_summary": _trace_counts(seed_traces),
        "model_report": model_report,
        "controller_report": controller_report,
        "trace_summary": trace_summary,
        "graph_comparison": comparison,
        "full_obligations_closed_by_policy": existing_closed,
        "model_guided_obligation_closure_rate": 0.0 if not open_obligations(merged) else existing_closed / len(open_obligations(merged)),
        "useful_action_rate": trace_summary["useful_action_rate"],
        "interpretation": (
            "This run changes the search target from local certificate volume to verifier-backed "
            "proof actions over open obligations. The comparable proof-progress delta counts only "
            "previously-open persistent graph nodes that became closed."
        ),
        "next_step": (
            "Add new exact action classes for parent-state transition templates and promote only "
            "actions that close existing graph nodes."
            if existing_closed == 0
            else "Promote the newly closed graph nodes into the theorem candidate, then rerun the strict verifier."
        ),
    }
    report_path = out / "obligation_search_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_obligation_search_markdown(report, out / "obligation_search_report.md")
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run obligation-conditioned proof search.")
    parser.add_argument("--obligations", action="append", required=True)
    parser.add_argument("--baseline-graph", default="reports/proof_graph_latest.json")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--beam-size", type=int, default=8)
    parser.add_argument("--max-rounds", type=int, default=2)
    parser.add_argument("--seed-rounds", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    reports = [load_json(path) for path in args.obligations]
    baseline_graph = load_json(args.baseline_graph)
    report = run_obligation_search(
        reports,
        baseline_graph,
        out_dir=args.out_dir,
        beam_size=args.beam_size,
        max_rounds=args.max_rounds,
        seed_rounds=args.seed_rounds,
    )
    Console().print(
        {
            "out": str(Path(args.out_dir) / "obligation_search_report.json"),
            "status": report["status"],
            "actions": report["controller_report"]["actions_tried"],
            "newly_closed_existing": report["graph_comparison"]["newly_closed_existing_count"],
            "useful_action_rate": report["useful_action_rate"],
        }
    )


if __name__ == "__main__":
    main()
