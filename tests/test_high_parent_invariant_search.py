from collatz_lab.high_parent_invariant_search import run_high_parent_invariant_search
from collatz_lab.high_parent_root_relative_graph import build_root_relative_transition_graph
from collatz_lab.p32_special_transition import (
    build_p32_special_transition_family,
    build_p32_special_transition_schema,
    build_p32_special_uncovered_domains,
)


def test_invariant_search_fails_closed_without_exact_progress() -> None:
    schema = build_p32_special_transition_schema()
    family = build_p32_special_transition_family(d_mod=1, d_period=2, h=1, b=1)
    uncovered = build_p32_special_uncovered_domains(h_max=1, b_max=1, families=[family])
    graph = build_root_relative_transition_graph(schema=schema, families=[family], uncovered_domains=uncovered)

    result = run_high_parent_invariant_search(graph=graph)

    assert result["run_result"]["status"] == "FAIL"
    assert result["run_result"]["formalization_status"] == "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING"
    assert result["accepted_certificates"] == []
    assert result["remaining_uncovered_domains"]
    assert result["minimal_obstruction"]["new_invariant_needed"] is True


def test_invariant_search_accepts_exact_synthetic_debt_decrease_graph() -> None:
    graph = {
        "graph_hash": "synthetic",
        "transition_count": 1,
        "progress_transition_count": 1,
        "transitions": [
            {
                "transition_id": "synthetic_debt_decrease",
                "domain_predicate": {"d_congruence": {"minimum_d": 2}},
                "classification": {
                    "descends_below_root": False,
                    "decreases_debt": True,
                    "exits_to_finite_subsystem": False,
                    "finite_subsystem_margin_available": False,
                },
                "root_relative_margin_at_min_debt": {"gain_num_lt_gain_den": False},
            }
        ],
        "uncovered_domains_from_run067": [],
        "graph_status": "ROOT_RELATIVE_PROGRESS_PRESENT",
    }

    result = run_high_parent_invariant_search(graph=graph)

    assert result["run_result"]["status"] == "PASS"
    assert result["accepted_certificates"]
    assert result["remaining_uncovered_domains"] == []
