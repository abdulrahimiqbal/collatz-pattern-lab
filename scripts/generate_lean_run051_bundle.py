#!/usr/bin/env python3
"""Generate typed finite Lean bundle data for RUN-053."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
S3_ROLES_PATH = REPO_ROOT / "certificate_store/run051_s3_semantic_roles.jsonl"
S4_WITNESSES_PATH = REPO_ROOT / "certificate_store/run048_semantic_witnesses.jsonl"
S6_TREES_PATH = REPO_ROOT / "certificate_store/run051_s6_proof_trees.jsonl"
COVERAGE_MAP_PATH = REPO_ROOT / "certificate_store/run051_top_level_coverage_domain_map.json"
TOP_LEVEL_PATH = REPO_ROOT / "certificate_store/run046_top_level_certificates.jsonl"
KERNEL_LINK_PATH = REPO_ROOT / "certificate_store/run051_kernel_to_path_link.json"
OUT_PATH = REPO_ROOT / "formal/lean/Collatz/Run051Bundle.lean"
AUDIT_PATH = REPO_ROOT / "reports/runs/RUN-054-lean-transition-soundness-completion/edge_kind_audit.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def constructor(prefix: str, raw: str, used: set[str]) -> str:
    base = re.sub(r"[^A-Za-z0-9_]", "_", raw).lower().strip("_")
    if not base:
        base = "empty"
    if base[0].isdigit():
        base = f"{prefix}_{base}"
    else:
        base = f"{prefix}_{base}"
    name = base
    index = 1
    while name in used:
        index += 1
        name = f"{base}_{index}"
    used.add(name)
    return name


def lean_list(items: list[str], *, indent: str = "  ") -> str:
    if not items:
        return "[]"
    return "[\n" + indent + (",\n" + indent).join(items) + "\n]"


def nat(value: Any) -> int:
    return int(value or 0)


def bool_lit(value: Any) -> str:
    return "true" if bool(value) else "false"


def pnode(parent: Any) -> str:
    return f"P{int(parent)}"


def top_level_by_type(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("type", "")): row for row in rows}


def rank_map(top_rows: list[dict[str, Any]]) -> dict[str, int]:
    ranks: dict[str, int] = {}
    wf = top_level_by_type(top_rows).get("well_founded_ranking_certificate", {})
    payload = wf.get("proof_payload") if isinstance(wf.get("proof_payload"), dict) else {}
    ranking = payload.get("ranking") if isinstance(payload.get("ranking"), dict) else {}
    for edge in ranking.get("edge_checks") or []:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        if source:
            ranks[source] = int(edge.get("source_rank", ranks.get(source, 0)) or 0)
        if target:
            ranks[target] = int(edge.get("target_rank", ranks.get(target, 0)) or 0)
    return ranks


def cert_id_from_top(row: dict[str, Any]) -> str:
    return str(row.get("certificate_id") or row.get("type") or "")


def s4_witnesses(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    witnesses = [row for row in rows if row.get("kind") == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"]
    witnesses.sort(key=lambda row: str(row.get("certificate_id", "")))
    return witnesses


def generate(
    *,
    s3_roles_path: Path = S3_ROLES_PATH,
    s4_witnesses_path: Path = S4_WITNESSES_PATH,
    s6_trees_path: Path = S6_TREES_PATH,
    coverage_map_path: Path = COVERAGE_MAP_PATH,
    top_level_path: Path = TOP_LEVEL_PATH,
    kernel_link_path: Path = KERNEL_LINK_PATH,
    out_path: Path = OUT_PATH,
    audit_path: Path = AUDIT_PATH,
) -> None:
    s3_roles = sorted(read_jsonl(s3_roles_path), key=lambda row: str(row.get("certificate_id", "")))
    s4_rows = s4_witnesses(read_jsonl(s4_witnesses_path))
    s6_trees = sorted(read_jsonl(s6_trees_path), key=lambda row: str(row.get("lemma_id", "")))
    coverage_map = read_json(coverage_map_path)
    top_rows = read_jsonl(top_level_path)
    kernel_link = read_json(kernel_link_path)
    ranks = rank_map(top_rows)

    node_raw: set[str] = set()
    for row in s3_roles:
        node_raw.add(str(row.get("source_node", "")))
        node_raw.add(str(row.get("target_node", "")))
    for row in s4_rows:
        node_raw.add(pnode(row.get("source_parent", 0)))
        node_raw.add(pnode(row.get("target_parent", 0)))
    node_raw = {node for node in node_raw if node and node != "P0"}
    node_used: set[str] = set()
    node_ctor = {node: constructor("p", node.removeprefix("P"), node_used) for node in sorted(node_raw, key=lambda value: int(value.removeprefix("P")))}

    cert_raw: set[str] = set()
    for row in s3_roles:
        cert_raw.add(str(row.get("certificate_id", "")))
    for row in s4_rows:
        cert_raw.add(str(row.get("certificate_id", "")))
    for row in s6_trees:
        cert_raw.add(str(row.get("lemma_id", "")))
        for dep in row.get("dependencies") or []:
            cert_raw.add(str(dep.get("certificate_id", "")))
    for domain in coverage_map.get("parent_state_domains") or []:
        cert_raw.add(str(domain.get("domain_id", "")))
        cert_raw.add(str(domain.get("coverage_certificate_id", "")))
        cert_raw.add(str(domain.get("residual_certificate_id", "")))
    for row in top_rows:
        cert_raw.add(cert_id_from_top(row))
    cert_raw.add(str(kernel_link.get("kernel_certificate_id", "")))
    cert_raw = {cert for cert in cert_raw if cert}
    cert_used: set[str] = set()
    cert_ctor = {cert: constructor("c", cert, cert_used) for cert in sorted(cert_raw)}

    edges: list[dict[str, Any]] = []
    edge_raw: set[str] = set()
    for row in s3_roles:
        edge_id = f"s3_edge:{row.get('certificate_id')}"
        edge_raw.add(edge_id)
        edges.append({"edge_id": edge_id, "kind": "s3", "row": row})
    for row in s4_rows:
        edge_id = f"s4:{row.get('certificate_id')}"
        edge_raw.add(edge_id)
        edges.append({"edge_id": edge_id, "kind": "s4", "row": row})
    edge_used: set[str] = set()
    edge_ctor = {edge: constructor("e", edge, edge_used) for edge in sorted(edge_raw)}
    edges.sort(key=lambda item: edge_ctor[item["edge_id"]])
    transition_edge_raw = {item["edge_id"] for item in edges if item["kind"] == "s4"}
    support_edge_raw = {item["edge_id"] for item in edges if item["kind"] == "s3"}

    def node_ref(node: str) -> str:
        return f"NodeId.{node_ctor[node]}"

    def cert_ref(cert: str) -> str:
        return f"CertId.{cert_ctor[cert]}"

    def edge_ref(edge: str) -> str:
        return f"EdgeId.{edge_ctor[edge]}"

    edge_meta: dict[str, dict[str, Any]] = {}
    for item in edges:
        row = item["row"]
        if item["kind"] == "s3":
            source = str(row.get("source_node", ""))
            target = str(row.get("target_node", ""))
            edge_meta[item["edge_id"]] = {
                "cert_id": str(row.get("certificate_id", "")),
                "kind": "EdgeKind.s3Debt",
                "role": "EdgeRole.rankingSupportOnly",
                "audit_kind": "RANKING_SUPPORT_ONLY",
                "source": source,
                "target": target,
                "source_parent": int(source.removeprefix("P") or 0),
                "target_parent": int(target.removeprefix("P") or 0),
                "valuation": 0,
                "base_burst_division_exponent": 0,
                "standard_step_count": 0,
                "source_depth": 0,
                "source_residue": 0,
                "map_a": 0,
                "map_b": 0,
                "map_d": 0,
                "branch_c": 0,
                "gain_num": nat(row.get("gain_num")),
                "gain_den": nat(row.get("gain_den")),
                "has_iterate": False,
                "ranking_decrease": nat(row.get("gain_den")) > 0 and nat(row.get("gain_num")) < nat(row.get("gain_den")),
                "guarded_kernel": False,
            }
        else:
            source = pnode(row.get("source_parent", 0))
            target = pnode(row.get("target_parent", 0))
            source_rank = ranks.get(source, 0)
            target_rank = ranks.get(target, 0)
            parent_map = row.get("parent_coordinate_map") if isinstance(row.get("parent_coordinate_map"), dict) else {}
            branch_identity = row.get("branch_coordinate_identity") if isinstance(row.get("branch_coordinate_identity"), dict) else {}
            edge_meta[item["edge_id"]] = {
                "cert_id": str(row.get("certificate_id", "")),
                "kind": "EdgeKind.s4ParentTransition",
                "role": "EdgeRole.actualCollatzTransition",
                "audit_kind": "ACTUAL_COLLATZ_TRANSITION",
                "source": source,
                "target": target,
                "source_parent": nat(row.get("source_parent")),
                "target_parent": nat(row.get("target_parent")),
                "valuation": nat(row.get("valuation")),
                "base_burst_division_exponent": nat(row.get("base_burst_division_exponent")),
                "standard_step_count": nat(row.get("standard_step_count")),
                "source_depth": nat(row.get("source_depth")),
                "source_residue": nat(row.get("source_residue")),
                "map_a": nat(parent_map.get("A")),
                "map_b": nat(parent_map.get("B")),
                "map_d": nat(parent_map.get("D")),
                "branch_c": nat(branch_identity.get("c")),
                "gain_num": 0,
                "gain_den": 0,
                "has_iterate": True,
                "ranking_decrease": target_rank < source_rank,
                "guarded_kernel": not (target_rank < source_rank),
            }

    def match_def(name: str, type_sig: str, rows: list[tuple[str, str]]) -> str:
        return "\n".join([f"def {name} : {type_sig}"] + [f"  | {lhs} => {rhs}" for lhs, rhs in rows])

    edge_source_rows = [(edge_ref(edge), node_ref(meta["source"])) for edge, meta in sorted(edge_meta.items(), key=lambda item: edge_ctor[item[0]])]
    edge_target_rows = [(edge_ref(edge), node_ref(meta["target"])) for edge, meta in sorted(edge_meta.items(), key=lambda item: edge_ctor[item[0]])]
    edge_cert_rows: list[tuple[str, str]] = []
    for edge, meta in sorted(edge_meta.items(), key=lambda item: edge_ctor[item[0]]):
        body = "\n".join(
            [
                "{",
                f"    certId := {cert_ref(meta['cert_id'])},",
                f"    kind := {meta['kind']},",
                f"    role := {meta['role']},",
                f"    sourceNode := {node_ref(meta['source'])},",
                f"    targetNode := {node_ref(meta['target'])},",
                f"    sourceParent := {meta['source_parent']},",
                f"    targetParent := {meta['target_parent']},",
                f"    valuation := {meta['valuation']},",
                f"    baseBurstDivisionExponent := {meta['base_burst_division_exponent']},",
                f"    standardStepCount := {meta['standard_step_count']},",
                f"    sourceDepth := {meta['source_depth']},",
                f"    sourceResidue := {meta['source_residue']},",
                f"    mapA := {meta['map_a']},",
                f"    mapB := {meta['map_b']},",
                f"    mapD := {meta['map_d']},",
                f"    branchC := {meta['branch_c']},",
                f"    gainNum := {meta['gain_num']},",
                f"    gainDen := {meta['gain_den']},",
                f"    hasIterateWitness := {bool_lit(meta['has_iterate'])},",
                f"    rankingDecrease := {bool_lit(meta['ranking_decrease'])},",
                f"    guardedKernel := {bool_lit(meta['guarded_kernel'])}",
                "  }",
            ]
        )
        edge_cert_rows.append((edge_ref(edge), body))
    node_level_rows = [(node_ref(node), str(int(node.removeprefix("P")))) for node in sorted(node_raw, key=lambda value: int(value.removeprefix("P")))]
    rank_rows = [(node_ref(node), str(ranks.get(node, 0))) for node in sorted(node_raw, key=lambda value: int(value.removeprefix("P")))]

    s3_role_terms: list[str] = []
    for row in s3_roles:
        role = {
            "SUPPORTING_DEBT_EDGE": "S3SemanticRole.supportingDebtEdge",
            "RANKING_DECREASE": "S3SemanticRole.rankingDecrease",
            "DIRECT_DESCENT": "S3SemanticRole.directDescent",
            "EXIT_CERTIFICATE": "S3SemanticRole.exitCertificate",
        }.get(str(row.get("semantic_role")), "S3SemanticRole.supportingDebtEdge")
        s3_role_terms.append(
            "\n".join(
                [
                    "{",
                    f"  certId := {cert_ref(str(row.get('certificate_id', '')))},",
                    f"  role := {role},",
                    f"  sourceNode := {node_ref(str(row.get('source_node', '')))},",
                    f"  targetNode := {node_ref(str(row.get('target_node', '')))},",
                    f"  gainNum := {nat(row.get('gain_num'))},",
                    f"  gainDen := {nat(row.get('gain_den'))},",
                    f"  consumedByCount := {len(row.get('consumed_by') or [])}",
                    "}",
                ]
            )
        )

    claim_map = {
        "coverage": "S6ClaimKind.coverage",
        "no_escape": "S6ClaimKind.noEscape",
        "induction": "S6ClaimKind.induction",
        "ranking": "S6ClaimKind.ranking",
        "transition_composition": "S6ClaimKind.transitionComposition",
        "residual_parent": "S6ClaimKind.residualParent",
    }
    dep_map = {
        "S3_DEBT": "DependencyKind.s3Debt",
        "S4_PARENT_MAP": "DependencyKind.s4ParentMap",
        "RESIDUAL_PARENT": "DependencyKind.residualParent",
        "COVERAGE": "DependencyKind.coverage",
        "NO_ESCAPE": "DependencyKind.noEscape",
        "NATURAL_KERNEL": "DependencyKind.naturalKernel",
        "TOP_LEVEL": "DependencyKind.topLevel",
    }
    rule_map = {
        "compose_transition": "ProofRule.composeTransition",
        "apply_coverage": "ProofRule.applyCoverage",
        "apply_no_escape": "ProofRule.applyNoEscape",
        "apply_ranking": "ProofRule.applyRanking",
        "apply_induction": "ProofRule.applyInduction",
        "apply_residual_parent": "ProofRule.applyResidualParent",
    }
    s6_tree_terms: list[str] = []
    no_escape_terms: list[str] = []
    for row in s6_trees:
        claim = claim_map.get(str(row.get("semantic_claim_type")), "S6ClaimKind.transitionComposition")
        deps: list[str] = []
        for dep in row.get("dependencies") or []:
            deps.append(
                "\n".join(
                    [
                        "{",
                        f"  certId := {cert_ref(str(dep.get('certificate_id', '')))},",
                        f"  kind := {dep_map.get(str(dep.get('dependency_type')), 'DependencyKind.topLevel')},",
                        f"  claimKind := {claim}",
                        "}",
                    ]
                )
            )
        steps: list[str] = []
        for step in row.get("proof_steps") or []:
            steps.append(
                "\n".join(
                    [
                        "{",
                        f"  rule := {rule_map.get(str(step.get('rule')), 'ProofRule.composeTransition')},",
                        f"  inputCount := {len(step.get('inputs') or [])}",
                        "}",
                    ]
                )
            )
        term = "\n".join(
            [
                "{",
                f"  certId := {cert_ref(str(row.get('lemma_id', '')))},",
                f"  claimKind := {claim},",
                f"  dependencies := {lean_list(deps, indent='    ')},",
                f"  proofSteps := {lean_list(steps, indent='    ')},",
                f"  closesBlocker := {bool_lit(row.get('closes_blocker'))}",
                "}",
            ]
        )
        s6_tree_terms.append(term)
        if row.get("semantic_claim_type") == "no_escape":
            no_escape_terms.append(term)

    domain_terms: list[str] = []
    for domain in coverage_map.get("parent_state_domains") or []:
        cert = str(domain.get("residual_certificate_id") or domain.get("coverage_certificate_id") or domain.get("domain_id"))
        parent_level = int(domain.get("parent_level") or 0)
        domain_terms.append(
            "\n".join(
                [
                    "{",
                    f"  certId := {cert_ref(cert)},",
                    f"  modulus := {nat(domain.get('modulus'))},",
                    f"  residueStart := {nat(domain.get('residue_start'))},",
                    f"  residueEndExclusive := {nat(domain.get('residue_end_exclusive'))},",
                    f"  parentLevel := {parent_level},",
                    f"  isResidual := {bool_lit(domain.get('residual_certificate_id'))}",
                    "}",
                ]
            )
        )

    descent_cert = top_level_by_type(top_rows).get("descent_implication_certificate", {})
    descent_payload = descent_cert.get("proof_payload") if isinstance(descent_cert.get("proof_payload"), dict) else {}
    base_case = (descent_payload.get("strong_induction") or {}).get("base_case", {}) if isinstance(descent_payload.get("strong_induction"), dict) else {}

    body = "\n".join(
        [
            "import Collatz.ReflectionCheckers",
            "",
            "/-!",
            "Generated typed RUN-051 certified-system bundle for RUN-053.",
            "",
            "This file contains finite typed IDs and data-valued reflection",
            "fields only.  It does not turn Python replay status into a theorem.",
            "-/",
            "",
            "namespace Collatz",
            "",
            "inductive NodeId where",
            *[f"  | {node_ctor[node]}" for node in sorted(node_raw, key=lambda value: int(value.removeprefix('P')))],
            "deriving DecidableEq, Repr",
            "",
            "inductive EdgeId where",
            *[f"  | {edge_ctor[edge]}" for edge in sorted(edge_raw)],
            "deriving DecidableEq, Repr",
            "",
            "inductive CertId where",
            *[f"  | {cert_ctor[cert]}" for cert in sorted(cert_raw)],
            "deriving DecidableEq, Repr",
            "",
            "def run051NodeIds : List NodeId :=",
            lean_list([node_ref(node) for node in sorted(node_raw, key=lambda value: int(value.removeprefix("P")))]),
            "",
            "def run051EdgeIds : List EdgeId :=",
            lean_list([edge_ref(edge) for edge in sorted(edge_raw)]),
            "",
            "def run051TransitionEdgeIds : List EdgeId :=",
            lean_list([edge_ref(edge) for edge in sorted(transition_edge_raw)]),
            "",
            "def run051SupportEdgeIds : List EdgeId :=",
            lean_list([edge_ref(edge) for edge in sorted(support_edge_raw)]),
            "",
            "def run051CertIds : List CertId :=",
            lean_list([cert_ref(cert) for cert in sorted(cert_raw)]),
            "",
            match_def("run051EdgeSource", "EdgeId → NodeId", edge_source_rows),
            "",
            match_def("run051EdgeTarget", "EdgeId → NodeId", edge_target_rows),
            "",
            match_def("run051EdgeCert", "EdgeId → EdgeCert CertId NodeId", edge_cert_rows),
            "",
            match_def("run051NodeLevel", "NodeId → Nat", node_level_rows),
            "",
            match_def("run051NodeRank", "NodeId → Nat", rank_rows),
            "",
            "def run051S3RoleCerts : List (S3RoleCert CertId NodeId) :=",
            lean_list(s3_role_terms),
            "",
            "def run051S6ProofTreeCerts : List (S6ProofTreeCert CertId) :=",
            lean_list(s6_tree_terms),
            "",
            "def run051NoEscapeProofTreeCerts : List (S6ProofTreeCert CertId) :=",
            lean_list(no_escape_terms),
            "",
            "def run051CoverageCert : CoverageCert CertId :=",
            "{",
            f"  domains := {lean_list(domain_terms, indent='    ')},",
            f"  noUncoveredDomains := {bool_lit(coverage_map.get('no_uncovered_domains'))},",
            "  hasResidualDomain := true",
            "}",
            "",
            "def run051NoEscapeCert : NoEscapeCert CertId :=",
            "{",
            "  proofTrees := run051NoEscapeProofTreeCerts,",
            f"  noEscapeTreeCount := {len(no_escape_terms)}",
            "}",
            "",
            "def run051WellFoundedCert : WellFoundedCert CertId EdgeId :=",
            "{",
            "  rankedEdges := run051EdgeIds,",
            f"  guardedKernelCertId := {cert_ref(str(kernel_link.get('kernel_certificate_id', '')))},",
            "  unresolvedSccCount := run051TopLevelCerts.wellFoundedRanking.unresolvedSccCount",
            "}",
            "",
            "def run051DescentBridgeCert : DescentBridgeCert CertId :=",
            "{",
            f"  certId := {cert_ref(cert_id_from_top(descent_cert))},",
            f"  blockedByCount := {len(descent_payload.get('blocked_by') or [])},",
            f"  baseCaseN := {nat(base_case.get('n'))},",
            f"  baseCaseReachesOne := {bool_lit(base_case.get('reaches_one'))}",
            "}",
            "",
            "def run051Bundle : CertifiedSystemBundle NodeId EdgeId CertId :=",
            "{",
            "  nodes := run051NodeIds,",
            "  edges := run051TransitionEdgeIds,",
            "  supportEdges := run051SupportEdgeIds,",
            "  transitionEdges := run051TransitionEdgeIds,",
            "  certs := run051CertIds,",
            "  edgeSource := run051EdgeSource,",
            "  edgeTarget := run051EdgeTarget,",
            "  edgeCert := run051EdgeCert,",
            "  nodeLevel := run051NodeLevel,",
            "  nodeRank := run051NodeRank,",
            "  entryCert := run051TopLevelCerts.universalEntry,",
            "  coverageCert := run051CoverageCert,",
            "  transitionSoundnessCert := run051TopLevelCerts.transitionSoundness,",
            "  noEscapeCert := run051NoEscapeCert,",
            "  wellFoundedCert := run051WellFoundedCert,",
            "  descentImplicationCert := run051DescentBridgeCert,",
            "  s3Certs := run051S3DebtCerts,",
            "  s4Certs := run051S4ParentMapCerts,",
            "  s6Certs := run051S6LemmaCerts,",
            "  kernelCert := run051NaturalKernelCert,",
            "  s3Roles := run051S3RoleCerts,",
            "  s6ProofTrees := run051S6ProofTreeCerts",
            "}",
            "",
            f"theorem run051_node_count : run051Bundle.nodes.length = {len(node_raw)} := by native_decide",
            f"theorem run051_edge_count : run051Bundle.edges.length = {len(transition_edge_raw)} := by native_decide",
            f"theorem run051_support_edge_count : run051Bundle.supportEdges.length = {len(support_edge_raw)} := by native_decide",
            f"theorem run051_cert_count : run051Bundle.certs.length = {len(cert_raw)} := by native_decide",
            "",
            "end Collatz",
            "",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_rows = [
        {
            "edge_id": edge,
            "constructor": edge_ctor[edge],
            "certificate_id": meta["cert_id"],
            "source": meta["source"],
            "target": meta["target"],
            "edge_kind": meta["audit_kind"],
            "lean_kind": meta["kind"],
            "lean_role": meta["role"],
                "has_iterate_witness": meta["has_iterate"],
                "ranking_decrease": meta["ranking_decrease"],
                "guarded_kernel": meta["guarded_kernel"],
                "source_depth": meta["source_depth"],
                "source_residue": meta["source_residue"],
                "map_a": meta["map_a"],
                "map_b": meta["map_b"],
                "map_d": meta["map_d"],
                "branch_c": meta["branch_c"],
            }
        for edge, meta in sorted(edge_meta.items(), key=lambda item: edge_ctor[item[0]])
    ]
    audit = {
        "run_id": "RUN-054-lean-transition-soundness-completion",
        "edge_count": len(audit_rows),
        "actual_transition_edge_count": len(transition_edge_raw),
        "ranking_support_edge_count": len(support_edge_raw),
        "direct_descent_edge_count": 0,
        "coverage_only_edge_count": 0,
        "no_escape_only_edge_count": 0,
        "s6_proof_tree_only_count": len(s6_trees),
        "partitions": {
            "ACTUAL_COLLATZ_TRANSITION": len(transition_edge_raw),
            "DIRECT_DESCENT_EDGE": 0,
            "RANKING_SUPPORT_ONLY": len(support_edge_raw),
            "COVERAGE_ONLY": 0,
            "NO_ESCAPE_ONLY": 0,
            "S6_PROOF_TREE_ONLY": len(s6_trees),
        },
        "edges": audit_rows,
    }
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    parser.add_argument("--audit-out", type=Path, default=AUDIT_PATH)
    args = parser.parse_args(argv)
    generate(out_path=args.out, audit_path=args.audit_out)


if __name__ == "__main__":
    main()
