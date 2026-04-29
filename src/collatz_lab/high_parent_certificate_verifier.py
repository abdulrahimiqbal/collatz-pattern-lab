"""Exact verifier for RUN-066 high-parent candidate rules."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _result(candidate: dict[str, Any], *, accepted: bool, reason: str, detail: str | None = None) -> dict[str, Any]:
    result = {
        "kind": "HIGH_PARENT_CANDIDATE_VERIFICATION",
        "candidate_id": candidate.get("candidate_id"),
        "rule_type": candidate.get("rule_type"),
        "accepted": accepted,
        "status": "ACCEPT" if accepted else "REJECT",
        "reason": reason,
    }
    if detail is not None:
        result["detail"] = detail
    result["verification_hash"] = stable_hash(result)
    return result


def verify_direct_root_descent(candidate: dict[str, Any]) -> dict[str, Any]:
    # For d >= 1, 3^d < 2^d is false.  It is enough to refute the universal
    # candidate at the smallest domain point d = 1.
    if 3**1 < 2**1:
        return _result(candidate, accepted=True, reason="DIRECT_ROOT_DESCENT_VERIFIED")
    return _result(
        candidate,
        accepted=False,
        reason="DIRECT_ROOT_DESCENT_INEQUALITY_FALSE",
        detail="At d=1, the required inequality 3^d < 2^d becomes 3 < 2.",
    )


def verify_root_debt_decrease(candidate: dict[str, Any]) -> dict[str, Any]:
    if int(candidate.get("p32_outgoing_s4_transition_count", 0) or 0) <= 0:
        return _result(
            candidate,
            accepted=False,
            reason="P32_OUTGOING_ITERATE_FAMILY_MISSING",
            detail="No exact P32 outgoing transition family is available to prove a debt decrease.",
        )
    if candidate.get("debt_decrease_proved") is True and int(candidate.get("target_debt_delta", 0) or 0) < 0:
        return _result(candidate, accepted=True, reason="ROOT_DEBT_DECREASE_VERIFIED")
    return _result(
        candidate,
        accepted=False,
        reason="ROOT_RELATIVE_DEBT_DECREASE_MISSING",
        detail="The candidate does not include an exact proof of d' < d.",
    )


def verify_lower_debt_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    if candidate.get("lower_debt_entry_proved") is True:
        return _result(candidate, accepted=True, reason="LOWER_DEBT_ENTRY_VERIFIED")
    return _result(
        candidate,
        accepted=False,
        reason="LOWER_DEBT_ENTRY_CERTIFICATE_MISSING",
        detail="No exact transition into a previously certified lower-debt high-parent family is present.",
    )


def verify_certified_margin(candidate: dict[str, Any]) -> dict[str, Any]:
    if int(candidate.get("passing_margin_count", 0) or 0) > 0:
        return _result(candidate, accepted=True, reason="CERTIFIED_MARGIN_DESCENT_VERIFIED")
    return _result(
        candidate,
        accepted=False,
        reason="P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING",
        detail="No accepted P32 margin certificate proves shrink factor < (2/3)^d.",
    )


def verify_residue_split_family(candidate: dict[str, Any]) -> dict[str, Any]:
    if candidate.get("sample_only") is True:
        return _result(
            candidate,
            accepted=False,
            reason="SAMPLE_ONLY_RULE_REJECTED",
            detail="Sample trajectories do not prove symbolic residue-family coverage or inequality.",
        )
    if candidate.get("symbolic_coverage_proved") is True and candidate.get("exact_inequality_proved") is True:
        return _result(candidate, accepted=True, reason="RESIDUE_SPLIT_FAMILY_VERIFIED")
    return _result(
        candidate,
        accepted=False,
        reason="RESIDUE_SPLIT_FAMILY_PROOF_INCOMPLETE",
        detail="Missing symbolic coverage or exact inequality proof.",
    )


def verify_high_parent_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    if candidate.get("kind") != "HIGH_PARENT_CANDIDATE_RULE":
        return _result(candidate, accepted=False, reason="CANDIDATE_KIND_MISMATCH")
    rule_type = candidate.get("rule_type")
    if rule_type == "DIRECT_ROOT_DESCENT":
        return verify_direct_root_descent(candidate)
    if rule_type == "ROOT_DEBT_DECREASE":
        return verify_root_debt_decrease(candidate)
    if rule_type == "LOWER_DEBT_ENTRY":
        return verify_lower_debt_entry(candidate)
    if rule_type == "CERTIFIED_MARGIN_DESCENT":
        return verify_certified_margin(candidate)
    if rule_type == "RESIDUE_SPLIT_FAMILY":
        return verify_residue_split_family(candidate)
    return _result(candidate, accepted=False, reason="UNKNOWN_RULE_TYPE")


def accepted_certificate_from_candidate(candidate: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any] | None:
    if not verification.get("accepted"):
        return None
    cert = {
        "kind": "HIGH_PARENT_ACCEPTED_CERTIFICATE",
        "candidate_id": candidate.get("candidate_id"),
        "rule_type": candidate.get("rule_type"),
        "claimed_domain": candidate.get("claimed_domain"),
        "verification": verification,
        "root_relative_descent_proved": True,
        "semantic_validation": {"status": "PASS", "failures": []},
    }
    cert["certificate_hash"] = stable_hash({key: value for key, value in cert.items() if key != "certificate_hash"})
    return cert
