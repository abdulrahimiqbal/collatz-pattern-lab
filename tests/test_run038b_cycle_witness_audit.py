import json
from pathlib import Path

from collatz_lab.proof_action_run038b import run_cycle_witness_audit_from_config


ROOT = Path(__file__).resolve().parents[1]


def test_run038b_audits_representative_cycle_without_claiming_proof(tmp_path: Path) -> None:
    cfg = tmp_path / "run038b.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "cycle_witness_audit_run038b:",
                f"  out_dir: {out_dir}",
                f"  obstruction: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/minimal_invariant_obstruction.json'}",
                f"  edge_maps: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/scc_edge_maps_normalized.jsonl'}",
                f"  cycles: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/scc_cycles_full_or_basis.jsonl'}",
                "  max_cycle_audits: 1",
                "  repeat_bound: 3",
            ]
        ),
        encoding="utf-8",
    )

    result = run_cycle_witness_audit_from_config(cfg)
    witnesses = [
        json.loads(line)
        for line in (out_dir / "cycle_witnesses.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert result["status"] == "EXECUTABLE_REPEATABLE_NON_DESCENDING"
    assert result["audited_cycle_count"] == 1
    assert witnesses[0]["cycle_id"] == "abbe9ad764c55f27"
    assert witnesses[0]["minimum_cycle_domain_witness"]["status"] == "PASS"
    assert witnesses[0]["minimum_self_return_domain_witness"]["status"] == "PASS"
    assert witnesses[0]["classification"] == "EXECUTABLE_REPEATABLE_NON_DESCENDING"
