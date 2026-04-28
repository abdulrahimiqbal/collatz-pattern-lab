"""RUN-039 top-level replay gate after RUN-038 SCC invariant discovery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-039-top-level-after-scc-invariant"
DEFAULT_RUN038_DIR = Path("reports/runs/RUN-038-scc-invariant-discovery")


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_top_level_after_scc_invariant(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("top_level_after_scc_invariant_run039", {})
        if isinstance(cfg.get("top_level_after_scc_invariant_run039", {}), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    run038_dir = Path(run_cfg.get("run038_dir") or DEFAULT_RUN038_DIR)
    run038_result_path = Path(run_cfg.get("run038_result") or run038_dir / "run_result.json")
    obstruction_path = Path(run_cfg.get("run038_obstruction") or run038_dir / "minimal_invariant_obstruction.json")
    run038_result = _load_json(run038_result_path)
    obstruction = _load_json(obstruction_path) if obstruction_path.exists() else {}

    root_replay_out = out_dir / "root_manifest_replay_result.json"
    root_replay = replay_manifest(run_cfg.get("manifest") or "proof_manifest.json", out=root_replay_out)

    status = "BLOCKED_BY_RUN038_INVARIANT_OBSTRUCTION"
    top_level_replay_pass = 0
    if run038_result.get("status") == "PASS" and run038_result.get("accepted_scc_ranking") is True:
        status = "RUN038_PASS_TOP_LEVEL_REFRESH_REQUIRES_SCC_AWARE_REPLAY"

    result = {
        "schema": "collatz_lab.run039_top_level_after_scc_invariant",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "status": status,
        "top_level_certificates_generated": 0,
        "top_level_replay_pass": top_level_replay_pass,
        "strict_verifier": root_replay.get("strict_verifier"),
        "proof_confidence_percent": root_replay.get("proof_confidence_percent"),
        "hash_failure_count": root_replay.get("hash_failure_count", 0),
        "scc_invariant_obstruction": {
            "run038_status": run038_result.get("status"),
            "classification": obstruction.get("classification", run038_result.get("failure_classification")),
            "scc_internal_edge_count": run038_result.get("scc_internal_edge_count"),
            "cycle_checks_attempted": run038_result.get("cycle_checks_attempted"),
            "domain_compatible_non_descending_cycle_count": run038_result.get("domain_compatible_non_descending_cycle_count"),
            "exact_invariant_gap": obstruction.get("exact_invariant_gap"),
            "representative_cycle_id": (
                obstruction.get("representative_non_descending_cycle", {}) or {}
            ).get("cycle_id"),
        },
        "artifacts": {
            "root_manifest_replay_result": str(root_replay_out),
            "scc_invariant_obstruction": str(obstruction_path),
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
    result = run_top_level_after_scc_invariant(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
