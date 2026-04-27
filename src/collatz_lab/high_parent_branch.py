"""Symbolic high-parent branch executor.

Variable-depth parent certificates can get stuck when a source residue proves
the first burst exponent ``h`` but does not contain enough source bits to prove
the next parent level.  Those branches are not arbitrary: for

    r = r0 + 2**d * k

the post-burst value has the exact form

    y(k) = 2**(d-h) * (c + 3**a*k) - 1.

So the missing next parent level is

    a_next(k) = d - h + v2(c + 3**a*k).

Because ``3**a`` is odd, this valuation is unbounded over the 2-adic family.
That does not prove Collatz closure; it proves that finite source-depth
refinement alone cannot be the final mechanism for these branches.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import burst_post_division_value
from .collatz import collatz_step
from .parent_states import parent_transition


HIGH_PARENT_BRANCH_SCHEMA = "collatz_lab.high_parent_branch"


def _is_high_parent_split(row: dict[str, Any]) -> bool:
    return (
        row.get("status") == "NEEDS_DEEPER_SOURCE_SPLIT"
        and row.get("a_next") is not None
        and row.get("required_source_depth") is not None
    )


def source_class_affine_descent(a: int, r_residue: int, r_depth: int) -> dict[str, Any]:
    """Try to prove descent for the whole source residue class directly."""

    n_depth = a + r_depth
    n_modulus = 1 << n_depth
    n_residue = ((1 << a) * (r_residue % (1 << r_depth)) - 1) % n_modulus
    min_n = n_residue if n_residue > 0 else n_modulus
    current = min_n
    affine_a, affine_b, affine_d = 1, 0, 1
    for step in range(1, n_depth + 1):
        if current & 1:
            affine_a = 3 * affine_a
            affine_b = 3 * affine_b + affine_d
        else:
            affine_d *= 2
        current = collatz_step(current)
        if affine_d > affine_a and affine_a * min_n + affine_b < affine_d * min_n:
            return {
                "status": "PASS",
                "reason": "source residue class has a stable affine descent certificate",
                "n_residue": n_residue,
                "n_modulus": n_modulus,
                "n_modulus_depth": n_depth,
                "descent_step": step,
                "affine_A": affine_a,
                "affine_B": affine_b,
                "affine_D": affine_d,
                "min_n": min_n,
            }
    return {
        "status": "UNKNOWN_NEEDS_VALUATION_RANK",
        "reason": "no source-class affine descent proof exists within the stable parity depth",
        "n_residue": n_residue,
        "n_modulus": n_modulus,
        "n_modulus_depth": n_depth,
        "checked_steps": n_depth,
        "min_n": min_n,
    }


def derive_high_parent_branch(a: int, r_residue: int, r_depth: int) -> dict[str, Any]:
    """Derive the exact symbolic branch behind one blocked transition."""

    if a < 1:
        raise ValueError("a must be positive")
    if r_depth < 1:
        raise ValueError("r_depth must be positive")
    if r_residue % 2 != 1:
        raise ValueError("r_residue must be odd")
    modulus = 1 << r_depth
    r0 = r_residue % modulus
    row = parent_transition(a, r0)
    h = int(row["h"])
    if r_depth <= h:
        return {
            "status": "NOT_HIGH_PARENT_BRANCH",
            "reason": "source depth does not prove a constant first burst exponent",
            "a": a,
            "r_residue": r0,
            "r_depth": r_depth,
            "h": h,
        }

    known_target_parent_floor = r_depth - h
    representative_a_next = int(row["a_next"])
    if representative_a_next < known_target_parent_floor:
        return {
            "status": "NOT_HIGH_PARENT_BRANCH",
            "reason": "representative next parent level is already determined below the floor",
            "a": a,
            "r_residue": r0,
            "r_depth": r_depth,
            "h": h,
            "representative_a_next": representative_a_next,
            "known_target_parent_floor": known_target_parent_floor,
        }

    y0 = burst_post_division_value(a, r0)
    factor = 1 << known_target_parent_floor
    if (y0 + 1) % factor != 0:
        raise AssertionError("high-parent branch derivation lost divisibility")
    c = (y0 + 1) // factor
    coefficient = 3**a
    representative_extra = representative_a_next - known_target_parent_floor
    representative_r_next = int(row["r_next"])
    required_source_depth = h + representative_a_next + 1
    source_descent = source_class_affine_descent(a, r0, r_depth)
    source_closed = source_descent["status"] == "PASS"
    return {
        "schema": HIGH_PARENT_BRANCH_SCHEMA,
        "status": "CLOSED_BY_SOURCE_CLASS_AFFINE_DESCENT" if source_closed else "OPEN_SYMBOLIC_VALUATION_BRANCH",
        "closure_status": "CLOSED_BY_SOURCE_CLASS_AFFINE_DESCENT" if source_closed else "NOT_CLOSED_REQUIRES_VALUATION_RANK",
        "a": a,
        "r_residue": r0,
        "r_depth": r_depth,
        "h": h,
        "representative_a_next": representative_a_next,
        "representative_r_next": representative_r_next,
        "required_source_depth": required_source_depth,
        "known_target_parent_floor": known_target_parent_floor,
        "symbolic_parameter": "k >= 0",
        "source_family": f"r = {r0} + 2^{r_depth}*k",
        "post_burst_family": (
            f"y(k) = 2^{known_target_parent_floor}*"
            f"({c} + {coefficient}*k) - 1"
        ),
        "next_parent_level_formula": (
            f"a_next(k) = {known_target_parent_floor} + "
            f"v2({c} + {coefficient}*k)"
        ),
        "next_parent_odd_coordinate_formula": (
            f"r_next(k) = oddpart({c} + {coefficient}*k)"
        ),
        "valuation_coefficient_is_odd": coefficient % 2 == 1,
        "unbounded_parent_level_proof": {
            "status": "PROVED_UNBOUNDED_A_NEXT_OVER_2ADIC_FAMILY",
            "reason": (
                "Since 3^a is odd, for every T >= 0 there is a residue class "
                "of k modulo 2^T satisfying c + 3^a*k == 0 mod 2^T."
            ),
            "congruence_for_extra_T": "k == -c * (3^a)^(-1) mod 2^T",
        },
        "finite_refinement_conclusion": {
            "status": "FINITE_SOURCE_DEPTH_REFINEMENT_CANNOT_CLOSE_BRANCH_GLOBALLY",
            "reason": (
                "Any finite refinement depth leaves deeper k-residue classes whose "
                "valuation, and therefore next parent level, is still unresolved."
            ),
        },
        "source_class_affine_descent": source_descent,
        "representative_extra_parent_bits": representative_extra,
        "ready_for_run7": source_closed,
        "next_step": (
            "Branch is closed by a direct source-class affine descent certificate."
            if source_closed
            else (
                "Add a valuation-rank theorem over z(k)=c+3^a*k, or a stronger global "
                "parent-state potential, before promoting this debt-induction branch."
            )
        ),
    }


def build_high_parent_branch_report(variable_depth_certificate: dict[str, Any]) -> dict[str, Any]:
    rows = variable_depth_certificate.get("bad_states") or variable_depth_certificate.get("bad_states_sample") or []
    branches = []
    skipped = []
    for row in rows:
        if not isinstance(row, dict) or not _is_high_parent_split(row):
            skipped.append(row)
            continue
        branches.append(
            derive_high_parent_branch(
                a=int(row["a"]),
                r_residue=int(row["r_residue"]),
                r_depth=int(row["r_depth"]),
            )
        )

    status_counts = Counter(str(row.get("status")) for row in branches)
    open_branches = [row for row in branches if row.get("ready_for_run7") is not True]
    ready = bool(branches) and not open_branches
    return {
        "schema": HIGH_PARENT_BRANCH_SCHEMA,
        "version": 1,
        "scope": "symbolic high-parent branches from variable-depth debt induction",
        "status": "HIGH_PARENT_BRANCHES_CLOSED" if ready else "HIGH_PARENT_BRANCHES_OPEN",
        "ready_for_run7": ready,
        "source_status": variable_depth_certificate.get("status"),
        "source_bad_state_count": variable_depth_certificate.get("bad_state_count"),
        "branch_count": len(branches),
        "open_branch_count": len(open_branches),
        "closed_branch_count": len(branches) - len(open_branches),
        "skipped_bad_state_count": len(skipped),
        "status_counts": dict(status_counts),
        "branches": branches,
        "branch_sample": branches[:40],
        "formal_blockers": []
        if ready
        else [
            "symbolic high-parent branches are derived but not closed",
            "unbounded a_next over the 2-adic branch rules out finite-depth-only closure",
            "missing valuation-rank/global-potential theorem for z(k)=c+3^a*k",
        ],
        "next_step": (
            "Prove a valuation-rank theorem for the derived z(k) branches; do not launch "
            "RUN-007 while any branch remains OPEN_SYMBOLIC_VALUATION_BRANCH."
        ),
    }


def write_high_parent_branch_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Symbolic High-Parent Branch Executor",
        "",
        f"- status: `{report['status']}`",
        f"- ready for RUN-007: `{report['ready_for_run7']}`",
        f"- source status: `{report['source_status']}`",
        f"- source bad states: `{report['source_bad_state_count']}`",
        f"- derived branches: `{report['branch_count']}`",
        f"- closed branches: `{report['closed_branch_count']}`",
        f"- open branches: `{report['open_branch_count']}`",
        f"- skipped bad states: `{report['skipped_bad_state_count']}`",
        f"- status counts: `{report['status_counts']}`",
        "",
        "## Formal Blockers",
        "",
    ]
    for blocker in report["formal_blockers"]:
        lines.append(f"- {blocker}")
    if report.get("branch_sample"):
        lines.extend(["", "## Branch Sample", ""])
        for row in report["branch_sample"][:12]:
            lines.extend(
                [
                    f"### P{row['a']}:r{row['r_residue']}:d{row['r_depth']}",
                    "",
                    f"- h: `{row['h']}`",
                    f"- representative a_next: `{row['representative_a_next']}`",
                    f"- parent floor: `{row['known_target_parent_floor']}`",
                    f"- source family: `{row['source_family']}`",
                    f"- post-burst family: `{row['post_burst_family']}`",
                    f"- next parent formula: `{row['next_parent_level_formula']}`",
                    f"- source-class affine descent: `{row['source_class_affine_descent']['status']}`",
                    f"- conclusion: `{row['finite_refinement_conclusion']['status']}`",
                    "",
                ]
            )
    lines.extend(["## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Derive symbolic high-parent branches from a variable-depth certificate.")
    parser.add_argument("--variable-depth-certificate", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    source = json.loads(Path(args.variable_depth_certificate).read_text(encoding="utf-8"))
    report = build_high_parent_branch_report(source)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_high_parent_branch_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "status": report["status"],
            "ready_for_run7": report["ready_for_run7"],
            "branches": report["branch_count"],
        }
    )


if __name__ == "__main__":
    main()
