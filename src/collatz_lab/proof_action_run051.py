"""RUN-051 semantic payload enrichment entrypoint."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_semantic_payload_enrichment import (
    REPO_ROOT,
    RUN_ID,
    build_semantic_payloads,
    manifest_artifact_path,
    read_json,
    read_jsonl,
    replay_semantic_payloads,
    sha256_file,
    write_json,
    write_jsonl,
)
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    suffix = "".join(path.suffixes)
    dst = store / f"run051_{name}{suffix}"
    shutil.copy2(path, dst)
    return dst


def _source_entry(path: Path) -> dict[str, Any]:
    return {"name": str(path.relative_to(REPO_ROOT)), "path": str(path.relative_to(REPO_ROOT)), "sha256": sha256_file(path)}


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
        REPO_ROOT / "src/collatz_lab/proof_action_semantic_payload_enrichment.py",
        REPO_ROOT / "src/collatz_lab/proof_action_run051.py",
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
            "semantic_payload_enrichment": {
                "enriched_semantic_payloads": "certificate_store/run051_enriched_semantic_payloads.jsonl",
                "s3_semantic_roles": "certificate_store/run051_s3_semantic_roles.jsonl",
                "s6_proof_trees": "certificate_store/run051_s6_proof_trees.jsonl",
                "kernel_to_path_link": "certificate_store/run051_kernel_to_path_link.json",
                "top_level_coverage_domain_map": "certificate_store/run051_top_level_coverage_domain_map.json",
            },
        },
        REPO_ROOT / "proof_manifest.json",
    )


def _artifact_hashes(paths: dict[str, Path]) -> dict[str, dict[str, str]]:
    return {name: {"path": str(path), "sha256": sha256_file(path)} for name, path in paths.items() if path.exists()}


def run_semantic_payload_enrichment(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("semantic_payload_enrichment_run051", {})
        if isinstance(cfg.get("semantic_payload_enrichment_run051"), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    manifest = read_json(manifest_path)
    s3_path = Path(run_cfg.get("s3_debt_certificates") or manifest_artifact_path(manifest, "s3_debt_certificates", manifest_path=manifest_path))
    s6_path = Path(run_cfg.get("s6_lemma_certificates") or manifest_artifact_path(manifest, "s6_lemma_certificates", manifest_path=manifest_path))
    top_path = Path(run_cfg.get("top_level_certificates") or manifest_artifact_path(manifest, "top_level_certificates", manifest_path=manifest_path))
    natural_path = Path(run_cfg.get("natural_viability_kernel_certificate") or "certificate_store/run045_natural_viability_kernel_certificate.json")
    run048_witnesses_path = Path(run_cfg.get("run048_semantic_witnesses") or "certificate_store/run048_semantic_witnesses.jsonl")
    run050_gap_path = Path(run_cfg.get("run050_missing_semantic_gaps") or "reports/runs/RUN-050-lean-abstract-transition-system-bridge/missing_semantic_gaps.md")

    bundle, build_failures = build_semantic_payloads(
        s3_rows=read_jsonl(s3_path),
        s6_rows=read_jsonl(s6_path),
        natural_kernel_certificate=read_json(natural_path),
        top_level_rows=read_jsonl(top_path),
    )
    payloads = bundle["payloads"]
    replay = replay_semantic_payloads(payloads)

    payloads_out = out_dir / "enriched_semantic_payloads.jsonl"
    s3_out = out_dir / "s3_semantic_roles.jsonl"
    s6_out = out_dir / "s6_proof_trees.jsonl"
    kernel_out = out_dir / "kernel_to_path_link.json"
    coverage_out = out_dir / "top_level_coverage_domain_map.json"
    run_result_out = out_dir / "run_result.json"

    write_jsonl(payloads, payloads_out)
    write_jsonl(bundle["s3_semantic_roles"], s3_out)
    write_jsonl(bundle["s6_proof_trees"], s6_out)
    write_json(bundle["kernel_to_path_link"], kernel_out)
    write_json(bundle["top_level_coverage_domain_map"], coverage_out)

    store_payloads = _copy_to_store("enriched_semantic_payloads", payloads_out)
    store_s3 = _copy_to_store("s3_semantic_roles", s3_out)
    store_s6 = _copy_to_store("s6_proof_trees", s6_out)
    store_kernel = _copy_to_store("kernel_to_path_link", kernel_out)
    store_coverage = _copy_to_store("top_level_coverage_domain_map", coverage_out)

    required_kinds = {
        "S3_SEMANTIC_ROLE",
        "S6_PROOF_TREE_SEMANTICS",
        "NATURAL_KERNEL_TO_PATH_LINK",
        "TOP_LEVEL_COVERAGE_DOMAIN_MAP",
    }
    present_kinds = {str(payload.get("kind", "")) for payload in payloads}
    status = "PASS" if replay.get("accepted") and not build_failures and required_kinds <= present_kinds else "FAIL"
    failure_reason = None
    if status != "PASS":
        failure_reason = "SEMANTIC_PAYLOAD_ENRICHMENT_FAILED"
        for failure in build_failures + replay.get("failures", []):
            if failure.get("reason"):
                failure_reason = str(failure["reason"])
                break

    source_artifacts = {
        "manifest": manifest_path,
        "s3_debt_certificates": s3_path,
        "s6_lemma_certificates": s6_path,
        "natural_viability_kernel_certificate": natural_path,
        "top_level_certificates": top_path,
    }
    if run048_witnesses_path.exists():
        source_artifacts["run048_semantic_witnesses"] = run048_witnesses_path
    if run050_gap_path.exists():
        source_artifacts["run050_missing_semantic_gaps"] = run050_gap_path

    result = {
        "schema": "collatz_lab.run051_semantic_payload_enrichment",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "search_launched": False,
        "status": status,
        "failure_reason": failure_reason,
        "semantic_payload_count": len(payloads),
        "s3_semantic_role_count": len(bundle["s3_semantic_roles"]),
        "s6_proof_tree_count": len(bundle["s6_proof_trees"]),
        "required_payload_kinds_present": sorted(present_kinds & required_kinds),
        "semantic_replay": replay,
        "build_failure_count": len(build_failures),
        "build_failures": build_failures[:50],
        "source_artifacts": _artifact_hashes(source_artifacts),
        "artifacts": {
            "enriched_semantic_payloads": str(payloads_out),
            "s3_semantic_roles": str(s3_out),
            "s6_proof_trees": str(s6_out),
            "kernel_to_path_link": str(kernel_out),
            "top_level_coverage_domain_map": str(coverage_out),
            "run_result": str(run_result_out),
            "certificate_store_enriched_semantic_payloads": str(store_payloads),
            "certificate_store_s3_semantic_roles": str(store_s3),
            "certificate_store_s6_proof_trees": str(store_s6),
            "certificate_store_kernel_to_path_link": str(store_kernel),
            "certificate_store_top_level_coverage_domain_map": str(store_coverage),
        },
    }
    write_json(result, run_result_out)
    store_result = _copy_to_store("run_result", run_result_out)
    result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(result, run_result_out)
    shutil.copy2(run_result_out, store_result)

    if bool(run_cfg.get("write_repo_replay_bundle", False)) and status == "PASS":
        _write_repo_manifest(
            manifest,
            store_artifacts={
                "semantic_payloads": store_payloads,
                "s3_semantic_roles": store_s3,
                "s6_proof_trees": store_s6,
                "kernel_to_path_link": store_kernel,
                "top_level_coverage_domain_map": store_coverage,
                "semantic_payload_run_result": store_result,
            },
        )
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_semantic_payload_enrichment(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
