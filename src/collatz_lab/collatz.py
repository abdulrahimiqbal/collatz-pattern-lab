"""Exact Collatz arithmetic.

All functions use Python ``int`` values. That matters: labels such as
``3*n + 1`` can overflow fixed-width integer arrays long before the surrounding
ML code notices. Keep arithmetic exact here, then serialize large values as
strings at dataset boundaries.
"""

from __future__ import annotations


NEGATIVE_CYCLE_IDS: dict[frozenset[int], int] = {
    frozenset({-2, -1}): 1,
    frozenset({-14, -7, -20, -10, -5}): 2,
    frozenset({-50, -25, -74, -37, -110, -55, -164, -82, -41, -122, -61, -182, -91, -272, -136, -68, -34, -17}): 3,
}


def _require_positive(n: int) -> None:
    if n < 1:
        raise ValueError("Collatz utilities require positive integers")


def _require_nonzero(n: int) -> None:
    if n == 0:
        raise ValueError("Signed Collatz utilities exclude zero")


def collatz_step(n: int) -> int:
    """Return the standard Collatz step C(n)."""

    _require_positive(n)
    if n % 2 == 0:
        return n // 2
    return 3 * n + 1


def shortcut_step(n: int) -> int:
    """Return the common one-division shortcut step.

    Odd values map to ``(3*n + 1) // 2`` and even values map to ``n // 2``.
    This is exact for odd ``n`` because ``3*n + 1`` is then even.
    """

    _require_positive(n)
    if n % 2 == 0:
        return n // 2
    return (3 * n + 1) // 2


def v2(n: int) -> int:
    """Return the 2-adic valuation of ``n``.

    ``v2(n)`` is the largest exponent ``a`` such that ``2**a`` divides ``n``.
    By convention in this codebase the input must be positive; ``v2(1) == 0``.
    """

    _require_positive(n)
    return (n & -n).bit_length() - 1


def syracuse_step_odd(n: int) -> int:
    """Return the accelerated Syracuse step for an odd integer.

    For odd ``n``, compute ``3*n + 1`` and divide out all powers of two:
    ``(3*n + 1) // 2**v2(3*n + 1)``.
    """

    _require_positive(n)
    if n % 2 == 0:
        raise ValueError("syracuse_step_odd requires n to be odd")
    m = 3 * n + 1
    return m // (1 << v2(m))


def trajectory(n: int, max_steps: int = 10000) -> list[int]:
    """Return the standard Collatz trajectory, including the starting value."""

    _require_positive(n)
    values = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = collatz_step(current)
        values.append(current)
    return values


def parity_prefix(n: int, k: int) -> list[int]:
    """Return the first ``k`` parity bits seen under standard Collatz steps."""

    _require_positive(n)
    if k < 0:
        raise ValueError("k must be non-negative")
    bits: list[int] = []
    current = n
    for _ in range(k):
        bits.append(current & 1)
        current = collatz_step(current)
    return bits


def first_descent_time(n: int, max_steps: int = 10000) -> int | None:
    """Return the first time ``t`` with ``C^t(n) < n``.

    ``None`` means no descent was found within ``max_steps``. For ``n == 1``
    there is no positive descent target, so the function returns ``None``.
    """

    _require_positive(n)
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")
    start = n
    current = n
    for t in range(1, max_steps + 1):
        current = collatz_step(current)
        if current < start:
            return t
    return None


def total_stopping_time(n: int, max_steps: int = 100000) -> int | None:
    """Return the first time ``t`` with ``C^t(n) == 1``."""

    _require_positive(n)
    current = n
    if current == 1:
        return 0
    for t in range(1, max_steps + 1):
        current = collatz_step(current)
        if current == 1:
            return t
    return None


def max_height_ratio(n: int, max_steps: int = 100000) -> float:
    """Return ``max(C^t(n)) / n`` over the computed trajectory."""

    _require_positive(n)
    values = trajectory(n, max_steps=max_steps)
    return float(max(values) / n)


def signed_collatz_step(n: int) -> int:
    """Return the standard Collatz step for any nonzero integer."""

    _require_nonzero(n)
    if n % 2 == 0:
        return n // 2
    return 3 * n + 1


def signed_shortcut_step(n: int) -> int:
    """Return the one-division shortcut step for any nonzero integer."""

    _require_nonzero(n)
    if n % 2 == 0:
        return n // 2
    return (3 * n + 1) // 2


def signed_v2_3n_plus_1(n: int) -> int:
    """Return ``v2(abs(3*n + 1))`` for any nonzero integer."""

    _require_nonzero(n)
    return v2(abs(3 * n + 1))


def signed_syracuse_step_odd(n: int) -> int:
    """Return the odd-only accelerated Syracuse step for signed odd integers."""

    _require_nonzero(n)
    if n % 2 == 0:
        raise ValueError("signed_syracuse_step_odd requires n to be odd")
    m = 3 * n + 1
    return m // (1 << v2(abs(m)))


def signed_trajectory(n: int, max_steps: int = 10000) -> list[int]:
    """Return the signed Collatz trajectory until a repeated value or 1."""

    _require_nonzero(n)
    values = [n]
    seen = {n}
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = signed_collatz_step(current)
        values.append(current)
        if current in seen:
            break
        seen.add(current)
    return values


def signed_parity_prefix(n: int, k: int) -> list[int]:
    """Return the first ``k`` parity bits under signed Collatz steps."""

    _require_nonzero(n)
    if k < 0:
        raise ValueError("k must be non-negative")
    bits: list[int] = []
    current = n
    for _ in range(k):
        bits.append(current & 1)
        current = signed_collatz_step(current)
    return bits


def normalize_cycle(cycle: list[int]) -> tuple[int, ...]:
    """Rotate a cycle so equivalent rotations share the same tuple."""

    if not cycle:
        return ()
    rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))]
    return min(rotations)


def detect_signed_cycle(n: int, max_steps: int = 10000) -> tuple[tuple[int, ...], int]:
    """Return ``(cycle, entry_time)`` for a signed Collatz orbit.

    If no repeat is found within ``max_steps``, ``cycle`` is empty and
    ``entry_time`` is ``max_steps``.
    """

    _require_nonzero(n)
    seen: dict[int, int] = {}
    current = n
    for step in range(max_steps + 1):
        if current in seen:
            entry = seen[current]
            values = list(seen.keys())
            return normalize_cycle(values[entry:]), entry
        seen[current] = step
        current = signed_collatz_step(current)
    return (), max_steps


def signed_cycle_id(n: int, max_steps: int = 10000) -> tuple[int, int]:
    """Return ``(cycle_id, entry_time)`` for a signed Collatz orbit.

    Known negative cycles receive stable ids. Unknown detected cycles receive
    id ``99`` and missing cycles receive id ``0``.
    """

    cycle, entry = detect_signed_cycle(n, max_steps=max_steps)
    if not cycle:
        return 0, entry
    return NEGATIVE_CYCLE_IDS.get(frozenset(cycle), 99), entry
