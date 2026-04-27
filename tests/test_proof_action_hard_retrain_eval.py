from collatz_lab.proof_action_hard_retrain_eval import next_bottleneck


def test_hard_retrain_next_bottleneck_prefers_s6_before_big():
    summary = {
        "original_regression": {"original_eval_regression_vs_RUN011": 0.0},
        "frontier_eval": {"raw_top5_gate_progress_rate": 0.8, "gate_delta_per_1000_calls": 0.8},
        "hard_holdout_eval": {"hard_holdout_improvement_vs_random": 4.0},
        "s6_eval": {"s6_gate_delta_per_1000_calls": 0.0, "s6_blockers_reduced": 0},
    }

    assert next_bottleneck(summary) == "S6 action generator insufficient"
