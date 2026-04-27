"""Weighted proof-progress accounting.

The persistent proof graph is useful for strict dependency tracking, but plain
node counts are a poor progress metric: one enormous frontier bucket and one
tiny generated child both count as one node.  This module reports progress with
explicit numerators, denominators, sources, and diagnostic scope.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import h_star
from .split_executor import split_parent_bucket_by_parent_level


_DUPLICATE_SUFFIX_RE = re.compile(r"#\d+$")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _percent(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else 100.0 * numerator / denominator


def canonical_obligation_id(obligation_id: str) -> str:
    """Strip generated duplicate suffixes such as ``#2`` from graph ids."""

    return _DUPLICATE_SUFFIX_RE.sub("", obligation_id)


def canonical_graph_summary(graph: dict[str, Any]) -> dict[str, Any]:
    """Summarize graph progress after duplicate-id canonicalization."""

    nodes = graph.get("nodes", {})
    canonical: dict[str, dict[str, int]] = {}
    for node_id, node in nodes.items():
        base = canonical_obligation_id(str(node_id))
        status = str(node.get("status", "UNKNOWN"))
        row = canonical.setdefault(base, {"total": 0, "closed": 0, "open": 0})
        row["total"] += 1
        if status.startswith("CLOSED_BY_"):
            row["closed"] += 1
        else:
            row["open"] += 1
    closed_bases = [base for base, row in canonical.items() if row["open"] == 0 and row["closed"] > 0]
    open_bases = [base for base, row in canonical.items() if row["open"] > 0]
    duplicate_groups = [
        {"obligation_id": base, **row}
        for base, row in sorted(canonical.items())
        if row["total"] > 1
    ]
    return {
        "canonical_node_count": len(canonical),
        "canonical_closed_count": len(closed_bases),
        "canonical_open_count": len(open_bases),
        "canonical_progress_percent": _percent(len(closed_bases), len(canonical)),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_groups_sample": duplicate_groups[:30],
    }


def _strict_graph_breakdown(graph: dict[str, Any], source: str) -> dict[str, Any]:
    summary = graph.get("summary") or {}
    closed = int(summary.get("closed_count", len(graph.get("closed", []))))
    total = int(summary.get("node_count", len(graph.get("nodes", {}))))
    return {
        "metric": "strict_persistent_graph_node_closure",
        "source": source,
        "numerator": closed,
        "denominator": total,
        "percent": _percent(closed, total),
        "status": "diagnostic_only_not_proof_confidence",
        "note": "Unweighted graph node closure; duplicates and tiny generated children count equally.",
    }


def _weighted_frontier_breakdown(residual: dict[str, Any], source: str) -> dict[str, Any]:
    certified = int(residual.get("total_certified_q_classes", 0) or 0)
    total = int(residual.get("total_q_classes", 0) or 0)
    unknown = int(residual.get("residual_unknown_q_classes", max(0, total - certified)) or 0)
    return {
        "metric": "weighted_p6_finite_frontier_coverage",
        "source": source,
        "numerator": certified,
        "denominator": total,
        "unknown": unknown,
        "percent": _percent(certified, total),
        "unknown_percent": _percent(unknown, total),
        "status": "finite_depth_diagnostic_not_global_proof",
        "note": "Weighted by q-classes inside n=64*q-1 at the current finite q-depth.",
    }


def _parent_split_for_bucket(row: dict[str, Any], r_depth: int = 7) -> dict[str, Any]:
    a = int(row["a"])
    h = int(row["h"])
    split = split_parent_bucket_by_parent_level(a=a, h=h, r_depth=r_depth)
    children = [
        {
            "a_next": int(child["coverage"]["a_next"]),
            "residue_count": int(child["coverage"]["residue_count"]),
            "relation": (
                "self"
                if int(child["coverage"]["a_next"]) == a
                else "lower"
                if int(child["coverage"]["a_next"]) < a
                else "higher"
            ),
        }
        for child in split.get("children", [])
    ]
    return {
        "r_depth": r_depth,
        "children": children,
        "self_transition_residue_count": sum(child["residue_count"] for child in children if child["relation"] == "self"),
        "lower_transition_residue_count": sum(child["residue_count"] for child in children if child["relation"] == "lower"),
        "higher_transition_residue_count": sum(child["residue_count"] for child in children if child["relation"] == "higher"),
    }


def weighted_bucket_targets(
    residual: dict[str, Any],
    frontier_strata: dict[str, Any],
    top_n: int = 12,
) -> list[dict[str, Any]]:
    """Return top unknown buckets with cumulative weighted progress if closed."""

    total = int(residual.get("total_q_classes", 0) or 0)
    certified = int(residual.get("total_certified_q_classes", 0) or 0)
    cumulative = certified
    targets: list[dict[str, Any]] = []
    for index, row in enumerate(frontier_strata.get("top_unresolved_buckets", [])[:top_n], start=1):
        count = int(row.get("count_unknown", 0) or 0)
        cumulative += count
        a = int(row["a"])
        h = int(row["h"])
        threshold = h_star(a)
        parent_split = _parent_split_for_bucket(row)
        targets.append(
            {
                "rank": index,
                "obligation_id": f"unresolved_bucket:t={row['t']}:a={a}:h={h}",
                "t": int(row["t"]),
                "a": a,
                "h": h,
                "unknown_q_classes": count,
                "bucket_weight_percent": _percent(count, total),
                "cumulative_certified_if_closed": cumulative,
                "cumulative_progress_if_closed_percent": _percent(cumulative, total),
                "direct_burst_descent_threshold_h": threshold,
                "direct_burst_descent_available": h >= threshold,
                "parent_transition_split": parent_split,
                "missing_executor": (
                    "direct_burst_descent"
                    if h >= threshold
                    else "parent_state_transition_ranking_or_induction"
                ),
            }
        )
    return targets


def build_weighted_progress_report(
    residual_frontier: dict[str, Any],
    frontier_strata: dict[str, Any],
    proof_graph: dict[str, Any],
    residual_source: str,
    strata_source: str,
    graph_source: str,
    top_n: int = 12,
) -> dict[str, Any]:
    weighted = _weighted_frontier_breakdown(residual_frontier, residual_source)
    strict = _strict_graph_breakdown(proof_graph, graph_source)
    canonical = canonical_graph_summary(proof_graph)
    targets = weighted_bucket_targets(residual_frontier, frontier_strata, top_n=top_n)
    return {
        "status": "WEIGHTED_PROGRESS_DIAGNOSTIC",
        "proof_progress_metric": weighted["metric"],
        "proof_progress_percent": weighted["percent"],
        "proof_progress_breakdown": {
            "selected": weighted,
            "strict_graph": strict,
            "canonicalized_graph": canonical,
        },
        "target_buckets": targets,
        "first_bucket_progress_if_closed_percent": targets[0]["cumulative_progress_if_closed_percent"] if targets else weighted["percent"],
        "second_bucket_progress_if_closed_percent": targets[1]["cumulative_progress_if_closed_percent"] if len(targets) > 1 else None,
        "model_guided_obligation_closure_rate": 0.0,
        "useful_action_rate": 0.0,
        "interpretation": (
            "The selected progress number is weighted finite-frontier coverage for the P6 "
            "laboratory. It is a proof-progress diagnostic, not proof confidence. Strict "
            "proof confidence remains verifier-gated."
        ),
        "next_step": (
            "Implement exact parent-state transition ranking/induction for the top weighted "
            "low-h buckets; closing the top two weighted buckets would exceed 60% finite P6 coverage."
        ),
    }


def write_weighted_progress_markdown(report: dict[str, Any], out: str | Path) -> None:
    selected = report["proof_progress_breakdown"]["selected"]
    strict = report["proof_progress_breakdown"]["strict_graph"]
    canonical = report["proof_progress_breakdown"]["canonicalized_graph"]
    lines = [
        "# Weighted Proof Progress",
        "",
        f"- selected metric: `{report['proof_progress_metric']}`",
        f"- selected progress: `{report['proof_progress_percent']:.6f}%`",
        f"- selected numerator: `{selected['numerator']}`",
        f"- selected denominator: `{selected['denominator']}`",
        f"- selected source: `{selected['source']}`",
        f"- selected status: `{selected['status']}`",
        "",
        "## Strict Graph Comparator",
        "",
        f"- strict graph progress: `{strict['percent']:.6f}%`",
        f"- strict graph numerator: `{strict['numerator']}`",
        f"- strict graph denominator: `{strict['denominator']}`",
        f"- strict graph source: `{strict['source']}`",
        f"- canonicalized graph progress: `{canonical['canonical_progress_percent']:.6f}%`",
        f"- canonicalized nodes: `{canonical['canonical_node_count']}`",
        f"- canonicalized closed: `{canonical['canonical_closed_count']}`",
        f"- duplicate groups: `{canonical['duplicate_group_count']}`",
        "",
        "## Top Weighted Targets",
        "",
        "| rank | obligation | q-classes | weight | cumulative if closed | missing executor |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in report["target_buckets"]:
        lines.append(
            f"| {row['rank']} | `{row['obligation_id']}` | `{row['unknown_q_classes']}` | "
            f"`{row['bucket_weight_percent']:.6f}%` | "
            f"`{row['cumulative_progress_if_closed_percent']:.6f}%` | "
            f"`{row['missing_executor']}` |"
        )
    lines.extend(["", "## Interpretation", "", report["interpretation"], "", "## Next Step", "", report["next_step"], ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build weighted proof-progress diagnostics.")
    parser.add_argument("--residual-frontier", default="reports/residual_frontier_63mod64_q20.json")
    parser.add_argument("--frontier-strata", default="reports/frontier_strata_63mod64_q20.json")
    parser.add_argument("--proof-graph", default="reports/proof_graph_latest.json")
    parser.add_argument("--top-n", type=int, default=12)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_weighted_progress_report(
        load_json(args.residual_frontier),
        load_json(args.frontier_strata),
        load_json(args.proof_graph),
        residual_source=args.residual_frontier,
        strata_source=args.frontier_strata,
        graph_source=args.proof_graph,
        top_n=args.top_n,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_weighted_progress_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "proof_progress_percent": report["proof_progress_percent"],
            "second_bucket_progress_if_closed_percent": report["second_bucket_progress_if_closed_percent"],
        }
    )


if __name__ == "__main__":
    main()
