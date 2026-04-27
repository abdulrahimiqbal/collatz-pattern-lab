import json

from collatz_lab.proof_action_dataset import build_tiny_dataset, build_arg_parser
from collatz_lab.proof_action_decode import verify_action_for_state


def test_build_tiny_dataset_has_accepted_replayable_actions(tmp_path) -> None:
    args = build_arg_parser().parse_args(["build-tiny", "--out", str(tmp_path), "--num-traces", "10", "--seed", "1337"])
    report = build_tiny_dataset(args)
    rows = [json.loads(line) for line in (tmp_path / "rows.jsonl").read_text(encoding="utf-8").splitlines()]

    assert report["row_count"] == 10
    assert report["verifier_status_counts"]["ACCEPT"] == 10
    for row in rows:
        check = verify_action_for_state(row["target_action"], row["state"])
        assert check.accepted


def test_tiny_dataset_writes_split_files(tmp_path) -> None:
    args = build_arg_parser().parse_args(["build-tiny", "--out", str(tmp_path), "--num-traces", "4"])
    build_tiny_dataset(args)

    assert (tmp_path / "rows.jsonl").exists()
    assert (tmp_path / "train.jsonl").exists()
    assert (tmp_path / "report.json").exists()
