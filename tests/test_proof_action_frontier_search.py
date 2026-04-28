from collatz_lab.proof_action_frontier_search import (
    _budget_improvement_fields,
    _budget_to_rate,
    _dataset_order,
    _event_from_order,
    _heuristic_order,
    _model_pre_verifier_order,
    _speedup_budget_to_rate,
    passes_run015a_gates,
    passes_run012_gates,
)
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


def test_model_pre_verifier_order_does_not_verify_before_ordering(monkeypatch) -> None:
    candidate_a = {"type": "SPLIT_RESIDUE", "target": "goal_0", "modulus": 2, "residues": [0, 1]}
    candidate_b = {"type": "UNROLL_PARITY", "target": "goal_0", "steps": 1, "parity_word": "1"}

    monkeypatch.setattr(
        "collatz_lab.proof_action_frontier_search._actions_from_row",
        lambda row, *, beam_width: [candidate_a, candidate_b],
    )
    monkeypatch.setattr(
        "collatz_lab.proof_action_frontier_search.score_action_components",
        lambda *args, **kwargs: [
            {"policy_score": 100.0, "ranker_score": 0.0, "value_score": 0.0},
            {"policy_score": 0.0, "ranker_score": 10.0, "value_score": 0.0},
        ],
    )

    def fail_if_verified(*args, **kwargs):
        raise AssertionError("verifier must not run during model pre-verifier ordering")

    monkeypatch.setattr("collatz_lab.proof_action_frontier_search.verify_action_for_state", fail_if_verified)

    ordered = _model_pre_verifier_order(
        model=None,
        tokenizer=None,
        row={"state": "gate=S2; target=goal_0"},
        max_state_len=8,
        max_action_len=8,
        beam_width=2,
        candidates_per_state=2,
        proposal_weights={"ranker_weight": 1.0, "value_weight": 0.25, "policy_weight": 0.05},
    )

    assert ordered[0]["action"] == candidate_b


def test_heuristic_order_is_independent_of_dataset_order(monkeypatch) -> None:
    low = {"type": "SPLIT_RESIDUE", "target": "goal_0", "modulus": 2, "residues": [0, 1]}
    high = {"type": "DERIVE_PARENT_TRANSITION", "target": "goal_0", "branch_id": "b", "source_parent": 1, "target_parent": 2, "valuation": 1}
    monkeypatch.setattr("collatz_lab.proof_action_frontier_search._actions_from_row", lambda row, *, beam_width: [low, high])

    row = {"state": "state"}

    assert _dataset_order(row, beam_width=2)[0]["action"] == low
    assert _heuristic_order(row, beam_width=2)[0]["action"] == high


def test_budget_improvement_fields_cover_early_budgets() -> None:
    budgets = [5, 10, 25, 50, 100]
    model_summary = {f"closure_at_{budget}_calls": 0.5 for budget in budgets}
    random_summary = {f"closure_at_{budget}_calls": 0.25 for budget in budgets}
    heuristic_summary = {f"closure_at_{budget}_calls": 0.1 for budget in budgets}

    fields = _budget_improvement_fields(
        model_summary=model_summary,
        random_summary=random_summary,
        heuristic_summary=heuristic_summary,
        budgets=budgets,
    )

    for budget in budgets:
        assert fields[f"improvement_vs_random_at_{budget}_calls"] == 2.0
        assert fields[f"improvement_vs_heuristic_at_{budget}_calls"] == 5.0


def test_budget_to_rate_tracks_saturation_speedup() -> None:
    budgets = [5, 10, 25]
    model = {"closure_at_5_calls": 0.85}
    random = {"closure_at_5_calls": 0.1, "closure_at_10_calls": 0.5, "closure_at_25_calls": 0.9}

    assert _budget_to_rate(model, budgets, target_rate=0.8) == 5
    assert _budget_to_rate(random, budgets, target_rate=0.8) == 25
    assert _speedup_budget_to_rate(model, random, budgets, target_rate=0.8) == 5.0


def test_go_gate_uses_early_budget_not_1000_call_saturation() -> None:
    summary = {
        "closure_at_25_calls": 0.25,
        "gate_delta_per_100_calls": 0.1,
        "s3_gate_delta_per_1000_calls": 0.1,
        "s4_gate_delta_per_1000_calls": 0.1,
        "improvement_vs_random_at_25_calls": 3.0,
        "improvement_vs_heuristic_at_25_calls": 2.0,
        "improvement_vs_random_at_1000_calls": 0.0,
    }
    raw = {
        "raw_top5_verifier_accept_rate": 0.5,
        "raw_top5_gate_progress_rate": 0.66,
        "raw_mrr_first_gate_progress_action": 0.51,
    }
    leakage = {"exact_state_hash_overlap": 0}

    assert passes_run012_gates(summary, raw, leakage)


def test_run015a_gate_uses_oracle_normalized_metrics_and_saturation() -> None:
    summary = {
        "model_budget_to_80pct_closure": 5,
        "random_budget_to_80pct_closure": 25,
        "heuristic_budget_to_80pct_closure": 5,
        "speedup_to_80pct_vs_random": 5.0,
        "improvement_vs_random_at_25_calls": 1.0,
        "baseline_saturates_by_25_calls": True,
        "s3_gate_delta_per_1000_calls": 0.1,
        "s4_gate_delta_per_1000_calls": 0.1,
        "s6_gate_delta_per_1000_calls": 0.1,
    }
    raw = {
        "oracle_gate_progress_available_rate": 0.712,
        "raw_top5_gate_progress_rate": 0.712,
        "raw_mrr_first_gate_progress_action": 0.698,
        "selector_top5_gate_progress_oracle_recall": 1.0,
        "selector_mrr_gate_progress_oracle_normalized": 0.98,
        "normalized_policy_regret": 0.056,
        "oracle_available_rate_by_objective": {"GATE_PROGRESS": 0.884, "S6_BLOCKER_REDUCE": 1.0},
    }
    leakage = {"exact_state_hash_overlap": 0}

    assert passes_run015a_gates(summary, raw, leakage)
