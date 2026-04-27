from collatz_lab.obligation_search import compare_graphs, merge_obligation_reports


def test_merge_obligation_reports_accepts_status_field() -> None:
    report = {
        "obligations": [
            {"obligation_id": "closed", "status": "CLOSED_BY_ANCESTOR_DESCENT"},
            {"obligation_id": "open", "status": "UNKNOWN"},
        ]
    }

    merged = merge_obligation_reports([report])

    assert merged["obligation_count"] == 2
    assert merged["open_obligation_count"] == 1
    assert merged["obligations"][1]["scc_status"] == "UNKNOWN"


def test_compare_graphs_counts_only_existing_open_closures() -> None:
    baseline = {
        "nodes": {
            "a": {"status": "NEEDS_SPLIT"},
            "b": {"status": "CLOSED_BY_HEIGHT_RANKING"},
        },
        "actions": [],
        "closed": ["b"],
        "open": ["a"],
    }
    candidate = {
        "nodes": {
            "a": {"status": "CLOSED_BY_HEIGHT_RANKING"},
            "b": {"status": "CLOSED_BY_HEIGHT_RANKING"},
            "new": {"status": "CLOSED_BY_HEIGHT_RANKING"},
        },
        "actions": [],
        "closed": ["a", "b", "new"],
        "open": [],
    }

    comparison = compare_graphs(baseline, candidate)

    assert comparison["newly_closed_existing_obligations"] == ["a"]
    assert comparison["new_closed_nodes"] == 1
