"""Exact root-relative inequalities for high-parent accelerated branches."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .high_parent_domain_partition import minimal_q_for_domain


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def prove_one_step_root_descent(
    *,
    domain: dict[str, Any],
    h: int,
) -> dict[str, Any]:
    """Try to prove ``(3^(32+d)q - 1)/2^h < 2^(32+d)q - 1``.

    The proof is exact and integer-only.  For the current RUN-067 bounded
    families this fails, but the returned object keeps the exact inequality and
    witness branch for downstream refinement.
    """

    d_congruence = domain.get("d_congruence", {}) if isinstance(domain.get("d_congruence"), dict) else {}
    d_min = _as_int(d_congruence.get("minimum_d"), 1)
    q_min = minimal_q_for_domain(domain)
    root_power = 32 + d_min
    left = (3**root_power) * q_min - 1
    right = (2**h) * ((2**root_power) * q_min - 1)
    coefficient = (2 ** (h + root_power)) - (3**root_power)
    threshold = (2**h) - 1
    passed = left < right
    result = {
        "kind": "ROOT_RELATIVE_INEQUALITY_PROOF",
        "status": "PASS" if passed else "FAIL",
        "inequality": "(3^(32+d)*q - 1) / 2^h < 2^(32+d)*q - 1",
        "integer_cross_multiplication": "3^(32+d)*q - 1 < 2^h*(2^(32+d)*q - 1)",
        "equivalent_linear_form": "(2^(h+32+d) - 3^(32+d))*q > 2^h - 1",
        "d_min": d_min,
        "q_min": q_min,
        "h": h,
        "coefficient_at_min_d": coefficient,
        "required_positive_rhs": threshold,
        "left_at_min_domain": left,
        "right_at_min_domain": right,
        "exact_arithmetic": True,
        "uses_float_or_log": False,
        "reason": "ROOT_RELATIVE_DESCENT_PROVED"
        if passed
        else "ROOT_RELATIVE_INEQUALITY_FALSE_AT_MIN_DOMAIN_POINT",
    }
    result["proof_hash"] = stable_hash({key: value for key, value in result.items() if key != "proof_hash"})
    return result


def prove_debt_reduction(*, domain: dict[str, Any], target_parent: int) -> dict[str, Any]:
    d_congruence = domain.get("d_congruence", {}) if isinstance(domain.get("d_congruence"), dict) else {}
    d_min = _as_int(d_congruence.get("minimum_d"), 1)
    target_debt = max(0, target_parent - 32)
    passed = target_parent >= 33 and target_debt < d_min
    result = {
        "kind": "ROOT_DEBT_REDUCTION_PROOF",
        "status": "PASS" if passed else "FAIL",
        "source_debt": {"symbol": "d", "minimum": d_min},
        "target_parent": target_parent,
        "target_debt": target_debt,
        "inequality": "target_debt < d",
        "exact_arithmetic": True,
        "reason": "ROOT_DEBT_DECREASE_PROVED" if passed else "TARGET_DOES_NOT_PROVE_SMALLER_HIGH_PARENT_DEBT",
    }
    result["proof_hash"] = stable_hash({key: value for key, value in result.items() if key != "proof_hash"})
    return result

