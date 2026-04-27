from collatz_lab.proof_action_frontier_eval import _actions_from_row, _mrr
from collatz_lab.proof_action_state import state_from_residue_task
from collatz_lab.proof_action_trap_states import trap_state_row


def test_frontier_eval_loads_labelled_candidates_from_row() -> None:
    state = state_from_residue_task(modulus=32, residue=5, steps=5, parity_word="10000")
    row = trap_state_row(state=state, gate="S2", source="unit")
    assert row is not None

    actions = _actions_from_row(row, beam_width=16)

    assert len(actions) >= 5
    assert any(action["type"] == "PROVE_AFFINE_DESCENT" for action in actions)


def test_frontier_mrr_helper() -> None:
    assert _mrr(None) == 0.0
    assert _mrr(4) == 0.25
