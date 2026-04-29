"""Exact symbolic composer for RUN-069 high-parent accelerated recursion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .high_parent_domain_partition import (
    domain_from_p32_family,
    domain_key,
    remaining_parent_family,
    universal_high_parent_domain,
)
from .high_parent_root_inequality import prove_debt_reduction, prove_one_step_root_descent
from .proof_action_parametric_entry_coverage import read_json, read_jsonl


RUN_ID = "RUN-069-high-parent-accelerated-recursion"
SCHEMA = "collatz_lab.run069_high_parent_accelerated_recursion"


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


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _family_id(family: dict[str, Any]) -> str:
    domain = family.get("domain", {})
    transition = family.get("transition", {})
    dc = domain.get("d_congruence", {})
    qc = domain.get("q_congruence", {})
    return (
        f"d{dc.get('residue')}_mod{dc.get('modulus')}:"
        f"h{transition.get('h')}:b{transition.get('target_parent')}:"
        f"q{qc.get('residue')}_mod{qc.get('modulus')}"
    )


def _branch_from_family(family: dict[str, Any]) -> dict[str, Any]:
    domain = domain_from_p32_family(family)
    transition = family.get("transition", {}) if isinstance(family.get("transition"), dict) else {}
    h = _as_int(transition.get("h"))
    target_parent = _as_int(transition.get("target_parent"))
    root_proof = prove_one_step_root_descent(domain=domain, h=h)
    debt_proof = prove_debt_reduction(domain=domain, target_parent=target_parent)
    descends = root_proof.get("status") == "PASS"
    debt_reduces = debt_proof.get("status") == "PASS"
    finite_entry = target_parent <= 32
    composable = target_parent == 32
    blocked_reason = None
    if descends or debt_reduces:
        branch_status = "CLOSED"
    elif composable:
        branch_status = "REQUIRES_SPECIAL_FORM_PROOF"
        blocked_reason = "TARGET_COORDINATE_SPECIAL_3_POWER_FORM_NOT_CERTIFIED"
    elif finite_entry:
        branch_status = "BLOCKED_AT_FINITE_SUBSYSTEM_MARGIN"
        blocked_reason = "FINITE_SUBSYSTEM_ROOT_RELATIVE_MARGIN_MISSING"
    else:
        branch_status = "BLOCKED_AT_NON_P32_TARGET"
        blocked_reason = "NO_ACCELERATED_SCHEMA_FOR_TARGET_PARENT"

    row = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "COMPOSED_HIGH_PARENT_TRANSITION_FAMILY",
        "branch_id": _family_id(family),
        "branch_depth": 1,
        "branch_sequence": [_family_id(family)],
        "source_state": {
            "root_expr": "R(d,q) = 2^(32+d)*q - 1",
            "current_parent": 32,
            "coordinate_expr": "3^d*q",
            "current_expr": "2^32*3^d*q - 1",
        },
        "domain": domain,
        "domain_key": domain_key(domain),
        "exact_composition": {
            "current_final_expr": "(3^(32+d)*q - 1) / 2^h",
            "target_parent": target_parent,
            "target_coordinate_expr": transition.get("target_q_expr"),
            "accumulated_power_three_expr": "32+d",
            "accumulated_power_two": h,
            "total_standard_step_count": transition.get("standard_step_count"),
            "v3_coordinate_lower_bound": "source coordinate has v3 >= d; target v3 not certified",
        },
        "root_relative_inequality": root_proof,
        "debt_reduction": debt_proof,
        "classification": {
            "descends_below_root": descends,
            "debt_reduces": debt_reduces,
            "finite_subsystem_entry": finite_entry,
            "finite_subsystem_margin_available": False,
            "can_compose_with_p32_special_schema": False,
            "branch_status": branch_status,
            "blocked_reason": blocked_reason,
        },
    }
    row["branch_hash"] = stable_hash({key: value for key, value in row.items() if key != "branch_hash"})
    return row


def compose_high_parent_families(
    *,
    families: list[dict[str, Any]],
    max_depth: int,
) -> list[dict[str, Any]]:
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1")
    # The current artifact inventory contains only the P32-special schema.
    # Branches that do not land back in a certified P32-special source are
    # deliberately stopped and marked blocked.
    return [_branch_from_family(family) for family in families]


def _descent_certificate(branch: dict[str, Any]) -> dict[str, Any] | None:
    if branch.get("classification", {}).get("descends_below_root") is not True:
        return None
    cert = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "HIGH_PARENT_ROOT_RELATIVE_DESCENT_CERTIFICATE",
        "branch_id": branch.get("branch_id"),
        "domain": branch.get("domain"),
        "branch_depth": branch.get("branch_depth"),
        "root_relative_inequality": branch.get("root_relative_inequality"),
        "root_relative_descent_proved": True,
        "semantic_validation": {"status": "PASS", "failures": []},
    }
    cert["certificate_hash"] = stable_hash({key: value for key, value in cert.items() if key != "certificate_hash"})
    return cert


def _debt_certificate(branch: dict[str, Any]) -> dict[str, Any] | None:
    if branch.get("classification", {}).get("debt_reduces") is not True:
        return None
    cert = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "HIGH_PARENT_DEBT_REDUCTION_CERTIFICATE",
        "branch_id": branch.get("branch_id"),
        "domain": branch.get("domain"),
        "branch_depth": branch.get("branch_depth"),
        "debt_reduction": branch.get("debt_reduction"),
        "debt_reduction_proved": True,
        "semantic_validation": {"status": "PASS", "failures": []},
    }
    cert["certificate_hash"] = stable_hash({key: value for key, value in cert.items() if key != "certificate_hash"})
    return cert


def _uncovered_domain(branches: list[dict[str, Any]], obstruction_reason: str) -> dict[str, Any]:
    blocked_counts: dict[str, int] = {}
    for branch in branches:
        reason = str(branch.get("classification", {}).get("blocked_reason"))
        blocked_counts[reason] = blocked_counts.get(reason, 0) + 1
    row = {
        **universal_high_parent_domain(),
        "failure_reason": obstruction_reason,
        "blocked_branch_counts": dict(sorted(blocked_counts.items())),
        "accepted_root_relative_descent_count": 0,
        "accepted_debt_reduction_count": 0,
    }
    row["domain_hash"] = stable_hash({key: value for key, value in row.items() if key != "domain_hash"})
    return row


def minimal_branch_obstruction(
    *,
    branches: list[dict[str, Any]],
    run068_obstruction: dict[str, Any],
    max_representatives: int,
) -> dict[str, Any]:
    representative = [
        {
            "branch_id": branch.get("branch_id"),
            "branch_depth": branch.get("branch_depth"),
            "domain": branch.get("domain"),
            "target_parent": branch.get("exact_composition", {}).get("target_parent"),
            "current_final_expr": branch.get("exact_composition", {}).get("current_final_expr"),
            "root_inequality_status": branch.get("root_relative_inequality", {}).get("status"),
            "root_inequality_reason": branch.get("root_relative_inequality", {}).get("reason"),
            "debt_reduction_status": branch.get("debt_reduction", {}).get("status"),
            "blocked_reason": branch.get("classification", {}).get("blocked_reason"),
        }
        for branch in branches[:max_representatives]
    ]
    obstruction = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "HIGH_PARENT_ACCELERATED_RECURSION_INCOMPLETE",
        "obstruction_id": "p32_special_branches_enter_finite_system_without_root_margin",
        "exact_uncovered_domain": universal_high_parent_domain(),
        "shortest_unresolved_branch_depth": 1,
        "representative_unresolved_branches": representative,
        "composed_formula": {
            "source": "P32(3^d*q)",
            "after_one_p32_special_block": "(3^(32+d)*q - 1) / 2^h",
            "root": "2^(32+d)*q - 1",
        },
        "exact_inequality_obligation": "3^(32+d)*q - 1 < 2^h*(2^(32+d)*q - 1)",
        "why_undecided_or_failed": [
            "No emitted branch proves the root-relative inequality below the original root.",
            "No emitted branch proves target high-parent debt d' < d.",
            "Every emitted RUN-067 branch lands in P1..P8, so the P32-special schema cannot be composed further.",
            "A finite-subsystem root-relative margin certificate is still absent.",
        ],
        "run068_obstruction_hash": run068_obstruction.get("obstruction_hash"),
        "suggested_split_or_invariant": [
            "add exact non-P32 continuation schemas for target parents P1..P8",
            "add finite-subsystem root-relative margin certificates for P_b targets reached from P32(3^d*q)",
            "derive composed gain inequalities over target parent paths instead of only P32-special first steps",
        ],
    }
    obstruction["obstruction_hash"] = stable_hash(
        {key: value for key, value in obstruction.items() if key != "obstruction_hash"}
    )
    return obstruction


def build_high_parent_accelerated_recursion(
    *,
    schema: dict[str, Any],
    families: list[dict[str, Any]],
    run068_obstruction: dict[str, Any],
    run068_uncovered: list[dict[str, Any]],
    max_depth: int,
    max_representatives: int = 8,
) -> dict[str, Any]:
    branches = compose_high_parent_families(families=families, max_depth=max_depth)
    descent_certs = [cert for branch in branches if (cert := _descent_certificate(branch)) is not None]
    debt_certs = [cert for branch in branches if (cert := _debt_certificate(branch)) is not None]
    success = not run068_uncovered and bool(branches) and len(descent_certs) + len(debt_certs) == len(branches)
    status = "HIGH_PARENT_ENTRY_COVERAGE_PASS" if success else "HIGH_PARENT_ACCELERATED_RECURSION_INCOMPLETE"
    uncovered = [] if success else [_uncovered_domain(branches, status)]
    remaining_parent = [] if success else [remaining_parent_family(status)]
    obstruction = (
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "status": "HIGH_PARENT_ENTRY_COVERAGE_PASS",
            "exact_uncovered_domain": None,
        }
        if success
        else minimal_branch_obstruction(
            branches=branches,
            run068_obstruction=run068_obstruction,
            max_representatives=max_representatives,
        )
    )
    run_result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if success else "FAIL",
        "formalization_status": status,
        "training_launched": False,
        "ml_hypothesis_generation_launched": False,
        "symbolic_composition_launched": True,
        "source_schema_hash": schema.get("schema_hash"),
        "max_depth": max_depth,
        "input_family_count": len(families),
        "composed_family_count": len(branches),
        "root_relative_descent_certificate_count": len(descent_certs),
        "debt_reduction_certificate_count": len(debt_certs),
        "uncovered_domain_count": len(uncovered),
        "remaining_uncovered_families": remaining_parent,
        "blocked_branch_reasons": sorted(
            {
                str(branch.get("classification", {}).get("blocked_reason"))
                for branch in branches
                if branch.get("classification", {}).get("blocked_reason")
            }
        ),
    }
    run_result["run_result_hash"] = stable_hash({key: value for key, value in run_result.items() if key != "run_result_hash"})
    return {
        "composed_transition_families": branches,
        "root_relative_descent_certificates": descent_certs,
        "debt_reduction_certificates": debt_certs,
        "uncovered_high_parent_domains": uncovered,
        "remaining_uncovered_parent_families": remaining_parent,
        "minimal_high_parent_branch_obstruction": obstruction,
        "run_result": run_result,
    }


def load_default_inputs(
    *,
    families_path: str | Path,
    schema_path: str | Path,
    obstruction_path: str | Path,
    uncovered_path: str | Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    return (
        read_json(schema_path),
        read_jsonl(families_path),
        read_json(obstruction_path),
        read_jsonl(uncovered_path),
    )

