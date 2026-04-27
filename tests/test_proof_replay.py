from collatz_lab.proof_replay import build_replay_examples, summarize_replay_examples


def test_replay_example_targets_first_blocker_repair() -> None:
    examples = build_replay_examples(
        [
            {
                "attempt_id": "a1",
                "run_id": "RUN-X",
                "verifier_status": "FAIL",
                "proof_confidence_percent": 0.0,
                "proof_progress_percent": 26.0,
                "blocking_steps": ["S3-global-parent-transitions", "S4-parametric-lifting"],
                "next_step": "Prove exact global parent-state transition templates.",
                "proof_search": {"variant": {"variant_id": "global-template-first"}},
                "proof_attempt": {
                    "theorem": "forall n > 1 exists k >= 1 such that C^k(n) < n",
                    "proof_text": "Attempt",
                    "proof_dsl": {"schema": "collatz_lab.proof_dsl"},
                },
                "proof_evaluation": {"step_results": []},
                "proof_critic": {"issues": [{"code": "local_to_global_gap"}]},
            }
        ]
    )

    assert examples[0]["schema"] == "collatz_lab.proof_replay_example"
    assert examples[0]["target"]["first_blocker"] == "S3-global-parent-transitions"
    assert examples[0]["target"]["repair_action"] == "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE"
    assert examples[0]["target"]["must_not_claim_proof"] is True


def test_replay_summary_counts_targets() -> None:
    report = summarize_replay_examples(
        [
            {"target": {"first_blocker": "S3-global-parent-transitions", "repair_action": "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE"}},
            {"target": {"first_blocker": "S4-parametric-lifting", "repair_action": "PROVE_PARAMETRIC_LIFTING_LEMMA"}},
            {"target": {"first_blocker": "S3-global-parent-transitions", "repair_action": "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE"}},
        ]
    )

    assert report["example_count"] == 3
    assert report["first_blocker_counts"]["S3-global-parent-transitions"] == 2
    assert report["repair_action_counts"]["PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE"] == 2
