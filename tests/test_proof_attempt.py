from collatz_lab.proof_attempt import build_proof_attempt, evaluate_proof_attempt


def test_proof_attempt_progress_evaluates_steps_not_raw_graph() -> None:
    attempt = build_proof_attempt(
        run_id="RUN-T",
        theorem_candidate={
            "verifier_status": "FAIL",
            "verification": {"errors": ["unknown obligations remain"]},
            "unknown_obligations": [{}],
        },
        progress_report={
            "proof_progress_breakdown": {
                "selected": {
                    "metric": "weighted_p6_finite_frontier_coverage",
                    "numerator": 40,
                    "denominator": 100,
                    "percent": 40.0,
                    "status": "finite_depth_diagnostic_not_global_proof",
                }
            }
        },
        global_obligations={
            "obligations": [
                {"obligation_id": "even_descent", "status": "CLOSED_BY_ANCESTOR_DESCENT"},
                {"obligation_id": "odd_parent_state_cover", "status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"},
                {"obligation_id": "parent_state_transition_templates", "status": "UNKNOWN"},
                {"obligation_id": "parametric_a_templates", "status": "NEEDS_SPLIT"},
            ]
        },
    )

    evaluation = evaluate_proof_attempt(attempt)

    assert evaluation["proof_confidence_percent"] == 0.0
    assert evaluation["proof_progress_metric"] == "evaluated_proof_attempt_weighted_gate_score"
    assert evaluation["proof_progress_percent"] == 26.0
    assert "S3-global-parent-transitions" in evaluation["blocking_steps"]


def test_passing_theorem_forces_full_progress_and_confidence() -> None:
    attempt = build_proof_attempt(
        run_id="RUN-PASS",
        theorem_candidate={"verifier_status": "PASS", "verification": {"errors": []}},
        progress_report={"proof_progress_percent": 0.0},
        global_obligations={
            "obligations": [
                {"obligation_id": "even_descent", "status": "CLOSED_BY_ANCESTOR_DESCENT"},
                {"obligation_id": "odd_parent_state_cover", "status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"},
            ]
        },
    )

    evaluation = evaluate_proof_attempt(attempt)

    assert evaluation["status"] == "PASS"
    assert evaluation["proof_confidence_percent"] == 100.0
    assert evaluation["proof_progress_percent"] == 100.0
