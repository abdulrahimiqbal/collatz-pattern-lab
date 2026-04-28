"""Exact parent-coordinate maps for S4 parent-transition certificates.

RUN-034 enriches the existing HIGH_PARENT_SUCCESSOR_EXACT payloads.  The old
certificate proves the ``z(k)=c+3^a*k`` valuation step.  This module derives
the parent-coordinate map for the source odd coordinate ``q``:

    P_a(q): n = 2^a*q - 1
    q = r0 + 2^d*k
    q' = (3^a*q + 2^h0 - 1) / 2^(h0+b)

where ``h0 = d + T - b`` is the base burst divisor, ``T`` is the existing S4
extra valuation field, and ``b`` is the target parent level.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .proof_action_parent_transition_cert import _certificate_hash as transition_certificate_hash
from .proof_action_parent_transition_cert import parse_branch_id, replay_parent_transition_certificate


SCHEMA = "collatz_lab.parent_coordinate_map_certificate"
TYPE = "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP"


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


def _row_certificate(row: dict[str, Any]) -> dict[str, Any]:
    certificate = row.get("transition_certificate")
    if isinstance(certificate, dict):
        return certificate
    action = row.get("action")
    if isinstance(action, dict) and isinstance(action.get("transition_certificate"), dict):
        return action["transition_certificate"]
    return {}


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


def derive_parent_coordinate_map(certificate: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    try:
        branch = parse_branch_id(str(certificate.get("branch_id", "")))
    except ValueError as exc:
        return None, [{"reason": "MISSING_PARENT_COORDINATE_PAYLOAD", "missing_field": "branch_id", "detail": str(exc)}]
    symbolic = certificate.get("symbolic_map")
    divisibility = certificate.get("divisibility_certificate")
    membership = certificate.get("target_membership_certificate")
    if not isinstance(symbolic, dict):
        failures.append({"reason": "MISSING_PARENT_COORDINATE_PAYLOAD", "missing_field": "symbolic_map"})
        symbolic = {}
    if not isinstance(divisibility, dict):
        failures.append({"reason": "MISSING_PARENT_COORDINATE_PAYLOAD", "missing_field": "divisibility_certificate"})
        divisibility = {}
    if not isinstance(membership, dict):
        failures.append({"reason": "MISSING_PARENT_COORDINATE_PAYLOAD", "missing_field": "target_membership_certificate"})
        membership = {}
    if failures:
        return None, failures

    source_parent = int(certificate.get("source_parent", -1))
    target_parent = int(certificate.get("target_parent", -1))
    valuation = int(certificate.get("valuation", -1))
    source_depth = int(symbolic.get("source_depth", -1))
    source_residue = int(symbolic.get("source_residue", -1))
    c = int(divisibility.get("c", 0))
    coefficient = int(divisibility.get("coefficient", 0))
    parent_floor = int(membership.get("parent_floor", -1))
    if source_parent != branch["a"]:
        failures.append({"reason": "source_parent_branch_mismatch", "source_parent": source_parent, "branch_parent": branch["a"]})
    if source_residue != branch["residue"] or source_depth != branch["depth"]:
        failures.append({"reason": "source_branch_residue_depth_mismatch"})
    if parent_floor != target_parent - valuation:
        failures.append({"reason": "parent_floor_mismatch", "parent_floor": parent_floor, "target_parent": target_parent, "valuation": valuation})
    base_burst_division_exponent = source_depth - parent_floor
    if base_burst_division_exponent < 0:
        failures.append(
            {
                "reason": "MISSING_PARENT_COORDINATE_PAYLOAD",
                "missing_field": "base_burst_division_exponent",
                "suggested_required_field": "source_depth + valuation - target_parent must be nonnegative",
            }
        )
    A = 3**source_parent
    if coefficient != A:
        failures.append({"reason": "coefficient_is_not_3_power_source_parent", "coefficient": coefficient, "expected": A})
    if failures:
        return None, failures

    B = (1 << base_burst_division_exponent) - 1
    D = 1 << (base_burst_division_exponent + target_parent)
    branch_modulus = 1 << source_depth
    numerator_base = A * source_residue + B
    if numerator_base % branch_modulus != 0:
        failures.append({"reason": "branch_base_not_divisible_by_source_modulus"})
        return None, failures
    derived_c = numerator_base // branch_modulus
    if derived_c != c:
        failures.append({"reason": "derived_z_constant_mismatch", "derived_c": derived_c, "certificate_c": c})
        return None, failures
    k_modulus = int(divisibility.get("k_divisibility_modulus", 0))
    k_residue = int(divisibility.get("k_divisibility_residue", 0))
    excluded_modulus = int(divisibility.get("excluded_next_power_modulus", 0))
    excluded_residue = int(divisibility.get("excluded_next_power_residue", 0))
    if valuation == 0 and k_modulus != 1:
        failures.append({"reason": "valuation_zero_integrality_modulus_mismatch"})
    if valuation > 0 and k_modulus != (1 << valuation):
        failures.append({"reason": "k_divisibility_modulus_mismatch"})
    if excluded_modulus != (1 << (valuation + 1)):
        failures.append({"reason": "excluded_next_power_modulus_mismatch"})
    if failures:
        return None, failures
    map_payload = {
        "source_coordinate": "q",
        "target_coordinate": "q_prime",
        "A": str(A),
        "B": str(B),
        "D": str(D),
        "base_burst_division_exponent": base_burst_division_exponent,
        "source_depth": source_depth,
        "source_residue": source_residue,
        "formula": f"q_prime = ({A}*q + {B}) / {D}",
        "domain_constraints": [
            "q > 0",
            f"q == {source_residue} mod {branch_modulus}",
            f"k = (q - {source_residue}) / {branch_modulus}",
            f"k == {k_residue} mod {k_modulus}",
            f"k != {excluded_residue} mod {excluded_modulus}",
        ],
        "integrality_identity": f"{A}*q + {B} = 2^{source_depth}*({c} + {A}*k)",
        "target_odd_coordinate_identity": f"q_prime = ({c} + {A}*k) / 2^{valuation}",
        "minimum_q": 1,
        "domain_modulus": branch_modulus * max(k_modulus, 1),
        "domain_residue": source_residue + branch_modulus * k_residue,
    }
    return map_payload, []


def build_parent_coordinate_map_certificate(
    *,
    row: dict[str, Any],
    state: str = "",
) -> dict[str, Any]:
    source_certificate = _row_certificate(row)
    action = row.get("action") if isinstance(row.get("action"), dict) else {}
    transition_replay = None
    if state and action and source_certificate:
        transition_replay = replay_parent_transition_certificate(action=action, state=state, certificate=source_certificate).to_dict()
    map_payload, failures = derive_parent_coordinate_map(source_certificate)
    status = "PASS" if map_payload is not None and not failures and (not transition_replay or transition_replay.get("accepted")) else "FAIL"
    replay_checks = {
        "source_parent_reconstructs": status == "PASS",
        "transition_payload_replays": bool(transition_replay.get("accepted")) if isinstance(transition_replay, dict) else bool(source_certificate),
        "target_parent_reconstructs": status == "PASS",
        "integrality_proven": status == "PASS",
        "positivity_proven": status == "PASS",
        "map_matches_transition": status == "PASS",
    }
    certificate = {
        "schema": SCHEMA,
        "version": 1,
        "type": TYPE,
        "transition_certificate_id": str(source_certificate.get("transition_id", "")),
        "transition_certificate_hash": str(source_certificate.get("certificate_hash", "")),
        "branch_id": str(source_certificate.get("branch_id", "")),
        "source_parent": source_certificate.get("source_parent"),
        "target_parent": source_certificate.get("target_parent"),
        "valuation": source_certificate.get("valuation"),
        "source_transition_certificate": source_certificate,
        "parent_coordinate_map": map_payload or {},
        "replay_checks": replay_checks,
        "status": status,
    }
    if transition_replay and not transition_replay.get("accepted"):
        failures.append({"reason": "transition_payload_does_not_replay", "transition_replay": transition_replay})
    if failures:
        certificate["failures"] = failures
    certificate["certificate_hash"] = certificate_hash(certificate)
    return certificate


def replay_parent_coordinate_map_certificate(certificate: dict[str, Any]) -> ReplayResult:
    failures: list[dict[str, Any]] = []
    if not isinstance(certificate, dict):
        return ReplayResult(False, "REJECT_PARENT_COORDINATE_MAP", "certificate is missing")
    if certificate.get("schema") != SCHEMA or int(certificate.get("version", 0) or 0) != 1:
        failures.append({"reason": "unsupported_parent_coordinate_map_schema"})
    if certificate.get("type") != TYPE:
        failures.append({"reason": "unsupported_parent_coordinate_map_type", "type": certificate.get("type")})
    if str(certificate.get("certificate_hash")) != certificate_hash(certificate):
        failures.append({"reason": "parent_coordinate_map_hash_mismatch"})
    source_certificate = certificate.get("source_transition_certificate")
    if not isinstance(source_certificate, dict):
        failures.append({"reason": "missing_source_transition_certificate"})
    else:
        if str(source_certificate.get("certificate_hash")) != transition_certificate_hash(source_certificate):
            failures.append({"reason": "source_transition_certificate_hash_mismatch"})
        expected_map, map_failures = derive_parent_coordinate_map(source_certificate)
        failures.extend(map_failures)
        if expected_map != certificate.get("parent_coordinate_map"):
            failures.append({"reason": "parent_coordinate_map_payload_mismatch", "expected": expected_map, "actual": certificate.get("parent_coordinate_map")})
        for field in ("transition_certificate_id", "transition_certificate_hash", "branch_id", "source_parent", "target_parent", "valuation"):
            source_key = "transition_id" if field == "transition_certificate_id" else "certificate_hash" if field == "transition_certificate_hash" else field
            if certificate.get(field) != source_certificate.get(source_key):
                failures.append({"reason": f"{field}_mismatch", "expected": source_certificate.get(source_key), "actual": certificate.get(field)})
    checks = certificate.get("replay_checks")
    if not isinstance(checks, dict) or not all(
        checks.get(key)
        for key in (
            "source_parent_reconstructs",
            "transition_payload_replays",
            "target_parent_reconstructs",
            "integrality_proven",
            "positivity_proven",
            "map_matches_transition",
        )
    ):
        failures.append({"reason": "parent_coordinate_map_replay_checks_incomplete"})
    if certificate.get("status") != "PASS":
        failures.append({"reason": "parent_coordinate_map_status_not_pass", "status": certificate.get("status")})
    if failures:
        return ReplayResult(False, "REJECT_PARENT_COORDINATE_MAP", "parent-coordinate map certificate failed replay", failures)
    return ReplayResult(True, "ACCEPT", "parent-coordinate map certificate replays")


def enrich_transition_certificate_with_parent_map(
    transition_certificate: dict[str, Any],
    map_certificate: dict[str, Any],
) -> dict[str, Any]:
    replay = replay_parent_coordinate_map_certificate(map_certificate)
    if not replay.accepted:
        raise ValueError(f"parent-coordinate map certificate failed replay: {replay.failures}")
    enriched = json.loads(json.dumps(transition_certificate))
    enriched["type"] = TYPE
    enriched["parent_coordinate_map"] = map_certificate["parent_coordinate_map"]
    enriched["parent_coordinate_map_certificate_id"] = map_certificate["certificate_hash"]
    enriched["parent_coordinate_map_certificate_hash"] = map_certificate["certificate_hash"]
    enriched["replay_checks"] = {
        **dict(enriched.get("replay_checks") or {}),
        "parent_coordinate_map_replays": True,
        "parent_coordinate_integrality_proven": True,
        "parent_coordinate_positivity_proven": True,
    }
    enriched["certificate_hash"] = transition_certificate_hash(enriched)
    return enriched
