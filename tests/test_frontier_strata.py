from collatz_lab.frontier_strata import (
    build_frontier_strata_report,
    burst_features_for_q_residue,
    representative_q,
)


def test_representative_q_handles_zero_residue() -> None:
    assert representative_q(0, 4) == 16
    assert representative_q(3, 4) == 3


def test_q_9_mod_16_is_burst_escape_at_a6() -> None:
    features = burst_features_for_q_residue(9, 4)
    assert features["a"] == 6
    assert features["burst_escape"] is True


def test_small_frontier_strata_report_smoke() -> None:
    report = build_frontier_strata_report(q_depth=3, candidate=None, max_steps=4, show_progress=False)
    assert report["q_depth"] == 3
    assert sum(report["status_counts"].values()) == 8
    assert report["by_t"]
    assert "top_unresolved_recursive_states" in report
