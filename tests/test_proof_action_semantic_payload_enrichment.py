import json
from pathlib import Path

from collatz_lab.proof_action_semantic_payload_enrichment import (
    build_kernel_to_path_link,
    build_s3_semantic_role,
    build_s6_proof_tree,
    build_top_level_coverage_domain_map,
    replay_semantic_payloads,
    validate_kernel_to_path_link_payload,
    validate_s3_semantic_role_payload,
    validate_s6_proof_tree_payload,
    validate_top_level_coverage_domain_map_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _first_jsonl(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").splitlines()[0])


def _reasons(failures: list[dict]) -> set[str]:
    return {str(failure.get("reason", "")) for failure in failures}


def test_s3_no_semantic_role_fails() -> None:
    failures = validate_s3_semantic_role_payload(
        {
            "kind": "S3_SEMANTIC_ROLE",
            "certificate_id": "s3-test",
            "measure_id": "rank",
            "decrease_certificate_id": "decrease",
        }
    )

    assert "S3_ROLE_UNCLASSIFIED" in _reasons(failures)


def test_s3_direct_descent_without_iterate_witness_fails() -> None:
    failures = validate_s3_semantic_role_payload(
        {
            "kind": "S3_SEMANTIC_ROLE",
            "certificate_id": "s3-test",
            "semantic_role": "DIRECT_DESCENT",
            "measure_id": "rank",
            "decrease_certificate_id": "decrease",
        }
    )

    assert "S3_DIRECT_DESCENT_ITERATE_WITNESS_MISSING" in _reasons(failures)


def test_s6_proof_tree_with_only_dependency_ids_fails() -> None:
    failures = validate_s6_proof_tree_payload(
        {
            "kind": "S6_PROOF_TREE_SEMANTICS",
            "lemma_id": "s6-test",
            "semantic_claim_type": "coverage",
            "conclusion": "coverage blocker closed",
            "dependencies": ["s3:a"],
            "proof_steps": [],
            "closes_blocker": True,
        }
    )

    reasons = _reasons(failures)
    assert "S6_PROOF_TREE_DEPENDENCIES_STATUS_ONLY" in reasons
    assert "S6_PROOF_TREE_MISSING_RULE" in reasons


def test_s6_proof_tree_with_mismatched_conclusion_fails() -> None:
    failures = validate_s6_proof_tree_payload(
        {
            "kind": "S6_PROOF_TREE_SEMANTICS",
            "lemma_id": "s6-test",
            "semantic_claim_type": "coverage",
            "conclusion": "no_escape blocker closed",
            "dependencies": [
                {
                    "dependency_type": "S4_PARENT_MAP",
                    "certificate_id": "s4",
                    "semantic_role": "PARENT_TRANSITION_ITERATE_WITNESS",
                    "used_for": "coverage blocker",
                }
            ],
            "proof_steps": [{"step_id": "step", "rule": "apply_coverage", "inputs": ["s4"], "output": "coverage"}],
            "closes_blocker": True,
        }
    )

    assert "S6_PROOF_TREE_CONCLUSION_MISMATCH" in _reasons(failures)


def test_kernel_link_without_divisibility_family_fails() -> None:
    failures = validate_kernel_to_path_link_payload(
        {
            "kind": "NATURAL_KERNEL_TO_PATH_LINK",
            "statement": "Any infinite internal guarded path over Nat induces membership in the surviving viability kernel.",
            "no_nat_in_kernel": {"reason": "positive distance"},
            "conclusion": "NoInfiniteInternalParentPathOverNat",
        }
    )

    assert "KERNEL_REFINEMENT_TO_DIVISIBILITY_MISSING" in _reasons(failures)


def test_top_level_coverage_without_explicit_domain_mapping_fails() -> None:
    failures = validate_top_level_coverage_domain_map_payload(
        {
            "kind": "TOP_LEVEL_COVERAGE_DOMAIN_MAP",
            "universal_entry": {"even_case": "even descends", "odd_case": "odd enters parent state"},
            "parent_state_domains": [],
            "no_uncovered_domains": True,
            "natural_kernel_reference": {"conclusion": "NoInfiniteInternalParentPathOverNat"},
        }
    )

    assert "TOP_LEVEL_DOMAIN_UNMAPPED" in _reasons(failures)


def test_valid_synthetic_payloads_pass() -> None:
    s3 = {
        "kind": "S3_SEMANTIC_ROLE",
        "certificate_id": "s3-test",
        "semantic_role": "SUPPORTING_DEBT_EDGE",
        "measure_id": "rank",
        "decrease_certificate_id": "decrease",
    }
    s6 = {
        "kind": "S6_PROOF_TREE_SEMANTICS",
        "lemma_id": "s6-test",
        "semantic_claim_type": "coverage",
        "conclusion": "coverage blocker closed",
        "dependencies": [
            {
                "dependency_type": "S3_DEBT",
                "certificate_id": "s3-test",
                "semantic_role": "SUPPORTING_DEBT_EDGE",
                "used_for": "coverage blocker",
            }
        ],
        "proof_steps": [{"step_id": "step", "rule": "apply_coverage", "inputs": ["s3-test"], "output": "coverage"}],
        "closes_blocker": True,
    }
    kernel = {
        "kind": "NATURAL_KERNEL_TO_PATH_LINK",
        "statement": "Any infinite internal guarded path over Nat induces membership in the surviving viability kernel.",
        "divisibility_family": {"statement": "for every N, 2^N divides denominator*q - numerator"},
        "no_nat_in_kernel": {"reason": "positive distance"},
        "conclusion": "NoInfiniteInternalParentPathOverNat",
    }
    coverage = {
        "kind": "TOP_LEVEL_COVERAGE_DOMAIN_MAP",
        "universal_entry": {"even_case": "even descends", "odd_case": "odd enters parent state"},
        "parent_state_domains": [
            {
                "domain_id": "P26:residual",
                "covered_predicate": "q mod 67108864 in [67108863, 67108864)",
                "residual_certificate_id": "residual",
            }
        ],
        "no_uncovered_domains": True,
        "natural_kernel_reference": {"conclusion": "NoInfiniteInternalParentPathOverNat"},
    }

    assert not validate_s3_semantic_role_payload(s3)
    assert not validate_s6_proof_tree_payload(s6)
    assert not validate_kernel_to_path_link_payload(kernel)
    assert not validate_top_level_coverage_domain_map_payload(coverage)


def test_real_payload_builders_generate_replayable_payloads() -> None:
    s3_row = _first_jsonl(ROOT / "certificate_store/run046_s3_debt_certificates.jsonl")
    s6_row = _first_jsonl(ROOT / "certificate_store/run046_s6_lemma_certificates.jsonl")
    kernel_cert = json.loads((ROOT / "certificate_store/run045_natural_viability_kernel_certificate.json").read_text(encoding="utf-8"))
    top_rows = [
        json.loads(line)
        for line in (ROOT / "certificate_store/run046_top_level_certificates.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    s3_payload, s3_failures = build_s3_semantic_role(
        s3_row,
        consumers={},
        transition_soundness_id="transition_soundness_certificate",
    )
    s3_roles = {s3_payload["certificate_id"]: s3_payload["semantic_role"]}
    s6_payload, s6_failures = build_s6_proof_tree(s6_row, s3_roles)
    kernel_payload, kernel_failures = build_kernel_to_path_link(kernel_cert)
    coverage_payload, coverage_failures = build_top_level_coverage_domain_map(top_rows, kernel_link=kernel_payload)

    assert not s3_failures
    assert not s6_failures
    assert not kernel_failures
    assert not coverage_failures
    assert replay_semantic_payloads([s3_payload, s6_payload, kernel_payload, coverage_payload])["accepted"]
