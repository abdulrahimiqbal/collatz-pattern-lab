from collatz_lab.proof_verifier import build_collatz_descent_theorem_candidate


def _top_level_certificate(name: str) -> dict:
    return {
        "certificate_type": name,
        "status": "PASS",
        "certificate_hash": f"hash_{name}",
        "proof_payload": {"symbolic_payload": f"exact replay payload for {name}"},
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
    cert_names = [
        "universal_entry_certificate",
        "parent_state_coverage_certificate",
        "transition_soundness_certificate",
        "well_founded_ranking_certificate",
        "descent_implication_certificate",
    ]
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
        "top_level_certificates": {name: _top_level_certificate(name) for name in cert_names},
    }

    proof = build_collatz_descent_theorem_candidate(proof_graph=graph)

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
