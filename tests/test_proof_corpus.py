from collatz_lab.proof_corpus import build_proof_corpus


def test_proof_corpus_mixes_collatz_structure_and_replay(tmp_path) -> None:
    attempts = tmp_path / "attempts.jsonl"
    attempts.write_text(
        '{"run_id":"R","verifier_status":"FAIL","proof_progress_percent":26,'
        '"blocking_steps":["S5-debt-induction"],"next_step":"fix debt"}\n',
        encoding="utf-8",
    )
    bypass = tmp_path / "bypass.json"
    bypass.write_text(
        """
        {
          "status": "MIXED_MODULUS_BYPASS_BUILT",
          "mixed_successor_families": [
            {
              "branch_id": "P7:r5:d3",
              "a": 7,
              "r_residue": 5,
              "r_depth": 3,
              "h": 1,
              "known_target_parent_floor": 2,
              "z_family": "z(k)=1+3^7*k",
              "successor_family_rule": "target r mod 3^a",
              "valuation_family_samples": [{"target_family": "P2 r == 1 mod 2187"}],
              "sample_checks_passed": true
            }
          ],
          "level_rank_analysis": {
            "status": "FAIL",
            "cycle_log_gain_sum": 1.0,
            "positive_cycle_witness": [{"branch_id": "P20"}]
          }
        }
        """,
        encoding="utf-8",
    )
    report = build_proof_corpus(
        proof_attempts_log=attempts,
        high_parent_bypass_path=bypass,
        mixed_modulus_debt_path=None,
        cycle_mining_path=None,
        theorem_candidate_path=None,
        preflight_path=None,
    )

    assert report["status"] == "PROOF_CORPUS_BUILT"
    assert report["example_count"] >= 3
    assert report["stream_mix"]["collatz_structural"] >= 2
    assert report["stream_mix"]["verifier_replay"] >= 1
    assert "TRY_MIXED_MODULUS_DEBT_VERIFIER" in report["label_counts"]
