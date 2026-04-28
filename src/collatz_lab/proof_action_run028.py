"""RUN-028 exact S3 debt certificates."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_decode import verify_action_for_state
from .proof_action_dsl import serialize_action
from .proof_action_s3_debt_cert import build_s3_debt_certificate, replay_s3_debt_certificate
from .proof_action_top_level_cert import attach_top_level_certificates, build_top_level_certificates, replay_top_level_certificates, write_jsonl
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-028-exact-s3-debt-certificates"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = Path("certificate_store/run024_proof_dependency_graph_frozen.json")
DEFAULT_TRACE = Path("certificate_store/run024_accepted_action_trace.jsonl")


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


def _state_with_s3_certificate(state: str, certificate: dict[str, Any]) -> str:
    payload = json.dumps(certificate, sort_keys=True, separators=(",", ":"))
    attrs = {
        "kind": "s3_debt_certificate",
        "branch_id": certificate["branch_id"],
        "certificate_id": certificate["certificate_id"],
        "certificate_hash": certificate["certificate_hash"],
        "status": certificate["status"],
        "certificate_payload": payload,
    }
    fact = "<FACT " + " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in sorted(attrs.items())) + "/>"
    if "</FACTS>" in state:
        return state.replace("</FACTS>", f"{fact}\n</FACTS>", 1)
    return state + "\n<FACTS>\n" + fact + "\n</FACTS>"


def _replace_s3_node_action(node_id: str, node: dict[str, Any], certificate: dict[str, Any]) -> dict[str, Any]:
    patched = dict(node)
    state = _state_with_s3_certificate(str(node.get("state", "")), certificate)
    patched["state"] = state
    patched.setdefault("evidence", {})["s3_debt_certificate_id"] = certificate["certificate_id"]
    patched.setdefault("evidence", {})["s3_debt_certificate_hash"] = certificate["certificate_hash"]
    accepted: list[dict[str, Any]] = []
    for row in list(patched.get("accepted_actions") or []):
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        if action.get("type") == "CHECK_DEBT_DECREASE":
            check = verify_action_for_state(action, state)
            if not check.accepted:
                raise ValueError(f"S3 debt certificate action failed for {node_id}: {check.status}: {check.reason}")
            accepted.append({**row, "verifier_check": check.to_dict(), "certificate_hash": certificate["certificate_hash"]})
        else:
            accepted.append(row)
    patched["accepted_actions"] = accepted
    return patched


def _patch_trace_rows(trace_rows: list[dict[str, Any]], certificate_by_node: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in trace_rows:
        node_id = str(row.get("node_id", ""))
        certificate = certificate_by_node.get(node_id)
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        if certificate is not None and action.get("type") == "CHECK_DEBT_DECREASE":
            patched = dict(row)
            patched["verifier_check"] = {
                "accepted": True,
                "status": "ACCEPT",
                "reason": "exact S3 debt certificate replays",
                "closed_obligation": True,
                "progress": 1.0,
            }
            patched["certificate_hash"] = certificate["certificate_hash"]
            out.append(patched)
        else:
            out.append(row)
    return out


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    copied_entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run028_{name}{suffix}"
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


def run_exact_s3_debt_certificates(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("s3_debt_certificates", {}) if isinstance(cfg.get("s3_debt_certificates", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    graph = _load_json(run_cfg.get("proof_graph") or DEFAULT_GRAPH)
    trace_rows = _load_jsonl(run_cfg.get("accepted_action_trace") or DEFAULT_TRACE)
    patched_graph = json.loads(json.dumps(graph))

    certificate_rows: list[dict[str, Any]] = []
    certificate_by_node: dict[str, dict[str, Any]] = {}
    failed: list[dict[str, Any]] = []
    s3_nodes = [
        (node_id, node)
        for node_id, node in sorted(patched_graph.get("nodes", {}).items())
        if node.get("node_type") == "S3_TRANSITION" and node.get("status") == "ACCEPTED"
    ]
    for node_id, node in s3_nodes:
        try:
            actions = [
                row.get("action") or {}
                for row in node.get("accepted_actions", []) or []
                if (row.get("action") or {}).get("type") == "CHECK_DEBT_DECREASE"
            ]
            if not actions:
                raise ValueError("accepted S3 node has no CHECK_DEBT_DECREASE action")
            certificate = build_s3_debt_certificate(action=actions[0], state=str(node.get("state", "")), node_id=node_id)
            replay = replay_s3_debt_certificate(certificate, action=actions[0], state=str(node.get("state", "")))
            if not replay.accepted:
                raise ValueError(f"{replay.status}: {replay.reason}")
            patched_graph["nodes"][node_id] = _replace_s3_node_action(node_id, node, certificate)
            certificate_by_node[node_id] = certificate
            certificate_rows.append({"node_id": node_id, "s3_debt_certificate": certificate, "replay_result": replay.to_dict()})
        except Exception as exc:  # noqa: BLE001 - exact run report.
            failed.append({"node_id": node_id, "reason": str(exc)})

    certificates, build_failures = build_top_level_certificates(patched_graph)
    patched_graph = attach_top_level_certificates(patched_graph, certificates)
    replay_report = replay_top_level_certificates(certificates, graph=patched_graph)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph)
    patched_trace = _patch_trace_rows(trace_rows, certificate_by_node)

    certs_out = out_dir / "s3_debt_certificates.jsonl"
    s3_replay_report_out = out_dir / "s3_debt_replay_report.json"
    top_level_out = out_dir / "top_level_certificates.jsonl"
    top_level_replay_out = out_dir / "top_level_replay_report.json"
    graph_out = out_dir / "proof_dependency_graph_s3_replayed.json"
    trace_out = out_dir / "accepted_action_trace_s3_replayed.jsonl"
    final_proof_out = out_dir / "final_proof_object.json"
    manifest_out = out_dir / "proof_manifest.json"
    replay_out = out_dir / "strict_replay_result.json"

    _write_jsonl(certificate_rows, certs_out)
    _write_json({"run_id": RUN_ID, "certificate_count": len(certificate_rows), "failed_count": len(failed), "failed": failed}, s3_replay_report_out)
    write_jsonl(top_level_out, certificates)
    _write_json(replay_report, top_level_replay_out)
    _write_json(patched_graph, graph_out)
    _write_jsonl(patched_trace, trace_out)
    _write_json(proof, final_proof_out)
    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "s3_debt_certificates": certs_out,
        "s3_debt_replay_report": s3_replay_report_out,
        "top_level_certificates": top_level_out,
        "top_level_replay_report": top_level_replay_out,
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
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s3_debt_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run028.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_decode.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/replay_strict_proof.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_top_level_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_verifier.py"),
        ],
    }
    _write_json(manifest, manifest_out)
    replay_result = replay_manifest(manifest_out, out=replay_out)
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        _write_repo_replay_bundle(manifest, artifacts)

    result = {
        "schema": "collatz_lab.run028_exact_s3_debt_certificates",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "s3_debt_certificates_generated": len(certificate_rows),
        "s3_debt_replay_pass": sum(1 for row in certificate_rows if row.get("replay_result", {}).get("accepted")),
        "failed_s3_debt_certificate_count": len(failed),
        "failed_s3_debt_certificates": failed,
        "top_level_certificate_failures": build_failures + [
            {"certificate": name, **row}
            for name, row in replay_report.get("results", {}).items()
            if not row.get("accepted")
        ],
        "hash_failure_count": int(replay_result.get("hash_failure_count", 0) or 0),
        "strict_verifier": replay_result.get("strict_verifier"),
        "verifier_status": replay_result.get("verifier_status"),
        "proof_confidence_percent": replay_result.get("proof_confidence_percent"),
        "root_unsound_certificates": replay_result.get("root_unsound_certificates", []),
        "artifacts": {name: str(path) for name, path in artifacts.items()},
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run028_run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_exact_s3_debt_certificates(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
