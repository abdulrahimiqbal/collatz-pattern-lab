import json

from collatz_lab.proof_action_dataset import residue_descent_rows
from collatz_lab.proof_action_hard_mix_dataset import build_hard_mix_dataset
from collatz_lab.proof_action_hard_trace_dataset import build_hard_trace_dataset
from collatz_lab.proof_action_s6_analyzer import analyze_s6_blockers
from collatz_lab.proof_action_s6_lemma_generator import generate_s6_candidate_lemmas
from collatz_lab.proof_action_trace_miner import mine_hard_traces
from collatz_lab.proof_action_frontier_generator import build_hard_frontier_dataset


def test_hard_mix_dataset_excludes_hard_holdout_from_train(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    rows = residue_descent_rows(k_min=4, k_max=4, max_examples=4, seed=1337, split="train")
    (original / "train.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    (original / "val.jsonl").write_text("")
    (original / "test.jsonl").write_text("")

    ranker = tmp_path / "ranker"
    ranker.mkdir()
    (ranker / "train_value.jsonl").write_text((original / "train.jsonl").read_text())
    pair = {
        "state": rows[0]["state"],
        "better_action": rows[0]["target_action_text"],
        "worse_action": rows[1]["target_action_text"],
        "split": "train",
        "reason": "accepted_vs_rejected",
    }
    (ranker / "train_pairs.jsonl").write_text(json.dumps(pair) + "\n")

    frontier = tmp_path / "frontier"
    hard = tmp_path / "hard"
    build_hard_frontier_dataset(out=frontier, max_frontier_states=24, train_rows=tmp_path / "missing.jsonl")
    mine_hard_traces(config=None, frontier_dir=frontier, checkpoint=None, out=hard, max_traces=8)
    build_hard_trace_dataset(traces=hard / "mined_hard_traces.jsonl", out=hard)

    s6 = tmp_path / "s6"
    analyze_s6_blockers(out=s6, sources=[], min_blockers=10)
    generate_s6_candidate_lemmas(blockers_path=s6 / "s6_blockers.jsonl", out=s6 / "s6_candidate_lemmas.jsonl", min_lemmas=10)

    out = tmp_path / "mix"
    summary = build_hard_mix_dataset(
        original_dir=original,
        ranker_dir=ranker,
        hard_trace_dir=hard,
        s6_dir=s6,
        frontier_dir=frontier,
        out=out,
        frontier_gate_progress_weight=3.0,
    )

    assert summary["train_policy_rows"] > 0
    assert summary["train_pair_rows"] > 0
    assert summary["s6_challenge_holdout_rows"] > 0
    assert summary["leakage"]["exact_state_hash_overlap"] == 0
    assert "s6_lemma" in summary["source_counts_policy"]
    assert summary["frontier_gate_progress_policy_rows"] > 0
    assert summary["frontier_gate_progress_pair_rows"] > 0
    assert "frontier_gate_progress" in summary["source_counts_policy"]
