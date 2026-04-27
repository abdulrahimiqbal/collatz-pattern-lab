from collatz_lab.debt_induction import (
    build_debt_induction_report,
    build_same_depth_residue_potential_search,
)


def _weighted_report() -> dict:
    return {
        "target_buckets": [
            {
                "rank": 1,
                "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
                "t": 0,
                "a": 6,
                "h": 1,
                "unknown_q_classes": 161792,
            }
        ]
    }


def test_same_depth_potential_search_is_diagnostic_only() -> None:
    report = build_same_depth_residue_potential_search(
        _weighted_report()["target_buckets"],
        r_depth=4,
        max_states=1000,
    )

    assert report["claim_status"] == "DIAGNOSTIC_NOT_PROOF"
    assert report["formal_exactness_passed"] is False
    assert report["edge_count"] > 0


def test_debt_induction_gate_blocks_run7_without_formal_certificate() -> None:
    report = build_debt_induction_report(
        _weighted_report(),
        top_n=1,
        r_depths=[4],
        max_states=1000,
    )

    assert report["ready_for_run7"] is False
    assert report["status"] == "DEBT_INDUCTION_NOT_FIXED"
    assert "no exact debt-carrying induction certificate has been verified" in report["formal_blockers"]


def test_variable_depth_certificate_promotes_debt_gate_when_ready() -> None:
    report = build_debt_induction_report(
        _weighted_report(),
        top_n=1,
        r_depths=[4],
        max_states=1000,
        variable_depth_certificate={
            "status": "EXACT_VARIABLE_DEPTH_POTENTIAL_PASS",
            "ready_for_run7": True,
        },
    )

    assert report["ready_for_run7"] is True
    assert report["status"] == "PROVED_DEBT_CARRYING_PARENT_INDUCTION"
    assert report["formal_certificate_sources"] == ["variable_depth_transition_certificate"]


def test_open_high_parent_branches_are_explicit_debt_blockers() -> None:
    report = build_debt_induction_report(
        _weighted_report(),
        top_n=1,
        r_depths=[4],
        max_states=1000,
        variable_depth_certificate={
            "status": "VARIABLE_DEPTH_CERTIFICATE_NOT_READY",
            "ready_for_run7": False,
            "formal_blockers": ["variable-depth exact projection still has blocked states"],
        },
        high_parent_branch_report={
            "status": "HIGH_PARENT_BRANCHES_OPEN",
            "ready_for_run7": False,
            "formal_blockers": ["symbolic high-parent branches are derived but not closed"],
        },
    )

    assert report["ready_for_run7"] is False
    assert "symbolic high-parent branches are derived but not closed" in report["formal_blockers"]
