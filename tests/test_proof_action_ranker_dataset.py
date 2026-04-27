import json

from collatz_lab.proof_action_dataset import build_arg_parser, build_dataset


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_ranker_dataset_writes_outcomes_and_pairs(tmp_path) -> None:
    args = build_arg_parser().parse_args(
        [
            "build",
            "--out",
            str(tmp_path),
            "--max-n",
            "100",
            "--residue-k-min",
            "4",
            "--residue-k-max",
            "6",
            "--negatives-per-positive",
            "2",
            "--pairwise-ranker-examples",
            "true",
            "--stratified-splits",
            "true",
            "--seed",
            "1337",
        ]
    )
    report = build_dataset(args)
    rows = _read_jsonl(tmp_path / "rows.jsonl")
    pairs = _read_jsonl(tmp_path / "train_pairs.jsonl")

    assert report["train_pair_rows"] > 0
    assert pairs
    assert {"outcome_class", "closure_reward", "net_goal_delta", "gate_progress_delta"} <= set(rows[0])
    assert {"state", "better_action", "worse_action", "reason"} <= set(pairs[0])
    assert (tmp_path / "val_stratified.jsonl").exists()
    assert (tmp_path / "challenge_s3_s4.jsonl").exists()
