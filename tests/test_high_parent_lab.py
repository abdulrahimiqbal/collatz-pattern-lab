from collatz_lab.high_parent_lab import (
    build_high_parent_feature_table,
    high_parent_feature_row,
    high_parent_p32_current,
    high_parent_root,
    parent_coordinate,
    v3_int,
)


def test_high_parent_entry_formula_and_features_are_exact() -> None:
    row = high_parent_feature_row(1, 1, max_steps=4)

    assert high_parent_root(1, 1) == 2**33 - 1
    assert high_parent_p32_current(1, 1) == 2**32 * 3 - 1
    assert row["first_p32_entry_step"] == 2
    assert row["enters_p32_with_expected_coordinate"] is True
    assert row["p32_entry_growth"] == {"num": 3, "den": 2, "is_below_root": False}
    assert parent_coordinate(high_parent_p32_current(1, 1)) == {"parent_level": 32, "parent_q": 3}
    assert v3_int(3**5 * 7) == 5


def test_feature_table_respects_configured_samples() -> None:
    rows = build_high_parent_feature_table(d_min=1, d_max=2, q_samples=[1, 2, 3], max_steps=4)

    assert [(row["d"], row["q"]) for row in rows] == [(1, 1), (1, 3), (2, 1), (2, 3)]
    assert all(row["kind"] == "HIGH_PARENT_FEATURE_ROW" for row in rows)
