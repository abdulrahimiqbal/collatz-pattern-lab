from fractions import Fraction

from collatz_lab.proof_action_guarded_domain import AffineMap, GuardedDomain, ResidueClass, add_non_congruence
from collatz_lab.proof_action_guarded_viability_kernel import (
    check_fraction_in_guarded_domain,
    fixed_point_for_cycle_map,
    replay_viability_kernel_witness,
)


def test_2adic_fixed_point_inside_guarded_domain_is_survivor() -> None:
    fixed = fixed_point_for_cycle_map(AffineMap(3, 1, 2))
    assert fixed == Fraction(-1, 1)
    domain = add_non_congruence(
        GuardedDomain(ResidueClass(3, 4), lower_bound=1),
        ResidueClass(1, 8, kind="non_congruence", source="excluded_next_power"),
    )
    assert domain is not None

    check = check_fraction_in_guarded_domain(fixed, domain)

    assert check["status"] == "PASS"
    assert check["natural_number_status"] == "NON_NATURAL_2ADIC"


def test_2adic_fixed_point_hitting_excluded_residue_is_rejected() -> None:
    fixed = fixed_point_for_cycle_map(AffineMap(3, 1, 2))
    domain = add_non_congruence(
        GuardedDomain(ResidueClass(3, 4), lower_bound=1),
        ResidueClass(7, 8, kind="non_congruence", source="excluded_next_power"),
    )
    assert domain is not None

    check = check_fraction_in_guarded_domain(fixed, domain)

    assert check["status"] == "FAIL"
    assert any(failure["reason"] == "fixed_point_hits_excluded_residue" for failure in check["failures"])


def test_viability_witness_hash_mutation_fails_replay() -> None:
    domain = GuardedDomain(ResidueClass(3, 4), lower_bound=1)
    witness = {
        "cycle_id": "c",
        "edge_ids": ["e"],
        "source_states": ["P1"],
        "status": "PASS",
        "classification": "NON_NATURAL_2ADIC_SURVIVING_KERNEL",
        "composed_map": {"A": "3", "B": "1", "D": "2"},
        "guarded_cycle_domain": domain.to_json(),
        "fixed_point": {"numerator": "-1", "denominator": "1"},
        "fixed_point_guard_check": check_fraction_in_guarded_domain(Fraction(-1, 1), domain),
    }
    from collatz_lab.proof_action_guarded_domain import stable_hash

    witness["witness_hash"] = stable_hash({key: value for key, value in witness.items() if key != "witness_hash"})
    witness["cycle_id"] = "mutated"

    replay = replay_viability_kernel_witness(witness)

    assert not replay["accepted"]
    assert any(failure["reason"] == "viability_witness_hash_mismatch" for failure in replay["failures"])

