"""Build the RUN-021 strict-verifier replay hardening package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-021-strict-verifier-replay-hardening"
REPO_ROOT = Path(__file__).resolve().parents[2]


DEFAULT_SOURCES = [
    "src/collatz_lab/proof_action_decode.py",
    "src/collatz_lab/proof_action_dsl.py",
    "src/collatz_lab/proof_verifier.py",
    "src/collatz_lab/replay_strict_proof.py",
    "src/collatz_lab/proof_action_run021.py",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_artifact(src: Path, dst: Path) -> dict[str, Any]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {"name": dst.stem, "path": str(dst.relative_to(dst.parents[1])), "sha256": _sha256(dst)}


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _manifest_artifact_entry(name: str, path: Path, manifest_dir: Path) -> dict[str, Any]:
    return {"name": name, "path": str(path.relative_to(manifest_dir)), "sha256": _sha256(path)}


def _source_entry(path: Path) -> dict[str, Any]:
    return {"name": str(path.relative_to(REPO_ROOT)), "path": str(path.relative_to(REPO_ROOT)), "sha256": _sha256(path)}


def _load_cfg(config_path: str | Path | None) -> dict[str, Any]:
    if config_path is None:
        return {}
    return load_yaml(config_path)


def _sound_failure_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# RUN-021 Strict Verifier Replay Hardening",
        "",
        f"- audit status: `{result['audit_status']}`",
        f"- strict verifier: `{result['strict_verifier']}`",
        f"- verifier status: `{result['verifier_status']}`",
        f"- proof confidence: `{result['proof_confidence_percent']}`%",
        "",
        "RUN-021 succeeds by making the former strict PASS fail soundly unless every accepted node is backed by a replayable certificate payload.",
        "",
        "## Root Unsound Certificates",
        "",
    ]
    for row in result.get("root_unsound_certificates", []):
        lines.append(
            f"- `{row['node_type']}` ({row.get('count', 1)}): {row['reason']}; fix: {row['required_fix']}"
        )
    lines.extend(["", "## Strict Errors", ""])
    for error in result.get("strict_errors", []):
        lines.append(f"- {error}")
    lines.extend(["", "## Source Run Downgrade", ""])
    source = result.get("source_run_accounting", {})
    lines.append(f"- source verifier status: `{source.get('verifier_status')}`")
    lines.append(f"- source proof confidence: `{source.get('proof_confidence_percent')}`")
    if source.get("run021_reason"):
        lines.append(f"- reason: {source['run021_reason']}")
    lines.append("")
    return "\n".join(lines)


def build_run021_package(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = _load_cfg(config_path)
    run_cfg = cfg.get("run021", {}) if isinstance(cfg.get("run021", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    store = out_dir / "certificate_store"
    out_dir.mkdir(parents=True, exist_ok=True)
    store.mkdir(parents=True, exist_ok=True)

    run019_dir = Path(run_cfg.get("run019_dir") or "reports/runs/RUN-019-proof-action-v2-parent-residual-cert")
    run020_dir = Path(run_cfg.get("run020_dir") or "reports/runs/RUN-020-proof-audit-package")
    source_artifacts = {
        "proof_dependency_graph_frozen": run020_dir / "proof_dependency_graph_frozen.json",
        "accepted_action_trace": run020_dir / "accepted_action_trace.jsonl",
        "run020_audit_summary": run020_dir / "audit_summary.json",
        "run020_audit_failures": run020_dir / "audit_failures_or_assumptions.md",
        "run019_run_result": run019_dir / "run_result.json",
        "run019_parent_residual_certificate": run019_dir / "parent_residual_certificate.json",
    }
    copied: list[dict[str, Any]] = []
    for name, src in source_artifacts.items():
        if not src.exists():
            raise FileNotFoundError(f"required RUN-021 source artifact is missing: {src}")
        suffix = "".join(src.suffixes)
        dst = store / f"{name}{suffix}"
        shutil.copy2(src, dst)
        copied.append(_manifest_artifact_entry(name, dst, out_dir))

    source_paths = [REPO_ROOT / path for path in run_cfg.get("source_files", DEFAULT_SOURCES)]
    source_entries = [_source_entry(path) for path in source_paths]
    audit_summary = json.loads((run020_dir / "audit_summary.json").read_text(encoding="utf-8"))
    run019_result = json.loads((run019_dir / "run_result.json").read_text(encoding="utf-8"))
    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {
            "run019_strict_verifier": run019_result.get("strict_theorem_verifier_result")
            or run019_result.get("composer_summary", {}).get("strict_theorem_verifier_result"),
            "strict_verifier": run019_result.get("strict_theorem_verifier_result")
            or run019_result.get("composer_summary", {}).get("strict_theorem_verifier_result"),
            "proof_confidence_percent": run019_result.get("proof_confidence_percent")
            or run019_result.get("composer_summary", {}).get("proof_confidence_percent"),
            "audit_status": audit_summary.get("verdict", "FAIL"),
        },
        "artifacts": copied,
        "source_files": source_entries,
        "clean_clone_replay": {
            "command": "python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    manifest_path = out_dir / "proof_manifest.json"
    _write_json(manifest, manifest_path)
    repo_manifest_path = REPO_ROOT / "proof_manifest.json"
    repo_store = REPO_ROOT / "certificate_store"
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copytree(store, repo_store, dirs_exist_ok=True)
        _write_json(manifest, repo_manifest_path)

    replay_result = replay_manifest(manifest_path, out=out_dir / "strict_replay_result.json")
    run_result = {
        **replay_result,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "artifacts": {
            "proof_manifest": str(manifest_path),
            "certificate_store": str(store),
            "repo_proof_manifest": str(repo_manifest_path),
            "repo_certificate_store": str(repo_store),
            "strict_replay_result": str(out_dir / "strict_replay_result.json"),
            "sound_failure_report": str(out_dir / "sound_failure_report.md"),
        },
    }
    _write_json(run_result, out_dir / "run_result.json")
    (out_dir / "sound_failure_report.md").write_text(_sound_failure_markdown(run_result), encoding="utf-8")
    (out_dir / "reproduction_script.sh").write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "python -m pip install -e \".[dev]\"",
                "python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json --out strict_replay_result.json",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return run_result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = build_run021_package(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
