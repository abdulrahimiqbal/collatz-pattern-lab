import json

from collatz_lab.run_result import (
    ProofScore,
    RunResult,
    append_run_to_runs_md,
    build_proof_score,
    load_run_result,
    save_run_result,
    summarize_verification_results,
)


def _sample_result(run_id: str = "RUN-X") -> RunResult:
    return RunResult(
        run_id=run_id,
        title="Synthetic run",
        created_at="2026-04-25T00:00:00Z",
        config_path="configs/example.yaml",
        checkpoint_path="/mnt/collatz/runs/example/checkpoint.pt",
        commands=["echo run"],
        artifacts={"report": "reports/example.json"},
        eval_metrics={"ood": {"hybrid_v2_syracuse_accuracy": 1.0}},
        discovery_metrics={},
        verification_metrics={},
        postprocess_metrics={},
        proof_graph_summary={"node_count": 2, "closed_count": 1},
        theorem_verifier_status="FAIL",
        score=ProofScore(
            verifier_status="FAIL",
            proof_confidence_percent=0.0,
            proof_progress_percent=50.0,
            model_discovery_score_percent=10.0,
            blocking_obligations=["open"],
        ),
        next_step_recommendation="Keep testing.",
    )


def test_proof_confidence_is_verifier_gated() -> None:
    score = build_proof_score(
        theorem_candidate={"verifier_status": "FAIL", "minimal_blocking_set": [{"obligation_id": "open"}]},
        proof_graph={"summary": {"node_count": 10, "closed_count": 5, "open_count": 5}},
        eval_metrics={"ood": {"hybrid_v2_syracuse_accuracy": 1.0, "exact_sequence_accuracy": 1.0}},
        verification_metrics={"rules": {"exact_pass_rate": 1.0}},
        postprocess_metrics={"raw_leaf_count": 10, "merged_leaf_count": 10},
        proof_policy_report={"useful_action_rate": 1.0},
    )
    assert score.proof_confidence_percent == 0.0
    assert score.proof_progress_percent == 50.0
    assert score.model_discovery_score_percent > 0.0
    assert score.blocking_obligations == ["open"]

    passing = build_proof_score({"verifier_status": "PASS"}, {"summary": {"node_count": 1, "closed_count": 1}})
    assert passing.proof_confidence_percent == 100.0


def test_weighted_progress_report_can_override_graph_progress() -> None:
    score = build_proof_score(
        theorem_candidate={"verifier_status": "FAIL"},
        proof_graph={"summary": {"node_count": 10, "closed_count": 1, "open_count": 9}},
        proof_policy_report={"proof_progress_percent": 40.13671875},
    )

    assert score.proof_confidence_percent == 0.0
    assert score.proof_progress_percent == 40.13671875


def test_proof_attempt_evaluation_overrides_progress_report() -> None:
    score = build_proof_score(
        theorem_candidate={"verifier_status": "FAIL"},
        proof_graph={"summary": {"node_count": 10, "closed_count": 1, "open_count": 9}},
        proof_policy_report={"proof_progress_percent": 40.13671875},
        proof_attempt_evaluation={
            "proof_progress_percent": 26.0546875,
            "blocking_steps": ["S3-global-parent-transitions"],
        },
    )

    assert score.proof_confidence_percent == 0.0
    assert score.proof_progress_percent == 26.0546875
    assert "S3-global-parent-transitions" in score.blocking_obligations


def test_run_result_schema_round_trips(tmp_path) -> None:
    path = tmp_path / "run_result.json"
    result = _sample_result()
    save_run_result(result, path)
    loaded = load_run_result(path)
    assert loaded.to_dict() == result.to_dict()
    assert json.loads(path.read_text(encoding="utf-8"))["schema"] == "collatz_lab.run_result"


def test_runs_markdown_append_preserves_existing_runs(tmp_path) -> None:
    runs_md = tmp_path / "runs.md"
    runs_md.write_text(
        "\n".join(
            [
                "# Collatz Proof-Discovery Runs",
                "",
                "| Run | Title | Verifier | Proof Confidence | Proof Progress | Discovery Score | Next Step |",
                "| --- | --- | --- | ---: | ---: | ---: | --- |",
                "| OLD | Old run | FAIL | 0.00% | 1.00% | 2.00% | old next |",
                "",
                "## Run Details",
                "",
                "Existing details stay here.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    append_run_to_runs_md(_sample_result("RUN-NEW"), runs_md)
    append_run_to_runs_md(_sample_result("RUN-NEW"), runs_md)
    text = runs_md.read_text(encoding="utf-8")
    assert "| OLD | Old run |" in text
    assert text.count("RUN-NEW") == 2  # one table row and one detail heading
    assert "Existing details stay here." in text


def test_verification_summary_counts_exact_statuses() -> None:
    summary = summarize_verification_results(
        [
            {"exact": {"status": "PASS"}, "sampling": {"status": "UNKNOWN_NEEDS_SYMBOLIC_CHECK"}},
            {"exact": {"status": "FAIL_WITH_COUNTEREXAMPLE"}, "sampling": {"status": "FAIL_WITH_COUNTEREXAMPLE"}},
            {"exact": {"status": "UNKNOWN_NEEDS_LARGER_MODULUS"}, "sampling": {"status": "UNKNOWN_NEEDS_SYMBOLIC_CHECK"}},
        ]
    )
    assert summary["total"] == 3
    assert summary["exact_pass_count"] == 1
    assert summary["exact_fail_count"] == 1
    assert summary["exact_unknown_count"] == 1
    assert summary["exact_pass_rate"] == 1 / 3
