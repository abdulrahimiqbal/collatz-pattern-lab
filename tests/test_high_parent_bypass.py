from collatz_lab.high_parent_branch import derive_high_parent_branch
from collatz_lab.high_parent_bypass import (
    build_high_parent_bypass_report,
    high_parent_coefficients,
    valuation_successor_family,
)


def test_valuation_successor_family_preserves_mod_3a_information() -> None:
    branch = derive_high_parent_branch(a=7, r_residue=9512459, r_depth=24)
    coeffs = high_parent_coefficients(branch)

    assert coeffs["known_target_parent_floor"] == 21
    assert coeffs["coefficient"] == 3**7

    for valuation in range(4):
        family = valuation_successor_family(branch, valuation)
        assert family["target_parent_level"] == 21 + valuation
        assert family["target_odd_modulus_3a"] == 3**7
        assert family["sample_checks_passed"] is True
        assert family["sample_checks"]


def test_high_parent_bypass_derives_successors_without_marking_proof_ready() -> None:
    branch = derive_high_parent_branch(a=7, r_residue=9512459, r_depth=24)
    report = build_high_parent_bypass_report(
        {
            "status": "HIGH_PARENT_BRANCHES_OPEN",
            "branch_count": 1,
            "open_branch_count": 1,
            "branches": [branch],
        },
        valuation_samples=3,
    )

    assert report["schema"] == "collatz_lab.high_parent_bypass"
    assert report["status"] == "MIXED_MODULUS_BYPASS_BUILT"
    assert report["mixed_successor_family_count"] == 1
    assert report["all_sample_checks_passed"] is True
    assert report["ready_for_run7"] is False
    assert "no verifier consumes odd-modulus/debt states" in report["formal_blockers"][0]


def test_level_rank_obstruction_is_reported_for_current_high_parent_fixture() -> None:
    branches = [
        derive_high_parent_branch(a=20, r_residue=46520809, r_depth=26),
        derive_high_parent_branch(a=23, r_residue=60246179, r_depth=26),
    ]
    report = build_high_parent_bypass_report(
        {
            "status": "HIGH_PARENT_BRANCHES_OPEN",
            "branch_count": len(branches),
            "open_branch_count": len(branches),
            "branches": branches,
        },
        valuation_samples=1,
    )

    assert report["level_rank_analysis"]["status"] == "FAIL"
    assert report["level_rank_analysis"]["positive_cycle_witness"]
