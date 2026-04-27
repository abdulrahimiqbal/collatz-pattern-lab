"""Parametric checks for parent-state rules grouped by ``a``.

For fixed 2-adic depth, powers of 3 are periodic.  This module records that
periodicity as an exact scaffold for future ``GENERALIZE_IN_A`` proof actions.
It does not by itself prove Collatz; it tells the proof compiler which
finite-a diagnostics can be grouped into residue classes of ``a``.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from rich.console import Console


def power_period_mod_power(depth: int) -> int:
    """Return the multiplicative order period of ``3**a mod 2**depth``."""

    if depth < 0:
        raise ValueError("depth must be non-negative")
    if depth <= 1:
        return 1
    if depth == 2:
        return 2
    return 1 << (depth - 2)


def verify_power_period(depth: int, a_min: int = 0, sample_count: int = 64) -> bool:
    """Sample-check the exact period identity for powers of three."""

    if sample_count < 0:
        raise ValueError("sample_count must be non-negative")
    modulus = 1 << depth
    period = power_period_mod_power(depth)
    for a in range(a_min, a_min + sample_count):
        if pow(3, a, modulus) != pow(3, a + period, modulus):
            return False
    return True


def group_a_by_power_residue(a_min: int, a_max: int, depth: int) -> list[dict[str, Any]]:
    """Group concrete ``a`` values by ``3**a mod 2**depth``."""

    if a_min < 0 or a_max < a_min:
        raise ValueError("invalid a range")
    modulus = 1 << depth
    groups: dict[int, list[int]] = defaultdict(list)
    for a in range(a_min, a_max + 1):
        groups[pow(3, a, modulus)].append(a)
    return [
        {
            "power_residue": residue,
            "depth": depth,
            "a_values": values,
            "a_residue_mod_period": values[0] % power_period_mod_power(depth),
            "count": len(values),
        }
        for residue, values in sorted(groups.items())
    ]


def build_parametric_a_report(a_min: int, a_max: int, depth: int) -> dict[str, Any]:
    """Build an exact periodicity report for ``a`` templates."""

    period = power_period_mod_power(depth)
    groups = group_a_by_power_residue(a_min, a_max, depth)
    return {
        "scope": "parametric grouping of parent-state exponent a",
        "status": "EXACT_PERIODICITY_SCAFFOLD_NOT_UNIVERSAL_PROOF",
        "depth": depth,
        "modulus": 1 << depth,
        "period": period,
        "a_min": a_min,
        "a_max": a_max,
        "period_identity": f"3^(a+{period}) == 3^a mod 2^{depth}",
        "sample_period_check_passed": verify_power_period(depth, a_min=a_min),
        "group_count": len(groups),
        "groups": groups,
        "proof_role": (
            "Candidate transition templates can be grouped by a modulo this period; "
            "separate exact verification is still required for each template."
        ),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build parametric-a periodicity report.")
    parser.add_argument("--depth", type=int, default=8)
    parser.add_argument("--a-min", type=int, default=1)
    parser.add_argument("--a-max", type=int, default=64)
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_parametric_a_report(args.a_min, args.a_max, args.depth)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print({"out": str(out), "period": report["period"], "groups": report["group_count"]})


if __name__ == "__main__":
    main()
