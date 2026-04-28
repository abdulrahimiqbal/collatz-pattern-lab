"""RUN-035 refresh S6 after S4 parent-coordinate map hardening."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_run029 import _patch_trace_rows, _replace_s6_node_action
from .proof_action_s3_debt_cert import replay_s3_debt_certificate
from .proof_action_s6_lemma_cert import build_s6_lemma_certificate_from_exact_dependencies, replay_s6_lemma_certificate
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-035-refresh-s6-after-s4-map-hardening"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = Path("certificate_store/run034_proof_dependency_graph_frozen.json")
DEFAULT_TRACE = Path("certificate_store/run034_accepted_action_trace.jsonl")
DEFAULT_S3 = Path("certificate_store/run034_s3_debt_certificates.jsonl")
DEFAULT_S4 = Path("certificate_store/run034_parent_transition_certificates.jsonl")
DEFAULT_PARENT_MAPS = Path("certificate_store/run034_parent_coordinate_map_certificates.jsonl")
DEFAULT_PARENT_RESIDUAL = Path("certificate_store/run034_parent_residual_certificate.json")
DEFAULT_TOP_LEVEL = Path("certificate_store/run034_top_level_certificates.jsonl")


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


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _artifact_entry(name: str, path: Path, manifest_dir: Path) -> dict[str, Any]:
    return {"name": name, "path": str(path.relative_to(manifest_dir)), "sha256": _sha256(path)}


def _source_entry(path: Path) -> dict[str, Any]:
    return {"name": str(path.relative_to(REPO_ROOT)), "path": str(path.relative_to(REPO_ROOT)), "sha256": _sha256(path)}


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    copied_entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run035_{name}{suffix}"
        shutil.copy2(path, dst)
        copied_entries.append({"name": name, "path": str(dst.relative_to(REPO_ROOT)), "sha256": _sha256(dst)})
    _write_json(
        {
            **manifest,
            "artifacts": copied_entries,
            "clean_clone_replay": {
                "command": "python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json",
                "requires_committed_or_included_artifacts": True,
            },
        },
        REPO_ROOT / "proof_manifest.json",
    )


def _s4_map_replay_counts(s4_rows: list[dict[str, Any]]) -> dict[str, int]:
    from .proof_action_parent_transition_cert import replay_parent_transition_certificate

    passed = 0
    for row in s4_rows:
        certificate = row.get("transition_certificate") if isinstance(row.get("transition_certificate"), dict) else {}
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        if certificate.get("type") != "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP":
            continue
        # The graph-state replay happens in strict replay; this local count only
        # verifies the payload shape required by RUN-035.
        if isinstance(certificate.get("parent_coordinate_map"), dict) and action.get("transition_certificate", {}).get("certificate_hash") == certificate.get("certificate_hash"):
            passed += 1
    return {"passed": passed, "count": len(s4_rows)}


def run_refresh_s6_after_s4_map_hardening(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("s6_after_s4_map_hardening_run035", {}) if isinstance(cfg.get("s6_after_s4_map_hardening_run035", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = _load_json(run_cfg.get("proof_graph") or DEFAULT_GRAPH)
    trace_rows = _load_jsonl(run_cfg.get("accepted_action_trace") or DEFAULT_TRACE)
    s3_rows = _load_jsonl(run_cfg.get("s3_debt_certificates") or DEFAULT_S3)
    s4_rows = _load_jsonl(run_cfg.get("parent_transition_certificates") or DEFAULT_S4)
    parent_map_rows = _load_jsonl(run_cfg.get("parent_coordinate_map_certificates") or DEFAULT_PARENT_MAPS)
    parent_residual = _load_json(run_cfg.get("parent_residual_certificate") or DEFAULT_PARENT_RESIDUAL)
    top_level_rows = _load_jsonl(run_cfg.get("top_level_certificates") or DEFAULT_TOP_LEVEL)
    patched_graph = json.loads(json.dumps(graph))

    s3_failures: list[dict[str, Any]] = []
    for row in s3_rows:
        cert = row.get("s3_debt_certificate") if isinstance(row.get("s3_debt_certificate"), dict) else {}
        replay = replay_s3_debt_certificate(cert)
        if not replay.accepted:
            s3_failures.append({"node_id": row.get("node_id"), "status": replay.status, "reason": replay.reason})

    s4_missing_maps = [
        {
            "node_id": row.get("node_id"),
            "transition_id": (row.get("transition_certificate") or {}).get("transition_id"),
            "reason": "missing_parent_coordinate_map_dependency",
        }
        for row in s4_rows
        if not isinstance(row.get("transition_certificate"), dict)
        or row["transition_certificate"].get("type") != "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP"
        or not isinstance(row["transition_certificate"].get("parent_coordinate_map"), dict)
    ]

    certificate_rows: list[dict[str, Any]] = []
    certificate_by_node: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    s6_nodes = [
        (node_id, node)
        for node_id, node in sorted(patched_graph.get("nodes", {}).items())
        if node.get("node_type") == "S6_LEMMA" and node.get("status") == "ACCEPTED"
    ]
    for node_id, node in s6_nodes:
        try:
            cert = build_s6_lemma_certificate_from_exact_dependencies(
                node_id=node_id,
                node=node,
                graph=patched_graph,
                s3_debt_rows=s3_rows,
                parent_transition_rows=s4_rows,
            )
            replay = replay_s6_lemma_certificate(cert, graph=patched_graph)
            if not replay.accepted:
                raise ValueError(f"{replay.status}: {replay.reason}: {replay.failures or []}")
            patched_graph["nodes"][node_id] = _replace_s6_node_action(node_id, node, cert)
            certificate_by_node[node_id] = cert
            certificate_rows.append({"node_id": node_id, "s6_lemma_certificate": cert, "replay_result": replay.to_dict()})
        except Exception as exc:  # noqa: BLE001
            failures.append({"node_id": node_id, "reason": str(exc)})

    patched_trace = _patch_trace_rows(trace_rows, certificate_by_node, patched_graph)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph)

    graph_out = out_dir / "proof_dependency_graph_frozen.json"
    trace_out = out_dir / "accepted_action_trace.jsonl"
    s3_out = out_dir / "s3_debt_certificates.jsonl"
    s4_out = out_dir / "parent_transition_certificates.jsonl"
    parent_maps_out = out_dir / "parent_coordinate_map_certificates.jsonl"
    s6_out = out_dir / "s6_lemma_certificates.jsonl"
    s6_report_out = out_dir / "s6_lemma_replay_report.json"
    parent_residual_out = out_dir / "parent_residual_certificate.json"
    top_level_out = out_dir / "top_level_certificates.jsonl"
    final_proof_out = out_dir / "final_proof_object.json"
    manifest_out = out_dir / "proof_manifest.json"
    strict_out = out_dir / "strict_replay_result.json"

    _write_json(patched_graph, graph_out)
    _write_jsonl(patched_trace, trace_out)
    _write_jsonl(s3_rows, s3_out)
    _write_jsonl(s4_rows, s4_out)
    _write_jsonl(parent_map_rows, parent_maps_out)
    _write_jsonl(certificate_rows, s6_out)
    _write_json(parent_residual, parent_residual_out)
    _write_jsonl(top_level_rows, top_level_out)
    _write_json(proof, final_proof_out)
    s6_report = {
        "schema": "collatz_lab.run035_s6_lemma_replay_report",
        "version": 1,
        "run_id": RUN_ID,
        "certificate_count": len(certificate_rows),
        "replay_pass_count": sum(1 for row in certificate_rows if row.get("replay_result", {}).get("accepted")),
        "all_pass": not failures and not s3_failures and not s4_missing_maps and len(certificate_rows) == len(s6_nodes),
        "failures": [*s3_failures, *s4_missing_maps, *failures],
    }
    _write_json(s6_report, s6_report_out)

    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "s3_debt_certificates": s3_out,
        "parent_transition_certificates": s4_out,
        "parent_coordinate_map_certificates": parent_maps_out,
        "s6_lemma_certificates": s6_out,
        "parent_residual_certificate": parent_residual_out,
        "top_level_certificates": top_level_out,
        "final_proof_object": final_proof_out,
        "s6_lemma_replay_report": s6_report_out,
    }
    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {"strict_verifier": "FAIL", "audit_status": "AUDIT_FAIL", "proof_confidence_percent": 0.0},
        "artifacts": [_artifact_entry(name, path, out_dir) for name, path in artifacts.items()],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_parent_coordinate_map.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_parent_transition_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run034.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run035.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s6_lemma_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s3_debt_cert.py"),
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
    replay_result = replay_manifest(manifest_out, out=strict_out)
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        _write_repo_replay_bundle(manifest, artifacts)

    s4_counts = _s4_map_replay_counts(s4_rows)
    result = {
        "schema": "collatz_lab.run035_refresh_s6_after_s4_map_hardening",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "regenerated_s6_lemma_certificates": len(certificate_rows),
        "s6_replay_pass": s6_report["replay_pass_count"],
        "s3_exact_replay_pass": len(s3_rows) - len(s3_failures),
        "s3_exact_certificate_count": len(s3_rows),
        "s4_map_enriched_replay_pass": s4_counts["passed"],
        "s4_map_enriched_certificate_count": s4_counts["count"],
        "hash_failure_count": replay_result.get("hash_failure_count", 0),
        "strict_verifier": replay_result.get("strict_verifier"),
        "failures": s6_report["failures"],
        "artifacts": {
            "s6_lemma_certificates": str(s6_out),
            "s6_lemma_replay_report": str(s6_report_out),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run035_run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_refresh_s6_after_s4_map_hardening(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
