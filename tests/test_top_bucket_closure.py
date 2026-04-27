from collatz_lab.top_bucket_closure import (
    audit_bucket,
    build_top_bucket_closure_report,
    parent_burst_affine_on_n,
)


def test_low_h_parent_burst_records_unpaid_debt() -> None:
    block = parent_burst_affine_on_n(a=6, h=1)

    assert block["A"] == 729
    assert block["D"] == 128
    assert block["expands_ancestor_value"] is True


def test_top_bucket_audit_does_not_close_lower_transition_debt() -> None:
    bucket = {
        "rank": 1,
        "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
        "t": 0,
        "a": 6,
        "h": 1,
        "unknown_q_classes": 161792,
        "parent_transition_split": {
            "children": [
                {"a_next": 1, "relation": "lower", "residue_count": 16},
                {"a_next": 2, "relation": "lower", "residue_count": 8},
                {"a_next": 3, "relation": "lower", "residue_count": 4},
                {"a_next": 4, "relation": "lower", "residue_count": 2},
                {"a_next": 5, "relation": "lower", "residue_count": 1},
                {"a_next": 6, "relation": "self", "residue_count": 1},
            ]
        },
    }

    audit = audit_bucket(bucket)

    assert audit["status"] == "NEEDS_DEBT_CARRYING_PARENT_INDUCTION"
    assert audit["is_closed"] is False
    assert audit["split_matches_weighted_report"] is True
    assert audit["debt_induction_certificate_applied"] is False
    assert audit["child_status_counts"]["BLOCKED_BY_UNPAID_ANCESTOR_DEBT"] == 5
    assert audit["child_status_counts"]["REDUCED_BY_HEIGHT_RANKED_SELF_RETURN"] == 1


def test_top_bucket_closure_report_keeps_progress_unchanged_without_closed_buckets() -> None:
    weighted = {
        "proof_progress_breakdown": {
            "selected": {
                "numerator": 40,
                "denominator": 100,
                "source": "residual.json",
            },
            "strict_graph": {"numerator": 1, "denominator": 4, "percent": 25.0},
        },
        "target_buckets": [
            {
                "rank": 1,
                "obligation_id": "unresolved_bucket:t=1:a=7:h=1",
                "t": 1,
                "a": 7,
                "h": 1,
                "unknown_q_classes": 10,
                "parent_transition_split": {
                    "children": [
                        {"a_next": 1, "relation": "lower", "residue_count": 16},
                        {"a_next": 2, "relation": "lower", "residue_count": 8},
                        {"a_next": 3, "relation": "lower", "residue_count": 4},
                        {"a_next": 4, "relation": "lower", "residue_count": 2},
                        {"a_next": 5, "relation": "lower", "residue_count": 1},
                        {"a_next": 6, "relation": "lower", "residue_count": 1},
                    ]
                },
            }
        ],
    }

    report = build_top_bucket_closure_report(weighted, top_n=1)

    assert report["closed_target_bucket_count"] == 0
    assert report["closed_target_q_classes"] == 0
    assert report["target_progress_if_all_top_n_closed_percent"] == 50.0
    assert report["proof_progress_percent"] == 40.0
    assert report["proof_progress_breakdown"]["selected"]["run6_added_closed_q_classes"] == 0


def test_formal_debt_induction_certificate_can_close_covered_bucket() -> None:
    weighted = {
        "proof_progress_breakdown": {
            "selected": {
                "numerator": 40,
                "denominator": 100,
                "source": "residual.json",
            },
        },
        "target_buckets": [
            {
                "rank": 1,
                "obligation_id": "unresolved_bucket:t=1:a=7:h=1",
                "t": 1,
                "a": 7,
                "h": 1,
                "unknown_q_classes": 10,
                "parent_transition_split": {
                    "children": [
                        {"a_next": 1, "relation": "lower", "residue_count": 16},
                        {"a_next": 2, "relation": "lower", "residue_count": 8},
                        {"a_next": 3, "relation": "lower", "residue_count": 4},
                        {"a_next": 4, "relation": "lower", "residue_count": 2},
                        {"a_next": 5, "relation": "lower", "residue_count": 1},
                        {"a_next": 6, "relation": "lower", "residue_count": 1},
                    ]
                },
            }
        ],
    }
    debt = {
        "status": "PROVED_DEBT_CARRYING_PARENT_INDUCTION",
        "ready_for_run7": True,
        "target_obligations": ["unresolved_bucket:t=1:a=7:h=1"],
    }

    report = build_top_bucket_closure_report(weighted, top_n=1, debt_induction_report=debt)

    assert report["closed_target_bucket_count"] == 1
    assert report["closed_target_q_classes"] == 10
    assert report["proof_progress_percent"] == 50.0
    assert report["ready_for_run7"] is True
