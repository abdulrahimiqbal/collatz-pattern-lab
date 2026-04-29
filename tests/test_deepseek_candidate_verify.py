from pathlib import Path

from collatz_lab.deepseek_candidate_verify import verify_candidate


def test_candidate_verifier_accepts_lean_checked_target(tmp_path: Path) -> None:
    candidate = tmp_path / "Run071TrivialCandidate.lean"
    candidate.write_text(
        "import Collatz.Core\n\n"
        "namespace Collatz\n\n"
        "theorem run071_trivial_target : True := by\n"
        "  trivial\n\n"
        "end Collatz\n",
        encoding="utf-8",
    )
    results_path = tmp_path / "results.jsonl"

    result = verify_candidate(
        candidate,
        target_theorem="run071_trivial_target",
        expected_statement="theorem run071_trivial_target : True := by\n  ...",
        results_path=results_path,
    )

    assert result["status"] == "ACCEPTED"
    assert result["lean"]["passed"] is True
    assert result["target_theorem_exists"] is True
    assert results_path.exists()


def test_candidate_verifier_rejects_blocked_terms_without_running_lean(tmp_path: Path) -> None:
    candidate = tmp_path / "Run071BlockedCandidate.lean"
    blocked = "so" + "rry"
    candidate.write_text(
        "import Collatz.Core\n\n"
        "namespace Collatz\n\n"
        f"theorem run071_bad_target : True := by\n  {blocked}\n\n"
        "end Collatz\n",
        encoding="utf-8",
    )

    result = verify_candidate(
        candidate,
        target_theorem="run071_bad_target",
        expected_statement="theorem run071_bad_target : True := by\n  ...",
        run_lean=False,
        write_result=False,
    )

    assert result["status"] == "REJECTED"
    assert "BLOCKED_TERM_FOUND" in result["failures"]
