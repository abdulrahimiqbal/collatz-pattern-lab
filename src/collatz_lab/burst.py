"""Exact forced-burst families inside ``n = 64*q - 1``.

For ``q = 2**t * r`` with ``r`` odd, the parent class has
``n = 2**(6+t) * r - 1``. Under the standard Collatz map, the first
``a = 6+t`` odd steps and their forced divisions take exactly ``2*a``
standard steps and send

    ``2**a * r - 1 -> 3**a * r - 1``.

After dividing by ``2**h`` where ``h = v2(3**a*r - 1)``, the block has a
direct descent when the post-division value is below the starting value.
All proof-critical predicates in this module use exact integer arithmetic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console


def v2_int(n: int) -> int:
    """Return the exponent of two dividing ``n``.

    ``v2_int(0)`` is undefined and raises ``ValueError``.
    """

    if n == 0:
        raise ValueError("v2_int is undefined for zero")
    value = abs(n)
    return (value & -value).bit_length() - 1


def decompose_q(q: int) -> tuple[int, int, int]:
    """Return ``(t, a, r)`` for ``q = 2**t * r`` and ``a = 6+t``."""

    if q <= 0:
        raise ValueError("q must be positive")
    t = v2_int(q)
    a = 6 + t
    r = q >> t
    if r % 2 != 1:
        raise AssertionError("decompose_q produced an even odd part")
    return t, a, r


def forced_burst_image(a: int, r: int) -> int:
    """Return ``3**a * r - 1``."""

    if a < 0:
        raise ValueError("a must be non-negative")
    if r <= 0 or r % 2 != 1:
        raise ValueError("r must be a positive odd integer")
    return (3**a) * r - 1


def burst_division_exponent(a: int, r: int) -> int:
    """Return ``v2(3**a * r - 1)``."""

    return v2_int(forced_burst_image(a, r))


def burst_post_division_value(a: int, r: int) -> int:
    """Return ``(3**a * r - 1) // 2**h`` for ``h = v2(3**a*r - 1)``."""

    value = forced_burst_image(a, r)
    h = v2_int(value)
    return value >> h


def is_burst_descent(a: int, r: int) -> bool:
    """Return whether the post-burst value is below ``2**a*r - 1``."""

    return burst_post_division_value(a, r) < (1 << a) * r - 1


def h_star(a: int) -> int:
    """Return the sufficient division threshold for burst descent.

    This is the smallest ``h >= 0`` satisfying
    ``2**h * (2**a - 1) > 3**a - 1``.
    """

    if a < 0:
        raise ValueError("a must be non-negative")
    h = 0
    left_factor = (1 << a) - 1
    right = (3**a) - 1
    while (1 << h) * left_factor <= right:
        h += 1
    return h


def burst_escape_residue_mod_power(a: int) -> tuple[int, int]:
    """Return ``(rho, d)`` for the sufficient burst escape condition.

    The condition ``v2(3**a*r - 1) >= d`` is equivalent to
    ``3**a*r == 1 mod 2**d``. Since ``3**a`` is odd, it has an inverse
    modulo ``2**d``.
    """

    d = h_star(a)
    modulus = 1 << d
    if modulus == 1:
        return 0, d
    base = pow(3, a, modulus)
    return pow(base, -1, modulus), d


def burst_escape_q_condition_for_parent(a: int) -> dict[str, Any]:
    """Return the q-space condition for a sufficient burst escape family."""

    if a < 6:
        raise ValueError("parent region n=64*q-1 requires a >= 6")
    t = a - 6
    rho, d = burst_escape_residue_mod_power(a)
    q_residue = (1 << t) * rho
    q_depth = t + d
    return {
        "a": a,
        "t": t,
        "r_residue": rho,
        "r_depth": d,
        "q_residue": q_residue % (1 << q_depth),
        "q_depth": q_depth,
        "h_star": d,
        "descent_steps_standard": 2 * a + d,
        "status": "PROVED_INFINITE_FAMILY",
    }


def verify_burst_escape_family(a: int, sample_limit: int = 1000) -> bool:
    """Sanity-check sampled ``r`` values from the symbolic family."""

    rho, d = burst_escape_residue_mod_power(a)
    modulus = 1 << d
    start = rho if rho % 2 == 1 else rho + modulus
    for sample_index in range(sample_limit):
        r = start + sample_index * modulus
        if r <= 0 or r % 2 != 1:
            continue
        if burst_division_exponent(a, r) < d:
            return False
        if not is_burst_descent(a, r):
            return False
    return True


def burst_family_row(a: int, sample_limit: int = 1000) -> dict[str, Any]:
    row = burst_escape_q_condition_for_parent(a)
    row["symbolic_statement"] = (
        f"For n = 64*q - 1 with v2(q) = {row['t']} and "
        f"q == {row['q_residue']} mod 2^{row['q_depth']}, "
        f"C^{row['descent_steps_standard']}(n) < n."
    )
    row["sample_check_passed"] = verify_burst_escape_family(a, sample_limit=sample_limit)
    return row


def build_burst_report(a_min: int, a_max: int, sample_limit: int = 1000) -> dict[str, Any]:
    if a_min < 6:
        raise ValueError("a_min must be at least 6 for the 63 mod 64 parent")
    if a_max < a_min:
        raise ValueError("a_max must be >= a_min")
    families = [burst_family_row(a, sample_limit=sample_limit) for a in range(a_min, a_max + 1)]
    return {
        "scope": "parent n = 64*q - 1",
        "claim_status": "PROVED_INFINITE_FAMILY where status labels say so",
        "a_min": a_min,
        "a_max": a_max,
        "families": families,
    }


def write_burst_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Forced Burst Families",
        "",
        "All inequalities in this report are derived with exact integer arithmetic.",
        "",
    ]
    for row in report["families"]:
        lines.extend(
            [
                f"## a={row['a']}",
                "",
                f"- status: `{row['status']}`",
                f"- t: `{row['t']}`",
                f"- h_star: `{row['h_star']}`",
                f"- r condition: `r == {row['r_residue']} mod 2^{row['r_depth']}`",
                f"- q condition: `q == {row['q_residue']} mod 2^{row['q_depth']}`",
                f"- standard descent steps: `{row['descent_steps_standard']}`",
                f"- sample check passed: `{row['sample_check_passed']}`",
                f"- statement: {row['symbolic_statement']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Highlight",
            "",
            "For `a=6`: `n = 64q - 1` and `q == 9 mod 16` implies `C^16(n) < n`.",
            "",
        ]
    )
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate exact forced-burst families.")
    parser.add_argument("--a-min", type=int, default=6)
    parser.add_argument("--a-max", type=int, default=20)
    parser.add_argument("--sample-limit", type=int, default=1000)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_burst_report(args.a_min, args.a_max, sample_limit=args.sample_limit)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_burst_markdown(report, md_out)
    Console().print(
        {
            "families": len(report["families"]),
            "first": report["families"][0],
            "out": str(out),
            "markdown": str(md_out),
        }
    )


if __name__ == "__main__":
    main()
