from pathlib import Path

from collatz_lab.proof_action_run037 import run_top_level_after_scc_ranking


ROOT = Path(__file__).resolve().parents[1]


def test_run037_carries_run036_obstruction_without_claiming_pass(tmp_path: Path) -> None:
    cfg = tmp_path / "run037.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "top_level_after_scc_ranking_run037:",
                f"  out_dir: {out_dir}",
                f"  run036_result: {ROOT / 'reports/runs/RUN-036-exact-scc-ranking-with-parent-coordinate-maps/run_result.json'}",
                f"  run036_obstruction: {ROOT / 'reports/runs/RUN-036-exact-scc-ranking-with-parent-coordinate-maps/minimal_ranking_obstruction.json'}",
                f"  manifest: {ROOT / 'proof_manifest.json'}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_top_level_after_scc_ranking(cfg)

    assert result["status"] == "BLOCKED_BY_RUN036_RANKING_OBSTRUCTION"
    assert result["strict_verifier"] == "FAIL"
    assert result["proof_confidence_percent"] == 0.0
    assert result["ranking_obstruction"]["classification"] == "CYCLE_COMPOSITION_NOT_DESCENDING"
