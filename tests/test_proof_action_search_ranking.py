from collatz_lab.proof_action_search import score_ranked_candidate


def test_search_ranking_prefers_closure_over_merely_valid_action() -> None:
    weights = {
        "verifier_accept_bonus": 10.0,
        "verifier_reject_penalty": -10.0,
        "closure_bonus": 5.0,
        "branch_close_bonus": 8.0,
        "gate_progress_weight": 10.0,
        "ranker_weight": 2.0,
        "value_weight": 1.0,
        "policy_weight": 0.2,
        "goal_creation_penalty": 0.25,
        "duplicate_action_penalty": 2.0,
    }
    valid_idle = score_ranked_candidate(
        {"ranker_score": 1.0, "value_score": 0.8, "policy_score": -0.1},
        {"accepted": True, "closed_obligation": False, "closed_branch": False, "gate_progress_delta": 0.0, "net_goal_delta": 0},
        weights,
    )
    closed = score_ranked_candidate(
        {"ranker_score": -0.5, "value_score": 0.2, "policy_score": -0.1},
        {"accepted": True, "closed_obligation": True, "closed_branch": False, "gate_progress_delta": 0.0, "net_goal_delta": 0},
        weights,
    )

    assert closed > valid_idle
