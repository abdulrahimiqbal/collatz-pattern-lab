from collatz_lab.proof_action_frontier_generator import build_hard_frontier_dataset
from collatz_lab.proof_action_hard_trace_dataset import build_hard_trace_dataset
from collatz_lab.proof_action_trace_miner import mine_hard_traces


def test_hard_trace_dataset_has_policy_value_and_pairs(tmp_path):
    frontier = tmp_path / "frontier"
    traces = tmp_path / "traces"
    build_hard_frontier_dataset(out=frontier, max_frontier_states=24, train_rows=tmp_path / "missing.jsonl")
    mine_hard_traces(config=None, frontier_dir=frontier, checkpoint=None, out=traces, max_traces=12)
    summary = build_hard_trace_dataset(traces=traces / "mined_hard_traces.jsonl", out=traces)
    assert summary["train_policy_rows"] > 0
    assert summary["train_value_rows"] >= summary["train_policy_rows"]
    assert summary["train_pair_rows"] > 0
    assert summary["challenge_holdout_rows"] > 0
