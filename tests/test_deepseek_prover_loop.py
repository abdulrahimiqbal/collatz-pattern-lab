from pathlib import Path

from collatz_lab.deepseek_prover_loop import (
    DeepSeekRequest,
    build_generation_prompt,
    concrete_witness_candidate,
    extract_lean_blocks,
    materialize_candidate,
    run_deepseek_prover_loop,
)
from collatz_lab.utils import write_jsonl


def _trivial_task() -> dict[str, object]:
    return {
        "task_id": "fake_true_task",
        "lean_file": "formal/lean/DeepSeekGoals/FakeTrue.lean",
        "target_theorem": "run071_fake_target",
        "target_statement": "theorem run071_fake_target : True := by\n  ...",
        "difficulty": "example",
        "imports": ["Collatz.Core"],
        "known_lemmas": ["C", "iter"],
        "prompt": "Prove theorem run071_fake_target : True.",
        "success_condition": "lake env lean <candidate-file> passes with no blocked terms",
        "forbidden": ["sorry", "admit", "axiom"],
    }


def test_extracts_lean_code_blocks() -> None:
    text = """
Plan first.

```lean4
import Collatz.Core

namespace Collatz

theorem run071_fake_target : True := by
  trivial

end Collatz
```
"""

    blocks = extract_lean_blocks(text, target_theorem="run071_fake_target")

    assert len(blocks) == 1
    assert "theorem run071_fake_target" in blocks[0]


def test_materialize_wraps_snippet_in_collatz_namespace() -> None:
    candidate = materialize_candidate(
        "theorem run071_fake_target : True := by\n  trivial",
        _trivial_task(),
    )

    assert candidate.startswith("import Collatz.HighParentRootRelative")
    assert "namespace Collatz" in candidate
    assert "theorem run071_fake_target" in candidate
    assert candidate.rstrip().endswith("end Collatz")


def test_generation_prompt_contains_target_and_retry_feedback() -> None:
    prompt = build_generation_prompt(
        _trivial_task(),
        previous_failure={
            "failures": ["LEAN_CHECK_FAILED"],
            "lean": {"stdout": "", "stderr": "unknown identifier"},
        },
    )

    assert "run071_fake_target" in prompt
    assert "unknown identifier" in prompt
    assert "complete Lean 4 file" in prompt


def test_concrete_witness_candidate_uses_exact_native_decide_repair() -> None:
    row = _trivial_task()
    row["task_id"] = "goal_d1_q1"
    row["target_theorem"] = "goal_d1_q1"
    row["target_statement"] = "theorem goal_d1_q1 : eventually_descends (2^33 * 1 - 1) := by\n  ..."

    candidate = concrete_witness_candidate(row)

    assert candidate is not None
    assert "theorem goal_d1_q1" in candidate
    assert "Exists.intro 200" in candidate
    assert "native_decide" in candidate


def test_prover_loop_with_fake_client_accepts_lean_checked_candidate(tmp_path: Path) -> None:
    task_bank = tmp_path / "deepseek_tasks.jsonl"
    write_jsonl([_trivial_task()], task_bank)

    def fake_client(_request: DeepSeekRequest) -> dict[str, object]:
        return {
            "text": (
                "```lean4\n"
                "import Collatz.Core\n\n"
                "namespace Collatz\n\n"
                "theorem run071_fake_target : True := by\n"
                "  trivial\n\n"
                "end Collatz\n"
                "```\n"
            ),
            "input_tokens": 1,
            "output_tokens": 12,
            "elapsed_seconds": 0.1,
        }

    result = run_deepseek_prover_loop(
        endpoint=None,
        task_bank_path=task_bank,
        out_dir=tmp_path / "run071",
        attempts_per_goal=1,
        max_new_tokens=64,
        lean_timeout_seconds=120,
        client=fake_client,
    )

    assert result["accepted_candidate_count"] == 1
    assert result["attempt_count"] == 1
    assert (tmp_path / "run071" / "deepseek_generation_attempts.jsonl").exists()
    assert (tmp_path / "run071" / "candidate_verification_results.jsonl").exists()
