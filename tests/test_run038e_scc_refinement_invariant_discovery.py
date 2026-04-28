import json
from pathlib import Path

from collatz_lab.proof_action_run038b import run_cycle_witness_audit_from_config
from collatz_lab.proof_action_run038e import run_scc_refinement_invariant_discovery_from_config
from collatz_lab.proof_action_scc_refinement_invariant_discovery import _same_refined_state_domain


ROOT = Path(__file__).resolve().parents[1]


def test_same_refined_state_domain_detects_surviving_exact_split() -> None:
    domain = {"residue": "1", "modulus": "2", "lower_bound": "1"}
    composed = {"A": "1", "B": "2", "D": "1"}

    result = _same_refined_state_domain(
        cycle_domain=domain,
        composed_map=composed,
        refinement_modulus=2,
    )

    assert result["status"] == "PASS"
    assert result["non_descending"] is True
    assert result["q_final"] == "3"


def test_run038e_emits_exact_obstruction_after_run038b(tmp_path: Path) -> None:
    run038b_cfg = tmp_path / "run038b.yaml"
    run038b_out = tmp_path / "run038b"
    run038b_cfg.write_text(
        "\n".join(
            [
                "cycle_witness_audit_run038b:",
                f"  out_dir: {run038b_out}",
                f"  obstruction: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/minimal_invariant_obstruction.json'}",
                f"  edge_maps: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/scc_edge_maps_normalized.jsonl'}",
                f"  cycles: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/scc_cycles_full_or_basis.jsonl'}",
                "  max_cycle_audits: 1",
                "  repeat_bound: 3",
            ]
        ),
        encoding="utf-8",
    )
    run_cycle_witness_audit_from_config(run038b_cfg)

    run038e_cfg = tmp_path / "run038e.yaml"
    run038e_out = tmp_path / "run038e"
    run038e_cfg.write_text(
        "\n".join(
            [
                "scc_refinement_invariant_discovery_run038e:",
                f"  out_dir: {run038e_out}",
                f"  run038b_dir: {run038b_out}",
                f"  cycle_witnesses: {run038b_out / 'cycle_witnesses.jsonl'}",
                f"  edge_maps: {ROOT / 'reports/runs/RUN-038-scc-invariant-discovery/scc_edge_maps_normalized.jsonl'}",
                f"  s3_debt_certificates: {ROOT / 'certificate_store/run035_s3_debt_certificates.jsonl'}",
                "  max_power2_split: 4",
                "  max_power3_split: 3",
            ]
        ),
        encoding="utf-8",
    )

    result = run_scc_refinement_invariant_discovery_from_config(run038e_cfg)
    obstruction = json.loads((run038e_out / "minimal_invariant_obstruction.json").read_text(encoding="utf-8"))

    assert result["status"] == "EXECUTABLE_REPEATABLE_NON_DESCENDING_REFINEMENT_OBSTRUCTION"
    assert result["accepted_scc_ranking"] is False
    assert result["obstruction_feature_rows"] == 8
    assert obstruction["executable"] is True
    assert obstruction["repeatable"] is True
    assert obstruction["cycle_id"] == "abbe9ad764c55f27"
    assert "finite `q mod 2^k`" in (run038e_out / "new_math_required.md").read_text(encoding="utf-8")
