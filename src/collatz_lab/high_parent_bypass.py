"""Mixed-modulus bypass analysis for high-parent valuation branches.

The high-parent blocker is not caused by a missing finite source depth.  Once a
branch has the form

    r = r0 + 2**d*k,
    y(k) = 2**f * (c + 3**a*k) - 1,

the next parent level is ``f + v2(c + 3**a*k)``.  The valuation is unbounded,
so a proof cannot keep refining only powers-of-two source residues.

This module derives the exact successor family that survives that obstruction:
for each valuation ``T``, the next odd coordinate satisfies an odd-modulus
condition modulo ``3**a``.  That is the representation the next verifier has to
carry; it is a bypass of the finite-depth representation blocker, not a proof
closure certificate.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import burst_post_division_value, v2_int


HIGH_PARENT_BYPASS_SCHEMA = "collatz_lab.high_parent_bypass"


def _branch_id(branch: dict[str, Any]) -> str:
    return f"P{branch['a']}:r{branch['r_residue']}:d{branch['r_depth']}"


def high_parent_coefficients(branch: dict[str, Any]) -> dict[str, Any]:
    """Return the exact affine data behind one high-parent branch."""

    a = int(branch["a"])
    r_residue = int(branch["r_residue"])
    r_depth = int(branch["r_depth"])
    h = int(branch["h"])
    floor = int(branch["known_target_parent_floor"])
    if floor != r_depth - h:
        raise ValueError("known_target_parent_floor must equal r_depth - h")

    y0 = burst_post_division_value(a, r_residue)
    factor = 1 << floor
    if (y0 + 1) % factor != 0:
        raise AssertionError("branch does not have the expected high-parent factor")
    c = (y0 + 1) // factor
    coefficient = 3**a
    first_block_growth = coefficient / (1 << (a + h))
    odd_gain_upper = max(c / r_residue, coefficient / (1 << r_depth))
    return {
        "branch_id": _branch_id(branch),
        "a": a,
        "r_residue": r_residue,
        "r_depth": r_depth,
        "h": h,
        "known_target_parent_floor": floor,
        "c": c,
        "coefficient": coefficient,
        "z_family": f"z(k) = {c} + {coefficient}*k",
        "first_block_growth": first_block_growth,
        "first_block_log_growth": math.log(first_block_growth),
        "odd_coordinate_gain_upper": odd_gain_upper,
        "odd_coordinate_log_gain_upper": math.log(odd_gain_upper),
        "odd_coordinate_descent_sufficient": coefficient < (1 << r_depth) and c < r_residue,
    }


def valuation_successor_family(branch: dict[str, Any], valuation: int) -> dict[str, Any]:
    """Derive the exact mixed-modulus target family for a fixed valuation.

    If ``T = v2(c + 3**a*k)``, then the target state is

        P_{floor+T}: r' = (c + 3**a*k) / 2**T.

    Since ``3**a*k`` vanishes modulo ``3**a``, the odd target coordinate obeys
    ``r' == c * 2**(-T) mod 3**a``.  The parity condition is added with CRT so
    the report gives one ordinary residue modulo ``2*3**a``.
    """

    if valuation < 0:
        raise ValueError("valuation must be non-negative")
    coeffs = high_parent_coefficients(branch)
    a = int(coeffs["a"])
    c = int(coeffs["c"])
    coefficient = int(coeffs["coefficient"])
    floor = int(coeffs["known_target_parent_floor"])
    odd_modulus = coefficient
    inverse_power = pow(pow(2, valuation, odd_modulus), -1, odd_modulus)
    odd_residue_mod_3a = (c * inverse_power) % odd_modulus
    parity_residue_mod_2_3a = odd_residue_mod_3a
    if parity_residue_mod_2_3a % 2 == 0:
        parity_residue_mod_2_3a += odd_modulus

    if valuation == 0:
        k_divisibility_residue = 0
        k_divisibility_modulus = 1
    else:
        k_divisibility_modulus = 1 << valuation
        k_divisibility_residue = (-c * pow(coefficient, -1, k_divisibility_modulus)) % k_divisibility_modulus
    next_modulus = 1 << (valuation + 1)
    excluded_next_residue = (-c * pow(coefficient, -1, next_modulus)) % next_modulus

    samples = []
    search_modulus = 1 << valuation
    start = k_divisibility_residue
    for index in range(64):
        k = start + search_modulus * index
        z = c + coefficient * k
        if z <= 0:
            continue
        if v2_int(z) != valuation:
            continue
        target_odd = z >> valuation
        samples.append(
            {
                "k": k,
                "z": z,
                "target_odd": target_odd,
                "target_odd_mod_3a": target_odd % odd_modulus,
                "matches_mod_3a": target_odd % odd_modulus == odd_residue_mod_3a,
            }
        )
        if len(samples) >= 4:
            break

    return {
        "valuation": valuation,
        "target_parent_level": floor + valuation,
        "target_family": (
            f"P{floor + valuation}: r' odd, "
            f"r' == {odd_residue_mod_3a} mod {odd_modulus}"
        ),
        "target_odd_residue_mod_3a": odd_residue_mod_3a,
        "target_odd_modulus_3a": odd_modulus,
        "target_odd_residue_mod_2_times_3a": parity_residue_mod_2_3a,
        "target_odd_modulus_2_times_3a": 2 * odd_modulus,
        "k_divisibility_residue_mod_2T": k_divisibility_residue,
        "k_divisibility_modulus_2T": k_divisibility_modulus,
        "excluded_residue_mod_2T_plus_1": excluded_next_residue,
        "excluded_modulus_2T_plus_1": next_modulus,
        "exactness_statement": (
            "v2(c+3^a*k)=T implies target level floor+T and "
            "target odd coordinate congruent to c*2^{-T} modulo 3^a"
        ),
        "sample_checks": samples,
        "sample_checks_passed": bool(samples) and all(row["matches_mod_3a"] for row in samples),
    }


def _find_level_rank_potential(edges: list[dict[str, Any]], epsilon: float) -> dict[str, Any]:
    states = sorted({str(edge["source_level"]) for edge in edges} | {str(edge["target_level"]) for edge in edges})
    dist = {state: 0.0 for state in states}
    predecessor: dict[str, tuple[str, dict[str, Any], float]] = {}
    weighted_edges = []
    for edge in edges:
        source = str(edge["source_level"])
        target = str(edge["target_level"])
        bound = -float(edge["odd_coordinate_log_gain_upper"]) - epsilon
        weighted_edges.append((source, target, bound, edge))

    updated: tuple[str, str, float, dict[str, Any]] | None = None
    for _ in range(len(states)):
        updated = None
        for source, target, bound, edge in weighted_edges:
            candidate = dist[source] + bound
            if dist[target] > candidate + 1e-15:
                dist[target] = candidate
                predecessor[target] = (source, edge, bound)
                updated = (source, target, bound, edge)
        if updated is None:
            break

    if updated is None:
        margins = []
        for source, target, bound, edge in weighted_edges:
            margins.append(
                {
                    "source_level": int(source),
                    "target_level": int(target),
                    "margin": bound - (dist[target] - dist[source]),
                    "bound": bound,
                    "branch_id": edge["branch_id"],
                }
            )
        margins.sort(key=lambda row: row["margin"])
        return {
            "status": "PASS",
            "reason": "found a finite parent-level correction for log odd-coordinate rank",
            "epsilon": epsilon,
            "parent_levels": states,
            "phi_by_parent_level": dist,
            "tight_edges": margins[:20],
        }

    cycle_state = updated[1]
    for _ in range(len(states)):
        if cycle_state not in predecessor:
            break
        cycle_state = predecessor[cycle_state][0]
    witness = []
    seen: set[str] = set()
    current = cycle_state
    while current not in seen and current in predecessor:
        seen.add(current)
        source, edge, bound = predecessor[current]
        witness.append(
            {
                "source_level": int(source),
                "target_level": int(current),
                "bound": bound,
                "odd_coordinate_log_gain_upper": edge["odd_coordinate_log_gain_upper"],
                "odd_coordinate_gain_upper": edge["odd_coordinate_gain_upper"],
                "branch_id": edge["branch_id"],
            }
        )
        current = source
    witness.reverse()
    return {
        "status": "FAIL",
        "reason": "no scalar parent-level correction can rank the open mixed-modulus branches",
        "epsilon": epsilon,
        "parent_levels": states,
        "positive_cycle_witness": witness,
        "cycle_log_gain_sum": sum(float(row["odd_coordinate_log_gain_upper"]) for row in witness),
    }


def build_high_parent_bypass_report(
    high_parent_branch_report: dict[str, Any],
    valuation_samples: int = 6,
    epsilon: float = 1e-9,
) -> dict[str, Any]:
    branches = list(high_parent_branch_report.get("branches") or [])
    open_branches = [row for row in branches if row.get("ready_for_run7") is not True]
    mixed_rows = []
    rank_edges = []
    for branch in open_branches:
        coeffs = high_parent_coefficients(branch)
        families = [valuation_successor_family(branch, valuation) for valuation in range(valuation_samples)]
        mixed_rows.append(
            {
                "branch_id": coeffs["branch_id"],
                "status": "MIXED_MODULUS_SUCCESSOR_DERIVED",
                "closure_status": "NOT_CLOSED_NEEDS_MIXED_MODULUS_DEBT_CERTIFICATE",
                "a": coeffs["a"],
                "r_residue": coeffs["r_residue"],
                "r_depth": coeffs["r_depth"],
                "h": coeffs["h"],
                "known_target_parent_floor": coeffs["known_target_parent_floor"],
                "z_family": coeffs["z_family"],
                "first_block_growth": coeffs["first_block_growth"],
                "odd_coordinate_gain_upper": coeffs["odd_coordinate_gain_upper"],
                "odd_coordinate_descent_sufficient": coeffs["odd_coordinate_descent_sufficient"],
                "successor_family_rule": (
                    "For every T>=0, v2(z(k))=T maps to "
                    "P_{floor+T} with r' == c*2^{-T} mod 3^a."
                ),
                "valuation_family_samples": families,
                "sample_checks_passed": all(row["sample_checks_passed"] for row in families),
            }
        )
        rank_edges.append(
            {
                "branch_id": coeffs["branch_id"],
                "source_level": coeffs["a"],
                "target_level": coeffs["known_target_parent_floor"],
                "odd_coordinate_gain_upper": coeffs["odd_coordinate_gain_upper"],
                "odd_coordinate_log_gain_upper": coeffs["odd_coordinate_log_gain_upper"],
            }
        )

    rank = _find_level_rank_potential(rank_edges, epsilon=epsilon) if rank_edges else {
        "status": "UNKNOWN",
        "reason": "no open branches to rank",
    }
    status_counts = Counter(row["status"] for row in mixed_rows)
    ready = False
    return {
        "schema": HIGH_PARENT_BYPASS_SCHEMA,
        "version": 1,
        "scope": "mixed-modulus bypass for symbolic high-parent valuation branches",
        "status": "MIXED_MODULUS_BYPASS_BUILT" if mixed_rows else "NO_OPEN_HIGH_PARENT_BRANCHES",
        "ready_for_run7": ready,
        "source_status": high_parent_branch_report.get("status"),
        "source_branch_count": high_parent_branch_report.get("branch_count"),
        "source_open_branch_count": high_parent_branch_report.get("open_branch_count"),
        "mixed_successor_family_count": len(mixed_rows),
        "status_counts": dict(status_counts),
        "valuation_samples_per_branch": valuation_samples,
        "all_sample_checks_passed": all(row["sample_checks_passed"] for row in mixed_rows),
        "odd_coordinate_descent_candidate_count": sum(
            1 for row in mixed_rows if row["odd_coordinate_descent_sufficient"]
        ),
        "level_rank_analysis": rank,
        "mixed_successor_families": mixed_rows,
        "mixed_successor_family_sample": mixed_rows[:20],
        "formal_blockers": [
            "mixed-modulus successor families are derived but no verifier consumes odd-modulus/debt states",
            "finite 2-adic source-depth refinement is known insufficient for these branches",
            "proof confidence remains 0 until a mixed-modulus debt verifier closes the families",
        ]
        + (
            ["scalar parent-level rank is obstructed by a positive mixed-branch cycle"]
            if rank.get("status") == "FAIL"
            else []
        ),
        "next_step": (
            "Build a mixed-modulus debt verifier whose state is "
            "(parent level, odd-coordinate congruence modulo 3^a, remaining growth debt). "
            "Use the exact successor families in this report as its transition source."
        ),
    }


def write_high_parent_bypass_markdown(report: dict[str, Any], out: str | Path) -> None:
    rank = report.get("level_rank_analysis") or {}
    lines = [
        "# High-Parent Mixed-Modulus Bypass",
        "",
        f"- status: `{report['status']}`",
        f"- ready for RUN-007: `{report['ready_for_run7']}`",
        f"- source status: `{report['source_status']}`",
        f"- source branches: `{report['source_branch_count']}`",
        f"- source open branches: `{report['source_open_branch_count']}`",
        f"- mixed successor families: `{report['mixed_successor_family_count']}`",
        f"- sample checks passed: `{report['all_sample_checks_passed']}`",
        f"- odd-coordinate descent candidates: `{report['odd_coordinate_descent_candidate_count']}`",
        f"- scalar level-rank status: `{rank.get('status')}`",
        "",
        "## What This Bypasses",
        "",
        (
            "The blocked branches cannot be closed by more finite 2-adic source splitting. "
            "This report carries the lost information as an exact odd-modulus successor family."
        ),
        "",
        "## Formal Blockers",
        "",
    ]
    for blocker in report["formal_blockers"]:
        lines.append(f"- {blocker}")
    if rank.get("positive_cycle_witness"):
        lines.extend(["", "## Scalar Rank Obstruction", ""])
        lines.append(f"- cycle log-gain sum: `{rank.get('cycle_log_gain_sum')}`")
        for row in rank["positive_cycle_witness"][:8]:
            lines.append(
                f"- `{row['branch_id']}`: P{row['source_level']} -> P{row['target_level']}, "
                f"odd gain <= `{row['odd_coordinate_gain_upper']}`"
            )
    if report.get("mixed_successor_family_sample"):
        lines.extend(["", "## Mixed Successor Sample", ""])
        for row in report["mixed_successor_family_sample"][:8]:
            first_family = row["valuation_family_samples"][0]
            lines.append(
                f"- `{row['branch_id']}`: `{row['z_family']}`; "
                f"T=0 target `{first_family['target_family']}`"
            )
    lines.extend(["", "## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Derive mixed-modulus bypass data for high-parent branches.")
    parser.add_argument("--high-parent-branch-report", required=True)
    parser.add_argument("--valuation-samples", type=int, default=6)
    parser.add_argument("--epsilon", type=float, default=1e-9)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    source = json.loads(Path(args.high_parent_branch_report).read_text(encoding="utf-8"))
    report = build_high_parent_bypass_report(
        source,
        valuation_samples=args.valuation_samples,
        epsilon=args.epsilon,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_high_parent_bypass_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "status": report["status"],
            "ready_for_run7": report["ready_for_run7"],
            "mixed_successor_families": report["mixed_successor_family_count"],
        }
    )


if __name__ == "__main__":
    main()
