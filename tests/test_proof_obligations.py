import json
from pathlib import Path

from collatz_lab.proof_obligations import build_proof_obligations_report


def test_proof_obligations_synthetic(tmp_path: Path) -> None:
    residual = tmp_path / "residual.json"
    residual.write_text(
        json.dumps(
            {
                "total_q_classes": 8,
                "total_certified_q_classes": 6,
                "residual_unknown_q_classes": 2,
                "total_certified_within_parent_percent": 75,
                "unknown_within_parent_percent": 25,
            }
        )
    )
    cube_lift = tmp_path / "cube_lift.json"
    cube_lift.write_text(
        json.dumps(
            {
                "sets": {
                    "k16": {
                        "status_counts": {
                            "PROVED_INFINITE_ANCESTOR_DESCENT": 1,
                            "NEEDS_SPLIT": 2,
                        }
                    }
                }
            }
        )
    )
    paths = {
        "residual": residual,
        "cube_lift": cube_lift,
        "adic_basin": tmp_path / "missing_adic.json",
        "cycle_mining": tmp_path / "missing_cycle.json",
        "sharp_return": tmp_path / "missing_sharp.json",
        "debt": tmp_path / "missing_debt.json",
        "frontier_strata": tmp_path / "missing_strata.json",
    }
    report = build_proof_obligations_report(paths)
    assert report["proof_status"] == "INCOMPLETE_OPEN_OBLIGATIONS"
    assert report["status_counts"]["CLOSED_BY_ANCESTOR_DESCENT"] == 1
    assert report["status_counts"]["NEEDS_SPLIT"] >= 1
