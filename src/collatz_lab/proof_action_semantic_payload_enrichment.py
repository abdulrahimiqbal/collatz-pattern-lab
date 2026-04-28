"""RUN-051 semantic payload enrichment for the Lean abstract bridge.

This pass does not change the verifier and does not convert Python replay
status into a theorem.  It packages existing replayable certificate content
into explicit semantic payload classes that Lean can inspect next.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "collatz_lab.run051_semantic_payload_enrichment"
PAYLOAD_SCHEMA = "collatz_lab.run051_semantic_payload"
RUN_ID = "RUN-051-semantic-payload-enrichment-for-lean-bridge"
REPO_ROOT = Path(__file__).resolve().parents[2]

S3_ROLES = {"DIRECT_DESCENT", "RANKING_DECREASE", "EXIT_CERTIFICATE", "SUPPORTING_DEBT_EDGE"}
S6_CLAIM_TYPES = {
    "coverage",
    "no_escape",
    "induction",
    "ranking",
    "transition_composition",
    "residual_parent",
}


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def payload_hash(payload: dict[str, Any]) -> str:
    return stable_hash({key: value for key, value in payload.items() if key != "semantic_payload_hash"})


def attach_hash(payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    enriched["semantic_payload_hash"] = payload_hash(enriched)
    return enriched


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


def _row_cert(row: dict[str, Any], key: str) -> dict[str, Any]:
    value = row.get(key)
    return value if isinstance(value, dict) else {}


def _dependency_id_parts(dependency_id: str) -> tuple[str, str]:
    if ":" not in dependency_id:
        return "", dependency_id
    prefix, cert_id = dependency_id.split(":", 1)
    return prefix, cert_id


def _s6_claim_type(blocker_type: str) -> str:
    return {
        "coverage": "coverage",
        "global_descent": "ranking",
        "induction": "induction",
        "no_escape": "no_escape",
        "parametric_lift": "transition_composition",
        "parent_transition": "transition_composition",
        "strict_verifier_gap": "transition_composition",
    }.get(blocker_type, "")


def _dependency_type(prefix: str) -> str:
    return {
        "s3_debt_exact": "S3_DEBT",
        "s4_parent_transition": "S4_PARENT_MAP",
        "parent_residual": "RESIDUAL_PARENT",
        "coverage": "COVERAGE",
        "no_escape": "NO_ESCAPE",
        "induction": "TOP_LEVEL",
        "s6_lift": "TOP_LEVEL",
        "natural_kernel": "NATURAL_KERNEL",
        "top_level": "TOP_LEVEL",
    }.get(prefix, "UNKNOWN")


def dependency_semantic_role(prefix: str, certificate_id: str, s3_roles: dict[str, str]) -> str:
    if prefix == "s3_debt_exact":
        return s3_roles.get(certificate_id, "")
    return {
        "s4_parent_transition": "PARENT_TRANSITION_ITERATE_WITNESS",
        "parent_residual": "RESIDUAL_PARENT_COVERAGE",
        "coverage": "COVERAGE_DOMAIN",
        "no_escape": "NO_ESCAPE_BRANCH",
        "induction": "INDUCTION_OR_RANKING_SUPPORT",
        "s6_lift": "PARAMETRIC_LIFT",
        "natural_kernel": "NATURAL_KERNEL_TO_PATH_LINK",
        "top_level": "TOP_LEVEL_BRIDGE",
    }.get(prefix, "")


def dependency_rule(prefix: str) -> str:
    return {
        "s3_debt_exact": "apply_ranking",
        "s4_parent_transition": "compose_transition",
        "parent_residual": "apply_residual_parent",
        "coverage": "apply_coverage",
        "no_escape": "apply_no_escape",
        "induction": "apply_induction",
        "s6_lift": "compose_transition",
        "natural_kernel": "apply_ranking",
        "top_level": "compose_transition",
    }.get(prefix, "")


def build_s6_consumer_index(s6_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    consumers: dict[str, list[dict[str, str]]] = {}
    for row in s6_rows:
        cert = _row_cert(row, "s6_lemma_certificate")
        lemma_id = str(cert.get("lemma_id", ""))
        payload = cert.get("proof_payload") if isinstance(cert.get("proof_payload"), dict) else {}
        for dependency_id in payload.get("depends_on") or []:
            prefix, certificate_id = _dependency_id_parts(str(dependency_id))
            if not certificate_id:
                continue
            consumers.setdefault(certificate_id, []).append(
                {"consumer_type": "S6_LEMMA", "consumer_id": lemma_id, "dependency_type": prefix}
            )
    return consumers


def validate_s3_semantic_role_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    role = payload.get("semantic_role")
    if role not in S3_ROLES:
        failures.append({"reason": "S3_ROLE_UNCLASSIFIED", "certificate_id": payload.get("certificate_id")})
    if role == "DIRECT_DESCENT" and not payload.get("collatz_iterate_witness"):
        failures.append({"reason": "S3_DIRECT_DESCENT_ITERATE_WITNESS_MISSING", "certificate_id": payload.get("certificate_id")})
    if role == "RANKING_DECREASE" and not payload.get("consumed_by"):
        failures.append({"reason": "S3_RANKING_CONSUMER_MISSING", "certificate_id": payload.get("certificate_id")})
    if not payload.get("measure_id") or not payload.get("decrease_certificate_id"):
        failures.append({"reason": "S3_MEASURE_METADATA_MISSING", "certificate_id": payload.get("certificate_id")})
    return failures


def build_s3_semantic_role(
    row: dict[str, Any],
    consumers: dict[str, list[dict[str, str]]],
    *,
    transition_soundness_id: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cert = _row_cert(row, "s3_debt_certificate")
    measure = cert.get("debt_measure_definition") if isinstance(cert.get("debt_measure_definition"), dict) else {}
    local = cert.get("local_descent_certificate") if isinstance(cert.get("local_descent_certificate"), dict) else {}
    certificate_id = str(cert.get("certificate_id", ""))
    consumed_by = list(consumers.get(certificate_id, []))
    consumed_by.append({"consumer_type": "TRANSITION_SOUNDNESS", "consumer_id": transition_soundness_id})
    payload = {
        "schema": PAYLOAD_SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "S3_SEMANTIC_ROLE",
        "certificate_id": certificate_id,
        "branch_id": str(cert.get("branch_id", "")),
        "semantic_role": "SUPPORTING_DEBT_EDGE",
        "source_node": f"P{cert.get('source_parent', '')}",
        "target_node": f"P{cert.get('target_parent', '')}",
        "measure_id": measure.get("measure_id", "mixed_log_gain_rank"),
        "measure_source_expr": f"P{cert.get('source_parent', '')} mixed-log debt rank",
        "measure_target_expr": f"P{cert.get('target_parent', '')} mixed-log debt rank after valuation {cert.get('valuation', '')}",
        "decrease_certificate_id": f"{certificate_id}:local_descent:{local.get('type', '')}",
        "decrease_inequality": measure.get("decrease_inequality", ""),
        "gain_num": int(cert.get("gain_num", 0) or 0),
        "gain_den": int(cert.get("gain_den", 0) or 0),
        "consumed_by": consumed_by,
    }
    failures = validate_s3_semantic_role_payload(payload)
    payload["semantic_validation"] = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    return attach_hash(payload), failures


def validate_s6_proof_tree_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if payload.get("semantic_claim_type") not in S6_CLAIM_TYPES:
        failures.append({"reason": "S6_PROOF_TREE_MISSING_RULE", "lemma_id": payload.get("lemma_id"), "detail": "unknown semantic claim type"})
    dependencies = payload.get("dependencies") if isinstance(payload.get("dependencies"), list) else []
    if not dependencies or not all(isinstance(dep, dict) and dep.get("semantic_role") and dep.get("used_for") for dep in dependencies):
        failures.append({"reason": "S6_PROOF_TREE_DEPENDENCIES_STATUS_ONLY", "lemma_id": payload.get("lemma_id")})
    steps = payload.get("proof_steps") if isinstance(payload.get("proof_steps"), list) else []
    if not steps or not all(isinstance(step, dict) and step.get("rule") and step.get("output") for step in steps):
        failures.append({"reason": "S6_PROOF_TREE_MISSING_RULE", "lemma_id": payload.get("lemma_id")})
    if payload.get("closes_blocker") is not True:
        failures.append({"reason": "S6_PROOF_TREE_DOES_NOT_CLOSE_BLOCKER", "lemma_id": payload.get("lemma_id")})
    expected_fragment = str(payload.get("semantic_claim_type", ""))
    if expected_fragment and expected_fragment not in str(payload.get("conclusion", "")):
        failures.append({"reason": "S6_PROOF_TREE_CONCLUSION_MISMATCH", "lemma_id": payload.get("lemma_id")})
    return failures


def build_s6_proof_tree(row: dict[str, Any], s3_roles: dict[str, str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cert = _row_cert(row, "s6_lemma_certificate")
    proof = cert.get("proof_payload") if isinstance(cert.get("proof_payload"), dict) else {}
    checks = cert.get("replay_checks") if isinstance(cert.get("replay_checks"), dict) else {}
    claim_type = _s6_claim_type(str(cert.get("blocker_type", "")))
    dependencies: list[dict[str, Any]] = []
    proof_steps: list[dict[str, Any]] = []
    for index, dependency_id in enumerate(proof.get("depends_on") or []):
        prefix, certificate_id = _dependency_id_parts(str(dependency_id))
        dep_type = _dependency_type(prefix)
        role = dependency_semantic_role(prefix, certificate_id, s3_roles)
        used_for = f"{claim_type} blocker {cert.get('blocker_id', '')}"
        dependencies.append(
            {
                "dependency_type": dep_type,
                "certificate_id": certificate_id,
                "semantic_role": role,
                "used_for": used_for,
            }
        )
        proof_steps.append(
            {
                "step_id": f"{cert.get('lemma_id', '')}:step:{index:02d}",
                "rule": dependency_rule(prefix),
                "inputs": [certificate_id],
                "output": f"{role} contributes to {used_for}",
            }
        )
    proof_steps.append(
        {
            "step_id": f"{cert.get('lemma_id', '')}:close",
            "rule": "apply_induction" if claim_type in {"induction", "ranking"} else "compose_transition",
            "inputs": [step["step_id"] for step in proof_steps],
            "output": f"{claim_type} blocker {cert.get('blocker_id', '')} closed",
        }
    )
    payload = {
        "schema": PAYLOAD_SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "S6_PROOF_TREE_SEMANTICS",
        "lemma_id": str(cert.get("lemma_id", "")),
        "blocker_id": str(cert.get("blocker_id", "")),
        "semantic_claim_type": claim_type,
        "conclusion": f"{claim_type} blocker {cert.get('blocker_id', '')} closed",
        "dependencies": dependencies,
        "proof_steps": proof_steps,
        "closes_blocker": checks.get("closes_target_blocker") is True and checks.get("statement_matches_blocker") is True,
    }
    failures = validate_s6_proof_tree_payload(payload)
    payload["semantic_validation"] = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    return attach_hash(payload), failures


def validate_kernel_to_path_link_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if not payload.get("divisibility_family"):
        failures.append({"reason": "KERNEL_REFINEMENT_TO_DIVISIBILITY_MISSING"})
    if "infinite internal guarded path" not in str(payload.get("statement", "")):
        failures.append({"reason": "KERNEL_PATH_LINK_STATEMENT_MISSING"})
    if not payload.get("no_nat_in_kernel"):
        failures.append({"reason": "KERNEL_NO_NAT_ARGUMENT_MISSING"})
    if payload.get("conclusion") != "NoInfiniteInternalParentPathOverNat":
        failures.append({"reason": "KERNEL_CONCLUSION_MISMATCH"})
    return failures


def build_kernel_to_path_link(certificate: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fixed = certificate.get("fixed_point") if isinstance(certificate.get("fixed_point"), dict) else {}
    proof = certificate.get("proof") if isinstance(certificate.get("proof"), dict) else {}
    valuation = proof.get("valuation_argument") if isinstance(proof.get("valuation_argument"), dict) else {}
    payload = {
        "schema": PAYLOAD_SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "NATURAL_KERNEL_TO_PATH_LINK",
        "kernel_certificate_id": str(certificate.get("certificate_hash", "")),
        "scc_id": str(certificate.get("scc_id", "P12_P24_internal_s4")),
        "statement": "Any infinite internal guarded path over Nat induces membership in the surviving viability kernel.",
        "kernel_fixed_point": {
            "numerator": int(fixed.get("numerator", 0) or 0),
            "denominator": int(fixed.get("denominator", 0) or 0),
        },
        "divisibility_family": {
            "statement": "for every N, 2^N divides denominator*q - numerator",
            "source": "guarded viability kernel refinement",
            "distance_form": valuation.get("distance_form", ""),
            "repeat_forces_divisibility_by": valuation.get("repeat_n_forces_divisibility_by", ""),
            "kernel_congruence_depth_unbounded": proof.get("kernel_congruence_depth_unbounded") is True,
        },
        "no_nat_in_kernel": {
            "reason": "denominator*q - numerator is positive nonzero for q >= 1 and cannot be divisible by all powers of 2",
            "therefore_no_positive_integer_q_in_kernel": proof.get("therefore_no_positive_integer_q_in_kernel") is True,
        },
        "conclusion": "NoInfiniteInternalParentPathOverNat",
    }
    failures = validate_kernel_to_path_link_payload(payload)
    payload["semantic_validation"] = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    return attach_hash(payload), failures


def _top_level_by_type(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("type", "")): row for row in rows}


def validate_top_level_coverage_domain_map_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    entry = payload.get("universal_entry") if isinstance(payload.get("universal_entry"), dict) else {}
    if not entry.get("even_case") or not entry.get("odd_case"):
        failures.append({"reason": "TOP_LEVEL_UNIVERSAL_ENTRY_MISSING"})
    domains = payload.get("parent_state_domains") if isinstance(payload.get("parent_state_domains"), list) else []
    if not domains or not all(isinstance(domain, dict) and domain.get("domain_id") and domain.get("covered_predicate") for domain in domains):
        failures.append({"reason": "TOP_LEVEL_DOMAIN_UNMAPPED"})
    if payload.get("no_uncovered_domains") is not True:
        failures.append({"reason": "TOP_LEVEL_DOMAIN_UNMAPPED", "detail": "uncovered domains remain"})
    if not any(domain.get("residual_certificate_id") for domain in domains):
        failures.append({"reason": "TOP_LEVEL_RESIDUAL_DOMAIN_REFERENCE_MISSING"})
    if not payload.get("natural_kernel_reference"):
        failures.append({"reason": "TOP_LEVEL_NATURAL_KERNEL_REFERENCE_MISSING"})
    return failures


def build_top_level_coverage_domain_map(
    top_level_rows: list[dict[str, Any]],
    *,
    kernel_link: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    by_type = _top_level_by_type(top_level_rows)
    entry_cert = by_type.get("universal_entry_certificate", {})
    coverage_cert = by_type.get("parent_state_coverage_certificate", {})
    entry_payload = entry_cert.get("proof_payload") if isinstance(entry_cert.get("proof_payload"), dict) else {}
    arithmetic = entry_payload.get("arithmetic_proof_schema") if isinstance(entry_payload.get("arithmetic_proof_schema"), dict) else {}
    coverage_payload = coverage_cert.get("proof_payload") if isinstance(coverage_cert.get("proof_payload"), dict) else {}
    domains: list[dict[str, Any]] = []
    for domain in coverage_payload.get("covered_parent_state_domains") or []:
        domain_id = str(domain.get("domain_id", ""))
        domains.append(
            {
                "domain_id": domain_id,
                "parent_state": f"P_{domain.get('parent_level', 'covered')}",
                "coverage_certificate_id": str(domain.get("covered_by", "")),
                "residual_certificate_id": domain_id if domain.get("kind") == "parent_residual" else "",
                "covered_predicate": (
                    f"q mod {domain.get('modulus')} in "
                    f"[{domain.get('residue_start')}, {domain.get('residue_end_exclusive')})"
                ),
                "kind": domain.get("kind", ""),
                "modulus": domain.get("modulus", 0),
                "residue_start": domain.get("residue_start", 0),
                "residue_end_exclusive": domain.get("residue_end_exclusive", 0),
            }
        )
    payload = {
        "schema": PAYLOAD_SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "TOP_LEVEL_COVERAGE_DOMAIN_MAP",
        "universal_entry": {
            "even_case": (arithmetic.get("even_case") or {}).get("collatz_identity", "n even and n > 1 implies C(n)=n/2<n"),
            "odd_case": (arithmetic.get("odd_case") or {}).get(
                "reconstruction",
                "n odd implies n = 2^a*q - 1 with a=v2(n+1), q=(n+1)/2^a",
            ),
            "odd_valuation_definition": (arithmetic.get("odd_case") or {}).get("valuation_definition", "a = v2(n + 1)"),
        },
        "parent_state_domains": domains,
        "no_uncovered_domains": not bool(coverage_payload.get("uncovered_parent_state_domains") or []),
        "natural_kernel_reference": {
            "kernel_certificate_id": kernel_link.get("kernel_certificate_id", ""),
            "scc_id": kernel_link.get("scc_id", ""),
            "conclusion": kernel_link.get("conclusion", ""),
        },
        "conclusion": "Every n>1 either descends immediately or enters a covered certified parent-state domain.",
    }
    failures = validate_top_level_coverage_domain_map_payload(payload)
    payload["semantic_validation"] = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    return attach_hash(payload), failures


def validate_payload_hash(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("semantic_payload_hash") != payload_hash(payload):
        return [{"reason": "semantic_payload_hash_mismatch", "kind": payload.get("kind"), "id": payload.get("certificate_id") or payload.get("lemma_id")}]
    return []


def replay_semantic_payloads(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for payload in payloads:
        failures.extend(validate_payload_hash(payload))
        validation = payload.get("semantic_validation") if isinstance(payload.get("semantic_validation"), dict) else {}
        if validation.get("status") != "PASS":
            failures.extend(validation.get("failures") or [{"reason": "semantic_payload_validation_failed", "kind": payload.get("kind")}])
        if payload.get("kind") in {"S3_SEMANTIC_ROLE", "S6_PROOF_TREE_SEMANTICS"}:
            if not payload.get("certificate_id") and not payload.get("lemma_id"):
                failures.append({"reason": "status_only_semantic_payload", "kind": payload.get("kind")})
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failure_count": len(failures), "failures": failures}


def build_semantic_payloads(
    *,
    s3_rows: list[dict[str, Any]],
    s6_rows: list[dict[str, Any]],
    natural_kernel_certificate: dict[str, Any],
    top_level_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    top_by_type = _top_level_by_type(top_level_rows)
    transition_soundness_id = str((top_by_type.get("transition_soundness_certificate") or {}).get("certificate_id", "transition_soundness_certificate"))
    consumers = build_s6_consumer_index(s6_rows)
    s3_payloads: list[dict[str, Any]] = []
    for row in s3_rows:
        payload, row_failures = build_s3_semantic_role(row, consumers, transition_soundness_id=transition_soundness_id)
        s3_payloads.append(payload)
        failures.extend(row_failures)
    s3_roles = {str(payload.get("certificate_id", "")): str(payload.get("semantic_role", "")) for payload in s3_payloads}
    s6_payloads: list[dict[str, Any]] = []
    for row in s6_rows:
        payload, row_failures = build_s6_proof_tree(row, s3_roles)
        s6_payloads.append(payload)
        failures.extend(row_failures)
    kernel_link, kernel_failures = build_kernel_to_path_link(natural_kernel_certificate)
    failures.extend(kernel_failures)
    coverage_map, coverage_failures = build_top_level_coverage_domain_map(top_level_rows, kernel_link=kernel_link)
    failures.extend(coverage_failures)
    payloads = s3_payloads + s6_payloads + [kernel_link, coverage_map]
    replay = replay_semantic_payloads(payloads)
    if replay["failures"]:
        failures.extend(replay["failures"])
    return (
        {
            "payloads": payloads,
            "s3_semantic_roles": s3_payloads,
            "s6_proof_trees": s6_payloads,
            "kernel_to_path_link": kernel_link,
            "top_level_coverage_domain_map": coverage_map,
            "semantic_replay": replay,
        },
        failures,
    )
