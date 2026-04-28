import json

from collatz_lab.proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from collatz_lab.proof_action_dsl import parse_action, serialize_action
from collatz_lab.proof_action_residual_coverage import build_residual_coverage_certificate
from collatz_lab.proof_action_state import canonical_state


def _lemma_payload() -> dict:
    return {
        "lemma_id": "s6_lemma",
        "statement": "residual S6 lemma",
        "depends_on": ["coverage_cert", "base_case_cert", "lifting_cert", "no_escape_cert", "coverage_cert_residual_7_8"],
        "proof_payload": {
            "coverage": {"certificate_hash": "coverage_hash", "proof": "exact residual coverage replay"},
            "transition_chain": {"certificate_hash": "transition_hash", "proof": "exact transition replay"},
            "ranking_decrease": {"certificate_hash": "rank_hash", "proof": "ranking replay"},
            "no_escape": {"certificate_hash": "escape_hash", "proof": "no escape replay"},
            "induction_link": {"certificate_hash": "induction_hash", "proof": "induction replay"},
        },
    }


def _s6_state_with_residual_cert() -> str:
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="close residual S6 coverage",
        goal_id="s6_goal",
        goal_attrs={"kind": "s6_blocker", "blocker_id": "s6_blocker:residual:7:8"},
        known_lemmas=["s6_lemma"],
        facts=[
            {
                "kind": "s6_blocker",
                "target": "s6_goal",
                "blocker_id": "s6_blocker:residual:7:8",
                "branch_id": "s6_branch",
                "lemma_id": "s6_lemma",
                "coverage_certificate": "coverage_cert",
                "certificate_id": "coverage_cert",
                "base_case_certificate": "base_case_cert",
                "lifting_certificate": "lifting_cert",
                "no_escape_certificate": "no_escape_cert",
                "coverage_modulus": 8,
                "covered_residue_count": 7,
                "verifier_status": "ACCEPT",
                "lemma_payload": json.dumps(_lemma_payload(), sort_keys=True, separators=(",", ":")),
            },
            {
                "kind": "residual_coverage_certificate",
                "target": "s6_goal",
                "certificate_id": "coverage_cert_residual_7_8",
                "parent_certificate_id": "coverage_cert",
                "modulus": 8,
                "residual_start": 7,
                "residual_end": 8,
                "covered_residue_count": 1,
                "leaf_certificate_count": 1,
                "certificate_hash": "abc123",
                "status": "PASS",
            },
        ],
        open_obligations=["s6_goal"],
    )


def _residual_action() -> dict:
    return {
        "type": "PROVE_RESIDUAL_COVERAGE",
        "target": "s6_goal",
        "certificate_id": "coverage_cert_residual_7_8",
        "parent_certificate_id": "coverage_cert",
        "modulus": 8,
        "residual_start": 7,
        "residual_end": 8,
        "covered_residue_count": 1,
        "leaf_certificate_count": 1,
        "certificate_hash": "abc123",
    }


def test_residual_coverage_action_round_trips_through_dsl() -> None:
    text = serialize_action(_residual_action())

    assert parse_action(text) == _residual_action()


def test_residual_coverage_verifier_accepts_exact_open_gap() -> None:
    check = verify_action_for_state(_residual_action(), _s6_state_with_residual_cert())

    assert check.accepted
    assert check.closed_obligation
    assert check.progress == 1.0


def test_legal_candidates_emit_residual_coverage_action() -> None:
    candidates = legal_action_candidates_from_state(_s6_state_with_residual_cert(), max_candidates=64)

    assert _residual_action() in candidates


def test_verify_s6_lemma_accepts_partial_parent_coverage_with_residual_cert() -> None:
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal",
        "lemma_id": "s6_lemma",
        "verifier": "strict_theorem_verifier",
        "status": "ACCEPT",
        "lemma": _lemma_payload(),
    }

    check = verify_action_for_state(action, _s6_state_with_residual_cert())

    assert check.accepted
    assert "proof payload" in check.reason


def test_residual_certificate_builder_passes_tiny_exact_leaf() -> None:
    obligation = {
        "coverage_certificate": "coverage_cert",
        "residual_domain": {
            "modulus": 2,
            "residue_start": 0,
            "residue_end_exclusive": 1,
            "residue_count": 1,
        },
    }

    certificate = build_residual_coverage_certificate(
        obligation=obligation,
        certificate_id="coverage_cert_residual_0_1",
        max_extra_depth=0,
        max_steps=8,
        t_limit_multiplier=2,
    )

    assert certificate["status"] == "PASS"
    assert certificate["covered_residue_count"] == 1
    assert certificate["leaf_certificate_count"] == 1
    assert certificate["leaf_certificates"][0]["status"] == "PASS"
    assert json.dumps(certificate, sort_keys=True)
