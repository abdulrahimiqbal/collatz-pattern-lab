from collatz_lab.proof_actions import ProofAction
from collatz_lab.proof_policy_model import rerank_actions_with_value_model, train_policy_from_traces
from collatz_lab.proof_trace import ProofActionResult, ProofTrace


def test_train_policy_from_traces() -> None:
    traces = [
        ProofTrace(
            "o1",
            {"obligation_id": "cube_lift:unknown:NEEDS_SPLIT", "scc_status": "NEEDS_SPLIT"},
            ProofAction("SPLIT_BY_H"),
            ProofActionResult("NEEDS_SPLIT", 12, "NEEDS_SPLIT"),
        ),
        ProofTrace(
            "o2",
            {"obligation_id": "unresolved_bucket:t=0:a=6:h=1", "scc_status": "NEEDS_SPLIT"},
            ProofAction("TRY_ADIC_BASIN"),
            ProofActionResult("REDUCED", 55, "REDUCED_BY_HEIGHT_RANKED_SUBBRANCH"),
        ),
        ProofTrace(
            "o3",
            {"obligation_id": "unresolved_bucket:t=1:a=7:h=1", "scc_status": "NEEDS_SPLIT"},
            ProofAction("PROMOTE_TO_PARENT_STATE"),
            ProofActionResult("REDUCED", 40, "REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION"),
        ),
        ProofTrace(
            "o4",
            {"obligation_id": "cube_lift:k19:NEEDS_SPLIT", "scc_status": "NEEDS_SPLIT"},
            ProofAction("SPLIT_BY_H"),
            ProofActionResult("NEEDS_SPLIT", 12, "NEEDS_SPLIT"),
        ),
    ]
    report = train_policy_from_traces(traces)
    assert report["status"] == "TRAINED_PROOF_POLICY_BASELINE"
    assert report["trace_count"] == 4
    assert "value_model" in report


def test_value_model_reranks_actions() -> None:
    traces = [
        ProofTrace(
            "o1",
            {"obligation_id": "unresolved_bucket:t=0:a=6:h=1", "scc_status": "NEEDS_SPLIT"},
            ProofAction("RUN_FALSIFIER"),
            ProofActionResult("REDUCED", 1, "REDUCED_BY_FALSIFIER_CHECK"),
        ),
        ProofTrace(
            "o2",
            {"obligation_id": "unresolved_bucket:t=0:a=6:h=1", "scc_status": "NEEDS_SPLIT"},
            ProofAction("TRY_ADIC_BASIN"),
            ProofActionResult("REDUCED", 80, "REDUCED_BY_HEIGHT_RANKED_SUBBRANCH"),
        ),
        ProofTrace(
            "o3",
            {"obligation_id": "unresolved_bucket:t=1:a=7:h=1", "scc_status": "NEEDS_SPLIT"},
            ProofAction("PROMOTE_TO_PARENT_STATE"),
            ProofActionResult("REDUCED", 40, "REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION"),
        ),
        ProofTrace(
            "o4",
            {"obligation_id": "cube_lift:k19:NEEDS_SPLIT", "scc_status": "NEEDS_SPLIT"},
            ProofAction("SPLIT_BY_H"),
            ProofActionResult("NEEDS_SPLIT", 12, "NEEDS_SPLIT"),
        ),
    ]
    bundle = train_policy_from_traces(traces)
    ranked = rerank_actions_with_value_model(
        bundle,
        {"obligation_id": "unresolved_bucket:t=0:a=6:h=1", "scc_status": "NEEDS_SPLIT"},
        [ProofAction("RUN_FALSIFIER"), ProofAction("TRY_ADIC_BASIN")],
    )
    assert ranked[0].score >= ranked[1].score
