"""RUN-034 enrich exact S4 certificates with parent-coordinate maps."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_decode import verify_action_for_state
from .proof_action_dsl import serialize_action
from .proof_action_parent_coordinate_map import (
    build_parent_coordinate_map_certificate,
    enrich_transition_certificate_with_parent_map,
    replay_parent_coordinate_map_certificate,
)
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-034-exact-s4-parent-coordinate-maps"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = Path("certificate_store/run030_proof_dependency_graph_frozen.json")
DEFAULT_TRACE = Path("certificate_store/run030_accepted_action_trace.jsonl")
DEFAULT_S3 = Path("certificate_store/run030_s3_debt_certificates.jsonl")
DEFAULT_S4 = Path("certificate_store/run030_parent_transition_certificates.jsonl")
DEFAULT_S6 = Path("certificate_store/run030_s6_lemma_certificates.jsonl")
DEFAULT_PARENT_RESIDUAL = Path("certificate_store/run030_parent_residual_certificate.json")
DEFAULT_TOP_LEVEL = Path("certificate_store/run030_top_level_certificates.jsonl")


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


def _row_certificate(row: dict[str, Any]) -> dict[str, Any]:
    cert = row.get("transition_certificate")
    if isinstance(cert, dict):
        return cert
    action = row.get("action")
    if isinstance(action, dict) and isinstance(action.get("transition_certificate"), dict):
        return action["transition_certificate"]
    return {}


def _patch_graph_s4_node(graph: dict[str, Any], row: dict[str, Any]) -> None:
    node_id = str(row.get("node_id", ""))
    node = graph.get("nodes", {}).get(node_id)
    if not isinstance(node, dict):
        return
    enriched_action = row.get("action") if isinstance(row.get("action"), dict) else {}
    state = str(node.get("state", ""))
    check = verify_action_for_state(enriched_action, state)
    if not check.accepted:
        raise ValueError(f"RUN-034 enriched S4 action failed replay for {node_id}: {check.status}: {check.reason}")
    action_text = serialize_action(enriched_action)
    patched_accepted: list[dict[str, Any]] = []
    replaced = False
    for accepted in list(node.get("accepted_actions") or []):
        action = accepted.get("action") if isinstance(accepted.get("action"), dict) else {}
        if action.get("type") == "DERIVE_PARENT_TRANSITION":
            patched_accepted.append({**accepted, "action": enriched_action, "action_text": action_text, "verifier_check": check.to_dict()})
            replaced = True
        else:
            patched_accepted.append(accepted)
    if not replaced:
        patched_accepted.append({"action": enriched_action, "action_text": action_text, "verifier_check": check.to_dict()})
    node["accepted_actions"] = patched_accepted
    node["accepted_action_text"] = action_text
    node.setdefault("evidence", {})["parent_coordinate_map_hash"] = _row_certificate(row).get("parent_coordinate_map_certificate_hash")
    for index, candidate in enumerate(list(node.get("candidate_actions") or [])):
        if isinstance(candidate, dict) and candidate.get("type") == "DERIVE_PARENT_TRANSITION":
            node["candidate_actions"][index] = enriched_action
            break


def _patch_trace_rows(trace_rows: list[dict[str, Any]], enriched_by_node: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    emitted: set[str] = set()
    for row in trace_rows:
        node_id = str(row.get("node_id", ""))
        replacement = enriched_by_node.get(node_id)
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        if replacement is not None and action.get("type") == "DERIVE_PARENT_TRANSITION":
            patched = dict(row)
            patched["action"] = replacement["action"]
            patched["action_text"] = serialize_action(replacement["action"])
            patched["verifier_check"] = replacement.get("verifier_check", row.get("verifier_check"))
            out.append(patched)
            emitted.add(node_id)
        else:
            out.append(row)
    for node_id, replacement in enriched_by_node.items():
        if node_id in emitted:
            continue
        out.append(
            {
                "node_id": node_id,
                "node_type": "S4_LIFT",
                "action": replacement["action"],
                "action_text": serialize_action(replacement["action"]),
                "verifier_check": replacement.get("verifier_check", {}),
            }
        )
    return out


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    copied_entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run034_{name}{suffix}"
        shutil.copy2(path, dst)
        copied_entries.append({"name": name, "path": str(dst.relative_to(REPO_ROOT)), "sha256": _sha256(dst)})
    root_manifest = {
        **manifest,
        "artifacts": copied_entries,
        "clean_clone_replay": {
            "command": "python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    _write_json(root_manifest, REPO_ROOT / "proof_manifest.json")


def _root_type_counts(replay_result: dict[str, Any]) -> dict[str, int]:
    return {str(row["node_type"]): int(row.get("count", 1) or 1) for row in replay_result.get("root_unsound_certificates", [])}


def run_s4_parent_coordinate_maps(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("s4_parent_coordinate_maps_run034", {}) if isinstance(cfg.get("s4_parent_coordinate_maps_run034", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = _load_json(run_cfg.get("proof_graph") or DEFAULT_GRAPH)
    trace_rows = _load_jsonl(run_cfg.get("accepted_action_trace") or DEFAULT_TRACE)
    s3_rows = _load_jsonl(run_cfg.get("s3_debt_certificates") or DEFAULT_S3)
    s4_rows = _load_jsonl(run_cfg.get("parent_transition_certificates") or DEFAULT_S4)
    s6_rows = _load_jsonl(run_cfg.get("s6_lemma_certificates") or DEFAULT_S6)
    parent_residual = _load_json(run_cfg.get("parent_residual_certificate") or DEFAULT_PARENT_RESIDUAL)
    top_level_rows = _load_jsonl(run_cfg.get("top_level_certificates") or DEFAULT_TOP_LEVEL)
    patched_graph = json.loads(json.dumps(graph))

    map_rows: list[dict[str, Any]] = []
    enriched_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    enriched_by_node: dict[str, dict[str, Any]] = {}
    for row in s4_rows:
        node_id = str(row.get("node_id", ""))
        state = str((graph.get("nodes") or {}).get(node_id, {}).get("state", ""))
        map_certificate = build_parent_coordinate_map_certificate(row=row, state=state)
        replay = replay_parent_coordinate_map_certificate(map_certificate)
        map_rows.append({"node_id": node_id, "parent_coordinate_map_certificate": map_certificate, "replay_result": replay.to_dict()})
        if not replay.accepted:
            failures.append({"node_id": node_id, "reason": replay.reason, "failures": replay.failures or []})
            continue
        original = _row_certificate(row)
        enriched_cert = enrich_transition_certificate_with_parent_map(original, map_certificate)
        enriched_action = dict(row.get("action") if isinstance(row.get("action"), dict) else {})
        enriched_action["transition_certificate"] = enriched_cert
        state_check = verify_action_for_state(enriched_action, state)
        if not state_check.accepted:
            failures.append({"node_id": node_id, "reason": "enriched_transition_action_replay_failed", "status": state_check.status, "detail": state_check.reason})
            continue
        enriched_row = {
            **row,
            "action": enriched_action,
            "transition_certificate": enriched_cert,
            "verifier_check": state_check.to_dict(),
            "parent_coordinate_map_certificate_hash": map_certificate["certificate_hash"],
        }
        enriched_rows.append(enriched_row)
        enriched_by_node[node_id] = enriched_row
        _patch_graph_s4_node(patched_graph, enriched_row)

    patched_trace = _patch_trace_rows(trace_rows, enriched_by_node)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph)
    graph_out = out_dir / "proof_dependency_graph_frozen.json"
    trace_out = out_dir / "accepted_action_trace.jsonl"
    map_certs_out = out_dir / "parent_coordinate_map_certificates.jsonl"
    enriched_s4_out = out_dir / "s4_transition_certificates_map_enriched.jsonl"
    replay_report_out = out_dir / "parent_coordinate_map_replay_report.json"
    s3_out = out_dir / "s3_debt_certificates.jsonl"
    s6_out = out_dir / "s6_lemma_certificates.jsonl"
    parent_residual_out = out_dir / "parent_residual_certificate.json"
    top_level_out = out_dir / "top_level_certificates.jsonl"
    final_proof_out = out_dir / "final_proof_object.json"
    manifest_out = out_dir / "proof_manifest.json"
    strict_out = out_dir / "strict_replay_result.json"

    _write_json(patched_graph, graph_out)
    _write_jsonl(patched_trace, trace_out)
    _write_jsonl(map_rows, map_certs_out)
    _write_jsonl(enriched_rows, enriched_s4_out)
    _write_jsonl(s3_rows, s3_out)
    _write_jsonl(s6_rows, s6_out)
    _write_json(parent_residual, parent_residual_out)
    _write_jsonl(top_level_rows, top_level_out)
    _write_json(proof, final_proof_out)
    replay_report = {
        "schema": "collatz_lab.parent_coordinate_map_replay_report",
        "version": 1,
        "run_id": RUN_ID,
        "certificate_count": len(map_rows),
        "replay_pass_count": sum(1 for row in map_rows if row.get("replay_result", {}).get("accepted")),
        "all_pass": not failures and len(map_rows) == len(s4_rows),
        "failures": failures,
    }
    _write_json(replay_report, replay_report_out)

    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "s3_debt_certificates": s3_out,
        "parent_transition_certificates": enriched_s4_out,
        "parent_coordinate_map_certificates": map_certs_out,
        "s6_lemma_certificates": s6_out,
        "parent_residual_certificate": parent_residual_out,
        "top_level_certificates": top_level_out,
        "final_proof_object": final_proof_out,
        "parent_coordinate_map_replay_report": replay_report_out,
    }
    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {
            "strict_verifier": "FAIL",
            "audit_status": "AUDIT_FAIL",
            "proof_confidence_percent": 0.0,
        },
        "artifacts": [_artifact_entry(name, path, out_dir) for name, path in artifacts.items()],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_parent_coordinate_map.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_parent_transition_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run034.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_decode.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s3_debt_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s6_lemma_cert.py"),
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

    root_counts = _root_type_counts(replay_result)
    result = {
        "schema": "collatz_lab.run034_exact_s4_parent_coordinate_maps",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "floating_point_certificate_used": False,
        "map_enriched_s4_certificates_generated": len(enriched_rows),
        "parent_coordinate_maps_replay_pass": replay_report["replay_pass_count"],
        "parent_coordinate_map_certificate_count": len(map_rows),
        "s4_exact_certificate_count": len(s4_rows),
        "internal_scc_edges_with_maps": _count_internal_scc_edges_with_maps(enriched_rows, run_cfg.get("scc_internal_edges")),
        "hash_failure_count": replay_result.get("hash_failure_count", 0),
        "strict_verifier": replay_result.get("strict_verifier"),
        "root_unsound_certificates": replay_result.get("root_unsound_certificates", []),
        "s4_root_failures": root_counts.get("S4_CERTIFICATE", 0),
        "failures": failures,
        "artifacts": {
            "parent_coordinate_map_certificates": str(map_certs_out),
            "s4_transition_certificates_map_enriched": str(enriched_s4_out),
            "parent_coordinate_map_replay_report": str(replay_report_out),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run034_run_result.json")
    return result


def _count_internal_scc_edges_with_maps(enriched_rows: list[dict[str, Any]], scc_internal_edges_path: str | None) -> dict[str, int]:
    if not scc_internal_edges_path:
        scc_internal_edges_path = "reports/runs/RUN-033-exact-scc-cycle-ranking-certificate/scc_internal_edges.jsonl"
    scc_path = Path(scc_internal_edges_path)
    if not scc_path.exists():
        return {"covered": 0, "total": 0}
    transition_ids_with_maps = {
        str((row.get("transition_certificate") or {}).get("transition_id", ""))
        for row in enriched_rows
        if isinstance(row.get("transition_certificate"), dict) and isinstance(row["transition_certificate"].get("parent_coordinate_map"), dict)
    }
    edges = _load_jsonl(scc_path)
    covered = sum(1 for edge in edges if str(edge.get("transition_certificate_id", "")) in transition_ids_with_maps)
    return {"covered": covered, "total": len(edges)}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_s4_parent_coordinate_maps(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
