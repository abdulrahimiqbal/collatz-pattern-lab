import json

from collatz_lab.proof_action_state import canonical_state
from collatz_lab.proof_action_top_level_cert import attach_top_level_certificates, build_top_level_certificates
from collatz_lab.proof_verifier import build_collatz_descent_theorem_candidate


def _closed_graph() -> dict:
    state = canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="coverage",
        goal_id="s6_goal",
        goal_attrs={"kind": "s6_blocker"},
        known_lemmas=["lemma"],
        facts=[
            {
                "kind": "s6_blocker",
                "target": "s6_goal",
                "blocker_id": "blocker",
                "branch_id": "branch",
                "lemma_id": "lemma",
                "certificate_id": "coverage_cert",
                "coverage_certificate": "coverage_cert",
                "base_case_certificate": "base_cert",
                "lifting_certificate": "lift_cert",
                "no_escape_certificate": "escape_cert",
                "coverage_modulus": 2,
                "covered_residue_count": 2,
                "status": "PASS",
            }
        ],
    )
    action = {
        "type": "PROVE_RESIDUE_COVERAGE",
        "target": "s6_goal",
        "modulus": 2,
        "covered_residue_count": 2,
        "certificate_id": "coverage_cert",
    }
    return {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "coverage:unit": {
                "node_id": "coverage:unit",
                "node_type": "COVERAGE_CERTIFICATE",
                "status": "ACCEPTED",
                "state": state,
                "accepted_actions": [{"action": action, "action_text": json.dumps(action, sort_keys=True)}],
            }
        },
        "edges": [],
        "open": [],
    }


def test_closed_proof_action_graph_without_top_level_certificates_is_strict_verifier_fail() -> None:
    graph = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "coverage:unit": {
                "node_id": "coverage:unit",
                "node_type": "COVERAGE_CERTIFICATE",
                "status": "ACCEPTED",
            }
        },
        "edges": [],
        "open": [],
    }

    proof = build_collatz_descent_theorem_candidate(proof_graph=graph)

    assert proof["verifier_status"] == "FAIL"
    assert proof["coverage"]["status"] == "FINITE_PARENT_STATE_DIAGNOSTIC"
    assert any(str(row["obligation_id"]).startswith("top_level:") for row in proof["unknown_obligations"])


def test_closed_proof_action_graph_requires_explicit_replayable_universal_certificates() -> None:
    graph = _closed_graph()
    certs, failures = build_top_level_certificates(graph)
    graph = attach_top_level_certificates(graph, certs)

    proof = build_collatz_descent_theorem_candidate(proof_graph=graph)

    assert failures == []
    assert proof["verifier_status"] == "PASS"
    assert proof["coverage"]["status"] == "UNIVERSAL_PARENT_STATES"


def test_open_proof_action_graph_keeps_strict_verifier_fail() -> None:
    graph = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "coverage:unit": {
                "node_id": "coverage:unit",
                "node_type": "COVERAGE_CERTIFICATE",
                "status": "OPEN",
            }
        },
        "edges": [],
        "open": ["coverage:unit"],
    }

    proof = build_collatz_descent_theorem_candidate(proof_graph=graph)

    assert proof["verifier_status"] == "FAIL"
    assert any(row["obligation_id"] == "coverage:unit" for row in proof["unknown_obligations"])
