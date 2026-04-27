from collatz_lab.proof_action_dataset import finite_descent_certificate
from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_outcome import (
    PARSE_VALID_BUT_REJECTED,
    VERIFIER_ACCEPTED_CLOSED_LOCAL,
    classify_action_outcome,
)
from collatz_lab.proof_action_state import state_from_finite_certificate


def test_outcome_classifies_closed_local_certificate() -> None:
    cert = finite_descent_certificate(7)
    assert cert is not None
    state = state_from_finite_certificate(cert)
    action = {"type": "CHECK_FINITE_DESCENT", "target": "goal_0", "certificate": cert}
    check = verify_action_for_state(action, state)
    outcome = classify_action_outcome(action, state, check)

    assert outcome.accepted
    assert outcome.closed_obligation
    assert outcome.outcome_class == VERIFIER_ACCEPTED_CLOSED_LOCAL
    assert outcome.closure_reward == 0.75


def test_outcome_rejected_valid_action_has_negative_reward() -> None:
    cert = finite_descent_certificate(7)
    assert cert is not None
    state = state_from_finite_certificate(cert)
    action = {"type": "CHECK_FINITE_DESCENT", "target": "goal_1", "certificate": cert}
    check = verify_action_for_state(action, state)
    outcome = classify_action_outcome(action, state, check)

    assert not outcome.accepted
    assert outcome.outcome_class == PARSE_VALID_BUT_REJECTED
    assert outcome.closure_reward == -0.5
