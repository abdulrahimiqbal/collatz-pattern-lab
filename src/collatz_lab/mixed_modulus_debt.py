"""Exact mixed-modulus debt-transition verifier.

The high-parent bypass derives successor families of the form

    source: r = r0 + 2^d k
    z(k) = c + 3^a k
    target: r' = z(k) / 2^T, where T = v2(z(k)).

This module checks the resulting local debt transitions exactly.  It is an
evaluator/training-data source for RUN-009, not a proof of Collatz by itself:
sampled valuation transitions can be exact while the unbounded valuation
closure and global theorem assembly remain open.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import v2_int


MIXED_MODULUS_DEBT_SCHEMA = "collatz_lab.mixed_modulus_debt_verifier"
_Z_RE = re.compile(r"z\(k\)\s*=\s*(?P<c>-?\d+)\s*\+\s*(?P<b>\d+)\*k")


def _parse_z_family(z_family: str) -> tuple[int, int]:
    match = _Z_RE.search(z_family)
    if not match:
        raise ValueError(f"cannot parse z_family: {z_family!r}")
    return int(match.group("c")), int(match.group("b"))


def _fraction_payload(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def _first_valid_k(
    *,
    c: int,
    coefficient: int,
    valuation: int,
    residue: int,
    modulus: int,
    excluded_residue: int,
    excluded_modulus: int,
) -> int:
    step = max(1, modulus)
    start = residue % step
    for offset in range(0, max(16, 4 * excluded_modulus + 4), step):
        k = start + offset
        if excluded_modulus > 1 and k % excluded_modulus == excluded_residue % excluded_modulus:
            continue
        z = c + coefficient * k
        if z > 0 and v2_int(z) == valuation:
            return k
    raise ValueError(f"could not find k for valuation={valuation}, residue={residue}, modulus={modulus}")


def debt_transition_for_family(row: dict[str, Any], valuation_family: dict[str, Any]) -> dict[str, Any]:
    """Build one exact local debt transition row.

    The gain bound is the supremum of
    ``target_odd(k) / source_odd(k)`` over the valuation class represented by
    this row.  The rational bound is exact; its decimal/log fields are only
    diagnostics for ranking and model features.
    """

    c, coefficient = _parse_z_family(str(row["z_family"]))
    valuation = int(valuation_family["valuation"])
    r0 = int(row["r_residue"])
    source_modulus = 1 << int(row["r_depth"])
    divisor = 1 << valuation
    residue = int(valuation_family["k_divisibility_residue_mod_2T"])
    modulus = int(valuation_family["k_divisibility_modulus_2T"])
    excluded_residue = int(valuation_family["excluded_residue_mod_2T_plus_1"])
    excluded_modulus = int(valuation_family["excluded_modulus_2T_plus_1"])

    first_k = _first_valid_k(
        c=c,
        coefficient=coefficient,
        valuation=valuation,
        residue=residue,
        modulus=modulus,
        excluded_residue=excluded_residue,
        excluded_modulus=excluded_modulus,
    )
    z_first = c + coefficient * first_k
    target_odd_first = z_first // divisor
    source_odd_first = r0 + source_modulus * first_k
    if z_first % divisor != 0 or v2_int(z_first) != valuation:
        raise AssertionError("valuation family produced an invalid first witness")
    if target_odd_first % 2 != 1:
        raise AssertionError("target odd coordinate is not odd")

    gain_at_first = Fraction(target_odd_first, source_odd_first)
    asymptotic_gain = Fraction(coefficient, divisor * source_modulus)
    derivative_numerator = coefficient * r0 - source_modulus * c
    if derivative_numerator > 0:
        gain_bound = asymptotic_gain
        bound_source = "asymptotic_supremum"
    elif derivative_numerator < 0:
        gain_bound = gain_at_first
        bound_source = "first_valid_k_maximum"
    else:
        gain_bound = gain_at_first
        bound_source = "constant_gain"

    target_modulus = int(valuation_family["target_odd_modulus_3a"])
    target_residue = int(valuation_family["target_odd_residue_mod_3a"])
    congruence_passed = target_odd_first % target_modulus == target_residue
    local_descent_passed = gain_bound < 1
    status = "PASS" if congruence_passed and local_descent_passed else "FAIL_REQUIRES_DEBT_RANK"

    return {
        "branch_id": row["branch_id"],
        "source_state": {
            "parent_level": int(row["a"]),
            "odd_coordinate_residue": r0,
            "odd_coordinate_modulus": source_modulus,
        },
        "target_state": {
            "parent_level": int(valuation_family["target_parent_level"]),
            "odd_coordinate_residue_mod_3a": target_residue,
            "odd_coordinate_modulus_3a": target_modulus,
            "valuation": valuation,
        },
        "mixed_state": {
            "a": int(row["a"]),
            "rho": target_residue,
            "m": target_modulus,
            "delta": "log2_gain_bound",
        },
        "z_family": row["z_family"],
        "first_valid_k": first_k,
        "first_valid_source_odd": source_odd_first,
        "first_valid_target_odd": target_odd_first,
        "gain_at_first_valid_k": _fraction_payload(gain_at_first),
        "asymptotic_gain": _fraction_payload(asymptotic_gain),
        "gain_bound": _fraction_payload(gain_bound),
        "gain_bound_source": bound_source,
        "gain_bound_log2": math.log2(float(gain_bound)) if gain_bound > 0 else float("-inf"),
        "derivative_numerator": derivative_numerator,
        "exact_congruence_passed": congruence_passed,
        "local_descent_passed": local_descent_passed,
        "status": status,
        "proof_obligation": (
            "local transition decreases odd coordinate exactly"
            if local_descent_passed
            else "requires a debt/rank term because local odd coordinate may grow"
        ),
    }


def build_mixed_modulus_debt_report(
    high_parent_bypass_report: dict[str, Any],
    max_valuation_samples: int | None = None,
) -> dict[str, Any]:
    rows = list(high_parent_bypass_report.get("mixed_successor_families") or [])
    transitions: list[dict[str, Any]] = []
    for row in rows:
        families = list(row.get("valuation_family_samples") or [])
        if max_valuation_samples is not None:
            families = families[:max_valuation_samples]
        for family in families:
            transitions.append(debt_transition_for_family(row, family))

    exact_passed = bool(transitions) and all(row["exact_congruence_passed"] for row in transitions)
    local_pass_count = sum(1 for row in transitions if row["local_descent_passed"])
    local_failures = [row for row in transitions if not row["local_descent_passed"]]
    proof_closed = bool(transitions) and not local_failures and max_valuation_samples is None
    status = (
        "MIXED_MODULUS_DEBT_VERIFIER_READY_WITH_OPEN_BLOCKERS"
        if transitions and exact_passed
        else "MIXED_MODULUS_DEBT_VERIFIER_FAILED_EXACTNESS"
        if transitions
        else "NO_MIXED_MODULUS_TRANSITIONS"
    )
    return {
        "schema": MIXED_MODULUS_DEBT_SCHEMA,
        "version": 1,
        "status": status,
        "verifier_available": transitions != [] and exact_passed,
        "ready_for_run9": transitions != [] and exact_passed,
        "proof_closed": proof_closed,
        "verifier_status": "PASS" if proof_closed else "FAIL",
        "source_schema": high_parent_bypass_report.get("schema"),
        "source_status": high_parent_bypass_report.get("status"),
        "source_mixed_successor_family_count": high_parent_bypass_report.get("mixed_successor_family_count"),
        "max_valuation_samples": max_valuation_samples,
        "transition_count": len(transitions),
        "exact_transition_checks_passed": exact_passed,
        "local_descent_pass_count": local_pass_count,
        "local_descent_fail_count": len(local_failures),
        "local_descent_pass_rate": 0.0 if not transitions else local_pass_count / len(transitions),
        "failure_sample": local_failures[:20],
        "transition_sample": transitions[:20],
        "transitions": transitions,
        "blocking_obligations": []
        if proof_closed
        else [
            "prove the debt/rank update for every local transition whose odd-coordinate gain bound is >= 1",
            "prove unbounded valuation closure for all T, not only the sampled valuation families",
            "map mixed-modulus target states back into the global theorem obligation graph",
            "assemble the strict theorem candidate and require strict verifier PASS before proof confidence changes",
        ],
        "next_step": (
            "Use this verifier's PASS/FAIL transition traces to train the RUN-009 proof model, "
            "then search for a mixed-modulus debt/rank law that closes the failing transitions."
        ),
    }


def write_mixed_modulus_debt_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Mixed-Modulus Debt Verifier",
        "",
        f"- status: `{report['status']}`",
        f"- verifier available: `{report['verifier_available']}`",
        f"- ready for RUN-009 evaluation: `{report['ready_for_run9']}`",
        f"- proof closed: `{report['proof_closed']}`",
        f"- verifier status: `{report['verifier_status']}`",
        f"- transitions: `{report['transition_count']}`",
        f"- exact transition checks passed: `{report['exact_transition_checks_passed']}`",
        f"- local descent pass count: `{report['local_descent_pass_count']}`",
        f"- local descent fail count: `{report['local_descent_fail_count']}`",
        f"- local descent pass rate: `{report['local_descent_pass_rate']}`",
        "",
        "## Blocking Obligations",
        "",
    ]
    for blocker in report["blocking_obligations"]:
        lines.append(f"- {blocker}")
    if report.get("failure_sample"):
        lines.extend(["", "## Failure Sample", ""])
        for row in report["failure_sample"][:8]:
            bound = row["gain_bound"]
            lines.append(
                f"- `{row['branch_id']}` T=`{row['target_state']['valuation']}` "
                f"P{row['source_state']['parent_level']} -> P{row['target_state']['parent_level']}: "
                f"gain <= `{bound['numerator']}/{bound['denominator']}`"
            )
    lines.extend(["", "## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify exact mixed-modulus debt transitions.")
    parser.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    parser.add_argument("--max-valuation-samples", type=int, default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    source = json.loads(Path(args.high_parent_bypass).read_text(encoding="utf-8"))
    report = build_mixed_modulus_debt_report(source, max_valuation_samples=args.max_valuation_samples)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_mixed_modulus_debt_markdown(report, args.out_md or out.with_suffix(".md"))
    Console().print(
        {
            "out": str(out),
            "status": report["status"],
            "ready_for_run9": report["ready_for_run9"],
            "proof_closed": report["proof_closed"],
            "transition_count": report["transition_count"],
        }
    )


if __name__ == "__main__":
    main()
