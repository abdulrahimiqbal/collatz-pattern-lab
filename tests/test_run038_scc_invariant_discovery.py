import json
from pathlib import Path

from collatz_lab.proof_action_run038 import run_scc_invariant_discovery_from_config


ROOT = Path(__file__).resolve().parents[1]


def test_run038_discovers_exact_cycle_obstruction_without_accepting_ranking(tmp_path: Path) -> None:
    cfg = tmp_path / "run038.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "scc_invariant_discovery_run038:",
                f"  out_dir: {out_dir}",
                f"  run030_dir: {ROOT / 'reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening'}",
                f"  run036_dir: {ROOT / 'reports/runs/RUN-036-exact-scc-ranking-with-parent-coordinate-maps'}",
                f"  unresolved_sccs: {ROOT / 'reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening/unresolved_sccs.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run035_parent_transition_certificates.jsonl'}",
                f"  manifest: {ROOT / 'proof_manifest.json'}",
                "  cycle_cap: 16",
                "  refinement_modulus_cap: 32",
            ]
        ),
        encoding="utf-8",
    )

    result = run_scc_invariant_discovery_from_config(cfg)
    obstruction = json.loads((out_dir / "minimal_invariant_obstruction.json").read_text(encoding="utf-8"))
    drift = json.loads((out_dir / "cycle_drift_report.json").read_text(encoding="utf-8"))

    assert result["scc_internal_edge_count"] == 106
    assert result["normalized_edge_map_pass"] == 106
    assert result["hash_failure_count"] == 0
    assert result["status"] == "CYCLE_COMPOSITION_NOT_DESCENDING"
    assert not result["accepted_scc_ranking"]
    assert not (out_dir / "accepted_scc_ranking_certificate.json").exists()
    assert obstruction["classification"] == "CYCLE_COMPOSITION_NOT_DESCENDING"
    assert obstruction["representative_non_descending_cycle"]["domain_status"] == "PASS"
    assert drift["non_descending"] > 0
