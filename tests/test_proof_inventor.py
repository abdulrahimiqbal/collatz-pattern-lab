from collatz_lab.proof_corpus import write_jsonl
from collatz_lab.proof_inventor import propose_proof, serializable_training_report, train_proof_inventor


def test_proof_inventor_trains_and_proposes_checked_proof(tmp_path) -> None:
    examples = []
    for i in range(3):
        examples.append(
            {
                "schema": "collatz_lab.proof_corpus_example",
                "version": 1,
                "example_id": f"hp-{i}",
                "source": "high_parent_bypass",
                "task": "collatz_structure_to_proof_dsl",
                "tags": ["mixed_modulus"],
                "prompt": f"<TASK=PROOF_DSL> branch {i}",
                "target": "define mixed-modulus state",
                "target_object": None,
                "label": "PROPOSE_MIXED_MODULUS_STATE",
                "verifier_status": "PASS",
                "weight": 1.0,
                "metadata": {},
            }
        )
        examples.append(
            {
                "schema": "collatz_lab.proof_corpus_example",
                "version": 1,
                "example_id": f"repair-{i}",
                "source": "proof_attempt_replay",
                "task": "verifier_feedback_to_repair_action",
                "tags": ["repair"],
                "prompt": f"<TASK=REPAIR> debt {i}",
                "target": "try mixed verifier",
                "target_object": None,
                "label": "TRY_MIXED_MODULUS_DEBT_VERIFIER",
                "verifier_status": "FAIL",
                "weight": 1.0,
                "metadata": {},
            }
        )
    corpus = tmp_path / "corpus.jsonl"
    write_jsonl(examples, corpus)

    model = train_proof_inventor(corpus)
    report = serializable_training_report(model)
    bypass = {
        "status": "MIXED_MODULUS_BYPASS_BUILT",
        "ready_for_run7": False,
        "mixed_successor_family_count": 3,
        "all_sample_checks_passed": True,
        "level_rank_analysis": {"status": "FAIL", "cycle_log_gain_sum": 1.0, "positive_cycle_witness": []},
    }
    result = propose_proof(model, "RUN-T", bypass, preflight={"blocking_checks": []}, theorem_candidate={"verifier_status": "FAIL"})

    assert report["status"] == "TRAINED_BOOTSTRAP_COLLATZ_PROOF_INVENTOR"
    assert report["scaling_law_readiness"]["has_collatz_structural_stream"] is True
    assert result["proposal"]["author"] == "collatz_proof_inventor_v1"
    assert result["verification"]["proof_confidence_percent"] == 0.0
    assert result["verification"]["accepted_claim_count"] == 1
