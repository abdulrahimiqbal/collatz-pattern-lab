from collatz_lab.parent_states import parent_level, parent_transition


def test_parent_level() -> None:
    assert parent_level(63) == 6
    assert parent_level(31) == 5


def test_parent_transition_q87_goes_from_p6_to_p5() -> None:
    row = parent_transition(6, 87)
    assert row["a"] == 6
    assert row["h"] == 1
    assert row["a_next"] == 5
    assert row["transition"] == "P_6->P_5"


def test_parent_transition_q23_returns_to_p6() -> None:
    row = parent_transition(6, 23)
    assert row["h"] == 1
    assert row["a_next"] == 6
    assert row["transition"] == "P_6->P_6"
