from collatz_lab.proof_action_leakage import leakage_report
from collatz_lab.proof_action_state import state_from_residue_task


def test_leakage_detects_exact_state_overlap() -> None:
    state = state_from_residue_task(modulus=16, residue=5, steps=4, parity_word="1000")
    train = [{"state": state, "target_action_text": "A"}]
    eval_rows = [{"state": state, "candidates": [{"action": "A"}]}]

    report = leakage_report(train_rows=train, eval_rows=eval_rows)

    assert report["exact_state_hash_overlap"] == 1
    assert not report["challenge_state_overlap_ok"]


def test_leakage_allows_distinct_challenge_state() -> None:
    train_state = state_from_residue_task(modulus=16, residue=5, steps=4, parity_word="1000")
    eval_state = state_from_residue_task(modulus=32, residue=13, steps=5, parity_word="10000")

    report = leakage_report(train_rows=[{"state": train_state}], eval_rows=[{"state": eval_state}])

    assert report["exact_state_hash_overlap"] == 0
    assert report["challenge_state_overlap_ok"]
