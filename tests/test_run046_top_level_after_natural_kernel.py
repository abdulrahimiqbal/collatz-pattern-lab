import json
from pathlib import Path

from collatz_lab.proof_action_run046 import run_top_level_after_natural_kernel_elimination


def test_run046_stops_when_run045_did_not_pass(tmp_path: Path) -> None:
    run045_dir = tmp_path / "run045"
    run045_dir.mkdir()
    (run045_dir / "run_result.json").write_text(json.dumps({"status": "FAIL"}) + "\n", encoding="utf-8")
    (run045_dir / "scc_guarded_ranking_certificate.json").write_text(json.dumps({"status": "FAIL"}) + "\n", encoding="utf-8")
    cfg = tmp_path / "run046.yaml"
    out_dir = tmp_path / "run046"
    cfg.write_text(
        "\n".join(
            [
                "top_level_after_natural_kernel_elimination_run046:",
                f"  out_dir: {out_dir}",
                f"  run045_result: {run045_dir / 'run_result.json'}",
                f"  scc_guarded_ranking_certificate: {run045_dir / 'scc_guarded_ranking_certificate.json'}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_top_level_after_natural_kernel_elimination(cfg)

    assert result["status"] == "BLOCKED_BY_RUN045_NATURAL_KERNEL_ELIMINATION"
    assert result["top_level_certificates_generated"] == 0
    assert result["strict_verifier"] == "FAIL"
