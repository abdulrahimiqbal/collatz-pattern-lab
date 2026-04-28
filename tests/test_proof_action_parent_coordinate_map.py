import copy

from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_parent_coordinate_map import (
    build_parent_coordinate_map_certificate,
    enrich_transition_certificate_with_parent_map,
    replay_parent_coordinate_map_certificate,
)
from collatz_lab.proof_action_parent_transition_cert import build_parent_transition_certificate
from collatz_lab.proof_action_state import canonical_state


def _action() -> dict:
    return {
        "type": "DERIVE_PARENT_TRANSITION",
        "target": "goal_0",
        "branch_id": "P1:r5:d3",
        "source_parent": 1,
        "target_parent": 3,
        "valuation": 1,
    }


def _state() -> str:
    return canonical_state(
        gate="S4_HIGH_PARENT_SUCCESSOR_FACT",
        goal="derive parent transition",
        goal_attrs={"kind": "high_parent_successor", "branch_id": "P1:r5:d3", "valuation": 1},
        assumptions=["z_family=z(k) = 2 + 3*k"],
        known_lemmas=["high_parent_successor_exactness"],
        facts=[
            {
                "kind": "high_parent_successor",
                "target": "goal_0",
                "branch_id": "P1:r5:d3",
                "source_parent": 1,
                "target_parent": 3,
                "valuation": 1,
                "sample_checks_passed": True,
            }
        ],
    )


def _row() -> dict:
    certificate = build_parent_transition_certificate(action=_action(), state=_state(), node_id="s4:unit")
    return {
        "node_id": "s4:unit",
        "action": {**_action(), "transition_certificate": certificate},
        "transition_certificate": certificate,
        "verifier_check": {"accepted": True, "status": "ACCEPT"},
    }


def test_synthetic_parent_coordinate_map_is_accepted_when_algebra_replays() -> None:
    cert = build_parent_coordinate_map_certificate(row=_row(), state=_state())
    replay = replay_parent_coordinate_map_certificate(cert)

    assert replay.accepted
    assert cert["parent_coordinate_map"]["A"] == "3"
    assert cert["parent_coordinate_map"]["B"] == "1"
    assert cert["parent_coordinate_map"]["D"] == "16"
    assert cert["parent_coordinate_map"]["target_odd_coordinate_identity"] == "q_prime = (2 + 3*k) / 2^1"


def test_wrong_parent_coordinate_map_is_rejected() -> None:
    cert = build_parent_coordinate_map_certificate(row=_row(), state=_state())
    cert["parent_coordinate_map"]["A"] = "5"
    cert["certificate_hash"] = "stale"

    replay = replay_parent_coordinate_map_certificate(cert)

    assert not replay.accepted
    assert any(failure["reason"] in {"parent_coordinate_map_payload_mismatch", "parent_coordinate_map_hash_mismatch"} for failure in replay.failures or [])


def test_missing_integrality_constraint_is_rejected() -> None:
    cert = build_parent_coordinate_map_certificate(row=_row(), state=_state())
    cert["parent_coordinate_map"]["domain_constraints"] = ["q > 0"]
    cert["certificate_hash"] = "stale"

    replay = replay_parent_coordinate_map_certificate(cert)

    assert not replay.accepted
    assert any(failure["reason"] == "parent_coordinate_map_payload_mismatch" for failure in replay.failures or [])


def test_nonpositive_or_wrong_shift_map_is_rejected() -> None:
    cert = build_parent_coordinate_map_certificate(row=_row(), state=_state())
    cert["parent_coordinate_map"]["B"] = "-17"
    cert["certificate_hash"] = "stale"

    replay = replay_parent_coordinate_map_certificate(cert)

    assert not replay.accepted
    assert any(failure["reason"] == "parent_coordinate_map_payload_mismatch" for failure in replay.failures or [])


def test_sample_only_transition_is_rejected() -> None:
    cert = build_parent_coordinate_map_certificate(
        row={"node_id": "s4:unit", "action": _action(), "verifier_check": {"accepted": True, "status": "ACCEPT"}},
        state=_state(),
    )
    replay = replay_parent_coordinate_map_certificate(cert)

    assert not replay.accepted
    assert cert["status"] == "FAIL"


def test_certificate_hash_mutation_is_rejected() -> None:
    cert = build_parent_coordinate_map_certificate(row=_row(), state=_state())
    mutated = copy.deepcopy(cert)
    mutated["certificate_hash"] = "deadbeef"

    replay = replay_parent_coordinate_map_certificate(mutated)

    assert not replay.accepted
    assert any(failure["reason"] == "parent_coordinate_map_hash_mismatch" for failure in replay.failures or [])


def test_map_enriched_transition_replays_through_action_verifier() -> None:
    row = _row()
    map_cert = build_parent_coordinate_map_certificate(row=row, state=_state())
    enriched = enrich_transition_certificate_with_parent_map(row["transition_certificate"], map_cert)
    action = {**_action(), "transition_certificate": enriched}

    check = verify_action_for_state(action, _state())

    assert check.accepted
