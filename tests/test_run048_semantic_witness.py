from pathlib import Path

from collatz_lab.proof_action_run048 import run_semantic_witness_enrichment


def test_run048_semantic_witness_replay_passes(tmp_path: Path) -> None:
    cfg = tmp_path / "run048.yaml"
    out_dir = tmp_path / "run048"
    cfg.write_text(
        "\n".join(
            [
                "semantic_witness_run048:",
                f"  out_dir: {out_dir}",
                "  manifest: proof_manifest.json",
                "  natural_viability_kernel_certificate: certificate_store/run045_natural_viability_kernel_certificate.json",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_semantic_witness_enrichment(cfg)

    assert result["status"] == "PASS"
    assert result["semantic_witness_count"] > 0
    assert result["failure_reason"] is None
    assert result["build_failure_count"] == 0
    assert result["semantic_replay"]["status"] == "PASS"
    assert not any(
        failure["reason"] == "MISSING_S4_ITERATE_WITNESS"
        for failure in result["semantic_replay"]["failures"]
    )
    assert (out_dir / "semantic_witnesses.jsonl").exists()
    assert (out_dir / "enriched_certificate_manifest.json").exists()
    assert (out_dir / "run_result.json").exists()
