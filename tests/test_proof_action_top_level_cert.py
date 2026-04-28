import json

from collatz_lab.proof_action_state import canonical_state
from collatz_lab.proof_action_top_level_cert import (
    TOP_LEVEL_CERTIFICATES,
    attach_top_level_certificates,
    build_top_level_certificates,
    certificate_hash,
    replay_top_level_certificate,
)
from collatz_lab.proof_verifier import build_collatz_descent_theorem_candidate


def _s6_state() -> str:
    return canonical_state(
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


def _closed_graph() -> dict:
    state = _s6_state()
    coverage_action = {
        "type": "PROVE_RESIDUE_COVERAGE",
        "target": "s6_goal",
        "modulus": 2,
        "covered_residue_count": 2,
        "certificate_id": "coverage_cert",
    }
    no_escape_action = {
        "type": "CERTIFY_NO_ESCAPE_BRANCH",
        "target": "s6_goal",
        "branch_id": "branch",
        "certificate_id": "escape_cert",
    }
    accepted = lambda action: [  # noqa: E731
        {
            "action": action,
            "action_text": json.dumps(action, sort_keys=True),
            "verifier_check": {"accepted": True, "status": "ACCEPT"},
        }
    ]
    return {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "coverage:coverage_cert": {
                "node_id": "coverage:coverage_cert",
                "node_type": "COVERAGE_CERTIFICATE",
                "status": "ACCEPTED",
                "state": state,
                "accepted_actions": accepted(coverage_action),
            },
            "no_escape:escape_cert": {
                "node_id": "no_escape:escape_cert",
                "node_type": "NO_ESCAPE_CERTIFICATE",
                "status": "ACCEPTED",
                "state": state,
                "accepted_actions": accepted(no_escape_action),
            },
        },
        "edges": [{"from": "coverage:coverage_cert", "to": "no_escape:escape_cert", "kind": "requires"}],
        "open": [],
    }


def test_graph_closed_but_missing_universal_entry_certificate_fails() -> None:
    proof = build_collatz_descent_theorem_candidate(proof_graph=_closed_graph())

    assert proof["verifier_status"] == "FAIL"
    assert any(row["obligation_id"] == "top_level:universal_entry_certificate" for row in proof["unknown_obligations"])


def test_status_only_top_level_certificate_fails() -> None:
    graph = _closed_graph()
    graph["top_level_certificates"] = {
        name: {
            "schema": "collatz_lab.top_level_theorem_certificate",
            "version": 1,
            "type": name,
            "certificate_type": name,
            "status": "PASS",
            "replay_status": "PASS",
            "certificate_hash": "abc",
            "proof_payload": {"status": "PASS"},
        }
        for name in TOP_LEVEL_CERTIFICATES
    }

    proof = build_collatz_descent_theorem_candidate(proof_graph=graph)

    assert proof["verifier_status"] == "FAIL"
    assert proof["top_level_replay_report"]["replay_pass_count"] == 0


def test_graph_closed_but_missing_ranking_certificate_fails() -> None:
    graph = _closed_graph()
    certs, failures = build_top_level_certificates(graph)
    assert failures == []
    patched = attach_top_level_certificates(graph, [cert for cert in certs if cert["type"] != "well_founded_ranking_certificate"])

    proof = build_collatz_descent_theorem_candidate(proof_graph=patched)

    assert proof["verifier_status"] == "FAIL"
    assert any(row["obligation_id"] == "top_level:well_founded_ranking_certificate" for row in proof["unknown_obligations"])


def test_ranking_certificate_with_non_decreasing_edge_fails() -> None:
    graph = _closed_graph()
    certs, _failures = build_top_level_certificates(graph)
    ranking = next(cert for cert in certs if cert["type"] == "well_founded_ranking_certificate")
    ranking["proof_payload"]["ranking"]["edge_checks"][0]["target_rank"] = ranking["proof_payload"]["ranking"]["edge_checks"][0]["source_rank"]
    ranking["proof_payload"]["ranking"]["edge_checks"][0]["decreases"] = False
    ranking["certificate_hash"] = certificate_hash(ranking)

    replay = replay_top_level_certificate(ranking, graph=graph)

    assert not replay.accepted
    assert replay.failures and replay.failures[0]["reason"] == "non_decreasing_edge"


def test_universal_entry_wrong_theorem_fails_even_with_recomputed_hash() -> None:
    graph = _closed_graph()
    certs, _failures = build_top_level_certificates(graph)
    universal = next(cert for cert in certs if cert["type"] == "universal_entry_certificate")
    universal["proof_payload"]["theorem"] = "forall n > 1 sample checks eventually decrease n"
    universal["certificate_hash"] = certificate_hash(universal)

    replay = replay_top_level_certificate(universal, graph=graph)

    assert not replay.accepted
    assert replay.failures and replay.failures[0]["reason"] == "wrong_theorem_statement"


def test_replayed_valid_synthetic_top_level_proof_object_passes() -> None:
    graph = _closed_graph()
    certs, failures = build_top_level_certificates(graph)
    patched = attach_top_level_certificates(graph, certs)

    proof = build_collatz_descent_theorem_candidate(proof_graph=patched)

    assert failures == []
    assert proof["verifier_status"] == "PASS"
    assert proof["top_level_replay_report"]["replay_pass_count"] == 5
