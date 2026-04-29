"""Candidate high-parent rules for RUN-066.

Rules generated here are hypotheses.  They become proof artifacts only if
`high_parent_certificate_verifier` accepts them with exact arithmetic.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


RULE_TYPES = {
    "DIRECT_ROOT_DESCENT",
    "ROOT_DEBT_DECREASE",
    "LOWER_DEBT_ENTRY",
    "CERTIFIED_MARGIN_DESCENT",
    "RESIDUE_SPLIT_FAMILY",
}


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _with_hash(rule: dict[str, Any]) -> dict[str, Any]:
    rule["candidate_rule_hash"] = stable_hash({key: value for key, value in rule.items() if key != "candidate_rule_hash"})
    return rule


def direct_root_descent_candidate() -> dict[str, Any]:
    return _with_hash(
        {
            "kind": "HIGH_PARENT_CANDIDATE_RULE",
            "rule_type": "DIRECT_ROOT_DESCENT",
            "candidate_id": "direct_p32_entry_below_root",
            "claimed_domain": "d >= 1 and q > 0 and q % 2 = 1",
            "iterate_statement": "After 2*d forced steps, P_(32+d)(q) reaches P32(3^d*q).",
            "required_inequality": "2^32*3^d*q - 1 < 2^(32+d)*q - 1",
            "equivalent_inequality": "3^d < 2^d",
            "expected_verifier_status": "REJECT",
        }
    )


def root_debt_decrease_candidate(*, p32_outgoing_count: int) -> dict[str, Any]:
    return _with_hash(
        {
            "kind": "HIGH_PARENT_CANDIDATE_RULE",
            "rule_type": "ROOT_DEBT_DECREASE",
            "candidate_id": "p32_transition_decreases_high_parent_debt",
            "claimed_domain": "d >= 1 and q > 0 and q % 2 = 1 after entry into P32(3^d*q)",
            "p32_outgoing_s4_transition_count": p32_outgoing_count,
            "required_witness": "a P32 outgoing iterate family with exact target debt d' < d or direct root-relative descent",
            "expected_verifier_status": "REJECT" if p32_outgoing_count == 0 else "UNKNOWN",
        }
    )


def certified_margin_candidate(*, candidate_count: int, passing_count: int) -> dict[str, Any]:
    return _with_hash(
        {
            "kind": "HIGH_PARENT_CANDIDATE_RULE",
            "rule_type": "CERTIFIED_MARGIN_DESCENT",
            "candidate_id": "reuse_existing_p32_root_relative_margin",
            "claimed_domain": "d >= 1 and q > 0 and q % 2 = 1",
            "candidate_margin_count": candidate_count,
            "passing_margin_count": passing_count,
            "required_witness": "certified P32 continuation with shrink factor < (2/3)^d",
            "expected_verifier_status": "ACCEPT" if passing_count > 0 else "REJECT",
        }
    )


def lower_debt_entry_candidate() -> dict[str, Any]:
    return _with_hash(
        {
            "kind": "HIGH_PARENT_CANDIDATE_RULE",
            "rule_type": "LOWER_DEBT_ENTRY",
            "candidate_id": "enter_previously_certified_lower_debt_family",
            "claimed_domain": "d >= 1 and q > 0 and q % 2 = 1",
            "required_witness": "exact transition into a high-parent certificate with debt d' < d",
            "known_lower_debt_certificate_count": 0,
            "expected_verifier_status": "REJECT",
        }
    )


def sample_residue_family_candidate(feature_rows: list[dict[str, Any]]) -> dict[str, Any]:
    descended = [row for row in feature_rows if row.get("descent_found_within_max_steps")]
    first = descended[0] if descended else (feature_rows[0] if feature_rows else {})
    return _with_hash(
        {
            "kind": "HIGH_PARENT_CANDIDATE_RULE",
            "rule_type": "RESIDUE_SPLIT_FAMILY",
            "candidate_id": "sample_observed_residue_family",
            "claimed_domain": "sampled d/q rows only",
            "sample_only": True,
            "sample_d": first.get("d"),
            "sample_q": first.get("q"),
            "sample_first_descent_below_root": first.get("first_descent_below_root"),
            "required_witness": "symbolic residue coverage plus exact inequality for all q in the residue family",
            "expected_verifier_status": "REJECT",
        }
    )


def generate_candidate_rules(
    *,
    feature_rows: list[dict[str, Any]],
    margin_report: dict[str, Any],
    p32_outgoing_count: int,
) -> list[dict[str, Any]]:
    inventory = margin_report.get("available_certificate_inventory", {}) if isinstance(margin_report, dict) else {}
    candidate_count = int(inventory.get("candidate_root_relative_margin_count", 0) or 0)
    passing_count = int(inventory.get("passing_root_relative_margin_count", 0) or 0)
    return [
        direct_root_descent_candidate(),
        root_debt_decrease_candidate(p32_outgoing_count=p32_outgoing_count),
        lower_debt_entry_candidate(),
        certified_margin_candidate(candidate_count=candidate_count, passing_count=passing_count),
        sample_residue_family_candidate(feature_rows),
    ]
