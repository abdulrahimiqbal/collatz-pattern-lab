"""CEGAR driver for RUN-066 high-parent proof search."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .high_parent_candidate_rules import generate_candidate_rules
from .high_parent_certificate_verifier import (
    accepted_certificate_from_candidate,
    verify_high_parent_candidate,
)
from .high_parent_lab import build_high_parent_feature_table
from .proof_action_parametric_entry_coverage import read_json, read_jsonl


RUN_ID = "RUN-066-high-parent-self-improving-proof-search"
SCHEMA = "collatz_lab.run066_high_parent_self_improving"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def write_json(data: Any, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _p32_outgoing_count(semantic_witnesses: list[dict[str, Any]]) -> int:
    return sum(
        1
        for row in semantic_witnesses
        if row.get("kind") == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"
        and int(row.get("source_parent", 0) or 0) == 32
    )


def _uncovered_domain(failed_rule_classes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "UNCOVERED_HIGH_PARENT_DOMAIN",
        "domain_id": "high_parent_all_d_ge_1_q_odd_positive",
        "family_id": "odd_entry_parent_levels_ge_33",
        "d_range": {"type": "tail", "lower_bound": 1},
        "parent_level_range": {"type": "tail", "lower_bound": 33},
        "q_domain": "q > 0 and q % 2 = 1",
        "example": {"d": 1, "a": 33, "q": 1, "n_expr": "2^33 - 1"},
        "failure_reason": "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING",
        "failed_rule_classes": failed_rule_classes,
    }


def _minimal_obstruction(uncovered: list[dict[str, Any]], verifications: list[dict[str, Any]]) -> dict[str, Any]:
    attempted = sorted({str(row.get("rule_type")) for row in verifications})
    reasons = sorted({str(row.get("reason")) for row in verifications if not row.get("accepted")})
    obstruction = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "HIGH_PARENT_OBSTRUCTION",
        "obstruction_id": "minimal_d1_q1_root_debt_obligation",
        "exact_uncovered_domain": uncovered[0] if uncovered else None,
        "minimal_example": {"d": 1, "a": 33, "q": 1, "n": 2**33 - 1},
        "candidate_rule_types_attempted": attempted,
        "failed_reasons": reasons,
        "new_invariant_needed": True,
        "suggested_features_for_next_search": [
            "P32 root-relative shrink certificate parameterized by d",
            "mixed 2-adic/3-adic debt state tracking Q = 3^d*q",
            "exact P32 outgoing transition family or direct root-relative residue theorem",
            "well-founded debt rank whose decrease is proved by integer inequalities",
        ],
    }
    obstruction["obstruction_hash"] = stable_hash({key: value for key, value in obstruction.items() if key != "obstruction_hash"})
    return obstruction


def _parent_family_from_uncovered(uncovered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not uncovered:
        return []
    return [
        {
            "kind": "UNCOVERED_PARENT_FAMILY",
            "family_id": "odd_entry_parent_levels_ge_33",
            "parent_level_range": {"type": "tail", "lower_bound": 33},
            "q_domain": "q > 0 and q % 2 = 1",
            "example": {"a": 33, "q": 1, "n_expr": "2^33 - 1"},
            "missing_transition_or_coverage_certificate": "no self-improving high-parent root-debt invariant certificate",
            "failure_reason": "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING",
        }
    ]


def run_high_parent_cegar(
    *,
    d_min: int,
    d_max: int,
    q_samples: list[int],
    max_steps: int,
    semantic_witnesses: list[dict[str, Any]],
    margin_report: dict[str, Any],
    powers_two: list[int] | None = None,
    powers_three: list[int] | None = None,
) -> dict[str, Any]:
    feature_rows = build_high_parent_feature_table(
        d_min=d_min,
        d_max=d_max,
        q_samples=q_samples,
        max_steps=max_steps,
        powers_two=powers_two,
        powers_three=powers_three,
    )
    p32_count = _p32_outgoing_count(semantic_witnesses)
    candidate_rules = generate_candidate_rules(
        feature_rows=feature_rows,
        margin_report=margin_report,
        p32_outgoing_count=p32_count,
    )
    verifications = [verify_high_parent_candidate(candidate) for candidate in candidate_rules]
    accepted = [
        cert
        for candidate, verification in zip(candidate_rules, verifications, strict=True)
        if (cert := accepted_certificate_from_candidate(candidate, verification)) is not None
    ]
    failed_rule_classes = [
        {
            "rule_type": verification.get("rule_type"),
            "candidate_id": verification.get("candidate_id"),
            "reason": verification.get("reason"),
            "detail": verification.get("detail"),
        }
        for verification in verifications
        if not verification.get("accepted")
    ]
    uncovered = [] if accepted else [_uncovered_domain(failed_rule_classes)]
    parent_uncovered = _parent_family_from_uncovered(uncovered)
    obstruction = (
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "status": "HIGH_PARENT_ENTRY_COVERAGE_PASS",
            "exact_uncovered_domain": None,
            "new_invariant_needed": False,
        }
        if not uncovered
        else _minimal_obstruction(uncovered, verifications)
    )
    run_result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if not uncovered else "FAIL",
        "formalization_status": "HIGH_PARENT_ENTRY_COVERAGE_PASS" if not uncovered else "HIGH_PARENT_OBSTRUCTION",
        "training_launched": False,
        "ml_hypothesis_generation_launched": False,
        "symbolic_search_launched": True,
        "feature_row_count": len(feature_rows),
        "candidate_rule_count": len(candidate_rules),
        "accepted_certificate_count": len(accepted),
        "uncovered_domain_count": len(uncovered),
        "remaining_uncovered_families": parent_uncovered,
        "p32_outgoing_s4_transition_count": p32_count,
        "candidate_rule_types_attempted": sorted({str(row.get("rule_type")) for row in candidate_rules}),
        "failed_reasons": sorted({str(row.get("reason")) for row in verifications if not row.get("accepted")}),
    }
    run_result["run_result_hash"] = stable_hash({key: value for key, value in run_result.items() if key != "run_result_hash"})
    return {
        "feature_rows": feature_rows,
        "candidate_rules": candidate_rules,
        "verifications": verifications,
        "accepted_certificates": accepted,
        "uncovered_domains": uncovered,
        "remaining_uncovered_parent_families": parent_uncovered,
        "minimal_obstruction": obstruction,
        "run_result": run_result,
    }


def load_default_inputs(
    *,
    semantic_witnesses_path: str | Path,
    margin_report_path: str | Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    semantic_witnesses = read_jsonl(semantic_witnesses_path)
    margin_report = read_json(margin_report_path) if Path(margin_report_path).exists() else {}
    return semantic_witnesses, margin_report
