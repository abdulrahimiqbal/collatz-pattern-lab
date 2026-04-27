from collatz_lab.lifted_postprocess import summarize_lifted_certificates


def test_lifted_postprocess_marks_local_certificates_not_global_closure() -> None:
    rows = [
        {
            "rule": {
                "modulus": 8,
                "residue": 7,
                "suggested_k": 3,
                "parent_residue_mod_64": 7,
                "parent_residue_mod_1024": 7,
                "support": 2,
                "source": "test",
            },
            "exact": {"status": "PASS", "modulus": 8, "residue": 7, "k": 3},
        },
        {
            "rule": {
                "modulus": 8,
                "residue": 7,
                "suggested_k": 3,
                "parent_residue_mod_64": 7,
                "parent_residue_mod_1024": 7,
                "support": 1,
                "source": "test",
            },
            "exact": {"status": "PASS", "modulus": 8, "residue": 7, "k": 3},
        },
        {
            "rule": {"modulus": 16, "residue": 15, "suggested_k": 4},
            "exact": {"status": "FAIL_WITH_COUNTEREXAMPLE", "modulus": 16, "residue": 15, "k": 4},
        },
    ]
    summary = summarize_lifted_certificates(
        rows,
        compression_report={"raw_leaf_count": 1, "compressed_leaf_count": 1, "merged_leaf_count": 0},
    )
    assert summary["verified_leaf_count"] == 1
    assert summary["verification_status_counts"]["PASS"] == 2
    assert summary["compression_status"] == "NO_MERGES_FOUND"
    assert summary["global_proof_closure"] is False
    assert summary["top_affine_groups"]
    assert summary["certificates_sample"][0]["support"] == 3
