from collatz_lab.burst import (
    burst_escape_q_condition_for_parent,
    burst_escape_residue_mod_power,
    decompose_q,
    h_star,
)
from collatz_lab.collatz import collatz_step


def _iterate_standard(n: int, steps: int) -> int:
    current = n
    for _ in range(steps):
        current = collatz_step(current)
    return current


def test_decompose_q() -> None:
    assert decompose_q(1) == (0, 6, 1)
    assert decompose_q(8) == (3, 9, 1)


def test_h_star_a6() -> None:
    assert h_star(6) == 4


def test_burst_escape_residue_a6() -> None:
    assert burst_escape_residue_mod_power(6) == (9, 4)


def test_burst_escape_q_condition_a6() -> None:
    condition = burst_escape_q_condition_for_parent(6)
    assert condition["q_residue"] == 9
    assert condition["q_depth"] == 4
    assert condition["descent_steps_standard"] == 16


def test_q_9_mod_16_descends_after_16_standard_steps() -> None:
    for high in range(8):
        q = 9 + 16 * high
        n = 64 * q - 1
        assert _iterate_standard(n, 16) < n
