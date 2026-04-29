from collatz_lab.high_parent_root_relative_graph import build_root_relative_transition_graph
from collatz_lab.p32_special_transition import (
    build_p32_special_transition_family,
    build_p32_special_transition_schema,
    build_p32_special_uncovered_domains,
)


def test_root_relative_graph_records_exact_p32_family_fields() -> None:
    schema = build_p32_special_transition_schema()
    family = build_p32_special_transition_family(d_mod=1, d_period=2, h=1, b=1)
    uncovered = build_p32_special_uncovered_domains(h_max=1, b_max=1, families=[family])

    graph = build_root_relative_transition_graph(schema=schema, families=[family], uncovered_domains=uncovered)
    transition = graph["transitions"][0]

    assert graph["transition_count"] == 1
    assert transition["source_state"]["coordinate_form"] == "Q = 3^d*q"
    assert transition["target_state"]["parent_level"] == 1
    assert transition["exact_map"]["h"] == 1
    assert transition["root_relative_margin_at_min_debt"]["gain_num_lt_gain_den"] is False
    assert transition["classification"]["finite_subsystem_margin_available"] is False
