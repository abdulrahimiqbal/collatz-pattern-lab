from collatz_lab.proof_actions import ProofAction
from collatz_lab.proof_graph import apply_trace_to_graph, build_graph_from_obligations, graph_summary
from collatz_lab.proof_trace import ProofActionResult, ProofTrace


def test_reduced_action_does_not_close_parent() -> None:
    graph = build_graph_from_obligations(
        {
            "obligations": [
                {
                    "obligation_id": "parent",
                    "scc_status": "NEEDS_SPLIT",
                    "scope": "synthetic",
                }
            ]
        }
    )
    trace = ProofTrace(
        obligation_id="parent",
        obligation_before={"obligation_id": "parent", "scc_status": "NEEDS_SPLIT"},
        action=ProofAction("SPLIT_BY_RESIDUE"),
        result=ProofActionResult(
            status="REDUCED",
            reward=1,
            proof_status="REDUCED_BY_RESIDUE_SPLIT",
            details={"children": [{"obligation_id": "child", "status": "NEEDS_SPLIT"}]},
        ),
    )
    apply_trace_to_graph(graph, trace)
    assert graph["nodes"]["parent"]["status"] == "NEEDS_SPLIT"
    assert "child" in graph["nodes"]
    assert graph_summary(graph)["open_count"] == 2


def test_parent_closes_after_all_children_close() -> None:
    graph = build_graph_from_obligations(
        {
            "obligations": [
                {
                    "obligation_id": "parent",
                    "scc_status": "NEEDS_SPLIT",
                    "scope": "synthetic",
                }
            ]
        }
    )
    apply_trace_to_graph(
        graph,
        ProofTrace(
            obligation_id="parent",
            obligation_before={"obligation_id": "parent", "scc_status": "NEEDS_SPLIT"},
            action=ProofAction("SPLIT_BY_RESIDUE"),
            result=ProofActionResult(
                status="REDUCED",
                reward=1,
                proof_status="REDUCED_BY_RESIDUE_SPLIT",
                details={"children": [{"obligation_id": "child", "status": "NEEDS_SPLIT"}]},
            ),
        ),
    )
    apply_trace_to_graph(
        graph,
        ProofTrace(
            obligation_id="child",
            obligation_before={"obligation_id": "child", "scc_status": "NEEDS_SPLIT"},
            action=ProofAction("TRY_ADIC_BASIN"),
            result=ProofActionResult(
                status="CLOSED",
                reward=80,
                proof_status="CLOSED_BY_HEIGHT_RANKING",
                message="synthetic close",
            ),
        ),
    )
    assert graph["nodes"]["child"]["status"] == "CLOSED_BY_HEIGHT_RANKING"
    assert graph["nodes"]["parent"]["status"] == "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"
    assert graph["status"] == "PASS"
