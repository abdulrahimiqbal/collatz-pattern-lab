from collatz_lab.proof_action_candidate_selector import candidate_utility, infer_target_objective
from collatz_lab.proof_action_candidate_selector_dataset import candidate_set_from_frontier_row


def test_candidate_selector_dataset_filters_for_gate_progress_choice(monkeypatch) -> None:
    records = [
        {"action_text": "a", "outcome_class": "ACCEPTED_NO_PROGRESS", "utility": 0.0},
        {"action_text": "b", "outcome_class": "ACCEPTED_REDUCED", "utility": 0.15},
        {"action_text": "c", "outcome_class": "ACCEPTED_DEAD_END", "utility": -0.5},
        {"action_text": "d", "outcome_class": "GATE_PROGRESS", "utility": 1.25},
        {"action_text": "e", "outcome_class": "REJECTED", "utility": -1.0},
    ]

    def fake_normalise(item, *, state, gate, target_objective):
        return records[int(item["index"])]

    monkeypatch.setattr("collatz_lab.proof_action_candidate_selector_dataset._normalise_candidate", fake_normalise)
    row = {
        "state": "state",
        "gate": "S3",
        "candidates": [{"index": index} for index in range(len(records))],
    }

    built = candidate_set_from_frontier_row(row, require_oracle_gap=0.75)

    assert built is not None
    assert built["target_objective"] == "GATE_PROGRESS"
    assert built["best_candidate_index"] == 3
    assert built["oracle_gap"] >= 0.75


def test_candidate_selector_dataset_uses_objective_candidate_not_global_gate_progress(monkeypatch) -> None:
    records = [
        {"action_text": "a", "outcome_class": "ACCEPTED_NO_PROGRESS", "utility": 0.05},
        {"action_text": "b", "outcome_class": "ACCEPTED_REDUCED", "utility": 0.5},
        {"action_text": "c", "outcome_class": "ACCEPTED_DEAD_END", "utility": -0.75},
        {"action_text": "d", "outcome_class": "CLOSED_LOCAL", "utility": 1.0},
        {"action_text": "e", "outcome_class": "REJECTED", "utility": -1.0},
    ]

    def fake_normalise(item, *, state, gate, target_objective):
        assert target_objective == "LOCAL_REDUCE"
        return records[int(item["index"])]

    monkeypatch.setattr("collatz_lab.proof_action_candidate_selector_dataset._normalise_candidate", fake_normalise)
    row = {
        "state": "state",
        "gate": "S2",
        "frontier_kind": "reduction_cases",
        "candidates": [{"index": index} for index in range(len(records))],
    }

    built = candidate_set_from_frontier_row(row, require_gate_progress_candidate=True, require_oracle_gap=0.5)

    assert built is not None
    assert built["target_objective"] == "LOCAL_REDUCE"
    assert built["best_candidate_index"] == 3


def test_target_objective_inference_and_utility_are_objective_specific() -> None:
    assert infer_target_objective({"gate": "S3"}) == "GATE_PROGRESS"
    assert infer_target_objective({"gate": "S6"}) == "S6_BLOCKER_REDUCE"
    assert infer_target_objective({"difficulty": "trap"}) == "TRAP_AVOIDANCE"
    assert infer_target_objective({"gate": "S3", "frontier_kind": "trap_states"}) == "TRAP_AVOIDANCE"
    assert candidate_utility({"outcome_class": "ACCEPTED_REDUCED"}, "LOCAL_REDUCE") == 0.5
    assert candidate_utility({"outcome_class": "ACCEPTED_REDUCED"}, "GATE_PROGRESS") == 0.10
