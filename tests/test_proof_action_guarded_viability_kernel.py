from fractions import Fraction

from collatz_lab.proof_action_guarded_domain import AffineMap, GuardedDomain, ResidueClass, add_non_congruence
from collatz_lab.proof_action_guarded_viability_kernel import (
    build_empty_viability_certificate,
    build_one_step_partition,
    check_fraction_in_guarded_domain,
    eliminate_nonviable_graph_pieces,
    exact_domain_difference_partition,
    exact_domain_intersection,
    fixed_point_for_cycle_map,
    replay_empty_viability_certificate,
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


def test_exact_domain_difference_partitions_power_two_cylinders() -> None:
    domain = GuardedDomain(ResidueClass(1, 2), lower_bound=1)
    removed = GuardedDomain(ResidueClass(1, 8), lower_bound=1)

    pieces = exact_domain_difference_partition(domain, [removed])

    assert [piece.congruence.to_json() for piece in pieces] == [
        {"kind": "congruence", "modulus": "4", "residue": "3", "source": "difference::"},
        {"kind": "congruence", "modulus": "8", "residue": "5", "source": "difference::"},
    ]


def test_exact_domain_intersection_combines_congruence_and_exclusion() -> None:
    left = GuardedDomain(ResidueClass(1, 2), lower_bound=1)
    right = add_non_congruence(
        GuardedDomain(ResidueClass(1, 4), lower_bound=1),
        ResidueClass(5, 8, kind="non_congruence", source="excluded"),
    )
    assert right is not None

    intersection = exact_domain_intersection(left, right)

    assert intersection is not None
    assert intersection.congruence.residue == 1
    assert intersection.congruence.modulus == 4
    assert len(intersection.non_congruences) == 1


def test_empty_viability_certificate_replay_accepts_decreasing_ranks() -> None:
    pieces = set()
    elimination = eliminate_nonviable_graph_pieces(piece_ids=pieces, graph_edges=[])
    certificate = build_empty_viability_certificate(
        states=["P1"],
        edge_ids=["e"],
        pieces=[],
        graph_edges=[],
        elimination=elimination,
    )

    replay = replay_empty_viability_certificate(certificate)

    assert replay["accepted"]


def test_one_step_partition_records_guard_exit_piece() -> None:
    guarded_edges = {
        "e0": {
            "edge_id": "e0",
            "source": "P1",
            "target": "P2",
            "affine_map": {"A": "1", "B": "0", "D": "1"},
            "guarded_domain": GuardedDomain(ResidueClass(1, 2), lower_bound=1).to_json(),
            "status": "PASS",
        },
        "e1": {
            "edge_id": "e1",
            "source": "P2",
            "target": "P3",
            "affine_map": {"A": "1", "B": "0", "D": "1"},
            "guarded_domain": GuardedDomain(ResidueClass(1, 4), lower_bound=1).to_json(),
            "status": "PASS",
        },
    }

    partition = build_one_step_partition(guarded_edges)
    classes = {piece.piece_class for piece in partition["pieces"]}

    assert "STAYS_IN_SCC" in classes
    assert "GUARD_EXIT" in classes
