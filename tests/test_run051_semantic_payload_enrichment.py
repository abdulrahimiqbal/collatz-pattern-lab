from pathlib import Path

from collatz_lab.proof_action_run051 import run_semantic_payload_enrichment


def test_run051_semantic_payload_enrichment_passes(tmp_path: Path) -> None:
    cfg = tmp_path / "run051.yaml"
    out_dir = tmp_path / "run051"
    cfg.write_text(
        "\n".join(
            [
                "semantic_payload_enrichment_run051:",
                f"  out_dir: {out_dir}",
                "  manifest: proof_manifest.json",
                "  natural_viability_kernel_certificate: certificate_store/run045_natural_viability_kernel_certificate.json",
                "  run048_semantic_witnesses: certificate_store/run048_semantic_witnesses.jsonl",
                "  run050_missing_semantic_gaps: reports/runs/RUN-050-lean-abstract-transition-system-bridge/missing_semantic_gaps.md",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_semantic_payload_enrichment(cfg)

    assert result["status"] == "PASS"
    assert result["failure_reason"] is None
    assert result["semantic_payload_count"] == 212
    assert result["s3_semantic_role_count"] == 182
    assert result["s6_proof_tree_count"] == 28
    assert result["build_failure_count"] == 0
    assert result["semantic_replay"]["status"] == "PASS"
    assert (out_dir / "enriched_semantic_payloads.jsonl").exists()
    assert (out_dir / "s3_semantic_roles.jsonl").exists()
    assert (out_dir / "s6_proof_trees.jsonl").exists()
    assert (out_dir / "kernel_to_path_link.json").exists()
    assert (out_dir / "top_level_coverage_domain_map.json").exists()
    assert (out_dir / "run_result.json").exists()
