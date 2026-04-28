from collatz_lab.proof_action_decode import ActionCheck
from collatz_lab.proof_action_frontier_eval import _actions_from_row, _mrr, _raw_ordered_candidates
from collatz_lab.proof_action_state import state_from_residue_task
from collatz_lab.proof_action_trap_states import trap_state_row


class _DummyOutcome:
    def to_dict(self) -> dict[str, object]:
        return {"gate_progress_delta": 0.0, "closed_obligation": False}


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


def test_raw_ordering_uses_proposal_score_not_policy_only(monkeypatch) -> None:
    candidate_a = {"type": "SPLIT_RESIDUE", "target": "goal_0", "modulus": 2, "residues": [0, 1]}
    candidate_b = {"type": "UNROLL_PARITY", "target": "goal_0", "steps": 1, "parity_word": "1"}

    monkeypatch.setattr(
        "collatz_lab.proof_action_frontier_eval._actions_from_row",
        lambda row, *, beam_width: [candidate_a, candidate_b],
    )
    monkeypatch.setattr(
        "collatz_lab.proof_action_frontier_eval.score_action_components",
        lambda *args, **kwargs: [
            {"policy_score": 100.0, "ranker_score": 0.0, "value_score": 0.0},
            {"policy_score": 0.0, "ranker_score": 10.0, "value_score": 0.0},
        ],
    )
    monkeypatch.setattr(
        "collatz_lab.proof_action_frontier_eval.verify_action_for_state",
        lambda action, state: ActionCheck(False, "REJECT", "unit"),
    )
    monkeypatch.setattr(
        "collatz_lab.proof_action_frontier_eval.classify_action_outcome",
        lambda action, state, check: _DummyOutcome(),
    )

    ordered = _raw_ordered_candidates(
        model=None,
        tokenizer=None,
        row={"state": "gate=S2; target=goal_0", "candidates": []},
        max_state_len=8,
        max_action_len=8,
        beam_width=2,
        candidates_per_state=2,
        proposal_weights={"ranker_weight": 1.0, "value_weight": 0.25, "policy_weight": 0.05},
    )

    assert ordered[0]["action"] == candidate_b
    assert ordered[0]["raw_score"] > ordered[1]["raw_score"]
