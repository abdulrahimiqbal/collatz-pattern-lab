from collatz_lab.proof_action_frontier_search import _event_from_order, _heuristic_order
from collatz_lab.proof_action_state import state_from_residue_task
from collatz_lab.proof_action_trap_states import trap_state_row


def test_frontier_search_event_tracks_budget_hits() -> None:
    state = state_from_residue_task(modulus=32, residue=5, steps=5, parity_word="10000")
    row = trap_state_row(state=state, gate="S2", source="unit")
    assert row is not None

    order = _heuristic_order(row, beam_width=16)
    event = _event_from_order(row, order, [1, 10, 100])

    assert event["accepted_actions"] >= 1
    assert "10" in event["budget_hits"]
    assert event["closed"] or event["dead_end"] or event["branch_explosion"]
