"""Exact cycle-witness audit for RUN-038B.

RUN-038 composes parent-coordinate maps exactly, but the SCC obstruction still
needs a concrete executable witness audit.  This module checks a cycle against
the raw parent-state transition semantics

    P_a(q): n = 2^a*q - 1

using only integer arithmetic.  It deliberately treats a map/composition as a
candidate until the concrete witness replays through ``parent_transition`` and
the standard Collatz steps.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .collatz import collatz_step
from .parent_states import parent_transition
from .proof_action_parent_transition_cert import parse_branch_id
from .proof_action_scc_invariant_discovery import (
    CycleDomain,
    _minimum_in_residue_class,
    compose_cycle_domain,
    impose_linear_congruence,
)
from .proof_action_scc_ranking_cert import load_jsonl, write_jsonl


RUN_ID = "RUN-038B-cycle-witness-audit"
SCHEMA = "collatz_lab.cycle_witness_audit"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_float(item) for item in value)
    return False


def _stringify_ints(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, dict):
        return {key: _stringify_ints(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_stringify_ints(item) for item in value]
    return value


def _power_of_two_exponent(value: int) -> int | None:
    if value <= 0 or value & (value - 1):
        return None
    return value.bit_length() - 1


def _normalise_fraction_triple(A: int, B: int, D: int) -> tuple[int, int, int]:
    if D < 0:
        A, B, D = -A, -B, -D
    gcd = math.gcd(math.gcd(abs(A), abs(B)), abs(D))
    if gcd > 1:
        A //= gcd
        B //= gcd
        D //= gcd
    return A, B, D


def _cycle_id(edge_ids: list[str], known: str | None = None) -> str:
    return known or _hash({"edge_ids": edge_ids, "run_id": "RUN-038-scc-invariant-discovery"})[:16]


def _edge_sequence(edge_maps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sequence: list[dict[str, Any]] = []
    for index, edge in enumerate(edge_maps):
        sequence.append(
            {
                "step_index": index,
                "edge_id": str(edge["edge_id"]),
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "source_parent": str(edge["source_parent"]),
                "target_parent": str(edge["target_parent"]),
                "A": str(edge["A"]),
                "B": str(edge["B"]),
                "D": str(edge["D"]),
                "domain_residue": str(edge["domain_residue"]),
                "domain_modulus": str(edge["domain_modulus"]),
                "minimum_q": str(edge.get("minimum_q", 1)),
                "branch_id": str(edge.get("branch_id", "")),
                "valuation": str(edge.get("valuation", "")),
                "transition_certificate_id": str(edge.get("transition_certificate_id", "")),
                "transition_certificate_hash": str(edge.get("transition_certificate_hash", "")),
                "parent_coordinate_map_certificate_hash": str(edge.get("parent_coordinate_map_certificate_hash", "")),
                "domain_constraints": list(edge.get("domain_constraints") or []),
                "all_integrality_domain_constraints": _stringify_ints(
                    edge.get("all_integrality_domain_constraints", {})
                ),
            }
        )
    return sequence


def _constraint_rows(edge: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    all_constraints = edge.get("all_integrality_domain_constraints")
    rows: list[dict[str, Any]] = []
    if isinstance(all_constraints, dict):
        for row in all_constraints.get("s4_domain_constraints") or []:
            if isinstance(row, dict) and row.get("kind") == kind:
                rows.append(row)
    return rows


def _check_edge_domain(edge: dict[str, Any], q: int) -> tuple[bool, dict[str, Any]]:
    checks: dict[str, Any] = {
        "q": str(q),
        "positive_q": q > 0,
        "odd_q": q % 2 == 1,
        "no_float_payload": not _contains_float(edge),
    }
    if not checks["positive_q"] or not checks["odd_q"] or not checks["no_float_payload"]:
        return False, checks

    domain_modulus = _as_int(edge["domain_modulus"], "domain_modulus")
    domain_residue = _as_int(edge["domain_residue"], "domain_residue") % domain_modulus
    minimum_q = _as_int(edge.get("minimum_q", 1), "minimum_q")
    checks["minimum_q_pass"] = q >= minimum_q
    checks["edge_domain_congruence_pass"] = (q - domain_residue) % domain_modulus == 0

    try:
        branch = parse_branch_id(str(edge.get("branch_id", "")))
        branch_modulus = 1 << branch["depth"]
        branch_delta = q - branch["residue"]
        branch_pass = branch_delta % branch_modulus == 0
        checks["branch_source_parent_pass"] = int(edge["source_parent"]) == branch["a"]
        checks["branch_congruence_pass"] = branch_pass
        checks["branch_residue"] = str(branch["residue"])
        checks["branch_modulus"] = str(branch_modulus)
        k = branch_delta // branch_modulus if branch_pass else None
        checks["k"] = str(k) if k is not None else None
    except (KeyError, ValueError) as exc:
        checks["branch_parse_failure"] = str(exc)
        k = None

    divisibility_pass = True
    for row in _constraint_rows(edge, "k_divisibility"):
        modulus = _as_int(row.get("modulus", 1), "k_divisibility.modulus")
        residue = _as_int(row.get("residue", 0), "k_divisibility.residue")
        passed = k is not None and (modulus == 1 or (k - residue) % modulus == 0)
        divisibility_pass = divisibility_pass and passed
        checks.setdefault("k_divisibility_checks", []).append(
            {"modulus": str(modulus), "residue": str(residue), "passed": passed}
        )
    exclusion_pass = True
    for row in _constraint_rows(edge, "excluded_next_power"):
        modulus = _as_int(row.get("modulus", 1), "excluded_next_power.modulus")
        residue = _as_int(row.get("residue", 0), "excluded_next_power.residue")
        passed = k is not None and modulus > 0 and (k - residue) % modulus != 0
        exclusion_pass = exclusion_pass and passed
        checks.setdefault("excluded_next_power_checks", []).append(
            {"modulus": str(modulus), "residue": str(residue), "passed": passed}
        )
    checks["k_divisibility_pass"] = divisibility_pass
    checks["excluded_next_power_pass"] = exclusion_pass

    A = _as_int(edge["A"], "A")
    B = _as_int(edge["B"], "B")
    D = _as_int(edge["D"], "D")
    numerator = A * q + B
    checks["map_integrality_pass"] = D > 0 and numerator % D == 0
    checks["map_numerator"] = str(numerator)
    checks["map_denominator"] = str(D)
    accepted = all(
        bool(checks.get(key))
        for key in (
            "minimum_q_pass",
            "edge_domain_congruence_pass",
            "branch_source_parent_pass",
            "branch_congruence_pass",
            "k_divisibility_pass",
            "excluded_next_power_pass",
            "map_integrality_pass",
        )
    )
    return accepted, checks


def _raw_collatz_replay(n0: int, expected_final: int, standard_steps: int) -> dict[str, Any]:
    current = n0
    values = [n0]
    first_descent_step: int | None = None
    max_value = n0
    for step in range(1, standard_steps + 1):
        current = collatz_step(current)
        values.append(current)
        max_value = max(max_value, current)
        if first_descent_step is None and current < n0:
            first_descent_step = step
    path_hash = _hash([str(value) for value in values])
    return {
        "start_n": str(n0),
        "expected_final_n": str(expected_final),
        "actual_final_n": str(current),
        "standard_steps": standard_steps,
        "first_descent_step": first_descent_step,
        "descends_below_start": first_descent_step is not None,
        "max_value": str(max_value),
        "path_hash": path_hash,
        "status": "PASS" if current == expected_final else "FAIL",
    }


def replay_cycle_witness(
    *,
    cycle_id: str,
    edge_maps: list[dict[str, Any]],
    q0: int,
    witness_kind: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    q = q0
    n0: int | None = None
    raw_rows: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    any_raw_descent = False

    for index, edge in enumerate(edge_maps):
        source_parent = _as_int(edge["source_parent"], "source_parent")
        target_parent = _as_int(edge["target_parent"], "target_parent")
        n = (1 << source_parent) * q - 1
        if n0 is None:
            n0 = n
        domain_ok, domain_checks = _check_edge_domain(edge, q)
        if not domain_ok:
            failures.append(
                {
                    "step_index": index,
                    "edge_id": edge.get("edge_id"),
                    "reason": "transition_domain_check_failed",
                    "checks": domain_checks,
                }
            )
            break

        A = _as_int(edge["A"], "A")
        B = _as_int(edge["B"], "B")
        D = _as_int(edge["D"], "D")
        q_next = (A * q + B) // D
        n_next = (1 << target_parent) * q_next - 1
        raw = parent_transition(source_parent, q)
        raw_ok = raw["a_next"] == target_parent and raw["r_next"] == q_next
        raw_replay = _raw_collatz_replay(n, n_next, int(raw["standard_steps"]))
        any_raw_descent = any_raw_descent or bool(raw_replay["descends_below_start"])
        raw_row = {
            "cycle_id": cycle_id,
            "witness_kind": witness_kind,
            "step_index": index,
            "edge_id": str(edge["edge_id"]),
            "source_parent": str(source_parent),
            "target_parent": str(target_parent),
            "q": str(q),
            "n": str(n),
            "q_next": str(q_next),
            "n_next": str(n_next),
            "parent_transition": _stringify_ints(raw),
            "raw_collatz": raw_replay,
            "status": "PASS" if raw_ok and raw_replay["status"] == "PASS" else "FAIL",
        }
        raw_rows.append(raw_row)
        if not raw_ok or raw_replay["status"] != "PASS":
            failures.append(
                {
                    "step_index": index,
                    "edge_id": edge.get("edge_id"),
                    "reason": "raw_collatz_branch_mismatch",
                    "expected_target_parent": str(target_parent),
                    "actual_target_parent": str(raw["a_next"]),
                    "expected_q_next": str(q_next),
                    "actual_q_next": str(raw["r_next"]),
                    "raw_collatz_status": raw_replay["status"],
                }
            )
            break
        steps.append(
            {
                "step_index": index,
                "edge_id": str(edge["edge_id"]),
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "q": str(q),
                "n": str(n),
                "q_next": str(q_next),
                "n_next": str(n_next),
                "standard_steps": int(raw["standard_steps"]),
                "raw_transition_hash": raw_replay["path_hash"],
                "transition_certificate_applies": True,
                "domain_checks": domain_checks,
            }
        )
        q = q_next

    final_n = None if not steps else int(steps[-1]["n_next"])
    start_n = n0 if n0 is not None else ((1 << _as_int(edge_maps[0]["source_parent"], "source_parent")) * q0 - 1)
    witness = {
        "cycle_id": cycle_id,
        "witness_kind": witness_kind,
        "edge_ids": [str(edge["edge_id"]) for edge in edge_maps],
        "start_parent": str(edge_maps[0]["source"]),
        "q0": str(q0),
        "n0": str(start_n),
        "steps": steps,
        "q_final": str(q) if steps else None,
        "n_final": str(final_n) if final_n is not None else None,
        "q_non_decreasing": bool(steps and q >= q0),
        "n_non_decreasing": bool(final_n is not None and final_n >= start_n),
        "raw_collatz_descends_below_start": any_raw_descent,
        "status": "PASS" if not failures and len(steps) == len(edge_maps) else "FAIL",
        "failures": failures,
        "no_floating_arithmetic": not _contains_float({"edge_maps": edge_maps, "witness": steps}),
    }
    return witness, raw_rows


def self_return_domain(domain: CycleDomain) -> dict[str, Any]:
    if not domain.accepted:
        return {"status": "NOT_APPLICABLE"}
    imposed = impose_linear_congruence(
        residue=domain.residue,
        modulus=domain.modulus,
        a=domain.A - domain.D,
        b=domain.B,
        congruence_modulus=domain.modulus * domain.D,
    )
    if imposed is None:
        return {"status": "EMPTY"}
    residue, modulus = imposed
    minimum_q = _minimum_in_residue_class(residue, modulus, domain.lower_bound)
    return {
        "status": "PASS",
        "residue": str(residue),
        "modulus": str(modulus),
        "minimum_q": str(minimum_q),
        "modulus_power_of_two_exponent": _power_of_two_exponent(modulus),
    }


def repeatability_domains(domain: CycleDomain, *, repeat_bound: int) -> list[dict[str, Any]]:
    if not domain.accepted:
        return []
    residue = domain.residue
    modulus = domain.modulus
    A_acc = 1
    B_acc = 0
    D_acc = 1
    rows: list[dict[str, Any]] = []
    for repeat_index in range(1, repeat_bound + 1):
        A_acc, B_acc, D_acc = domain.A * A_acc, domain.A * B_acc + domain.B * D_acc, domain.D * D_acc
        A_acc, B_acc, D_acc = _normalise_fraction_triple(A_acc, B_acc, D_acc)
        imposed = impose_linear_congruence(
            residue=residue,
            modulus=modulus,
            a=A_acc,
            b=B_acc - domain.residue * D_acc,
            congruence_modulus=domain.modulus * D_acc,
        )
        if imposed is None:
            rows.append(
                {
                    "repeat_count": repeat_index,
                    "status": "EMPTY",
                    "reason": "no q in the previous exact repeat domain returns to the cycle domain",
                }
            )
            break
        residue, modulus = imposed
        minimum_q = _minimum_in_residue_class(residue, modulus, domain.lower_bound)
        delta = (A_acc - D_acc) * minimum_q + B_acc
        rows.append(
            {
                "repeat_count": repeat_index,
                "status": "PASS",
                "residue": str(residue),
                "modulus": str(modulus),
                "minimum_q": str(minimum_q),
                "composed_A": str(A_acc),
                "composed_B": str(B_acc),
                "composed_D": str(D_acc),
                "growth_delta_at_minimum_q": str(delta),
                "nondescending_at_minimum_q": delta >= 0,
                "modulus_power_of_two_exponent": _power_of_two_exponent(modulus),
            }
        )
    return rows


def classify_cycle_audit(
    *,
    domain: CycleDomain,
    minimum_witness: dict[str, Any],
    return_witness: dict[str, Any] | None,
    repeat_domains: list[dict[str, Any]],
) -> str:
    if not domain.accepted or minimum_witness.get("status") != "PASS":
        return "DOMAIN_OVERAPPROX"
    if minimum_witness.get("raw_collatz_descends_below_start"):
        return "EXECUTABLE_DESCENDS_IN_RAW_COLLatz"
    if return_witness and return_witness.get("status") == "PASS":
        q_final = int(return_witness["q_final"])
        n_final = int(return_witness["n_final"])
        q0 = int(return_witness["q0"])
        n0 = int(return_witness["n0"])
        final_in_cycle_domain = (q_final - domain.residue) % domain.modulus == 0 and q_final >= domain.lower_bound
        if final_in_cycle_domain and q_final >= q0 and n_final >= n0:
            return "EXECUTABLE_REPEATABLE_NON_DESCENDING"
    if repeat_domains and all(row.get("status") == "PASS" for row in repeat_domains):
        if all(row.get("nondescending_at_minimum_q") for row in repeat_domains):
            return "EXECUTABLE_REPEATABLE_NON_DESCENDING"
    q_final = minimum_witness.get("q_final")
    if q_final is not None and (int(q_final) - domain.residue) % domain.modulus != 0:
        return "EXECUTABLE_TRANSIENT"
    return "EXECUTABLE_BOUNDED_REPEAT_DESCENT"


def audit_cycle(
    *,
    cycle_record: dict[str, Any],
    edge_maps_by_id: dict[str, dict[str, Any]],
    repeat_bound: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    edge_ids = [str(edge_id) for edge_id in cycle_record.get("edge_ids") or []]
    edge_maps = [edge_maps_by_id[edge_id] for edge_id in edge_ids]
    cycle_id = _cycle_id(edge_ids, str(cycle_record.get("cycle_id") or ""))
    domain = compose_cycle_domain(edge_maps)
    raw_rows: list[dict[str, Any]] = []
    if not domain.accepted:
        witness = {
            "cycle_id": cycle_id,
            "edge_ids": edge_ids,
            "classification": "DOMAIN_OVERAPPROX",
            "domain_status": "FAIL",
            "domain_failure": domain.failure,
            "domain_trace": list(domain.trace),
            "status": "FAIL",
        }
        return witness, raw_rows

    minimum_witness, rows = replay_cycle_witness(
        cycle_id=cycle_id,
        edge_maps=edge_maps,
        q0=domain.minimum_q,
        witness_kind="minimum_cycle_domain",
    )
    raw_rows.extend(rows)

    return_domain = self_return_domain(domain)
    return_witness: dict[str, Any] | None = None
    if return_domain.get("status") == "PASS":
        return_witness, rows = replay_cycle_witness(
            cycle_id=cycle_id,
            edge_maps=edge_maps,
            q0=int(return_domain["minimum_q"]),
            witness_kind="minimum_self_return_domain",
        )
        raw_rows.extend(rows)

    repeat_domains = repeatability_domains(domain, repeat_bound=repeat_bound)
    classification = classify_cycle_audit(
        domain=domain,
        minimum_witness=minimum_witness,
        return_witness=return_witness,
        repeat_domains=repeat_domains,
    )
    witness = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "cycle_id": cycle_id,
        "edge_ids": edge_ids,
        "edge_sequence": _edge_sequence(edge_maps),
        "cycle_domain": {
            "residue": str(domain.residue),
            "modulus": str(domain.modulus),
            "lower_bound": str(domain.lower_bound),
            "minimum_q": str(domain.minimum_q),
            "modulus_power_of_two_exponent": _power_of_two_exponent(domain.modulus),
        },
        "composed_map": {"A": str(domain.A), "B": str(domain.B), "D": str(domain.D)},
        "domain_trace": list(domain.trace),
        "minimum_cycle_domain_witness": minimum_witness,
        "self_return_domain": return_domain,
        "minimum_self_return_domain_witness": return_witness,
        "repeatability_domains": repeat_domains,
        "classification": classification,
        "status": "PASS" if classification != "DOMAIN_OVERAPPROX" else "FAIL",
        "no_floating_arithmetic": not _contains_float(
            {"cycle_record": cycle_record, "edge_maps": edge_maps, "minimum_witness": minimum_witness}
        ),
    }
    return witness, raw_rows


def cycles_to_audit(
    *,
    obstruction: dict[str, Any],
    cycle_records: list[dict[str, Any]],
    max_cycle_audits: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()

    def add(record: dict[str, Any] | None) -> None:
        if not isinstance(record, dict):
            return
        edge_ids = tuple(str(edge_id) for edge_id in record.get("edge_ids") or [])
        if not edge_ids or edge_ids in seen:
            return
        seen.add(edge_ids)
        selected.append(record)

    add(obstruction.get("representative_non_descending_cycle"))
    for record in cycle_records:
        if len(selected) >= max_cycle_audits:
            break
        if record.get("classification") == "NON_DESCENDING" and record.get("domain_status") == "PASS":
            add(record)
    return selected


def run_cycle_witness_audit(config: dict[str, Any] | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = (
        cfg.get("cycle_witness_audit_run038b", {})
        if isinstance(cfg.get("cycle_witness_audit_run038b", {}), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    obstruction_path = Path(
        run_cfg.get("obstruction")
        or "reports/runs/RUN-038-scc-invariant-discovery/minimal_invariant_obstruction.json"
    )
    edge_maps_path = Path(
        run_cfg.get("edge_maps")
        or "reports/runs/RUN-038-scc-invariant-discovery/scc_edge_maps_normalized.jsonl"
    )
    cycles_path = Path(
        run_cfg.get("cycles")
        or "reports/runs/RUN-038-scc-invariant-discovery/scc_cycles_full_or_basis.jsonl"
    )
    max_cycle_audits = int(run_cfg.get("max_cycle_audits", 64))
    repeat_bound = int(run_cfg.get("repeat_bound", 12))

    obstruction = _load_json(obstruction_path)
    edge_maps = load_jsonl(edge_maps_path)
    edge_maps_by_id = {str(row["edge_id"]): row for row in edge_maps}
    cycle_records = load_jsonl(cycles_path)
    selected_cycles = cycles_to_audit(
        obstruction=obstruction,
        cycle_records=cycle_records,
        max_cycle_audits=max_cycle_audits,
    )

    witnesses: list[dict[str, Any]] = []
    raw_rows: list[dict[str, Any]] = []
    load_failures: list[dict[str, Any]] = []
    for record in selected_cycles:
        try:
            witness, rows = audit_cycle(
                cycle_record=record,
                edge_maps_by_id=edge_maps_by_id,
                repeat_bound=repeat_bound,
            )
            witnesses.append(witness)
            raw_rows.extend(rows)
        except KeyError as exc:
            load_failures.append(
                {
                    "cycle_id": record.get("cycle_id"),
                    "reason": "missing_edge_map",
                    "missing_edge_id": str(exc),
                }
            )

    write_jsonl(out_dir / "cycle_witnesses.jsonl", witnesses)
    write_jsonl(out_dir / "raw_collatz_replay.jsonl", raw_rows)

    classification_counts: dict[str, int] = {}
    for witness in witnesses:
        classification = str(witness.get("classification"))
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
    if load_failures:
        status = "LOAD_FAILURE"
    elif any(row.get("classification") == "DOMAIN_OVERAPPROX" for row in witnesses):
        status = "DOMAIN_OVERAPPROX"
    elif any(row.get("classification") == "EXECUTABLE_REPEATABLE_NON_DESCENDING" for row in witnesses):
        status = "EXECUTABLE_REPEATABLE_NON_DESCENDING"
    elif any(row.get("classification") == "EXECUTABLE_TRANSIENT" for row in witnesses):
        status = "EXECUTABLE_TRANSIENT"
    elif any(row.get("classification") == "EXECUTABLE_DESCENDS_IN_RAW_COLLatz" for row in witnesses):
        status = "EXECUTABLE_DESCENDS_IN_RAW_COLLatz"
    else:
        status = "NO_CYCLE_WITNESSES_AUDITED"

    repeatability_report = {
        "schema": "collatz_lab.run038b_cycle_repeatability_report",
        "version": 1,
        "run_id": RUN_ID,
        "repeat_bound": repeat_bound,
        "classification_counts": classification_counts,
        "audited_cycle_count": len(witnesses),
        "representative_cycle_id": (
            (obstruction.get("representative_non_descending_cycle") or {}).get("cycle_id")
        ),
        "repeatable_cycle_ids": [
            row["cycle_id"]
            for row in witnesses
            if row.get("classification") == "EXECUTABLE_REPEATABLE_NON_DESCENDING"
        ],
        "transient_cycle_ids": [
            row["cycle_id"] for row in witnesses if row.get("classification") == "EXECUTABLE_TRANSIENT"
        ],
        "domain_overapprox_cycle_ids": [
            row["cycle_id"] for row in witnesses if row.get("classification") == "DOMAIN_OVERAPPROX"
        ],
        "status": status,
    }
    _write_json(repeatability_report, out_dir / "cycle_repeatability_report.json")

    result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "floating_point_certificate_used": False,
        "status": status,
        "audited_cycle_count": len(witnesses),
        "raw_collatz_replay_rows": len(raw_rows),
        "classification_counts": classification_counts,
        "load_failures": load_failures,
        "representative_cycle_id": (
            (obstruction.get("representative_non_descending_cycle") or {}).get("cycle_id")
        ),
        "artifacts": {
            "cycle_witnesses": str(out_dir / "cycle_witnesses.jsonl"),
            "raw_collatz_replay": str(out_dir / "raw_collatz_replay.jsonl"),
            "cycle_repeatability_report": str(out_dir / "cycle_repeatability_report.json"),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result

