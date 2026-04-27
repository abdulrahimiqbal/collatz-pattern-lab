from collatz_lab.proof_dsl_model import (
    build_model_proof_proposal,
    build_training_examples,
    train_bootstrap_proof_dsl_model,
    verify_model_proof_proposal,
)


def test_bootstrap_proof_dsl_model_trains_and_targets_mixed_modulus() -> None:
    records = [
        {
            "status": "FAIL",
            "verifier_status": "FAIL",
            "proof_progress_percent": 26.0,
            "blocking_steps": ["S3-global-parent-transitions", "S5-debt-induction"],
        },
        {
            "status": "FAIL",
            "verifier_status": "FAIL",
            "proof_progress_percent": 26.0,
            "blocking_steps": ["S4-parametric-lifting", "S6-strict-theorem-verifier"],
        },
    ]
    bypass = {
        "status": "MIXED_MODULUS_BYPASS_BUILT",
        "ready_for_run7": False,
        "mixed_successor_family_count": 2,
        "all_sample_checks_passed": True,
        "level_rank_analysis": {"status": "FAIL", "cycle_log_gain_sum": 1.0, "positive_cycle_witness": []},
    }
    examples = build_training_examples(records, high_parent_bypass=bypass, preflight={"blocking_checks": []})
    model = train_bootstrap_proof_dsl_model(examples)

    assert model["status"] == "TRAINED_BOOTSTRAP_PROOF_DSL_GENERATOR"
    assert model["example_count"] == len(examples)
    assert "TRY_MIXED_MODULUS_DEBT_VERIFIER" in model["label_counts"]


def test_model_proposal_verification_accepts_only_exact_successor_claim() -> None:
    bypass = {
        "status": "MIXED_MODULUS_BYPASS_BUILT",
        "ready_for_run7": False,
        "mixed_successor_family_count": 164,
        "all_sample_checks_passed": True,
        "level_rank_analysis": {
            "status": "FAIL",
            "cycle_log_gain_sum": 11.0,
            "positive_cycle_witness": [{"branch_id": "P20"}],
        },
    }
    examples = build_training_examples([], high_parent_bypass=bypass, preflight={"blocking_checks": []})
    model = train_bootstrap_proof_dsl_model(examples)
    proposal = build_model_proof_proposal("RUN-T", model, bypass, preflight={"blocking_checks": []})
    verification = verify_model_proof_proposal(
        proposal,
        bypass,
        theorem_candidate={"verifier_status": "FAIL"},
    )

    assert proposal["schema"] == "collatz_lab.model_proof_proposal"
    assert proposal["proof_dsl"]["definitions"][0]["definition_id"] == "mixed_modulus_debt_state"
    assert verification["proof_confidence_percent"] == 0.0
    assert verification["claim_status_counts"]["PASS"] == 1
    assert verification["claim_status_counts"]["FAIL"] == 1
    assert verification["claim_status_counts"]["FAIL_REQUIRES_REPAIR"] == 1
