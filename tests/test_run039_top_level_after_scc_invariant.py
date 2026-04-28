from pathlib import Path

from collatz_lab.proof_action_run038 import run_scc_invariant_discovery_from_config
from collatz_lab.proof_action_run039 import run_top_level_after_scc_invariant


ROOT = Path(__file__).resolve().parents[1]


def test_run039_carries_run038_obstruction_without_claiming_pass(tmp_path: Path) -> None:
    run038_cfg = tmp_path / "run038.yaml"
    run038_out = tmp_path / "run038"
    run038_cfg.write_text(
        "\n".join(
            [
                "scc_invariant_discovery_run038:",
                f"  out_dir: {run038_out}",
                f"  unresolved_sccs: {ROOT / 'reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening/unresolved_sccs.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run035_parent_transition_certificates.jsonl'}",
                f"  manifest: {ROOT / 'proof_manifest.json'}",
                "  cycle_cap: 8",
                "  refinement_modulus_cap: 16",
            ]
        ),
        encoding="utf-8",
    )
    run_scc_invariant_discovery_from_config(run038_cfg)

    run039_cfg = tmp_path / "run039.yaml"
    run039_out = tmp_path / "run039"
    run039_cfg.write_text(
        "\n".join(
            [
                "top_level_after_scc_invariant_run039:",
                f"  out_dir: {run039_out}",
                f"  run038_result: {run038_out / 'run_result.json'}",
                f"  run038_obstruction: {run038_out / 'minimal_invariant_obstruction.json'}",
                f"  manifest: {ROOT / 'proof_manifest.json'}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_top_level_after_scc_invariant(run039_cfg)

    assert result["status"] == "BLOCKED_BY_RUN038_INVARIANT_OBSTRUCTION"
    assert result["strict_verifier"] == "FAIL"
    assert result["proof_confidence_percent"] == 0.0
    assert result["scc_invariant_obstruction"]["classification"] == "CYCLE_COMPOSITION_NOT_DESCENDING"
