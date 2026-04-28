import json
from pathlib import Path

from collatz_lab.proof_action_run041 import run_top_level_after_guarded_scc_ranking


def test_run041_stops_when_run040_did_not_replay_pass(tmp_path: Path) -> None:
    run040_dir = tmp_path / "run040"
    run040_dir.mkdir()
    (run040_dir / "run_result.json").write_text(
        json.dumps({"status": "REFINEMENT_CAP_INSUFFICIENT"}) + "\n",
        encoding="utf-8",
    )
    (run040_dir / "scc_guarded_ranking_certificate.json").write_text(
        json.dumps({"status": "FAIL"}) + "\n",
        encoding="utf-8",
    )
    cfg = tmp_path / "run041.yaml"
    out_dir = tmp_path / "run041"
    cfg.write_text(
        "\n".join(
            [
                "top_level_after_guarded_scc_ranking_run041:",
                f"  out_dir: {out_dir}",
                f"  run040_result: {run040_dir / 'run_result.json'}",
                f"  scc_guarded_ranking_certificate: {run040_dir / 'scc_guarded_ranking_certificate.json'}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_top_level_after_guarded_scc_ranking(cfg)

    assert result["status"] == "BLOCKED_BY_RUN040_GUARDED_SCC_RANKING"
    assert result["top_level_certificates_generated"] == 0
    assert result["strict_verifier"] == "FAIL"

