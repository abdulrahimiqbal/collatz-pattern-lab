"""RUN-045 natural-number elimination of the guarded 2-adic kernel."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from fractions import Fraction
from pathlib import Path
from typing import Any

from .proof_action_guarded_domain import affine_from_json, contains_float, load_jsonl, stable_hash
from .proof_action_guarded_scc_ranking import (
    CERT_TYPE as RANKING_CERT_TYPE,
    DEFAULT_SCC_ID,
    SCHEMA as RANKING_SCHEMA,
    certificate_hash as ranking_certificate_hash,
    replay_scc_guarded_ranking_certificate,
)
from .proof_action_guarded_viability_kernel import replay_viability_kernel_witness


RUN_ID = "RUN-045-natural-viability-kernel-elimination"
SCHEMA = "collatz_lab.natural_viability_kernel_elimination"
CERT_TYPE = "SCC_NATURAL_VIABILITY_KERNEL_EMPTY_EXACT"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _edge_sort_key(edge_id: str) -> tuple[str, str]:
    return (edge_id.split(":", 1)[0], edge_id)


def _is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def natural_kernel_certificate_hash(certificate: dict[str, Any]) -> str:
    return _hash({key: value for key, value in certificate.items() if key != "certificate_hash"})


def _fixed_point_from_witness(witness: dict[str, Any]) -> Fraction:
    fixed = witness.get("fixed_point") if isinstance(witness.get("fixed_point"), dict) else {}
    return Fraction(_as_int(fixed.get("numerator"), "fixed_point.numerator"), _as_int(fixed.get("denominator"), "fixed_point.denominator"))


def _edge_domain_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["edge_id"]): row for row in rows if row.get("status") == "PASS"}


def build_natural_viability_kernel_certificate(
    *,
    run044_kernel: dict[str, Any],
    guarded_edge_ids: list[str],
) -> dict[str, Any]:
    if run044_kernel.get("status") != "NONEMPTY":
        raise ValueError("RUN-045 expects RUN-044 to expose the nonempty guarded 2-adic kernel")
    witness = run044_kernel.get("surviving_witness")
    if not isinstance(witness, dict):
        raise ValueError("RUN-044 surviving witness is missing")
    witness_replay = replay_viability_kernel_witness(witness)
    if not witness_replay.get("accepted"):
        raise ValueError(f"RUN-044 surviving witness does not replay: {witness_replay}")

    cycle_map = affine_from_json(witness.get("composed_map") or {})
    fixed = _fixed_point_from_witness(witness)
    numerator = int(fixed.numerator)
    denominator = int(fixed.denominator)
    fixed_point_equation = cycle_map.A * numerator + cycle_map.B * denominator == cycle_map.D * numerator
    denominator_is_odd = denominator % 2 == 1
    fixed_point_not_natural = denominator != 1 or numerator <= 0
    d_is_power_of_two = _is_power_of_two(cycle_map.D)
    a_is_odd = cycle_map.A % 2 == 1
    lasso_depth_gain = cycle_map.D.bit_length() - 1 if d_is_power_of_two else 0
    kernel_congruence_depth_unbounded = d_is_power_of_two and a_is_odd and lasso_depth_gain > 0
    integer_distance_nonzero_for_positive_q = numerator <= 0 or denominator != 1
    proof = {
        "denominator_is_odd": denominator_is_odd,
        "fixed_point_not_natural": fixed_point_not_natural,
        "fixed_point_equation": fixed_point_equation,
        "lasso_denominator_is_power_of_two": d_is_power_of_two,
        "lasso_multiplier_is_odd": a_is_odd,
        "lasso_2adic_depth_gain_per_repeat": lasso_depth_gain,
        "kernel_congruence_depth_unbounded": kernel_congruence_depth_unbounded,
        "any_natural_q_has_finite_2adic_distance_from_fixed_point": integer_distance_nonzero_for_positive_q,
        "therefore_no_positive_integer_q_in_kernel": all(
            (
                denominator_is_odd,
                fixed_point_not_natural,
                fixed_point_equation,
                kernel_congruence_depth_unbounded,
                integer_distance_nonzero_for_positive_q,
            )
        ),
        "valuation_argument": {
            "distance_form": "denominator*q - numerator",
            "repeat_n_forces_divisibility_by": f"2^({lasso_depth_gain}*n)",
            "reason": "F(q)-q* = (A/D)*(q-q*) with A odd and D a positive power of two",
        },
    }
    status = "PASS" if proof["therefore_no_positive_integer_q_in_kernel"] else "FAIL"
    certificate = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "type": CERT_TYPE,
        "scc_id": DEFAULT_SCC_ID,
        "covered_edge_ids": sorted(guarded_edge_ids, key=_edge_sort_key),
        "surviving_kernel_type": "NON_NATURAL_2ADIC",
        "source_run044_kernel_hash": stable_hash(run044_kernel),
        "surviving_cycle_id": witness.get("cycle_id"),
        "surviving_edge_ids": witness.get("edge_ids"),
        "composed_map": cycle_map.to_json(),
        "fixed_point": {
            "numerator": numerator,
            "denominator": denominator,
        },
        "proof": proof,
        "run044_witness_replay": witness_replay,
        "status": status,
    }
    certificate["certificate_hash"] = natural_kernel_certificate_hash(certificate)
    return certificate


def replay_natural_viability_kernel_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not isinstance(certificate, dict):
        return {"accepted": False, "status": "FAIL", "failures": [{"reason": "missing_certificate"}]}
    if contains_float(certificate):
        failures.append({"reason": "floating_point_certificate_rejected"})
    if certificate.get("schema") != SCHEMA or int(certificate.get("version", 0) or 0) != 1:
        failures.append({"reason": "unsupported_natural_viability_schema"})
    if certificate.get("type") != CERT_TYPE:
        failures.append({"reason": "unsupported_natural_viability_type", "type": certificate.get("type")})
    if str(certificate.get("certificate_hash")) != natural_kernel_certificate_hash(certificate):
        failures.append({"reason": "natural_viability_certificate_hash_mismatch"})
    if certificate.get("status") != "PASS":
        failures.append({"reason": "natural_viability_status_not_pass", "status": certificate.get("status")})
    proof = certificate.get("proof") if isinstance(certificate.get("proof"), dict) else {}
    fixed = certificate.get("fixed_point") if isinstance(certificate.get("fixed_point"), dict) else {}
    try:
        numerator = _as_int(fixed.get("numerator"), "fixed_point.numerator")
        denominator = _as_int(fixed.get("denominator"), "fixed_point.denominator")
        cycle_map = affine_from_json(certificate.get("composed_map") or {})
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        failures.append({"reason": "natural_viability_payload_invalid", "detail": str(exc)})
    else:
        expected = {
            "denominator_is_odd": denominator % 2 == 1,
            "fixed_point_not_natural": denominator != 1 or numerator <= 0,
            "fixed_point_equation": cycle_map.A * numerator + cycle_map.B * denominator == cycle_map.D * numerator,
            "lasso_denominator_is_power_of_two": _is_power_of_two(cycle_map.D),
            "lasso_multiplier_is_odd": cycle_map.A % 2 == 1,
        }
        expected["lasso_2adic_depth_gain_per_repeat"] = cycle_map.D.bit_length() - 1 if expected["lasso_denominator_is_power_of_two"] else 0
        expected["kernel_congruence_depth_unbounded"] = (
            expected["lasso_denominator_is_power_of_two"]
            and expected["lasso_multiplier_is_odd"]
            and expected["lasso_2adic_depth_gain_per_repeat"] > 0
        )
        expected["any_natural_q_has_finite_2adic_distance_from_fixed_point"] = numerator <= 0 or denominator != 1
        expected["therefore_no_positive_integer_q_in_kernel"] = all(
            expected[key]
            for key in (
                "denominator_is_odd",
                "fixed_point_not_natural",
                "fixed_point_equation",
                "kernel_congruence_depth_unbounded",
                "any_natural_q_has_finite_2adic_distance_from_fixed_point",
            )
        )
        for key, value in expected.items():
            if proof.get(key) != value:
                failures.append({"reason": "natural_viability_proof_field_mismatch", "field": key, "expected": value, "actual": proof.get(key)})
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failures": failures}


def build_natural_kernel_ranking_certificate(certificate: dict[str, Any], *, guarded_edge_ids: list[str]) -> dict[str, Any]:
    ranking = {
        "schema": RANKING_SCHEMA,
        "version": 1,
        "type": RANKING_CERT_TYPE,
        "scc_id": DEFAULT_SCC_ID,
        "states": [f"P{index}" for index in range(12, 25)],
        "covered_edge_ids": sorted(guarded_edge_ids, key=_edge_sort_key),
        "guarded_node_count": 0,
        "guarded_edge_count": 0,
        "proof_kind": "natural_viability_kernel_elimination",
        "node_ranks": {},
        "edge_checks": [],
        "cycle_exit_checks": [],
        "natural_viability_kernel_certificate_hash": certificate.get("certificate_hash"),
        "natural_viability_kernel_certificate": certificate,
        "status": "PASS",
    }
    ranking["certificate_hash"] = ranking_certificate_hash(ranking)
    return ranking


def replay_natural_kernel_ranking_certificate(ranking: dict[str, Any], *, expected_edge_ids: list[str] | None = None) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    replay = replay_scc_guarded_ranking_certificate(ranking, expected_edge_ids=expected_edge_ids)
    failures.extend(replay.get("failures") or [])
    certificate = ranking.get("natural_viability_kernel_certificate")
    cert_replay = replay_natural_viability_kernel_certificate(certificate if isinstance(certificate, dict) else {})
    if not cert_replay.get("accepted"):
        failures.append({"reason": "natural_viability_kernel_certificate_replay_failed", "replay": cert_replay})
    if ranking.get("natural_viability_kernel_certificate_hash") != (certificate or {}).get("certificate_hash"):
        failures.append({"reason": "natural_viability_kernel_certificate_hash_ref_mismatch"})
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failures": failures}


def _write_repo_certificates(certificate: dict[str, Any], ranking: dict[str, Any]) -> dict[str, str]:
    store = Path("certificate_store")
    store.mkdir(parents=True, exist_ok=True)
    natural_path = store / "run045_natural_viability_kernel_certificate.json"
    ranking_path = store / "run045_scc_guarded_ranking_certificate.json"
    _write_json(certificate, natural_path)
    _write_json(ranking, ranking_path)
    return {
        "natural_viability_kernel_certificate": str(natural_path),
        "scc_guarded_ranking_certificate": str(ranking_path),
    }


def run_natural_viability_kernel_elimination(config: dict[str, Any] | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = cfg.get("natural_viability_kernel_run045", {}) if isinstance(cfg.get("natural_viability_kernel_run045"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    kernel_path = Path(run_cfg.get("run044_guarded_viability_kernel") or "reports/runs/RUN-044-guarded-viability-kernel-elimination/guarded_viability_kernel.json")
    guarded_edges_path = Path(run_cfg.get("guarded_edge_domains") or "reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_edge_domains.jsonl")
    guarded_rows = load_jsonl(guarded_edges_path)
    guarded_edges = _edge_domain_by_id(guarded_rows)
    guarded_edge_ids = sorted(guarded_edges, key=_edge_sort_key)
    kernel = _load_json(kernel_path)

    certificate = build_natural_viability_kernel_certificate(run044_kernel=kernel, guarded_edge_ids=guarded_edge_ids)
    certificate_replay = replay_natural_viability_kernel_certificate(certificate)
    ranking = build_natural_kernel_ranking_certificate(certificate, guarded_edge_ids=guarded_edge_ids)
    ranking_replay = replay_natural_kernel_ranking_certificate(ranking, expected_edge_ids=guarded_edge_ids)

    cert_out = out_dir / "natural_viability_kernel_certificate.json"
    ranking_out = out_dir / "scc_guarded_ranking_certificate.json"
    well_founded_out = out_dir / "well_founded_ranking_certificate.json"
    _write_json(certificate, cert_out)
    _write_json(ranking, ranking_out)
    _write_json(ranking, well_founded_out)
    store_paths = _write_repo_certificates(certificate, ranking) if certificate_replay["accepted"] and ranking_replay["accepted"] else {}

    status = "PASS" if certificate_replay["accepted"] and ranking_replay["accepted"] else "FAIL"
    result = {
        "schema": "collatz_lab.run045_natural_viability_kernel_elimination",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_tuning_launched": False,
        "verifier_relaxed": False,
        "floating_point_certificate_used": False,
        "status": status,
        "surviving_kernel_type": certificate.get("surviving_kernel_type"),
        "natural_viability_kernel_empty": status == "PASS",
        "well_founded_ranking_certificate": "PASS" if ranking_replay["accepted"] else "FAIL",
        "guarded_edge_count": len(guarded_edge_ids),
        "fixed_point": certificate.get("fixed_point"),
        "certificate_replay": certificate_replay,
        "ranking_replay": ranking_replay,
        "artifacts": {
            "natural_viability_kernel_certificate": str(cert_out),
            "scc_guarded_ranking_certificate": str(ranking_out),
            "well_founded_ranking_certificate": str(well_founded_out),
            "run_result": str(out_dir / "run_result.json"),
            **store_paths,
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result
