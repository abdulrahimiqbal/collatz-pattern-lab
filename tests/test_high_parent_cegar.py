from collatz_lab.high_parent_cegar import run_high_parent_cegar


def test_cegar_reports_minimal_obstruction_when_no_rule_verifies() -> None:
    result = run_high_parent_cegar(
        d_min=1,
        d_max=1,
        q_samples=[1],
        max_steps=8,
        semantic_witnesses=[],
        margin_report={"available_certificate_inventory": {"passing_root_relative_margin_count": 0}},
    )

    assert result["run_result"]["status"] == "FAIL"
    assert result["run_result"]["formalization_status"] == "HIGH_PARENT_OBSTRUCTION"
    assert result["accepted_certificates"] == []
    assert result["uncovered_domains"][0]["failure_reason"] == "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING"
    assert result["minimal_obstruction"]["minimal_example"] == {"d": 1, "a": 33, "q": 1, "n": 2**33 - 1}


def test_cegar_closes_when_exact_margin_candidate_is_present() -> None:
    result = run_high_parent_cegar(
        d_min=1,
        d_max=1,
        q_samples=[1],
        max_steps=8,
        semantic_witnesses=[],
        margin_report={"available_certificate_inventory": {"candidate_root_relative_margin_count": 1, "passing_root_relative_margin_count": 1}},
    )

    assert result["run_result"]["status"] == "PASS"
    assert result["run_result"]["formalization_status"] == "HIGH_PARENT_ENTRY_COVERAGE_PASS"
    assert len(result["accepted_certificates"]) == 1
    assert result["uncovered_domains"] == []
