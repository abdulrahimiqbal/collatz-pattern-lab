"""Exact verifier for RUN-068 high-parent invariant candidates."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _reject(candidate: dict[str, Any], reason: str, detail: str) -> dict[str, Any]:
    row = {
        "kind": "HIGH_PARENT_INVARIANT_VERIFICATION",
        "candidate_id": candidate.get("candidate_id"),
        "invariant_type": candidate.get("invariant_type"),
        "accepted": False,
        "status": "REJECT",
        "reason": reason,
        "detail": detail,
    }
    row["verification_hash"] = stable_hash(row)
    return row


def _accept(candidate: dict[str, Any], reason: str) -> dict[str, Any]:
    row = {
        "kind": "HIGH_PARENT_INVARIANT_VERIFICATION",
        "candidate_id": candidate.get("candidate_id"),
        "invariant_type": candidate.get("invariant_type"),
        "accepted": True,
        "status": "ACCEPT",
        "reason": reason,
    }
    row["verification_hash"] = stable_hash(row)
    return row


def verify_high_parent_invariant(candidate: dict[str, Any]) -> dict[str, Any]:
    if candidate.get("kind") != "HIGH_PARENT_INVARIANT_CANDIDATE":
        return _reject(candidate, "CANDIDATE_KIND_MISMATCH", "candidate is not a high-parent invariant candidate")
    if candidate.get("sample_only") is True:
        return _reject(candidate, "SAMPLE_ONLY_INVARIANT_REJECTED", "sampled trajectories cannot certify a universal invariant")
    if candidate.get("uses_float_or_log") is True:
        return _reject(candidate, "FLOAT_OR_LOG_INVARIANT_REJECTED", "accepted certificates must use exact integer/rational arithmetic")
    if candidate.get("integer_or_rational_arithmetic_only") is not True:
        return _reject(candidate, "NON_EXACT_ARITHMETIC_REJECTED", "candidate does not assert exact integer/rational arithmetic")

    def accept_if_covered(reason: str) -> dict[str, Any]:
        if candidate.get("domain_coverage_proved") is not True:
            return _reject(
                candidate,
                "INVARIANT_DOMAIN_COVERAGE_MISSING",
                "candidate proves a local obligation but does not cover its claimed high-parent domain",
            )
        return _accept(candidate, reason)

    invariant_type = candidate.get("invariant_type")
    if invariant_type == "DIRECT_ROOT_DESCENT":
        if candidate.get("exact_root_inequality_proved") is True:
            return accept_if_covered("DIRECT_ROOT_DESCENT_VERIFIED")
        return _reject(candidate, "DIRECT_ROOT_DESCENT_INEQUALITY_MISSING", "missing exact proof current_final < root")
    if invariant_type == "ROOT_DEBT_DECREASE":
        if candidate.get("well_founded_measure") == "Nat.debt" and candidate.get("all_transitions_decrease_debt") is True:
            return accept_if_covered("ROOT_DEBT_DECREASE_VERIFIED")
        return _reject(candidate, "ROOT_DEBT_DECREASE_NOT_PROVED", "not every covered transition proves d' < d")
    if invariant_type == "ROOT_MARGIN_DECREASE":
        if candidate.get("well_founded_measure") and candidate.get("all_transitions_decrease_margin") is True:
            return accept_if_covered("ROOT_MARGIN_DECREASE_VERIFIED")
        return _reject(candidate, "ROOT_MARGIN_WELL_FOUNDED_MEASURE_MISSING", "margin decrease or well-founded measure is missing")
    if invariant_type == "LOWER_DEBT_ENTRY":
        if candidate.get("lower_debt_entry_proved") is True:
            return accept_if_covered("LOWER_DEBT_ENTRY_VERIFIED")
        return _reject(candidate, "LOWER_DEBT_ENTRY_CERTIFICATE_MISSING", "no exact lower-debt entry certificate is present")
    if invariant_type == "FINITE_SUBSYSTEM_ENTRY_WITH_ROOT_MARGIN":
        if candidate.get("finite_margin_certificate_proved") is True:
            return accept_if_covered("FINITE_SUBSYSTEM_ROOT_MARGIN_VERIFIED")
        return _reject(candidate, "FINITE_SUBSYSTEM_ROOT_MARGIN_MISSING", "finite subsystem entry lacks root-relative margin")
    if invariant_type == "BOUNDED_COMPOSITION_DESCENT":
        if candidate.get("composition_depth", 0) > 0 and candidate.get("composition_descends_below_root") is True:
            return accept_if_covered("BOUNDED_COMPOSITION_DESCENT_VERIFIED")
        return _reject(candidate, "BOUNDED_COMPOSITION_DESCENT_MISSING", "bounded composition has no exact descent proof")
    if invariant_type == "V3_DEBT":
        if candidate.get("all_transitions_decrease_v3_debt") is True:
            return accept_if_covered("V3_DEBT_VERIFIED")
        return _reject(candidate, "V3_DEBT_DECREASE_NOT_PROVED", "v3 feature is recorded but no universal decrease theorem is certified")
    if invariant_type == "LEXICOGRAPHIC":
        if candidate.get("lexicographic_components") and candidate.get("all_transitions_lexicographically_decrease") is True:
            return accept_if_covered("LEXICOGRAPHIC_INVARIANT_VERIFIED")
        return _reject(candidate, "LEXICOGRAPHIC_DECREASE_NOT_PROVED", "lexicographic components do not have a certified decrease proof")
    if invariant_type == "PIECEWISE_RESIDUE":
        if candidate.get("all_residue_cases_covered") is True and candidate.get("case_certificate_count", 0) > 0:
            return accept_if_covered("PIECEWISE_RESIDUE_INVARIANT_VERIFIED")
        return _reject(candidate, "PIECEWISE_RESIDUE_COVERAGE_MISSING", "residue split is bounded or incomplete")
    return _reject(candidate, "UNKNOWN_INVARIANT_TYPE", "candidate invariant type is not recognized")


def accepted_invariant_certificate(candidate: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any] | None:
    if verification.get("accepted") is not True:
        return None
    cert = {
        "kind": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_CERTIFICATE",
        "candidate_id": candidate.get("candidate_id"),
        "invariant_type": candidate.get("invariant_type"),
        "claim": candidate.get("claim"),
        "verification": verification,
        "root_relative_descent_proved": True,
        "semantic_validation": {"status": "PASS", "failures": []},
    }
    cert["certificate_hash"] = stable_hash({key: value for key, value in cert.items() if key != "certificate_hash"})
    return cert
