from collatz_lab.parent_graph import build_parent_transition_graph, tarjan_scc


def test_tarjan_scc_finds_cycle() -> None:
    graph = {"a": {"b"}, "b": {"a", "c"}, "c": set()}
    components = tarjan_scc(graph)
    assert ["a", "b"] in components
    assert ["c"] in components


def test_parent_graph_small_smoke() -> None:
    residual = {"unknown_q_mod_64": [{"value": 8, "count": 3}]}
    burst = {"families": [{"a": 6, "h_star": 4, "q_residue": 9, "q_depth": 4}]}
    returns = {"maps": [{"a": 6, "h": 1}]}
    report = build_parent_transition_graph(6, residual, burst, returns)
    assert report["node_count"] >= 5
    assert report["terminal_burst_escape_nodes"] == 1
    assert report["return_to_parent_edges"] == 1
