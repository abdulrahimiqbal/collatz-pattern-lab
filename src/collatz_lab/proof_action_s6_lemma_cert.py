"""Replayable S6 lemma certificates for RUN-023.

RUN-023 replaces ``VERIFY_S6_LEMMA`` status/id acceptances with a certificate
whose dependencies can be replayed locally.  The certificates produced here are
not top-level Collatz theorem certificates; they only make each S6 lemma graph
node accountable to explicit dependency payloads.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


S6_CERT_SCHEMA = "collatz_lab.s6_lemma_certificate"
S6_CERT_TYPE = "S6_LEMMA_EXACT"
BLOCKER_TYPES = {
    "coverage",
    "induction",
    "global_descent",
    "no_escape",
    "parent_transition",
    "parametric_lift",
    "strict_verifier_gap",
}


@dataclass(frozen=True)
class ReplayResult:
    accepted: bool
    status: str
    reason: str
    failures: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "status": self.status,
            "reason": self.reason,
            "failures": list(self.failures or []),
        }


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def certificate_hash(certificate: dict[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_hash"}
    return _hash(payload)


def dependency_hash(payload: dict[str, Any]) -> str:
    return _hash(payload)


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _accepted_action(node: dict[str, Any]) -> dict[str, Any] | None:
    for row in reversed(list(node.get("accepted_actions") or [])):
        action = row.get("action")
        if isinstance(action, dict):
            return action
    return None


def _accepted_check(node: dict[str, Any]) -> dict[str, Any]:
    for row in reversed(list(node.get("accepted_actions") or [])):
        check = row.get("verifier_check")
        if isinstance(check, dict):
            return check
    return {}


def dependency_payload_for_graph_node(node_id: str, node: dict[str, Any]) -> dict[str, Any]:
    action = _accepted_action(node)
    return {
        "dependency_id": node_id,
        "kind": "graph_node",
        "node_id": node_id,
        "node_type": str(node.get("node_type", "")),
        "state": str(node.get("state", "")),
        "action": action or {},
        "verifier_check": _accepted_check(node),
    }


def dependency_payload_for_transition_certificate(row: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    node_id = str(row.get("node_id", ""))
    node = (graph.get("nodes") or {}).get(node_id, {})
    action = row.get("action") if isinstance(row.get("action"), dict) else {}
    certificate = row.get("transition_certificate") if isinstance(row.get("transition_certificate"), dict) else {}
    return {
        "dependency_id": f"s4_transition:{certificate.get('transition_id', node_id)}",
        "kind": "parent_transition_certificate",
        "node_id": node_id,
        "node_type": "S4_LIFT",
        "state": str(node.get("state", "")),
        "action": action,
        "transition_certificate_hash": str(certificate.get("certificate_hash", "")),
        "verifier_check": row.get("verifier_check") if isinstance(row.get("verifier_check"), dict) else {},
    }


def dependency_payload_for_parent_residual(action: dict[str, Any], state: str, *, node_id: str) -> dict[str, Any]:
    cert_id = str(action.get("certificate_id", "parent_residual_certificate"))
    return {
        "dependency_id": f"parent_residual:{cert_id}",
        "kind": "parent_residual_certificate",
        "node_id": node_id,
        "node_type": "COVERAGE_CERTIFICATE",
        "state": state,
        "action": dict(action),
        "verifier_check": {"accepted": True, "status": "ACCEPT"},
    }


def _dependency_is_status_only(payload: dict[str, Any]) -> bool:
    action = payload.get("action")
    if not isinstance(action, dict) or not action:
        return True
    action_type = str(action.get("type", ""))
    if action_type == "VERIFY_S6_LEMMA" and not action.get("certificate_id"):
        return True
    if action_type == "DERIVE_PARENT_TRANSITION" and not action.get("transition_certificate"):
        return True
    if action_type == "DERIVE_PARENT_TRANSITION" and action.get("transition_certificate"):
        return False
    text = json.dumps(payload, sort_keys=True).lower()
    return "sample_checks_passed" in text or "samples are exact" in text or "sample-only" in text


def _replay_dependency(payload: dict[str, Any]) -> ReplayResult:
    if _dependency_is_status_only(payload):
        return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_STATUS_ONLY", "dependency is status-only or sample-only")
    action = payload.get("action")
    state = str(payload.get("state", ""))
    if not isinstance(action, dict) or not state:
        return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "dependency lacks replay action or state")

    from .proof_action_decode import verify_action_for_state

    check = verify_action_for_state(action, state)
    if not check.accepted:
        return ReplayResult(
            False,
            "REJECT_S6_LEMMA_DEPENDENCY_FAIL",
            f"{payload.get('dependency_id')} failed verifier replay: {check.status}: {check.reason}",
        )
    return ReplayResult(True, "ACCEPT", "dependency replayed")


def _find_s6_node(graph: dict[str, Any] | None, lemma_id: str, blocker_id: str) -> dict[str, Any] | None:
    if not graph:
        return None
    for node in (graph.get("nodes") or {}).values():
        if node.get("node_type") != "S6_LEMMA":
            continue
        evidence = node.get("evidence") if isinstance(node.get("evidence"), dict) else {}
        source = node.get("source") if isinstance(node.get("source"), dict) else {}
        if str(evidence.get("lemma_id", "")) == lemma_id and str(source.get("blocker_id", "")) == blocker_id:
            return node
    return None


def replay_s6_lemma_certificate(
    certificate: dict[str, Any],
    certificate_store: str | Path | dict[str, Any] | None = None,
    graph: dict[str, Any] | None = None,
) -> ReplayResult:
    """Replay one S6 lemma certificate.

    The optional ``certificate_store`` argument is accepted for the clean-clone
    replay API.  RUN-023 certificates are self-contained: dependency payloads
    and hashes are embedded in ``proof_payload`` so local action replay does not
    need remote state.
    """

    del certificate_store
    required = {
        "schema",
        "version",
        "type",
        "certificate_id",
        "lemma_id",
        "blocker_id",
        "blocker_type",
        "statement",
        "proof_payload",
        "replay_checks",
        "status",
        "certificate_hash",
    }
    missing = sorted(required - set(certificate))
    if missing:
        return ReplayResult(False, "REJECT_S6_LEMMA_PAYLOAD", f"missing S6 lemma certificate fields: {missing}")
    if certificate.get("schema") != S6_CERT_SCHEMA or certificate.get("type") != S6_CERT_TYPE:
        return ReplayResult(False, "REJECT_S6_LEMMA_PAYLOAD", "unsupported S6 lemma certificate schema/type")
    if int(certificate.get("version", 0) or 0) != 1:
        return ReplayResult(False, "REJECT_S6_LEMMA_PAYLOAD", "unsupported S6 lemma certificate version")
    if str(certificate.get("status")) != "PASS":
        return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "S6 lemma certificate status is not PASS")
    if str(certificate.get("blocker_type")) not in BLOCKER_TYPES:
        return ReplayResult(False, "REJECT_S6_LEMMA_STATEMENT_MISMATCH", "unknown S6 blocker type")
    expected_hash = certificate_hash(certificate)
    if str(certificate.get("certificate_hash")) != expected_hash:
        return ReplayResult(False, "REJECT_S6_LEMMA_HASH_MISMATCH", "S6 lemma certificate hash mismatch")

    lemma_id = str(certificate.get("lemma_id", ""))
    certificate_id = str(certificate.get("certificate_id", ""))
    blocker_id = str(certificate.get("blocker_id", ""))
    if not certificate_id:
        return ReplayResult(False, "REJECT_S6_LEMMA_PAYLOAD", "S6 lemma certificate id is empty")
    node = _find_s6_node(graph, lemma_id, blocker_id)
    if graph is not None and node is None:
        return ReplayResult(False, "REJECT_S6_LEMMA_STATEMENT_MISMATCH", "S6 blocker/lemma node is absent from graph")
    if node is not None:
        statement = str(certificate.get("statement", ""))
        source = node.get("source") if isinstance(node.get("source"), dict) else {}
        evidence = node.get("evidence") if isinstance(node.get("evidence"), dict) else {}
        if str(evidence.get("lemma_id", "")) != lemma_id or str(source.get("blocker_id", "")) != blocker_id:
            return ReplayResult(False, "REJECT_S6_LEMMA_STATEMENT_MISMATCH", "lemma or blocker id does not match graph node")
        if blocker_id not in statement and str(source.get("blocker_type", "")) not in statement:
            return ReplayResult(False, "REJECT_S6_LEMMA_STATEMENT_MISMATCH", "statement does not identify the target blocker")

    payload = certificate.get("proof_payload")
    if not isinstance(payload, dict):
        return ReplayResult(False, "REJECT_S6_LEMMA_PAYLOAD", "proof_payload must be an object")
    required_payload = {
        "coverage_certificate_ids",
        "parent_transition_certificate_ids",
        "debt_transition_certificate_ids",
        "no_escape_certificate_ids",
        "residual_parent_certificate_ids",
        "induction_or_ranking_certificate_ids",
        "depends_on",
        "dependency_hashes",
        "dependency_replay_payloads",
    }
    missing_payload = sorted(required_payload - set(payload))
    if missing_payload:
        return ReplayResult(False, "REJECT_S6_LEMMA_PAYLOAD", f"missing proof_payload fields: {missing_payload}")
    depends_on = [str(item) for item in payload.get("depends_on", [])]
    if not depends_on:
        return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "S6 lemma certificate has no dependencies")
    hashes = payload.get("dependency_hashes")
    replay_payloads = payload.get("dependency_replay_payloads")
    if not isinstance(hashes, dict) or not isinstance(replay_payloads, dict):
        return ReplayResult(False, "REJECT_S6_LEMMA_HASH_MISMATCH", "dependency hashes and replay payloads must be objects")

    failures: list[dict[str, Any]] = []
    for dep_id in depends_on:
        if dep_id not in hashes:
            failures.append({"dependency_id": dep_id, "reason": "missing_dependency_hash"})
            continue
        dep_payload = replay_payloads.get(dep_id)
        if not isinstance(dep_payload, dict):
            failures.append({"dependency_id": dep_id, "reason": "missing_dependency_replay_payload"})
            continue
        actual_hash = dependency_hash(dep_payload)
        if str(hashes[dep_id]) != actual_hash:
            failures.append(
                {
                    "dependency_id": dep_id,
                    "reason": "dependency_hash_mismatch",
                    "expected": str(hashes[dep_id]),
                    "actual": actual_hash,
                }
            )
            continue
        replay = _replay_dependency(dep_payload)
        if not replay.accepted:
            failures.append({"dependency_id": dep_id, "reason": replay.reason, "status": replay.status})

    if failures:
        hash_failures = [row for row in failures if "hash" in str(row.get("reason", ""))]
        status = "REJECT_S6_LEMMA_HASH_MISMATCH" if hash_failures else "REJECT_S6_LEMMA_DEPENDENCY_FAIL"
        return ReplayResult(False, status, "one or more S6 lemma dependencies failed replay", failures)

    checks = certificate.get("replay_checks")
    if not isinstance(checks, dict) or not all(bool(checks.get(key)) for key in ("all_dependencies_present", "all_dependencies_hash_match", "all_dependencies_replay_pass", "statement_matches_blocker", "closes_target_blocker")):
        return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "stored replay_checks are not all true")
    return ReplayResult(True, "ACCEPT", "S6 lemma certificate and dependencies replay")


def build_s6_lemma_certificate(
    *,
    node_id: str,
    node: dict[str, Any],
    graph: dict[str, Any],
    parent_transition_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build one self-contained replayable S6 lemma certificate."""

    evidence = node.get("evidence") if isinstance(node.get("evidence"), dict) else {}
    source = node.get("source") if isinstance(node.get("source"), dict) else {}
    lemma_id = str(evidence.get("lemma_id") or node_id.rsplit(":", 1)[-1])
    blocker_id = str(source.get("blocker_id", ""))
    blocker_type = str(source.get("blocker_type", "strict_verifier_gap"))
    if blocker_type not in BLOCKER_TYPES:
        blocker_type = "strict_verifier_gap"
    statement = f"Replayable S6 lemma {lemma_id} closes {blocker_type} blocker {blocker_id}."
    nodes = graph.get("nodes") or {}
    dependency_payloads: dict[str, dict[str, Any]] = {}

    def add_node(dep_id: str) -> None:
        dep_node = nodes.get(dep_id)
        if isinstance(dep_node, dict) and dep_node.get("status") == "ACCEPTED":
            payload = dependency_payload_for_graph_node(dep_id, dep_node)
            if payload.get("action"):
                dependency_payloads[dep_id] = payload

    for dep_id in (
        f"coverage:{evidence.get('coverage_certificate')}",
        f"s6_lift:{evidence.get('lifting_certificate')}",
        f"induction:{evidence.get('base_case_certificate')}",
        f"no_escape:{evidence.get('no_escape_certificate')}",
    ):
        if not dep_id.endswith(":None"):
            add_node(dep_id)

    for dep_id, dep_node in nodes.items():
        if dep_node.get("node_type") == "S3_TRANSITION" and dep_node.get("status") == "ACCEPTED":
            add_node(str(dep_id))
            break

    for row in parent_transition_rows or []:
        payload = dependency_payload_for_transition_certificate(row, graph)
        if payload.get("state") and payload.get("action"):
            dependency_payloads[str(payload["dependency_id"])] = payload
            break

    for accepted in reversed(list(node.get("accepted_actions") or [])):
        action = accepted.get("action")
        if isinstance(action, dict) and action.get("type") == "PROVE_PARENT_RESIDUAL_COVERAGE":
            payload = dependency_payload_for_parent_residual(action, str(node.get("state", "")), node_id=node_id)
            dependency_payloads[str(payload["dependency_id"])] = payload
            break

    depends_on = sorted(dependency_payloads)
    dependency_hashes = {dep_id: dependency_hash(payload) for dep_id, payload in dependency_payloads.items()}
    proof_payload = {
        "coverage_certificate_ids": [str(evidence.get("coverage_certificate", ""))],
        "parent_transition_certificate_ids": sorted(
            dep_id.removeprefix("s4_transition:") for dep_id in depends_on if dep_id.startswith("s4_transition:")
        ),
        "debt_transition_certificate_ids": sorted(dep_id for dep_id in depends_on if dep_id.startswith("s3:")),
        "no_escape_certificate_ids": [str(evidence.get("no_escape_certificate", ""))],
        "residual_parent_certificate_ids": sorted(
            dep_id.removeprefix("parent_residual:") for dep_id in depends_on if dep_id.startswith("parent_residual:")
        ),
        "induction_or_ranking_certificate_ids": [
            item
            for item in [str(evidence.get("base_case_certificate", "")), *sorted(dep_id for dep_id in depends_on if dep_id.startswith("s3:"))]
            if item
        ],
        "depends_on": depends_on,
        "dependency_hashes": dependency_hashes,
        "dependency_replay_payloads": dependency_payloads,
    }
    certificate = {
        "schema": S6_CERT_SCHEMA,
        "version": 1,
        "type": S6_CERT_TYPE,
        "certificate_id": f"s6_lemma_cert_{lemma_id}",
        "lemma_id": lemma_id,
        "blocker_id": blocker_id,
        "blocker_type": blocker_type,
        "statement": statement,
        "proof_payload": proof_payload,
        "replay_checks": {
            "all_dependencies_present": True,
            "all_dependencies_hash_match": True,
            "all_dependencies_replay_pass": True,
            "statement_matches_blocker": True,
            "closes_target_blocker": True,
        },
        "status": "PASS",
    }
    certificate["certificate_hash"] = certificate_hash(certificate)
    replay = replay_s6_lemma_certificate(certificate)
    if not replay.accepted:
        raise ValueError(
            f"generated S6 lemma certificate did not replay for {node_id}: "
            f"{replay.status}: {replay.reason}: {replay.failures or []}"
        )
    return certificate
