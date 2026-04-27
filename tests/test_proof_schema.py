import pytest

from collatz_lab.proof_schema import ProofObligation, ProofState, Transition, status_is_closed


def test_proof_schema_round_trip() -> None:
    state = ProofState("P_6", "parent_state", {"a": 6})
    transition = Transition("t", "P_6", "P_6", A=729, B=1, D=128)
    obligation = ProofObligation("o", "NEEDS_SPLIT", "scope", "claim")
    assert state.to_dict()["parameters"]["a"] == 6
    assert transition.to_dict()["D"] == 128
    assert obligation.is_closed is False
    assert status_is_closed("CLOSED_BY_HEIGHT_RANKING") is True


def test_proof_schema_rejects_bad_status() -> None:
    with pytest.raises(ValueError):
        ProofObligation("o", "MAYBE", "scope", "claim")
