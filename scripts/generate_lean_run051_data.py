#!/usr/bin/env python3
"""Generate Lean data for RUN-051 semantic payload enrichment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
S3_ROLES_PATH = REPO_ROOT / "certificate_store/run051_s3_semantic_roles.jsonl"
S6_TREES_PATH = REPO_ROOT / "certificate_store/run051_s6_proof_trees.jsonl"
KERNEL_LINK_PATH = REPO_ROOT / "certificate_store/run051_kernel_to_path_link.json"
COVERAGE_MAP_PATH = REPO_ROOT / "certificate_store/run051_top_level_coverage_domain_map.json"
OUT_PATH = REPO_ROOT / "formal/lean/Collatz/Run051Data.lean"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _lean_string(value: Any) -> str:
    return json.dumps(str(value or ""), ensure_ascii=True)


def _nat(value: Any) -> str:
    return str(int(value or 0))


def _int(value: Any) -> str:
    return str(int(value or 0))


def _bool(value: Any) -> str:
    return "true" if bool(value) else "false"


def _lean_list(items: list[str], *, indent: str = "  ") -> str:
    if not items:
        return "[]"
    return "[\n" + indent + (",\n" + indent).join(items) + "\n]"


def _lean_s3_consumer(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"  consumerType := {_lean_string(row.get('consumer_type'))},",
            f"  consumerId := {_lean_string(row.get('consumer_id'))},",
            f"  dependencyType := {_lean_string(row.get('dependency_type'))}",
            "}",
        ]
    )


def _lean_s3_role(row: dict[str, Any]) -> str:
    consumers = row.get("consumed_by") if isinstance(row.get("consumed_by"), list) else []
    return "\n".join(
        [
            "{",
            f"  certificateId := {_lean_string(row.get('certificate_id'))},",
            f"  branchId := {_lean_string(row.get('branch_id'))},",
            f"  semanticRole := {_lean_string(row.get('semantic_role'))},",
            f"  sourceNode := {_lean_string(row.get('source_node'))},",
            f"  targetNode := {_lean_string(row.get('target_node'))},",
            f"  measureId := {_lean_string(row.get('measure_id'))},",
            f"  measureSourceExpr := {_lean_string(row.get('measure_source_expr'))},",
            f"  measureTargetExpr := {_lean_string(row.get('measure_target_expr'))},",
            f"  decreaseCertificateId := {_lean_string(row.get('decrease_certificate_id'))},",
            f"  decreaseInequality := {_lean_string(row.get('decrease_inequality'))},",
            f"  gainNum := {_nat(row.get('gain_num'))},",
            f"  gainDen := {_nat(row.get('gain_den'))},",
            f"  consumedBy := {_lean_list([_lean_s3_consumer(consumer) for consumer in consumers], indent='    ')},",
            f"  collatzIterateWitnessPresent := {_bool(bool(row.get('collatz_iterate_witness')))},",
            f"  semanticPayloadHash := {_lean_string(row.get('semantic_payload_hash'))}",
            "}",
        ]
    )


def _lean_s6_dependency(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"  dependencyType := {_lean_string(row.get('dependency_type'))},",
            f"  certificateId := {_lean_string(row.get('certificate_id'))},",
            f"  semanticRole := {_lean_string(row.get('semantic_role'))},",
            f"  usedFor := {_lean_string(row.get('used_for'))}",
            "}",
        ]
    )


def _lean_s6_step(row: dict[str, Any]) -> str:
    inputs = row.get("inputs") if isinstance(row.get("inputs"), list) else []
    return "\n".join(
        [
            "{",
            f"  stepId := {_lean_string(row.get('step_id'))},",
            f"  rule := {_lean_string(row.get('rule'))},",
            f"  inputCount := {_nat(len(inputs))},",
            f"  output := {_lean_string(row.get('output'))}",
            "}",
        ]
    )


def _lean_s6_tree(row: dict[str, Any]) -> str:
    dependencies = row.get("dependencies") if isinstance(row.get("dependencies"), list) else []
    proof_steps = row.get("proof_steps") if isinstance(row.get("proof_steps"), list) else []
    return "\n".join(
        [
            "{",
            f"  lemmaId := {_lean_string(row.get('lemma_id'))},",
            f"  blockerId := {_lean_string(row.get('blocker_id'))},",
            f"  semanticClaimType := {_lean_string(row.get('semantic_claim_type'))},",
            f"  conclusion := {_lean_string(row.get('conclusion'))},",
            f"  dependencies := {_lean_list([_lean_s6_dependency(dep) for dep in dependencies], indent='    ')},",
            f"  proofSteps := {_lean_list([_lean_s6_step(step) for step in proof_steps], indent='    ')},",
            f"  closesBlocker := {_bool(row.get('closes_blocker'))},",
            f"  semanticPayloadHash := {_lean_string(row.get('semantic_payload_hash'))}",
            "}",
        ]
    )


def _lean_kernel_link(row: dict[str, Any]) -> str:
    fixed = row.get("kernel_fixed_point") if isinstance(row.get("kernel_fixed_point"), dict) else {}
    divisibility = row.get("divisibility_family") if isinstance(row.get("divisibility_family"), dict) else {}
    no_nat = row.get("no_nat_in_kernel") if isinstance(row.get("no_nat_in_kernel"), dict) else {}
    return "\n".join(
        [
            "{",
            f"  kernelCertificateId := {_lean_string(row.get('kernel_certificate_id'))},",
            f"  sccId := {_lean_string(row.get('scc_id'))},",
            f"  statement := {_lean_string(row.get('statement'))},",
            "  fixedPoint := {",
            f"    numerator := {_int(fixed.get('numerator'))},",
            f"    denominator := {_nat(fixed.get('denominator'))}",
            "  },",
            "  divisibilityFamily := {",
            f"    statement := {_lean_string(divisibility.get('statement'))},",
            f"    source := {_lean_string(divisibility.get('source'))},",
            f"    distanceForm := {_lean_string(divisibility.get('distance_form'))},",
            f"    repeatForcesDivisibilityBy := {_lean_string(divisibility.get('repeat_forces_divisibility_by'))},",
            f"    kernelCongruenceDepthUnbounded := {_bool(divisibility.get('kernel_congruence_depth_unbounded'))}",
            "  },",
            f"  noNatReason := {_lean_string(no_nat.get('reason'))},",
            f"  noPositiveIntegerQInKernel := {_bool(no_nat.get('therefore_no_positive_integer_q_in_kernel'))},",
            f"  conclusion := {_lean_string(row.get('conclusion'))},",
            f"  semanticPayloadHash := {_lean_string(row.get('semantic_payload_hash'))}",
            "}",
        ]
    )


def _lean_coverage_domain(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"  domainId := {_lean_string(row.get('domain_id'))},",
            f"  parentState := {_lean_string(row.get('parent_state'))},",
            f"  coverageCertificateId := {_lean_string(row.get('coverage_certificate_id'))},",
            f"  residualCertificateId := {_lean_string(row.get('residual_certificate_id'))},",
            f"  coveredPredicate := {_lean_string(row.get('covered_predicate'))},",
            f"  kind := {_lean_string(row.get('kind'))},",
            f"  modulus := {_nat(row.get('modulus'))},",
            f"  residueStart := {_nat(row.get('residue_start'))},",
            f"  residueEndExclusive := {_nat(row.get('residue_end_exclusive'))}",
            "}",
        ]
    )


def _lean_coverage_map(row: dict[str, Any]) -> str:
    entry = row.get("universal_entry") if isinstance(row.get("universal_entry"), dict) else {}
    domains = row.get("parent_state_domains") if isinstance(row.get("parent_state_domains"), list) else []
    kernel = row.get("natural_kernel_reference") if isinstance(row.get("natural_kernel_reference"), dict) else {}
    return "\n".join(
        [
            "{",
            f"  evenCase := {_lean_string(entry.get('even_case'))},",
            f"  oddCase := {_lean_string(entry.get('odd_case'))},",
            f"  oddValuationDefinition := {_lean_string(entry.get('odd_valuation_definition'))},",
            f"  parentStateDomains := {_lean_list([_lean_coverage_domain(domain) for domain in domains], indent='    ')},",
            f"  noUncoveredDomains := {_bool(row.get('no_uncovered_domains'))},",
            "  naturalKernelReference := {",
            f"    kernelCertificateId := {_lean_string(kernel.get('kernel_certificate_id'))},",
            f"    sccId := {_lean_string(kernel.get('scc_id'))},",
            f"    conclusion := {_lean_string(kernel.get('conclusion'))}",
            "  },",
            f"  conclusion := {_lean_string(row.get('conclusion'))},",
            f"  semanticPayloadHash := {_lean_string(row.get('semantic_payload_hash'))}",
            "}",
        ]
    )


def generate(
    *,
    s3_roles_path: Path = S3_ROLES_PATH,
    s6_trees_path: Path = S6_TREES_PATH,
    kernel_link_path: Path = KERNEL_LINK_PATH,
    coverage_map_path: Path = COVERAGE_MAP_PATH,
    out_path: Path = OUT_PATH,
) -> None:
    s3_roles = sorted(_read_jsonl(s3_roles_path), key=lambda row: str(row.get("certificate_id", "")))
    s6_trees = sorted(_read_jsonl(s6_trees_path), key=lambda row: str(row.get("lemma_id", "")))
    kernel_link = _read_json(kernel_link_path)
    coverage_map = _read_json(coverage_map_path)
    body = "\n".join(
        [
            "import Collatz.Run048Data",
            "",
            "/-!",
            "Generated RUN-051 semantic payload data.",
            "",
            "This file contains literal payload fields only.  The checks below",
            "inspect those fields in Lean; they are not Python PASS theorems.",
            "-/",
            "",
            "namespace Collatz",
            "",
            "def run051S3DebtCerts : List S3DebtExactCert := run046S3DebtCerts",
            "def run051S4ParentMapCerts : List S4ParentMapCert := run046S4ParentMapCerts",
            "def run051S6LemmaCerts : List S6LemmaCert := run046S6LemmaCerts",
            "def run051NaturalKernelCert : NaturalViabilityKernelCert := run046NaturalKernelCert",
            "def run051TopLevelCerts : TopLevelCertBundle := run046TopLevelCerts",
            "def run051S4SemanticWitnesses : List S4ParentTransitionSemanticWitness := run048S4SemanticWitnesses",
            "",
            "def run051S3SemanticRoles : List S3SemanticRolePayload :=",
            _lean_list([_lean_s3_role(row) for row in s3_roles]),
            "",
            "def run051S6ProofTrees : List S6ProofTreePayload :=",
            _lean_list([_lean_s6_tree(row) for row in s6_trees]),
            "",
            "def run051KernelToPathLink : NaturalKernelToPathLinkPayload :=",
            _lean_kernel_link(kernel_link),
            "",
            "def run051TopLevelCoverageDomainMap : TopLevelCoverageDomainMapPayload :=",
            _lean_coverage_map(coverage_map),
            "",
            f"theorem run051_s3_semantic_role_count : run051S3SemanticRoles.length = {len(s3_roles)} := by",
            "  native_decide",
            "",
            f"theorem run051_s6_proof_tree_count : run051S6ProofTrees.length = {len(s6_trees)} := by",
            "  native_decide",
            "",
            "theorem run051_s3_semantic_roles_valid :",
            "    (∀ payload ∈ run051S3SemanticRoles, payload.Valid) := by",
            "  native_decide",
            "",
            "theorem run051_s6_proof_trees_valid :",
            "    (∀ payload ∈ run051S6ProofTrees, payload.Valid) := by",
            "  native_decide",
            "",
            "theorem run051_kernel_to_path_link_valid :",
            "    run051KernelToPathLink.Valid := by",
            "  native_decide",
            "",
            "theorem run051_top_level_coverage_domain_map_valid :",
            "    run051TopLevelCoverageDomainMap.Valid := by",
            "  native_decide",
            "",
            "end Collatz",
            "",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--s3-roles", type=Path, default=S3_ROLES_PATH)
    parser.add_argument("--s6-trees", type=Path, default=S6_TREES_PATH)
    parser.add_argument("--kernel-link", type=Path, default=KERNEL_LINK_PATH)
    parser.add_argument("--coverage-map", type=Path, default=COVERAGE_MAP_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args(argv)
    generate(
        s3_roles_path=args.s3_roles,
        s6_trees_path=args.s6_trees,
        kernel_link_path=args.kernel_link,
        coverage_map_path=args.coverage_map,
        out_path=args.out,
    )


if __name__ == "__main__":
    main()
