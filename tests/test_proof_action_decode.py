from collatz_lab.proof_action_dataset import finite_descent_certificate
from collatz_lab.proof_action_decode import (
    is_degenerate_output,
    legal_action_candidates_from_state,
    verify_action_for_state,
)
from collatz_lab.proof_action_state import state_from_finite_certificate, state_from_residue_task


def test_finite_descent_action_verifies_against_state() -> None:
    cert = finite_descent_certificate(3)
    assert cert is not None
    state = state_from_finite_certificate(cert)
    action = {"type": "CHECK_FINITE_DESCENT", "target": "goal_0", "certificate": cert}

    assert verify_action_for_state(action, state).accepted


def test_residue_affine_candidate_is_legal_and_accepted() -> None:
    state = state_from_residue_task(modulus=16, residue=5, steps=4, parity_word="1000")
    candidates = legal_action_candidates_from_state(state)
    affine = next(row for row in candidates if row["type"] == "PROVE_AFFINE_DESCENT")

    assert verify_action_for_state(affine, state).accepted


def test_decode_rejects_wrong_target_and_degenerate_text() -> None:
    cert = finite_descent_certificate(5)
    assert cert is not None
    state = state_from_finite_certificate(cert)
    action = {"type": "CHECK_FINITE_DESCENT", "target": "goal_1", "certificate": cert}

    assert not verify_action_for_state(action, state).accepted
    assert is_degenerate_output("<<<<<<<<<<<<")


def test_s6_candidate_generator_does_not_emit_missing_certificate_actions() -> None:
    state = """<GATE>S6_PROOF_REPLAY_REPAIR</GATE>
<GOAL id="goal_0" kind="proof_replay">repair strict theorem frontier</GOAL>
<KNOWN_LEMMAS>
strict_verifier_blocks_confidence
</KNOWN_LEMMAS>
<OPEN_OBLIGATIONS>
goal_0
</OPEN_OBLIGATIONS>"""

    candidates = legal_action_candidates_from_state(state)
    serialized = [str(candidate) for candidate in candidates]

    assert not any("_missing" in candidate for candidate in serialized)
    assert any(candidate["type"] == "PROVE_GLOBAL_DESCENT_INDUCTION" for candidate in candidates)
    assert all(verify_action_for_state(candidate, state).accepted for candidate in candidates if candidate["type"] in {"PROPOSE_S6_LEMMA", "PROVE_GLOBAL_DESCENT_INDUCTION"})
