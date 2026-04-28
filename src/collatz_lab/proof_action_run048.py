"""RUN-048 semantic witness enrichment entrypoint."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_semantic_witness import (
    REPO_ROOT,
    RUN_ID,
    build_semantic_witnesses,
    manifest_artifact_path,
    read_json,
    read_jsonl,
    replay_semantic_witnesses,
    sha256_file,
    write_json,
    write_jsonl,
)
from .utils import load_yaml


def _artifact_entry(name: str, path: Path, manifest_dir: Path) -> dict[str, Any]:
    return {"name": name, "path": str(path.relative_to(manifest_dir)), "sha256": sha256_file(path)}


def _source_entry(path: Path) -> dict[str, Any]:
    return {"name": str(path.relative_to(REPO_ROOT)), "path": str(path.relative_to(REPO_ROOT)), "sha256": sha256_file(path)}


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    suffix = "".join(path.suffixes)
    dst = store / f"run048_{name}{suffix}"
    shutil.copy2(path, dst)
    return dst


def _write_repo_manifest(source_manifest: dict[str, Any], *, store_artifacts: dict[str, Path]) -> None:
    artifact_names = {entry.get("name") for entry in source_manifest.get("artifacts", []) or []}
    artifacts = list(source_manifest.get("artifacts", []) or [])
    for name, path in store_artifacts.items():
        entry = {"name": name, "path": str(path.relative_to(REPO_ROOT)), "sha256": sha256_file(path)}
        if name in artifact_names:
            artifacts = [entry if row.get("name") == name else row for row in artifacts]
        else:
            artifacts.append(entry)
    source_names = {entry.get("name") for entry in source_manifest.get("source_files", []) or []}
    source_files = list(source_manifest.get("source_files", []) or [])
    for path in [
        REPO_ROOT / "src/collatz_lab/proof_action_semantic_witness.py",
        REPO_ROOT / "src/collatz_lab/proof_action_run048.py",
    ]:
        entry = _source_entry(path)
        if entry["name"] in source_names:
            source_files = [entry if row.get("name") == entry["name"] else row for row in source_files]
        else:
            source_files.append(entry)
    write_json(
        {
            **source_manifest,
            "run_id": RUN_ID,
            "artifacts": artifacts,
            "source_files": source_files,
            "semantic_witness_enrichment": {
                "semantic_witnesses": "certificate_store/run048_semantic_witnesses.jsonl",
                "enriched_certificate_manifest": "certificate_store/run048_enriched_certificate_manifest.json",
            },
        },
        REPO_ROOT / "proof_manifest.json",
    )


def run_semantic_witness_enrichment(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("semantic_witness_run048", {}) if isinstance(cfg.get("semantic_witness_run048"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    manifest = read_json(manifest_path)
    s3_path = Path(run_cfg.get("s3_debt_certificates") or manifest_artifact_path(manifest, "s3_debt_certificates", manifest_path=manifest_path))
    s4_path = Path(run_cfg.get("parent_transition_certificates") or manifest_artifact_path(manifest, "parent_transition_certificates", manifest_path=manifest_path))
    s6_path = Path(run_cfg.get("s6_lemma_certificates") or manifest_artifact_path(manifest, "s6_lemma_certificates", manifest_path=manifest_path))
    top_path = Path(run_cfg.get("top_level_certificates") or manifest_artifact_path(manifest, "top_level_certificates", manifest_path=manifest_path))
    natural_path = Path(run_cfg.get("natural_viability_kernel_certificate") or "certificate_store/run045_natural_viability_kernel_certificate.json")

    witnesses, build_failures = build_semantic_witnesses(
        s3_rows=read_jsonl(s3_path),
        s4_rows=read_jsonl(s4_path),
        s6_rows=read_jsonl(s6_path),
        natural_kernel_certificate=read_json(natural_path),
        top_level_rows=read_jsonl(top_path),
    )
    replay = replay_semantic_witnesses(witnesses)

    semantic_out = out_dir / "semantic_witnesses.jsonl"
    manifest_out = out_dir / "enriched_certificate_manifest.json"
    run_result_out = out_dir / "run_result.json"
    write_jsonl(witnesses, semantic_out)
    enriched_manifest = {
        "schema": "collatz_lab.enriched_certificate_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_manifest": str(manifest_path),
        "status": "PASS" if replay.get("accepted") else "FAIL",
        "semantic_witness_count": len(witnesses),
        "semantic_witness_hash": sha256_file(semantic_out),
        "source_artifacts": {
            "s3_debt_certificates": str(s3_path),
            "parent_transition_certificates": str(s4_path),
            "s6_lemma_certificates": str(s6_path),
            "natural_viability_kernel_certificate": str(natural_path),
            "top_level_certificates": str(top_path),
        },
        "semantic_replay": replay,
    }
    write_json(enriched_manifest, manifest_out)

    store_semantic = _copy_to_store("semantic_witnesses", semantic_out)
    store_manifest = _copy_to_store("enriched_certificate_manifest", manifest_out)
    status = "PASS" if replay.get("accepted") and not build_failures else "FAIL"
    result = {
        "schema": "collatz_lab.run048_semantic_witness_enrichment",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "search_launched": False,
        "status": status,
        "semantic_witness_count": len(witnesses),
        "semantic_replay": replay,
        "build_failure_count": len(build_failures),
        "build_failures": build_failures[:20],
        "failure_reason": None if status == "PASS" else "MISSING_SEMANTIC_ITERATE_WITNESS",
        "artifacts": {
            "semantic_witnesses": str(semantic_out),
            "enriched_certificate_manifest": str(manifest_out),
            "run_result": str(run_result_out),
            "certificate_store_semantic_witnesses": str(store_semantic),
            "certificate_store_enriched_certificate_manifest": str(store_manifest),
        },
    }
    write_json(result, run_result_out)
    store_result = _copy_to_store("run_result", run_result_out)
    result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(result, run_result_out)
    shutil.copy2(run_result_out, store_result)

    if bool(run_cfg.get("write_repo_replay_bundle", True)) and status == "PASS":
        _write_repo_manifest(
            manifest,
            store_artifacts={
                "semantic_witnesses": store_semantic,
                "enriched_certificate_manifest": store_manifest,
                "semantic_witness_run_result": store_result,
            },
        )
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_semantic_witness_enrichment(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
