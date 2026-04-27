from collatz_lab.global_parent_obligations import build_global_parent_obligations


def test_global_parent_obligations_expose_transition_blockers() -> None:
    report = build_global_parent_obligations(
        parent_state_system={"a_min": 1, "a_max": 3, "r_depth": 4, "row_count": 24, "state_count": 3},
        parametric_a={"depth": 5, "period": 8, "group_count": 8, "sample_period_check_passed": True},
    )
    assert report["status"] == "INCOMPLETE_OPEN_OBLIGATIONS"
    assert report["coverage"]["status"] == "UNIVERSAL_ENTRY_COVERAGE_ONLY"
    assert report["open_obligation_count"] == 2
