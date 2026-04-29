from pathlib import Path

from collatz_lab.proof_action_run056b import run_global_semantic_maps


def test_run056b_global_semantic_maps_reports_exact_gaps(tmp_path: Path) -> None:
    cfg = tmp_path / "run056b.yaml"
    out_dir = tmp_path / "run056b"
    cfg.write_text(
        "\n".join(
            [
                "global_semantic_maps_run056b:",
                f"  out_dir: {out_dir}",
                "  manifest: proof_manifest.json",
                "  s4_semantic_witnesses: certificate_store/run048_semantic_witnesses.jsonl",
                "  s6_proof_trees: certificate_store/run051_s6_proof_trees.jsonl",
                "  s3_semantic_roles: certificate_store/run051_s3_semantic_roles.jsonl",
                "  coverage_domain_map: certificate_store/run051_top_level_coverage_domain_map.json",
                "  kernel_to_path_link: certificate_store/run051_kernel_to_path_link.json",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_global_semantic_maps(cfg)

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "ENTRY_MAP_GAP"
    assert result["semantic_replay"]["well_formed"]
    assert not result["semantic_replay"]["accepted"]
    assert (out_dir / "entry_map.json").exists()
    assert (out_dir / "coverage_map.json").exists()
    assert (out_dir / "no_escape_map.json").exists()
    assert (out_dir / "well_founded_bridge.json").exists()
    assert (out_dir / "formalization_status.json").exists()
    assert (out_dir / "missing_global_semantic_map_gaps.md").exists()
    assert (out_dir / "run_result.json").exists()
