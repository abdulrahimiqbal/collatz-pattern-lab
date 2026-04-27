from collatz_lab.collatz import (
    first_descent_time,
    signed_collatz_step,
    signed_cycle_id,
    signed_syracuse_step_odd,
    signed_v2_3n_plus_1,
    syracuse_step_odd,
    v2,
)


def test_v2_examples() -> None:
    assert v2(8) == 3
    assert v2(12) == 2
    assert v2(1) == 0


def test_syracuse_step_odd() -> None:
    assert syracuse_step_odd(3) == 5


def test_first_descent_time_small_values() -> None:
    assert first_descent_time(2) == 1
    assert first_descent_time(3) == 6
    assert first_descent_time(1) is None


def test_signed_collatz_negative_cycles() -> None:
    assert signed_collatz_step(-1) == -2
    assert signed_collatz_step(-2) == -1
    assert signed_cycle_id(-1)[0] == 1
    assert signed_cycle_id(-5)[0] == 2
    assert signed_cycle_id(-17)[0] == 3


def test_signed_syracuse_and_v2() -> None:
    assert signed_syracuse_step_odd(-1) == -1
    assert signed_syracuse_step_odd(-5) == -7
    assert signed_syracuse_step_odd(-7) == -5
    assert signed_v2_3n_plus_1(-7) == 2
