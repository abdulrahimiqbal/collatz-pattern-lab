"""Exact P32 special-family transition derivation for RUN-067.

The remaining high-parent entry family reaches

    P32(Q),  Q = 3^d * q

with root still equal to ``2^(32+d)*q - 1``.  This module derives exact
symbolic transition families for the next accelerated P32 block:

    3^32 * Q - 1 = 3^(32+d) * q - 1.

For fixed ``d``, ``h`` and target parent ``b``, the domain is a single residue
class modulo ``2^(h+b+1)``.  The extra bit makes the valuation exact rather
than merely divisibility metadata.
"""

from __future__ import annotations

import hashlib
import json
from math import gcd
from pathlib import Path
from typing import Any

from .burst import v2_int


RUN_ID = "RUN-067-p32-special-family-transition-derivation"
SCHEMA = "collatz_lab.run067_p32_special_transition"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def write_json(data: Any, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def multiplicative_order_mod_power_two(base: int, modulus_power: int) -> int:
    """Return the multiplicative order of ``base`` modulo ``2^modulus_power``."""

    if modulus_power < 1:
        raise ValueError("modulus_power must be positive")
    modulus = 1 << modulus_power
    if gcd(base, modulus) != 1:
        raise ValueError("base must be odd for a power-of-two modulus")
    value = base % modulus
    current = 1 % modulus
    for order in range(1, 1 << max(1, modulus_power)):
        current = (current * value) % modulus
        if current == 1 % modulus:
            return order
    raise AssertionError("failed to find multiplicative order modulo 2^k")


def p32_special_residue(*, d_mod: int, d_period: int, h: int, b: int) -> dict[str, int]:
    """Return the exact residue class for fixed ``d mod period``, ``h`` and ``b``.

    The class is modulo ``2^(h+b+1)`` and is characterized by:

    * ``v2(3^(32+d) q - 1) = h``;
    * ``v2(((3^(32+d) q - 1) / 2^h) + 1) = b``.
    """

    if h < 1:
        raise ValueError("h must be at least 1")
    if b < 1:
        raise ValueError("b must be at least 1")
    if not (0 <= d_mod < d_period):
        raise ValueError("d_mod must be in [0, d_period)")
    modulus_power = h + b + 1
    modulus = 1 << modulus_power
    a_mod = pow(3, 32 + d_mod, modulus)
    base_modulus = 1 << (h + b)
    base_residue = ((1 - (1 << h)) * pow(a_mod % base_modulus, -1, base_modulus)) % base_modulus
    residues = [base_residue, base_residue + base_modulus]
    exact = [
        residue
        for residue in residues
        if v2_int(a_mod * residue + (1 << h) - 1) == h + b
        and v2_int(a_mod * residue - 1) == h
    ]
    if len(exact) != 1:
        raise AssertionError(f"expected exactly one exact residue, got {exact}")
    return {
        "modulus_power": modulus_power,
        "modulus": modulus,
        "residue": exact[0],
        "a_mod": a_mod,
        "base_residue_mod_2_h_plus_b": base_residue,
    }


def minimal_positive_q(residue: int, modulus: int) -> int:
    if residue > 0:
        return residue
    return modulus


def direct_root_descent_holds_for_family(*, d_min: int, h: int, q_min: int) -> bool:
    """Check the exact family inequality at the smallest q in the residue class."""

    if d_min < 1:
        raise ValueError("d_min must be >= 1")
    a = 32 + d_min
    coefficient = (1 << h) * ((1 << a)) - 3**a
    return coefficient > 0 and coefficient * q_min > (1 << h) - 1


def root_relative_outcome(*, d_min: int, h: int, b: int, q_min: int) -> dict[str, Any]:
    direct = direct_root_descent_holds_for_family(d_min=d_min, h=h, q_min=q_min)
    if direct:
        kind = "DIRECT_ROOT_DESCENT"
    elif b >= 33 and b - 32 < d_min:
        kind = "ROOT_DEBT_DECREASE"
    elif b <= 32:
        kind = "FINITE_SUBSYSTEM_ENTRY_NEEDS_ROOT_MARGIN"
    else:
        kind = "NO_ROOT_RELATIVE_PROGRESS_PROVED"
    return {
        "kind": kind,
        "direct_root_descent": direct,
        "target_debt": b - 32 if b >= 33 else 0,
        "debt_decreases_for_min_d": b >= 33 and b - 32 < d_min,
        "needs_p32_or_finite_margin": kind == "FINITE_SUBSYSTEM_ENTRY_NEEDS_ROOT_MARGIN",
    }


def build_p32_special_transition_family(*, d_mod: int, d_period: int, h: int, b: int) -> dict[str, Any]:
    residue_data = p32_special_residue(d_mod=d_mod, d_period=d_period, h=h, b=b)
    # Smallest positive d in this congruence class with d >= 1.
    d_min = d_mod if d_mod >= 1 else d_period
    q_min = minimal_positive_q(residue_data["residue"], residue_data["modulus"])
    outcome = root_relative_outcome(d_min=d_min, h=h, b=b, q_min=q_min)
    family = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "P32_SPECIAL_TRANSITION_FAMILY",
        "domain": {
            "d_congruence": {"residue": d_mod, "modulus": d_period, "minimum_d": d_min},
            "q_congruence": {
                "residue": residue_data["residue"],
                "modulus": residue_data["modulus"],
                "modulus_power": residue_data["modulus_power"],
            },
            "q_domain": "q > 0 and q % 2 = 1",
        },
        "transition": {
            "source": "P32(3^d*q)",
            "root": "2^(32+d)*q - 1",
            "current": "2^32*3^d*q - 1",
            "forced_burst": "3^(32+d)*q - 1",
            "h": h,
            "post_division": "(3^(32+d)*q - 1) / 2^h",
            "target_parent": b,
            "target_q_expr": "(3^(32+d)*q + 2^h - 1) / 2^(h+b)",
            "standard_step_count": 64 + h,
        },
        "exactness_checks": {
            "h_exact_statement": "v2(3^(32+d)*q - 1) = h",
            "b_exact_statement": "v2(((3^(32+d)*q - 1)/2^h) + 1) = b",
            "residue_modulus_uses_exactness_bit": True,
            "a_mod": residue_data["a_mod"],
        },
        "root_relative_outcome": outcome,
    }
    family["family_hash"] = stable_hash({key: value for key, value in family.items() if key != "family_hash"})
    return family


def build_p32_special_transition_schema() -> dict[str, Any]:
    schema = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "P32_SPECIAL_TRANSITION_SCHEMA",
        "statement": "For every d >= 1, q odd positive, h = v2(3^(32+d)q - 1), and b = v2(((3^(32+d)q - 1)/2^h)+1), the next P32 special transition reaches P_b(q').",
        "domain_parameters": ["d >= 1", "h >= 1", "b >= 1", "q > 0 odd"],
        "q_residue_formula": "For fixed d modulo ord_{2^(h+b+1)}(3), q is the unique residue modulo 2^(h+b+1) with v2(3^(32+d)q-1)=h and v2(3^(32+d)q+2^h-1)=h+b.",
        "target_q_expr": "(3^(32+d)*q + 2^h - 1) / 2^(h+b)",
        "standard_step_count": "64 + h",
        "root_relative_note": "This schema derives transitions only; root-relative descent still requires a margin/debt invariant.",
    }
    schema["schema_hash"] = stable_hash({key: value for key, value in schema.items() if key != "schema_hash"})
    return schema


def build_p32_special_transition_families(
    *,
    h_max: int,
    b_max: int,
    max_families: int | None = None,
) -> list[dict[str, Any]]:
    if h_max < 1:
        raise ValueError("h_max must be >= 1")
    if b_max < 1:
        raise ValueError("b_max must be >= 1")
    families: list[dict[str, Any]] = []
    for h in range(1, h_max + 1):
        for b in range(1, b_max + 1):
            period = multiplicative_order_mod_power_two(3, h + b + 1)
            for d_mod in range(period):
                families.append(build_p32_special_transition_family(d_mod=d_mod, d_period=period, h=h, b=b))
                if max_families is not None and len(families) >= max_families:
                    return families
    return families


def build_p32_special_uncovered_domains(*, h_max: int, b_max: int, families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    uncovered = [
        {
            "kind": "P32_SPECIAL_UNCOVERED_DOMAIN",
            "domain_id": "p32_special_h_beyond_enumeration_bound",
            "d_range": {"type": "tail", "lower_bound": 1},
            "q_domain": f"q odd positive with h = v2(3^(32+d)q - 1) > {h_max}",
            "failure_reason": "P32_SPECIAL_VALUATION_BOUND_INCOMPLETE",
        },
        {
            "kind": "P32_SPECIAL_UNCOVERED_DOMAIN",
            "domain_id": "p32_special_b_beyond_enumeration_bound",
            "d_range": {"type": "tail", "lower_bound": 1},
            "q_domain": f"q odd positive with target parent b > {b_max}",
            "failure_reason": "P32_SPECIAL_TARGET_PARENT_BOUND_INCOMPLETE",
        },
    ]
    if not any(row.get("root_relative_outcome", {}).get("kind") in {"DIRECT_ROOT_DESCENT", "ROOT_DEBT_DECREASE"} for row in families):
        uncovered.append(
            {
                "kind": "P32_SPECIAL_UNCOVERED_DOMAIN",
                "domain_id": "p32_special_root_relative_invariant_missing",
                "d_range": {"type": "tail", "lower_bound": 1},
                "q_domain": "q > 0 and q % 2 = 1",
                "failure_reason": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING",
                "detail": "Derived transition families do not by themselves prove universal root-relative descent.",
            }
        )
    return uncovered
