"""RUN-064 high-parent root-relative margin audit.

This pass does not search for new trajectories.  It audits the existing
certificates and asks whether they expose enough root-relative contraction
information to turn the high-parent `P_a -> P32` transition into a descent
theorem below the original root.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .proof_action_parametric_entry_coverage import REPO_ROOT, read_jsonl


RUN_ID = "RUN-064-high-parent-root-relative-margin"
SCHEMA = "collatz_lab.run064_high_parent_root_relative_margin"


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


def _p32_path_records(s4_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in s4_rows:
        if int(row.get("source_parent", 0) or 0) != 32:
            continue
        edge_ratio = {
            "asymptotic_q_multiplier_num": int(row.get("parent_coordinate_map", {}).get("A", 0) or 0),
            "asymptotic_q_multiplier_den": int(row.get("parent_coordinate_map", {}).get("D", 0) or 0),
        }
        records.append(
            {
                "kind": "P32_CERTIFIED_PATH_FRAGMENT",
                "certificate_id": row.get("certificate_id"),
                "source_parent": row.get("source_parent"),
                "target_parent": row.get("target_parent"),
                "standard_step_count": row.get("standard_step_count"),
                "edge_ratio": edge_ratio,
                "root_relative_margin_available": False,
                "reason": "S4 edge witness is transition-local and does not state a bound below the high-parent root.",
            }
        )
    return records


def _s3_p32_inventory(s3_roles: list[dict[str, Any]]) -> dict[str, Any]:
    source_p32 = [row for row in s3_roles if row.get("source_node") == "P32"]
    target_p32 = [row for row in s3_roles if row.get("target_node") == "P32"]
    return {
        "source_p32_count": len(source_p32),
        "target_p32_count": len(target_p32),
        "target_p32_certificate_ids": [row.get("certificate_id") for row in target_p32],
        "source_p32_certificate_ids": [row.get("certificate_id") for row in source_p32],
        "semantic_role_note": "S3 records are ranking/support facts, not actual Collatz iterate paths from P32.",
    }


def _candidate_margin_certificates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in rows:
        if row.get("kind") in {
            "HIGH_PARENT_ROOT_RELATIVE_MARGIN_CERTIFICATE",
            "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE",
        }:
            candidates.append(row)
    return candidates


def _failing_d_samples(reason: str) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for d in (1, 2, 8):
        samples.append(
            {
                "kind": "HIGH_PARENT_MARGIN_OBLIGATION",
                "d": d,
                "a": 32 + d,
                "q_domain": "q > 0 and q % 2 = 1",
                "original_root_expr": f"2^{32 + d}*q - 1",
                "p32_entry_current_expr": f"2^32*3^{d}*q - 1",
                "needed_p32_shrink_factor": f"< (2/3)^{d}",
                "status": "HIGH_PARENT_CERTIFICATE_INSUFFICIENT",
                "failure_reason": reason,
            }
        )
    return samples


def build_high_parent_margin_audit(
    *,
    s4_semantic_witnesses: list[dict[str, Any]],
    s3_semantic_roles: list[dict[str, Any]],
    enriched_semantic_payloads: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    s4_rows = _s4_witnesses(s4_semantic_witnesses)
    p32_paths = _p32_path_records(s4_rows)
    candidate_margins = _candidate_margin_certificates(enriched_semantic_payloads)
    p32_s3_inventory = _s3_p32_inventory(s3_semantic_roles)

    root_relative_candidates = [
        row
        for row in candidate_margins
        if row.get("semantic_validation", {}).get("status") == "PASS"
        and row.get("root_relative_descent_proved") is True
    ]
    if root_relative_candidates:
        status = "HIGH_PARENT_MARGIN_PASS"
        formalization_status = "HIGH_PARENT_MARGIN_PASS"
        failure_reason = None
        failing_d_values: list[dict[str, Any]] = []
    else:
        status = "HIGH_PARENT_CERTIFICATE_INSUFFICIENT"
        formalization_status = "HIGH_PARENT_CERTIFICATE_INSUFFICIENT"
        failure_reason = "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING"
        failing_d_values = _failing_d_samples(failure_reason)

    report = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": status,
        "formalization_status": formalization_status,
        "failure_reason": failure_reason,
        "training_launched": False,
        "search_launched": False,
        "high_parent_obligation": {
            "family_id": "odd_entry_parent_levels_ge_33",
            "d_definition": "d = a - 32 >= 1",
            "original_root": "n0 = 2^(32+d)*q - 1",
            "p32_entry_current": "m0 = 2^32*3^d*q - 1",
            "growth_factor": "(3/2)^d",
            "needed_subsystem_margin": "certified P32 path must output y < 2^(32+d)*q - 1, equivalently recover a factor stronger than (2/3)^d relative to m0",
        },
        "available_certificate_inventory": {
            "s4_semantic_witness_count": len(s4_rows),
            "p32_outgoing_s4_path_count": len(p32_paths),
            "s3_p32_inventory": p32_s3_inventory,
            "candidate_root_relative_margin_count": len(candidate_margins),
            "passing_root_relative_margin_count": len(root_relative_candidates),
        },
        "conclusion": (
            "Existing certificates expose a high-parent transition into P32 but do not expose a "
            "root-relative P32 margin certificate."
            if failure_reason
            else "Existing certificates expose a passing high-parent root-relative margin certificate."
        ),
    }
    report["audit_hash"] = stable_hash({key: value for key, value in report.items() if key != "audit_hash"})
    return report, p32_paths, failing_d_values, candidate_margins


def load_default_inputs(
    *,
    semantic_witnesses_path: str | Path = "certificate_store/run048_semantic_witnesses.jsonl",
    s3_roles_path: str | Path = "certificate_store/run051_s3_semantic_roles.jsonl",
    enriched_payloads_path: str | Path = "certificate_store/run051_enriched_semantic_payloads.jsonl",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        read_jsonl(semantic_witnesses_path),
        read_jsonl(s3_roles_path),
        read_jsonl(enriched_payloads_path),
    )
