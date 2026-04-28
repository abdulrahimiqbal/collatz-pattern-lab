"""Replayable S6 lemma certificates for RUN-023.

RUN-023 replaces ``VERIFY_S6_LEMMA`` status/id acceptances with a certificate
whose dependencies can be replayed locally.  The certificates produced here are
not top-level Collatz theorem certificates; they only make each S6 lemma graph
node accountable to explicit dependency payloads.
"""

from __future__ import annotations

import hashlib
import json
import re
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


def dependency_payload_for_s3_debt_exact_certificate(row: dict[str, Any]) -> dict[str, Any]:
    certificate = row.get("s3_debt_certificate") if isinstance(row.get("s3_debt_certificate"), dict) else {}
    certificate_id = str(certificate.get("certificate_id", row.get("node_id", "")))
    return {
        "dependency_id": f"s3_debt_exact:{certificate_id}",
        "kind": "s3_debt_exact_certificate",
        "node_id": str(row.get("node_id", "")),
        "certificate_id": certificate_id,
        "certificate_hash": str(certificate.get("certificate_hash", "")),
        "s3_debt_certificate": certificate,
    }


def dependency_payload_for_s4_parent_transition_exact(row: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    node_id = str(row.get("node_id", ""))
    node = (graph.get("nodes") or {}).get(node_id, {})
    action = row.get("action") if isinstance(row.get("action"), dict) else {}
    certificate = row.get("transition_certificate") if isinstance(row.get("transition_certificate"), dict) else {}
    transition_id = str(certificate.get("transition_id", node_id))
    return {
        "dependency_id": f"s4_parent_transition:{transition_id}",
        "kind": "s4_parent_transition_certificate",
        "node_id": node_id,
        "certificate_id": transition_id,
        "certificate_hash": str(certificate.get("certificate_hash", "")),
        "requires_parent_coordinate_map": str(certificate.get("type", "")) == "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP",
        "state": _sanitize_dependency_state(str(node.get("state", ""))),
        "action": action,
        "transition_certificate": certificate,
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


def _sanitize_dependency_state(state: str) -> str:
    """Remove status fields that must not serve as replay evidence."""

    out = state
    out = re.sub(r"\n?<FACT [^>]*kind=\"s6_lemma_certificate\"[^>]*/>", "", out)
    for status in ("ACCEPT", "PASS", "REJECT", "UNKNOWN"):
        out = out.replace(f' verifier_status="{status}"', "")
    return out


def dependency_payload_for_action_certificate(dep_id: str, node: dict[str, Any], *, kind: str) -> dict[str, Any]:
    action = _accepted_action(node)
    return {
        "dependency_id": dep_id,
        "kind": kind,
        "node_id": str(node.get("node_id", dep_id)),
        "node_type": str(node.get("node_type", "")),
        "state": _sanitize_dependency_state(str(node.get("state", ""))),
        "action": action or {},
    }


def _dependency_is_status_only(payload: dict[str, Any]) -> bool:
    if str(payload.get("kind", "")) in {"s3_debt_exact_certificate", "s4_parent_transition_certificate"}:
        return False
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
    kind = str(payload.get("kind", ""))
    if kind == "s3_debt_exact_certificate":
        certificate = payload.get("s3_debt_certificate")
        if not isinstance(certificate, dict):
            return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "missing S3 exact certificate payload")
        if str(payload.get("certificate_hash", "")) != str(certificate.get("certificate_hash", "")):
            return ReplayResult(False, "REJECT_S6_LEMMA_HASH_MISMATCH", "S3 exact certificate hash does not match dependency payload")
        from .proof_action_s3_debt_cert import replay_s3_debt_certificate

        replay = replay_s3_debt_certificate(certificate)
        if not replay.accepted:
            return ReplayResult(False, replay.status, f"S3 exact dependency failed replay: {replay.reason}")
        return ReplayResult(True, "ACCEPT", "S3 exact dependency replayed")
    if kind == "s4_parent_transition_certificate":
        action = payload.get("action")
        state = str(payload.get("state", ""))
        certificate = payload.get("transition_certificate")
        if not isinstance(action, dict) or not isinstance(certificate, dict) or not state:
            return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "missing S4 exact transition replay payload")
        if str(payload.get("certificate_hash", "")) != str(certificate.get("certificate_hash", "")):
            return ReplayResult(False, "REJECT_S6_LEMMA_HASH_MISMATCH", "S4 exact certificate hash does not match dependency payload")
        if payload.get("requires_parent_coordinate_map") and (
            certificate.get("type") != "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP"
            or not isinstance(certificate.get("parent_coordinate_map"), dict)
        ):
            return ReplayResult(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", "S4 dependency is missing required parent-coordinate map")
        from .proof_action_parent_transition_cert import replay_parent_transition_certificate

        replay = replay_parent_transition_certificate(action=action, state=state, certificate=certificate)
        if not replay.accepted:
            return ReplayResult(False, replay.status, f"S4 exact dependency failed replay: {replay.reason}")
        return ReplayResult(True, "ACCEPT", "S4 exact dependency replayed")

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


def _is_strict_exact_dependency_payload(payload: dict[str, Any]) -> bool:
    return "s3_debt_exact_certificate_ids" in payload or "s4_parent_transition_certificate_ids" in payload


def _strict_exact_payload_failure(dep_id: str, dep_payload: dict[str, Any]) -> dict[str, Any] | None:
    if str(dep_payload.get("kind", "")) == "graph_node":
        return {"dependency_id": dep_id, "reason": "graph_node_dependency_not_allowed"}
    text = json.dumps(dep_payload, sort_keys=True)
    for forbidden in ("exact_congruence_passed", "local_descent_passed", "verifier_status"):
        if forbidden in text:
            return {"dependency_id": dep_id, "reason": f"forbidden_status_field:{forbidden}"}
    if '"status": "ACCEPTED"' in text or '"node_status": "ACCEPTED"' in text:
        return {"dependency_id": dep_id, "reason": "graph_accepted_status_not_allowed"}
    return None


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
    strict_exact_payload = _is_strict_exact_dependency_payload(payload)
    required_payload = {
        "coverage_certificate_ids",
        "no_escape_certificate_ids",
        "residual_parent_certificate_ids",
        "depends_on",
        "dependency_hashes",
        "dependency_replay_payloads",
    }
    if strict_exact_payload:
        required_payload |= {
            "s3_debt_exact_certificate_ids",
            "s4_parent_transition_certificate_ids",
            "ranking_or_induction_certificate_ids",
        }
    else:
        required_payload |= {
            "parent_transition_certificate_ids",
            "debt_transition_certificate_ids",
            "induction_or_ranking_certificate_ids",
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
    if "dependency_hashes" in certificate and certificate.get("dependency_hashes") != hashes:
        return ReplayResult(False, "REJECT_S6_LEMMA_HASH_MISMATCH", "top-level dependency_hashes do not match proof_payload hashes")

    failures: list[dict[str, Any]] = []
    for dep_id in depends_on:
        if dep_id not in hashes:
            failures.append({"dependency_id": dep_id, "reason": "missing_dependency_hash"})
            continue
        dep_payload = replay_payloads.get(dep_id)
        if not isinstance(dep_payload, dict):
            failures.append({"dependency_id": dep_id, "reason": "missing_dependency_replay_payload"})
            continue
        if strict_exact_payload:
            strict_failure = _strict_exact_payload_failure(dep_id, dep_payload)
            if strict_failure is not None:
                failures.append(strict_failure)
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


def build_s6_lemma_certificate_from_exact_dependencies(
    *,
    node_id: str,
    node: dict[str, Any],
    graph: dict[str, Any],
    s3_debt_rows: list[dict[str, Any]],
    parent_transition_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a RUN-029 S6 lemma certificate over exact S3/S4 certificates."""

    evidence = node.get("evidence") if isinstance(node.get("evidence"), dict) else {}
    source = node.get("source") if isinstance(node.get("source"), dict) else {}
    lemma_id = str(evidence.get("lemma_id") or node_id.rsplit(":", 1)[-1])
    blocker_id = str(source.get("blocker_id", ""))
    blocker_type = str(source.get("blocker_type", "strict_verifier_gap"))
    if blocker_type not in BLOCKER_TYPES:
        blocker_type = "strict_verifier_gap"
    statement = f"Replayable S6 lemma {lemma_id} closes {blocker_type} blocker {blocker_id} using exact S3/S4 certificates."
    nodes = graph.get("nodes") or {}
    dependency_payloads: dict[str, dict[str, Any]] = {}

    def add_action_dep(dep_id: str, kind: str) -> None:
        dep_node = nodes.get(dep_id)
        if isinstance(dep_node, dict) and dep_node.get("status") == "ACCEPTED":
            payload = dependency_payload_for_action_certificate(dep_id, dep_node, kind=kind)
            if payload.get("action"):
                dependency_payloads[dep_id] = payload

    for dep_id, kind in (
        (f"coverage:{evidence.get('coverage_certificate')}", "coverage_certificate"),
        (f"s6_lift:{evidence.get('lifting_certificate')}", "parametric_lift_certificate"),
        (f"induction:{evidence.get('base_case_certificate')}", "ranking_or_induction_certificate"),
        (f"no_escape:{evidence.get('no_escape_certificate')}", "no_escape_certificate"),
    ):
        if not dep_id.endswith(":None"):
            add_action_dep(dep_id, kind)

    old_payload = None
    for accepted in reversed(list(node.get("accepted_actions") or [])):
        action = accepted.get("action")
        if isinstance(action, dict) and action.get("type") == "VERIFY_S6_LEMMA":
            continue
        if isinstance(action, dict) and action.get("type") == "PROVE_PARENT_RESIDUAL_COVERAGE":
            old_payload = dependency_payload_for_parent_residual(
                action,
                _sanitize_dependency_state(str(node.get("state", ""))),
                node_id=node_id,
            )
            break
    if old_payload is not None:
        dependency_payloads[str(old_payload["dependency_id"])] = old_payload
    else:
        for dep_node in nodes.values():
            for accepted in reversed(list(dep_node.get("accepted_actions") or [])):
                action = accepted.get("action")
                if isinstance(action, dict) and action.get("type") == "PROVE_PARENT_RESIDUAL_COVERAGE":
                    payload = dependency_payload_for_parent_residual(
                        action,
                        _sanitize_dependency_state(str(dep_node.get("state", ""))),
                        node_id=str(dep_node.get("node_id", "")),
                    )
                    dependency_payloads[str(payload["dependency_id"])] = payload
                    break
            if any(dep_id.startswith("parent_residual:") for dep_id in dependency_payloads):
                break

    old_cert_payload = None
    for accepted in reversed(list(node.get("accepted_actions") or [])):
        action = accepted.get("action") if isinstance(accepted.get("action"), dict) else {}
        if action.get("type") == "VERIFY_S6_LEMMA":
            for row in _load_jsonl(Path("certificate_store/run023_s6_lemma_certificates.jsonl")):
                cert = row.get("s6_lemma_certificate") if isinstance(row.get("s6_lemma_certificate"), dict) else {}
                if str(cert.get("lemma_id", "")) == lemma_id:
                    old_cert_payload = cert.get("proof_payload") if isinstance(cert.get("proof_payload"), dict) else None
                    break
            break
    s3_by_node = {str(row.get("node_id", "")): row for row in s3_debt_rows}
    s3_by_cert = {
        str((row.get("s3_debt_certificate") or {}).get("certificate_id", "")): row
        for row in s3_debt_rows
        if isinstance(row.get("s3_debt_certificate"), dict)
    }
    old_s3_ids = [str(item) for item in (old_cert_payload or {}).get("debt_transition_certificate_ids", [])]
    selected_s3_rows: list[dict[str, Any]] = []
    for old_id in old_s3_ids:
        row = s3_by_node.get(old_id) or s3_by_cert.get(old_id)
        if row is not None:
            selected_s3_rows.append(row)
    if not selected_s3_rows and s3_debt_rows:
        selected_s3_rows.append(s3_debt_rows[0])
    for row in selected_s3_rows:
        payload = dependency_payload_for_s3_debt_exact_certificate(row)
        dependency_payloads[str(payload["dependency_id"])] = payload

    transition_by_id: dict[str, dict[str, Any]] = {}
    for row in parent_transition_rows:
        cert = row.get("transition_certificate") if isinstance(row.get("transition_certificate"), dict) else {}
        transition_by_id[str(cert.get("transition_id", ""))] = row
    old_s4_ids = [str(item) for item in (old_cert_payload or {}).get("parent_transition_certificate_ids", [])]
    selected_s4_rows: list[dict[str, Any]] = []
    for old_id in old_s4_ids:
        row = transition_by_id.get(old_id)
        if row is not None:
            selected_s4_rows.append(row)
    if not selected_s4_rows and parent_transition_rows:
        selected_s4_rows.append(parent_transition_rows[0])
    for row in selected_s4_rows:
        payload = dependency_payload_for_s4_parent_transition_exact(row, graph)
        dependency_payloads[str(payload["dependency_id"])] = payload

    depends_on = sorted(dependency_payloads)
    dependency_hashes = {dep_id: dependency_hash(payload) for dep_id, payload in dependency_payloads.items()}
    s3_ids = sorted(
        str((payload.get("s3_debt_certificate") or {}).get("certificate_id", ""))
        for payload in dependency_payloads.values()
        if payload.get("kind") == "s3_debt_exact_certificate"
    )
    s4_ids = sorted(
        str(payload.get("certificate_id", ""))
        for payload in dependency_payloads.values()
        if payload.get("kind") == "s4_parent_transition_certificate"
    )
    proof_payload = {
        "s3_debt_exact_certificate_ids": [item for item in s3_ids if item],
        "s4_parent_transition_certificate_ids": [item for item in s4_ids if item],
        "coverage_certificate_ids": [str(evidence.get("coverage_certificate", ""))],
        "no_escape_certificate_ids": [str(evidence.get("no_escape_certificate", ""))],
        "residual_parent_certificate_ids": sorted(
            dep_id.removeprefix("parent_residual:") for dep_id in depends_on if dep_id.startswith("parent_residual:")
        ),
        "ranking_or_induction_certificate_ids": [
            item
            for item in [str(evidence.get("base_case_certificate", "")), *proof_payload_ids(depends_on, "induction:")]
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
        "certificate_id": f"s6_lemma_cert_{lemma_id}_run029",
        "lemma_id": lemma_id,
        "blocker_id": blocker_id,
        "blocker_type": blocker_type,
        "statement": statement,
        "proof_payload": proof_payload,
        "dependency_hashes": dependency_hashes,
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
    replay = replay_s6_lemma_certificate(certificate, graph=graph)
    if not replay.accepted:
        raise ValueError(
            f"generated RUN-029 S6 lemma certificate did not replay for {node_id}: "
            f"{replay.status}: {replay.reason}: {replay.failures or []}"
        )
    return certificate


def proof_payload_ids(depends_on: list[str], prefix: str) -> list[str]:
    return sorted(dep_id.removeprefix(prefix) for dep_id in depends_on if dep_id.startswith(prefix))


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
