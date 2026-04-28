#!/usr/bin/env python3
"""Generate literal Lean data from the frozen RUN-024 artifacts.

The generated file contains data values only.  It does not turn Python replay
status into a Lean theorem.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = REPO_ROOT / "certificate_store/run028_proof_dependency_graph_frozen.json"
S3_EXACT_CERTS_PATH = REPO_ROOT / "certificate_store/run028_s3_debt_certificates.jsonl"
S6_CERTS_PATH = REPO_ROOT / "certificate_store/run023_s6_lemma_certificates.jsonl"
TOP_LEVEL_CERTS_PATH = REPO_ROOT / "certificate_store/run028_top_level_certificates.jsonl"
FINAL_PROOF_PATH = REPO_ROOT / "certificate_store/run028_final_proof_object.json"
OUT_PATH = REPO_ROOT / "formal/lean/Collatz/Run024Data.lean"
BRANCH_RE = re.compile(r"^P(?P<parent>\d+):r(?P<residue>\d+):d(?P<depth>\d+)$")


def _lean_string(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def _nat(value: Any) -> str:
    return str(int(value or 0))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _list(items: list[str], *, indent: str = "") -> str:
    if not items:
        return "[]"
    inner = (",\n" + indent).join(items)
    return "[\n" + indent + inner + "\n]"


def _extract_s4_certs(graph: dict[str, Any]) -> list[dict[str, Any]]:
    certs: list[dict[str, Any]] = []
    for node_id, node in (graph.get("nodes") or {}).items():
        if node.get("node_type") != "S4_LIFT":
            continue
        for accepted in node.get("accepted_actions") or []:
            action = accepted.get("action") or {}
            if action.get("type") == "DERIVE_PARENT_TRANSITION" and isinstance(action.get("transition_certificate"), dict):
                cert = dict(action["transition_certificate"])
                cert["_node_id"] = node_id
                certs.append(cert)
    certs.sort(key=lambda row: (str(row.get("transition_id")), str(row.get("_node_id"))))
    return certs


def _parse_branch(branch_id: str) -> dict[str, int]:
    match = BRANCH_RE.fullmatch(branch_id)
    if not match:
        return {"parent": 0, "residue": 0, "depth": 0}
    return {key: int(value) for key, value in match.groupdict().items()}


def _extract_s3_exact_certs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    certs = [row["s3_debt_certificate"] for row in rows if isinstance(row.get("s3_debt_certificate"), dict)]
    certs.sort(key=lambda row: str(row.get("node_id", "")))
    return certs


def _lean_s4_cert(cert: dict[str, Any]) -> str:
    div = cert.get("divisibility_certificate") or {}
    cong = cert.get("congruence_certificate") or {}
    mem = cert.get("target_membership_certificate") or {}
    return "\n".join(
        [
            "{",
            f"  transitionId := {_lean_string(cert.get('transition_id', ''))},",
            f"  branchId := {_lean_string(cert.get('branch_id', ''))},",
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
            f"  certificateHash := {_lean_string(cert.get('certificate_hash', ''))}",
            "}",
        ]
    )


def _lean_s3_exact_congruence(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"    typeName := {_lean_string(cert.get('type', ''))},",
            f"    branchId := {_lean_string(cert.get('branch_id', ''))},",
            f"    sourceParent := {_nat(cert.get('source_parent'))},",
            f"    targetParent := {_nat(cert.get('target_parent'))},",
            f"    valuation := {_nat(cert.get('valuation'))},",
            f"    branchResidue := {_nat(cert.get('branch_residue'))},",
            f"    branchDepth := {_nat(cert.get('branch_depth'))},",
            f"    sourceModulus := {_nat(cert.get('source_modulus'))},",
            f"    theoremName := {_lean_string(cert.get('theorem', ''))},",
            f"    statement := {_lean_string(cert.get('statement', ''))}",
            "  }",
        ]
    )


def _lean_s3_measure(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"    typeName := {_lean_string(cert.get('type', ''))},",
            f"    measureId := {_lean_string(cert.get('measure_id', ''))},",
            f"    branchId := {_lean_string(cert.get('branch_id', ''))},",
            f"    sourceParent := {_nat(cert.get('source_parent'))},",
            f"    targetParent := {_nat(cert.get('target_parent'))},",
            f"    valuation := {_nat(cert.get('valuation'))},",
            f"    gainNum := {_nat(cert.get('gain_num'))},",
            f"    gainDen := {_nat(cert.get('gain_den'))},",
            f"    decreaseInequality := {_lean_string(cert.get('decrease_inequality', ''))}",
            "  }",
        ]
    )


def _lean_s3_local_descent(cert: dict[str, Any]) -> str:
    return "\n".join(
        [
            "{",
            f"    typeName := {_lean_string(cert.get('type', ''))},",
            f"    branchId := {_lean_string(cert.get('branch_id', ''))},",
            f"    gainNum := {_nat(cert.get('gain_num'))},",
            f"    gainDen := {_nat(cert.get('gain_den'))},",
            f"    rule := {_lean_string(cert.get('rule', ''))}",
            "  }",
        ]
    )


def _lean_s3_exact_cert(cert: dict[str, Any]) -> str:
    congruence = cert.get("exact_congruence_certificate") or {}
    measure = cert.get("debt_measure_definition") or {}
    descent = cert.get("local_descent_certificate") or {}
    return "\n".join(
        [
            "{",
            f"  nodeId := {_lean_string(cert.get('node_id', ''))},",
            f"  branchId := {_lean_string(cert.get('branch_id', ''))},",
            f"  sourceParent := {_nat(cert.get('source_parent'))},",
            f"  targetParent := {_nat(cert.get('target_parent'))},",
            f"  valuation := {_nat(cert.get('valuation'))},",
            f"  gainNum := {_nat(cert.get('gain_num'))},",
            f"  gainDen := {_nat(cert.get('gain_den'))},",
            "  exactCongruenceCertificate :=",
            _lean_s3_exact_congruence(congruence) + ",",
            "  debtMeasureDefinition :=",
            _lean_s3_measure(measure) + ",",
            "  localDescentCertificate :=",
            _lean_s3_local_descent(descent) + ",",
            f"  certificateHash := {_lean_string(cert.get('certificate_hash', ''))}",
            "}",
        ]
    )


def _lean_string_list(items: list[str]) -> str:
    return "[" + ", ".join(_lean_string(item) for item in items) + "]"


def _extract_s6_certs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    certs = [row["s6_lemma_certificate"] for row in rows if isinstance(row.get("s6_lemma_certificate"), dict)]
    certs.sort(key=lambda row: str(row.get("lemma_id", "")))
    return certs


def _lean_s6_cert(cert: dict[str, Any]) -> str:
    payload = cert.get("proof_payload") or {}
    depends = [str(item) for item in payload.get("depends_on", [])]
    return "\n".join(
        [
            "{",
            f"  certificateId := {_lean_string(cert.get('certificate_id', ''))},",
            f"  lemmaId := {_lean_string(cert.get('lemma_id', ''))},",
            f"  blockerId := {_lean_string(cert.get('blocker_id', ''))},",
            f"  blockerType := {_lean_string(cert.get('blocker_type', ''))},",
            f"  dependencyIds := {_lean_string_list(depends)},",
            f"  certificateHash := {_lean_string(cert.get('certificate_hash', ''))}",
            "}",
        ]
    )


def _top_level_bundle(top_rows: list[dict[str, Any]], proof: dict[str, Any]) -> str:
    certs = {str(row.get("type")): row for row in top_rows}
    coverage_payload = certs.get("parent_state_coverage_certificate", {}).get("proof_payload") or {}
    descent_payload = certs.get("descent_implication_certificate", {}).get("proof_payload") or {}
    return "\n".join(
        [
            "{",
            f"  universalEntryHash := {_lean_string(certs.get('universal_entry_certificate', {}).get('certificate_hash', ''))},",
            f"  parentStateCoverageHash := {_lean_string(certs.get('parent_state_coverage_certificate', {}).get('certificate_hash', ''))},",
            f"  transitionSoundnessHash := {_lean_string(certs.get('transition_soundness_certificate', {}).get('certificate_hash', ''))},",
            f"  wellFoundedRankingHash := {_lean_string(certs.get('well_founded_ranking_certificate', {}).get('certificate_hash', ''))},",
            f"  descentImplicationHash := {_lean_string(certs.get('descent_implication_certificate', {}).get('certificate_hash', ''))},",
            f"  theoremStatement := {_lean_string(proof.get('theorem', ''))},",
            f"  descentImplicationStatement := {_lean_string(descent_payload.get('collatz_conjecture') or proof.get('descent_implication', ''))},",
            f"  acceptedNodeCount := {_nat(coverage_payload.get('accepted_node_count'))},",
            f"  totalNodeCount := {_nat(coverage_payload.get('total_node_count'))},",
            f"  openNodeCount := {_nat(coverage_payload.get('open_node_count'))}",
            "}",
        ]
    )


def generate(out: Path) -> None:
    graph = _read_json(GRAPH_PATH)
    s3_certs = _extract_s3_exact_certs(_read_jsonl(S3_EXACT_CERTS_PATH))
    s4_certs = _extract_s4_certs(graph)
    s6_certs = _extract_s6_certs(_read_jsonl(S6_CERTS_PATH))
    top_rows = _read_jsonl(TOP_LEVEL_CERTS_PATH)
    proof = _read_json(FINAL_PROOF_PATH)

    s3_items = [_lean_s3_exact_cert(cert) for cert in s3_certs]
    s4_items = [_lean_s4_cert(cert) for cert in s4_certs]
    s6_items = [_lean_s6_cert(cert) for cert in s6_certs]
    top_bundle = _top_level_bundle(top_rows, proof)

    text = "\n".join(
        [
            "import Collatz.Checkers",
            "",
            "/-!",
            "Generated literal data from RUN-024/RUN-023 frozen artifacts.",
            "This file contains data and computable checks; it does not trust Python replay status.",
            "-/",
            "",
            "namespace Collatz",
            "",
            "def run024S3DebtExactCerts : List S3DebtExactCert :=",
            _list(s3_items, indent="  "),
            "",
            "def run024S4Certs : List S4TransitionCert :=",
            _list(s4_items, indent="  "),
            "",
            "def run024S6Certs : List S6LemmaCert :=",
            _list(s6_items, indent="  "),
            "",
            "def run024TopLevelCerts : TopLevelCertBundle :=",
            top_bundle,
            "",
            "def run024Manifest : Run024Manifest :=",
            "{",
            "  s3DebtExactCerts := run024S3DebtExactCerts,",
            "  s4Certs := run024S4Certs,",
            "  s6Certs := run024S6Certs,",
            "  topLevel := run024TopLevelCerts",
            "}",
            "",
            "theorem run024_s3_debt_exact_cert_count : run024S3DebtExactCerts.length = 182 := by native_decide",
            "",
            "theorem run024_s4_cert_count : run024S4Certs.length = 135 := by native_decide",
            "",
            "theorem run024_s6_cert_count : run024S6Certs.length = 28 := by native_decide",
            "",
            "theorem run024S3DebtExactCerts_check : checkAllS3DebtExactCerts run024S3DebtExactCerts = true := by native_decide",
            "",
            "theorem run024S3DebtExactCerts_sound : AllS3DebtExactClaims run024S3DebtExactCerts :=",
            "  checkAllS3DebtExactCerts_sound run024S3DebtExactCerts run024S3DebtExactCerts_check",
            "",
            "theorem run024S4Certs_check : checkAllS4TransitionCerts run024S4Certs = true := by native_decide",
            "",
            "theorem run024S4Certs_sound : AllS4TransitionClaims run024S4Certs :=",
            "  checkAllS4TransitionCerts_sound run024S4Certs run024S4Certs_check",
            "",
            "theorem run024Manifest_check : checkRun024Manifest run024Manifest = true := by native_decide",
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
