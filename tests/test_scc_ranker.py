from collatz_lab.cycle_certificates import sharp_q23_return_map
from collatz_lab.scc_ranker import SymbolicEdge, rank_graph, strongly_connected_components


def test_tarjan_scc() -> None:
    edges = [SymbolicEdge("A", "B"), SymbolicEdge("B", "A"), SymbolicEdge("B", "C")]
    components = strongly_connected_components(edges)
    assert ["A", "B"] in components
    assert ["C"] in components


def test_rank_sharp_self_loop() -> None:
    sharp = sharp_q23_return_map()
    report = rank_graph(
        [
            SymbolicEdge(
                "P6_q23",
                "P6_q23",
                A=sharp.A,
                B=sharp.B,
                D=sharp.D,
                domain_residue=sharp.domain_residue,
                domain_depth=sharp.domain_depth,
            )
        ]
    )
    assert report["status"] == "PASS"
    assert report["rankings"][0]["status"] == "CLOSED_BY_HEIGHT_RANKING"


def test_rank_deterministic_mixed_cycle_by_composition() -> None:
    report = rank_graph(
        [
            SymbolicEdge("A", "B", A=3, B=1, D=2),
            SymbolicEdge("B", "A", A=5, B=1, D=2),
        ]
    )
    assert report["status"] == "PASS"
    assert report["rankings"][0]["ranking_kind"] == "multi_state_affine_cycle_height"
