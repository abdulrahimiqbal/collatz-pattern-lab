import json

from collatz_lab.proof_corpus_scaler import build_scaled_proof_corpus, build_scaled_proof_corpus_shards


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_jsonl(path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_scaled_corpus_meets_stream_thresholds(tmp_path) -> None:
    attempts = tmp_path / "attempts.jsonl"
    _write_jsonl(
        attempts,
        [
            {
                "run_id": "R",
                "verifier_status": "FAIL",
                "proof_progress_percent": 0,
                "blocking_steps": ["S5-debt-induction"],
            }
        ],
    )
    bypass = tmp_path / "bypass.json"
    _write_json(
        bypass,
        {
            "schema": "collatz_lab.high_parent_bypass",
            "status": "MIXED_MODULUS_BYPASS_BUILT",
            "mixed_successor_family_count": 1,
            "mixed_successor_families": [
                {
                    "branch_id": "P2:r5:d3",
                    "a": 2,
                    "r_residue": 5,
                    "r_depth": 3,
                    "h": 1,
                    "known_target_parent_floor": 2,
                    "z_family": "z(k) = 1 + 9*k",
                    "successor_family_rule": "successor",
                    "valuation_family_samples": [{"target_family": "P2"}],
                    "sample_checks_passed": True,
                }
            ],
        },
    )
    debt = tmp_path / "debt.json"
    _write_json(
        debt,
        {
            "schema": "collatz_lab.mixed_modulus_debt_verifier",
            "status": "MIXED_MODULUS_DEBT_VERIFIER_READY_WITH_OPEN_BLOCKERS",
            "verifier_status": "FAIL",
            "transitions": [
                {
                    "branch_id": "P2:r5:d3",
                    "source_state": {"parent_level": 2},
                    "target_state": {"parent_level": 2, "valuation": 0},
                    "gain_bound": {"numerator": 1, "denominator": 2},
                    "local_descent_passed": True,
                    "status": "PASS",
                }
            ],
            "blocking_obligations": ["prove unbounded valuation closure"],
        },
    )

    report = build_scaled_proof_corpus(
        target_examples=30,
        min_general_formal=8,
        min_collatz_structural=12,
        min_verifier_replay=8,
        proof_attempts_log=attempts,
        high_parent_bypass_path=bypass,
        mixed_modulus_debt_path=debt,
        cycle_mining_path=None,
        theorem_candidate_path=None,
        preflight_path=None,
    )

    assert report["status"] == "SCALED_PROOF_CORPUS_BUILT"
    assert report["thresholds_met"]["target_examples"] is True
    assert report["thresholds_met"]["general_formal_proof"] is True
    assert report["thresholds_met"]["collatz_structural"] is True
    assert report["thresholds_met"]["verifier_replay"] is True
    assert report["stream_mix"]["general_formal_proof"] >= 8
    assert report["stream_mix"]["collatz_structural"] >= 12
    assert report["stream_mix"]["verifier_replay"] >= 8


def test_scaled_corpus_shards_write_without_materializing_one_file(tmp_path) -> None:
    attempts = tmp_path / "attempts.jsonl"
    _write_jsonl(attempts, [])
    bypass = tmp_path / "bypass.json"
    _write_json(
        bypass,
        {
            "schema": "collatz_lab.high_parent_bypass",
            "status": "MIXED_MODULUS_BYPASS_BUILT",
            "mixed_successor_families": [
                {
                    "branch_id": "P2:r5:d3",
                    "a": 2,
                    "r_residue": 5,
                    "r_depth": 3,
                    "h": 1,
                    "known_target_parent_floor": 2,
                    "z_family": "z(k) = 1 + 9*k",
                    "successor_family_rule": "successor",
                    "valuation_family_samples": [{"target_family": "P2"}],
                    "sample_checks_passed": True,
                }
            ],
        },
    )
    debt = tmp_path / "debt.json"
    _write_json(
        debt,
        {
            "schema": "collatz_lab.mixed_modulus_debt_verifier",
            "transitions": [
                {
                    "branch_id": "P2:r5:d3",
                    "source_state": {"parent_level": 2},
                    "target_state": {"parent_level": 2, "valuation": 0},
                    "gain_bound": {"numerator": 1, "denominator": 2},
                    "local_descent_passed": True,
                    "status": "PASS",
                }
            ],
            "blocking_obligations": ["prove unbounded valuation closure"],
        },
    )

    report = build_scaled_proof_corpus_shards(
        shard_dir=tmp_path / "shards",
        target_examples=30,
        min_general_formal=8,
        min_collatz_structural=12,
        min_verifier_replay=8,
        shard_size=10,
        chunk_size=5,
        proof_attempts_log=attempts,
        high_parent_bypass_path=bypass,
        mixed_modulus_debt_path=debt,
        cycle_mining_path=None,
        theorem_candidate_path=None,
        preflight_path=None,
    )

    assert report["example_count"] >= 30
    assert report["shard_count"] >= 3
    assert len(list((tmp_path / "shards").glob("*.jsonl"))) == report["shard_count"]
