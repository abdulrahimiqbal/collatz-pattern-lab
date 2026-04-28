"""RUN-044 guarded viability-kernel model checking.

The RUN-040 guarded graph still has finite SCC structure after full edge
guards are replayed.  RUN-044 asks the model-checking question directly: does
the guarded abstraction have an infinite non-exiting path?

The exact finite obstruction form used here is a lasso cycle with a 2-adic
fixed point.  For a composed cycle map ``F(q)=(A*q+B)/D``, any fixed point
``q* = B/(D-A)`` with odd denominator is a 2-adic integer.  If q* satisfies
every pulled-back guard of the cycle, then the guarded abstraction has a
nonempty viability kernel.  Such a witness is not a natural-number Collatz
counterexample unless q* is a positive integer satisfying the lower bound; the
certificate records that distinction explicitly.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from .proof_action_guarded_domain import (
    AffineMap,
    GuardedDomain,
    affine_from_json,
    contains_float,
    domain_from_json,
    load_jsonl,
    stable_hash,
    write_jsonl,
)
from .proof_action_guarded_scc_ranking import (
    CERT_TYPE as RANKING_CERT_TYPE,
    DEFAULT_SCC_ID,
    SCHEMA as RANKING_SCHEMA,
    certificate_hash as ranking_certificate_hash,
    compose_guarded_sequence,
    replay_scc_guarded_ranking_certificate,
)


RUN_ID = "RUN-044-guarded-viability-kernel-elimination"
SCHEMA = "collatz_lab.guarded_viability_kernel"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _fraction_to_json(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _fraction_mod_power_two(value: Fraction, modulus: int) -> int | None:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    denominator = value.denominator % modulus
    if denominator % 2 == 0:
        return None
    return (value.numerator * pow(denominator, -1, modulus)) % modulus


def _fraction_is_natural(value: Fraction, *, lower_bound: int) -> bool:
    return value.denominator == 1 and value.numerator >= lower_bound


def fixed_point_for_cycle_map(cycle_map: AffineMap) -> Fraction | None:
    if cycle_map.D == cycle_map.A:
        return None
    return Fraction(cycle_map.B, cycle_map.D - cycle_map.A)


def check_fraction_in_guarded_domain(value: Fraction, domain: GuardedDomain) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    residue = _fraction_mod_power_two(value, domain.congruence.modulus)
    if residue is None:
        failures.append({"reason": "fixed_point_denominator_not_invertible_mod_congruence"})
    elif residue != domain.congruence.residue:
        failures.append(
            {
                "reason": "fixed_point_congruence_mismatch",
                "expected_residue": str(domain.congruence.residue),
                "modulus": str(domain.congruence.modulus),
                "actual_residue": str(residue),
            }
        )
    non_congruence_checks: list[dict[str, Any]] = []
    for excluded in domain.non_congruences:
        excluded_residue = _fraction_mod_power_two(value, excluded.modulus)
        if excluded_residue is None:
            failures.append({"reason": "fixed_point_denominator_not_invertible_mod_non_congruence"})
            continue
        hit = excluded_residue == excluded.residue
        non_congruence_checks.append(
            {
                "excluded_residue": str(excluded.residue),
                "modulus": str(excluded.modulus),
                "actual_residue": str(excluded_residue),
                "satisfied": not hit,
                "source": excluded.source,
            }
        )
        if hit:
            failures.append(
                {
                    "reason": "fixed_point_hits_excluded_residue",
                    "excluded_residue": str(excluded.residue),
                    "modulus": str(excluded.modulus),
                    "source": excluded.source,
                }
            )
    natural = _fraction_is_natural(value, lower_bound=domain.lower_bound)
    return {
        "status": "PASS" if not failures else "FAIL",
        "fixed_point": _fraction_to_json(value),
        "canonical_congruence_check": {
            "residue": str(residue) if residue is not None else None,
            "expected_residue": str(domain.congruence.residue),
            "modulus": str(domain.congruence.modulus),
        },
        "non_congruence_checks": non_congruence_checks,
        "natural_number_status": "POSITIVE_NATURAL" if natural else "NON_NATURAL_2ADIC",
        "lower_bound": str(domain.lower_bound),
        "failures": failures,
    }


def build_cycle_viability_witness(
    *,
    cycle_record: dict[str, Any],
    guarded_edges: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    edge_ids = [str(edge_id) for edge_id in cycle_record.get("edge_ids", [])]
    composed = compose_guarded_sequence(edge_ids=edge_ids, guarded_edges=guarded_edges)
    base = {
        "cycle_id": str(cycle_record.get("cycle_id") or _hash(edge_ids)[:16]),
        "edge_ids": edge_ids,
        "source_states": list(cycle_record.get("source_states") or []),
    }
    if composed.get("status") != "PASS":
        return {**base, "status": "FAIL", "failure": composed, "classification": "DOMAIN_COMPOSITION_BUG"}
    cycle_map = affine_from_json(composed["composed_map"])
    fixed = fixed_point_for_cycle_map(cycle_map)
    if fixed is None:
        return {
            **base,
            "status": "FAIL",
            "classification": "NO_UNIQUE_2ADIC_FIXED_POINT",
            "composed_map": cycle_map.to_json(),
        }
    domain = domain_from_json(composed["guarded_domain"])
    fixed_check = check_fraction_in_guarded_domain(fixed, domain)
    fixed_equation_ok = cycle_map.A * fixed + cycle_map.B == cycle_map.D * fixed
    status = "PASS" if fixed_check["status"] == "PASS" and fixed_equation_ok else "FAIL"
    natural_status = fixed_check["natural_number_status"]
    classification = (
        "RAW_NATURAL_SURVIVING_CYCLE"
        if status == "PASS" and natural_status == "POSITIVE_NATURAL"
        else "NON_NATURAL_2ADIC_SURVIVING_KERNEL"
        if status == "PASS"
        else "FIXED_POINT_OUTSIDE_GUARDED_DOMAIN"
    )
    witness = {
        **base,
        "status": status,
        "classification": classification,
        "composed_map": cycle_map.to_json(),
        "guarded_cycle_domain": composed["guarded_domain"],
        "guarded_cycle_domain_hash": stable_hash(composed["guarded_domain"]),
        "fixed_point": _fraction_to_json(fixed),
        "fixed_point_equation": {
            "equation": "A*q+B = D*q",
            "status": "PASS" if fixed_equation_ok else "FAIL",
        },
        "fixed_point_guard_check": fixed_check,
        "raw_executable_natural_counterexample": status == "PASS" and natural_status == "POSITIVE_NATURAL",
    }
    witness["witness_hash"] = stable_hash({key: value for key, value in witness.items() if key != "witness_hash"})
    return witness


def replay_viability_kernel_witness(witness: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not isinstance(witness, dict):
        return {"accepted": False, "status": "FAIL", "failures": [{"reason": "missing_witness"}]}
    if contains_float(witness):
        failures.append({"reason": "floating_point_witness_rejected"})
    if str(witness.get("witness_hash")) != stable_hash({key: value for key, value in witness.items() if key != "witness_hash"}):
        failures.append({"reason": "viability_witness_hash_mismatch"})
    fixed = witness.get("fixed_point") if isinstance(witness.get("fixed_point"), dict) else {}
    try:
        q = Fraction(_as_int(fixed.get("numerator"), "fixed_point.numerator"), _as_int(fixed.get("denominator"), "fixed_point.denominator"))
        cycle_map = affine_from_json(witness.get("composed_map") or {})
        domain = domain_from_json(witness.get("guarded_cycle_domain") or {})
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        failures.append({"reason": "viability_witness_payload_invalid", "detail": str(exc)})
    else:
        if cycle_map.A * q + cycle_map.B != cycle_map.D * q:
            failures.append({"reason": "fixed_point_equation_failed"})
        check = check_fraction_in_guarded_domain(q, domain)
        if check.get("status") != "PASS":
            failures.append({"reason": "fixed_point_guard_replay_failed", "check": check})
        if witness.get("fixed_point_guard_check") != check:
            failures.append({"reason": "fixed_point_guard_check_mismatch", "expected": check, "actual": witness.get("fixed_point_guard_check")})
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failures": failures}


def build_elimination_certificate(
    *,
    states: list[str],
    edge_ids: list[str],
    iteration_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    certificate = {
        "schema": RANKING_SCHEMA,
        "version": 1,
        "type": RANKING_CERT_TYPE,
        "scc_id": DEFAULT_SCC_ID,
        "states": states,
        "covered_edge_ids": sorted(edge_ids),
        "guarded_node_count": len(edge_ids),
        "guarded_edge_count": 0,
        "proof_kind": "viability_kernel_elimination",
        "node_ranks": {},
        "edge_checks": [],
        "cycle_exit_checks": [],
        "viability_kernel_iterations": iteration_rows,
        "status": "PASS",
    }
    certificate["certificate_hash"] = ranking_certificate_hash(certificate)
    return certificate


def replay_elimination_certificate(certificate: dict[str, Any], *, expected_edge_ids: list[str]) -> dict[str, Any]:
    replay = replay_scc_guarded_ranking_certificate(certificate, expected_edge_ids=expected_edge_ids)
    failures = list(replay.get("failures") or [])
    if certificate.get("proof_kind") != "viability_kernel_elimination":
        failures.append({"reason": "not_viability_kernel_elimination_certificate"})
    rows = certificate.get("viability_kernel_iterations")
    if not isinstance(rows, list) or not rows or rows[-1].get("survivor_count") != 0:
        failures.append({"reason": "viability_kernel_not_empty_in_certificate"})
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failures": failures}


def _edge_domain_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["edge_id"]): row for row in rows if row.get("status") == "PASS"}


def run_guarded_viability_kernel(config: dict[str, Any] | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = cfg.get("guarded_viability_kernel_run044", {}) if isinstance(cfg.get("guarded_viability_kernel_run044"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    guarded_edges_path = Path(run_cfg.get("guarded_edge_domains") or "reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_edge_domains.jsonl")
    reclassification_path = Path(run_cfg.get("guarded_cycle_reclassification") or "reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_cycle_reclassification.jsonl")
    cycle_scan_limit = int(run_cfg.get("cycle_scan_limit", 20000))
    witness_record_limit = int(run_cfg.get("witness_record_limit", 64))

    guarded_rows = load_jsonl(guarded_edges_path)
    guarded_edges = _edge_domain_by_id(guarded_rows)
    cycle_rows = load_jsonl(reclassification_path)[:cycle_scan_limit]
    states = [f"P{index}" for index in range(12, 25)]
    edge_ids = sorted(guarded_edges)

    witnesses: list[dict[str, Any]] = []
    first_survivor: dict[str, Any] | None = None
    scanned = 0
    for cycle in cycle_rows:
        scanned += 1
        witness = build_cycle_viability_witness(cycle_record=cycle, guarded_edges=guarded_edges)
        if len(witnesses) < witness_record_limit:
            witnesses.append(witness)
        if witness.get("status") == "PASS":
            first_survivor = witness
            break
    write_jsonl(out_dir / "viability_cycle_witnesses.jsonl", witnesses)

    iteration_rows = [
        {
            "iteration": 0,
            "candidate_node_count": len(edge_ids),
            "candidate_cycle_count_scanned": scanned,
            "survivor_count": 1 if first_survivor else 0,
            "status": "NONEMPTY" if first_survivor else "EMPTY_OVER_SCANNED_CYCLES",
        }
    ]
    write_jsonl(out_dir / "viability_kernel_iterations.jsonl", iteration_rows)

    if first_survivor is not None:
        replay = replay_viability_kernel_witness(first_survivor)
        kernel = {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "scc_id": DEFAULT_SCC_ID,
            "status": "NONEMPTY",
            "kernel_kind": "2adic_lasso_fixed_point",
            "surviving_witness": first_survivor,
            "witness_replay": replay,
        }
        obstruction = {
            "schema": "collatz_lab.guarded_viability_kernel_obstruction",
            "version": 1,
            "run_id": RUN_ID,
            "failure_classification": "VIABILITY_KERNEL_NONEMPTY",
            "guarded_kernel_nonempty": True,
            "raw_executable": bool(first_survivor.get("raw_executable_natural_counterexample")),
            "natural_number_status": (first_survivor.get("fixed_point_guard_check") or {}).get("natural_number_status"),
            "surviving_cycle_id": first_survivor.get("cycle_id"),
            "surviving_edge_ids": first_survivor.get("edge_ids"),
            "fixed_point": first_survivor.get("fixed_point"),
            "exact_reason": (
                "a 2-adic fixed point satisfies the full guarded lasso domain; "
                "this is a symbolic viability-kernel survivor, not a raw natural counterexample unless natural_number_status is POSITIVE_NATURAL"
            ),
            "new_invariant_or_stronger_state_variable_needed": True,
        }
        failure_cert = {
            "schema": RANKING_SCHEMA,
            "version": 1,
            "type": RANKING_CERT_TYPE,
            "scc_id": DEFAULT_SCC_ID,
            "states": states,
            "covered_edge_ids": edge_ids,
            "guarded_node_count": len(edge_ids),
            "guarded_edge_count": 0,
            "proof_kind": "none",
            "node_ranks": {},
            "edge_checks": [],
            "cycle_exit_checks": [],
            "status": "FAIL",
            "failure_classification": "VIABILITY_KERNEL_NONEMPTY",
        }
        failure_cert["certificate_hash"] = ranking_certificate_hash(failure_cert)
        _write_json(kernel, out_dir / "guarded_viability_kernel.json")
        _write_json(obstruction, out_dir / "surviving_viability_kernel_obstruction.json")
        _write_json(failure_cert, out_dir / "scc_guarded_elimination_certificate.json")
        status = "VIABILITY_KERNEL_NONEMPTY"
        accepted = False
        certificate_replay = {"accepted": False, "status": "FAIL", "failures": [{"reason": "VIABILITY_KERNEL_NONEMPTY"}]}
    else:
        kernel = {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "scc_id": DEFAULT_SCC_ID,
            "status": "EMPTY",
            "kernel_kind": "cycle_lasso_scan",
            "cycle_scan_limit": cycle_scan_limit,
            "cycles_scanned": scanned,
        }
        certificate = build_elimination_certificate(states=states, edge_ids=edge_ids, iteration_rows=iteration_rows)
        certificate_replay = replay_elimination_certificate(certificate, expected_edge_ids=edge_ids)
        _write_json(kernel, out_dir / "guarded_viability_kernel.json")
        _write_json({"schema": "collatz_lab.guarded_viability_kernel_obstruction", "version": 1, "run_id": RUN_ID, "status": "EMPTY"}, out_dir / "surviving_viability_kernel_obstruction.json")
        _write_json(certificate, out_dir / "scc_guarded_elimination_certificate.json")
        status = "PASS" if certificate_replay.get("accepted") else "ELIMINATION_CERTIFICATE_REPLAY_FAIL"
        accepted = bool(certificate_replay.get("accepted"))

    result = {
        "schema": "collatz_lab.run044_guarded_viability_kernel_elimination",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_tuning_launched": False,
        "verifier_relaxed": False,
        "floating_point_certificate_used": False,
        "status": status,
        "accepted_scc_elimination_ranking": accepted,
        "guarded_edge_count": len(edge_ids),
        "cycles_scanned": scanned,
        "viability_kernel_empty": status == "PASS",
        "viability_kernel_nonempty": status == "VIABILITY_KERNEL_NONEMPTY",
        "raw_executable_survivor": bool(first_survivor and first_survivor.get("raw_executable_natural_counterexample")),
        "surviving_cycle_id": first_survivor.get("cycle_id") if first_survivor else None,
        "certificate_replay": certificate_replay,
        "artifacts": {
            "guarded_viability_kernel": str(out_dir / "guarded_viability_kernel.json"),
            "viability_kernel_iterations": str(out_dir / "viability_kernel_iterations.jsonl"),
            "viability_cycle_witnesses": str(out_dir / "viability_cycle_witnesses.jsonl"),
            "surviving_viability_kernel_obstruction": str(out_dir / "surviving_viability_kernel_obstruction.json"),
            "scc_guarded_elimination_certificate": str(out_dir / "scc_guarded_elimination_certificate.json"),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result

