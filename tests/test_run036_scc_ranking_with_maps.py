import json
from pathlib import Path

from collatz_lab.proof_action_run036 import run_scc_ranking_with_parent_maps


ROOT = Path(__file__).resolve().parents[1]


def test_run036_uses_parent_maps_and_reports_cycle_obstruction(tmp_path: Path) -> None:
    cfg = tmp_path / "run036.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "scc_ranking_with_maps_run036:",
                f"  out_dir: {out_dir}",
                f"  unresolved_sccs: {ROOT / 'reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening/unresolved_sccs.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run035_parent_transition_certificates.jsonl'}",
                f"  s6_lemma_certificates: {ROOT / 'certificate_store/run035_s6_lemma_certificates.jsonl'}",
                "  cycle_cap: 128",
            ]
        ),
        encoding="utf-8",
    )

    result = run_scc_ranking_with_parent_maps(cfg)
    obstruction = json.loads((out_dir / "minimal_ranking_obstruction.json").read_text(encoding="utf-8"))

    assert result["scc_internal_edge_count"] == 106
    assert result["affine_edge_map_pass"] == 106
    assert result["affine_edge_map_fail"] == 0
    assert result["status"] == "CYCLE_COMPOSITION_NOT_DESCENDING"
    assert result["cycle_obstruction_count"] > 0
    assert obstruction["classification"] == "CYCLE_COMPOSITION_NOT_DESCENDING"
    assert obstruction["unresolved_scc_states"] == [f"P{i}" for i in range(12, 25)]
