"""RUN-058A proof-scope status guard."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_scope_status import REPO_ROOT, build_proof_scope_status, sha256_file, write_json
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-058A-proof-scope-status-guard"


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run058a_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_proof_scope_guard(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("proof_scope_guard_run058a", {}) if isinstance(cfg.get("proof_scope_guard_run058a"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    uncovered_path = Path(run_cfg.get("run057_uncovered_parent_families") or "certificate_store/run057_uncovered_parent_families.jsonl")

    strict = replay_manifest(manifest_path)
    scope = build_proof_scope_status(strict_replay=strict, uncovered_families_path=uncovered_path)
    status = scope["scope_status"]

    status_out = out_dir / "formalization_status.json"
    guard_out = out_dir / "proof_scope_status.json"
    run_result_out = out_dir / "run_result.json"
    write_json(scope, guard_out)
    write_json(
        {
            "schema": "collatz_lab.run058a_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": status,
            "strict_replay_status": strict.get("strict_verifier"),
            "global_verifier_status": scope.get("global_verifier_status"),
            "public_proof_confidence_percent": scope.get("public_proof_confidence_percent"),
        },
        status_out,
    )
    result = {
        "schema": "collatz_lab.run058a_proof_scope_status_guard",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if status in {"UNIVERSAL_COLLATZ_ENTRY_FAIL", "UNIVERSAL_ENTRY_COVERAGE_CLOSED"} else "FAIL",
        "formalization_status": status,
        "training_launched": False,
        "search_launched": False,
        "strict_replay": strict,
        "proof_scope_status": scope,
        "source_artifacts": {
            "manifest": {"path": str(manifest_path), "sha256": sha256_file(manifest_path)},
            "run057_uncovered_parent_families": {
                "path": str(uncovered_path),
                "sha256": sha256_file(uncovered_path) if uncovered_path.exists() else "",
            },
        },
        "artifacts": {
            "proof_scope_status": str(guard_out),
            "formalization_status": str(status_out),
            "run_result": str(run_result_out),
        },
    }
    write_json(result, run_result_out)
    store_guard = _copy_to_store("proof_scope_status", guard_out)
    store_result = _copy_to_store("run_result", run_result_out)
    result["artifacts"]["certificate_store_proof_scope_status"] = str(store_guard)
    result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(result, run_result_out)
    shutil.copy2(run_result_out, store_result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_proof_scope_guard(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
