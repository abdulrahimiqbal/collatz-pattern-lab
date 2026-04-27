import pytest

from collatz_lab.proof_actions import ProofAction, action_from_dict


def test_proof_action_round_trip() -> None:
    action = ProofAction(
        action="TRY_ADIC_BASIN",
        params={"form": {"u": 601, "v": 1}},
        score=0.9,
        rationale="sharp branch",
    )
    loaded = action_from_dict(action.to_dict())
    assert loaded == action
    assert "TRY_ADIC_BASIN" in action.to_json()


def test_proof_action_rejects_unknown_action() -> None:
    with pytest.raises(ValueError):
        ProofAction(action="DO_MAGIC")
