from collatz_lab.proof_action_hard_retrain_eval import next_bottleneck


def test_forgetting_regression_blocks_big_model_decision():
    summary = {
        "original_regression": {"original_eval_regression_vs_RUN011": 0.2},
        "frontier_eval": {"raw_top5_gate_progress_rate": 1.0, "gate_delta_per_1000_calls": 1.0},
        "hard_holdout_eval": {"hard_holdout_improvement_vs_random": 999.0},
        "s6_eval": {"s6_gate_delta_per_1000_calls": 1.0, "s6_blockers_reduced": 2},
    }

    assert next_bottleneck(summary) == "catastrophic forgetting"
