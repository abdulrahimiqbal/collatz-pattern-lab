"""Finite-depth symbolic system for parent states ``P_a``.

This module promotes branches that leave the ``P6`` laboratory into the general
parent-state language ``P_a: n = 2**a*r - 1``.  Reports are finite-depth
diagnostics unless a row is explicitly backed by a separate infinite proof.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from rich.console import Console

from .parent_states import parent_transition


def classify_parent_residue(a: int, r_residue: int, r_depth: int) -> dict[str, Any]:
    """Classify one odd residue representative for ``P_a``."""

    if r_depth < 1:
        raise ValueError("r_depth must be positive")
    modulus = 1 << r_depth
    residue = r_residue % modulus
    if residue % 2 != 1:
        raise ValueError("parent-state r residue must be odd")
    row = parent_transition(a, residue)
    return {
        "status": "VERIFIED_FINITE_DEPTH_REPRESENTATIVE",
        "a": a,
        "r_residue": residue,
        "r_depth": r_depth,
        "h": row["h"],
        "a_next": row["a_next"],
        "r_next": row["r_next"],
        "transition": row["transition"],
        "post_burst_mod_64": row["post_burst_value"] % 64,
        "standard_steps": row["standard_steps"],
    }


def build_parent_state_system_report(a_min: int, a_max: int, r_depth: int = 7) -> dict[str, Any]:
    """Enumerate finite-depth parent-state transitions for ``a_min..a_max``."""

    if a_min < 1 or a_max < a_min:
        raise ValueError("invalid a range")
    if r_depth < 1:
        raise ValueError("r_depth must be positive")
    rows: list[dict[str, Any]] = []
    transition_counts: Counter[str] = Counter()
    bucket_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for a in range(a_min, a_max + 1):
        for r in range(1, 1 << r_depth, 2):
            row = classify_parent_residue(a, r, r_depth)
            rows.append(row)
            transition_counts[row["transition"]] += 1
            bucket_counts[f"P_{a}"][f"h={row['h']}:a_next={row['a_next']}"] += 1
    return {
        "scope": "finite-depth parent-state transition system",
        "status": "FINITE_DEPTH_DIAGNOSTIC_NOT_PROOF",
        "a_min": a_min,
        "a_max": a_max,
        "r_depth": r_depth,
        "state_count": a_max - a_min + 1,
        "row_count": len(rows),
        "transition_counts": [
            {"transition": key, "count": count}
            for key, count in transition_counts.most_common()
        ],
        "bucket_counts": {
            state: [{"bucket": key, "count": count} for key, count in counts.most_common()]
            for state, counts in sorted(bucket_counts.items())
        },
        "notable_rows": [
            row
            for row in rows
            if (row["a"] == 6 and row["r_residue"] in {23, 87, 9})
        ],
        "sample_rows": rows[:500],
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build finite-depth P_a transition report.")
    parser.add_argument("--a-min", type=int, default=1)
    parser.add_argument("--a-max", type=int, default=20)
    parser.add_argument("--r-depth", type=int, default=7)
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_parent_state_system_report(args.a_min, args.a_max, args.r_depth)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print({"out": str(out), "rows": report["row_count"], "status": report["status"]})


if __name__ == "__main__":
    main()
