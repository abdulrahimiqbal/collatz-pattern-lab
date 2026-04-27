from collatz_lab.high_parent_bypass import build_high_parent_bypass_report
from collatz_lab.mixed_modulus_debt import build_mixed_modulus_debt_report, debt_transition_for_family


def _source_report():
    return {
        "schema": "collatz_lab.high_parent_branch_report",
        "status": "HIGH_PARENT_BRANCHES_OPEN",
        "branch_count": 1,
        "open_branch_count": 1,
        "branches": [
            {
                "a": 2,
                "r_residue": 5,
                "r_depth": 3,
                "h": 1,
                "known_target_parent_floor": 2,
                "ready_for_run7": False,
            }
        ],
    }


def test_debt_transition_computes_exact_gain_bound() -> None:
    bypass = build_high_parent_bypass_report(_source_report(), valuation_samples=2)
    row = bypass["mixed_successor_families"][0]
    transition = debt_transition_for_family(row, row["valuation_family_samples"][0])

    assert transition["exact_congruence_passed"] is True
    assert transition["gain_bound"]["numerator"] > 0
    assert transition["gain_bound"]["denominator"] > 0
    assert transition["status"] in {"PASS", "FAIL_REQUIRES_DEBT_RANK"}


def test_mixed_modulus_debt_report_is_run9_evaluator_not_proof_closure() -> None:
    bypass = build_high_parent_bypass_report(_source_report(), valuation_samples=2)
    report = build_mixed_modulus_debt_report(bypass)

    assert report["schema"] == "collatz_lab.mixed_modulus_debt_verifier"
    assert report["verifier_available"] is True
    assert report["ready_for_run9"] is True
    assert report["proof_closed"] is False
    assert report["verifier_status"] == "FAIL"
    assert report["transition_count"] == 2
    assert report["exact_transition_checks_passed"] is True
