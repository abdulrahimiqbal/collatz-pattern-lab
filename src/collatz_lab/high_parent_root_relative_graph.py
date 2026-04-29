"""Root-relative graph built from RUN-067 P32 special families."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .proof_action_parametric_entry_coverage import read_json, read_jsonl


RUN_ID = "RUN-068-high-parent-root-relative-invariant-search"
SCHEMA = "collatz_lab.run068_root_relative_graph"


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


def _family_id(family: dict[str, Any]) -> str:
    domain = family.get("domain", {})
    dc = domain.get("d_congruence", {})
    qc = domain.get("q_congruence", {})
    h = family.get("transition", {}).get("h")
    b = family.get("transition", {}).get("target_parent")
    return f"d{dc.get('residue')}_mod{dc.get('modulus')}:h{h}:b{b}:q{qc.get('residue')}_mod{qc.get('modulus')}"


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def root_relative_transition_from_family(family: dict[str, Any]) -> dict[str, Any]:
    domain = family.get("domain", {})
    transition = family.get("transition", {})
    outcome = family.get("root_relative_outcome", {})
    dc = domain.get("d_congruence", {})
    qc = domain.get("q_congruence", {})
    d_min = _as_int(dc.get("minimum_d"), 1)
    h = _as_int(transition.get("h"), 0)
    b = _as_int(transition.get("target_parent"), 0)
    q_residue = _as_int(qc.get("residue"), 0)
    q_modulus = _as_int(qc.get("modulus"), 1)
    target_debt = max(0, b - 32)
    source_debt = d_min
    margin_num = 3 ** (32 + d_min)
    margin_den = 2 ** (32 + d_min + h)
    direct_below_root_at_min = margin_num < margin_den
    transition_row = {
        "kind": "ROOT_RELATIVE_TRANSITION",
        "transition_id": _family_id(family),
        "source_state": {
            "debt": {"symbol": "d", "minimum": d_min, "congruence": dc},
            "parent_level": 32,
            "coordinate_form": "Q = 3^d*q",
            "q_residue_predicate": qc,
            "root_expr": "2^(32+d)*q - 1",
            "current_expr": "2^32*3^d*q - 1",
            "accumulated_relative_gain": {"num_expr": "3^d", "den_expr": "2^d"},
            "v3_coordinate_lower_bound": d_min,
        },
        "target_state": {
            "parent_level": b,
            "target_debt": target_debt,
            "coordinate_form": transition.get("target_q_expr"),
            "root_expr": "2^(32+d)*q - 1",
            "current_expr": f"P{b}({transition.get('target_q_expr')})",
            "v3_coordinate_lower_bound": "not_certified_without_target_coordinate_theorem",
        },
        "domain_predicate": {
            "d_congruence": dc,
            "q_congruence": qc,
            "q_domain": domain.get("q_domain", "q > 0 and q % 2 = 1"),
            "h": h,
            "target_parent": b,
        },
        "exact_map": {
            "forced_burst": transition.get("forced_burst"),
            "h": h,
            "target_q_expr": transition.get("target_q_expr"),
            "standard_step_count": transition.get("standard_step_count"),
        },
        "root_relative_margin_at_min_debt": {
            "gain_num": margin_num,
            "gain_den": margin_den,
            "gain_num_lt_gain_den": direct_below_root_at_min,
            "q_residue": q_residue,
            "q_modulus": q_modulus,
        },
        "classification": {
            "descends_below_root": bool(outcome.get("direct_root_descent")) or direct_below_root_at_min,
            "decreases_debt": b >= 33 and target_debt < source_debt,
            "transitions_to_high_parent_special_state": b >= 33,
            "exits_to_finite_subsystem": b <= 32,
            "finite_subsystem_margin_available": False,
            "root_relative_outcome": outcome.get("kind"),
        },
    }
    transition_row["transition_hash"] = stable_hash({key: value for key, value in transition_row.items() if key != "transition_hash"})
    return transition_row


def build_root_relative_transition_graph(
    *,
    schema: dict[str, Any],
    families: list[dict[str, Any]],
    uncovered_domains: list[dict[str, Any]],
) -> dict[str, Any]:
    transitions = [root_relative_transition_from_family(family) for family in families]
    progress = [
        row
        for row in transitions
        if row["classification"]["descends_below_root"]
        or row["classification"]["decreases_debt"]
        or (
            row["classification"]["exits_to_finite_subsystem"]
            and row["classification"]["finite_subsystem_margin_available"]
        )
    ]
    by_target_parent: dict[str, int] = {}
    for row in transitions:
        key = str(row["target_state"]["parent_level"])
        by_target_parent[key] = by_target_parent.get(key, 0) + 1
    graph = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "source_schema_hash": schema.get("schema_hash"),
        "state_space": {
            "root_family": "root = 2^(32+d)*q - 1",
            "source_family": "P32(3^d*q)",
            "domain": "d >= 1 and q > 0 and q % 2 = 1",
        },
        "transition_count": len(transitions),
        "progress_transition_count": len(progress),
        "target_parent_counts": dict(sorted(by_target_parent.items(), key=lambda item: int(item[0]))),
        "transitions": transitions,
        "uncovered_domains_from_run067": uncovered_domains,
        "graph_status": "ROOT_RELATIVE_PROGRESS_PRESENT" if progress else "NO_ROOT_RELATIVE_PROGRESS_CERTIFIED",
    }
    graph["graph_hash"] = stable_hash({key: value for key, value in graph.items() if key != "graph_hash"})
    return graph


def load_run067_inputs(
    *,
    schema_path: str | Path,
    families_path: str | Path,
    uncovered_path: str | Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    return read_json(schema_path), read_jsonl(families_path), read_jsonl(uncovered_path)
