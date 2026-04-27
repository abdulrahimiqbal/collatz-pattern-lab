from collatz_lab.weighted_progress import (
    build_weighted_progress_report,
    canonical_graph_summary,
    canonical_obligation_id,
)


def test_canonical_obligation_id_strips_duplicate_suffix() -> None:
    assert canonical_obligation_id("P6:h=1:to=P1:rdepth=7#3") == "P6:h=1:to=P1:rdepth=7"
    assert canonical_obligation_id("unresolved_bucket:t=0:a=6:h=1") == "unresolved_bucket:t=0:a=6:h=1"


def test_canonical_graph_summary_groups_duplicates() -> None:
    graph = {
        "nodes": {
            "a": {"status": "CLOSED_BY_HEIGHT_RANKING"},
            "b": {"status": "NEEDS_SPLIT"},
            "b#2": {"status": "NEEDS_SPLIT"},
        }
    }

    summary = canonical_graph_summary(graph)

    assert summary["canonical_node_count"] == 2
    assert summary["canonical_closed_count"] == 1
    assert summary["canonical_open_count"] == 1
    assert summary["duplicate_group_count"] == 1


def test_weighted_progress_report_uses_q_class_denominator() -> None:
    residual = {
        "total_q_classes": 100,
        "total_certified_q_classes": 40,
        "residual_unknown_q_classes": 60,
    }
    strata = {
        "top_unresolved_buckets": [
            {"t": 0, "a": 6, "h": 1, "count_unknown": 15},
            {"t": 1, "a": 7, "h": 1, "count_unknown": 10},
        ]
    }
    graph = {
        "summary": {"node_count": 4, "closed_count": 1},
        "nodes": {
            "closed": {"status": "CLOSED_BY_HEIGHT_RANKING"},
            "open": {"status": "NEEDS_SPLIT"},
        },
    }

    report = build_weighted_progress_report(
        residual,
        strata,
        graph,
        residual_source="residual.json",
        strata_source="strata.json",
        graph_source="graph.json",
        top_n=2,
    )

    assert report["proof_progress_percent"] == 40.0
    assert report["target_buckets"][0]["cumulative_progress_if_closed_percent"] == 55.0
    assert report["target_buckets"][1]["cumulative_progress_if_closed_percent"] == 65.0
    assert report["proof_progress_breakdown"]["strict_graph"]["percent"] == 25.0
