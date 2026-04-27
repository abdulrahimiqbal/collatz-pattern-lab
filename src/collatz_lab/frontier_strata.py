"""Stratify the residual ``n = 64*q - 1`` frontier by burst variables."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from rich.console import Console
from tqdm import tqdm

from .burst import (
    burst_division_exponent,
    burst_post_division_value,
    decompose_q,
    h_star,
)
from .residual_frontier import (
    STATUS_CERTIFIED_RESIDUAL_DESCENT,
    STATUS_COVERED_BY_EXISTING_CUBE,
    STATUS_UNKNOWN_RESIDUAL,
    classify_q_residue,
    mark_existing_cube_coverage,
)

STATUS_NAMES = {
    STATUS_COVERED_BY_EXISTING_CUBE: "already_cube_covered",
    STATUS_CERTIFIED_RESIDUAL_DESCENT: "residual_certified",
    STATUS_UNKNOWN_RESIDUAL: "unknown",
}


def default_theorem_candidate_path() -> Path | None:
    path = Path("reports/theorem_candidate_63mod64_cubes.json")
    return path if path.exists() else None


def load_candidate(path: str | Path | None) -> dict[str, Any] | None:
    chosen = Path(path) if path else default_theorem_candidate_path()
    if chosen is None or not chosen.exists():
        return None
    return json.loads(chosen.read_text(encoding="utf-8"))


def representative_q(q_residue: int, q_depth: int) -> int:
    """Return a positive representative for a finite q residue class."""

    if q_depth < 0:
        raise ValueError("q_depth must be non-negative")
    return q_residue if q_residue > 0 else 1 << q_depth


def classify_all_q(
    q_depth: int,
    burst_length: int = 6,
    max_steps: int = 120,
    candidate: dict[str, Any] | None = None,
    show_progress: bool = False,
) -> tuple[bytearray, dict[int, dict[str, Any]]]:
    """Classify every q-class at fixed depth.

    Existing theorem-candidate cubes are marked first. Remaining classes are
    classified with the existing residual-frontier affine descent verifier.
    """

    total = 1 << q_depth
    if candidate is not None:
        statuses, _ = mark_existing_cube_coverage(candidate, q_depth)
    else:
        statuses = bytearray(total)
    certified_results: dict[int, dict[str, Any]] = {}
    iterator = range(total)
    if show_progress:
        iterator = tqdm(iterator, desc=f"stratify q-frontier 2^{q_depth}")  # type: ignore[assignment]
    for q_residue in iterator:
        if statuses[q_residue] == STATUS_COVERED_BY_EXISTING_CUBE:
            continue
        result = classify_q_residue(q_residue, q_depth, burst_length=burst_length, max_steps=max_steps)
        if result["status"] == "CERTIFIED_DESCENT":
            statuses[q_residue] = STATUS_CERTIFIED_RESIDUAL_DESCENT
            certified_results[q_residue] = result
        else:
            statuses[q_residue] = STATUS_UNKNOWN_RESIDUAL
    return statuses, certified_results


def burst_features_for_q_residue(q_residue: int, q_depth: int) -> dict[str, Any]:
    q = representative_q(q_residue, q_depth)
    t, a, r = decompose_q(q)
    h = burst_division_exponent(a, r)
    h_threshold = h_star(a)
    post_value = burst_post_division_value(a, r)
    returns = post_value % 64 == 63
    return {
        "q_residue": q_residue,
        "q_representative": q,
        "q_zero_residue_represented_by_modulus": q_residue == 0,
        "t": t,
        "a": a,
        "r": r,
        "h": h,
        "h_star": h_threshold,
        "burst_escape": h >= h_threshold,
        "post_burst_value": post_value,
        "post_burst_mod_64": post_value % 64,
        "returns_to_parent": returns,
        "leaves_parent": not returns,
    }


def _percent(part: int, total: int) -> float:
    return 0.0 if total == 0 else part / total * 100.0


def build_frontier_strata_report(
    q_depth: int,
    residual_report: dict[str, Any] | None = None,
    candidate: dict[str, Any] | None = None,
    burst_length: int = 6,
    max_steps: int = 120,
    show_progress: bool = False,
) -> dict[str, Any]:
    statuses, certified_results = classify_all_q(
        q_depth,
        burst_length=burst_length,
        max_steps=max_steps,
        candidate=candidate,
        show_progress=show_progress,
    )

    by_t: dict[tuple[int, int], dict[str, Any]] = {}
    by_a_h: dict[tuple[int, int], dict[str, Any]] = {}
    unknown_buckets: Counter[tuple[int, int, int]] = Counter()
    unknown_outcome_states: Counter[tuple[int, int, int, int, bool]] = Counter()
    unknown_recursive_states: Counter[tuple[int, int, int, int, int, bool]] = Counter()
    status_counts = Counter(statuses)

    for q_residue, status in enumerate(statuses):
        features = burst_features_for_q_residue(q_residue, q_depth)
        t = int(features["t"])
        a = int(features["a"])
        h = int(features["h"])
        status_name = STATUS_NAMES.get(status, "unclassified")

        row_t = by_t.setdefault(
            (t, a),
            {
                "t": t,
                "a": a,
                "count": 0,
                "already_cube_covered": 0,
                "residual_certified": 0,
                "unknown": 0,
                "burst_escape_count": 0,
                "return_to_parent_count": 0,
                "leaves_parent_count": 0,
            },
        )
        row_t["count"] += 1
        row_t[status_name] += 1
        if features["burst_escape"]:
            row_t["burst_escape_count"] += 1
        if features["returns_to_parent"]:
            row_t["return_to_parent_count"] += 1
        else:
            row_t["leaves_parent_count"] += 1

        row_h = by_a_h.setdefault(
            (a, h),
            {
                "a": a,
                "h": h,
                "count": 0,
                "certified": 0,
                "unknown": 0,
                "already_cube_covered": 0,
                "burst_escape": h >= int(features["h_star"]),
                "returns_to_parent_count": 0,
                "leaves_parent_count": 0,
            },
        )
        row_h["count"] += 1
        if status == STATUS_UNKNOWN_RESIDUAL:
            row_h["unknown"] += 1
            unknown_buckets[(t, a, h)] += 1
            unknown_outcome_states[
                (t, a, h, int(features["post_burst_mod_64"]), bool(features["returns_to_parent"]))
            ] += 1
            unknown_recursive_states[
                (
                    t,
                    a,
                    h,
                    int(features["post_burst_mod_64"]),
                    q_residue % 64,
                    bool(features["returns_to_parent"]),
                )
            ] += 1
        elif status == STATUS_CERTIFIED_RESIDUAL_DESCENT:
            row_h["certified"] += 1
        elif status == STATUS_COVERED_BY_EXISTING_CUBE:
            row_h["already_cube_covered"] += 1
            row_h["certified"] += 1
        if features["returns_to_parent"]:
            row_h["returns_to_parent_count"] += 1
        else:
            row_h["leaves_parent_count"] += 1

    by_t_rows = []
    for row in by_t.values():
        row["unknown_percent"] = _percent(int(row["unknown"]), int(row["count"]))
        by_t_rows.append(row)
    by_t_rows.sort(key=lambda row: (row["t"], row["a"]))

    by_a_h_rows = list(by_a_h.values())
    by_a_h_rows.sort(key=lambda row: (row["a"], row["h"]))

    top_unresolved = []
    for (t, a, h), count in unknown_buckets.most_common(40):
        bucket_total = by_a_h[(a, h)]["count"]
        top_unresolved.append(
            {
                "t": t,
                "a": a,
                "h": h,
                "count_unknown": count,
                "unknown_percent": _percent(count, int(bucket_total)),
            }
        )

    total_unknown = int(status_counts[STATUS_UNKNOWN_RESIDUAL])
    top_outcome_states = [
        {
            "t": t,
            "a": a,
            "h": h,
            "post_burst_mod_64": post_mod,
            "returns_to_parent": returns,
            "count_unknown": count,
            "percent_of_unknown": _percent(count, total_unknown),
        }
        for (t, a, h, post_mod, returns), count in unknown_outcome_states.most_common(60)
    ]
    top_recursive_states = [
        {
            "t": t,
            "a": a,
            "h": h,
            "post_burst_mod_64": post_mod,
            "q_mod_64": q_mod,
            "returns_to_parent": returns,
            "count_unknown": count,
            "percent_of_unknown": _percent(count, total_unknown),
            "state_id": (
                f"unknown:t={t}:a={a}:h={h}:post64={post_mod}:"
                f"q64={q_mod}:return={int(returns)}"
            ),
        }
        for (t, a, h, post_mod, q_mod, returns), count in unknown_recursive_states.most_common(80)
    ]

    return {
        "scope": "parent n = 64*q - 1",
        "q_depth": q_depth,
        "burst_length": burst_length,
        "max_steps": max_steps,
        "q_zero_handling": "q residue 0 is represented by q = 2**q_depth for burst variables",
        "residual_report_summary": None
        if residual_report is None
        else {
            key: residual_report.get(key)
            for key in [
                "total_q_classes",
                "existing_cube_covered_q_classes",
                "residual_certified_q_classes",
                "residual_unknown_q_classes",
                "total_certified_within_parent_percent",
                "unknown_within_parent_percent",
            ]
        },
        "status_counts": {
            STATUS_NAMES.get(status, str(status)): count for status, count in sorted(status_counts.items())
        },
        "certified_result_count": len(certified_results),
        "by_t": by_t_rows,
        "by_a_h": by_a_h_rows,
        "top_unresolved_buckets": top_unresolved,
        "top_unresolved_outcome_states": top_outcome_states,
        "top_unresolved_recursive_states": top_recursive_states,
    }


def write_frontier_strata_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Frontier Strata for `n = 64q - 1`",
        "",
        f"- q-depth: `{report['q_depth']}`",
        f"- q=0 handling: {report['q_zero_handling']}",
        f"- status counts: `{report['status_counts']}`",
        "",
        "## By t",
        "",
    ]
    for row in report["by_t"][:40]:
        lines.append(
            f"- `t={row['t']}`, `a={row['a']}`: count `{row['count']}`, "
            f"unknown `{row['unknown']}` ({row['unknown_percent']:.4f}%), "
            f"burst escapes `{row['burst_escape_count']}`, returns `{row['return_to_parent_count']}`"
        )
    lines.extend(["", "## Top Unresolved Buckets", ""])
    for row in report["top_unresolved_buckets"][:30]:
        lines.append(
            f"- `t={row['t']}`, `a={row['a']}`, `h={row['h']}`: "
            f"unknown `{row['count_unknown']}` ({row['unknown_percent']:.4f}%)"
        )
    lines.extend(["", "## Top Recursive Unknown States", ""])
    for row in report["top_unresolved_recursive_states"][:30]:
        lines.append(
            f"- `{row['state_id']}`: `{row['count_unknown']}` "
            f"({row['percent_of_unknown']:.4f}% of unknown)"
        )
    lines.append("")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stratify residual q-frontier by burst variables.")
    parser.add_argument("--q-depth", type=int, required=True)
    parser.add_argument("--residual-report", default=None)
    parser.add_argument("--theorem-candidate", default=None)
    parser.add_argument("--burst-length", type=int, default=6)
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    parser.add_argument("--no-progress", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    residual = json.loads(Path(args.residual_report).read_text(encoding="utf-8")) if args.residual_report else None
    candidate = load_candidate(args.theorem_candidate)
    report = build_frontier_strata_report(
        q_depth=args.q_depth,
        residual_report=residual,
        candidate=candidate,
        burst_length=args.burst_length,
        max_steps=args.max_steps,
        show_progress=not args.no_progress,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_frontier_strata_markdown(report, md_out)
    Console().print(
        {
            "q_depth": report["q_depth"],
            "status_counts": report["status_counts"],
            "top_unresolved": report["top_unresolved_buckets"][:5],
            "out": str(out),
        }
    )


if __name__ == "__main__":
    main()
