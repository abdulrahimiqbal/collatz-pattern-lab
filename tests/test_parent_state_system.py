from collatz_lab.parent_state_system import build_parent_state_system_report, classify_parent_residue


def test_q23_and_q87_parent_transitions() -> None:
    q23 = classify_parent_residue(6, 23, 7)
    q87 = classify_parent_residue(6, 87, 7)
    assert q23["transition"] == "P_6->P_6"
    assert q87["transition"] == "P_6->P_5"


def test_parent_state_system_report() -> None:
    report = build_parent_state_system_report(1, 3, r_depth=3)
    assert report["status"] == "FINITE_DEPTH_DIAGNOSTIC_NOT_PROOF"
    assert report["row_count"] == 12
    assert report["transition_counts"]
