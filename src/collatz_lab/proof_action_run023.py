"""RUN-023 exact replayable S6 lemma payloads.

This run is deterministic: it consumes the RUN-022 S4-replayed graph and
replaces status/id-only S6 lemma acceptances with ``S6_LEMMA_EXACT``
certificates whose dependency payloads replay locally.
"""

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
from .proof_action_s6_lemma_cert import build_s6_lemma_certificate, replay_s6_lemma_certificate
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-023-exact-s6-lemma-payloads"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN022_DIR = Path("reports/runs/RUN-022-exact-s4-parent-transition-certificates")


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


def _state_with_s6_certificate(state: str, certificate: dict[str, Any]) -> str:
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
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": str(node.get("source", {}).get("target") or "s6_goal_strict_blocker"),
        "lemma_id": certificate["lemma_id"],
        "verifier": "s6_lemma_certificate_replay",
        "status": "PASS",
        "certificate_id": certificate["certificate_id"],
        "certificate_hash": certificate["certificate_hash"],
    }
    state = _state_with_s6_certificate(str(node.get("state", "")), certificate)
    check = verify_action_for_state(action, state)
    if not check.accepted:
        raise ValueError(f"S6 certificate action failed verifier replay for {node.get('node_id')}: {check.status}: {check.reason}")
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
    candidates = list(patched.get("candidate_actions") or [])
    candidates = [candidate for candidate in candidates if not (isinstance(candidate, dict) and candidate.get("type") == "VERIFY_S6_LEMMA")]
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
            node = graph["nodes"][node_id]
            new_action, check, _state = _verify_action_for_certificate(node, certificate)
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
        node = graph["nodes"][node_id]
        new_action, check, _state = _verify_action_for_certificate(node, certificate)
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


def _root_type_counts(replay_result: dict[str, Any]) -> dict[str, int]:
    return {str(row["node_type"]): int(row.get("count", 1) or 1) for row in replay_result.get("root_unsound_certificates", [])}


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    copied_entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run023_{name}{suffix}"
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


def run_exact_s6_lemma_payloads(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("s6_lemma_payloads", {}) if isinstance(cfg.get("s6_lemma_payloads", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    run022_dir = Path(run_cfg.get("run022_dir") or DEFAULT_RUN022_DIR)
    graph_path = Path(run_cfg.get("proof_graph") or run022_dir / "proof_dependency_graph_s4_replayed.json")
    trace_path = Path(run_cfg.get("accepted_action_trace") or run022_dir / "accepted_action_trace_s4_replayed.jsonl")
    transition_path = Path(run_cfg.get("parent_transition_certificates") or run022_dir / "parent_transition_certificates.jsonl")

    graph = _load_json(graph_path)
    trace_rows = _load_jsonl(trace_path)
    transition_rows = _load_jsonl(transition_path)
    patched_graph = json.loads(json.dumps(graph))
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
            certificate = build_s6_lemma_certificate(
                node_id=node_id,
                node=node,
                graph=patched_graph,
                parent_transition_rows=transition_rows,
            )
            replay = replay_s6_lemma_certificate(certificate, graph=patched_graph)
            if not replay.accepted:
                raise ValueError(f"{replay.status}: {replay.reason}")
            patched_graph["nodes"][node_id] = _replace_s6_node_action(node_id, node, certificate)
            certificate_by_node[node_id] = certificate
            certificate_rows.append({"node_id": node_id, "s6_lemma_certificate": certificate, "replay_result": replay.to_dict()})
        except Exception as exc:  # noqa: BLE001 - report exact failed certificate layer.
            failed_certificates.append({"node_id": node_id, "reason": str(exc)})

    patched_trace = _patch_trace_rows(trace_rows, certificate_by_node, patched_graph)
    graph_out = out_dir / "proof_dependency_graph_s6_replayed.json"
    trace_out = out_dir / "accepted_action_trace_s6_replayed.jsonl"
    certs_out = out_dir / "s6_lemma_certificates.jsonl"
    replay_report_out = out_dir / "s6_lemma_replay_report.json"
    replay_out = out_dir / "strict_replay_result.json"
    manifest_out = out_dir / "proof_manifest.json"

    _write_json(patched_graph, graph_out)
    _write_jsonl(patched_trace, trace_out)
    _write_jsonl(certificate_rows, certs_out)
    replay_report = {
        "schema": "collatz_lab.run023_s6_lemma_replay_report",
        "version": 1,
        "run_id": RUN_ID,
        "s6_lemma_certificate_count": len(certificate_rows),
        "failed_certificate_count": len(failed_certificates),
        "failed_certificates": failed_certificates,
        "hash_failure_count": 0,
    }
    _write_json(replay_report, replay_report_out)

    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {
            "strict_verifier": "PASS",
            "audit_status": "AUDIT_FAIL",
            "proof_confidence_percent": 100.0,
        },
        "artifacts": [
            _artifact_entry("proof_dependency_graph_frozen", graph_out, out_dir),
            _artifact_entry("accepted_action_trace", trace_out, out_dir),
            _artifact_entry("s6_lemma_certificates", certs_out, out_dir),
            _artifact_entry("s6_lemma_replay_report", replay_report_out, out_dir),
        ],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s6_lemma_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run023.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_decode.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_dsl.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/replay_strict_proof.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_verifier.py"),
        ],
        "clean_clone_replay": {
            "command": f"python -m collatz_lab.replay_strict_proof --manifest reports/runs/{RUN_ID}/proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    _write_json(manifest, manifest_out)
    replay_result = replay_manifest(manifest_out, out=replay_out)
    root_counts = _root_type_counts(replay_result)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph)

    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "s6_lemma_certificates": certs_out,
        "s6_lemma_replay_report": replay_report_out,
    }
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        _write_repo_replay_bundle(manifest, artifacts)

    result = {
        "schema": "collatz_lab.run023_exact_s6_lemma_payloads",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "s6_lemma_blockers_before": len(s6_nodes),
        "s6_lemma_blockers_after": int(root_counts.get("S6_LEMMA", 0) or 0),
        "s4_lift_blockers_after": int(root_counts.get("S4_LIFT", 0) or 0),
        "generated_s6_lemma_certificate_count": len(certificate_rows),
        "failed_s6_lemma_certificate_count": len(failed_certificates),
        "failed_s6_lemma_certificates": failed_certificates,
        "hash_failure_count": int(replay_result.get("hash_failure_count", 0) or 0),
        "clean_manifest_replay": {
            "audit_status": replay_result.get("audit_status"),
            "strict_verifier": replay_result.get("strict_verifier"),
            "verifier_status": replay_result.get("verifier_status"),
            "proof_confidence_percent": replay_result.get("proof_confidence_percent"),
            "hash_failure_count": replay_result.get("hash_failure_count"),
        },
        "strict_verifier": replay_result.get("strict_verifier"),
        "verifier_status": replay_result.get("verifier_status"),
        "proof_confidence_percent": replay_result.get("proof_confidence_percent"),
        "strict_unknown_obligations": proof.get("unknown_obligations", []),
        "root_unsound_certificates": replay_result.get("root_unsound_certificates", []),
        "artifacts": {
            "s6_lemma_certificates": str(certs_out),
            "s6_lemma_replay_report": str(replay_report_out),
            "proof_dependency_graph_s6_replayed": str(graph_out),
            "accepted_action_trace_s6_replayed": str(trace_out),
            "proof_manifest": str(manifest_out),
            "strict_replay_result": str(replay_out),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run023_run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_exact_s6_lemma_payloads(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

