from collatz_lab.proof_action_frontier_generator import build_hard_frontier_dataset
from collatz_lab.proof_action_trace_miner import mine_hard_traces


def test_trace_miner_saves_only_verified_hard_traces(tmp_path):
    frontier = tmp_path / "frontier"
    traces = tmp_path / "traces"
    build_hard_frontier_dataset(out=frontier, max_frontier_states=24, s3=True, s4=True, s6=True, train_rows=tmp_path / "missing.jsonl")
    report = mine_hard_traces(config=None, frontier_dir=frontier, checkpoint=None, out=traces, max_traces=12)
    assert report["mined_hard_traces_count"] > 0
    import json

    rows = [json.loads(line) for line in (traces / "mined_hard_traces.jsonl").read_text().splitlines() if line.strip()]
    assert rows
    assert all(step["verifier_status"] == "ACCEPT" for row in rows for step in row["actions"])
    assert all(row["hard_filter"]["accepted"] for row in rows)
