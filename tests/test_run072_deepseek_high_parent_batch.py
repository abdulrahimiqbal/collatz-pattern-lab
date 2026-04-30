from pathlib import Path

from collatz_lab.deepseek_batch_campaign import (
    DeepSeekRequest,
    build_run072_tasks,
    refresh_run072_task_bank,
    run_deepseek_batch_campaign,
    verify_run072_candidate,
)
from collatz_lab.deepseek_feedback_retry import build_feedback_retry_prompt
from collatz_lab.high_parent_theorem_synthesizer import synthesize_high_parent_patterns


def test_run072_task_bank_contains_required_priorities(tmp_path: Path) -> None:
    result = refresh_run072_task_bank(tmp_path / "run072")
    rows = (tmp_path / "run072" / "deepseek_tasks.jsonl").read_text(encoding="utf-8")

    assert result["task_count"] >= 23
    assert "p32_special_root_relative_d1" in rows
    assert "low_parent_b8_margin" in rows
    assert "high_parent_root_relative_descent" in rows


def test_feedback_retry_prompt_includes_candidate_and_error() -> None:
    task = {
        "target_statement": "theorem high_parent_d1 (q : Nat) : True := by\n  ...",
    }
    prompt = build_feedback_retry_prompt(
        task=task,
        previous_candidate="theorem high_parent_d1 (q : Nat) : True := by\n  trivial",
        verification_result={"failures": ["LEAN_CHECK_FAILED"], "lean": {"stdout": "unknown tactic", "stderr": ""}},
        retry_index=1,
    )

    assert "Fix only the proof body" in prompt
    assert "unknown tactic" in prompt
    assert "high_parent_d1" in prompt


def test_batch_campaign_with_fake_client_records_rejected_symbolic_task(tmp_path: Path) -> None:
    def fake_client(_request: DeepSeekRequest) -> dict[str, object]:
        return {
            "text": (
                "```lean4\n"
                "import Collatz.HighParentRootRelative\n\n"
                "namespace Collatz\n\n"
                "theorem high_parent_d1\n"
                "  (q : Nat)\n"
                "  (hq : q > 0)\n"
                "  (hodd : q % 2 = 1) :\n"
                "  eventually_descends (2^33 * q - 1) := by\n"
                "  exact False.elim (by contradiction)\n\n"
                "end Collatz\n"
                "```"
            ),
            "input_tokens": 1,
            "output_tokens": 10,
            "elapsed_seconds": 0.1,
        }

    result = run_deepseek_batch_campaign(
        endpoint=None,
        out_dir=tmp_path / "run072",
        task_ids=["high_parent_d1"],
        attempts_per_goal=1,
        feedback_retries_per_failed_task=0,
        max_new_tokens=64,
        lean_timeout_seconds=120,
        client=fake_client,
    )

    assert result["task_count"] == 1
    assert result["accepted_symbolic_count"] == 0
    assert (tmp_path / "run072" / "candidate_verification_results.jsonl").exists()


def test_blocked_rejected_candidate_copy_is_sanitized(tmp_path: Path) -> None:
    task = next(item for item in build_run072_tasks() if item.task_id == "high_parent_d1")
    row = {
        "task_id": task.task_id,
        "target_theorem": task.target_theorem,
        "target_statement": task.target_statement,
        "priority": task.priority,
        "proof_level": task.proof_level,
        "allowed_imports": list(task.allowed_imports),
    }
    task_bank = tmp_path / "tasks.jsonl"
    task_bank.write_text("", encoding="utf-8")
    candidate = tmp_path / "blocked_candidate.lean"
    candidate.write_text(
        "namespace Collatz\n\n"
        "/-\n"
        "sorry\n"
        "-/\n\n"
        "end Collatz\n",
        encoding="utf-8",
    )

    result = verify_run072_candidate(
        candidate,
        row,
        task_bank_path=task_bank,
        results_path=tmp_path / "results.jsonl",
        timeout_seconds=120,
        accepted_dir=tmp_path / "accepted",
        rejected_dir=tmp_path / "rejected",
    )

    rejected_copy = tmp_path / "rejected" / candidate.name
    assert result["status"] == "REJECTED"
    assert "BLOCKED_TERM_FOUND" in result["failures"]
    assert rejected_copy.exists()
    assert "sorry" not in rejected_copy.read_text(encoding="utf-8")


def test_pattern_synthesis_emits_generalization_task_for_d1_d2(tmp_path: Path) -> None:
    rows = [
        {"status": "ACCEPTED", "proof_level": "FIXED_D_SYMBOLIC", "target_theorem": "high_parent_d1"},
        {"status": "ACCEPTED", "proof_level": "FIXED_D_SYMBOLIC", "target_theorem": "high_parent_d2"},
    ]

    result = synthesize_high_parent_patterns(accepted_rows=rows, out_dir=tmp_path / "run072")

    assert result["generated_task_count"] == 1
    assert (tmp_path / "run072" / "pattern_synthesis_report.md").exists()
