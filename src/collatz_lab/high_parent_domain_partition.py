"""Exact symbolic domain helpers for RUN-069 high-parent recursion."""

from __future__ import annotations

from math import gcd
from typing import Any


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def merge_congruence(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Merge two congruences exactly.

    Returns a fail-closed object instead of silently accepting incompatible
    residue constraints.
    """

    r1 = _as_int(left.get("residue"))
    m1 = _as_int(left.get("modulus"), 1)
    r2 = _as_int(right.get("residue"))
    m2 = _as_int(right.get("modulus"), 1)
    if m1 <= 0 or m2 <= 0:
        return {"status": "INCOMPATIBLE", "reason": "NONPOSITIVE_MODULUS", "left": left, "right": right}
    g = gcd(m1, m2)
    if (r2 - r1) % g != 0:
        return {"status": "INCOMPATIBLE", "reason": "RESIDUES_DISAGREE_MOD_GCD", "left": left, "right": right}
    lcm = m1 // g * m2
    # Solve r1 + m1*t = r2 mod m2.
    reduced_m1 = m1 // g
    reduced_m2 = m2 // g
    rhs = (r2 - r1) // g
    t = (rhs * pow(reduced_m1 % reduced_m2, -1, reduced_m2)) % reduced_m2
    residue = (r1 + m1 * t) % lcm
    return {"status": "PASS", "residue": residue, "modulus": lcm}


def domain_from_p32_family(family: dict[str, Any]) -> dict[str, Any]:
    domain = family.get("domain", {}) if isinstance(family.get("domain"), dict) else {}
    d_congruence = domain.get("d_congruence", {}) if isinstance(domain.get("d_congruence"), dict) else {}
    q_congruence = domain.get("q_congruence", {}) if isinstance(domain.get("q_congruence"), dict) else {}
    return {
        "kind": "HIGH_PARENT_DOMAIN",
        "d_range": {"type": "tail", "lower_bound": _as_int(d_congruence.get("minimum_d"), 1)},
        "d_congruence": {
            "residue": _as_int(d_congruence.get("residue")),
            "modulus": _as_int(d_congruence.get("modulus"), 1),
            "minimum_d": _as_int(d_congruence.get("minimum_d"), 1),
        },
        "q_domain": domain.get("q_domain", "q > 0 and q % 2 = 1"),
        "q_congruence": {
            "residue": _as_int(q_congruence.get("residue")),
            "modulus": _as_int(q_congruence.get("modulus"), 1),
            "modulus_power": _as_int(q_congruence.get("modulus_power"), 0),
        },
    }


def minimal_positive_residue(residue: int, modulus: int) -> int:
    return residue if residue > 0 else modulus


def minimal_q_for_domain(domain: dict[str, Any]) -> int:
    q_congruence = domain.get("q_congruence", {}) if isinstance(domain.get("q_congruence"), dict) else {}
    return minimal_positive_residue(_as_int(q_congruence.get("residue")), _as_int(q_congruence.get("modulus"), 1))


def domain_key(domain: dict[str, Any]) -> str:
    dc = domain.get("d_congruence", {})
    qc = domain.get("q_congruence", {})
    return (
        f"d{dc.get('residue')}_mod{dc.get('modulus')}_from{dc.get('minimum_d')}:"
        f"q{qc.get('residue')}_mod{qc.get('modulus')}"
    )


def universal_high_parent_domain() -> dict[str, Any]:
    return {
        "kind": "HIGH_PARENT_DOMAIN",
        "domain_id": "high_parent_all_d_ge_1_q_odd_positive",
        "d_range": {"type": "tail", "lower_bound": 1},
        "parent_level_range": {"type": "tail", "lower_bound": 33},
        "q_domain": "q > 0 and q % 2 = 1",
    }


def remaining_parent_family(reason: str) -> dict[str, Any]:
    return {
        "kind": "UNCOVERED_PARENT_FAMILY",
        "family_id": "odd_entry_parent_levels_ge_33",
        "parent_level_range": {"type": "tail", "lower_bound": 33},
        "q_domain": "q > 0 and q % 2 = 1",
        "example": {"a": 33, "d": 1, "q": 1, "n_expr": "2^33 - 1"},
        "missing_transition_or_coverage_certificate": "no exact accelerated-recursion certificate closes the high-parent root-relative branch",
        "failure_reason": reason,
    }

