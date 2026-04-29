from collatz_lab.high_parent_invariant_verifier import verify_high_parent_invariant


def _base_candidate(**overrides):
    candidate = {
        "kind": "HIGH_PARENT_INVARIANT_CANDIDATE",
        "candidate_id": "synthetic",
        "invariant_type": "ROOT_DEBT_DECREASE",
        "claimed_domain": "d >= 1 and q > 0 and q % 2 = 1",
        "domain_coverage_proved": True,
        "integer_or_rational_arithmetic_only": True,
        "sample_only": False,
        "uses_float_or_log": False,
        "well_founded_measure": "Nat.debt",
        "all_transitions_decrease_debt": True,
    }
    candidate.update(overrides)
    return candidate


def test_verifier_rejects_sample_only_candidates() -> None:
    result = verify_high_parent_invariant(_base_candidate(sample_only=True))

    assert result["accepted"] is False
    assert result["reason"] == "SAMPLE_ONLY_INVARIANT_REJECTED"


def test_verifier_rejects_float_or_log_candidates() -> None:
    result = verify_high_parent_invariant(_base_candidate(uses_float_or_log=True))

    assert result["accepted"] is False
    assert result["reason"] == "FLOAT_OR_LOG_INVARIANT_REJECTED"


def test_verifier_rejects_missing_domain_after_local_proof() -> None:
    result = verify_high_parent_invariant(_base_candidate(domain_coverage_proved=False))

    assert result["accepted"] is False
    assert result["reason"] == "INVARIANT_DOMAIN_COVERAGE_MISSING"


def test_verifier_accepts_exact_synthetic_debt_decrease() -> None:
    result = verify_high_parent_invariant(_base_candidate())

    assert result["accepted"] is True
    assert result["reason"] == "ROOT_DEBT_DECREASE_VERIFIED"
