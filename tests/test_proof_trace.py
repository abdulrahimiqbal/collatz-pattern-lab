from pathlib import Path

from collatz_lab.proof_actions import ProofAction
from collatz_lab.proof_trace import ProofActionResult, ProofTrace, load_traces, write_traces


def test_proof_trace_jsonl_round_trip(tmp_path: Path) -> None:
    trace = ProofTrace(
        obligation_id="o1",
        obligation_before={"obligation_id": "o1", "scc_status": "NEEDS_SPLIT"},
        action=ProofAction("SPLIT_BY_H", {"a": 6}, 0.7, "split h"),
        result=ProofActionResult("NEEDS_SPLIT", 12, "NEEDS_SPLIT", "ok"),
    )
    out = tmp_path / "trace.jsonl"
    write_traces(out, [trace])
    loaded = load_traces(out)
    assert len(loaded) == 1
    assert loaded[0].obligation_id == "o1"
    assert loaded[0].action.action == "SPLIT_BY_H"
    assert loaded[0].result.reward == 12
