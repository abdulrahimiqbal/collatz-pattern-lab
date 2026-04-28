import json

from collatz_lab.proof_action_candidate_selector_eval import candidate_set_oracle_metrics, selector_go_no_go


def test_selector_go_gate_requires_oracle_pool_and_selector_metrics() -> None:
    summary = {
        "raw_proposal_metrics": {
            "oracle_gate_progress_available_rate": 0.712,
            "oracle_available_rate_by_objective": {
                "GATE_PROGRESS": 0.884,
                "S6_BLOCKER_REDUCE": 1.0,
                "TRAP_AVOIDANCE": 0.8,
            },
            "raw_top5_gate_progress_rate": 0.712,
            "raw_mrr_first_gate_progress_action": 0.698,
            "mean_policy_regret": 0.049,
            "selector_top5_gate_progress_oracle_recall": 1.0,
            "selector_mrr_gate_progress_oracle_normalized": 0.98,
            "normalized_policy_regret": 0.056,
        },
        "candidate_selector_hard_holdout_oracle_available_rate": 0.95,
        "model_budget_to_80pct_closure": 5,
        "random_budget_to_80pct_closure": 25,
        "heuristic_budget_to_80pct_closure": 5,
        "speedup_to_80pct_vs_random": 5.0,
        "speedup_to_80pct_vs_heuristic": 1.0,
        "improvement_vs_random_at_25_calls": 1.0,
        "improvement_vs_heuristic_at_25_calls": 1.0,
        "baseline_saturates_by_25_calls": True,
        "s3_gate_delta_per_1000_calls": 0.1,
        "s4_gate_delta_per_1000_calls": 0.1,
        "s6_gate_delta_per_1000_calls": 0.1,
        "leakage_report": {"exact_state_hash_overlap": 0},
    }

    assert selector_go_no_go(summary)

    summary["raw_proposal_metrics"]["raw_top5_gate_progress_rate"] = 0.1
    assert selector_go_no_go(summary)

    summary["raw_proposal_metrics"]["selector_top5_gate_progress_oracle_recall"] = 0.94
    assert not selector_go_no_go(summary)


def test_candidate_set_oracle_metrics_use_target_objective(tmp_path) -> None:
    path = tmp_path / "hard_holdout_candidate_sets.jsonl"
    rows = [
        {
            "target_objective": "LOCAL_REDUCE",
            "candidates": [
                {"action_text": "a", "outcome_class": "ACCEPTED_NO_PROGRESS", "utility": 0.05},
                {"action_text": "b", "outcome_class": "ACCEPTED_REDUCED", "utility": 0.5},
            ],
        },
        {
            "target_objective": "GATE_PROGRESS",
            "candidates": [
                {"action_text": "a", "outcome_class": "ACCEPTED_REDUCED", "utility": 0.1},
                {"action_text": "b", "outcome_class": "GATE_PROGRESS", "utility": 1.25},
            ],
        },
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    metrics = candidate_set_oracle_metrics(path)

    assert metrics["oracle_available_rate"] == 1.0
    assert metrics["oracle_available_rate_by_objective"]["LOCAL_REDUCE"] == 1.0
    assert metrics["oracle_available_rate_by_objective"]["GATE_PROGRESS"] == 1.0
