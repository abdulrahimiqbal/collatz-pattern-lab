from collatz_lab.frontier import classify_frontier, classify_residue, summarize_frontier


def test_even_residue_is_certified_by_affine_descent() -> None:
    row = classify_residue(mod_power=1, residue=0, max_steps=4)
    assert row.status == "CERTIFIED_DESCENT"
    assert row.descent_k == 1


def test_frontier_reports_unknown_when_modulus_is_too_shallow() -> None:
    row = classify_residue(mod_power=1, residue=1, max_steps=6, include_eventual_residue=False)
    assert row.status == "UNKNOWN"
    assert "lift-power" in row.reason


def test_lifted_frontier_aggregates_child_certificates() -> None:
    rows = classify_frontier(mod_power=1, lift_power=2, max_steps=2, show_progress=False)
    summary = summarize_frontier(rows)
    assert summary["rows"] == 2
    assert set(summary["status_counts"])
