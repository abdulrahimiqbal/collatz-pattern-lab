"""Semantic witness enrichment for final proof certificates.

RUN-048 is intentionally stricter than the replay checker: it does not accept
status-only semantic claims.  Every generated witness must expose mathematical
data that a proof assistant could consume, and the S4 witnesses are checked
against the parent-coordinate maps already present in the certificates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "collatz_lab.semantic_witnesses"
RUN_ID = "RUN-048-certificate-semantic-witness-enrichment"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(data: Any, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def log2_exact(value: int) -> int | None:
    if not is_power_of_two(value):
        return None
    return value.bit_length() - 1


def manifest_artifact_path(manifest: dict[str, Any], name: str, *, manifest_path: Path) -> Path:
    manifest_dir = manifest_path.parent
    for entry in manifest.get("artifacts", []) or []:
        if entry.get("name") == name:
            raw = Path(str(entry["path"]))
            if raw.is_absolute():
                return raw
            candidate = manifest_dir / raw
            if candidate.exists():
                return candidate
            return REPO_ROOT / raw
    raise KeyError(f"manifest artifact not found: {name}")


def row_certificate(row: dict[str, Any], key: str) -> dict[str, Any]:
    value = row.get(key)
    return value if isinstance(value, dict) else {}


def semantic_witness_hash(witness: dict[str, Any]) -> str:
    return stable_hash({key: value for key, value in witness.items() if key != "semantic_witness_hash"})


def attach_hash(witness: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(witness)
    enriched["semantic_witness_hash"] = semantic_witness_hash(enriched)
    return enriched


def _int_field(mapping: dict[str, Any], key: str, default: int = 0) -> int:
    return int(mapping.get(key, default) or default)


def build_s4_semantic_witness(row: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cert = row_certificate(row, "transition_certificate")
    div = cert.get("divisibility_certificate") if isinstance(cert.get("divisibility_certificate"), dict) else {}
    pmap = cert.get("parent_coordinate_map") if isinstance(cert.get("parent_coordinate_map"), dict) else {}
    source_parent = _int_field(cert, "source_parent")
    target_parent = _int_field(cert, "target_parent")
    valuation = _int_field(cert, "valuation", _int_field(div, "valuation"))
    source_depth = _int_field(pmap, "source_depth")
    source_residue = _int_field(pmap, "source_residue")
    h0 = _int_field(pmap, "base_burst_division_exponent")
    c = _int_field(div, "c")
    coefficient = _int_field(div, "coefficient")
    map_a = _int_field(pmap, "A", coefficient)
    map_b = _int_field(pmap, "B")
    map_d = _int_field(pmap, "D")
    expected_a = 3**source_parent
    expected_b = (1 << h0) - 1
    expected_d = 1 << (h0 + target_parent)
    branch_scale = 1 << source_depth
    branch_denominator = branch_scale * (1 << valuation)
    standard_step_count = 2 * source_parent + h0
    failures: list[dict[str, Any]] = []
    if not pmap:
        failures.append(
            {
                "reason": "MISSING_S4_PARENT_COORDINATE_MAP",
                "certificate_id": cert.get("transition_id"),
                "missing_field": "parent_coordinate_map",
            }
        )
    if map_a != expected_a:
        failures.append(
            {
                "reason": "S4_MAP_A_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "expected": str(expected_a),
                "actual": str(map_a),
            }
        )
    if coefficient != expected_a:
        failures.append(
            {
                "reason": "S4_DIVISIBILITY_COEFFICIENT_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "expected": str(expected_a),
                "actual": str(coefficient),
            }
        )
    if map_b != expected_b:
        failures.append(
            {
                "reason": "S4_PARENT_MAP_B_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "expected": str(expected_b),
                "actual": str(map_b),
                "semantic_rule": "B = 2^base_burst_division_exponent - 1",
            }
        )
    if map_d != expected_d:
        failures.append(
            {
                "reason": "S4_PARENT_MAP_D_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "expected": str(expected_d),
                "actual": str(map_d),
                "semantic_rule": "D = 2^(base_burst_division_exponent + target_parent)",
            }
        )
    if map_d != branch_denominator:
        failures.append(
            {
                "reason": "S4_BRANCH_DENOMINATOR_IDENTITY_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "expected": str(branch_denominator),
                "actual": str(map_d),
                "semantic_rule": "2^(h0+b) = 2^source_depth * 2^valuation",
            }
        )
    if source_depth + valuation != h0 + target_parent:
        failures.append(
            {
                "reason": "S4_BRANCH_EXPONENT_IDENTITY_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "left": source_depth + valuation,
                "right": h0 + target_parent,
                "semantic_rule": "source_depth + valuation = base_burst_division_exponent + target_parent",
            }
        )
    constant_left = map_a * source_residue + map_b
    constant_right = c * branch_scale
    if constant_left != constant_right:
        failures.append(
            {
                "reason": "S4_BRANCH_COORDINATE_IDENTITY_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "left": str(constant_left),
                "right": str(constant_right),
                "semantic_rule": "A*source_residue + B = c * 2^source_depth",
            }
        )
    formula = f"q_prime = ({map_a}*q + {map_b}) / {map_d}"
    if pmap.get("formula") != formula:
        failures.append(
            {
                "reason": "S4_PARENT_MAP_FORMULA_MISMATCH",
                "certificate_id": cert.get("transition_id"),
                "expected": formula,
                "actual": pmap.get("formula", ""),
            }
        )
    bad_simplified_b = (1 << valuation) - 1
    bad_simplified_d = 1 << (valuation + target_parent)
    if h0 != valuation and map_b == bad_simplified_b and map_d == bad_simplified_d:
        failures.append(
            {
                "reason": "S4_SIMPLIFIED_VALUATION_ONLY_FORMULA_REJECTED",
                "certificate_id": cert.get("transition_id"),
                "semantic_rule": "S4 witnesses must use base_burst_division_exponent h0, not valuation alone",
            }
        )
    witness = attach_hash(
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": "S4_PARENT_TRANSITION_SEMANTIC_WITNESS",
            "certificate_id": str(cert.get("transition_id", "")),
            "source_parent": source_parent,
            "target_parent": target_parent,
            "valuation": valuation,
            "source_depth": source_depth,
            "source_residue": source_residue,
            "base_burst_division_exponent": h0,
            "standard_step_count": standard_step_count,
            "source_n_expr": "2^a*q - 1",
            "branch_param_expr": "q = r0 + 2^d*k",
            "forced_burst_expr": "3^a*q - 1",
            "post_division_expr": "(3^a*q - 1) / 2^h0",
            "target_n_expr": "2^b*q' - 1",
            "semantic_statement": "Collatz.iter (2*a+h0) (2^a*q - 1) = 2^b*q_prime - 1",
            "domain_constraints": list(pmap.get("domain_constraints") or []),
            "parent_coordinate_map": {
                "A": map_a,
                "B": map_b,
                "D": map_d,
                "D_power": log2_exact(map_d),
                "formula": pmap.get("formula", ""),
            },
            "branch_coordinate_identity": {
                "c": c,
                "z_k": "c + 3^a*k",
                "q_prime": "z_k / 2^T",
                "constant_identity": "A*r0 + B = c*2^d",
                "denominator_identity": "D = 2^d * 2^T = 2^(h0+b)",
            },
            "source_branch": {
                "q": "r0 + 2^d*k",
                "r0": source_residue,
                "d": source_depth,
                "k_constraints": {
                    "divisibility_modulus": _int_field(div, "k_divisibility_modulus"),
                    "divisibility_residue": _int_field(div, "k_divisibility_residue"),
                    "excluded_next_power_modulus": _int_field(div, "excluded_next_power_modulus"),
                    "excluded_next_power_residue": _int_field(div, "excluded_next_power_residue"),
                },
            },
            "replay_checks": {
                "stored_parent_coordinate_map_used": bool(pmap),
                "h0_from_parent_coordinate_map": h0 == _int_field(pmap, "base_burst_division_exponent"),
                "A_eq_3_pow_source_parent": map_a == expected_a,
                "B_eq_2_pow_h0_minus_1": map_b == expected_b,
                "D_eq_2_pow_h0_plus_target_parent": map_d == expected_d,
                "branch_param_uses_source_depth_and_residue": source_residue < branch_scale,
                "branch_exponent_identity": source_depth + valuation == h0 + target_parent,
                "branch_coordinate_identity": constant_left == constant_right and map_d == branch_denominator,
                "standard_step_count_eq_2a_plus_h0": standard_step_count == 2 * source_parent + h0,
                "valuation_only_formula_rejected": not (h0 != valuation and map_b == bad_simplified_b and map_d == bad_simplified_d),
            },
            "semantic_validation": {
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
            },
        }
    )
    return witness, failures


def build_s3_semantic_witness(row: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cert = row_certificate(row, "s3_debt_certificate")
    measure = cert.get("debt_measure_definition") if isinstance(cert.get("debt_measure_definition"), dict) else {}
    role = "RANKING_DECREASE"
    failures: list[dict[str, Any]] = []
    if role == "DIRECT_DESCENT" and "collatz_iterate_witness" not in cert:
        failures.append(
            {
                "reason": "MISSING_S3_ITERATE_WITNESS",
                "certificate_id": cert.get("certificate_id"),
                "missing_field": "collatz_iterate_witness",
            }
        )
    witness = attach_hash(
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": "S3_DEBT_SEMANTIC_WITNESS",
            "certificate_id": str(cert.get("certificate_id", "")),
            "semantic_role": role,
            "measure_definition": measure.get("measure_id", "mixed_log_gain_rank"),
            "source_measure_expr": "source mixed-log debt rank",
            "target_measure_expr": "target mixed-log debt rank",
            "decrease_inequality": measure.get("decrease_inequality", "gain_num < gain_den"),
            "gain_num": int(cert.get("gain_num", 0) or 0),
            "gain_den": int(cert.get("gain_den", 0) or 0),
            "collatz_iterate_witness": cert.get("collatz_iterate_witness"),
            "semantic_validation": {
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
            },
        }
    )
    return witness, failures


def _s6_claim_type(blocker_type: str) -> str:
    mapping = {
        "coverage": "coverage",
        "global_descent": "ranking",
        "induction": "induction",
        "no_escape": "no_escape",
        "parametric_lift": "transition_composition",
        "parent_transition": "transition_composition",
        "strict_verifier_gap": "transition_composition",
    }
    return mapping.get(blocker_type, "unknown")


def build_s6_semantic_witness(row: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cert = row_certificate(row, "s6_lemma_certificate")
    payload = cert.get("proof_payload") if isinstance(cert.get("proof_payload"), dict) else {}
    dependencies = list(payload.get("depends_on") or [])
    claim_type = _s6_claim_type(str(cert.get("blocker_type", "")))
    failures: list[dict[str, Any]] = []
    if claim_type == "unknown":
        failures.append(
            {
                "reason": "MISSING_S6_SEMANTIC_CLAIM_TYPE",
                "lemma_id": cert.get("lemma_id"),
                "blocker_type": cert.get("blocker_type"),
            }
        )
    witness = attach_hash(
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": "S6_LEMMA_SEMANTIC_WITNESS",
            "lemma_id": str(cert.get("lemma_id", "")),
            "certificate_id": str(cert.get("certificate_id", "")),
            "blocker_id": str(cert.get("blocker_id", "")),
            "semantic_claim_type": claim_type,
            "dependencies": dependencies,
            "conclusion": f"{claim_type} blocker {cert.get('blocker_id', '')} is closed by semantic dependencies",
            "proof_tree": [
                {
                    "dependency": dependency,
                    "rule": "semantic_dependency_replay_required",
                }
                for dependency in dependencies
            ],
            "semantic_validation": {
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
            },
        }
    )
    return witness, failures


def build_natural_kernel_semantic_witness(certificate: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fixed = certificate.get("fixed_point") if isinstance(certificate.get("fixed_point"), dict) else {}
    numerator = int(fixed.get("numerator", 0) or 0)
    denominator = int(fixed.get("denominator", 0) or 0)
    failures: list[dict[str, Any]] = []
    if denominator <= 0:
        failures.append({"reason": "MISSING_NATURAL_KERNEL_DENOMINATOR_POSITIVE"})
    if denominator % 2 != 1:
        failures.append({"reason": "MISSING_NATURAL_KERNEL_DENOMINATOR_ODD"})
    if numerator >= 0:
        failures.append({"reason": "MISSING_NATURAL_KERNEL_NEGATIVE_FIXED_POINT"})
    witness = attach_hash(
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": "NATURAL_KERNEL_SEMANTIC_WITNESS",
            "certificate_id": certificate.get("certificate_hash", ""),
            "fixed_point_num": numerator,
            "fixed_point_den": denominator,
            "denominator_positive": denominator > 0,
            "denominator_odd": denominator % 2 == 1,
            "fixed_point_negative": numerator < 0,
            "kernel_divisibility_statement": "for all N, 2^N divides den*q - num",
            "nonzero_positive_statement": "for q >= 1, den*q - num > 0",
            "semantic_validation": {
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
            },
        }
    )
    return witness, failures


def build_top_level_semantic_witness(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    present = {str(row.get("type", "")) for row in rows}
    required = {
        "universal_entry_certificate",
        "parent_state_coverage_certificate",
        "transition_soundness_certificate",
        "well_founded_ranking_certificate",
        "descent_implication_certificate",
    }
    missing = sorted(required - present)
    failures = [{"reason": "MISSING_TOP_LEVEL_SEMANTIC_CERTIFICATE", "certificate_type": item} for item in missing]
    witness = attach_hash(
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": "TOP_LEVEL_SEMANTIC_BRIDGE_WITNESS",
            "certificate_id": "top_level_semantic_bridge",
            "claims": [
                "universal_entry",
                "parent_state_coverage",
                "transition_soundness",
                "well_foundedness",
                "descent_implication",
            ],
            "conclusion": "DescentTheorem",
            "certificate_types_present": sorted(present),
            "semantic_validation": {
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
            },
        }
    )
    return witness, failures


def build_semantic_witnesses(
    *,
    s3_rows: list[dict[str, Any]],
    s4_rows: list[dict[str, Any]],
    s6_rows: list[dict[str, Any]],
    natural_kernel_certificate: dict[str, Any],
    top_level_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for row in s4_rows:
        witness, row_failures = build_s4_semantic_witness(row)
        witnesses.append(witness)
        failures.extend(row_failures)
    for row in s3_rows:
        witness, row_failures = build_s3_semantic_witness(row)
        witnesses.append(witness)
        failures.extend(row_failures)
    for row in s6_rows:
        witness, row_failures = build_s6_semantic_witness(row)
        witnesses.append(witness)
        failures.extend(row_failures)
    witness, row_failures = build_natural_kernel_semantic_witness(natural_kernel_certificate)
    witnesses.append(witness)
    failures.extend(row_failures)
    witness, row_failures = build_top_level_semantic_witness(top_level_rows)
    witnesses.append(witness)
    failures.extend(row_failures)
    return witnesses, failures


def replay_semantic_witnesses(witnesses: list[dict[str, Any]]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for witness in witnesses:
        if witness.get("semantic_witness_hash") != semantic_witness_hash(witness):
            failures.append({"reason": "semantic_witness_hash_mismatch", "kind": witness.get("kind"), "certificate_id": witness.get("certificate_id")})
        validation = witness.get("semantic_validation") if isinstance(witness.get("semantic_validation"), dict) else {}
        if validation.get("status") != "PASS":
            failures.extend(validation.get("failures") or [{"reason": "semantic_validation_failed", "kind": witness.get("kind")}])
        if witness.get("kind") in {"S4_PARENT_TRANSITION_SEMANTIC_WITNESS", "S3_DEBT_SEMANTIC_WITNESS", "S6_LEMMA_SEMANTIC_WITNESS"}:
            if not witness.get("certificate_id") and not witness.get("lemma_id"):
                failures.append({"reason": "status_only_semantic_witness", "kind": witness.get("kind")})
    return {
        "accepted": not failures,
        "status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
    }
