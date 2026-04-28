import json

from collatz_lab.proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from collatz_lab.proof_action_dsl import parse_action, serialize_action
from collatz_lab.proof_action_parent_residual import build_parent_residual_certificate
from collatz_lab.proof_action_state import canonical_state


def _parent_action() -> dict:
    return {
        "type": "PROVE_PARENT_RESIDUAL_COVERAGE",
        "target": "s6_goal",
        "certificate_id": "parent_residual_cert_P3_7_8",
        "parent_certificate_id": "coverage_cert",
        "residual_certificate_id": "coverage_cert_residual_7_8",
        "parent_level": 3,
        "modulus": 8,
        "residual_start": 7,
        "residual_end": 8,
        "path_node_count": 6,
        "s3_dependency_count": 1,
        "s4_dependency_count": 1,
        "s6_dependency_count": 1,
        "no_escape_dependency_count": 1,
        "ranking_delta_num": 1,
        "ranking_delta_den": 2,
        "certificate_hash": "def456",
    }


def _lemma_payload() -> dict:
    return {
        "lemma_id": "s6_lemma",
        "statement": "parent residual S6 lemma",
        "depends_on": ["coverage_cert", "base_case_cert", "lifting_cert", "no_escape_cert", "parent_residual_cert_P3_7_8"],
        "proof_payload": {
            "coverage": {"certificate_hash": "coverage_hash", "proof": "exact coverage plus residual replay"},
            "transition_chain": {"certificate_hash": "transition_hash", "proof": "closed parent path replay"},
            "ranking_decrease": {"certificate_hash": "rank_hash", "proof": "ranking delta 1/2"},
            "no_escape": {"certificate_hash": "escape_hash", "proof": "no escape replay"},
            "induction_link": {"certificate_hash": "induction_hash", "proof": "well-founded induction replay"},
        },
    }


def _state_with_parent_cert() -> str:
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="close parent residual S6 coverage",
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
                "verifier_status": "REJECT",
                "lemma_payload": json.dumps(_lemma_payload(), sort_keys=True, separators=(",", ":")),
            },
            {
                "kind": "parent_residual_certificate",
                "target": "s6_goal",
                "certificate_id": "parent_residual_cert_P3_7_8",
                "parent_certificate_id": "coverage_cert",
                "residual_certificate_id": "coverage_cert_residual_7_8",
                "parent_level": 3,
                "modulus": 8,
                "residual_start": 7,
                "residual_end": 8,
                "path_node_count": 6,
                "s3_dependency_count": 1,
                "s4_dependency_count": 1,
                "s6_dependency_count": 1,
                "no_escape_dependency_count": 1,
                "ranking_delta_num": 1,
                "ranking_delta_den": 2,
                "certificate_hash": "def456",
                "status": "PASS",
            },
        ],
        open_obligations=["s6_goal"],
    )


def _accepted_node(node_type: str, action: dict, *, source: dict | None = None, deps: list[str] | None = None, evidence: dict | None = None) -> dict:
    return {
        "node_type": node_type,
        "status": "ACCEPTED",
        "depends_on": deps or [],
        "source": source or {},
        "evidence": evidence or {},
        "accepted_actions": [{"action": action}],
    }


def _tiny_parent_graph() -> dict:
    common = {
        "lemma_id": "s6_parent_transition_lemma",
        "coverage_certificate": "coverage_parent",
        "lifting_certificate": "lifting_parent",
        "base_case_certificate": "base_parent",
        "no_escape_certificate": "no_escape_parent",
    }
    return {
        "nodes": {
            "s3:p3": _accepted_node(
                "S3_TRANSITION",
                {
                    "type": "CHECK_DEBT_DECREASE",
                    "target": "goal_0",
                    "branch_id": "P2:r7:d3",
                    "gain_num": 1,
                    "gain_den": 2,
                    "valuation": 1,
                },
            ),
            "coverage:coverage_parent": _accepted_node(
                "COVERAGE_CERTIFICATE",
                {
                    "type": "PROVE_RESIDUE_COVERAGE",
                    "target": "s6_goal_parent_transition",
                    "modulus": 8,
                    "covered_residue_count": 8,
                    "certificate_id": "coverage_parent",
                },
                source={"blocker_type": "parent_transition"},
                evidence=common,
            ),
            "s6_lemma:s6_parent_transition_lemma": _accepted_node(
                "S6_LEMMA",
                {
                    "type": "VERIFY_S6_LEMMA",
                    "target": "s6_goal_parent_transition",
                    "lemma_id": "s6_parent_transition_lemma",
                    "verifier": "strict_theorem_verifier",
                    "status": "ACCEPT",
                },
                source={"blocker_type": "parent_transition"},
                evidence=common,
            ),
            "s6_lift:lifting_parent": _accepted_node(
                "S4_LIFT",
                {
                    "type": "LIFT_LOCAL_TO_PARAMETRIC_FAMILY",
                    "target": "s6_goal_parent_transition",
                    "local_lemma": "s6_parent_transition_lemma",
                    "family_id": "s6_parametric_family",
                    "lifting_certificate": "lifting_parent",
                },
                source={"blocker_type": "parent_transition"},
                evidence=common,
            ),
            "induction:base_parent": _accepted_node(
                "INDUCTION_CLOSURE",
                {
                    "type": "CLOSE_WELL_FOUNDED_INDUCTION",
                    "target": "s6_goal_parent_transition",
                    "measure": "n",
                    "descent_lemma": "s6_parent_transition_lemma",
                    "base_case_certificate": "base_parent",
                },
                source={"blocker_type": "parent_transition"},
                evidence=common,
            ),
            "no_escape:no_escape_parent": _accepted_node(
                "NO_ESCAPE_CERTIFICATE",
                {
                    "type": "CERTIFY_NO_ESCAPE_BRANCH",
                    "target": "s6_goal_parent_transition",
                    "branch_id": "s6_branch_parent",
                    "certificate_id": "no_escape_parent",
                },
                source={"blocker_type": "parent_transition"},
                evidence=common,
            ),
            "strict_blocker:parent": _accepted_node(
                "STRICT_THEOREM_BLOCKER",
                {
                    "type": "CLOSE_STRICT_THEOREM_BLOCKER",
                    "target": "s6_goal_parent_transition",
                    "blocker_id": "s6_parent_transition",
                    "lemma_id": "s6_parent_transition_lemma",
                },
                source={"blocker_type": "parent_transition"},
                deps=[
                    "s6_lemma:s6_parent_transition_lemma",
                    "coverage:coverage_parent",
                    "s6_lift:lifting_parent",
                    "induction:base_parent",
                    "no_escape:no_escape_parent",
                ],
                evidence=common,
            ),
        }
    }


def test_parent_residual_action_round_trips_through_dsl() -> None:
    text = serialize_action(_parent_action())

    assert parse_action(text) == _parent_action()


def test_parent_residual_verifier_and_candidate_generation() -> None:
    state = _state_with_parent_cert()

    assert verify_action_for_state(_parent_action(), state).accepted
    assert _parent_action() in legal_action_candidates_from_state(state)


def test_verify_s6_lemma_accepts_partial_coverage_with_parent_residual_cert() -> None:
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal",
        "lemma_id": "s6_lemma",
        "verifier": "strict_theorem_verifier",
        "status": "ACCEPT",
        "lemma": _lemma_payload(),
    }

    check = verify_action_for_state(action, _state_with_parent_cert())

    assert check.accepted


def test_verify_s6_lemma_rejects_status_only_even_with_parent_residual_cert() -> None:
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal",
        "lemma_id": "s6_lemma",
        "verifier": "strict_theorem_verifier",
        "status": "ACCEPT",
    }

    check = verify_action_for_state(action, _state_with_parent_cert())

    assert not check.accepted
    assert check.status == "REJECT_SYNTAX"


def test_parent_residual_certificate_uses_accepted_graph_path() -> None:
    certificate = build_parent_residual_certificate(
        residual={
            "residual_certificate_id": "coverage_cert_residual_7_8",
            "parent_certificate_id": "coverage_cert",
            "modulus": 8,
            "residual_start": 7,
            "residual_end": 8,
        },
        theorem_graph=_tiny_parent_graph(),
        certificate_id="parent_residual_cert_P3_7_8",
    )

    assert certificate["status"] == "PASS"
    assert certificate["parent_level"] == 3
    assert certificate["s3_dependency_count"] == 1
    assert certificate["s4_dependency_count"] == 1
    assert certificate["s6_dependency_count"] == 1
    assert certificate["no_escape_dependency_count"] == 1
    assert certificate["ranking_delta_num"] < certificate["ranking_delta_den"]
