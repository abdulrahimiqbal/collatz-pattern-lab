import json

from collatz_lab.run_pipeline import RUN001_ID, build_a10g_dry_run, write_proof_attempt_bundle
from collatz_lab.train import make_run_dir


def test_a10g_dry_run_builds_stable_artifact_paths() -> None:
    result = build_a10g_dry_run()
    assert result.run_id == RUN001_ID
    assert result.checkpoint_path == f"/mnt/collatz/runs/{RUN001_ID}/checkpoint.pt"
    assert any("--run-name RUN-001-a10g-reference" in command for command in result.commands)
    assert result.discovery_metrics["planned"] is True


def test_make_run_dir_accepts_explicit_run_name(tmp_path) -> None:
    run_dir = make_run_dir({"run_root": str(tmp_path), "run_name": "stable-run", "task": "x", "base": 2})
    assert run_dir == tmp_path / "stable-run"
    assert run_dir.exists()
    latest = tmp_path / "latest"
    if latest.exists():
        assert latest.resolve() == run_dir


def test_write_proof_attempt_bundle_creates_run_proof_artifacts(tmp_path) -> None:
    theorem = tmp_path / "theorem.json"
    theorem.write_text(json.dumps({"verifier_status": "FAIL", "verification": {"errors": ["open"]}}), encoding="utf-8")
    progress = tmp_path / "progress.json"
    progress.write_text(json.dumps({"proof_progress_percent": 25.0}), encoding="utf-8")
    obligations = tmp_path / "obligations.json"
    obligations.write_text(
        json.dumps(
            {
                "obligations": [
                    {"obligation_id": "even_descent", "status": "CLOSED_BY_ANCESTOR_DESCENT"},
                    {"obligation_id": "odd_parent_state_cover", "status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"},
                ]
            }
        ),
        encoding="utf-8",
    )
    attempt_path = tmp_path / "run" / "proof_attempt.json"
    evaluation_path = tmp_path / "run" / "proof_evaluation.json"
    central_log_path = tmp_path / "proof_attempts.jsonl"

    write_proof_attempt_bundle(
        run_id="RUN-T",
        theorem_candidate_path=theorem,
        progress_report_path=progress,
        global_obligations_path=obligations,
        debt_induction_path=None,
        proof_attempt_path=attempt_path,
        proof_evaluation_path=evaluation_path,
        central_proof_attempts_log_path=central_log_path,
        proof_attempt_beam_size=3,
    )
    write_proof_attempt_bundle(
        run_id="RUN-T",
        theorem_candidate_path=theorem,
        progress_report_path=progress,
        global_obligations_path=obligations,
        debt_induction_path=None,
        proof_attempt_path=attempt_path,
        proof_evaluation_path=evaluation_path,
        central_proof_attempts_log_path=central_log_path,
        proof_attempt_beam_size=3,
    )

    attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    assert attempt["schema"] == "collatz_lab.proof_attempt"
    assert attempt["proof_dsl"]["schema"] == "collatz_lab.proof_dsl"
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    assert evaluation["schema"] == "collatz_lab.proof_attempt_evaluation"
    assert evaluation["proof_confidence_percent"] == 0.0
    assert (tmp_path / "run" / "proof_attempt.md").exists()
    assert (tmp_path / "run" / "proof_evaluation.md").exists()
    assert (tmp_path / "run" / "proof_attempt_search.json").exists()
    per_run_records = (tmp_path / "run" / "proof_attempts.jsonl").read_text(encoding="utf-8").splitlines()
    central_records = central_log_path.read_text(encoding="utf-8").splitlines()
    assert len(per_run_records) == 3
    assert len(central_records) == 3
    record = json.loads(per_run_records[0])
    assert record["schema"] == "collatz_lab.proof_attempt_record"
    assert record["proof_evaluation"]["proof_confidence_percent"] == 0.0
    assert record["proof_critic"]["schema"] == "collatz_lab.proof_critic"
    assert record["proof_search"]["selected"] is True
