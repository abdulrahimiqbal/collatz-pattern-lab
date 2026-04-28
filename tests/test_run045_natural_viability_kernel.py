from pathlib import Path

from collatz_lab.proof_action_run045 import run_natural_viability_kernel_elimination_from_config


ROOT = Path(__file__).resolve().parents[1]


def test_run045_emits_pass_certificate(tmp_path: Path) -> None:
    cfg = tmp_path / "run045.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "natural_viability_kernel_run045:",
                f"  out_dir: {out_dir}",
                f"  run044_guarded_viability_kernel: {ROOT / 'reports/runs/RUN-044-guarded-viability-kernel-elimination/guarded_viability_kernel.json'}",
                f"  guarded_edge_domains: {ROOT / 'reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_edge_domains.jsonl'}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_natural_viability_kernel_elimination_from_config(cfg)

    assert result["status"] == "PASS"
    assert result["natural_viability_kernel_empty"]
    assert result["well_founded_ranking_certificate"] == "PASS"
    assert result["fixed_point"] == {"numerator": -580126354671, "denominator": 141087436042258129}
