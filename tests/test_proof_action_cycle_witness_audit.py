from collatz_lab.proof_action_cycle_witness_audit import (
    audit_cycle,
    replay_cycle_witness,
)


def _edge(**overrides):
    row = {
        "edge_id": "s4:unit",
        "source": "P1",
        "target": "P1",
        "source_parent": 1,
        "target_parent": 1,
        "A": 1,
        "B": 0,
        "D": 1,
        "domain_modulus": 2,
        "domain_residue": 1,
        "minimum_q": 1,
        "branch_id": "P1:r1:d1",
        "valuation": 1,
        "transition_certificate_id": "unit",
        "transition_certificate_hash": "hash",
        "parent_coordinate_map_certificate_hash": "map_hash",
        "domain_constraints": [
            "q > 0",
            "q == 1 mod 2",
            "k = (q - 1) / 2",
            "k == 0 mod 1",
            "k != 1 mod 2",
        ],
        "all_integrality_domain_constraints": {
            "s4_domain_constraints": [
                {
                    "kind": "source_branch_residue",
                    "branch_id": "P1:r1:d1",
                    "source_parent": 1,
                    "source_residue": 1,
                    "source_depth": 1,
                    "modulus": 2,
                    "residue": 1,
                },
                {"kind": "k_divisibility", "modulus": 1, "residue": 0, "valuation": 1},
                {"kind": "excluded_next_power", "modulus": 2, "residue": 1},
            ]
        },
        "status": "PASS",
    }
    row.update(overrides)
    return row


def test_witness_replay_accepts_exact_executable_cycle() -> None:
    edge = _edge()
    witness, raw_rows = replay_cycle_witness(
        cycle_id="unit",
        edge_maps=[edge],
        q0=1,
        witness_kind="minimum_cycle_domain",
    )

    assert witness["status"] == "PASS"
    assert witness["q_final"] == "1"
    assert raw_rows[0]["status"] == "PASS"


def test_witness_replay_rejects_overapprox_cycle_domain() -> None:
    edge = _edge(domain_residue=0)
    witness, _ = replay_cycle_witness(
        cycle_id="overapprox",
        edge_maps=[edge],
        q0=2,
        witness_kind="minimum_cycle_domain",
    )

    assert witness["status"] == "FAIL"
    assert witness["failures"][0]["reason"] == "transition_domain_check_failed"


def test_repeatability_check_detects_cycle_domain_return() -> None:
    edge = _edge()
    witness, _ = audit_cycle(
        cycle_record={"cycle_id": "unit", "edge_ids": ["s4:unit"]},
        edge_maps_by_id={"s4:unit": edge},
        repeat_bound=3,
    )

    assert witness["classification"] == "EXECUTABLE_REPEATABLE_NON_DESCENDING"
    assert witness["self_return_domain"]["status"] == "PASS"
    assert len(witness["repeatability_domains"]) == 3


def test_raw_collatz_replay_catches_branch_mismatch() -> None:
    edge = _edge(B=2)
    witness, raw_rows = replay_cycle_witness(
        cycle_id="mismatch",
        edge_maps=[edge],
        q0=1,
        witness_kind="minimum_cycle_domain",
    )

    assert witness["status"] == "FAIL"
    assert witness["failures"][0]["reason"] == "raw_collatz_branch_mismatch"
    assert raw_rows[0]["status"] == "FAIL"


def test_no_floating_arithmetic_appears_in_accepted_witness() -> None:
    edge = _edge()
    witness, _ = replay_cycle_witness(
        cycle_id="unit",
        edge_maps=[edge],
        q0=1,
        witness_kind="minimum_cycle_domain",
    )

    assert witness["status"] == "PASS"
    assert witness["no_floating_arithmetic"] is True
