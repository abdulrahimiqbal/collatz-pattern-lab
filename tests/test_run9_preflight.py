import json

from collatz_lab.run9_preflight import build_run9_preflight


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_jsonl(path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _base_paths(tmp_path):
    return {
        "corpus_jsonl": tmp_path / "corpus.jsonl",
        "corpus_report_path": tmp_path / "corpus.json",
        "model_report_path": tmp_path / "model.json",
        "proposal_path": tmp_path / "proposal.json",
        "verification_path": tmp_path / "verification.json",
        "high_parent_bypass_path": tmp_path / "high_parent_bypass.json",
        "mixed_modulus_debt_verifier_path": tmp_path / "mixed_modulus_debt_verifier.json",
    }


def _write_smoke_artifacts(tmp_path, example_count=12, proof_confidence=0.0, verification_status="FAIL"):
    paths = _base_paths(tmp_path)
    _write_jsonl(paths["corpus_jsonl"], [{"id": i} for i in range(example_count)])
    _write_json(
        paths["corpus_report_path"],
        {
            "schema": "collatz_lab.proof_corpus_report",
            "example_count": example_count,
            "stream_mix": {
                "general_formal_proof": 3,
                "collatz_structural": 5,
                "verifier_replay": 4,
            },
        },
    )
    model_path = tmp_path / "model.pkl"
    model_path.write_text("placeholder", encoding="utf-8")
    _write_json(
        paths["model_report_path"],
        {
            "schema": "collatz_lab.proof_inventor_training_report",
            "status": "TRAINED_BOOTSTRAP_COLLATZ_PROOF_INVENTOR",
            "model_kind": "Tfidf char n-gram retrieval + LogisticRegression task/action/outcome heads",
            "model_path": str(model_path),
            "example_count": example_count,
            "scaling_law_readiness": {
                "has_general_proof_stream": True,
                "has_collatz_structural_stream": True,
                "has_verifier_replay_stream": True,
            },
        },
    )
    _write_json(
        paths["proposal_path"],
        {
            "schema": "collatz_lab.model_proof_proposal",
            "proof_text": "Try the mixed-modulus debt verifier.",
        },
    )
    _write_json(
        paths["verification_path"],
        {
            "schema": "collatz_lab.model_proof_verification",
            "status": verification_status,
            "proof_confidence_percent": proof_confidence,
            "accepted_claim_count": 1,
            "total_claim_count": 4,
            "proof_inventor_predictions": {
                "actions": [
                    {"label": "TRY_MIXED_MODULUS_DEBT_VERIFIER", "score": 0.8},
                    {"label": "PROPOSE_MIXED_MODULUS_STATE", "score": 0.1},
                ]
            },
        },
    )
    _write_json(
        paths["high_parent_bypass_path"],
        {
            "schema": "collatz_lab.high_parent_bypass",
            "status": "MIXED_MODULUS_BYPASS_BUILT",
            "mixed_successor_family_count": 164,
            "all_sample_checks_passed": True,
        },
    )
    return paths


def test_run9_preflight_blocks_small_bootstrap_model(tmp_path) -> None:
    paths = _write_smoke_artifacts(tmp_path)

    report = build_run9_preflight(**paths)

    assert report["ready_for_run9"] is False
    assert report["local_smoke_ready"] is True
    assert "proof_corpus_large_enough_for_scaling_run" in report["blocking_checks"]
    assert "proof_model_is_scaling_target_not_bootstrap" in report["blocking_checks"]
    assert "mixed_modulus_debt_verifier_available" in report["blocking_checks"]


def test_run9_preflight_passes_with_scale_model_and_debt_verifier(tmp_path) -> None:
    paths = _write_smoke_artifacts(tmp_path, example_count=12)
    model_path = tmp_path / "transformer.pt"
    model_path.write_text("placeholder", encoding="utf-8")
    _write_json(
        paths["model_report_path"],
        {
            "schema": "collatz_lab.proof_inventor_training_report",
            "status": "TRAINED_SHARED_PROOF_MODEL",
            "model_kind": "shared Transformer proof model",
            "model_path": str(model_path),
            "example_count": 12,
            "parameter_count": 128,
            "train_steps_completed": 4,
            "scaling_law_readiness": {
                "has_general_proof_stream": True,
                "has_collatz_structural_stream": True,
                "has_verifier_replay_stream": True,
            },
        },
    )
    _write_json(
        paths["mixed_modulus_debt_verifier_path"],
        {
            "schema": "collatz_lab.mixed_modulus_debt_verifier",
            "status": "MIXED_MODULUS_DEBT_VERIFIER_READY_WITH_OPEN_BLOCKERS",
            "verifier_available": True,
            "ready_for_run9": True,
            "proof_closed": False,
            "exact_transition_checks_passed": True,
            "transition_count": 8,
        },
    )

    report = build_run9_preflight(
        **paths,
        min_examples=12,
        min_general_formal=3,
        min_collatz_structural=5,
        min_verifier_replay=4,
        min_model_parameters=128,
        min_train_steps=4,
    )

    assert report["ready_for_run9"] is True
    assert report["blocking_checks"] == []


def test_run9_preflight_blocks_inflated_confidence_without_pass(tmp_path) -> None:
    paths = _write_smoke_artifacts(tmp_path, proof_confidence=25.0, verification_status="FAIL")

    report = build_run9_preflight(**paths)

    assert report["ready_for_run9"] is False
    assert "proof_confidence_is_verifier_gated" in report["blocking_checks"]
