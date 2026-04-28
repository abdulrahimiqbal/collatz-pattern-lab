"""RUN-046 top-level replay after natural kernel elimination."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_guarded_scc_ranking import replay_scc_guarded_ranking_certificate
from .proof_action_top_level_cert import (
    attach_top_level_certificates,
    build_replay_context,
    build_top_level_certificates_after_hardening,
    replay_top_level_certificates,
    write_jsonl,
)
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-046-top-level-after-natural-kernel-elimination"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _artifact_entry(name: str, path: Path, manifest_dir: Path) -> dict[str, Any]:
    return {"name": name, "path": str(path.relative_to(manifest_dir)), "sha256": _sha256(path)}


def _source_entry(path: Path) -> dict[str, Any]:
    return {"name": str(path.relative_to(REPO_ROOT)), "path": str(path.relative_to(REPO_ROOT)), "sha256": _sha256(path)}


def _resolve_manifest_artifact(manifest: dict[str, Any], name: str, *, manifest_path: Path) -> Path:
    manifest_dir = manifest_path.parent
    for entry in manifest.get("artifacts", []) or []:
        if entry.get("name") == name:
            raw = Path(str(entry["path"]))
            if raw.is_absolute():
                return raw
            candidate = manifest_dir / raw
            if candidate.exists():
                return candidate
            return REPO_ROOT / raw
    raise KeyError(f"manifest artifact not found: {name}")


def _manifest_hashes(manifest: dict[str, Any]) -> dict[str, str]:
    return {str(entry.get("name")): str(entry.get("sha256")) for entry in manifest.get("artifacts", []) if entry.get("name")}


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run046_{name}{suffix}"
        shutil.copy2(path, dst)
        entries.append({"name": name, "path": str(dst.relative_to(REPO_ROOT)), "sha256": _sha256(dst)})
    _write_json(
        {
            **manifest,
            "artifacts": entries,
            "clean_clone_replay": {
                "command": "python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json",
                "requires_committed_or_included_artifacts": True,
            },
        },
        REPO_ROOT / "proof_manifest.json",
    )


def run_top_level_after_natural_kernel_elimination(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("top_level_after_natural_kernel_elimination_run046", {}) if isinstance(cfg.get("top_level_after_natural_kernel_elimination_run046"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    run045_result_path = Path(run_cfg.get("run045_result") or "reports/runs/RUN-045-natural-viability-kernel-elimination/run_result.json")
    run045_cert_path = Path(run_cfg.get("scc_guarded_ranking_certificate") or "reports/runs/RUN-045-natural-viability-kernel-elimination/scc_guarded_ranking_certificate.json")
    run045_result = _load_json(run045_result_path) if run045_result_path.exists() else {}
    scc_cert = _load_json(run045_cert_path) if run045_cert_path.exists() else {}
    scc_replay = replay_scc_guarded_ranking_certificate(scc_cert)
    if run045_result.get("status") != "PASS" or not scc_replay.get("accepted"):
        result = {
            "schema": "collatz_lab.run046_top_level_after_natural_kernel_elimination",
            "version": 1,
            "run_id": RUN_ID,
            "training_launched": False,
            "big_model_launched": False,
            "selector_work_launched": False,
            "search_launched": False,
            "status": "BLOCKED_BY_RUN045_NATURAL_KERNEL_ELIMINATION",
            "top_level_certificates_generated": 0,
            "top_level_replay_pass": 0,
            "strict_verifier": "FAIL",
            "proof_confidence_percent": 0.0,
            "run045_status": run045_result.get("status"),
            "run045_replay": scc_replay,
            "artifacts": {"run_result": str(out_dir / "run_result.json")},
        }
        _write_json(result, out_dir / "run_result.json")
        return result

    source_manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    source_manifest = _load_json(source_manifest_path)
    graph_path = Path(run_cfg.get("proof_graph") or _resolve_manifest_artifact(source_manifest, "proof_dependency_graph_frozen", manifest_path=source_manifest_path))
    trace_path = Path(run_cfg.get("accepted_action_trace") or _resolve_manifest_artifact(source_manifest, "accepted_action_trace", manifest_path=source_manifest_path))
    s3_path = Path(run_cfg.get("s3_debt_certificates") or _resolve_manifest_artifact(source_manifest, "s3_debt_certificates", manifest_path=source_manifest_path))
    s4_path = Path(run_cfg.get("parent_transition_certificates") or _resolve_manifest_artifact(source_manifest, "parent_transition_certificates", manifest_path=source_manifest_path))
    s6_path = Path(run_cfg.get("s6_lemma_certificates") or _resolve_manifest_artifact(source_manifest, "s6_lemma_certificates", manifest_path=source_manifest_path))
    parent_residual_path = Path(run_cfg.get("parent_residual_certificate") or _resolve_manifest_artifact(source_manifest, "parent_residual_certificate", manifest_path=source_manifest_path))

    graph = _load_json(graph_path)
    trace_rows = _load_jsonl(trace_path)
    s3_rows = _load_jsonl(s3_path)
    s4_rows = _load_jsonl(s4_path)
    s6_rows = _load_jsonl(s6_path)
    parent_residual = _load_json(parent_residual_path)
    manifest_hashes = _manifest_hashes(source_manifest)
    manifest_hashes["scc_guarded_ranking_certificate"] = _sha256(run045_cert_path)
    manifest_hashes["parent_residual_certificate"] = _sha256(parent_residual_path)

    context = build_replay_context(
        graph=graph,
        s3_rows=s3_rows,
        s4_rows=s4_rows,
        s6_rows=s6_rows,
        parent_residual_certificate=parent_residual,
        scc_guarded_ranking_certificate=scc_cert,
        manifest_hashes=manifest_hashes,
    )
    certificates, build_failures = build_top_level_certificates_after_hardening(graph, context=context, run_id=RUN_ID)
    patched_graph = attach_top_level_certificates(graph, certificates)
    patched_context = {**context, "graph": patched_graph}
    replay_report = replay_top_level_certificates(certificates, graph=patched_graph, context=patched_context, run_id=RUN_ID)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph, replay_context=patched_context)

    certs_out = out_dir / "top_level_certificates.jsonl"
    replay_report_out = out_dir / "top_level_replay_report.json"
    graph_out = out_dir / "proof_dependency_graph_frozen.json"
    trace_out = out_dir / "accepted_action_trace.jsonl"
    s3_out = out_dir / "s3_debt_certificates.jsonl"
    s4_out = out_dir / "parent_transition_certificates.jsonl"
    s6_out = out_dir / "s6_lemma_certificates.jsonl"
    parent_residual_out = out_dir / "parent_residual_certificate.json"
    scc_out = out_dir / "scc_guarded_ranking_certificate.json"
    final_proof_out = out_dir / "final_proof_object.json"
    manifest_out = out_dir / "proof_manifest.json"
    strict_out = out_dir / "strict_replay_result.json"
    root_replay_out = out_dir / "root_manifest_replay_result.json"

    write_jsonl(certs_out, certificates)
    _write_json(replay_report, replay_report_out)
    _write_json(patched_graph, graph_out)
    write_jsonl(trace_out, trace_rows)
    write_jsonl(s3_out, s3_rows)
    write_jsonl(s4_out, s4_rows)
    write_jsonl(s6_out, s6_rows)
    _write_json(parent_residual, parent_residual_out)
    _write_json(scc_cert, scc_out)
    _write_json(proof, final_proof_out)

    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "s3_debt_certificates": s3_out,
        "parent_transition_certificates": s4_out,
        "s6_lemma_certificates": s6_out,
        "parent_residual_certificate": parent_residual_out,
        "scc_guarded_ranking_certificate": scc_out,
        "top_level_certificates": certs_out,
        "top_level_replay_report": replay_report_out,
        "final_proof_object": final_proof_out,
    }
    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {
            "strict_verifier": proof.get("verifier_status"),
            "audit_status": "PASS" if proof.get("verifier_status") == "PASS" and replay_report.get("all_pass") else "AUDIT_FAIL",
            "proof_confidence_percent": 100.0 if proof.get("verifier_status") == "PASS" and replay_report.get("all_pass") else 0.0,
        },
        "artifacts": [_artifact_entry(name, path, out_dir) for name, path in artifacts.items()],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_guarded_domain.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_guarded_scc_ranking.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_guarded_viability_kernel.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_natural_viability_kernel.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run044.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run045.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run046.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_top_level_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_verifier.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/replay_strict_proof.py"),
        ],
        "clean_clone_replay": {
            "command": f"python -m collatz_lab.replay_strict_proof --manifest reports/runs/{RUN_ID}/proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    _write_json(manifest, manifest_out)
    strict = replay_manifest(manifest_out, out=strict_out)
    status = "PASS" if strict.get("strict_verifier") == "PASS" and replay_report.get("all_pass") else "FAIL"
    if bool(run_cfg.get("write_repo_replay_bundle", True)) and status == "PASS":
        _write_repo_replay_bundle(manifest, artifacts)
        root_replay = replay_manifest(REPO_ROOT / "proof_manifest.json", out=root_replay_out)
    else:
        root_replay = strict

    result = {
        "schema": "collatz_lab.run046_top_level_after_natural_kernel_elimination",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "status": status,
        "top_level_certificates_generated": len(certificates),
        "top_level_replay_pass": int(replay_report.get("replay_pass_count", 0) or 0),
        "strict_verifier": strict.get("strict_verifier"),
        "proof_confidence_percent": strict.get("proof_confidence_percent"),
        "hash_failure_count": strict.get("hash_failure_count", 0),
        "clean_manifest_replay": {
            "strict_verifier": root_replay.get("strict_verifier"),
            "hash_failure_count": root_replay.get("hash_failure_count"),
            "proof_confidence_percent": root_replay.get("proof_confidence_percent"),
        },
        "top_level_certificate_failures": build_failures + [
            {"certificate": name, **row}
            for name, row in replay_report.get("results", {}).items()
            if not row.get("accepted")
        ],
        "artifacts": {
            "top_level_certificates": str(certs_out),
            "top_level_replay_report": str(replay_report_out),
            "root_manifest_replay_result": str(root_replay_out),
            "final_proof_object": str(final_proof_out),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)) and status == "PASS":
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run046_run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_top_level_after_natural_kernel_elimination(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
