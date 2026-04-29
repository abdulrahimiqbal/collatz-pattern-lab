from pathlib import Path

from collatz_lab.proof_action_run071 import run_deepseek_prover_prep


def test_run071_prepares_manual_deepseek_bank(tmp_path: Path) -> None:
    result = run_deepseek_prover_prep(out=tmp_path / "run071")

    assert result["status"] == "MANUAL_DEEPSEEK_REQUIRED"
    assert result["global_proof_claimed"] is False
    assert result["remaining_high_parent_gap"] == "odd_entry_parent_levels_ge_33"
    assert result["accepted_candidate_count"] == 0
    assert result["harvested_theorem_count"] == 0
    assert result["task_count"] >= 23
    assert (tmp_path / "run071" / "run_result.json").exists()
    assert (tmp_path / "run071" / "deepseek_tasks.jsonl").exists()
