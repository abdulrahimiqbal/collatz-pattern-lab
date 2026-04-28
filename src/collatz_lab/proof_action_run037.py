"""RUN-037 top-level refresh gate after SCC ranking."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-037-top-level-after-scc-ranking"
DEFAULT_RUN036_DIR = Path("reports/runs/RUN-036-exact-scc-ranking-with-parent-coordinate-maps")


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_top_level_after_scc_ranking(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("top_level_after_scc_ranking_run037", {}) if isinstance(cfg.get("top_level_after_scc_ranking_run037", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    run036_dir = Path(run_cfg.get("run036_dir") or DEFAULT_RUN036_DIR)
    run036_result = _load_json(run_cfg.get("run036_result") or run036_dir / "run_result.json")
    obstruction_path = Path(run_cfg.get("run036_obstruction") or run036_dir / "minimal_ranking_obstruction.json")
    obstruction = _load_json(obstruction_path) if obstruction_path.exists() else {}
    root_replay_out = out_dir / "root_manifest_replay_result.json"
    root_replay = replay_manifest(run_cfg.get("manifest") or "proof_manifest.json", out=root_replay_out)

    status = "BLOCKED_BY_RUN036_RANKING_OBSTRUCTION"
    if run036_result.get("status") == "PASS":
        status = "RUN036_PASS_TOP_LEVEL_REFRESH_NOT_IMPLEMENTED"
    blocked = status != "PASS"
    result = {
        "schema": "collatz_lab.run037_top_level_after_scc_ranking",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "status": status,
        "top_level_replay_pass": 0,
        "strict_verifier": "FAIL" if blocked else root_replay.get("strict_verifier"),
        "proof_confidence_percent": 0.0 if blocked else root_replay.get("proof_confidence_percent"),
        "hash_failure_count": root_replay.get("hash_failure_count", 0),
        "ranking_obstruction": {
            "run036_status": run036_result.get("status"),
            "classification": obstruction.get("classification", run036_result.get("status")),
            "cycle_obstruction_count": run036_result.get("cycle_obstruction_count"),
            "affine_edge_map_pass": run036_result.get("affine_edge_map_pass"),
            "scc_internal_edge_count": run036_result.get("scc_internal_edge_count"),
            "exact_missing_invariant_type": obstruction.get("exact_missing_invariant_type"),
        },
        "artifacts": {
            "root_manifest_replay_result": str(root_replay_out),
            "ranking_obstruction": str(obstruction_path),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_top_level_after_scc_ranking(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
