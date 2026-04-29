from pathlib import Path

from collatz_lab.deepseek_goal_bank import build_goal_specs, generate_goal_bank, task_rows


def test_goal_bank_contains_required_targets(tmp_path: Path) -> None:
    result = generate_goal_bank(out=tmp_path / "run071")
    rows = task_rows()
    task_ids = {row["task_id"] for row in rows}

    assert result["status"] == "GOAL_BANK_READY"
    assert result["task_count"] >= 23
    assert "high_parent_d1" in task_ids
    assert "p32_special_root_relative_general" in task_ids
    assert "low_parent_b8_margin" in task_ids
    assert (tmp_path / "run071" / "deepseek_tasks.jsonl").exists()


def test_goal_specs_are_one_theorem_per_task() -> None:
    specs = build_goal_specs()

    assert len({spec.task_id for spec in specs}) == len(specs)
    assert all(spec.target_theorem for spec in specs)
    assert all(spec.target_statement.count("theorem ") == 1 for spec in specs)
    assert all("lake env lean <candidate-file>" in row["success_condition"] for row in task_rows())
