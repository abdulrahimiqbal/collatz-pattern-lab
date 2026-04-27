from collatz_lab.p6_subtheorem import build_p6_subtheorem_report


def test_p6_subtheorem_remains_open_with_blockers() -> None:
    report = build_p6_subtheorem_report(
        {
            "open_obligation_count": 1,
            "obligations": [
                {
                    "obligation_id": "open",
                    "scc_status": "NEEDS_SPLIT",
                    "scope": "synthetic blocker",
                }
            ],
        }
    )
    assert report["verifier_status"] == "FAIL"
    assert report["open_obligation_count"] == 1


def test_p6_subtheorem_passes_empty_graph() -> None:
    report = build_p6_subtheorem_report(
        {"open_obligation_count": 0, "obligations": []},
        {"open": [], "closed": ["a"], "nodes": {"a": {"status": "CLOSED_BY_ANCESTOR_DESCENT"}}},
    )
    assert report["verifier_status"] == "PASS"
