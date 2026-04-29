"""RUN-065 high-parent root-debt system.

This run tries to close the remaining odd-entry family `a >= 33` by tracking
the debt introduced when the certified high-parent transition moves

    P_(32+d)(q) -> P32(3^d*q).

It is deliberately fail-closed: descriptive certificates or subsystem-local
descent are not accepted as root-relative descent below the original root.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .proof_action_parametric_entry_coverage import REPO_ROOT, read_json, read_jsonl


RUN_ID = "RUN-065-high-parent-root-debt-system"
SCHEMA = "collatz_lab.run065_high_parent_root_debt_system"


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


def _s4_witnesses(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("kind") == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"]


def _pow_expr(base: int, exponent_expr: str) -> str:
    return f"{base}^{exponent_expr}"


def build_root_debt_states(sample_ds: list[int] | None = None) -> list[dict[str, Any]]:
    """Build exact symbolic root-debt obligations for representative debts."""

    ds = sample_ds or [1, 2, 8]
    states: list[dict[str, Any]] = []
    for d in ds:
        if d < 1:
            raise ValueError("high-parent debt samples must be positive")
        states.append(
            {
                "kind": "HIGH_PARENT_ROOT_DEBT_STATE",
                "debt": d,
                "parent_level": 32 + d,
                "source_q_domain": "q > 0 and q % 2 = 1",
                "root_expr": f"2^{32 + d}*q - 1",
                "p32_coordinate_expr": f"3^{d}*q",
                "current_expr": f"2^32*3^{d}*q - 1",
                "transition_step_count": 2 * d,
                "transition_theorem": "Collatz.high_parent_to_p32",
                "direct_current_below_root": False,
                "direct_current_below_root_check": {
                    "required_inequality": f"{_pow_expr(3, str(d))} < {_pow_expr(2, str(d))}",
                    "status": "FAIL",
                    "reason": "for d >= 1, 3^d > 2^d, so the P32 entry current is larger than the original root",
                },
                "needed_subsystem_margin": f"certified P32 continuation must recover factor < (2/3)^{d}",
            }
        )
    return states


def _p32_outgoing_s4_witnesses(s4_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in s4_rows if int(row.get("source_parent", 0) or 0) == 32]


def _root_relative_transition_certificates(p32_edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    certificates: list[dict[str, Any]] = []
    for row in p32_edges:
        pmap = row.get("parent_coordinate_map", {}) if isinstance(row.get("parent_coordinate_map"), dict) else {}
        cert = {
            "kind": "ROOT_RELATIVE_TRANSITION_CERTIFICATE",
            "certificate_id": row.get("certificate_id"),
            "source_parent": 32,
            "target_parent": row.get("target_parent"),
            "standard_step_count": row.get("standard_step_count"),
            "q_source_expr": "Q = 3^d*q",
            "root_expr": "2^(32+d)*q - 1",
            "current_expr": "2^32*Q - 1",
            "parent_coordinate_map": {
                "A": pmap.get("A"),
                "B": pmap.get("B"),
                "D": pmap.get("D"),
            },
            "root_relative_debt_delta_proved": False,
            "semantic_validation": {
                "status": "FAIL",
                "failures": [
                    {
                        "reason": "ROOT_RELATIVE_DEBT_DELTA_MISSING",
                        "detail": "the S4 witness is transition-local and does not prove a decrease below the original high-parent root",
                    }
                ],
            },
        }
        cert["certificate_hash"] = stable_hash(cert)
        certificates.append(cert)
    return certificates


def _passing_margin_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row.get("kind") in {
            "HIGH_PARENT_ROOT_RELATIVE_MARGIN_CERTIFICATE",
            "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE",
            "HIGH_PARENT_ROOT_DEBT_RANKING_CERTIFICATE",
        }
        and row.get("root_relative_descent_proved") is True
        and row.get("semantic_validation", {}).get("status") == "PASS"
    ]


def _remaining_high_parent_family() -> dict[str, Any]:
    return {
        "kind": "UNCOVERED_PARENT_FAMILY",
        "family_id": "odd_entry_parent_levels_ge_33",
        "parent_level_range": {"type": "tail", "lower_bound": 33},
        "q_domain": "q > 0 and q % 2 = 1",
        "example": {"a": 33, "q": 1, "n_expr": "2^33 - 1"},
        "missing_transition_or_coverage_certificate": "no root-relative P32 margin/debt invariant certificate",
        "failure_reason": "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING",
    }


def build_high_parent_root_debt_system(
    *,
    s4_semantic_witnesses: list[dict[str, Any]],
    s3_semantic_roles: list[dict[str, Any]],
    margin_report: dict[str, Any],
    candidate_margin_certificates: list[dict[str, Any]],
    sample_ds: list[int] | None = None,
) -> dict[str, Any]:
    s4_rows = _s4_witnesses(s4_semantic_witnesses)
    p32_edges = _p32_outgoing_s4_witnesses(s4_rows)
    root_debt_states = build_root_debt_states(sample_ds)
    transition_certs = _root_relative_transition_certificates(p32_edges)
    passing_candidates = _passing_margin_candidates(candidate_margin_certificates)
    p32_s3_source = [row for row in s3_semantic_roles if row.get("source_node") == "P32"]
    p32_s3_target = [row for row in s3_semantic_roles if row.get("target_node") == "P32"]

    direct_states_closed = False
    transition_debt_decreases = any(row.get("root_relative_debt_delta_proved") for row in transition_certs)
    lower_debt_entry = bool(passing_candidates)
    success = direct_states_closed or transition_debt_decreases or lower_debt_entry
    missing_reasons: list[str] = []
    if not direct_states_closed:
        missing_reasons.append("HIGH_PARENT_DIRECT_CURRENT_BELOW_ROOT_FALSE")
    if not p32_edges:
        missing_reasons.append("P32_OUTGOING_ITERATE_FAMILY_MISSING")
    if not transition_debt_decreases:
        missing_reasons.append("ROOT_RELATIVE_DEBT_DECREASE_MISSING")
    if not lower_debt_entry:
        missing_reasons.append("LOWER_DEBT_ENTRY_CERTIFICATE_MISSING")
    if margin_report.get("status") != "HIGH_PARENT_MARGIN_PASS":
        missing_reasons.append(str(margin_report.get("failure_reason") or "HIGH_PARENT_MARGIN_NOT_PROVED"))

    ranking_cert = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "HIGH_PARENT_ROOT_DEBT_RANKING_CERTIFICATE",
        "status": "PASS" if success else "FAIL",
        "ranking_measure": "debt d = a - 32 plus root-relative current/root margin",
        "accepted_closure_modes": [
            "direct current < root",
            "root-relative debt decreases",
            "transition enters already certified lower-debt state",
        ],
        "direct_states_closed": direct_states_closed,
        "transition_debt_decreases": transition_debt_decreases,
        "lower_debt_entry": lower_debt_entry,
        "p32_outgoing_transition_count": len(p32_edges),
        "passing_margin_candidate_count": len(passing_candidates),
        "missing_reasons": [] if success else sorted(set(missing_reasons)),
        "semantic_validation": {
            "status": "PASS" if success else "FAIL",
            "failures": []
            if success
            else [
                {
                    "reason": "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING",
                    "detail": "no exact invariant/path family proves root-relative descent for all d >= 1",
                }
            ],
        },
    }
    ranking_cert["certificate_hash"] = stable_hash({key: value for key, value in ranking_cert.items() if key != "certificate_hash"})

    entry_coverage_cert = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "HIGH_PARENT_ENTRY_COVERAGE_CERTIFICATE",
        "status": "PASS" if success else "FAIL",
        "covered_family_id": "odd_entry_parent_levels_ge_33",
        "statement": "For all a >= 33 and q odd positive, P_a(q) eventually descends below 2^a*q - 1 or enters a certified lower-debt state.",
        "uses_transition_theorem": "Collatz.high_parent_to_p32",
        "root_relative_descent_proved": success,
        "remaining_uncovered_families": [] if success else [_remaining_high_parent_family()],
        "semantic_validation": ranking_cert["semantic_validation"],
    }
    entry_coverage_cert["certificate_hash"] = stable_hash(
        {key: value for key, value in entry_coverage_cert.items() if key != "certificate_hash"}
    )

    report = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if success else "FAIL",
        "formalization_status": "HIGH_PARENT_ROOT_DEBT_CLOSED" if success else "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING",
        "training_launched": False,
        "ml_launched": False,
        "symbolic_search_launched": True,
        "root_relative_descent_proved": success,
        "remaining_uncovered_families": [] if success else [_remaining_high_parent_family()],
        "root_debt_state_count": len(root_debt_states),
        "root_relative_transition_certificate_count": len(transition_certs),
        "p32_outgoing_s4_transition_count": len(p32_edges),
        "s4_semantic_witness_count": len(s4_rows),
        "s3_p32_source_support_count": len(p32_s3_source),
        "s3_p32_target_support_count": len(p32_s3_target),
        "candidate_margin_count": len(candidate_margin_certificates),
        "passing_margin_candidate_count": len(passing_candidates),
        "missing_reasons": [] if success else sorted(set(missing_reasons)),
        "ranking_certificate": ranking_cert,
        "entry_coverage_certificate": entry_coverage_cert,
    }
    report["system_hash"] = stable_hash({key: value for key, value in report.items() if key != "system_hash"})
    return {
        "report": report,
        "root_debt_states": root_debt_states,
        "transition_certificates": transition_certs,
        "ranking_certificate": ranking_cert,
        "entry_coverage_certificate": entry_coverage_cert,
        "remaining_uncovered_families": report["remaining_uncovered_families"],
    }


def load_default_inputs(
    *,
    semantic_witnesses_path: str | Path = "certificate_store/run048_semantic_witnesses.jsonl",
    s3_roles_path: str | Path = "certificate_store/run051_s3_semantic_roles.jsonl",
    margin_report_path: str | Path = "certificate_store/run064_high_parent_margin_report.json",
    candidate_margin_certificates_path: str | Path = "certificate_store/run064_candidate_margin_certificates.jsonl",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    margin_report = read_json(margin_report_path) if Path(margin_report_path).exists() else {}
    return (
        read_jsonl(semantic_witnesses_path),
        read_jsonl(s3_roles_path),
        margin_report,
        read_jsonl(candidate_margin_certificates_path),
    )
