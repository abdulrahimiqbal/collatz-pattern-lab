from collatz_lab.proof_action_state import state_from_residue_task
from collatz_lab.proof_action_trap_states import labelled_candidates_for_state, trap_state_row


def test_trap_state_has_accepted_dead_ends_and_progress() -> None:
    state = state_from_residue_task(modulus=32, residue=5, steps=5, parity_word="10000")
    candidates = labelled_candidates_for_state(state)
    trap = trap_state_row(state=state, gate="S2", source="unit")

    assert trap is not None
    assert sum(1 for item in candidates if item["verifier_status"] == "ACCEPT") >= 5
    assert any(item["downstream_outcome"] in {"CLOSED", "GATE_PROGRESS"} for item in trap["candidates"])
    assert sum(1 for item in trap["candidates"] if item["downstream_outcome"] in {"DEAD_END", "BRANCH_EXPLOSION"}) >= 3
