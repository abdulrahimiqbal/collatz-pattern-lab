#!/usr/bin/env python3
"""Generate literal Lean data from the final RUN-046 certificate artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
S3_CERTS_PATH = REPO_ROOT / "certificate_store/run046_s3_debt_certificates.jsonl"
S4_CERTS_PATH = REPO_ROOT / "certificate_store/run046_parent_transition_certificates.jsonl"
S6_CERTS_PATH = REPO_ROOT / "certificate_store/run046_s6_lemma_certificates.jsonl"
NATURAL_KERNEL_PATH = REPO_ROOT / "certificate_store/run045_natural_viability_kernel_certificate.json"
TOP_LEVEL_CERTS_PATH = REPO_ROOT / "certificate_store/run046_top_level_certificates.jsonl"
FINAL_PROOF_PATH = REPO_ROOT / "certificate_store/run046_final_proof_object.json"
OUT_PATH = REPO_ROOT / "formal/lean/Collatz/Run046Data.lean"


def _lean_string(value: Any) -> str:
    return json.dumps(str(value or ""), ensure_ascii=True)


def _nat(value: Any) -> str:
    return str(int(value or 0))


def _int(value: Any) -> str:
    return str(int(value or 0))


def _bool(value: Any) -> str:
    return "true" if bool(value) else "false"


def _pass(value: Any) -> str:
    return "true" if value is True or value == "PASS" or value == "ACCEPT" else "false"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _list(items: list[str], *, indent: str = "") -> str:
    if not items:
        return "[]"
    return "[\n" + indent + (",\n" + indent).join(items) + "\n]"


def _lean_string_list(items: list[str]) -> str:
    return "[" + ", ".join(_lean_string(item) for item in items) + "]"


def _extract_s3_exact_certs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    certs = [row["s3_debt_certificate"] for row in rows if isinstance(row.get("s3_debt_certificate"), dict)]
    certs.sort(key=lambda row: str(row.get("node_id", "")))
    return certs


def _lean_s3_exact_congruence(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"    typeName := {_lean_string(cert.get('type'))},",
            f"    branchId := {_lean_string(cert.get('branch_id'))},",
            f"    sourceParent := {_nat(cert.get('source_parent'))},",
            f"    targetParent := {_nat(cert.get('target_parent'))},",
            f"    valuation := {_nat(cert.get('valuation'))},",
            f"    branchResidue := {_nat(cert.get('branch_residue'))},",
            f"    branchDepth := {_nat(cert.get('branch_depth'))},",
            f"    sourceModulus := {_nat(cert.get('source_modulus'))},",
            f"    theoremName := {_lean_string(cert.get('theorem'))},",
            f"    statement := {_lean_string(cert.get('statement'))}",
            "  }",
        ]
    )


def _lean_s3_measure(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"    typeName := {_lean_string(cert.get('type'))},",
            f"    measureId := {_lean_string(cert.get('measure_id'))},",
            f"    branchId := {_lean_string(cert.get('branch_id'))},",
            f"    sourceParent := {_nat(cert.get('source_parent'))},",
            f"    targetParent := {_nat(cert.get('target_parent'))},",
            f"    valuation := {_nat(cert.get('valuation'))},",
            f"    gainNum := {_nat(cert.get('gain_num'))},",
            f"    gainDen := {_nat(cert.get('gain_den'))},",
            f"    decreaseInequality := {_lean_string(cert.get('decrease_inequality'))}",
            "  }",
        ]
    )


def _lean_s3_local_descent(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"    typeName := {_lean_string(cert.get('type'))},",
            f"    branchId := {_lean_string(cert.get('branch_id'))},",
            f"    gainNum := {_nat(cert.get('gain_num'))},",
            f"    gainDen := {_nat(cert.get('gain_den'))},",
            f"    rule := {_lean_string(cert.get('rule'))}",
            "  }",
        ]
    )


def _lean_s3_exact_cert(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"  nodeId := {_lean_string(cert.get('node_id'))},",
            f"  branchId := {_lean_string(cert.get('branch_id'))},",
            f"  sourceParent := {_nat(cert.get('source_parent'))},",
            f"  targetParent := {_nat(cert.get('target_parent'))},",
            f"  valuation := {_nat(cert.get('valuation'))},",
            f"  gainNum := {_nat(cert.get('gain_num'))},",
            f"  gainDen := {_nat(cert.get('gain_den'))},",
            "  exactCongruenceCertificate :=",
            _lean_s3_exact_congruence(cert.get("exact_congruence_certificate") or {}) + ",",
            "  debtMeasureDefinition :=",
            _lean_s3_measure(cert.get("debt_measure_definition") or {}) + ",",
            "  localDescentCertificate :=",
            _lean_s3_local_descent(cert.get("local_descent_certificate") or {}) + ",",
            f"  certificateHash := {_lean_string(cert.get('certificate_hash'))}",
            "}",
        ]
    )


def _extract_s4_parent_map_certs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    certs = [row["transition_certificate"] for row in rows if isinstance(row.get("transition_certificate"), dict)]
    certs.sort(key=lambda row: str(row.get("transition_id", "")))
    return certs


def _lean_s4_cert(cert: dict[str, Any]) -> str:
    div = cert.get("divisibility_certificate") or {}
    cong = cert.get("congruence_certificate") or {}
    mem = cert.get("target_membership_certificate") or {}
    pmap = cert.get("parent_coordinate_map") or {}
    replay = cert.get("replay_checks") or {}
    return "\n".join(
        [
            "{",
            f"  transitionId := {_lean_string(cert.get('transition_id'))},",
            f"  branchId := {_lean_string(cert.get('branch_id'))},",
            f"  sourceParent := {_nat(cert.get('source_parent'))},",
            f"  targetParent := {_nat(cert.get('target_parent'))},",
            f"  valuation := {_nat(cert.get('valuation'))},",
            f"  c := {_nat(div.get('c'))},",
            f"  coefficient := {_nat(div.get('coefficient'))},",
            f"  divValuation := {_nat(div.get('valuation'))},",
            f"  kDivisibilityModulus := {_nat(div.get('k_divisibility_modulus'))},",
            f"  kDivisibilityResidue := {_nat(div.get('k_divisibility_residue'))},",
            f"  excludedNextPowerModulus := {_nat(div.get('excluded_next_power_modulus'))},",
            f"  excludedNextPowerResidue := {_nat(div.get('excluded_next_power_residue'))},",
            f"  oddModulus := {_nat(cong.get('odd_modulus'))},",
            f"  inversePowerTwoMod3a := {_nat(cong.get('inverse_power_two_mod_3a'))},",
            f"  targetOddResidueMod3a := {_nat(cong.get('target_odd_residue_mod_3a'))},",
            f"  parentFloor := {_nat(mem.get('parent_floor'))},",
            f"  membershipTargetParent := {_nat(mem.get('target_parent'))},",
            f"  certificateHash := {_lean_string(cert.get('certificate_hash'))},",
            "  hasParentMapPayload := true,",
            f"  mapA := {_nat(pmap.get('A'))},",
            f"  mapB := {_nat(pmap.get('B'))},",
            f"  mapD := {_nat(pmap.get('D'))},",
            f"  baseBurstDivisionExponent := {_nat(pmap.get('base_burst_division_exponent'))},",
            f"  domainModulus := {_nat(pmap.get('domain_modulus'))},",
            f"  domainResidue := {_nat(pmap.get('domain_residue'))},",
            f"  minimumQ := {_nat(pmap.get('minimum_q'))},",
            f"  sourceDepth := {_nat(pmap.get('source_depth'))},",
            f"  sourceResidue := {_nat(pmap.get('source_residue'))},",
            f"  parentCoordinateMapCertificateHash := {_lean_string(cert.get('parent_coordinate_map_certificate_hash'))},",
            f"  parentCoordinateMapCertificateId := {_lean_string(cert.get('parent_coordinate_map_certificate_id'))},",
            f"  parentCoordinateMapReplays := {_bool(replay.get('parent_coordinate_map_replays'))},",
            f"  parentCoordinateIntegralityProven := {_bool(replay.get('parent_coordinate_integrality_proven'))},",
            f"  parentCoordinatePositivityProven := {_bool(replay.get('parent_coordinate_positivity_proven'))}",
            "}",
        ]
    )


def _extract_s6_certs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    certs = [row["s6_lemma_certificate"] for row in rows if isinstance(row.get("s6_lemma_certificate"), dict)]
    certs.sort(key=lambda row: str(row.get("lemma_id", "")))
    return certs


def _lean_s6_cert(cert: dict[str, Any]) -> str:
    payload = cert.get("proof_payload") or {}
    replay = cert.get("replay_checks") or {}
    depends = [str(item) for item in payload.get("depends_on", [])]
    return "\n".join(
        [
            "{",
            f"  certificateId := {_lean_string(cert.get('certificate_id'))},",
            f"  lemmaId := {_lean_string(cert.get('lemma_id'))},",
            f"  blockerId := {_lean_string(cert.get('blocker_id'))},",
            f"  blockerType := {_lean_string(cert.get('blocker_type'))},",
            f"  dependencyIds := {_lean_string_list(depends)},",
            f"  certificateHash := {_lean_string(cert.get('certificate_hash'))},",
            "  hasExactPayload := true,",
            f"  dependencyHashCount := {_nat(len(payload.get('dependency_hashes') or {}))},",
            f"  dependencyReplayPayloadCount := {_nat(len(payload.get('dependency_replay_payloads') or {}))},",
            f"  coverageCertificateCount := {_nat(len(payload.get('coverage_certificate_ids') or []))},",
            f"  noEscapeCertificateCount := {_nat(len(payload.get('no_escape_certificate_ids') or []))},",
            f"  rankingOrInductionCertificateCount := {_nat(len(payload.get('ranking_or_induction_certificate_ids') or []))},",
            f"  residualParentCertificateCount := {_nat(len(payload.get('residual_parent_certificate_ids') or []))},",
            f"  s3DebtExactCertificateCount := {_nat(len(payload.get('s3_debt_exact_certificate_ids') or []))},",
            f"  s4ParentTransitionCertificateCount := {_nat(len(payload.get('s4_parent_transition_certificate_ids') or []))},",
            f"  allDependenciesPresent := {_bool(replay.get('all_dependencies_present'))},",
            f"  allDependenciesHashMatch := {_bool(replay.get('all_dependencies_hash_match'))},",
            f"  allDependenciesReplayPass := {_bool(replay.get('all_dependencies_replay_pass'))},",
            f"  closesTargetBlocker := {_bool(replay.get('closes_target_blocker'))},",
            f"  statementMatchesBlocker := {_bool(replay.get('statement_matches_blocker'))},",
            f"  status := {_pass(cert.get('status'))}",
            "}",
        ]
    )


def _lean_natural_kernel_cert(cert: dict[str, Any]) -> str:
    fixed = cert.get("fixed_point") or {}
    proof = cert.get("proof") or {}
    cmap = cert.get("composed_map") or {}
    return "\n".join(
        [
            "{",
            f"  numerator := {_int(fixed.get('numerator'))},",
            f"  denominator := {_nat(fixed.get('denominator'))},",
            f"  denominatorOdd := {_bool(proof.get('denominator_is_odd'))},",
            f"  numeratorNegative := {_bool(int(fixed.get('numerator') or 0) < 0)},",
            f"  status := {_pass(cert.get('status'))},",
            f"  mapA := {_nat(cmap.get('A'))},",
            f"  mapB := {_nat(cmap.get('B'))},",
            f"  mapD := {_nat(cmap.get('D'))},",
            f"  lassoDepth := {_nat(proof.get('lasso_2adic_depth_gain_per_repeat'))},",
            f"  fixedPointEquation := {_bool(proof.get('fixed_point_equation'))},",
            f"  lassoDenominatorIsPowerOfTwo := {_bool(proof.get('lasso_denominator_is_power_of_two'))},",
            f"  lassoMultiplierIsOdd := {_bool(proof.get('lasso_multiplier_is_odd'))},",
            f"  kernelCongruenceDepthUnbounded := {_bool(proof.get('kernel_congruence_depth_unbounded'))},",
            f"  anyNaturalQHasFiniteDistance := {_bool(proof.get('any_natural_q_has_finite_2adic_distance_from_fixed_point'))},",
            f"  thereforeNoPositiveIntegerQInKernel := {_bool(proof.get('therefore_no_positive_integer_q_in_kernel'))},",
            f"  certificateHash := {_lean_string(cert.get('certificate_hash'))}",
            "}",
        ]
    )


def _lean_domain(domain: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"  domainId := {_lean_string(domain.get('domain_id'))},",
            f"  kind := {_lean_string(domain.get('kind'))},",
            f"  modulus := {_nat(domain.get('modulus'))},",
            f"  residueStart := {_nat(domain.get('residue_start'))},",
            f"  residueEndExclusive := {_nat(domain.get('residue_end_exclusive'))},",
            f"  parentLevel := {_nat(domain.get('parent_level'))}",
            "}",
        ]
    )


def _lean_residual(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"    certificateId := {_lean_string(cert.get('certificate_id'))},",
            f"    parentLevel := {_nat(cert.get('parent_level'))},",
            f"    modulus := {_nat(cert.get('modulus'))},",
            f"    residualStart := {_nat(cert.get('residual_start'))},",
            f"    residualEnd := {_nat(cert.get('residual_end'))},",
            f"    pathNodeCount := {_nat(cert.get('path_node_count'))},",
            f"    rankingDeltaNum := {_nat(cert.get('ranking_delta_num'))},",
            f"    rankingDeltaDen := {_nat(cert.get('ranking_delta_den'))},",
            f"    certificateHash := {_lean_string(cert.get('certificate_hash'))}",
            "  }",
        ]
    )


def _lean_edge_check(edge: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"  edgeId := {_lean_string(edge.get('edge_id'))},",
            f"  source := {_lean_string(edge.get('source'))},",
            f"  target := {_lean_string(edge.get('target'))},",
            f"  sourceRank := {_nat(edge.get('source_rank'))},",
            f"  targetRank := {_nat(edge.get('target_rank'))},",
            f"  decreases := {_bool(edge.get('decreases'))}",
            "}",
        ]
    )


def _lean_scc_check(check: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"  sccId := {_lean_string(check.get('scc_id'))},",
            f"  proofKind := {_lean_string(check.get('proof_kind'))},",
            f"  status := {_pass(check.get('status'))},",
            f"  coveredEdgeCount := {_nat(check.get('covered_edge_count'))}",
            "}",
        ]
    )


def _top_level_bundle(top_rows: list[dict[str, Any]], proof: dict[str, Any]) -> str:
    certs = {str(row.get("type")): row for row in top_rows}
    universal = certs.get("universal_entry_certificate", {})
    coverage = certs.get("parent_state_coverage_certificate", {})
    transition = certs.get("transition_soundness_certificate", {})
    ranking = certs.get("well_founded_ranking_certificate", {})
    descent = certs.get("descent_implication_certificate", {})

    up = universal.get("proof_payload") or {}
    arith = up.get("arithmetic_proof_schema") or {}
    even = ((arith.get("even_case") or {}).get("replay_checks") or {})
    odd = ((arith.get("odd_case") or {}).get("replay_checks") or {})

    cp = coverage.get("proof_payload") or {}
    lower = cp.get("lower_layer_replay") or {}
    expected = lower.get("expected") or {}
    passed = lower.get("passed") or {}
    required_domains = [_lean_domain(item) for item in cp.get("required_parent_state_domains") or []]
    covered_domains = [_lean_domain(item) for item in cp.get("covered_parent_state_domains") or []]

    tp = transition.get("proof_payload") or {}
    counts = tp.get("expected_counts") or {}

    rp = (ranking.get("proof_payload") or {}).get("ranking") or {}
    edge_checks = [_lean_edge_check(item) for item in rp.get("edge_checks") or []]
    scc_checks = [_lean_scc_check(item) for item in rp.get("scc_checks") or []]

    dp = descent.get("proof_payload") or {}
    bridge = dp.get("parent_state_bridge") or {}
    base = ((dp.get("strong_induction") or {}).get("base_case") or {})
    graph_count = int(((proof.get("coverage") or {}).get("proof_graph_node_count")) or 0)

    return "\n".join(
        [
            "{",
            f"  universalEntryHash := {_lean_string(universal.get('certificate_hash'))},",
            f"  parentStateCoverageHash := {_lean_string(coverage.get('certificate_hash'))},",
            f"  transitionSoundnessHash := {_lean_string(transition.get('certificate_hash'))},",
            f"  wellFoundedRankingHash := {_lean_string(ranking.get('certificate_hash'))},",
            f"  descentImplicationHash := {_lean_string(descent.get('certificate_hash'))},",
            f"  theoremStatement := {_lean_string(dp.get('descent_theorem') or proof.get('theorem'))},",
            f"  descentImplicationStatement := {_lean_string(dp.get('collatz_conjecture') or proof.get('descent_implication'))},",
            f"  acceptedNodeCount := {graph_count},",
            f"  totalNodeCount := {graph_count},",
            "  openNodeCount := 0,",
            "  universalEntry :=",
            "  {",
            f"    certificateId := {_lean_string(universal.get('certificate_id'))},",
            f"    certificateHash := {_lean_string(universal.get('certificate_hash'))},",
            f"    certificateType := {_lean_string(universal.get('certificate_type'))},",
            f"    theoremStatement := {_lean_string(up.get('theorem'))},",
            f"    replayStatus := {_pass(universal.get('replay_status'))},",
            f"    strictReplay := {_bool(universal.get('strict_replay'))},",
            f"    status := {_pass(universal.get('status'))},",
            f"    evenDenominatorPositive := {_bool(even.get('denominator_positive'))},",
            f"    evenStrictDescentForKGeOne := {_bool(even.get('strict_descent_for_k_ge_1'))},",
            f"    oddExactReconstruction := {_bool(odd.get('exact_reconstruction'))},",
            f"    oddNPlusOnePositive := {_bool(odd.get('n_plus_one_positive'))},",
            f"    oddQuotientAfterV2 := {_bool(odd.get('odd_quotient_after_v2'))},",
            f"    oddPowerTwoDivides := {_bool(odd.get('power_two_divides_n_plus_one'))}",
            "  },",
            "  parentStateCoverage :=",
            "  {",
            f"    certificateId := {_lean_string(coverage.get('certificate_id'))},",
            f"    certificateHash := {_lean_string(coverage.get('certificate_hash'))},",
            f"    certificateType := {_lean_string(coverage.get('certificate_type'))},",
            f"    replayStatus := {_pass(coverage.get('replay_status'))},",
            f"    strictReplay := {_bool(coverage.get('strict_replay'))},",
            f"    status := {_pass(coverage.get('status'))},",
            f"    requiredDomains := {_list(required_domains, indent='      ')},",
            f"    coveredDomains := {_list(covered_domains, indent='      ')},",
            f"    uncoveredDomainCount := {_nat(len(cp.get('uncovered_parent_state_domains') or []))},",
            f"    lowerExpectedS3 := {_nat(expected.get('s3'))},",
            f"    lowerExpectedS4 := {_nat(expected.get('s4'))},",
            f"    lowerExpectedS6 := {_nat(expected.get('s6'))},",
            f"    lowerPassedS3 := {_nat(passed.get('s3'))},",
            f"    lowerPassedS4 := {_nat(passed.get('s4'))},",
            f"    lowerPassedS6 := {_nat(passed.get('s6'))},",
            f"    lowerLayerStatus := {_pass(lower.get('status'))},",
            "    parentResidual :=",
            _lean_residual(cp.get("parent_residual_certificate") or {}),
            "  },",
            "  transitionSoundness :=",
            "  {",
            f"    certificateId := {_lean_string(transition.get('certificate_id'))},",
            f"    certificateHash := {_lean_string(transition.get('certificate_hash'))},",
            f"    certificateType := {_lean_string(transition.get('certificate_type'))},",
            f"    replayStatus := {_pass(transition.get('replay_status'))},",
            f"    strictReplay := {_bool(transition.get('strict_replay'))},",
            f"    status := {_pass(transition.get('status'))},",
            f"    expectedS3 := {_nat(counts.get('s3'))},",
            f"    expectedS4 := {_nat(counts.get('s4'))},",
            f"    expectedS6 := {_nat(counts.get('s6'))},",
            f"    s3ExactCertificateCount := {_nat(tp.get('s3_exact_certificate_count'))},",
            f"    s3ExactReplayPass := {_nat(tp.get('s3_exact_replay_pass'))},",
            f"    s4ExactCertificateCount := {_nat(tp.get('s4_exact_certificate_count'))},",
            f"    s4ExactReplayPass := {_nat(tp.get('s4_exact_replay_pass'))},",
            f"    s6ExactCertificateCount := {_nat(tp.get('s6_exact_certificate_count'))},",
            f"    s6ExactReplayPass := {_nat(tp.get('s6_exact_replay_pass'))},",
            f"    failureCount := {_nat(len(tp.get('failures') or []))}",
            "  },",
            "  wellFoundedRanking :=",
            "  {",
            f"    certificateId := {_lean_string(ranking.get('certificate_id'))},",
            f"    certificateHash := {_lean_string(ranking.get('certificate_hash'))},",
            f"    certificateType := {_lean_string(ranking.get('certificate_type'))},",
            f"    replayStatus := {_pass(ranking.get('replay_status'))},",
            f"    strictReplay := {_bool(ranking.get('strict_replay'))},",
            f"    status := {_pass(ranking.get('status'))},",
            f"    domain := {_lean_string(rp.get('domain'))},",
            f"    wellFoundedOrder := {_lean_string(rp.get('well_founded_order'))},",
            f"    nonterminalEdgeCount := {_nat(rp.get('nonterminal_edge_count'))},",
            f"    terminalEdgeCount := {_nat(rp.get('terminal_edge_count'))},",
            f"    transitionEdgeCount := {_nat(len(rp.get('transition_edges') or []))},",
            f"    nondecreasingEdgeCount := {_nat(len(rp.get('nondecreasing_edges') or []))},",
            f"    unresolvedSccCount := {_nat(len(rp.get('unresolved_sccs') or []))},",
            f"    edgeChecks := {_list(edge_checks, indent='      ')},",
            f"    sccChecks := {_list(scc_checks, indent='      ')}",
            "  },",
            "  descentImplication :=",
            "  {",
            f"    certificateId := {_lean_string(descent.get('certificate_id'))},",
            f"    certificateHash := {_lean_string(descent.get('certificate_hash'))},",
            f"    certificateType := {_lean_string(descent.get('certificate_type'))},",
            f"    replayStatus := {_pass(descent.get('replay_status'))},",
            f"    strictReplay := {_bool(descent.get('strict_replay'))},",
            f"    status := {_pass(descent.get('status'))},",
            f"    descentTheoremStatement := {_lean_string(dp.get('descent_theorem'))},",
            f"    collatzConjectureStatement := {_lean_string(dp.get('collatz_conjecture'))},",
            f"    blockedByCount := {_nat(len(dp.get('blocked_by') or []))},",
            f"    baseCaseN := {_nat(base.get('n'))},",
            f"    baseCaseReachesOne := {_bool(base.get('reaches_one'))},",
            f"    universalEntryHash := {_lean_string(bridge.get('universal_entry_certificate'))},",
            f"    parentStateCoverageHash := {_lean_string(bridge.get('parent_state_coverage_certificate'))},",
            f"    transitionSoundnessHash := {_lean_string(bridge.get('transition_soundness_certificate'))},",
            f"    wellFoundedRankingHash := {_lean_string(bridge.get('well_founded_ranking_certificate'))}",
            "  }",
            "}",
        ]
    )


def generate(out: Path) -> None:
    s3_certs = _extract_s3_exact_certs(_read_jsonl(S3_CERTS_PATH))
    s4_certs = _extract_s4_parent_map_certs(_read_jsonl(S4_CERTS_PATH))
    s6_certs = _extract_s6_certs(_read_jsonl(S6_CERTS_PATH))
    natural_kernel = _read_json(NATURAL_KERNEL_PATH)
    top_rows = _read_jsonl(TOP_LEVEL_CERTS_PATH)
    proof = _read_json(FINAL_PROOF_PATH) if FINAL_PROOF_PATH.exists() else {}

    text = "\n".join(
        [
            "import Collatz.Checkers",
            "",
            "/-!",
            "Generated literal data from final RUN-045/RUN-046 artifacts.",
            "This file contains certificate data and computable count checks.",
            "-/",
            "",
            "namespace Collatz",
            "",
            "def run046S3DebtCerts : List S3DebtExactCert :=",
            _list([_lean_s3_exact_cert(cert) for cert in s3_certs], indent="  "),
            "",
            "def run046S4ParentMapCerts : List S4ParentMapCert :=",
            _list([_lean_s4_cert(cert) for cert in s4_certs], indent="  "),
            "",
            "def run046S6LemmaCerts : List S6LemmaCert :=",
            _list([_lean_s6_cert(cert) for cert in s6_certs], indent="  "),
            "",
            "def run046NaturalKernelCert : NaturalViabilityKernelCert :=",
            _lean_natural_kernel_cert(natural_kernel),
            "",
            "def run046TopLevelCerts : TopLevelCertBundle :=",
            _top_level_bundle(top_rows, proof),
            "",
            "theorem run046_s3_count : run046S3DebtCerts.length = 182 := by native_decide",
            "",
            "theorem run046_s4_count : run046S4ParentMapCerts.length = 135 := by native_decide",
            "",
            "theorem run046_s6_count : run046S6LemmaCerts.length = 28 := by native_decide",
            "",
            "end Collatz",
            "",
        ]
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(OUT_PATH))
    args = parser.parse_args()
    generate(Path(args.out))


if __name__ == "__main__":
    main()
