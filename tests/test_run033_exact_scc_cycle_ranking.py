import json
from pathlib import Path

from collatz_lab.proof_action_scc_ranking_cert import run_exact_scc_cycle_ranking_certificate

ROOT = Path(__file__).resolve().parents[1]
RUN030 = ROOT / "reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening"


def test_run033_extracts_real_scc_and_reports_missing_parent_coordinate_maps(tmp_path: Path) -> None:
    cfg = tmp_path / "run033.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "scc_ranking_run033:",
                f"  out_dir: {out_dir}",
                f"  run030_dir: {RUN030}",
                f"  unresolved_sccs: {RUN030 / 'unresolved_sccs.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run030_parent_transition_certificates.jsonl'}",
                f"  manifest: {ROOT / 'proof_manifest.json'}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_exact_scc_cycle_ranking_certificate(cfg)
    obstruction = json.loads((out_dir / "minimal_ranking_obstruction.json").read_text(encoding="utf-8"))
    map_rows = [json.loads(line) for line in (out_dir / "scc_affine_edge_maps.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    assert result["status"] == "MISSING_PARENT_COORDINATE_MAP"
    assert result["scc_internal_edge_count"] == 106
    assert result["affine_edge_map_pass"] == 0
    assert result["affine_edge_map_fail"] == 106
    assert result["training_launched"] is False
    assert result["big_model_launched"] is False
    assert result["selector_work_launched"] is False
    assert result["floating_point_certificate_used"] is False
    assert obstruction["classification"] == "MISSING_PARENT_COORDINATE_MAP"
    assert obstruction["unresolved_scc_states"] == [f"P{i}" for i in range(12, 25)]
    assert len(obstruction["missing_parent_coordinate_map_certificate_ids"]) == 106
    assert {row["failure_classification"] for row in map_rows} == {"MISSING_PARENT_COORDINATE_MAP"}
    assert "q' = (A*q + B) / D" in (out_dir / "new_math_required.md").read_text(encoding="utf-8")


def test_run030_still_does_not_pass_without_replayed_scc_ranking_certificate() -> None:
    replay = json.loads((RUN030 / "strict_replay_result.json").read_text(encoding="utf-8"))

    assert replay["strict_verifier"] == "FAIL"
    assert any(row["obligation_id"] == "top_level:well_founded_ranking_certificate" for row in replay["unknown_obligations"])
