"""Exact transitions among parent states ``P_a: n = 2**a*r - 1``."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import burst_division_exponent, burst_post_division_value, forced_burst_image, v2_int


def parent_level(n: int) -> int:
    """Return ``a = v2(n + 1)``."""

    if n <= 0:
        raise ValueError("n must be positive")
    return v2_int(n + 1)


def parent_transition(a: int, r: int) -> dict[str, Any]:
    """Compute the exact forced-burst transition from ``P_a``.

    Input represents ``n = 2**a*r - 1`` with ``r`` odd.
    """

    if a < 1:
        raise ValueError("a must be positive")
    if r <= 0 or r % 2 != 1:
        raise ValueError("r must be positive odd")
    n = (1 << a) * r - 1
    h = burst_division_exponent(a, r)
    y = burst_post_division_value(a, r)
    a_next = parent_level(y)
    r_next = (y + 1) >> a_next
    if r_next % 2 != 1:
        raise AssertionError("next parent odd coordinate is not odd")
    return {
        "status": "PROVED_TRANSITION_ONLY",
        "a": a,
        "r": r,
        "n": n,
        "forced_burst_image": forced_burst_image(a, r),
        "h": h,
        "post_burst_value": y,
        "a_next": a_next,
        "r_next": r_next,
        "transition": f"P_{a}->P_{a_next}",
        "standard_steps": 2 * a + h,
    }


def build_parent_state_sample_report(a_min: int, a_max: int, r_limit: int = 255) -> dict[str, Any]:
    if a_min < 1 or a_max < a_min:
        raise ValueError("invalid a range")
    rows = []
    transition_counts: Counter[str] = Counter()
    for a in range(a_min, a_max + 1):
        for r in range(1, r_limit + 1, 2):
            row = parent_transition(a, r)
            transition_counts[row["transition"]] += 1
            if len(rows) < 500:
                rows.append(row)
    return {
        "scope": "sampled exact parent-state transitions P_a: n=2^a*r-1",
        "status": "SAMPLED_TRANSITION_SUMMARY_EXACT_PER_ROW",
        "a_min": a_min,
        "a_max": a_max,
        "r_limit": r_limit,
        "transition_counts": [
            {"transition": transition, "count": count}
            for transition, count in transition_counts.most_common()
        ],
        "sample_rows": rows,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build sampled exact parent-state transition report.")
    parser.add_argument("--a-min", type=int, default=1)
    parser.add_argument("--a-max", type=int, default=20)
    parser.add_argument("--r-limit", type=int, default=255)
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_parent_state_sample_report(args.a_min, args.a_max, args.r_limit)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print(
        {
            "out": str(out),
            "top_transitions": report["transition_counts"][:10],
        }
    )


if __name__ == "__main__":
    main()
