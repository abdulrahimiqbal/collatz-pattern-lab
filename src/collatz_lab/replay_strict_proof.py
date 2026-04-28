"""Replay a frozen proof manifest under the hardened strict verifier.

RUN-021 intentionally treats a closed proof-action graph as supporting evidence
only.  A strict PASS now requires replayable certificates from the manifest,
not status fields, sample checks, or generated graph closure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .proof_action_top_level_cert import build_replay_context, replay_lower_layer_context
from .proof_verifier import build_collatz_descent_theorem_candidate


REPO_ROOT = Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _resolve_path(raw_path: str, *, manifest_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    candidate = manifest_dir / path
    if candidate.exists():
        return candidate
    return REPO_ROOT / path


def _verify_hash_entries(entries: list[dict[str, Any]], *, manifest_dir: Path) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for entry in entries:
        path = _resolve_path(str(entry.get("path", "")), manifest_dir=manifest_dir)
        expected = str(entry.get("sha256", ""))
        if not path.exists():
            failures.append({"path": str(path), "reason": "missing_manifest_artifact"})
            continue
        actual = _sha256(path)
        if expected != actual:
            failures.append({"path": str(path), "reason": "sha256_mismatch", "expected": expected, "actual": actual})
    return failures


def _artifact_path(manifest: dict[str, Any], name: str, *, manifest_dir: Path) -> Path:
    for entry in manifest.get("artifacts", []):
        if entry.get("name") == name:
            return _resolve_path(str(entry["path"]), manifest_dir=manifest_dir)
    raise KeyError(f"manifest artifact not found: {name}")


def _optional_artifact_path(manifest: dict[str, Any], name: str, *, manifest_dir: Path) -> Path | None:
    for entry in manifest.get("artifacts", []):
        if entry.get("name") == name:
            return _resolve_path(str(entry["path"]), manifest_dir=manifest_dir)
    return None


def _manifest_hashes(manifest: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for entry in manifest.get("artifacts", []):
        name = str(entry.get("name", ""))
        if name:
            hashes[name] = str(entry.get("sha256", ""))
    return hashes


def _load_graph(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    graph = payload.get("graph", payload) if isinstance(payload, dict) else payload
    if not isinstance(graph, dict):
        raise ValueError(f"frozen graph artifact is not a JSON object: {path}")
    return graph


def _load_optional_jsonl_artifact(manifest: dict[str, Any], name: str, *, manifest_dir: Path) -> list[dict[str, Any]]:
    path = _optional_artifact_path(manifest, name, manifest_dir=manifest_dir)
    if path is None or not path.exists():
        return []
    return _read_jsonl(path)


def _load_optional_json_artifact(manifest: dict[str, Any], name: str, *, manifest_dir: Path) -> dict[str, Any]:
    path = _optional_artifact_path(manifest, name, manifest_dir=manifest_dir)
    if path is not None and path.exists():
        value = _read_json(path)
        return value if isinstance(value, dict) else {}
    default_parent = REPO_ROOT / "certificate_store/run019_parent_residual_certificate.json"
    if name == "parent_residual_certificate" and default_parent.exists():
        value = _read_json(default_parent)
        return value if isinstance(value, dict) else {}
    return {}


def _build_manifest_replay_context(manifest: dict[str, Any], *, manifest_dir: Path, graph: dict[str, Any]) -> dict[str, Any]:
    return build_replay_context(
        graph=graph,
        s3_rows=_load_optional_jsonl_artifact(manifest, "s3_debt_certificates", manifest_dir=manifest_dir),
        s4_rows=_load_optional_jsonl_artifact(manifest, "parent_transition_certificates", manifest_dir=manifest_dir),
        s6_rows=_load_optional_jsonl_artifact(manifest, "s6_lemma_certificates", manifest_dir=manifest_dir),
        parent_residual_certificate=_load_optional_json_artifact(manifest, "parent_residual_certificate", manifest_dir=manifest_dir),
        scc_guarded_ranking_certificate=_load_optional_json_artifact(manifest, "scc_guarded_ranking_certificate", manifest_dir=manifest_dir),
        manifest_hashes=_manifest_hashes(manifest),
    )


def _s4_graph_replay_failures(graph: dict[str, Any]) -> list[dict[str, Any]]:
    from .proof_action_decode import verify_action_for_state

    failures: list[dict[str, Any]] = []
    for node_id, node in graph.get("nodes", {}).items():
        if node.get("node_type") != "S4_LIFT" or node.get("status") != "ACCEPTED":
            continue
        for accepted in node.get("accepted_actions", []) or []:
            action = accepted.get("action") or {}
            if action.get("type") != "DERIVE_PARENT_TRANSITION":
                continue
            check = verify_action_for_state(action, str(node.get("state", "")))
            if not check.accepted:
                failures.append(
                    {
                        "node_id": node_id,
                        "status": check.status,
                        "reason": check.reason,
                    }
                )
    return failures


def _s3_graph_replay_failures(graph: dict[str, Any]) -> list[dict[str, Any]]:
    from .proof_action_decode import verify_action_for_state

    failures: list[dict[str, Any]] = []
    for node_id, node in graph.get("nodes", {}).items():
        if node.get("node_type") != "S3_TRANSITION" or node.get("status") != "ACCEPTED":
            continue
        debt_actions = [
            row.get("action") or {}
            for row in node.get("accepted_actions", []) or []
            if (row.get("action") or {}).get("type") == "CHECK_DEBT_DECREASE"
        ]
        if not debt_actions:
            failures.append(
                {
                    "node_id": node_id,
                    "status": "REJECT_MISSING_S3_DEBT_CERTIFICATE",
                    "reason": "accepted S3 transition node has no CHECK_DEBT_DECREASE action",
                }
            )
            continue
        replayed = False
        last_failure: dict[str, Any] | None = None
        for action in debt_actions:
            check = verify_action_for_state(action, str(node.get("state", "")))
            if check.accepted:
                replayed = True
                break
            last_failure = {"node_id": node_id, "status": check.status, "reason": check.reason}
        if not replayed:
            failures.append(last_failure or {"node_id": node_id, "status": "REJECT_S3_DEBT_REPLAY_FAIL", "reason": "S3 debt replay failed"})
    return failures


def _s6_graph_replay_failures(graph: dict[str, Any]) -> list[dict[str, Any]]:
    from .proof_action_decode import verify_action_for_state

    failures: list[dict[str, Any]] = []
    for node_id, node in graph.get("nodes", {}).items():
        if node.get("node_type") != "S6_LEMMA" or node.get("status") != "ACCEPTED":
            continue
        verify_actions = [
            row.get("action") or {}
            for row in node.get("accepted_actions", []) or []
            if (row.get("action") or {}).get("type") == "VERIFY_S6_LEMMA"
        ]
        if not verify_actions:
            failures.append(
                {
                    "node_id": node_id,
                    "status": "REJECT_MISSING_S6_LEMMA_CERTIFICATE",
                    "reason": "accepted S6 lemma node has no VERIFY_S6_LEMMA action",
                }
            )
            continue
        replayed = False
        last_failure: dict[str, Any] | None = None
        for action in verify_actions:
            if not action.get("certificate_id") or not action.get("certificate_hash"):
                last_failure = {
                    "node_id": node_id,
                    "status": "REJECT_S6_LEMMA_STATUS_ONLY",
                    "reason": "VERIFY_S6_LEMMA action is status/id-only",
                }
                continue
            check = verify_action_for_state(action, str(node.get("state", "")))
            if check.accepted:
                replayed = True
                break
            last_failure = {"node_id": node_id, "status": check.status, "reason": check.reason}
        if not replayed:
            failures.append(last_failure or {"node_id": node_id, "status": "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "reason": "S6 lemma replay failed"})
    return failures


def _root_unsound_certificates(
    trace_rows: list[dict[str, Any]],
    proof: dict[str, Any],
    graph: dict[str, Any],
    *,
    replay_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    roots: list[dict[str, Any]] = []
    derive_rows = [
        row
        for row in trace_rows
        if (row.get("action") or {}).get("type") == "DERIVE_PARENT_TRANSITION"
        and "transition_certificate" not in (row.get("action") or {})
    ]
    sample_rows = [
        row
        for row in trace_rows
        if (row.get("action") or {}).get("type") == "DERIVE_PARENT_TRANSITION"
        and "sample" in str((row.get("verifier_check") or {}).get("reason", "")).lower()
    ]
    if derive_rows or sample_rows:
        roots.append(
            {
                "node_type": "S4_LIFT",
                "count": len({row.get("node_id", index) for index, row in enumerate(derive_rows + sample_rows)}),
                "reason": "sample-only transition certificate",
                "required_fix": "attach and replay an exact HIGH_PARENT_SUCCESSOR_EXACT symbolic parent-transition payload",
            }
        )
    s3_replay_failures = _s3_graph_replay_failures(graph)
    if s3_replay_failures:
        roots.append(
            {
                "node_type": "S3_DEBT",
                "count": len(s3_replay_failures),
                "reason": "S3 debt certificate replay failed",
                "required_fix": "replace exact_congruence_passed/local_descent_passed booleans with replayable S3_DEBT_EXACT certificates",
                "examples": s3_replay_failures[:5],
            }
        )

    s4_replay_failures = _s4_graph_replay_failures(graph)
    if s4_replay_failures and not any(row["node_type"] == "S4_LIFT" for row in roots):
        roots.append(
            {
                "node_type": "S4_LIFT",
                "count": len(s4_replay_failures),
                "reason": "parent-transition certificate replay failed",
                "required_fix": "regenerate exact HIGH_PARENT_SUCCESSOR_EXACT payloads and replay them from graph states",
                "examples": s4_replay_failures[:5],
            }
        )

    s6_replay_failures = _s6_graph_replay_failures(graph)
    if s6_replay_failures:
        roots.append(
            {
                "node_type": "S6_LEMMA",
                "count": len(s6_replay_failures),
                "reason": "status-id lemma acceptance",
                "required_fix": "replace status/certificate identifiers with a replayable S6 lemma proof_payload",
                "examples": s6_replay_failures[:5],
            }
        )

    lower = replay_lower_layer_context(replay_context)
    lower_failures = list(lower.get("failures") or [])
    if lower_failures:
        by_layer: dict[str, list[dict[str, Any]]] = {}
        for failure in lower_failures:
            layer = str(failure.get("layer") or "")
            if not layer:
                text = json.dumps(failure, sort_keys=True)
                if "s3" in text.lower():
                    layer = "S3"
                elif "s4" in text.lower() or "transition" in text.lower():
                    layer = "S4"
                elif "s6" in text.lower():
                    layer = "S6"
                elif "parent_residual" in text.lower():
                    layer = "PARENT_RESIDUAL"
                else:
                    layer = "LOWER_LAYER"
            by_layer.setdefault(layer, []).append(failure)
        for layer, failures in sorted(by_layer.items()):
            roots.append(
                {
                    "node_type": f"{layer}_CERTIFICATE",
                    "count": len(failures),
                    "reason": "lower-layer certificate replay/count check failed",
                    "required_fix": "restore the exact manifest-backed certificate rows or regenerate the dependent top-level certificate",
                    "examples": failures[:5],
                }
            )

    missing_top_level = [
        row
        for row in proof.get("unknown_obligations", [])
        if str(row.get("obligation_id", "")).startswith("top_level:")
    ]
    if missing_top_level:
        roots.append(
            {
                "node_type": "STRICT_THEOREM_TOP_LEVEL",
                "count": len(missing_top_level),
                "reason": "one or more top-level theorem certificates do not replay",
                "required_fix": "provide the exact missing replayable top-level theorem certificate(s)",
                "missing": missing_top_level,
            }
        )
    return roots


def _source_run_accounting(manifest: dict[str, Any]) -> dict[str, Any]:
    source = manifest.get("source_run_accounting", {})
    strict_status = str(source.get("strict_verifier", source.get("verifier_status", "")))
    audit_status = str(source.get("audit_status", ""))
    if strict_status == "PASS" and audit_status not in {"PASS", "AUDIT_PASS"}:
        return {
            **source,
            "verifier_status": "UNSOUND_PASS",
            "proof_confidence_percent": 0.0,
            "run021_reason": "strict verifier PASS was downgraded because RUN-020 audit failed",
        }
    return dict(source)


def replay_manifest(manifest_path: str | Path, *, out: str | Path | None = None) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest_dir = manifest_path.parent
    manifest = _read_json(manifest_path)
    hash_failures = _verify_hash_entries(manifest.get("artifacts", []) + manifest.get("source_files", []), manifest_dir=manifest_dir)

    graph = _load_graph(_artifact_path(manifest, "proof_dependency_graph_frozen", manifest_dir=manifest_dir))
    trace_rows = _read_jsonl(_artifact_path(manifest, "accepted_action_trace", manifest_dir=manifest_dir))
    replay_context = _build_manifest_replay_context(manifest, manifest_dir=manifest_dir, graph=graph)
    proof = build_collatz_descent_theorem_candidate(proof_graph=graph, replay_context=replay_context)
    roots = _root_unsound_certificates(trace_rows, proof, graph, replay_context=replay_context)
    if hash_failures:
        roots.append(
            {
                "node_type": "REPRODUCTION",
                "count": len(hash_failures),
                "reason": "manifest hash replay failed",
                "required_fix": "commit or explicitly include every proof artifact and source file used by replay",
            }
        )

    raw_strict_status = str(proof.get("verifier_status", "FAIL"))
    strict_status = raw_strict_status
    audit_status = "PASS_FOR_VERIFIER_SOUNDNESS" if not hash_failures else "FAIL_REPRODUCTION"
    verifier_status = strict_status
    if raw_strict_status == "PASS" and not hash_failures and not roots:
        audit_status = "PASS"
    proof_confidence = 100.0 if raw_strict_status == "PASS" and audit_status == "PASS" else 0.0
    if raw_strict_status == "PASS" and roots:
        strict_status = "FAIL"
        verifier_status = "FAIL"
        proof_confidence = 0.0

    result = {
        "schema": "collatz_lab.strict_proof_replay_result",
        "version": 1,
        "run_id": manifest.get("run_id", "RUN-021-strict-verifier-replay-hardening"),
        "manifest_path": str(manifest_path),
        "audit_status": audit_status,
        "strict_verifier": strict_status,
        "verifier_status": verifier_status,
        "proof_confidence_percent": proof_confidence,
        "hash_failure_count": len(hash_failures),
        "hash_failures": hash_failures,
        "source_run_accounting": _source_run_accounting(manifest),
        "root_unsound_certificates": roots,
        "unknown_obligations": proof.get("unknown_obligations", []),
        "strict_errors": proof.get("verification", {}).get("errors", []),
    }

    if out is not None:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = replay_manifest(args.manifest, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
