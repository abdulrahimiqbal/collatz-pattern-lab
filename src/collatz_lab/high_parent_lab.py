"""Exact high-parent trajectory lab for RUN-066.

This module samples the remaining high-parent family

    n = 2^(32+d) * q - 1,  d >= 1, q odd positive

with exact integer arithmetic.  Rows emitted here are diagnostic data only;
they are not certificates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .collatz import collatz_step, v2


@dataclass(frozen=True)
class HighParentSample:
    d: int
    q: int


def v3_int(n: int) -> int:
    if n == 0:
        raise ValueError("v3_int is undefined for zero")
    value = abs(n)
    exponent = 0
    while value % 3 == 0:
        exponent += 1
        value //= 3
    return exponent


def high_parent_root(d: int, q: int) -> int:
    _check_sample(d, q)
    return (1 << (32 + d)) * q - 1


def high_parent_p32_current(d: int, q: int) -> int:
    _check_sample(d, q)
    return (1 << 32) * (3**d) * q - 1


def _check_sample(d: int, q: int) -> None:
    if d < 1:
        raise ValueError("d must be >= 1")
    if q <= 0 or q % 2 != 1:
        raise ValueError("q must be positive and odd")


def parent_coordinate(n: int) -> dict[str, int]:
    if n <= 0:
        raise ValueError("n must be positive")
    level = v2(n + 1)
    q = (n + 1) >> level
    return {"parent_level": level, "parent_q": q}


def _mod_features(q: int, powers_two: list[int], powers_three: list[int]) -> dict[str, Any]:
    return {
        "q_mod_powers_two": {f"2^{k}": q % (1 << k) for k in powers_two},
        "q_mod_powers_three": {f"3^{k}": q % (3**k) for k in powers_three},
    }


def high_parent_feature_row(
    d: int,
    q: int,
    *,
    max_steps: int = 1000,
    powers_two: list[int] | None = None,
    powers_three: list[int] | None = None,
) -> dict[str, Any]:
    """Return an exact diagnostic row for one high-parent sample."""

    _check_sample(d, q)
    powers_two = powers_two or [1, 2, 3, 4, 5, 6, 8]
    powers_three = powers_three or [1, 2, 3, 4]
    root = high_parent_root(d, q)
    p32_current = high_parent_p32_current(d, q)
    current = root
    parent_sequence: list[dict[str, int]] = []
    v2_sequence: list[int] = []
    v3_parent_coordinate_sequence: list[int] = []
    first_descent_below_root: int | None = None
    first_p32_entry_step: int | None = None
    enters_p32_with_expected_coordinate = False

    for step in range(0, max_steps + 1):
        coord = parent_coordinate(current)
        parent_sequence.append({"step": step, "n": current, **coord})
        v3_parent_coordinate_sequence.append(v3_int(coord["parent_q"]))
        if step > 0:
            v2_sequence.append(v2(previous_current_for_v2 + 1 if previous_current_for_v2 % 2 else previous_current_for_v2))
        if step == 2 * d and current == p32_current:
            first_p32_entry_step = step
            enters_p32_with_expected_coordinate = coord["parent_level"] == 32 and coord["parent_q"] == (3**d) * q
        if step > 0 and current < root:
            first_descent_below_root = step
            break
        if step == max_steps:
            break
        previous_current_for_v2 = current
        current = collatz_step(current)

    p32_entry_growth_num = 3**d
    p32_entry_growth_den = 2**d
    row = {
        "kind": "HIGH_PARENT_FEATURE_ROW",
        "d": d,
        "a": 32 + d,
        "q": q,
        "root": str(root),
        "p32_entry_current": str(p32_current),
        "p32_entry_step_count": 2 * d,
        "p32_entry_coordinate": str((3**d) * q),
        "p32_entry_growth": {
            "num": p32_entry_growth_num,
            "den": p32_entry_growth_den,
            "is_below_root": p32_current < root,
        },
        "first_p32_entry_step": first_p32_entry_step,
        "enters_p32_with_expected_coordinate": enters_p32_with_expected_coordinate,
        "first_descent_below_root": first_descent_below_root,
        "descent_found_within_max_steps": first_descent_below_root is not None,
        "parent_state_sequence_prefix": parent_sequence[:64],
        "v2_sequence_prefix": v2_sequence[:64],
        "v3_parent_coordinate_sequence_prefix": v3_parent_coordinate_sequence[:64],
        "debt_decreases_observed": any(
            entry["parent_level"] >= 33 and entry["parent_level"] - 32 < d
            for entry in parent_sequence
        ),
        "enters_certified_parent_range": any(2 <= entry["parent_level"] <= 32 for entry in parent_sequence),
        "enters_certified_subsystem_with_enough_root_margin": False,
        **_mod_features(q, powers_two, powers_three),
    }
    return row


def build_high_parent_feature_table(
    *,
    d_min: int,
    d_max: int,
    q_samples: list[int],
    max_steps: int,
    powers_two: list[int] | None = None,
    powers_three: list[int] | None = None,
) -> list[dict[str, Any]]:
    if d_min < 1:
        raise ValueError("d_min must be >= 1")
    if d_max < d_min:
        raise ValueError("d_max must be >= d_min")
    samples = [q for q in q_samples if q > 0 and q % 2 == 1]
    if not samples:
        raise ValueError("q_samples must contain at least one positive odd sample")
    return [
        high_parent_feature_row(
            d,
            q,
            max_steps=max_steps,
            powers_two=powers_two,
            powers_three=powers_three,
        )
        for d in range(d_min, d_max + 1)
        for q in samples
    ]
