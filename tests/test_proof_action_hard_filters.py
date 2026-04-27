from collatz_lab.proof_action_hard_filters import is_hard_positive_trace


def test_hard_filter_accepts_long_frontier_progress():
    trace = {
        "gate": "S6",
        "depth": 9,
        "actions": [
            {"action": '{"type":"PROPOSE_S6_LEMMA"}', "verifier_status": "ACCEPT", "gate_progress_delta": 0.0}
            for _ in range(8)
        ]
        + [{"action": '{"type":"CLOSE_STRICT_THEOREM_BLOCKER"}', "verifier_status": "ACCEPT", "gate_progress_delta": 1.0}],
        "closed_obligation": True,
        "closed_branch": False,
        "gate_progress_total": 1.0,
        "one_step_close_from_start": False,
        "baseline_random_success_at_same_budget": False,
        "baseline_heuristic_success_at_same_budget": False,
        "novelty": {"exact_state_overlap": False, "near_duplicate_trace": False},
    }
    result = is_hard_positive_trace(trace)
    assert result.accepted
    assert "frontier_progress" in result.reasons


def test_hard_filter_rejects_one_step_local_closure():
    trace = {
        "gate": "S2",
        "depth": 1,
        "actions": [{"action": "{}", "verifier_status": "ACCEPT"}],
        "closed_obligation": True,
        "gate_progress_total": 0.0,
        "one_step_close_from_start": True,
        "baseline_random_success_at_same_budget": True,
    }
    result = is_hard_positive_trace(trace)
    assert not result.accepted
    assert "not_frontier_gate" in result.rejects
