from collatz_lab.proof_verifier import build_collatz_descent_theorem_candidate, verify_proof_object


def test_proof_verifier_rejects_unknowns() -> None:
    proof = build_collatz_descent_theorem_candidate()
    assert proof["verifier_status"] == "FAIL"
    assert proof["unknown_obligations"]
    assert proof["minimal_blocking_set"]


def test_proof_verifier_accepts_minimal_closed_shape() -> None:
    proof = {
        "theorem": "forall n > 1 exists k with C^k(n)<n",
        "coverage": {"status": "UNIVERSAL_PARENT_STATES"},
        "states": [],
        "transitions": [],
        "scc_rankings": [],
        "ancestor_descent_certificates": [],
        "finite_exceptions": [],
        "unknown_obligations": [],
        "verifier_status": "PENDING",
    }
    result = verify_proof_object(proof)
    assert result["verifier_status"] == "PASS"


def test_proof_verifier_reads_persistent_graph_blockers() -> None:
    proof = build_collatz_descent_theorem_candidate(
        proof_graph={
            "open": ["node"],
            "nodes": {"node": {"status": "NEEDS_SPLIT", "scope": "synthetic", "coverage": {"count_unknown": 7}}},
        }
    )
    assert proof["verifier_status"] == "FAIL"
    assert any(row.get("obligation_id") == "node" for row in proof["minimal_blocking_set"])
