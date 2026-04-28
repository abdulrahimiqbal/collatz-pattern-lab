import copy

from collatz_lab.proof_action_scc_ranking_cert import (
    build_affine_ranking_certificate,
    build_refined_scc_graph,
    check_affine_cycle_descent,
    compose_affine_maps,
    derive_parent_coordinate_affine_map,
    extract_scc_internal_edges,
    replay_scc_ranking_certificate,
)


def _scc_edge(edge_id: str = "s4:unit", cert_id: str = "cert_unit") -> dict:
    return {
        "edge_id": edge_id,
        "kind": "HIGH_PARENT_SUCCESSOR_EXACT",
        "node_id": "s4:unit",
        "source": "P1",
        "target": "P1",
        "terminal_descent": False,
        "transition_certificate_id": cert_id,
        "transition_certificate_hash": "hash",
    }


def _synthetic_edge(edge_id: str, source: str, target: str, A: int, B: int, D: int = 1) -> dict:
    return {
        "edge_id": edge_id,
        "source": source,
        "target": target,
        "source_parent": int(source[1:]),
        "target_parent": int(target[1:]),
        "branch_id": f"{source}:r0:d1",
        "valuation": 0,
        "transition_certificate_id": f"cert_{edge_id}",
        "transition_certificate_hash": f"hash_{edge_id}",
        "parent_coordinate_map": {
            "edge_id": edge_id,
            "source": source,
            "target": target,
            "A": A,
            "B": B,
            "D": D,
            "minimum_q": 2,
            "domain_modulus": 1,
            "domain_residue": 0,
        },
        "exact_symbolic_transition_payload": {
            "transition_id": f"cert_{edge_id}",
            "symbolic_map": {
                "parent_coordinate_map": {
                    "A": A,
                    "B": B,
                    "D": D,
                    "minimum_q": 2,
                    "domain_modulus": 1,
                    "domain_residue": 0,
                }
            },
        },
    }


def test_scc_edge_extraction_rejects_status_only_edges() -> None:
    result = extract_scc_internal_edges(
        [{"scc_id": "unit", "nodes": ["P1"], "edge_count": 1, "edges": [_scc_edge()]}],
        [{"node_id": "s4:unit", "verifier_check": {"accepted": True, "status": "ACCEPT"}}],
    )

    assert not result.accepted
    assert result.edges == []
    assert result.failures[0]["reason"] == "REJECT_STATUS_ONLY_EDGE"


def test_parent_coordinate_affine_map_replays_on_synthetic_transition() -> None:
    edge = _synthetic_edge("e1", "P1", "P1", 1, -1)

    replay = derive_parent_coordinate_affine_map(edge)

    assert replay.accepted
    assert replay.row["status"] == "PASS"
    assert replay.row["statement"] == "q' = (1*q + -1) / 1"


def test_cycle_composition_detects_descending_affine_cycle() -> None:
    maps = [
        _synthetic_edge("e1", "P1", "P1", 1, -1)["parent_coordinate_map"],
        _synthetic_edge("e2", "P1", "P1", 1, 0)["parent_coordinate_map"],
    ]

    composed = compose_affine_maps(maps)
    replay = check_affine_cycle_descent(maps, minimum_q=2)

    assert composed["A"] == 1
    assert composed["B"] == -1
    assert replay["status"] == "PASS"


def test_cycle_composition_rejects_non_descending_cycle() -> None:
    maps = [_synthetic_edge("e1", "P1", "P1", 1, 1)["parent_coordinate_map"]]

    replay = check_affine_cycle_descent(maps, minimum_q=2)

    assert replay["status"] == "FAIL"
    assert not replay["descent_check"]["minimum_domain_passes"]


def test_affine_ranking_checker_accepts_valid_rational_ranking() -> None:
    edge = _synthetic_edge("e1", "P1", "P1", 1, -1)
    cert = build_affine_ranking_certificate(
        scc_id="unit",
        states=["P1"],
        edges=[edge],
        coefficients={"P1": {"alpha": "1/2", "beta": "0"}},
    )

    replay = replay_scc_ranking_certificate(cert, [edge])

    assert replay["accepted"]
    assert replay["status"] == "PASS"


def test_affine_ranking_checker_rejects_non_decreasing_edge() -> None:
    edge = _synthetic_edge("e1", "P1", "P1", 1, 1)
    cert = build_affine_ranking_certificate(
        scc_id="unit",
        states=["P1"],
        edges=[edge],
        coefficients={"P1": {"alpha": "1", "beta": "0"}},
    )

    replay = replay_scc_ranking_certificate(cert, [edge])

    assert not replay["accepted"]
    assert any(failure["reason"] == "non_decreasing_edge" for failure in replay["failures"])


def test_scc_ranking_certificate_fails_if_one_internal_edge_is_missing() -> None:
    edge1 = _synthetic_edge("e1", "P1", "P1", 1, -1)
    edge2 = _synthetic_edge("e2", "P1", "P1", 1, -1)
    cert = build_affine_ranking_certificate(
        scc_id="unit",
        states=["P1"],
        edges=[edge1],
        coefficients={"P1": {"alpha": "1", "beta": "0"}},
    )

    replay = replay_scc_ranking_certificate(cert, [edge1, edge2])

    assert not replay["accepted"]
    assert any(failure["reason"] == "ranking_certificate_missing_internal_edges" for failure in replay["failures"])


def test_refined_graph_preserves_exact_edge_coverage() -> None:
    edges = [_synthetic_edge("e1", "P1", "P2", 1, -1), _synthetic_edge("e2", "P2", "P1", 1, -1)]

    graph = build_refined_scc_graph(edges)

    assert graph["coverage_preserved"]
    assert graph["edge_count"] == len(edges)
    assert {edge["edge_id"] for edge in graph["edges"]} == {"e1", "e2"}


def test_manifest_hash_mutation_of_ranking_cert_fails_replay() -> None:
    edge = _synthetic_edge("e1", "P1", "P1", 1, -1)
    cert = build_affine_ranking_certificate(
        scc_id="unit",
        states=["P1"],
        edges=[edge],
        coefficients={"P1": {"alpha": "1", "beta": "0"}},
    )
    mutated = copy.deepcopy(cert)
    mutated["certificate_hash"] = "deadbeef"

    replay = replay_scc_ranking_certificate(mutated, [edge])

    assert not replay["accepted"]
    assert any(failure["reason"] == "scc_ranking_certificate_hash_mismatch" for failure in replay["failures"])
