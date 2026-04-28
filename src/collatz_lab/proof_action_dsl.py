"""Typed proof-action DSL for verifier-guided Collatz proof search.

The v2 proof-action path deliberately avoids free-form proof paragraphs.  A
model is allowed to emit only canonical JSON objects whose ``type`` is one of
the known action names and whose fields match the action schema exactly.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any


class ProofActionError(ValueError):
    """Raised when proof-action JSON is syntactically or semantically invalid."""


_TARGET_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]*$")
_PARITY_RE = re.compile(r"^[01]+$")


@dataclass(frozen=True)
class ActionSpec:
    fields: tuple[str, ...]
    required: tuple[str, ...]


ACTION_SPECS: dict[str, ActionSpec] = {
    "SPLIT_RESIDUE": ActionSpec(("type", "target", "modulus", "residues"), ("target", "modulus", "residues")),
    "UNROLL_PARITY": ActionSpec(
        ("type", "target", "steps", "parity_word"),
        ("target", "steps", "parity_word"),
    ),
    "APPLY_LEMMA": ActionSpec(("type", "target", "lemma_id", "bindings"), ("target", "lemma_id", "bindings")),
    "PROVE_AFFINE_DESCENT": ActionSpec(
        ("type", "target", "modulus", "residue", "steps", "odd_count", "affine_b"),
        ("target", "modulus", "residue", "steps", "odd_count", "affine_b"),
    ),
    "LIFT_MODULUS": ActionSpec(
        ("type", "target", "from_modulus", "to_modulus", "residue"),
        ("target", "from_modulus", "to_modulus", "residue"),
    ),
    "DERIVE_PARENT_TRANSITION": ActionSpec(
        ("type", "target", "branch_id", "source_parent", "target_parent", "valuation", "transition_certificate"),
        ("target", "branch_id", "source_parent", "target_parent", "valuation", "transition_certificate"),
    ),
    "CHECK_FINITE_DESCENT": ActionSpec(("type", "target", "certificate"), ("target", "certificate")),
    "CHECK_DEBT_DECREASE": ActionSpec(
        ("type", "target", "branch_id", "gain_num", "gain_den", "valuation"),
        ("target", "branch_id", "gain_num", "gain_den", "valuation"),
    ),
    "INTRODUCE_DEBT_FUNCTION": ActionSpec(
        ("type", "target", "function_id", "variables"),
        ("target", "function_id", "variables"),
    ),
    "GENERALIZE_FROM_RESIDUES": ActionSpec(
        ("type", "target", "modulus", "residues", "lemma_id"),
        ("target", "modulus", "residues", "lemma_id"),
    ),
    "CLOSE_BY_VERIFIER": ActionSpec(("type", "target", "verifier", "status"), ("target", "verifier", "status")),
    "ABANDON_BRANCH": ActionSpec(("type", "target", "reason"), ("target", "reason")),
    "PROVE_RESIDUE_COVERAGE": ActionSpec(
        ("type", "target", "modulus", "covered_residue_count", "certificate_id"),
        ("target", "modulus", "covered_residue_count", "certificate_id"),
    ),
    "PROVE_RESIDUAL_COVERAGE": ActionSpec(
        (
            "type",
            "target",
            "certificate_id",
            "parent_certificate_id",
            "modulus",
            "residual_start",
            "residual_end",
            "covered_residue_count",
            "leaf_certificate_count",
            "certificate_hash",
        ),
        (
            "target",
            "certificate_id",
            "parent_certificate_id",
            "modulus",
            "residual_start",
            "residual_end",
            "covered_residue_count",
            "leaf_certificate_count",
            "certificate_hash",
        ),
    ),
    "PROVE_PARENT_RESIDUAL_COVERAGE": ActionSpec(
        (
            "type",
            "target",
            "certificate_id",
            "parent_certificate_id",
            "residual_certificate_id",
            "parent_level",
            "modulus",
            "residual_start",
            "residual_end",
            "path_node_count",
            "s3_dependency_count",
            "s4_dependency_count",
            "s6_dependency_count",
            "no_escape_dependency_count",
            "ranking_delta_num",
            "ranking_delta_den",
            "certificate_hash",
        ),
        (
            "target",
            "certificate_id",
            "parent_certificate_id",
            "residual_certificate_id",
            "parent_level",
            "modulus",
            "residual_start",
            "residual_end",
            "path_node_count",
            "s3_dependency_count",
            "s4_dependency_count",
            "s6_dependency_count",
            "no_escape_dependency_count",
            "ranking_delta_num",
            "ranking_delta_den",
            "certificate_hash",
        ),
    ),
    "PROVE_GLOBAL_DESCENT_INDUCTION": ActionSpec(
        ("type", "target", "lemma_id", "depends_on"),
        ("target", "lemma_id", "depends_on"),
    ),
    "CLOSE_WELL_FOUNDED_INDUCTION": ActionSpec(
        ("type", "target", "measure", "descent_lemma", "base_case_certificate"),
        ("target", "measure", "descent_lemma", "base_case_certificate"),
    ),
    "CERTIFY_NO_ESCAPE_BRANCH": ActionSpec(
        ("type", "target", "branch_id", "certificate_id"),
        ("target", "branch_id", "certificate_id"),
    ),
    "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM": ActionSpec(
        ("type", "target", "local_gate", "lifting_gate", "coverage_certificate"),
        ("target", "local_gate", "lifting_gate", "coverage_certificate"),
    ),
    "LIFT_LOCAL_TO_PARAMETRIC_FAMILY": ActionSpec(
        ("type", "target", "local_lemma", "family_id", "lifting_certificate"),
        ("target", "local_lemma", "family_id", "lifting_certificate"),
    ),
    "CLOSE_STRICT_THEOREM_BLOCKER": ActionSpec(
        ("type", "target", "blocker_id", "lemma_id"),
        ("target", "blocker_id", "lemma_id"),
    ),
    "PROPOSE_S6_LEMMA": ActionSpec(
        ("type", "target", "lemma_id", "statement"),
        ("target", "lemma_id", "statement"),
    ),
    "VERIFY_S6_LEMMA": ActionSpec(
        ("type", "target", "lemma_id", "verifier", "status", "certificate_id", "certificate_hash", "lemma"),
        ("target", "lemma_id"),
    ),
    "COMPOSE_GATE_PROOF": ActionSpec(
        ("type", "target", "proof_id", "depends_on"),
        ("target", "proof_id", "depends_on"),
    ),
}

ACTION_TYPES = tuple(ACTION_SPECS)

FINITE_CERTIFICATE_FIELDS = (
    "n",
    "first_descent_below_n",
    "steps_to_descent",
    "parity_word",
    "max_value",
    "reaches_terminal_cycle",
    "trajectory_hash",
)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ProofActionError(f"duplicate field: {key}")
        out[key] = value
    return out


def _require_int(value: Any, field: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProofActionError(f"{field} must be an integer")
    if minimum is not None and value < minimum:
        raise ProofActionError(f"{field} must be >= {minimum}")
    return value


def _require_str(value: Any, field: str, *, target: bool = False, nonempty: bool = True) -> str:
    if not isinstance(value, str):
        raise ProofActionError(f"{field} must be a string")
    if nonempty and not value:
        raise ProofActionError(f"{field} must be non-empty")
    if target and not _TARGET_RE.fullmatch(value):
        raise ProofActionError(f"{field} is not a valid target id")
    return value


def _require_int_list(value: Any, field: str, *, nonempty: bool = True) -> list[int]:
    if not isinstance(value, list):
        raise ProofActionError(f"{field} must be a list")
    if nonempty and not value:
        raise ProofActionError(f"{field} must be non-empty")
    out = [_require_int(item, f"{field}[]", minimum=0) for item in value]
    if len(out) != len(set(out)):
        raise ProofActionError(f"{field} must not contain duplicates")
    return out


def _validate_certificate(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProofActionError("certificate must be an object")
    unknown = sorted(set(value) - set(FINITE_CERTIFICATE_FIELDS))
    missing = sorted(set(FINITE_CERTIFICATE_FIELDS) - set(value))
    if unknown:
        raise ProofActionError(f"unknown certificate fields: {unknown}")
    if missing:
        raise ProofActionError(f"missing certificate fields: {missing}")
    cert = dict(value)
    _require_int(cert["n"], "certificate.n", minimum=1)
    _require_int(cert["first_descent_below_n"], "certificate.first_descent_below_n", minimum=1)
    _require_int(cert["steps_to_descent"], "certificate.steps_to_descent", minimum=1)
    parity = _require_str(cert["parity_word"], "certificate.parity_word")
    if not _PARITY_RE.fullmatch(parity):
        raise ProofActionError("certificate.parity_word must contain only 0/1")
    if len(parity) != cert["steps_to_descent"]:
        raise ProofActionError("certificate.parity_word length must equal certificate.steps_to_descent")
    _require_int(cert["max_value"], "certificate.max_value", minimum=1)
    if not isinstance(cert["reaches_terminal_cycle"], bool):
        raise ProofActionError("certificate.reaches_terminal_cycle must be a boolean")
    _require_str(cert["trajectory_hash"], "certificate.trajectory_hash")
    return cert


def _require_string_map(value: Any, field: str, required: set[str]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ProofActionError(f"{field} must be an object")
    unknown = sorted(set(value) - required)
    missing = sorted(required - set(value))
    if unknown:
        raise ProofActionError(f"unknown {field} fields: {unknown}")
    if missing:
        raise ProofActionError(f"missing {field} fields: {missing}")
    return {key: _require_str(value[key], f"{field}.{key}") for key in sorted(required)}


def _validate_transition_certificate(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProofActionError("transition_certificate must be an object")
    required = {
        "type",
        "transition_id",
        "branch_id",
        "source_parent",
        "target_parent",
        "valuation",
        "statement",
        "symbolic_map",
        "divisibility_certificate",
        "congruence_certificate",
        "target_membership_certificate",
        "status",
    }
    allowed = required | {
        "certificate_hash",
        "parent_coordinate_map",
        "parent_coordinate_map_certificate_id",
        "parent_coordinate_map_certificate_hash",
        "replay_checks",
    }
    unknown = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if unknown:
        raise ProofActionError(f"unknown transition_certificate fields: {unknown}")
    if missing:
        raise ProofActionError(f"missing transition_certificate fields: {missing}")
    cert = {
        "type": _require_str(value["type"], "transition_certificate.type"),
        "transition_id": _require_str(value["transition_id"], "transition_certificate.transition_id"),
        "branch_id": _require_str(value["branch_id"], "transition_certificate.branch_id"),
        "source_parent": _require_int(value["source_parent"], "transition_certificate.source_parent", minimum=1),
        "target_parent": _require_int(value["target_parent"], "transition_certificate.target_parent", minimum=1),
        "valuation": _require_int(value["valuation"], "transition_certificate.valuation", minimum=0),
        "statement": _require_str(value["statement"], "transition_certificate.statement"),
        "symbolic_map": _validate_replay_section(value["symbolic_map"], "transition_certificate.symbolic_map"),
        "divisibility_certificate": _validate_replay_section(value["divisibility_certificate"], "transition_certificate.divisibility_certificate"),
        "congruence_certificate": _validate_replay_section(value["congruence_certificate"], "transition_certificate.congruence_certificate"),
        "target_membership_certificate": _validate_replay_section(value["target_membership_certificate"], "transition_certificate.target_membership_certificate"),
        "status": _require_str(value["status"], "transition_certificate.status"),
    }
    if cert["type"] not in {"HIGH_PARENT_SUCCESSOR_EXACT", "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP"}:
        raise ProofActionError("transition_certificate.type must be HIGH_PARENT_SUCCESSOR_EXACT or HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP")
    if cert["status"] != "PASS":
        raise ProofActionError("transition_certificate.status must be PASS")
    if "certificate_hash" in value:
        cert["certificate_hash"] = _require_str(value["certificate_hash"], "transition_certificate.certificate_hash")
    if "parent_coordinate_map" in value:
        cert["parent_coordinate_map"] = _validate_replay_section(value["parent_coordinate_map"], "transition_certificate.parent_coordinate_map")
    if "parent_coordinate_map_certificate_id" in value:
        cert["parent_coordinate_map_certificate_id"] = _require_str(
            value["parent_coordinate_map_certificate_id"], "transition_certificate.parent_coordinate_map_certificate_id"
        )
    if "parent_coordinate_map_certificate_hash" in value:
        cert["parent_coordinate_map_certificate_hash"] = _require_str(
            value["parent_coordinate_map_certificate_hash"], "transition_certificate.parent_coordinate_map_certificate_hash"
        )
    if "replay_checks" in value:
        cert["replay_checks"] = _validate_replay_section(value["replay_checks"], "transition_certificate.replay_checks")
    return cert


def _validate_replay_section(value: Any, field: str) -> Any:
    if isinstance(value, str):
        return _require_str(value, field)
    if not isinstance(value, dict):
        raise ProofActionError(f"{field} must be a string or object")
    if not value:
        raise ProofActionError(f"{field} must be non-empty")
    normalized: dict[str, Any] = {}
    for key, item in sorted(value.items()):
        key_str = _require_str(key, f"{field}.key")
        if isinstance(item, str):
            normalized[key_str] = _require_str(item, f"{field}.{key_str}")
        elif isinstance(item, int) and not isinstance(item, bool):
            normalized[key_str] = item
        elif isinstance(item, bool):
            normalized[key_str] = item
        elif isinstance(item, list):
            if not item:
                raise ProofActionError(f"{field}.{key_str} must be non-empty")
            normalized[key_str] = [_require_str(entry, f"{field}.{key_str}[]") for entry in item]
        elif isinstance(item, dict):
            normalized[key_str] = _validate_replay_section(item, f"{field}.{key_str}")
        else:
            raise ProofActionError(f"{field}.{key_str} has unsupported JSON value")
    return normalized


def _validate_s6_lemma_payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProofActionError("lemma must be an object")
    required = {"lemma_id", "statement", "depends_on", "proof_payload"}
    unknown = sorted(set(value) - required)
    missing = sorted(required - set(value))
    if unknown:
        raise ProofActionError(f"unknown lemma fields: {unknown}")
    if missing:
        raise ProofActionError(f"missing lemma fields: {missing}")
    depends_on = value["depends_on"]
    if not isinstance(depends_on, list) or not depends_on:
        raise ProofActionError("lemma.depends_on must be a non-empty list")
    proof_payload = value["proof_payload"]
    required_payload = {"coverage", "transition_chain", "ranking_decrease", "no_escape", "induction_link"}
    if not isinstance(proof_payload, dict):
        raise ProofActionError("lemma.proof_payload must be an object")
    unknown_payload = sorted(set(proof_payload) - required_payload)
    missing_payload = sorted(required_payload - set(proof_payload))
    if unknown_payload:
        raise ProofActionError(f"unknown lemma.proof_payload fields: {unknown_payload}")
    if missing_payload:
        raise ProofActionError(f"missing lemma.proof_payload fields: {missing_payload}")
    return {
        "lemma_id": _require_str(value["lemma_id"], "lemma.lemma_id"),
        "statement": _require_str(value["statement"], "lemma.statement"),
        "depends_on": [_require_str(item, "lemma.depends_on[]") for item in depends_on],
        "proof_payload": {key: _validate_replay_section(proof_payload[key], f"lemma.proof_payload.{key}") for key in sorted(required_payload)},
    }


def validate_action(action: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized action after exact schema validation."""

    if not isinstance(action, dict):
        raise ProofActionError("action must be a JSON object")
    action_type = action.get("type")
    if not isinstance(action_type, str) or action_type not in ACTION_SPECS:
        raise ProofActionError(f"unknown action type: {action_type!r}")
    spec = ACTION_SPECS[action_type]
    unknown = sorted(set(action) - set(spec.fields))
    missing = sorted(set(spec.required) - set(action))
    if unknown:
        raise ProofActionError(f"unknown fields for {action_type}: {unknown}")
    if missing:
        raise ProofActionError(f"missing fields for {action_type}: {missing}")

    out: dict[str, Any] = {"type": action_type}
    for field in spec.fields:
        if field == "type" or field not in action:
            continue
        value = action[field]
        if field == "target":
            out[field] = _require_str(value, field, target=True)
        elif field in {
            "modulus",
            "steps",
            "from_modulus",
            "to_modulus",
            "source_parent",
            "target_parent",
            "gain_den",
            "covered_residue_count",
            "leaf_certificate_count",
            "parent_level",
            "path_node_count",
            "s3_dependency_count",
            "s4_dependency_count",
            "s6_dependency_count",
            "no_escape_dependency_count",
            "ranking_delta_num",
            "ranking_delta_den",
        }:
            out[field] = _require_int(value, field, minimum=1)
        elif field in {"residue", "odd_count", "affine_b", "valuation", "gain_num", "residual_start", "residual_end"}:
            out[field] = _require_int(value, field, minimum=0)
        elif field == "residues":
            out[field] = _require_int_list(value, field)
        elif field == "parity_word":
            parity = _require_str(value, field)
            if not _PARITY_RE.fullmatch(parity):
                raise ProofActionError("parity_word must contain only 0/1")
            out[field] = parity
        elif field == "bindings":
            if not isinstance(value, dict):
                raise ProofActionError("bindings must be an object")
            out[field] = dict(value)
        elif field == "certificate":
            out[field] = _validate_certificate(value)
        elif field == "transition_certificate":
            out[field] = _validate_transition_certificate(value)
        elif field == "lemma":
            out[field] = _validate_s6_lemma_payload(value)
        elif field == "variables":
            if not isinstance(value, list) or not value:
                raise ProofActionError("variables must be a non-empty list")
            out[field] = [_require_str(item, "variables[]") for item in value]
        elif field == "depends_on":
            if not isinstance(value, list) or not value:
                raise ProofActionError("depends_on must be a non-empty list")
            out[field] = [_require_str(item, "depends_on[]") for item in value]
        else:
            out[field] = _require_str(value, field)

    if action_type == "UNROLL_PARITY" and len(out["parity_word"]) != out["steps"]:
        raise ProofActionError("parity_word length must equal steps")
    if action_type == "PROVE_AFFINE_DESCENT":
        if out["residue"] >= out["modulus"]:
            raise ProofActionError("residue must be less than modulus")
        if out["odd_count"] > out["steps"]:
            raise ProofActionError("odd_count must be <= steps")
    if action_type == "LIFT_MODULUS":
        if out["to_modulus"] <= out["from_modulus"]:
            raise ProofActionError("to_modulus must be larger than from_modulus")
        if out["to_modulus"] % out["from_modulus"] != 0:
            raise ProofActionError("to_modulus must be a multiple of from_modulus")
        if out["residue"] >= out["from_modulus"]:
            raise ProofActionError("residue must be less than from_modulus")
    if action_type == "SPLIT_RESIDUE":
        if any(residue >= out["modulus"] for residue in out["residues"]):
            raise ProofActionError("all residues must be less than modulus")
    if action_type == "GENERALIZE_FROM_RESIDUES":
        if any(residue >= out["modulus"] for residue in out["residues"]):
            raise ProofActionError("all residues must be less than modulus")
    if action_type == "CHECK_DEBT_DECREASE" and out["gain_den"] <= 0:
        raise ProofActionError("gain_den must be positive")
    if action_type == "DERIVE_PARENT_TRANSITION":
        cert = out["transition_certificate"]
        for field in ("branch_id", "source_parent", "target_parent", "valuation"):
            if out[field] != cert[field]:
                raise ProofActionError(f"transition_certificate.{field} must match action {field}")
    if action_type == "VERIFY_S6_LEMMA":
        if "lemma" in out and out["lemma"]["lemma_id"] != out["lemma_id"]:
            raise ProofActionError("lemma.lemma_id must match action lemma_id")
    if action_type == "PROVE_RESIDUE_COVERAGE" and out["covered_residue_count"] > out["modulus"]:
        raise ProofActionError("covered_residue_count must be <= modulus")
    if action_type == "PROVE_RESIDUAL_COVERAGE":
        if out["residual_end"] <= out["residual_start"]:
            raise ProofActionError("residual_end must be larger than residual_start")
        if out["residual_end"] > out["modulus"]:
            raise ProofActionError("residual_end must be <= modulus")
    if action_type == "PROVE_PARENT_RESIDUAL_COVERAGE":
        if out["residual_end"] <= out["residual_start"]:
            raise ProofActionError("residual_end must be larger than residual_start")
        if out["residual_end"] > out["modulus"]:
            raise ProofActionError("residual_end must be <= modulus")
        if out["ranking_delta_num"] >= out["ranking_delta_den"]:
            raise ProofActionError("ranking delta must be a strict decrease")
    return canonical_action(out)


def canonical_action(action: dict[str, Any]) -> dict[str, Any]:
    """Return ``action`` with deterministic field order for its action type."""

    action_type = str(action.get("type"))
    if action_type not in ACTION_SPECS:
        raise ProofActionError(f"unknown action type: {action_type!r}")
    spec = ACTION_SPECS[action_type]
    return {field: action[field] for field in spec.fields if field in action}


def serialize_action(action: dict[str, Any]) -> str:
    """Serialize a proof action as compact canonical JSON."""

    normalized = validate_action(action)
    return json.dumps(normalized, ensure_ascii=True, separators=(",", ":"))


def parse_action(text: str) -> dict[str, Any]:
    """Parse and validate a canonical proof-action JSON object."""

    try:
        payload = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except ProofActionError:
        raise
    except json.JSONDecodeError as exc:
        raise ProofActionError(f"invalid action JSON: {exc.msg}") from exc
    return validate_action(payload)


def action_digest(action: dict[str, Any]) -> str:
    """Return a stable short digest for action identity."""

    text = serialize_action(action)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
