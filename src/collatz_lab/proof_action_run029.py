"""RUN-029 refresh S6 lemma payloads after S3 hardening.

This run consumes the RUN-028 graph and exact S3 certificates, then rebuilds
the 28 S6 lemma certificates so their S3 dependencies point at
``S3_DEBT_EXACT`` payloads instead of pre-hardening graph snapshots.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

from .proof_action_decode import verify_action_for_state
from .proof_action_dsl import serialize_action
from .proof_action_s3_debt_cert import replay_s3_debt_certificate
from .proof_action_s6_lemma_cert import (
    build_s6_lemma_certificate_from_exact_dependencies,
    replay_s6_lemma_certificate,
)
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-029-refresh-s6-lemma-payloads-after-s3-hardening"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = Path("certificate_store/run028_proof_dependency_graph_frozen.json")
DEFAULT_TRACE = Path("certificate_store/run028_accepted_action_trace.jsonl")
DEFAULT_S3_CERTS = Path("certificate_store/run028_s3_debt_certificates.jsonl")
DEFAULT_S4_CERTS = Path("reports/runs/RUN-022-exact-s4-parent-transition-certificates/parent_transition_certificates.jsonl")


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


def _root_type_counts(replay_result: dict[str, Any]) -> dict[str, int]:
    return {str(row["node_type"]): int(row.get("count", 1) or 1) for row in replay_result.get("root_unsound_certificates", [])}


def _state_with_s6_certificate(state: str, certificate: dict[str, Any]) -> str:
    state = re.sub(r"\n?<FACT [^>]*kind=\"s6_lemma_certificate\"[^>]*/>", "", state)
    payload = json.dumps(certificate, sort_keys=True, separators=(",", ":"))
    attrs = {
        "kind": "s6_lemma_certificate",
        "lemma_id": certificate["lemma_id"],
        "blocker_id": certificate["blocker_id"],
        "certificate_id": certificate["certificate_id"],
        "certificate_hash": certificate["certificate_hash"],
        "status": certificate["status"],
        "certificate_payload": payload,
    }
    fact = "<FACT " + " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in sorted(attrs.items())) + "/>"
    if "</FACTS>" in state:
        return state.replace("</FACTS>", f"{fact}\n</FACTS>", 1)
    return state + "\n<FACTS>\n" + fact + "\n</FACTS>"


def _verify_action_for_certificate(node: dict[str, Any], certificate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
    source = node.get("source") if isinstance(node.get("source"), dict) else {}
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": str(source.get("target") or "s6_goal_strict_blocker"),
        "lemma_id": certificate["lemma_id"],
        "verifier": "s6_lemma_certificate_replay",
        "status": "PASS",
        "certificate_id": certificate["certificate_id"],
        "certificate_hash": certificate["certificate_hash"],
    }
    state = _state_with_s6_certificate(str(node.get("state", "")), certificate)
    check = verify_action_for_state(action, state)
    if not check.accepted:
        raise ValueError(f"S6 RUN-029 certificate action failed verifier replay: {check.status}: {check.reason}")
    return action, check.to_dict(), state


def _replace_s6_node_action(node_id: str, node: dict[str, Any], certificate: dict[str, Any]) -> dict[str, Any]:
    patched = dict(node)
    action, check, state = _verify_action_for_certificate(patched, certificate)
    action_text = serialize_action(action)
    patched["state"] = state
    patched.setdefault("evidence", {})["s6_lemma_certificate_id"] = certificate["certificate_id"]
    patched.setdefault("evidence", {})["s6_lemma_certificate_hash"] = certificate["certificate_hash"]
    patched["accepted_action_text"] = action_text
    patched["status"] = "ACCEPTED"
    replacement = {
        "node_id": node_id,
        "node_type": patched.get("node_type"),
        "action": action,
        "action_text": action_text,
        "verifier_check": check,
        "certificate_hash": certificate["certificate_hash"],
    }
    accepted: list[dict[str, Any]] = []
    replaced = False
    for row in list(patched.get("accepted_actions") or []):
        existing = row.get("action") if isinstance(row.get("action"), dict) else {}
        if existing.get("type") == "VERIFY_S6_LEMMA":
            accepted.append({**row, **replacement})
            replaced = True
        else:
            accepted.append(row)
    if not replaced:
        accepted.append(replacement)
    patched["accepted_actions"] = accepted
    candidates = [
        candidate
        for candidate in list(patched.get("candidate_actions") or [])
        if not (isinstance(candidate, dict) and candidate.get("type") == "VERIFY_S6_LEMMA")
    ]
    candidates.insert(0, action)
    patched["candidate_actions"] = candidates
    return patched


def _patch_trace_rows(trace_rows: list[dict[str, Any]], certificate_by_node: dict[str, dict[str, Any]], graph: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    emitted_nodes: set[str] = set()
    for row in trace_rows:
        node_id = str(row.get("node_id", ""))
        certificate = certificate_by_node.get(node_id)
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        if certificate is not None and action.get("type") == "VERIFY_S6_LEMMA":
            new_action, check, _state = _verify_action_for_certificate(graph["nodes"][node_id], certificate)
            patched = dict(row)
            patched["action"] = new_action
            patched["action_text"] = serialize_action(new_action)
            patched["verifier_check"] = check
            patched.setdefault("evidence", {})["s6_lemma_certificate_hash"] = certificate["certificate_hash"]
            out.append(patched)
            emitted_nodes.add(node_id)
        else:
            out.append(row)
    for node_id, certificate in certificate_by_node.items():
        if node_id in emitted_nodes:
            continue
        new_action, check, _state = _verify_action_for_certificate(graph["nodes"][node_id], certificate)
        out.append(
            {
                "node_id": node_id,
                "node_type": "S6_LEMMA",
                "action": new_action,
                "action_text": serialize_action(new_action),
                "verifier_check": check,
                "evidence": {"s6_lemma_certificate_hash": certificate["certificate_hash"]},
            }
        )
    return out


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    copied_entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run029_{name}{suffix}"
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


def run_refresh_s6_after_s3_hardening(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("s6_after_s3_hardening", {}) if isinstance(cfg.get("s6_after_s3_hardening", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    graph = _load_json(run_cfg.get("proof_graph") or DEFAULT_GRAPH)
    trace_rows = _load_jsonl(run_cfg.get("accepted_action_trace") or DEFAULT_TRACE)
    s3_rows = _load_jsonl(run_cfg.get("s3_debt_certificates") or DEFAULT_S3_CERTS)
    s4_rows = _load_jsonl(run_cfg.get("parent_transition_certificates") or DEFAULT_S4_CERTS)
    patched_graph = json.loads(json.dumps(graph))

    s3_replay_failures = []
    for row in s3_rows:
        certificate = row.get("s3_debt_certificate") if isinstance(row.get("s3_debt_certificate"), dict) else {}
        replay = replay_s3_debt_certificate(certificate)
        if not replay.accepted:
            s3_replay_failures.append({"node_id": row.get("node_id"), "status": replay.status, "reason": replay.reason})

    certificate_rows: list[dict[str, Any]] = []
    certificate_by_node: dict[str, dict[str, Any]] = {}
    failed_certificates: list[dict[str, Any]] = []
    s6_nodes = [
        (node_id, node)
        for node_id, node in sorted(patched_graph.get("nodes", {}).items())
        if node.get("node_type") == "S6_LEMMA" and node.get("status") == "ACCEPTED"
    ]
    for node_id, node in s6_nodes:
        try:
            certificate = build_s6_lemma_certificate_from_exact_dependencies(
                node_id=node_id,
                node=node,
                graph=patched_graph,
                s3_debt_rows=s3_rows,
                parent_transition_rows=s4_rows,
            )
            replay = replay_s6_lemma_certificate(certificate, graph=patched_graph)
            if not replay.accepted:
                raise ValueError(f"{replay.status}: {replay.reason}: {replay.failures or []}")
            patched_graph["nodes"][node_id] = _replace_s6_node_action(node_id, node, certificate)
            certificate_by_node[node_id] = certificate
            certificate_rows.append({"node_id": node_id, "s6_lemma_certificate": certificate, "replay_result": replay.to_dict()})
        except Exception as exc:  # noqa: BLE001 - exact failed layer belongs in report.
            failed_certificates.append({"node_id": node_id, "reason": str(exc)})

    patched_trace = _patch_trace_rows(trace_rows, certificate_by_node, patched_graph)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph)
    graph_out = out_dir / "proof_dependency_graph_s6_refreshed.json"
    trace_out = out_dir / "accepted_action_trace_s6_refreshed.jsonl"
    certs_out = out_dir / "s6_lemma_certificates.jsonl"
    replay_report_out = out_dir / "s6_lemma_replay_report.json"
    s3_replay_report_out = out_dir / "s3_exact_dependency_replay_report.json"
    s3_certs_out = out_dir / "s3_debt_certificates.jsonl"
    s4_certs_out = out_dir / "parent_transition_certificates.jsonl"
    final_proof_out = out_dir / "final_proof_object.json"
    manifest_out = out_dir / "proof_manifest.json"
    replay_out = out_dir / "strict_replay_result.json"
    _write_json(patched_graph, graph_out)
    _write_jsonl(patched_trace, trace_out)
    _write_jsonl(certificate_rows, certs_out)
    _write_jsonl(s3_rows, s3_certs_out)
    _write_jsonl(s4_rows, s4_certs_out)
    _write_json(proof, final_proof_out)
    replay_report = {
        "schema": "collatz_lab.run029_s6_lemma_replay_report",
        "version": 1,
        "run_id": RUN_ID,
        "s6_lemma_certificate_count": len(certificate_rows),
        "s6_lemma_replay_pass": sum(1 for row in certificate_rows if row.get("replay_result", {}).get("accepted")),
        "failed_certificate_count": len(failed_certificates),
        "failed_certificates": failed_certificates,
        "hash_failure_count": 0,
    }
    _write_json(replay_report, replay_report_out)
    _write_json(
        {
            "schema": "collatz_lab.run029_s3_exact_dependency_replay_report",
            "version": 1,
            "run_id": RUN_ID,
            "s3_exact_certificate_count": len(s3_rows),
            "s3_exact_replay_pass": len(s3_rows) - len(s3_replay_failures),
            "failed": s3_replay_failures,
        },
        s3_replay_report_out,
    )

    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "s6_lemma_certificates": certs_out,
        "s6_lemma_replay_report": replay_report_out,
        "s3_debt_certificates": s3_certs_out,
        "s3_exact_dependency_replay_report": s3_replay_report_out,
        "parent_transition_certificates": s4_certs_out,
        "final_proof_object": final_proof_out,
    }
    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {
            "strict_verifier": proof.get("verifier_status"),
            "audit_status": "AUDIT_FAIL",
            "proof_confidence_percent": 0.0,
        },
        "artifacts": [_artifact_entry(name, path, out_dir) for name, path in artifacts.items()],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s6_lemma_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run029.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_decode.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s3_debt_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_parent_transition_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/replay_strict_proof.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_verifier.py"),
        ],
    }
    _write_json(manifest, manifest_out)
    replay_result = replay_manifest(manifest_out, out=replay_out)
    root_counts = _root_type_counts(replay_result)
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        _write_repo_replay_bundle(manifest, artifacts)

    result = {
        "schema": "collatz_lab.run029_refresh_s6_lemma_payloads_after_s3_hardening",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "s6_lemma_blockers_before": len(s6_nodes),
        "s6_lemma_blockers_after": int(root_counts.get("S6_LEMMA", 0) or 0),
        "s3_exact_replay_pass": len(s3_rows) - len(s3_replay_failures),
        "s3_exact_certificate_count": len(s3_rows),
        "s4_exact_certificate_count": len(s4_rows),
        "generated_s6_lemma_certificate_count": len(certificate_rows),
        "s6_lemma_replay_pass": sum(1 for row in certificate_rows if row.get("replay_result", {}).get("accepted")),
        "failed_s6_lemma_certificate_count": len(failed_certificates),
        "failed_s6_lemma_certificates": failed_certificates,
        "hash_failure_count": int(replay_result.get("hash_failure_count", 0) or 0),
        "strict_verifier": replay_result.get("strict_verifier"),
        "verifier_status": replay_result.get("verifier_status"),
        "proof_confidence_percent": replay_result.get("proof_confidence_percent"),
        "root_unsound_certificates": replay_result.get("root_unsound_certificates", []),
        "strict_errors": replay_result.get("strict_errors", []),
        "artifacts": {name: str(path) for name, path in artifacts.items()},
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run029_run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_refresh_s6_after_s3_hardening(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
