import json
from pathlib import Path

from collatz_lab.proof_action_run040 import run_guarded_scc_ranking_from_config


ROOT = Path(__file__).resolve().parents[1]


def test_run040_builds_full_guarded_domains_and_reclassifies_run039_exit(tmp_path: Path) -> None:
    cfg = tmp_path / "run040.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "guarded_scc_ranking_run040:",
                f"  out_dir: {out_dir}",
                f"  cycle_invariance_report: {ROOT / 'reports/runs/RUN-039-independent-cycle-counterexample-audit/cycle_invariance_report.json'}",
                f"  raw_collatz_multicycle_replay: {ROOT / 'reports/runs/RUN-039-independent-cycle-counterexample-audit/raw_collatz_multicycle_replay.jsonl'}",
                f"  scc_edge_maps_normalized: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/scc_edge_maps_normalized.jsonl'}",
                f"  scc_cycles_full_or_basis: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/scc_cycles_full_or_basis.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run035_parent_transition_certificates.jsonl'}",
                f"  parent_coordinate_map_certificates: {ROOT / 'certificate_store/run034_parent_coordinate_map_certificates.jsonl'}",
                f"  manifest: {ROOT / 'proof_manifest.json'}",
                "  repeat_refinement_cap: 2",
                "  repeat_prefix_cycle_limit: 1",
                "  cycle_reclassification_limit: 1",
                "  cycle_detail_limit: 1",
            ]
        ),
        encoding="utf-8",
    )

    result = run_guarded_scc_ranking_from_config(cfg)
    rows = [json.loads(line) for line in (out_dir / "guarded_cycle_reclassification.jsonl").read_text(encoding="utf-8").splitlines()]

    assert result["guarded_domains_built"] == 106
    assert result["hash_failure_count"] == 0
    assert rows[0]["classification"] == "GUARDED_TRANSIENT_EXIT"
    assert rows[0]["failed_edge_id"] == "s4:s4_parent_transition_73499df187f4649c"
    assert rows[0]["failed_guard"] == "map_integrality"
    assert result["status"] in {"REFINEMENT_CAP_INSUFFICIENT", "NEEDS_NEW_INVARIANT_AFTER_GUARDS"}

