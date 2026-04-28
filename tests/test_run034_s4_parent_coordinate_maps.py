import json
from pathlib import Path

from collatz_lab.proof_action_run034 import run_s4_parent_coordinate_maps


ROOT = Path(__file__).resolve().parents[1]
RUN033 = ROOT / "reports/runs/RUN-033-exact-scc-cycle-ranking-certificate"


def test_run034_generates_map_enriched_s4_certificates(tmp_path: Path) -> None:
    cfg = tmp_path / "run034.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "s4_parent_coordinate_maps_run034:",
                f"  out_dir: {out_dir}",
                f"  proof_graph: {ROOT / 'certificate_store/run030_proof_dependency_graph_frozen.json'}",
                f"  accepted_action_trace: {ROOT / 'certificate_store/run030_accepted_action_trace.jsonl'}",
                f"  s3_debt_certificates: {ROOT / 'certificate_store/run030_s3_debt_certificates.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run030_parent_transition_certificates.jsonl'}",
                f"  s6_lemma_certificates: {ROOT / 'certificate_store/run030_s6_lemma_certificates.jsonl'}",
                f"  parent_residual_certificate: {ROOT / 'certificate_store/run030_parent_residual_certificate.json'}",
                f"  top_level_certificates: {ROOT / 'certificate_store/run030_top_level_certificates.jsonl'}",
                f"  scc_internal_edges: {RUN033 / 'scc_internal_edges.jsonl'}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_s4_parent_coordinate_maps(cfg)
    replay_report = json.loads((out_dir / "parent_coordinate_map_replay_report.json").read_text(encoding="utf-8"))
    enriched = [json.loads(line) for line in (out_dir / "s4_transition_certificates_map_enriched.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    assert result["map_enriched_s4_certificates_generated"] == 135
    assert result["parent_coordinate_maps_replay_pass"] == 135
    assert result["internal_scc_edges_with_maps"] == {"covered": 106, "total": 106}
    assert result["hash_failure_count"] == 0
    assert result["s4_root_failures"] == 0
    assert replay_report["all_pass"]
    assert all(row["transition_certificate"]["type"] == "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP" for row in enriched)
    assert all(isinstance(row["transition_certificate"].get("parent_coordinate_map"), dict) for row in enriched)
