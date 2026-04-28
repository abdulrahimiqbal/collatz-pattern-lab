import copy
import json
from pathlib import Path

from collatz_lab.proof_action_guarded_domain import (
    AffineMap,
    GuardedDomain,
    ResidueClass,
    add_non_congruence,
    contains_float,
    domain_self_invariance,
    replay_guarded_edge_domain_row,
)
from collatz_lab.proof_action_guarded_scc_ranking import classify_guarded_cycle


def test_coarse_return_failing_excluded_next_power_is_not_repeatable() -> None:
    domain = GuardedDomain(ResidueClass(1, 4), lower_bound=1)
    guarded = add_non_congruence(domain, ResidueClass(5, 8, kind="non_congruence", source="excluded_next_power"))
    assert guarded is not None

    replay = domain_self_invariance(guarded, AffineMap(1, 4, 1))

    assert replay["status"] == "FAIL"
    assert any(failure["guard"] == "non_congruence" for failure in replay["failures"])


def test_expected_q_not_integral_repeat_is_guarded_exit() -> None:
    edge = {
        "edge_id": "e",
        "source": "P1",
        "target": "P1",
        "affine_map": {"A": "3", "B": "1", "D": "2"},
        "guarded_domain": GuardedDomain(ResidueClass(0, 2), lower_bound=1).to_json(),
        "status": "PASS",
    }
    cycle = {"cycle_id": "c", "edge_ids": ["e"], "source_states": ["P1"]}

    row = classify_guarded_cycle(cycle_record=cycle, guarded_edges={"e": edge}, repeat_cap=1, compute_repeat_prefix=False)

    assert row["classification"] == "GUARDED_TRANSIENT_EXIT"
    assert row["full_domain_self_invariance"]["status"] == "FAIL"


def test_full_guarded_self_map_synthetic_cycle_is_repeatable() -> None:
    domain = GuardedDomain(ResidueClass(1, 4), lower_bound=1)
    guarded = add_non_congruence(domain, ResidueClass(3, 8, kind="non_congruence", source="excluded_next_power"))
    assert guarded is not None

    replay = domain_self_invariance(guarded, AffineMap(1, 8, 1))

    assert replay["status"] == "PASS"


def test_missing_non_congruence_guard_makes_replay_fail() -> None:
    row = {
        "schema": "collatz_lab.guarded_edge_domain",
        "version": 1,
        "edge_id": "e",
        "guarded_domain": GuardedDomain(ResidueClass(1, 2), lower_bound=1).to_json(),
        "guard_components": {"valuation_exactness": {"valuation": "0"}},
        "replay_checks": {
            "parent_coordinate_map_certificate_replays": True,
            "branch_guard_present": True,
            "k_divisibility_present": True,
            "excluded_next_power_present": True,
            "map_integrality_present": True,
            "valuation_exactness_present": True,
            "not_status_or_id_only": True,
            "no_floats": True,
        },
        "status": "PASS",
    }
    from collatz_lab.proof_action_guarded_domain import stable_hash

    row["guarded_domain_hash"] = stable_hash({key: value for key, value in row.items() if key != "guarded_domain_hash"})

    replay = replay_guarded_edge_domain_row(row)

    assert not replay["accepted"]
    assert any(failure["reason"] == "missing_non_congruence_guard" for failure in replay["failures"])


def test_no_floats_accepted() -> None:
    assert contains_float({"rank": 1.25})
