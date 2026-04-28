"""Independent counterexample-family audit for RUN-039.

This module does not use parent-transition semantics as proof of a Collatz
counterexample family.  It first asks whether the composed cycle map has a
single invariant arithmetic progression, then checks concrete multi-cycle
boundaries with a generated standalone standard-Collatz script that imports no
project code.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .proof_action_scc_ranking_cert import load_jsonl, write_jsonl


RUN_ID = "RUN-039-independent-cycle-counterexample-audit"
SCHEMA = "collatz_lab.counterexample_family_audit"


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


def _minimum_in_residue_class(residue: int, modulus: int, lower_bound: int) -> int:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    residue %= modulus
    if residue >= lower_bound:
        return residue
    return residue + ((lower_bound - residue + modulus - 1) // modulus) * modulus


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_float(item) for item in value)
    return False


def check_affine_self_map_invariance(
    *,
    residue: int,
    modulus: int,
    minimum_q: int,
    A: int,
    B: int,
    D: int,
) -> dict[str, Any]:
    """Prove exact invariance/growth of F(q)=(Aq+B)/D on q == r mod M."""

    if modulus <= 0 or D <= 0:
        raise ValueError("modulus and D must be positive")
    r = residue % modulus
    q_min = _minimum_in_residue_class(r, modulus, minimum_q)
    base_num = A * r + B
    step_num = A * modulus
    integrality_failures = []
    if base_num % D != 0:
        integrality_failures.append(
            {
                "reason": "base_residue_not_integral",
                "congruence": f"A*r+B == {base_num % D} mod D",
                "A_r_plus_B": str(base_num),
                "D": str(D),
            }
        )
    if step_num % D != 0:
        integrality_failures.append(
            {
                "reason": "domain_step_not_integral",
                "congruence": f"A*M == {step_num % D} mod D",
                "A_M": str(step_num),
                "D": str(D),
            }
        )

    return_base = A * r + B - D * r
    return_step = A * modulus
    return_modulus = D * modulus
    domain_failures = []
    if return_base % return_modulus != 0:
        domain_failures.append(
            {
                "reason": "base_residue_does_not_return",
                "congruence": f"A*r+B-D*r == {return_base % return_modulus} mod D*M",
                "A_r_plus_B_minus_D_r": str(return_base),
                "D_M": str(return_modulus),
            }
        )
    if return_step % return_modulus != 0:
        domain_failures.append(
            {
                "reason": "domain_step_does_not_return",
                "congruence": f"A*M == {return_step % return_modulus} mod D*M",
                "A_M": str(return_step),
                "D_M": str(return_modulus),
            }
        )

    slope = A - D
    delta_at_min = slope * q_min + B
    growth_failures = []
    if slope < 0:
        growth_failures.append(
            {
                "reason": "negative_growth_slope",
                "slope_A_minus_D": str(slope),
                "detail": "growth eventually fails on an unbounded arithmetic progression",
            }
        )
    elif delta_at_min <= 0:
        growth_failures.append(
            {
                "reason": "not_growing_at_minimum_q",
                "minimum_q": str(q_min),
                "growth_delta_at_minimum_q": str(delta_at_min),
            }
        )

    q1: int | None = None
    if not integrality_failures:
        q1 = (A * q_min + B) // D
    accepted = not integrality_failures and not domain_failures and not growth_failures
    return {
        "status": "PASS" if accepted else "FAIL",
        "domain": {
            "residue": str(r),
            "modulus": str(modulus),
            "minimum_q": str(q_min),
        },
        "self_map": {"A": str(A), "B": str(B), "D": str(D)},
        "integrality": {
            "status": "PASS" if not integrality_failures else "FAIL",
            "checks": [
                "D | A*r+B",
                "D | A*M",
            ],
            "failures": integrality_failures,
        },
        "domain_invariance": {
            "status": "PASS" if not domain_failures else "FAIL",
            "checks": [
                "D*M | A*r+B-D*r",
                "D*M | A*M",
            ],
            "failures": domain_failures,
        },
        "growth": {
            "status": "PASS" if not growth_failures else "FAIL",
            "slope_A_minus_D": str(slope),
            "minimum_q": str(q_min),
            "growth_delta_at_minimum_q": str(delta_at_min),
            "failures": growth_failures,
        },
        "first_image": {"q0": str(q_min), "q1": str(q1) if q1 is not None else None},
    }


def _edge_parent(label: str) -> int:
    text = str(label)
    return int(text[1:] if text.startswith("P") else text)


def _normalise_edge_sequence(raw_edges: list[dict[str, Any]], witness_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    steps_by_edge = {str(row["edge_id"]): row for row in witness_steps}
    out: list[dict[str, Any]] = []
    for edge in raw_edges:
        edge_id = str(edge["edge_id"])
        step = steps_by_edge.get(edge_id, {})
        out.append(
            {
                "edge_id": edge_id,
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "source_parent": _edge_parent(str(edge["source"])),
                "target_parent": _edge_parent(str(edge["target"])),
                "A": _as_int(edge["A"], "A"),
                "B": _as_int(edge["B"], "B"),
                "D": _as_int(edge["D"], "D"),
                "domain_residue": _as_int(edge["domain_residue"], "domain_residue"),
                "domain_modulus": _as_int(edge["domain_modulus"], "domain_modulus"),
                "branch_id": str(edge.get("branch_id", "")),
                "valuation": str(edge.get("valuation", "")),
                "standard_steps": _as_int(step.get("standard_steps", 0), "standard_steps"),
            }
        )
    return out


def extract_cycle_family(
    *,
    cycle_witnesses: list[dict[str, Any]],
    obstruction: dict[str, Any],
    cycle_id: str = "abbe9ad764c55f27",
) -> dict[str, Any]:
    witness = next((row for row in cycle_witnesses if str(row.get("cycle_id")) == cycle_id), None)
    if witness is None:
        raise ValueError(f"cycle witness not found: {cycle_id}")
    repeat_witness = obstruction.get("repeat_witness") or {}
    self_return_witness = witness.get("minimum_self_return_domain_witness") or {}
    minimum_witness = witness.get("minimum_cycle_domain_witness") or {}
    q0 = _as_int(repeat_witness.get("q0") or self_return_witness.get("q0"), "q0")
    n0 = _as_int(repeat_witness.get("n0") or self_return_witness.get("n0"), "n0")
    raw_edges = obstruction.get("exact_edge_sequence") or witness.get("edge_sequence") or []
    edge_sequence = _normalise_edge_sequence(raw_edges, self_return_witness.get("steps") or minimum_witness.get("steps") or [])
    cycle_domain = obstruction.get("exact_cycle_domain") or witness.get("cycle_domain")
    composed = obstruction.get("composed_map") or witness.get("composed_map")
    self_return_domain = witness.get("self_return_domain") or {}
    return {
        "cycle_id": cycle_id,
        "edge_ids": [str(edge["edge_id"]) for edge in edge_sequence],
        "start_parent": edge_sequence[0]["source"] if edge_sequence else None,
        "cycle_domain": {
            "residue": str(cycle_domain["residue"]),
            "modulus": str(cycle_domain["modulus"]),
            "minimum_q": str(cycle_domain.get("minimum_q") or cycle_domain.get("lower_bound") or 1),
            "lower_bound": str(cycle_domain.get("lower_bound") or cycle_domain.get("minimum_q") or 1),
        },
        "self_return_candidate_domain": {
            "residue": str(self_return_domain.get("residue", "")),
            "modulus": str(self_return_domain.get("modulus", "")),
            "minimum_q": str(self_return_domain.get("minimum_q", "")),
        }
        if self_return_domain.get("status") == "PASS"
        else None,
        "composed_map": {"A": str(composed["A"]), "B": str(composed["B"]), "D": str(composed["D"])},
        "q0": str(q0),
        "n0": str(n0),
        "edge_sequence": edge_sequence,
    }


def standard_collatz_step(n: int) -> int:
    if n <= 0:
        raise ValueError("n must be positive")
    return n // 2 if n % 2 == 0 else 3 * n + 1


def replay_standard_multicycle(
    *,
    q0: int,
    edge_sequence: list[dict[str, Any]],
    cycle_counts: list[int],
) -> list[dict[str, Any]]:
    """Replay the explicit edge path using standard Collatz steps only."""

    rows: list[dict[str, Any]] = []
    start_parent = _as_int(edge_sequence[0]["source_parent"], "source_parent")
    n0 = (1 << start_parent) * q0 - 1
    current_q = q0
    current_n = n0
    completed_cycles = 0
    max_cycle = max(cycle_counts)
    no_drop = True
    while completed_cycles < max_cycle:
        cycle_start_q = current_q
        cycle_start_n = current_n
        cycle_ok = True
        failure: dict[str, Any] | None = None
        for edge_index, edge in enumerate(edge_sequence):
            source_parent = _as_int(edge["source_parent"], "source_parent")
            target_parent = _as_int(edge["target_parent"], "target_parent")
            expected_start_n = (1 << source_parent) * current_q - 1
            if current_n != expected_start_n:
                cycle_ok = False
                failure = {
                    "reason": "bad_start_boundary",
                    "edge_index": edge_index,
                    "edge_id": edge["edge_id"],
                    "actual_n": str(current_n),
                    "expected_n": str(expected_start_n),
                }
                break
            numerator = _as_int(edge["A"], "A") * current_q + _as_int(edge["B"], "B")
            denominator = _as_int(edge["D"], "D")
            if numerator % denominator != 0:
                cycle_ok = False
                failure = {
                    "reason": "expected_q_not_integral",
                    "edge_index": edge_index,
                    "edge_id": edge["edge_id"],
                    "numerator_mod_D": str(numerator % denominator),
                }
                break
            expected_q_next = numerator // denominator
            expected_n_next = (1 << target_parent) * expected_q_next - 1
            values = [current_n]
            for _ in range(_as_int(edge["standard_steps"], "standard_steps")):
                current_n = standard_collatz_step(current_n)
                values.append(current_n)
                if current_n < n0:
                    no_drop = False
            if current_n != expected_n_next:
                cycle_ok = False
                failure = {
                    "reason": "bad_expected_boundary",
                    "edge_index": edge_index,
                    "edge_id": edge["edge_id"],
                    "actual_n": str(current_n),
                    "expected_n": str(expected_n_next),
                    "path_hash": _hash([str(value) for value in values]),
                }
                break
            current_q = expected_q_next
        completed_cycles += 1
        if completed_cycles in cycle_counts or not cycle_ok:
            rows.append(
                {
                    "cycle_count": completed_cycles,
                    "requested_checkpoint": completed_cycles in cycle_counts,
                    "status": "PASS" if cycle_ok else "FAIL",
                    "q_start": str(cycle_start_q),
                    "n_start": str(cycle_start_n),
                    "q_boundary": str(current_q),
                    "n_boundary": str(current_n),
                    "n_increases_from_n0": current_n > n0,
                    "n_increases_this_cycle": current_n > cycle_start_n,
                    "no_intermediate_drop_below_n0": no_drop,
                    "failure": failure,
                }
            )
        if not cycle_ok:
            break
    recorded = {int(row["cycle_count"]) for row in rows}
    for count in cycle_counts:
        if count not in recorded:
            rows.append(
                {
                    "cycle_count": count,
                    "status": "NOT_REACHED",
                    "reason": "earlier cycle replay failed",
                }
            )
    return sorted(rows, key=lambda row: int(row["cycle_count"]))


def _standalone_script_text(payload: dict[str, Any]) -> str:
    return f'''#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

CYCLE_COUNTS = {payload["cycle_counts"]!r}
Q0 = {payload["q0"]}
EDGE_SEQUENCE = {payload["edge_sequence"]!r}


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(data):
    return hashlib.sha256(canonical(data).encode("utf-8")).hexdigest()


def C(n):
    if n <= 0:
        raise ValueError("n must be positive")
    return n // 2 if n % 2 == 0 else 3 * n + 1


def iterate(n, steps):
    values = [n]
    for _ in range(steps):
        n = C(n)
        values.append(n)
    return n, values


def replay():
    rows = []
    start_parent = int(EDGE_SEQUENCE[0]["source_parent"])
    n0 = (1 << start_parent) * Q0 - 1
    current_q = Q0
    current_n = n0
    completed_cycles = 0
    no_drop = True
    max_cycle = max(CYCLE_COUNTS)
    while completed_cycles < max_cycle:
        cycle_start_q = current_q
        cycle_start_n = current_n
        cycle_ok = True
        failure = None
        for edge_index, edge in enumerate(EDGE_SEQUENCE):
            source_parent = int(edge["source_parent"])
            target_parent = int(edge["target_parent"])
            expected_start_n = (1 << source_parent) * current_q - 1
            if current_n != expected_start_n:
                cycle_ok = False
                failure = {{"reason": "bad_start_boundary", "edge_index": edge_index, "edge_id": edge["edge_id"], "actual_n": str(current_n), "expected_n": str(expected_start_n)}}
                break
            numerator = int(edge["A"]) * current_q + int(edge["B"])
            denominator = int(edge["D"])
            if numerator % denominator != 0:
                cycle_ok = False
                failure = {{"reason": "expected_q_not_integral", "edge_index": edge_index, "edge_id": edge["edge_id"], "numerator_mod_D": str(numerator % denominator)}}
                break
            expected_q_next = numerator // denominator
            expected_n_next = (1 << target_parent) * expected_q_next - 1
            current_n, values = iterate(current_n, int(edge["standard_steps"]))
            if min(values) < n0:
                no_drop = False
            if current_n != expected_n_next:
                cycle_ok = False
                failure = {{"reason": "bad_expected_boundary", "edge_index": edge_index, "edge_id": edge["edge_id"], "actual_n": str(current_n), "expected_n": str(expected_n_next), "path_hash": digest([str(value) for value in values])}}
                break
            current_q = expected_q_next
        completed_cycles += 1
        if completed_cycles in CYCLE_COUNTS or not cycle_ok:
            rows.append({{"cycle_count": completed_cycles, "requested_checkpoint": completed_cycles in CYCLE_COUNTS, "status": "PASS" if cycle_ok else "FAIL", "q_start": str(cycle_start_q), "n_start": str(cycle_start_n), "q_boundary": str(current_q), "n_boundary": str(current_n), "n_increases_from_n0": current_n > n0, "n_increases_this_cycle": current_n > cycle_start_n, "no_intermediate_drop_below_n0": no_drop, "failure": failure}})
        if not cycle_ok:
            break
    recorded = {{int(row["cycle_count"]) for row in rows}}
    for count in CYCLE_COUNTS:
        if count not in recorded:
            rows.append({{"cycle_count": count, "status": "NOT_REACHED", "reason": "earlier cycle replay failed"}})
    return sorted(rows, key=lambda row: int(row["cycle_count"]))


def main():
    out = Path("raw_collatz_multicycle_replay.jsonl")
    import sys
    if len(sys.argv) > 1:
        out = Path(sys.argv[1])
    rows = replay()
    out.write_text("\\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\\n", encoding="utf-8")
    print(json.dumps({{"status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL", "rows": rows}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
'''


def write_and_run_standalone_replay(
    *,
    script_path: Path,
    out_jsonl: Path,
    q0: int,
    edge_sequence: list[dict[str, Any]],
    cycle_counts: list[int],
) -> list[dict[str, Any]]:
    payload = {
        "q0": q0,
        "edge_sequence": [
            {
                "edge_id": edge["edge_id"],
                "source_parent": int(edge["source_parent"]),
                "target_parent": int(edge["target_parent"]),
                "A": int(edge["A"]),
                "B": int(edge["B"]),
                "D": int(edge["D"]),
                "standard_steps": int(edge["standard_steps"]),
            }
            for edge in edge_sequence
        ],
        "cycle_counts": cycle_counts,
    }
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(_standalone_script_text(payload), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(script_path.resolve()), str(out_jsonl.resolve())],
        check=True,
        cwd=str(script_path.parent.resolve()),
    )
    return load_jsonl(out_jsonl)


def compare_project_and_standalone_first_cycle(
    *,
    raw_project_rows: list[dict[str, Any]],
    cycle_id: str,
    witness_kind: str,
    edge_sequence: list[dict[str, Any]],
) -> dict[str, Any]:
    project = [
        row
        for row in raw_project_rows
        if str(row.get("cycle_id")) == cycle_id and str(row.get("witness_kind")) == witness_kind
    ]
    if len(project) != len(edge_sequence):
        return {
            "status": "FAIL",
            "reason": "project_raw_replay_rows_missing",
            "expected": len(edge_sequence),
            "actual": len(project),
        }
    failures = []
    for project_row, edge in zip(project, edge_sequence, strict=True):
        if str(project_row.get("edge_id")) != str(edge["edge_id"]):
            failures.append({"reason": "edge_id_order_mismatch", "project": project_row.get("edge_id"), "edge": edge["edge_id"]})
        if int((project_row.get("parent_transition") or {}).get("standard_steps")) != int(edge["standard_steps"]):
            failures.append({"reason": "standard_step_mismatch", "edge_id": edge["edge_id"]})
        if project_row.get("status") != "PASS" or (project_row.get("raw_collatz") or {}).get("status") != "PASS":
            failures.append({"reason": "project_raw_replay_not_pass", "edge_id": edge["edge_id"]})
    return {"status": "PASS" if not failures else "FAIL", "failures": failures}


def build_counterexample_family_certificate(
    *,
    cycle_family: dict[str, Any],
    invariant_check: dict[str, Any],
    multicycle_rows: list[dict[str, Any]],
    project_compare: dict[str, Any],
) -> dict[str, Any] | None:
    proof = {
        "integrality": invariant_check.get("integrality", {}).get("status"),
        "domain_invariance": invariant_check.get("domain_invariance", {}).get("status"),
        "growth": invariant_check.get("growth", {}).get("status"),
        "raw_collatz_replay": project_compare.get("status"),
        "multi_cycle_replay": "PASS" if all(row.get("status") == "PASS" for row in multicycle_rows) else "FAIL",
    }
    if any(value != "PASS" for value in proof.values()):
        return None
    A = cycle_family["composed_map"]["A"]
    B = cycle_family["composed_map"]["B"]
    D = cycle_family["composed_map"]["D"]
    q0 = int(cycle_family["q0"])
    q1 = (int(A) * q0 + int(B)) // int(D)
    start_parent = str(cycle_family["start_parent"])
    start_parent_number = _edge_parent(start_parent)
    n0 = (1 << start_parent_number) * q0 - 1
    n1 = (1 << start_parent_number) * q1 - 1
    return {
        "type": "COLLATZ_NON_DESCENDING_FAMILY_CERTIFICATE",
        "cycle_id": cycle_family["cycle_id"],
        "status": "PASS",
        "statement": "For all q in this exact arithmetic progression, the standard Collatz orbit follows a repeatable cycle and never descends below its start.",
        "start_parent": start_parent,
        "domain": invariant_check["domain"],
        "self_map": {"A": A, "B": B, "D": D, "F(q)": "(A*q+B)/D"},
        "proof": proof,
        "first_witness": {"q0": str(q0), "n0": str(n0), "q1": str(q1), "n1": str(n1)},
        "certificate_hash": _hash(
            {
                "cycle_id": cycle_family["cycle_id"],
                "domain": invariant_check["domain"],
                "self_map": {"A": A, "B": B, "D": D},
                "proof": proof,
                "q0": str(q0),
            }
        ),
    }


def _bug_or_mismatch_status(
    *,
    invariant_checks: list[dict[str, Any]],
    project_compare: dict[str, Any],
    multicycle_rows: list[dict[str, Any]],
) -> str:
    if all(check.get("status") != "PASS" for check in invariant_checks):
        return "CYCLE_INVARIANCE_FAIL"
    if project_compare.get("status") != "PASS":
        return "PARENT_TRANSITION_SEMANTICS_MISMATCH"
    if any(row.get("failure", {}).get("reason") == "bad_expected_boundary" for row in multicycle_rows if isinstance(row.get("failure"), dict)):
        return "RAW_COLLATZ_REPLAY_BUG"
    if any(row.get("failure", {}).get("reason") == "expected_q_not_integral" for row in multicycle_rows if isinstance(row.get("failure"), dict)):
        return "PARENT_COORDINATE_MAP_BUG"
    return "CYCLE_INVARIANCE_FAIL"


def run_counterexample_audit(config: dict[str, Any] | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = (
        cfg.get("counterexample_audit_run039", {})
        if isinstance(cfg.get("counterexample_audit_run039", {}), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    cycle_witnesses_path = Path(
        run_cfg.get("cycle_witnesses") or "reports/runs/RUN-038B-cycle-witness-audit/cycle_witnesses.jsonl"
    )
    raw_replay_path = Path(
        run_cfg.get("raw_collatz_replay") or "reports/runs/RUN-038B-cycle-witness-audit/raw_collatz_replay.jsonl"
    )
    obstruction_path = Path(
        run_cfg.get("minimal_invariant_obstruction")
        or "reports/runs/RUN-038E-scc-refinement-and-invariant-discovery/minimal_invariant_obstruction.json"
    )
    cycle_id = str(run_cfg.get("cycle_id") or "abbe9ad764c55f27")
    cycle_counts = [int(value) for value in run_cfg.get("cycle_counts", [1, 2, 5, 10])]

    cycle_witnesses = load_jsonl(cycle_witnesses_path)
    raw_project_rows = load_jsonl(raw_replay_path)
    obstruction = _load_json(obstruction_path)
    cycle_family = extract_cycle_family(cycle_witnesses=cycle_witnesses, obstruction=obstruction, cycle_id=cycle_id)
    A = int(cycle_family["composed_map"]["A"])
    B = int(cycle_family["composed_map"]["B"])
    D = int(cycle_family["composed_map"]["D"])

    candidate_domains: list[dict[str, Any]] = [
        {"name": "cycle_domain", **cycle_family["cycle_domain"]},
    ]
    if cycle_family.get("self_return_candidate_domain"):
        candidate_domains.append({"name": "self_return_candidate_domain", **cycle_family["self_return_candidate_domain"]})

    invariant_checks = []
    for domain in candidate_domains:
        check = check_affine_self_map_invariance(
            residue=int(domain["residue"]),
            modulus=int(domain["modulus"]),
            minimum_q=int(domain["minimum_q"]),
            A=A,
            B=B,
            D=D,
        )
        check["domain_name"] = domain["name"]
        invariant_checks.append(check)
    accepted_invariant = next((check for check in invariant_checks if check.get("status") == "PASS"), None)

    script_path = out_dir / "standalone_replay_script.py"
    raw_multicycle_path = out_dir / "raw_collatz_multicycle_replay.jsonl"
    multicycle_rows = write_and_run_standalone_replay(
        script_path=script_path,
        out_jsonl=raw_multicycle_path,
        q0=int(cycle_family["q0"]),
        edge_sequence=cycle_family["edge_sequence"],
        cycle_counts=cycle_counts,
    )
    project_compare = compare_project_and_standalone_first_cycle(
        raw_project_rows=raw_project_rows,
        cycle_id=cycle_id,
        witness_kind="minimum_self_return_domain",
        edge_sequence=cycle_family["edge_sequence"],
    )

    certificate = None
    if accepted_invariant is not None:
        certificate = build_counterexample_family_certificate(
            cycle_family=cycle_family,
            invariant_check=accepted_invariant,
            multicycle_rows=multicycle_rows,
            project_compare=project_compare,
        )
    if certificate is None:
        certificate = {
            "type": "COLLATZ_NON_DESCENDING_FAMILY_CERTIFICATE",
            "cycle_id": cycle_id,
            "status": "FAIL",
            "reason": "all exact invariance and replay checks must pass before emitting a counterexample-family candidate",
        }
    _write_json(certificate, out_dir / "counterexample_family_certificate.json")

    cycle_invariance_report = {
        "schema": "collatz_lab.run039_cycle_invariance_report",
        "version": 1,
        "run_id": RUN_ID,
        "cycle_family": cycle_family,
        "invariant_checks": invariant_checks,
        "accepted_invariant_domain": accepted_invariant.get("domain_name") if accepted_invariant else None,
        "project_vs_standalone_first_cycle": project_compare,
        "multi_cycle_summary": multicycle_rows,
    }
    _write_json(cycle_invariance_report, out_dir / "cycle_invariance_report.json")

    if certificate.get("status") == "PASS":
        status = "COUNTEREXAMPLE_FAMILY_CANDIDATE"
    else:
        status = _bug_or_mismatch_status(
            invariant_checks=invariant_checks,
            project_compare=project_compare,
            multicycle_rows=multicycle_rows,
        )
    result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_tuning_launched": False,
        "verifier_relaxed": False,
        "floating_point_certificate_used": False,
        "status": status,
        "cycle_id": cycle_id,
        "counterexample_family_certificate_status": certificate.get("status"),
        "invariant_domain_pass_count": sum(1 for check in invariant_checks if check.get("status") == "PASS"),
        "project_standalone_replay_agree": project_compare.get("status") == "PASS",
        "standalone_multicycle_all_pass": all(row.get("status") == "PASS" for row in multicycle_rows),
        "no_floating_arithmetic": not _contains_float(
            {"cycle_family": cycle_family, "invariant_checks": invariant_checks, "multicycle_rows": multicycle_rows}
        ),
        "artifacts": {
            "counterexample_family_certificate": str(out_dir / "counterexample_family_certificate.json"),
            "standalone_replay_script": str(script_path),
            "raw_collatz_multicycle_replay": str(raw_multicycle_path),
            "cycle_invariance_report": str(out_dir / "cycle_invariance_report.json"),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result
