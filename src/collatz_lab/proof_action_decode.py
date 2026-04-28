"""Constrained decoding and exact verifier checks for typed proof actions."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from .collatz import collatz_step, parity_prefix
from .proof_action_dsl import ProofActionError, parse_action, serialize_action, validate_action
from .proof_action_state import parse_state_facts
from .verifier import affine_for_parity_prefix, verify_fixed_residue_descent_exhaustive


@dataclass(frozen=True)
class ActionCheck:
    accepted: bool
    status: str
    reason: str
    closed_obligation: bool = False
    progress: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "status": self.status,
            "reason": self.reason,
            "closed_obligation": self.closed_obligation,
            "progress": self.progress,
        }


def repair_json_action(text: str) -> str | None:
    """Return a JSON object substring if there is a single deterministic repair."""

    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if 0 <= start < end:
        return stripped[start : end + 1]
    return None


def parse_or_repair_action(text: str) -> dict[str, Any]:
    try:
        return parse_action(text)
    except ProofActionError:
        repaired = repair_json_action(text)
        if repaired is None or repaired == text.strip():
            raise
        return parse_action(repaired)


def _trajectory_hash(values: list[int]) -> str:
    return hashlib.sha256(",".join(str(value) for value in values).encode("utf-8")).hexdigest()


def _trajectory_until(n: int, steps: int) -> list[int]:
    values = [n]
    current = n
    for _ in range(steps):
        current = collatz_step(current)
        values.append(current)
    return values


def _fact_values(facts: dict[str, Any], *keys: str) -> set[str]:
    values: set[str] = set()
    for key in keys:
        if key in facts:
            values.add(str(facts[key]))
    for value in facts.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for key in keys:
                        if key in item:
                            values.add(str(item[key]))
        elif isinstance(value, dict):
            for key in keys:
                if key in value:
                    values.add(str(value[key]))
    return values


def _s6_context(facts: dict[str, Any]) -> bool:
    return str(facts.get("gate", "")).startswith("S6") or str(facts.get("goal_kind", "")).startswith("s6")


def _fact_rows(facts: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    rows = facts.get(f"{kind}_facts", [])
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _s6_blocker_fact(facts: dict[str, Any]) -> dict[str, Any]:
    rows = _fact_rows(facts, "s6_blocker")
    return rows[0] if rows else {}


def _first_fact_payload(facts: dict[str, Any], key: str, *kinds: str) -> dict[str, Any] | None:
    payload = _decode_json_payload(facts.get(key))
    if payload is not None:
        return payload
    for kind in kinds:
        for row in _fact_rows(facts, kind):
            payload = _decode_json_payload(row.get(key))
            if payload is not None:
                return payload
    return None


def _int_fact(facts: dict[str, Any], key: str, default: int = 0) -> int:
    if key in facts:
        return int(facts.get(key) or default)
    blocker = _s6_blocker_fact(facts)
    if key in blocker:
        return int(blocker.get(key) or default)
    return default


def _decode_json_payload(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip().startswith("{"):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _payload_hash(value: dict[str, Any]) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _transition_certificate_replays(parsed: dict[str, Any], fact: dict[str, Any], state: str) -> ActionCheck | None:
    cert = parsed["transition_certificate"]
    state_cert = _decode_json_payload(fact.get("transition_certificate"))
    if state_cert is not None and state_cert != cert:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "transition certificate does not match state artifact payload")
    expected_hash = str(fact.get("transition_certificate_hash", "") or "")
    if expected_hash and expected_hash not in {_payload_hash(cert), str(cert.get("certificate_hash", "") or "")}:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "transition certificate hash does not match state artifact")
    from .proof_action_parent_transition_cert import replay_parent_transition_certificate

    replay = replay_parent_transition_certificate(action=parsed, state=state, certificate=cert)
    if not replay.accepted:
        return replay
    return None


def _section_is_replayable(value: Any, *, dependencies: set[str], certs: set[str], statuses: set[str]) -> bool:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped in dependencies or stripped in certs or stripped in statuses:
            return False
        return stripped not in {"ACCEPT", "PASS", "REJECT", "UNKNOWN"}
    if not isinstance(value, dict) or not value:
        return False
    keys = set(value)
    if keys <= {"certificate_id", "lemma_id", "status", "verifier_status"}:
        return False
    if str(value.get("status", "")).upper() in {"ACCEPT", "PASS"} and len(keys) <= 2:
        return False
    if str(value.get("replay_status", "PASS")).upper() not in {"PASS", "ACCEPT"}:
        return False
    payloadish_keys = {
        "certificate_hash",
        "payload_hash",
        "proof",
        "proof_terms",
        "symbolic_payload",
        "replay_steps",
        "congruence_identity",
        "integer_divisibility",
        "target_membership",
        "coverage_identity",
        "transition_chain",
        "ranking_decrease",
        "no_escape",
        "induction_link",
    }
    if keys & payloadish_keys:
        return True
    return any(_section_is_replayable(item, dependencies=dependencies, certs=certs, statuses=statuses) for item in value.values())


def _s6_lemma_payload_replays(
    lemma: dict[str, Any],
    *,
    dependencies: set[str],
    certs: set[str],
    statuses: set[str],
) -> ActionCheck | None:
    if set(lemma.get("depends_on", [])) != dependencies:
        return ActionCheck(False, "REJECT_S6_LEMMA_PAYLOAD", "lemma dependency list changed during normalization")
    missing = dependencies - (certs | {str(lemma.get("lemma_id", ""))})
    if missing:
        return ActionCheck(False, "REJECT_MISSING_DEPENDENCY", f"S6 lemma payload references unavailable dependencies: {sorted(missing)}")
    proof_payload = lemma.get("proof_payload", {})
    for key in ("coverage", "transition_chain", "ranking_decrease", "no_escape", "induction_link"):
        if not _section_is_replayable(proof_payload.get(key), dependencies=dependencies, certs=certs, statuses=statuses):
            return ActionCheck(False, "REJECT_S6_LEMMA_PAYLOAD", f"S6 lemma proof_payload.{key} is only a name/status or is missing replay data")
    return None


def _s6_lemma_certificate_fact(facts: dict[str, Any], lemma_id: str, certificate_id: str | None = None) -> dict[str, Any] | None:
    for row in _fact_rows(facts, "s6_lemma_certificate"):
        if str(row.get("lemma_id", "")) != lemma_id:
            continue
        if certificate_id and str(row.get("certificate_id", "")) != certificate_id:
            continue
        return row
    return None


def _s6_lemma_certificate_payload(row: dict[str, Any]) -> dict[str, Any] | None:
    return (
        _decode_json_payload(row.get("certificate_payload"))
        or _decode_json_payload(row.get("s6_lemma_certificate"))
        or _decode_json_payload(row.get("proof_payload"))
    )


def _s6_lemma_certificate_replays(parsed: dict[str, Any], facts: dict[str, Any]) -> ActionCheck | None:
    lemma_id = str(parsed["lemma_id"])
    certificate_id = str(parsed.get("certificate_id", "") or "")
    if not certificate_id:
        return ActionCheck(False, "REJECT_MISSING_S6_LEMMA_CERTIFICATE", "VERIFY_S6_LEMMA requires a replayable S6 lemma certificate id")
    row = _s6_lemma_certificate_fact(facts, lemma_id, certificate_id)
    if row is None:
        return ActionCheck(False, "REJECT_MISSING_S6_LEMMA_CERTIFICATE", "S6 lemma certificate is not present in the state")
    if str(row.get("status", "")) in {"PASS", "ACCEPT"} and _s6_lemma_certificate_payload(row) is None:
        return ActionCheck(False, "REJECT_S6_LEMMA_STATUS_ONLY", "S6 lemma certificate fact has status but no replay payload")
    certificate = _s6_lemma_certificate_payload(row)
    if certificate is None:
        return ActionCheck(False, "REJECT_MISSING_S6_LEMMA_CERTIFICATE", "S6 lemma certificate payload is missing")
    expected_hashes = {str(row.get("certificate_hash", "") or ""), str(certificate.get("certificate_hash", "") or "")}
    action_hash = str(parsed.get("certificate_hash", "") or "")
    if action_hash and action_hash not in expected_hashes:
        return ActionCheck(False, "REJECT_S6_LEMMA_HASH_MISMATCH", "VERIFY_S6_LEMMA certificate hash does not match state fact")
    if str(certificate.get("lemma_id", "")) != lemma_id:
        return ActionCheck(False, "REJECT_S6_LEMMA_STATEMENT_MISMATCH", "S6 lemma certificate lemma_id does not match action")

    from .proof_action_s6_lemma_cert import replay_s6_lemma_certificate

    replay = replay_s6_lemma_certificate(certificate)
    if not replay.accepted:
        if replay.status == "REJECT_S6_LEMMA_HASH_MISMATCH":
            return ActionCheck(False, "REJECT_S6_LEMMA_HASH_MISMATCH", replay.reason)
        if replay.status == "REJECT_S6_LEMMA_STATEMENT_MISMATCH":
            return ActionCheck(False, "REJECT_S6_LEMMA_STATEMENT_MISMATCH", replay.reason)
        return ActionCheck(False, "REJECT_S6_LEMMA_DEPENDENCY_FAIL", replay.reason)
    return None


def _s3_debt_certificate_fact(facts: dict[str, Any], branch_id: str) -> dict[str, Any] | None:
    for row in _fact_rows(facts, "s3_debt_certificate"):
        if str(row.get("branch_id", "")) == branch_id:
            return row
    return None


def _s3_debt_certificate_payload(row: dict[str, Any]) -> dict[str, Any] | None:
    return (
        _decode_json_payload(row.get("certificate_payload"))
        or _decode_json_payload(row.get("s3_debt_certificate"))
        or _decode_json_payload(row.get("proof_payload"))
    )


def _s3_status_only_debt_fact(debt: dict[str, Any]) -> bool:
    return "exact_congruence_passed" in debt or "local_descent_passed" in debt


def _s3_debt_certificate_replays(parsed: dict[str, Any], facts: dict[str, Any], state: str) -> ActionCheck | None:
    branch_id = str(parsed["branch_id"])
    row = _s3_debt_certificate_fact(facts, branch_id)
    debt = facts.get("debt_transition") or {}
    if row is None:
        if _s3_status_only_debt_fact(debt):
            return ActionCheck(False, "REJECT_S3_DEBT_STATUS_ONLY", "S3 debt transition has only legacy status booleans")
        return ActionCheck(False, "REJECT_MISSING_S3_DEBT_CERTIFICATE", "S3 debt certificate is not present in the state")
    certificate = _s3_debt_certificate_payload(row)
    if certificate is None:
        if str(row.get("status", "")) in {"PASS", "ACCEPT"}:
            return ActionCheck(False, "REJECT_S3_DEBT_STATUS_ONLY", "S3 debt certificate fact has status but no replay payload")
        return ActionCheck(False, "REJECT_MISSING_S3_DEBT_CERTIFICATE", "S3 debt certificate payload is missing")
    expected_hash = str(row.get("certificate_hash", "") or "")
    cert_hash = str(certificate.get("certificate_hash", "") or "")
    if expected_hash and expected_hash != cert_hash:
        return ActionCheck(False, "REJECT_S3_DEBT_HASH_MISMATCH", "S3 debt certificate hash does not match state fact")

    from .proof_action_s3_debt_cert import replay_s3_debt_certificate

    replay = replay_s3_debt_certificate(certificate, action=parsed, state=state)
    if not replay.accepted:
        if replay.status == "REJECT_S3_DEBT_HASH_MISMATCH":
            return ActionCheck(False, "REJECT_S3_DEBT_HASH_MISMATCH", replay.reason)
        if replay.status == "REJECT_S3_DEBT_STATUS_ONLY":
            return ActionCheck(False, "REJECT_S3_DEBT_STATUS_ONLY", replay.reason)
        return ActionCheck(False, "REJECT_S3_DEBT_REPLAY_FAIL", replay.reason)
    return None


def _residual_covers_gap(facts: dict[str, Any], residual_start: int, residual_end: int) -> bool:
    if residual_end <= residual_start:
        return False
    for row in _fact_rows(facts, "residual_coverage_certificate"):
        if str(row.get("status", "")) not in {"PASS", "ACCEPT"}:
            continue
        try:
            start = int(row["residual_start"])
            end = int(row["residual_end"])
            count = int(row["covered_residue_count"])
        except (KeyError, TypeError, ValueError):
            continue
        if start <= residual_start and end >= residual_end and count >= residual_end - residual_start:
            return True
    return False


def _parent_residual_covers_gap(facts: dict[str, Any], residual_start: int, residual_end: int) -> bool:
    if residual_end <= residual_start:
        return False
    for row in _fact_rows(facts, "parent_residual_certificate"):
        if str(row.get("status", "")) not in {"PASS", "ACCEPT"}:
            continue
        try:
            start = int(row["residual_start"])
            end = int(row["residual_end"])
            path_count = int(row["path_node_count"])
            ranking_num = int(row["ranking_delta_num"])
            ranking_den = int(row["ranking_delta_den"])
        except (KeyError, TypeError, ValueError):
            continue
        if start <= residual_start and end >= residual_end and path_count > 0 and 0 < ranking_num < ranking_den:
            return True
    return False


def verify_action_for_state(action: dict[str, Any] | str, state: str) -> ActionCheck:
    """Check one typed action against one canonical proof state."""

    try:
        parsed = parse_or_repair_action(action) if isinstance(action, str) else validate_action(action)
    except ProofActionError as exc:
        return ActionCheck(False, "REJECT_SYNTAX", str(exc))
    facts = parse_state_facts(state)
    action_type = parsed["type"]
    target = parsed.get("target")
    if facts.get("target") and target != facts.get("target"):
        return ActionCheck(False, "REJECT_TARGET", "action target does not match the open goal")

    if action_type == "PROVE_AFFINE_DESCENT":
        for field in ("modulus", "residue", "steps", "odd_count", "affine_b"):
            if field in facts and int(parsed[field]) != int(facts[field]):
                return ActionCheck(False, "REJECT_FIELD_MISMATCH", f"{field} does not match state")
        modulus = int(parsed["modulus"])
        residue = int(parsed["residue"])
        steps = int(parsed["steps"])
        representative = residue if residue > 0 else modulus
        bits = parity_prefix(representative, steps)
        affine_a, affine_b, affine_d = affine_for_parity_prefix(bits)
        if sum(bits) != int(parsed["odd_count"]) or affine_b != int(parsed["affine_b"]):
            return ActionCheck(False, "REJECT_AFFINE_MISMATCH", "odd count or affine offset is wrong")
        exact = verify_fixed_residue_descent_exhaustive(
            modulus=modulus,
            residue=residue,
            k=steps,
            t_limit=max(modulus * 2, representative),
        )
        if exact.status == "PASS":
            return ActionCheck(True, "ACCEPT", exact.reason, closed_obligation=True, progress=1.0)
        return ActionCheck(False, exact.status, exact.reason)

    if action_type == "UNROLL_PARITY":
        if "modulus" not in facts or "residue" not in facts:
            return ActionCheck(False, "REJECT_MISSING_STATE_FACT", "state has no residue facts")
        steps = int(parsed["steps"])
        modulus = int(facts["modulus"])
        representative = int(facts["residue"]) or modulus
        if modulus % (1 << steps) != 0:
            return ActionCheck(False, "REJECT_UNSTABLE_PARITY", "modulus does not determine this parity prefix")
        expected = "".join(str(bit) for bit in parity_prefix(representative, steps))
        if parsed["parity_word"] != expected:
            return ActionCheck(False, "REJECT_PARITY", "parity_word does not match exact Collatz unroll")
        return ActionCheck(True, "ACCEPT", "parity prefix is exact and stable", progress=0.25)

    if action_type == "CHECK_FINITE_DESCENT":
        cert = parsed["certificate"]
        n = int(cert["n"])
        steps = int(cert["steps_to_descent"])
        values = _trajectory_until(n, steps)
        if values[-1] >= n:
            return ActionCheck(False, "REJECT_NO_DESCENT", "certificate endpoint is not below n")
        expected_parity = "".join(str(bit) for bit in parity_prefix(n, steps))
        if cert["parity_word"] != expected_parity:
            return ActionCheck(False, "REJECT_PARITY", "certificate parity does not replay")
        if cert["first_descent_below_n"] != values[-1] or cert["max_value"] != max(values):
            return ActionCheck(False, "REJECT_CERTIFICATE", "descent value or max value does not replay")
        if cert["trajectory_hash"] != _trajectory_hash(values):
            return ActionCheck(False, "REJECT_HASH", "trajectory hash does not replay")
        return ActionCheck(True, "ACCEPT", "finite descent certificate replays exactly", closed_obligation=True, progress=1.0)

    if action_type == "CHECK_DEBT_DECREASE":
        debt = facts.get("debt_transition") or {}
        for field in ("branch_id", "valuation", "gain_num", "gain_den"):
            if field in debt and parsed[field] != debt[field]:
                return ActionCheck(False, "REJECT_FIELD_MISMATCH", f"{field} does not match debt transition")
        certificate_failure = _s3_debt_certificate_replays(parsed, facts, state)
        if certificate_failure is not None:
            return certificate_failure
        return ActionCheck(True, "ACCEPT", "exact S3 debt certificate replays", closed_obligation=True, progress=1.0)

    if action_type == "DERIVE_PARENT_TRANSITION":
        fact = facts.get("high_parent_successor") or {}
        for field in ("branch_id", "source_parent", "target_parent", "valuation"):
            if field in fact and parsed[field] != fact[field]:
                return ActionCheck(False, "REJECT_FIELD_MISMATCH", f"{field} does not match high-parent fact")
        certificate_failure = _transition_certificate_replays(parsed, fact, state)
        if certificate_failure is not None:
            return certificate_failure
        return ActionCheck(True, "ACCEPT", "exact symbolic parent-transition certificate replays", progress=0.6)

    if action_type == "INTRODUCE_DEBT_FUNCTION":
        if facts.get("gate", "").startswith("S3") or facts.get("goal_kind") == "debt_transition":
            return ActionCheck(True, "ACCEPT", "debt function is a valid reduced obligation", progress=0.2)
        return ActionCheck(False, "REJECT_CONTEXT", "debt functions require a debt-transition state")

    if action_type == "APPLY_LEMMA":
        known = set(str(item) for item in facts.get("known_lemmas", []))
        lemma_id = str(parsed["lemma_id"])
        if lemma_id in known or lemma_id.startswith(("L", "STRICT_", "PROVE_", "REFINE_", "TRY_")):
            return ActionCheck(True, "ACCEPT", "lemma id is known in this proof state", progress=0.1)
        return ActionCheck(False, "REJECT_UNKNOWN_LEMMA", "lemma is not available in the state")

    if action_type == "SPLIT_RESIDUE":
        modulus = int(parsed["modulus"])
        residues = list(parsed["residues"])
        if residues != sorted(residues):
            return ActionCheck(False, "REJECT_CANONICAL_ORDER", "residues must be sorted")
        if any(residue >= modulus for residue in residues):
            return ActionCheck(False, "REJECT_RESIDUE", "residue out of range")
        return ActionCheck(True, "ACCEPT", "residue split is syntactically exact", progress=0.2)

    if action_type == "LIFT_MODULUS":
        if int(parsed["to_modulus"]) % int(parsed["from_modulus"]) == 0:
            return ActionCheck(True, "ACCEPT", "modulus lift preserves residue projection", progress=0.2)
        return ActionCheck(False, "REJECT_MODULUS", "invalid modulus lift")

    if action_type == "GENERALIZE_FROM_RESIDUES":
        if parsed["residues"] == sorted(parsed["residues"]):
            return ActionCheck(True, "ACCEPT", "generalization candidate has canonical residue witnesses", progress=0.2)
        return ActionCheck(False, "REJECT_CANONICAL_ORDER", "residues must be sorted")

    if action_type == "CLOSE_BY_VERIFIER":
        strict_statuses = _fact_values(facts, "strict_verifier_status", "theorem_verifier_status", "verifier_status")
        if str(parsed["status"]) == "PASS" and "PASS" in strict_statuses:
            return ActionCheck(True, "ACCEPT", "state already carries verifier PASS", closed_obligation=True, progress=1.0)
        return ActionCheck(False, "REJECT_STRICT_VERIFIER", "strict verifier has not passed in this state")

    if action_type == "PROVE_RESIDUE_COVERAGE":
        certs = _fact_values(facts, "certificate_id", "coverage_certificate")
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "residue coverage is an S6 theorem obligation")
        if str(parsed["certificate_id"]) not in certs:
            return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "coverage certificate is not present in the state")
        if int(parsed["covered_residue_count"]) == int(parsed["modulus"]):
            return ActionCheck(True, "ACCEPT", "coverage certificate covers every residue in the stated modulus", progress=0.7)
        return ActionCheck(False, "REJECT_INCOMPLETE_COVERAGE", "coverage certificate is partial")

    if action_type == "PROVE_RESIDUAL_COVERAGE":
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "residual coverage is an S6 theorem obligation")

        certs = _fact_values(
            facts,
            "certificate_id",
            "coverage_certificate",
            "residual_coverage_certificate",
        )

        certificate_id = str(parsed["certificate_id"])
        parent_certificate_id = str(parsed["parent_certificate_id"])
        if certificate_id not in certs:
            return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "residual coverage certificate is not present in the state")
        if parent_certificate_id not in certs:
            return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "parent coverage certificate is not present in the state")

        residual_start = int(parsed["residual_start"])
        residual_end = int(parsed["residual_end"])
        covered_count = int(parsed["covered_residue_count"])

        if residual_end <= residual_start:
            return ActionCheck(False, "REJECT_RESIDUAL_RANGE", "empty residual range")

        if covered_count != residual_end - residual_start:
            return ActionCheck(False, "REJECT_INCOMPLETE_RESIDUAL_COVERAGE", "residual coverage count does not match residual range")

        blocker_ids = _fact_values(facts, "blocker_id")
        expected_fragment = f"residual:{residual_start}:{residual_end}"
        expected_underscore = f"residual_{residual_start}_{residual_end}"
        if not any(expected_fragment in blocker_id or expected_underscore in blocker_id for blocker_id in blocker_ids) and expected_fragment not in certificate_id and expected_underscore not in certificate_id:
            return ActionCheck(False, "REJECT_RESIDUAL_MISMATCH", "certificate does not match the open residual blocker")

        return ActionCheck(
            True,
            "ACCEPT",
            "residual coverage certificate closes the exact uncovered residue range",
            closed_obligation=True,
            progress=1.0,
        )

    if action_type == "PROVE_PARENT_RESIDUAL_COVERAGE":
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "parent residual coverage is an S6 theorem obligation")

        certs = _fact_values(
            facts,
            "certificate_id",
            "coverage_certificate",
            "parent_residual_certificate",
        )
        certificate_id = str(parsed["certificate_id"])
        parent_certificate_id = str(parsed["parent_certificate_id"])
        if certificate_id not in certs:
            return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "parent residual certificate is not present in the state")
        if parent_certificate_id not in certs:
            return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "parent coverage certificate is not present in the state")

        modulus = int(parsed["modulus"])
        parent_level = int(parsed["parent_level"])
        residual_start = int(parsed["residual_start"])
        residual_end = int(parsed["residual_end"])
        if modulus != 1 << parent_level or residual_start != modulus - 1 or residual_end != modulus:
            return ActionCheck(False, "REJECT_PARENT_RESIDUAL_DOMAIN", "residual range is not the exact P_a class 2^a*q - 1")
        if int(parsed["path_node_count"]) <= 0:
            return ActionCheck(False, "REJECT_PARENT_PATH", "parent residual certificate has no closed dependency path")
        if int(parsed["s3_dependency_count"]) <= 0 or int(parsed["s4_dependency_count"]) <= 0 or int(parsed["s6_dependency_count"]) <= 0 or int(parsed["no_escape_dependency_count"]) <= 0:
            return ActionCheck(False, "REJECT_PARENT_DEPENDENCIES", "parent residual certificate is missing accepted S3/S4/S6/no-escape dependencies")
        if int(parsed["ranking_delta_num"]) >= int(parsed["ranking_delta_den"]):
            return ActionCheck(False, "REJECT_PARENT_RANKING", "parent residual ranking does not strictly decrease")

        return ActionCheck(
            True,
            "ACCEPT",
            "parent-state transition/ranking certificate closes the residual P_a class",
            closed_obligation=True,
            progress=1.0,
        )

    if action_type == "PROVE_GLOBAL_DESCENT_INDUCTION":
        lemmas = _fact_values(facts, "lemma_id") | set(str(item) for item in facts.get("known_lemmas", []))
        depends = set(str(item) for item in parsed["depends_on"])
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "global induction requires an S6 state")
        if str(parsed["lemma_id"]) not in lemmas:
            return ActionCheck(False, "REJECT_UNKNOWN_LEMMA", "descent induction lemma is not proposed in this state")
        if depends and depends <= lemmas:
            return ActionCheck(True, "ACCEPT", "global descent induction dependencies are available", progress=0.8)
        return ActionCheck(False, "REJECT_MISSING_DEPENDENCY", "not all induction dependencies are available")

    if action_type == "CLOSE_WELL_FOUNDED_INDUCTION":
        certs = _fact_values(facts, "certificate_id", "base_case_certificate")
        lemmas = _fact_values(facts, "lemma_id", "descent_lemma") | set(str(item) for item in facts.get("known_lemmas", []))
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "well-founded closure requires an S6 state")
        if str(parsed["measure"]) != "n":
            return ActionCheck(False, "REJECT_MEASURE", "only the natural-number measure n is currently verified")
        if str(parsed["descent_lemma"]) in lemmas and str(parsed["base_case_certificate"]) in certs:
            return ActionCheck(True, "ACCEPT", "well-founded induction closes from descent lemma and base case", closed_obligation=True, progress=1.0)
        return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "missing descent lemma or base case certificate")

    if action_type == "CERTIFY_NO_ESCAPE_BRANCH":
        branches = _fact_values(facts, "branch_id")
        certs = _fact_values(facts, "certificate_id", "no_escape_certificate")
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "no-escape certificates require an S6 state")
        if str(parsed["branch_id"]) in branches and str(parsed["certificate_id"]) in certs:
            return ActionCheck(True, "ACCEPT", "no-escape branch certificate is present", progress=0.6)
        return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "branch or no-escape certificate is absent")

    if action_type == "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM":
        certs = _fact_values(facts, "certificate_id", "coverage_certificate")
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "global theorem linking requires an S6 state")
        if str(parsed["local_gate"]) in {"S3", "S4"} and str(parsed["lifting_gate"]) == "S4" and str(parsed["coverage_certificate"]) in certs:
            return ActionCheck(True, "ACCEPT", "local descent and lifting gates are linked to a coverage certificate", progress=0.9)
        return ActionCheck(False, "REJECT_GATE_LINK", "missing S3/S4 link or coverage certificate")

    if action_type == "LIFT_LOCAL_TO_PARAMETRIC_FAMILY":
        lemmas = _fact_values(facts, "lemma_id", "local_lemma") | set(str(item) for item in facts.get("known_lemmas", []))
        certs = _fact_values(facts, "certificate_id", "lifting_certificate")
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "parametric lift requires an S6 state")
        if str(parsed["local_lemma"]) in lemmas and str(parsed["lifting_certificate"]) in certs:
            return ActionCheck(True, "ACCEPT", "local lemma lifts to the stated parametric family", progress=0.7)
        return ActionCheck(False, "REJECT_MISSING_CERTIFICATE", "local lemma or lifting certificate is absent")

    if action_type == "CLOSE_STRICT_THEOREM_BLOCKER":
        blockers = _fact_values(facts, "blocker_id")
        lemmas = _fact_values(facts, "lemma_id") | set(str(item) for item in facts.get("known_lemmas", []))
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "strict theorem blockers are S6 obligations")
        if str(parsed["blocker_id"]) in blockers and str(parsed["lemma_id"]) in lemmas:
            return ActionCheck(True, "ACCEPT", "strict theorem blocker is discharged by an available lemma", closed_obligation=True, progress=1.0)
        return ActionCheck(False, "REJECT_OPEN_BLOCKER", "blocker id or closing lemma is not available")

    if action_type == "PROPOSE_S6_LEMMA":
        lemma_ids = _fact_values(facts, "lemma_id") | set(str(item) for item in facts.get("known_lemmas", []))
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "S6 lemmas require an S6 state")
        if str(parsed["lemma_id"]) in lemma_ids:
            return ActionCheck(True, "ACCEPT", "S6 lemma proposal matches a generated theorem obligation", progress=0.3)
        return ActionCheck(False, "REJECT_UNKNOWN_LEMMA", "S6 lemma was not generated from known blockers")

    if action_type == "VERIFY_S6_LEMMA":
        lemma_ids = _fact_values(facts, "lemma_id") | set(str(item) for item in facts.get("known_lemmas", []))
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "S6 lemma verification requires an S6 state")
        if str(parsed["lemma_id"]) not in lemma_ids:
            return ActionCheck(False, "REJECT_UNKNOWN_LEMMA", "lemma id is not available")
        certificate_failure = _s6_lemma_certificate_replays(parsed, facts)
        if certificate_failure is not None:
            return certificate_failure
        if str(parsed.get("status", "PASS")) in {"ACCEPT", "PASS"}:
            return ActionCheck(True, "ACCEPT", "S6 lemma certificate and dependencies replay", progress=0.8)
        return ActionCheck(False, "REJECT_S6_LEMMA", "S6 lemma verifier did not accept this lemma")

    if action_type == "COMPOSE_GATE_PROOF":
        depends = set(str(item) for item in parsed["depends_on"])
        available = _fact_values(facts, "lemma_id", "certificate_id", "proof_id") | set(str(item) for item in facts.get("known_lemmas", []))
        if not _s6_context(facts):
            return ActionCheck(False, "REJECT_CONTEXT", "gate proof composition requires an S6 state")
        if depends and depends <= available:
            return ActionCheck(True, "ACCEPT", "gate proof components compose into an S6 proof obligation", progress=1.0)
        return ActionCheck(False, "REJECT_MISSING_DEPENDENCY", "gate proof dependencies are incomplete")

    if action_type == "ABANDON_BRANCH":
        return ActionCheck(True, "ACCEPT_CONTROL", "branch abandoned; no proof progress", progress=0.0)

    return ActionCheck(False, "REJECT_UNKNOWN", f"unhandled action type {action_type}")


def legal_action_candidates_from_state(state: str, *, max_candidates: int = 64) -> list[dict[str, Any]]:
    """Enumerate typed legal action candidates implied by structured state facts."""

    facts = parse_state_facts(state)
    target = str(facts.get("target", "goal_0"))
    candidates: list[dict[str, Any]] = []
    if "certificate" in facts:
        candidates.append({"type": "CHECK_FINITE_DESCENT", "target": target, "certificate": facts["certificate"]})
    if facts.get("goal_kind") == "residue_descent" or {"modulus", "residue", "steps", "odd_count", "affine_b"} <= set(facts):
        candidates.append(
            {
                "type": "PROVE_AFFINE_DESCENT",
                "target": target,
                "modulus": int(facts["modulus"]),
                "residue": int(facts["residue"]),
                "steps": int(facts["steps"]),
                "odd_count": int(facts["odd_count"]),
                "affine_b": int(facts["affine_b"]),
            }
        )
        if "parity_word" in facts:
            candidates.append(
                {
                    "type": "UNROLL_PARITY",
                    "target": target,
                    "steps": int(facts["steps"]),
                    "parity_word": str(facts["parity_word"]),
                }
            )
        modulus = int(facts["modulus"])
        residue = int(facts["residue"])
        candidates.append(
            {
                "type": "LIFT_MODULUS",
                "target": target,
                "from_modulus": modulus,
                "to_modulus": modulus * 2,
                "residue": residue,
            }
        )
        sibling = (residue + modulus // 2) % modulus if modulus > 2 else (residue + 1) % modulus
        residues = sorted({residue, sibling})
        candidates.append(
            {
                "type": "GENERALIZE_FROM_RESIDUES",
                "target": target,
                "modulus": modulus,
                "residues": residues,
                "lemma_id": f"residue_family_mod_{modulus}",
            }
        )
        if len(residues) > 1:
            candidates.append({"type": "SPLIT_RESIDUE", "target": target, "modulus": modulus, "residues": residues})
    if "debt_transition" in facts:
        debt = facts["debt_transition"]
        candidates.append(
            {
                "type": "CHECK_DEBT_DECREASE",
                "target": target,
                "branch_id": str(debt["branch_id"]),
                "gain_num": int(debt["gain_num"]),
                "gain_den": int(debt["gain_den"]),
                "valuation": int(debt["valuation"]),
            }
        )
        candidates.append(
            {
                "type": "INTRODUCE_DEBT_FUNCTION",
                "target": target,
                "function_id": "mixed_log_gain_rank",
                "variables": ["parent_level", "rho_mod_3a", "log2_gain_bound"],
            }
        )
        candidates.append(
            {
                "type": "APPLY_LEMMA",
                "target": target,
                "lemma_id": "mixed_modulus_debt_transition_exactness",
                "bindings": {"branch_id": str(debt.get("branch_id", ""))},
            }
        )
    if "high_parent_successor" in facts:
        fact = facts["high_parent_successor"]
        transition_certificate = _decode_json_payload(fact.get("transition_certificate"))
        if transition_certificate is not None:
            candidates.append(
                {
                    "type": "DERIVE_PARENT_TRANSITION",
                    "target": target,
                    "branch_id": str(fact["branch_id"]),
                    "source_parent": int(fact["source_parent"]),
                    "target_parent": int(fact["target_parent"]),
                    "valuation": int(fact["valuation"]),
                    "transition_certificate": transition_certificate,
                }
            )
        candidates.append(
            {
                "type": "APPLY_LEMMA",
                "target": target,
                "lemma_id": "high_parent_successor_exactness",
                "bindings": {"branch_id": str(fact.get("branch_id", ""))},
            }
        )
    for lemma in facts.get("known_lemmas", [])[:8]:
        if lemma:
            candidates.append({"type": "APPLY_LEMMA", "target": target, "lemma_id": str(lemma), "bindings": {}})
    if _s6_context(facts):
        blockers = list(_fact_values(facts, "blocker_id"))
        lemma_ids = list(_fact_values(facts, "lemma_id") | set(str(item) for item in facts.get("known_lemmas", [])))
        certs = list(
            _fact_values(
                facts,
                "certificate_id",
                "coverage_certificate",
                "base_case_certificate",
                "lifting_certificate",
                "no_escape_certificate",
                "residual_coverage_certificate",
                "parent_residual_certificate",
            )
        )
        coverage = next((cert for cert in certs if "coverage" in cert), None)
        base_cert = next((cert for cert in certs if "base" in cert), None)
        lifting_cert = next((cert for cert in certs if "lift" in cert), None)
        no_escape_cert = next((cert for cert in certs if "escape" in cert), None)
        residual_rows = _fact_rows(facts, "residual_coverage_certificate")
        parent_residual_rows = _fact_rows(facts, "parent_residual_certificate")
        s6_lemma_certificate_rows = _fact_rows(facts, "s6_lemma_certificate")
        if lemma_ids:
            lemma = lemma_ids[0]
            candidates.append({"type": "PROPOSE_S6_LEMMA", "target": target, "lemma_id": lemma, "statement": "generated S6 obligation candidate"})
            for cert_row in s6_lemma_certificate_rows:
                if str(cert_row.get("lemma_id", "")) != lemma:
                    continue
                if str(cert_row.get("status", "")) not in {"PASS", "ACCEPT"}:
                    continue
                candidates.append(
                    {
                        "type": "VERIFY_S6_LEMMA",
                        "target": target,
                        "lemma_id": lemma,
                        "verifier": "s6_lemma_certificate_replay",
                        "status": "PASS",
                        "certificate_id": str(cert_row.get("certificate_id", "")),
                        "certificate_hash": str(cert_row.get("certificate_hash", "")),
                    }
                )
            candidates.append({"type": "PROVE_GLOBAL_DESCENT_INDUCTION", "target": target, "lemma_id": lemma, "depends_on": [lemma]})
            if blockers:
                candidates.append({"type": "CLOSE_STRICT_THEOREM_BLOCKER", "target": target, "blocker_id": blockers[0], "lemma_id": lemma})
            if coverage is not None:
                candidates.append(
                    {
                        "type": "PROVE_RESIDUE_COVERAGE",
                        "target": target,
                        "modulus": int(facts.get("coverage_modulus", facts.get("modulus", 2))),
                        "covered_residue_count": int(facts.get("covered_residue_count", facts.get("coverage_modulus", facts.get("modulus", 2)))),
                        "certificate_id": coverage,
                    }
                )
                candidates.append({"type": "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM", "target": target, "local_gate": "S3", "lifting_gate": "S4", "coverage_certificate": coverage})
                candidates.append({"type": "COMPOSE_GATE_PROOF", "target": target, "proof_id": f"compose_{lemma}", "depends_on": [lemma, coverage]})
            if base_cert is not None:
                candidates.append({"type": "CLOSE_WELL_FOUNDED_INDUCTION", "target": target, "measure": "n", "descent_lemma": lemma, "base_case_certificate": base_cert})
            if lifting_cert is not None:
                candidates.append({"type": "LIFT_LOCAL_TO_PARAMETRIC_FAMILY", "target": target, "local_lemma": lemma, "family_id": "s6_parametric_family", "lifting_certificate": lifting_cert})
            if blockers and no_escape_cert is not None:
                candidates.append({"type": "CERTIFY_NO_ESCAPE_BRANCH", "target": target, "branch_id": blockers[0], "certificate_id": no_escape_cert})
            for residual in residual_rows:
                try:
                    residual_start = int(residual["residual_start"])
                    residual_end = int(residual["residual_end"])
                except (KeyError, TypeError, ValueError):
                    continue
                candidates.append(
                    {
                        "type": "PROVE_RESIDUAL_COVERAGE",
                        "target": target,
                        "certificate_id": str(residual["certificate_id"]),
                        "parent_certificate_id": str(residual["parent_certificate_id"]),
                        "modulus": int(residual["modulus"]),
                        "residual_start": residual_start,
                        "residual_end": residual_end,
                        "covered_residue_count": int(residual.get("covered_residue_count", residual_end - residual_start)),
                        "leaf_certificate_count": int(residual.get("leaf_certificate_count", 1)),
                        "certificate_hash": str(residual.get("certificate_hash", "")),
                    }
                )
            for residual in parent_residual_rows:
                try:
                    residual_start = int(residual["residual_start"])
                    residual_end = int(residual["residual_end"])
                except (KeyError, TypeError, ValueError):
                    continue
                candidates.append(
                    {
                        "type": "PROVE_PARENT_RESIDUAL_COVERAGE",
                        "target": target,
                        "certificate_id": str(residual["certificate_id"]),
                        "parent_certificate_id": str(residual["parent_certificate_id"]),
                        "residual_certificate_id": str(residual["residual_certificate_id"]),
                        "parent_level": int(residual["parent_level"]),
                        "modulus": int(residual["modulus"]),
                        "residual_start": residual_start,
                        "residual_end": residual_end,
                        "path_node_count": int(residual["path_node_count"]),
                        "s3_dependency_count": int(residual["s3_dependency_count"]),
                        "s4_dependency_count": int(residual["s4_dependency_count"]),
                        "s6_dependency_count": int(residual["s6_dependency_count"]),
                        "no_escape_dependency_count": int(residual["no_escape_dependency_count"]),
                        "ranking_delta_num": int(residual["ranking_delta_num"]),
                        "ranking_delta_den": int(residual["ranking_delta_den"]),
                        "certificate_hash": str(residual.get("certificate_hash", "")),
                    }
                )
    if facts.get("gate", "").startswith(("S1", "S2", "S3", "S4", "S6")):
        candidates.append({"type": "SPLIT_RESIDUE", "target": target, "modulus": 2, "residues": [0, 1]})
        candidates.append(
            {
                "type": "CLOSE_BY_VERIFIER",
                "target": target,
                "verifier": "strict_collatz_descent",
                "status": "PASS",
            }
        )
    candidates.append({"type": "ABANDON_BRANCH", "target": target, "reason": "search_budget_or_ranker_pruned"})

    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for candidate in candidates:
        try:
            text = serialize_action(candidate)
        except ProofActionError:
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append(parse_action(text))
        if len(out) >= max_candidates:
            break
    return out


def dedupe_candidates(candidates: list[dict[str, Any]], *, max_candidates: int | None = None) -> list[dict[str, Any]]:
    """Deduplicate candidates by canonical action text while preserving order."""

    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for candidate in candidates:
        try:
            text = serialize_action(candidate)
        except ProofActionError:
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append(parse_action(text))
        if max_candidates is not None and len(out) >= max_candidates:
            break
    return out


def is_degenerate_output(text: str) -> bool:
    clean = text.strip()
    if not clean:
        return True
    if len(set(clean)) <= 2 and len(clean) >= 8:
        return True
    pieces = re.findall(r'"[^"]+"|[A-Za-z_]+|\d+|[{}[\]:,]', clean)
    if len(pieces) >= 8:
        most_common = max(pieces.count(piece) for piece in set(pieces))
        return most_common / len(pieces) > 0.75
    return False


def serialize_candidates(candidates: list[dict[str, Any]]) -> list[str]:
    return [serialize_action(candidate) for candidate in candidates]
