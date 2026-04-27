from collatz_lab.proof_attempt_search import build_ranked_proof_attempts, critique_proof_attempt


def _fixtures():
    return {
        "theorem_candidate": {
            "verifier_status": "FAIL",
            "verification": {"errors": ["unknown obligations remain"]},
            "unknown_obligations": [{}],
        },
        "progress_report": {"proof_progress_percent": 40.0},
        "global_obligations": {
            "obligations": [
                {"obligation_id": "even_descent", "status": "CLOSED_BY_ANCESTOR_DESCENT"},
                {"obligation_id": "odd_parent_state_cover", "status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"},
                {"obligation_id": "parent_state_transition_templates", "status": "UNKNOWN"},
                {"obligation_id": "parametric_a_templates", "status": "NEEDS_SPLIT"},
            ]
        },
    }


def test_ranked_proof_attempts_have_typed_dsl_and_critic() -> None:
    fixtures = _fixtures()
    ranked = build_ranked_proof_attempts(run_id="RUN-S", max_attempts=4, **fixtures)

    assert len(ranked) == 4
    assert ranked[0]["selected"] is True
    assert ranked[0]["attempt"]["proof_dsl"]["schema"] == "collatz_lab.proof_dsl"
    assert ranked[0]["evaluation"]["proof_confidence_percent"] == 0.0
    assert ranked[0]["critic"]["status"] == "REJECTED_BY_CRITIC"
    assert "S3-global-parent-transitions" in ranked[0]["evaluation"]["blocking_steps"]


def test_proof_critic_rejects_untyped_attempts() -> None:
    critic = critique_proof_attempt(
        {
            "run_id": "RUN-BAD",
            "source_status": {"theorem_verifier_status": "FAIL"},
            "steps": [],
        }
    )

    assert critic["status"] == "REJECTED_BY_CRITIC"
    assert any(issue["code"] == "missing_typed_proof_dsl" for issue in critic["issues"])
