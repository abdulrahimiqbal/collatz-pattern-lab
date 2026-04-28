from pathlib import Path

from collatz_lab.proof_action_run044 import run_guarded_viability_kernel_from_config


ROOT = Path(__file__).resolve().parents[1]


def test_run044_finds_non_natural_2adic_kernel_witness(tmp_path: Path) -> None:
    cfg = tmp_path / "run044.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "guarded_viability_kernel_run044:",
                f"  out_dir: {out_dir}",
                f"  guarded_edge_domains: {ROOT / 'reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_edge_domains.jsonl'}",
                f"  guarded_cycle_reclassification: {ROOT / 'reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_cycle_reclassification.jsonl'}",
                "  cycle_scan_limit: 1",
                "  witness_record_limit: 1",
            ]
        ),
        encoding="utf-8",
    )

    result = run_guarded_viability_kernel_from_config(cfg)

    assert result["status"] == "VIABILITY_KERNEL_NONEMPTY"
    assert result["viability_kernel_nonempty"]
    assert not result["raw_executable_survivor"]
    assert result["surviving_cycle_id"] == "abbe9ad764c55f27"

