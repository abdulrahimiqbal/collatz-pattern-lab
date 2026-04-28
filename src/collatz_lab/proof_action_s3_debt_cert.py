"""Replayable exact S3 debt certificates for RUN-028."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from .proof_action_state import parse_state_facts


S3_DEBT_SCHEMA = "collatz_lab.s3_debt_certificate"
S3_DEBT_TYPE = "S3_DEBT_EXACT"
BRANCH_RE = re.compile(r"^P(?P<source_parent>\d+):r(?P<residue>\d+):d(?P<depth>\d+)$")


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


def certificate_hash(certificate: dict[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_hash"}
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def parse_branch_id(branch_id: str) -> dict[str, int]:
    match = BRANCH_RE.fullmatch(branch_id)
    if not match:
        raise ValueError(f"invalid S3 branch id: {branch_id}")
    return {key: int(value) for key, value in match.groupdict().items()}


def _reject_status_booleans(section: Any, *, path: str = "") -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if isinstance(section, dict):
        for key, value in section.items():
            child = f"{path}.{key}" if path else str(key)
            if key in {"exact_congruence_passed", "local_descent_passed"}:
                failures.append({"field": child, "reason": "status_boolean_not_allowed"})
            failures.extend(_reject_status_booleans(value, path=child))
    elif isinstance(section, list):
        for index, value in enumerate(section):
            failures.extend(_reject_status_booleans(value, path=f"{path}[{index}]"))
    return failures


def build_s3_debt_certificate(*, action: dict[str, Any], state: str, node_id: str) -> dict[str, Any]:
    facts = parse_state_facts(state)
    debt = facts.get("debt_transition") or {}
    branch_id = str(action["branch_id"])
    branch = parse_branch_id(branch_id)
    source_parent = int(debt.get("source_parent", branch["source_parent"]))
    target_parent = int(debt.get("target_parent", 0))
    valuation = int(action["valuation"])
    gain_num = int(action["gain_num"])
    gain_den = int(action["gain_den"])
    certificate = {
        "schema": S3_DEBT_SCHEMA,
        "version": 1,
        "type": S3_DEBT_TYPE,
        "certificate_id": f"s3_debt_cert_{node_id.replace(':', '_')}",
        "node_id": node_id,
        "branch_id": branch_id,
        "source_parent": source_parent,
        "target_parent": target_parent,
        "valuation": valuation,
        "gain_num": gain_num,
        "gain_den": gain_den,
        "exact_congruence_certificate": {
            "type": "S3_EXACT_CONGRUENCE",
            "branch_id": branch_id,
            "source_parent": source_parent,
            "target_parent": target_parent,
            "valuation": valuation,
            "branch_residue": branch["residue"],
            "branch_depth": branch["depth"],
            "source_modulus": 1 << branch["depth"],
            "theorem": "mixed_modulus_debt_transition_exactness",
            "statement": "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition",
        },
        "debt_measure_definition": {
            "type": "MIXED_LOG_GAIN_RANK",
            "measure_id": "mixed_log_gain_rank",
            "branch_id": branch_id,
            "source_parent": source_parent,
            "target_parent": target_parent,
            "valuation": valuation,
            "gain_num": gain_num,
            "gain_den": gain_den,
            "decrease_inequality": "gain_num < gain_den",
        },
        "local_descent_certificate": {
            "type": "LOCAL_DESCENT_FROM_DEBT_GAIN",
            "branch_id": branch_id,
            "gain_num": gain_num,
            "gain_den": gain_den,
            "rule": "positive denominator and gain ratio below one implies local debt descent",
        },
        "status": "PASS",
    }
    certificate["certificate_hash"] = certificate_hash(certificate)
    replay = replay_s3_debt_certificate(certificate, action=action, state=state)
    if not replay.accepted:
        raise ValueError(f"generated S3 debt certificate did not replay: {replay.status}: {replay.reason}")
    return certificate


def replay_s3_debt_certificate(
    certificate: dict[str, Any],
    *,
    action: dict[str, Any] | None = None,
    state: str | None = None,
) -> ReplayResult:
    required = {
        "schema",
        "version",
        "type",
        "certificate_id",
        "branch_id",
        "source_parent",
        "target_parent",
        "valuation",
        "gain_num",
        "gain_den",
        "exact_congruence_certificate",
        "debt_measure_definition",
        "local_descent_certificate",
        "status",
        "certificate_hash",
    }
    missing = sorted(required - set(certificate))
    if missing:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", f"missing S3 debt certificate fields: {missing}")
    if certificate.get("schema") != S3_DEBT_SCHEMA or certificate.get("type") != S3_DEBT_TYPE:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "unsupported S3 debt certificate schema/type")
    if int(certificate.get("version", 0) or 0) != 1:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "unsupported S3 debt certificate version")
    if str(certificate.get("status")) != "PASS":
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "S3 debt certificate status is not PASS")
    if str(certificate.get("certificate_hash")) != certificate_hash(certificate):
        return ReplayResult(False, "REJECT_S3_DEBT_HASH_MISMATCH", "S3 debt certificate hash mismatch")
    boolean_failures = _reject_status_booleans(certificate)
    if boolean_failures:
        return ReplayResult(False, "REJECT_S3_DEBT_STATUS_ONLY", "S3 debt certificate contains trusted status booleans", boolean_failures)

    try:
        branch = parse_branch_id(str(certificate["branch_id"]))
    except ValueError as exc:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", str(exc))
    source_parent = int(certificate["source_parent"])
    target_parent = int(certificate["target_parent"])
    valuation = int(certificate["valuation"])
    gain_num = int(certificate["gain_num"])
    gain_den = int(certificate["gain_den"])
    if action is not None:
        for field in ("branch_id", "valuation", "gain_num", "gain_den"):
            if certificate[field] != action[field]:
                return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", f"{field} does not match action")
    if state is not None:
        debt = parse_state_facts(state).get("debt_transition") or {}
        for field in ("branch_id", "valuation", "gain_num", "gain_den", "source_parent", "target_parent"):
            if field in debt and certificate[field] != debt[field]:
                return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", f"{field} does not match state debt fact")
    if source_parent != branch["source_parent"]:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "source_parent does not match branch id")

    congruence = certificate.get("exact_congruence_certificate")
    measure = certificate.get("debt_measure_definition")
    descent = certificate.get("local_descent_certificate")
    if not isinstance(congruence, dict):
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "exact_congruence_certificate is missing")
    if not isinstance(measure, dict):
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "debt_measure_definition is missing")
    if not isinstance(descent, dict):
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "local_descent_certificate is missing")

    expected_modulus = 1 << branch["depth"]
    congruence_checks = {
        "type": "S3_EXACT_CONGRUENCE",
        "branch_id": certificate["branch_id"],
        "source_parent": source_parent,
        "target_parent": target_parent,
        "valuation": valuation,
        "branch_residue": branch["residue"],
        "branch_depth": branch["depth"],
        "source_modulus": expected_modulus,
        "theorem": "mixed_modulus_debt_transition_exactness",
    }
    for field, expected in congruence_checks.items():
        if congruence.get(field) != expected:
            return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", f"exact_congruence_certificate.{field} mismatch")
    if branch["residue"] >= expected_modulus:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "branch residue is outside source modulus")

    measure_checks = {
        "type": "MIXED_LOG_GAIN_RANK",
        "measure_id": "mixed_log_gain_rank",
        "branch_id": certificate["branch_id"],
        "source_parent": source_parent,
        "target_parent": target_parent,
        "valuation": valuation,
        "gain_num": gain_num,
        "gain_den": gain_den,
        "decrease_inequality": "gain_num < gain_den",
    }
    for field, expected in measure_checks.items():
        if measure.get(field) != expected:
            return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", f"debt_measure_definition.{field} mismatch")
    if gain_den <= 0:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "gain_den must be positive")
    if gain_num >= gain_den:
        return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", "gain_num is not below gain_den")

    descent_checks = {
        "type": "LOCAL_DESCENT_FROM_DEBT_GAIN",
        "branch_id": certificate["branch_id"],
        "gain_num": gain_num,
        "gain_den": gain_den,
        "rule": "positive denominator and gain ratio below one implies local debt descent",
    }
    for field, expected in descent_checks.items():
        if descent.get(field) != expected:
            return ReplayResult(False, "REJECT_S3_DEBT_REPLAY_FAIL", f"local_descent_certificate.{field} mismatch")
    return ReplayResult(True, "ACCEPT", "exact S3 debt certificate replays")
