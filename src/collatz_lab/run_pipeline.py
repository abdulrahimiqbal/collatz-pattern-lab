"""Refresh/orchestration CLI for Collatz proof-discovery runs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console

from .lifted_postprocess import summarize_lifted_certificates, summarize_lifted_certificates_file
from .proof_attempt import (
    append_proof_attempt_record_to_logs,
    build_proof_attempt_record,
    write_evaluation_markdown,
    write_proof_attempt_markdown,
)
from .proof_attempt_search import build_ranked_proof_attempts, summarize_ranked_attempts
from .run_result import (
    RunResult,
    append_run_to_runs_md,
    build_proof_score,
    load_json,
    recommend_next_step,
    save_run_result,
    summarize_eval_files,
    summarize_proof_graph,
    summarize_verification_file,
    utc_stamp,
    write_run_result_markdown,
)
from .utils import load_jsonl


BASELINE_RUN_ID = "RUN-000-current-baseline"
RUN001_ID = "RUN-001-a10g-reference"


BASELINE_EVALS = {
    "id_bits48_signed_100k": "remote_reports/signed_reference/20260424_222430_multitask_base24_eval_id_bits48_signed_100k.json",
    "residue_holdout_bits48_100k": "remote_reports/signed_reference/20260424_222430_multitask_base24_eval_residue_holdout_bits48_100k.json",
    "ood_bits56_positive_100k": "remote_reports/signed_reference/20260424_222430_multitask_base24_eval_ood_bits56_positive_100k.json",
    "ood_bits56_negative_100k": "remote_reports/signed_reference/20260424_222430_multitask_base24_eval_ood_bits56_negative_100k.json",
    "ood_bits64_positive_100k": "remote_reports/signed_reference/20260424_222430_multitask_base24_eval_ood_bits64_positive_100k.json",
    "ood_bits64_negative_100k": "remote_reports/signed_reference/20260424_222430_multitask_base24_eval_ood_bits64_negative_100k.json",
    "hard_positive_bits56_100k": "remote_reports/signed_reference/20260424_222430_multitask_base24_eval_hard_positive_bits56_100k.json",
}

BASELINE_VERIFICATIONS = {
    "hard_positive_dataset": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_verification_hard_positive_dataset.json",
    "hard_positive_model_cluster": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_verification_hard_positive_model_cluster.json",
    "hard_positive_lifted": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_verification_hard_positive_lifted.json",
}

BASELINE_CANDIDATES = {
    "hard_positive_dataset": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_candidates_hard_positive_dataset.jsonl",
    "hard_positive_model_cluster": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_candidates_hard_positive_model_cluster.jsonl",
    "hard_positive_lifted": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_candidates_hard_positive_lifted.jsonl",
}

BASELINE_PROBES = {
    "residue_holdout_bits48": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_probes_residue_holdout_bits48.json",
    "hard_positive_bits56": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_probes_hard_positive_bits56.json",
}


def _existing_paths(root: Path, paths: dict[str, str]) -> dict[str, Path]:
    return {name: root / path for name, path in paths.items() if (root / path).exists()}


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return len(load_jsonl(path))


def _parse_named_paths(values: list[str]) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Expected NAME=PATH, got {value!r}")
        name, path = value.split("=", 1)
        parsed[name] = Path(path)
    return parsed


def _write_result_bundle(
    result: RunResult,
    out_root: Path,
    runs_md: Path | None = None,
    append_runs: bool = False,
) -> dict[str, str]:
    run_dir = out_root / result.run_id
    json_path = run_dir / "run_result.json"
    md_path = run_dir / "run_result.md"
    save_run_result(result, json_path)
    write_run_result_markdown(result, md_path)
    if append_runs and runs_md is not None:
        append_run_to_runs_md(result, runs_md)
    return {"json": str(json_path), "markdown": str(md_path)}


def build_run_result_from_artifacts(
    run_id: str,
    title: str,
    config_path: str | None,
    checkpoint_path: str | None,
    eval_paths: dict[str, Path],
    verification_paths: dict[str, Path],
    candidate_paths: dict[str, Path] | None = None,
    probe_paths: dict[str, Path] | None = None,
    lifted_verification_path: Path | None = None,
    compression_path: Path | None = None,
    theorem_candidate_path: Path | None = None,
    proof_graph_path: Path | None = None,
    proof_policy_report_path: Path | None = None,
    proof_action_eval_path: Path | None = None,
    frontier_search_eval_path: Path | None = None,
    hard_trace_mining_path: Path | None = None,
    hard_retrain_eval_path: Path | None = None,
    proof_attempt_path: Path | None = None,
    proof_evaluation_path: Path | None = None,
    commands: list[str] | None = None,
    artifacts: dict[str, str] | None = None,
    notes: list[str] | None = None,
) -> RunResult:
    eval_metrics = summarize_eval_files(eval_paths)
    verification_metrics = {
        name: summarize_verification_file(path)
        for name, path in verification_paths.items()
        if path.exists()
    }
    discovery_metrics: dict[str, Any] = {}
    if candidate_paths:
        discovery_metrics["candidate_counts"] = {
            name: _count_jsonl(path)
            for name, path in candidate_paths.items()
        }
    if probe_paths:
        discovery_metrics["probes"] = {
            name: _load_optional_json(path)
            for name, path in probe_paths.items()
            if path.exists()
        }

    postprocess_metrics: dict[str, Any] = {}
    if lifted_verification_path and lifted_verification_path.exists():
        compression = _load_optional_json(compression_path) if compression_path else None
        rows = json.loads(lifted_verification_path.read_text(encoding="utf-8"))
        postprocess_metrics = summarize_lifted_certificates(rows, compression)

    theorem_candidate = _load_optional_json(theorem_candidate_path) if theorem_candidate_path else None
    proof_graph = _load_optional_json(proof_graph_path) if proof_graph_path else None
    proof_policy_report = _load_optional_json(proof_policy_report_path) if proof_policy_report_path else None
    proof_action_eval = _load_optional_json(proof_action_eval_path) if proof_action_eval_path else None
    frontier_search_eval = _load_optional_json(frontier_search_eval_path) if frontier_search_eval_path else None
    hard_trace_mining = _load_optional_json(hard_trace_mining_path) if hard_trace_mining_path else None
    hard_retrain_eval = _load_optional_json(hard_retrain_eval_path) if hard_retrain_eval_path else None
    score_policy_report = proof_policy_report
    proof_attempt = _load_optional_json(proof_attempt_path) if proof_attempt_path else None
    proof_evaluation = _load_optional_json(proof_evaluation_path) if proof_evaluation_path else None
    if proof_action_eval:
        score_policy_report = {
            **proof_action_eval,
            "proof_progress_percent": 100.0 * float(proof_action_eval.get("heldout_obligation_close_rate", 0.0) or 0.0),
        }
        discovery_metrics["proof_action_eval"] = {
            key: proof_action_eval.get(key)
            for key in (
                "syntax_valid_rate",
                "action_parse_rate",
                "degenerate_output_rate",
                "unique_actions_per_state_mean",
                "top1_verifier_accept_rate",
                "top5_verifier_accept_rate",
                "top5_accept_lift",
                "top1_close_rate",
                "top5_close_rate",
                "top5_close_lift",
                "trace_replay_close_rate",
                "heldout_obligation_close_rate",
                "random_legal_action_close_rate",
                "heuristic_legal_action_close_rate",
                "heldout_close_vs_random",
                "heldout_close_vs_heuristic",
                "gate_close_counts",
                "gate_progress_counts",
                "strict_theorem_verifier_result",
                "proof_confidence_percent",
                "model_discovery_score_percent",
                "go_no_go",
            )
        }
    if proof_policy_report and proof_policy_report.get("proof_progress_breakdown"):
        discovery_metrics["proof_progress_metric"] = proof_policy_report.get("proof_progress_metric")
        discovery_metrics["proof_progress_breakdown"] = proof_policy_report["proof_progress_breakdown"]
    if frontier_search_eval:
        raw = frontier_search_eval.get("raw_proposal_metrics") or {}
        discovery_metrics["proof_action_frontier_search"] = {
            key: frontier_search_eval.get(key)
            for key in (
                "closure_at_100_calls",
                "closure_at_1000_calls",
                "gate_delta_per_1000_calls",
                "s3_gate_delta_per_1000_calls",
                "s4_gate_delta_per_1000_calls",
                "s6_gate_delta_per_1000_calls",
                "trap_state_success_rate",
                "trap_state_dead_end_rate",
                "improvement_vs_random_at_1000_calls",
                "improvement_vs_heuristic_at_1000_calls",
                "strict_theorem_verifier_result",
                "proof_confidence_percent",
                "go_no_go",
            )
        } | {
            "raw_model_top1_accept_rate": raw.get("raw_top1_verifier_accept_rate"),
            "raw_model_top5_accept_rate": raw.get("raw_top5_verifier_accept_rate"),
            "raw_model_top10_accept_rate": raw.get("raw_top10_verifier_accept_rate"),
            "raw_model_top1_close_rate": raw.get("raw_top1_close_or_reduce_rate"),
            "raw_model_top5_close_rate": raw.get("raw_top5_close_or_reduce_rate"),
            "raw_model_top10_close_rate": raw.get("raw_top10_close_or_reduce_rate"),
            "raw_model_top5_gate_progress_rate": raw.get("raw_top5_gate_progress_rate"),
            "raw_mrr_first_gate_progress_action": raw.get("raw_mrr_first_gate_progress_action"),
        }
    if hard_trace_mining:
        gate_counts = hard_trace_mining.get("gate_counts") or {}
        baseline = hard_trace_mining.get("baseline_comparison") or {}
        leakage = hard_trace_mining.get("leakage_report") or {}
        filter_summary = hard_trace_mining.get("hard_positive_filter_summary") or {}
        discovery_metrics["proof_action_hard_trace_mining"] = {
            "mined_hard_traces_count": hard_trace_mining.get("mined_hard_traces_count"),
            "median_trace_depth": hard_trace_mining.get("median_trace_depth"),
            "trace_depth_min": hard_trace_mining.get("trace_depth_min"),
            "trace_depth_max": hard_trace_mining.get("trace_depth_max"),
            "s3_trace_count": gate_counts.get("S3"),
            "s4_trace_count": gate_counts.get("S4"),
            "s6_trace_count": gate_counts.get("S6"),
            "random_success_rate_at_same_budget": baseline.get("random_success_rate_at_same_budget"),
            "heuristic_success_rate_at_same_budget": baseline.get("heuristic_success_rate_at_same_budget"),
            "accepted_hard_positive_count": filter_summary.get("accepted_hard_positive_count"),
            "exact_state_hash_overlap": leakage.get("exact_state_hash_overlap"),
            "near_duplicate_trace_rate": leakage.get("near_duplicate_trace_rate"),
            "strict_theorem_verifier_result": hard_trace_mining.get("strict_theorem_verifier_result"),
            "proof_confidence_percent": hard_trace_mining.get("proof_confidence_percent"),
            "go_no_go_run014": hard_trace_mining.get("go_no_go_run014"),
        }
    if hard_retrain_eval:
        eval_metrics = hard_retrain_eval.get("eval_metrics") or hard_retrain_eval
        discovery_metrics["proof_action_hard_retrain_eval"] = {
            "syntax_valid_rate": (eval_metrics.get("original_regression") or {}).get("syntax_valid_rate"),
            "action_parse_rate": (eval_metrics.get("original_regression") or {}).get("action_parse_rate"),
            "original_eval_regression_vs_RUN011": (eval_metrics.get("original_regression") or {}).get("original_eval_regression_vs_RUN011"),
            "raw_top5_gate_progress_rate": (eval_metrics.get("frontier_eval") or {}).get("raw_top5_gate_progress_rate"),
            "raw_mrr_first_gate_progress_action": (eval_metrics.get("frontier_eval") or {}).get("raw_mrr_first_gate_progress_action"),
            "closure_at_1000_calls": (eval_metrics.get("frontier_eval") or {}).get("closure_at_1000_calls"),
            "gate_delta_per_1000_calls": (eval_metrics.get("frontier_eval") or {}).get("gate_delta_per_1000_calls"),
            "s3_gate_delta_per_1000_calls": (eval_metrics.get("frontier_eval") or {}).get("s3_gate_delta_per_1000_calls"),
            "s4_gate_delta_per_1000_calls": (eval_metrics.get("frontier_eval") or {}).get("s4_gate_delta_per_1000_calls"),
            "s6_gate_delta_per_1000_calls": (eval_metrics.get("frontier_eval") or {}).get("s6_gate_delta_per_1000_calls"),
            "hard_holdout_closure_at_1000_calls": (eval_metrics.get("hard_holdout_eval") or {}).get("hard_holdout_closure_at_1000_calls"),
            "hard_holdout_improvement_vs_random": (eval_metrics.get("hard_holdout_eval") or {}).get("hard_holdout_improvement_vs_random"),
            "hard_holdout_improvement_vs_heuristic": (eval_metrics.get("hard_holdout_eval") or {}).get("hard_holdout_improvement_vs_heuristic"),
            "s6_blockers_reduced": (eval_metrics.get("s6_eval") or {}).get("s6_blockers_reduced"),
            "s6_new_accepted_lemmas_not_in_train": (eval_metrics.get("s6_eval") or {}).get("s6_new_accepted_lemmas_not_in_train"),
            "strict_theorem_verifier": eval_metrics.get("strict_theorem_verifier_result"),
            "proof_confidence": eval_metrics.get("proof_confidence_percent"),
            "go_no_go_big": eval_metrics.get("go_no_go_big") or hard_retrain_eval.get("go_no_go_big"),
        }
        score_policy_report = {
            **(score_policy_report or {}),
            "useful_action_rate": float((eval_metrics.get("frontier_eval") or {}).get("raw_top5_gate_progress_rate", 0.0) or 0.0),
            "model_guided_obligation_closure_rate": float((eval_metrics.get("hard_holdout_eval") or {}).get("hard_holdout_closure_at_1000_calls", 0.0) or 0.0),
            "proof_progress_percent": 0.0,
        }
        if hard_trace_mining:
            trace_count = float(hard_trace_mining.get("mined_hard_traces_count", 0.0) or 0.0)
            score_policy_report = {
                **(score_policy_report or {}),
                "useful_action_rate": 1.0 if trace_count > 0 else 0.0,
                "model_guided_obligation_closure_rate": min(1.0, trace_count / 100.0),
                "proof_progress_percent": 0.0,
            }
    if proof_evaluation:
        discovery_metrics["proof_progress_metric"] = proof_evaluation.get("proof_progress_metric")
        if proof_evaluation.get("proof_progress_breakdown"):
            discovery_metrics["proof_progress_breakdown"] = proof_evaluation["proof_progress_breakdown"]
        discovery_metrics["proof_attempt_evaluation"] = {
            key: proof_evaluation.get(key)
            for key in (
                "status",
                "verifier_status",
                "proof_progress_metric",
                "proof_progress_percent",
                "verified_weight",
                "total_weight",
                "blocking_steps",
            )
        }
    if proof_attempt:
        discovery_metrics["proof_attempt"] = {
            "schema": proof_attempt.get("schema"),
            "run_id": proof_attempt.get("run_id"),
            "proof_style": proof_attempt.get("proof_style"),
            "step_count": len(proof_attempt.get("steps", [])),
        }
        if isinstance(proof_attempt.get("model_proof_proposal"), dict):
            discovery_metrics["model_proof_proposal"] = proof_attempt["model_proof_proposal"]
        if isinstance(proof_attempt.get("model_proof_verification"), dict):
            discovery_metrics["model_proof_verification"] = proof_attempt["model_proof_verification"]
    score = build_proof_score(
        theorem_candidate=theorem_candidate,
        proof_graph=proof_graph,
        eval_metrics=eval_metrics,
        verification_metrics=verification_metrics,
        postprocess_metrics=postprocess_metrics,
        proof_policy_report=score_policy_report,
        proof_attempt_evaluation=proof_evaluation,
    )
    graph_summary = summarize_proof_graph(proof_graph)
    recommendation = recommend_next_step(score, postprocess_metrics)
    if proof_policy_report and proof_policy_report.get("next_step"):
        recommendation = str(proof_policy_report["next_step"])
    if proof_evaluation and proof_evaluation.get("next_step"):
        recommendation = str(proof_evaluation["next_step"])
    if proof_action_eval:
        recommendation = (
            "Proof-action interface works, but do not launch the big model until the missed small-run gates pass."
            if proof_action_eval.get("go_no_go") != "GO"
            else "Small proof-action gates passed; big A100 run is eligible."
        )
    if hard_trace_mining:
        recommendation = (
            "Use the mined hard traces in RUN-014 small retraining, then rerun the frontier benchmark; do not launch the big model yet."
            if hard_trace_mining.get("go_no_go_run014") == "GO"
            else "Keep mining hard positive traces before RUN-014; the hard-trace corpus did not meet its minimum gates."
        )
    if hard_retrain_eval:
        eval_metrics = hard_retrain_eval.get("eval_metrics") or hard_retrain_eval
        recommendation = (
            "Prepare RUN-015 big-model config for review, but do not launch automatically."
            if (eval_metrics.get("go_no_go_big") or hard_retrain_eval.get("go_no_go_big")) == "GO"
            else f"Do not launch big model; weakest layer: {hard_retrain_eval.get('next_step_recommendation', 'hard retrain gates did not pass')}."
        )
    artifact_map = dict(artifacts or {})
    if proof_attempt_path and proof_attempt_path.exists():
        artifact_map.setdefault("proof_attempt", str(proof_attempt_path))
    if proof_evaluation_path and proof_evaluation_path.exists():
        artifact_map.setdefault("proof_evaluation", str(proof_evaluation_path))
    if proof_action_eval_path and proof_action_eval_path.exists():
        artifact_map.setdefault("proof_action_eval", str(proof_action_eval_path))
    if frontier_search_eval_path and frontier_search_eval_path.exists():
        artifact_map.setdefault("proof_action_frontier_search", str(frontier_search_eval_path))
    if hard_trace_mining_path and hard_trace_mining_path.exists():
        artifact_map.setdefault("proof_action_hard_trace_mining", str(hard_trace_mining_path))
    if hard_retrain_eval_path and hard_retrain_eval_path.exists():
        artifact_map.setdefault("proof_action_hard_retrain_eval", str(hard_retrain_eval_path))
    if proof_attempt:
        model_proposal = proof_attempt.get("model_proof_proposal")
        if isinstance(model_proposal, dict) and model_proposal.get("path"):
            artifact_map.setdefault("model_proof_proposal", str(model_proposal["path"]))
        model_verification = proof_attempt.get("model_proof_verification")
        if isinstance(model_verification, dict) and model_verification.get("path"):
            artifact_map.setdefault("model_proof_verification", str(model_verification["path"]))
    return RunResult(
        run_id=run_id,
        title=title,
        created_at=utc_stamp(),
        config_path=config_path,
        checkpoint_path=checkpoint_path,
        commands=commands or [],
        artifacts=artifact_map,
        eval_metrics=eval_metrics,
        discovery_metrics=discovery_metrics,
        verification_metrics=verification_metrics,
        postprocess_metrics=postprocess_metrics,
        proof_graph_summary=graph_summary,
        theorem_verifier_status=score.verifier_status,
        score=score,
        next_step_recommendation=recommendation,
        notes=notes or [],
    )


def build_baseline_result(project_root: Path) -> RunResult:
    lifted_verification = project_root / BASELINE_VERIFICATIONS["hard_positive_lifted"]
    compression = project_root / "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_lifted_compression.json"
    commands = [
        "scripts/eval_signed_reference_modal.sh /mnt/collatz/runs/20260424_222430_multitask_base24",
        "scripts/run_signed_reference_analysis.sh /mnt/collatz/runs/20260424_222430_multitask_base24",
        "python -m collatz_lab.proof_verifier --proof-graph reports/proof_graph_latest.json --global-obligations reports/parent_state_global_obligations.json --out reports/collatz_descent_theorem_candidate.json",
    ]
    artifacts = {
        "checkpoint": "/mnt/collatz/runs/20260424_222430_multitask_base24/checkpoint.pt",
        "theorem_candidate": "reports/collatz_descent_theorem_candidate.json",
        "proof_graph": "reports/proof_graph_latest.json",
        "discovery_summary": "remote_reports/signed_reference/analysis/20260424_222430_multitask_base24_discovery_summary.md",
        "lifted_postprocess": "reports/runs/RUN-000-current-baseline/lifted_postprocess.json",
    }
    return build_run_result_from_artifacts(
        run_id=BASELINE_RUN_ID,
        title="Current signed multitask baseline",
        config_path="configs/syracuse_multitask_reference_modal.yaml",
        checkpoint_path="/mnt/collatz/runs/20260424_222430_multitask_base24/checkpoint.pt",
        eval_paths=_existing_paths(project_root, BASELINE_EVALS),
        verification_paths=_existing_paths(project_root, BASELINE_VERIFICATIONS),
        candidate_paths=_existing_paths(project_root, BASELINE_CANDIDATES),
        probe_paths=_existing_paths(project_root, BASELINE_PROBES),
        lifted_verification_path=lifted_verification,
        compression_path=compression,
        theorem_candidate_path=project_root / "reports/collatz_descent_theorem_candidate.json",
        proof_graph_path=project_root / "reports/proof_graph_latest.json",
        proof_policy_report_path=project_root / "reports/proof_policy_run_v1.json",
        proof_action_eval_path=None,
        proof_attempt_path=project_root / "reports/runs/RUN-000-current-baseline/proof_attempt.json",
        proof_evaluation_path=project_root / "reports/runs/RUN-000-current-baseline/proof_evaluation.json",
        commands=commands,
        artifacts=artifacts,
        notes=[
            "Backfilled from existing local and remote_reports artifacts.",
            "Strict verifier remains the authority; exact lifted leaves do not imply global closure.",
        ],
    )


def a10g_reference_commands(run_id: str, config_path: str) -> list[str]:
    remote_run_dir = f"/mnt/collatz/runs/{run_id}"
    return [
        f".venv/bin/python -m modal run modal_app.py::train_remote --config-path {config_path} --run-name {run_id}",
        f"scripts/eval_signed_reference_modal.sh {remote_run_dir}",
        f"scripts/run_signed_reference_analysis.sh {remote_run_dir}",
        f".venv/bin/python -m modal volume get collatz-pattern-lab /reports/{run_id}_eval_id_bits48_signed_100k.json remote_reports/{run_id}/",
        f".venv/bin/python -m modal volume get collatz-pattern-lab /reports/{run_id}_verification_hard_positive_lifted.json remote_reports/{run_id}/",
        (
            "python -m collatz_lab.run_pipeline assemble "
            f"--run-id {run_id} --title 'A10G reference run' "
            f"--config-path {config_path} --checkpoint-path {remote_run_dir}/checkpoint.pt "
            "--append-runs"
        ),
    ]


def build_a10g_dry_run(run_id: str = RUN001_ID, config_path: str = "configs/syracuse_multitask_reference_modal.yaml") -> RunResult:
    score = build_proof_score(
        theorem_candidate={"verifier_status": "PLANNED"},
        proof_graph=None,
        eval_metrics={},
        verification_metrics={},
        postprocess_metrics={},
    )
    commands = a10g_reference_commands(run_id, config_path)
    return RunResult(
        run_id=run_id,
        title="A10G reference run plan",
        created_at=utc_stamp(),
        config_path=config_path,
        checkpoint_path=f"/mnt/collatz/runs/{run_id}/checkpoint.pt",
        commands=commands,
        artifacts={
            "remote_run_dir": f"/mnt/collatz/runs/{run_id}",
            "local_result_dir": f"reports/runs/{run_id}",
        },
        eval_metrics={},
        discovery_metrics={"planned": True},
        verification_metrics={},
        postprocess_metrics={},
        proof_graph_summary={},
        theorem_verifier_status="PLANNED",
        score=score,
        next_step_recommendation="Launch the Modal A10G run, then assemble the downloaded artifacts into a completed run result.",
        notes=[
            "Dry-run record only; no proof or model metrics have been produced yet.",
            "Do not append this to runs.md until the run completes.",
        ],
    )


def write_proof_attempt_bundle(
    run_id: str,
    theorem_candidate_path: Path | None,
    progress_report_path: Path | None,
    global_obligations_path: Path | None,
    debt_induction_path: Path | None,
    proof_attempt_path: Path,
    proof_evaluation_path: Path,
    proof_attempts_log_path: Path | None = None,
    central_proof_attempts_log_path: Path | None = None,
    proof_attempt_beam_size: int = 1,
) -> tuple[Path, Path]:
    ranked_attempts = build_ranked_proof_attempts(
        run_id=run_id,
        theorem_candidate=_load_optional_json(theorem_candidate_path) if theorem_candidate_path else None,
        progress_report=_load_optional_json(progress_report_path) if progress_report_path else None,
        global_obligations=_load_optional_json(global_obligations_path) if global_obligations_path else None,
        debt_induction=_load_optional_json(debt_induction_path) if debt_induction_path else None,
        max_attempts=max(1, proof_attempt_beam_size),
    )
    selected = ranked_attempts[0]
    attempt = selected["attempt"]
    evaluation = selected["evaluation"]
    search_summary = summarize_ranked_attempts(ranked_attempts)
    proof_attempt_path.parent.mkdir(parents=True, exist_ok=True)
    proof_attempt_path.write_text(json.dumps(attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    proof_evaluation_path.parent.mkdir(parents=True, exist_ok=True)
    proof_evaluation_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    proof_attempt_md_path = proof_attempt_path.with_suffix(".md")
    proof_evaluation_md_path = proof_evaluation_path.with_suffix(".md")
    write_proof_attempt_markdown(attempt, proof_attempt_md_path)
    write_evaluation_markdown(evaluation, proof_evaluation_md_path)
    search_summary_path = proof_attempt_path.with_name("proof_attempt_search.json")
    artifacts = {
        "proof_attempt": str(proof_attempt_path),
        "proof_evaluation": str(proof_evaluation_path),
        "proof_attempt_markdown": str(proof_attempt_md_path),
        "proof_evaluation_markdown": str(proof_evaluation_md_path),
        "proof_attempt_search": str(search_summary_path),
    }
    records = []
    for row in ranked_attempts:
        record = build_proof_attempt_record(
            row["attempt"],
            row["evaluation"],
            artifacts=artifacts,
            critic=row["critic"],
            search={
                "rank": row["rank"],
                "selected": row["selected"],
                "rank_score": row["rank_score"],
                "focus_bonus": row["focus_bonus"],
                "variant": row["attempt"].get("attempt_variant", {}),
            },
        )
        records.append(record)
        append_proof_attempt_record_to_logs(
            record,
            [
                proof_attempts_log_path or proof_attempt_path.with_name("proof_attempts.jsonl"),
                central_proof_attempts_log_path,
            ],
        )
    if records:
        search_summary["selected_attempt_id"] = records[0]["attempt_id"]
        for summary_row, record in zip(search_summary["ranked_attempts"], records, strict=True):
            summary_row["attempt_id"] = record["attempt_id"]
    search_summary_path.write_text(json.dumps(search_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return proof_attempt_path, proof_evaluation_path


def run_commands(commands: list[str]) -> None:
    for command in commands:
        subprocess.run(command, shell=True, check=True)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Collatz proof-discovery run records.")
    sub = parser.add_subparsers(dest="command", required=True)

    baseline = sub.add_parser("backfill-baseline", help="Create RUN-000 from existing artifacts.")
    baseline.add_argument("--project-root", default=".")
    baseline.add_argument("--out-root", default="reports/runs")
    baseline.add_argument("--runs-md", default="runs.md")
    baseline.add_argument("--no-append-runs", action="store_true")

    dry = sub.add_parser("plan-a10g-reference", help="Create a dry-run command bundle for RUN-001.")
    dry.add_argument("--run-id", default=RUN001_ID)
    dry.add_argument("--config-path", default="configs/syracuse_multitask_reference_modal.yaml")
    dry.add_argument("--out-root", default="reports/runs")
    dry.add_argument("--execute-remote", action="store_true", help="Run the planned Modal commands synchronously.")

    assemble = sub.add_parser("assemble", help="Assemble completed run artifacts into a run result.")
    assemble.add_argument("--run-id", required=True)
    assemble.add_argument("--title", required=True)
    assemble.add_argument("--config-path", default=None)
    assemble.add_argument("--checkpoint-path", default=None)
    assemble.add_argument("--eval", action="append", default=[], help="NAME=PATH")
    assemble.add_argument("--verification", action="append", default=[], help="NAME=PATH")
    assemble.add_argument("--candidate", action="append", default=[], help="NAME=PATH")
    assemble.add_argument("--probe", action="append", default=[], help="NAME=PATH")
    assemble.add_argument("--lifted-verification", default=None)
    assemble.add_argument("--compression", default=None)
    assemble.add_argument("--theorem-candidate", default="reports/collatz_descent_theorem_candidate.json")
    assemble.add_argument("--proof-graph", default="reports/proof_graph_latest.json")
    assemble.add_argument("--proof-policy-report", default="reports/proof_policy_run_v1.json")
    assemble.add_argument("--proof-action-eval", default=None)
    assemble.add_argument("--frontier-search-eval", default=None)
    assemble.add_argument("--hard-trace-mining", default=None)
    assemble.add_argument("--hard-retrain-eval", default=None)
    assemble.add_argument("--proof-attempt", default=None)
    assemble.add_argument("--proof-evaluation", default=None)
    assemble.add_argument("--proof-attempts-log", default=None)
    assemble.add_argument("--central-proof-attempts-log", default="proof_attempts.jsonl")
    assemble.add_argument("--proof-attempt-beam-size", type=int, default=5)
    assemble.add_argument("--global-obligations", default="reports/parent_state_global_obligations.json")
    assemble.add_argument("--debt-induction", default=None)
    assemble.add_argument("--no-build-proof-attempt", action="store_true")
    assemble.add_argument("--out-root", default="reports/runs")
    assemble.add_argument("--runs-md", default="runs.md")
    assemble.add_argument("--append-runs", action="store_true")

    post = sub.add_parser("postprocess-lifted", help="Summarize verified lifted certificates.")
    post.add_argument("--verification", required=True)
    post.add_argument("--compression", default=None)
    post.add_argument("--out", required=True)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    console = Console()

    if args.command == "backfill-baseline":
        result = build_baseline_result(Path(args.project_root))
        paths = _write_result_bundle(
            result,
            Path(args.out_root),
            runs_md=Path(args.runs_md),
            append_runs=not args.no_append_runs,
        )
        console.print({"run_id": result.run_id, **paths})
        return

    if args.command == "plan-a10g-reference":
        result = build_a10g_dry_run(run_id=args.run_id, config_path=args.config_path)
        paths = _write_result_bundle(result, Path(args.out_root))
        console.print({"run_id": result.run_id, **paths, "commands": result.commands})
        if args.execute_remote:
            run_commands(result.commands[:3])
        return

    if args.command == "assemble":
        proof_attempt_path = Path(args.proof_attempt) if args.proof_attempt else Path(args.out_root) / args.run_id / "proof_attempt.json"
        proof_evaluation_path = (
            Path(args.proof_evaluation)
            if args.proof_evaluation
            else Path(args.out_root) / args.run_id / "proof_evaluation.json"
        )
        proof_attempts_log_path = (
            Path(args.proof_attempts_log)
            if args.proof_attempts_log
            else proof_attempt_path.with_name("proof_attempts.jsonl")
        )
        proof_attempt_search_path = proof_attempt_path.with_name("proof_attempt_search.json")
        central_proof_attempts_log_path = Path(args.central_proof_attempts_log) if args.central_proof_attempts_log else None
        if not args.no_build_proof_attempt:
            write_proof_attempt_bundle(
                run_id=args.run_id,
                theorem_candidate_path=Path(args.theorem_candidate) if args.theorem_candidate else None,
                progress_report_path=Path(args.proof_policy_report) if args.proof_policy_report else None,
                global_obligations_path=Path(args.global_obligations) if args.global_obligations else None,
                debt_induction_path=Path(args.debt_induction) if args.debt_induction else None,
                proof_attempt_path=proof_attempt_path,
                proof_evaluation_path=proof_evaluation_path,
                proof_attempts_log_path=proof_attempts_log_path,
                central_proof_attempts_log_path=central_proof_attempts_log_path,
                proof_attempt_beam_size=args.proof_attempt_beam_size,
            )
        artifact_paths = {}
        if proof_attempts_log_path.exists():
            artifact_paths["proof_attempts_log"] = str(proof_attempts_log_path)
        if proof_attempt_search_path.exists():
            artifact_paths["proof_attempt_search"] = str(proof_attempt_search_path)
        if central_proof_attempts_log_path and central_proof_attempts_log_path.exists():
            artifact_paths["central_proof_attempts_log"] = str(central_proof_attempts_log_path)
        result = build_run_result_from_artifacts(
            run_id=args.run_id,
            title=args.title,
            config_path=args.config_path,
            checkpoint_path=args.checkpoint_path,
            eval_paths=_parse_named_paths(args.eval),
            verification_paths=_parse_named_paths(args.verification),
            candidate_paths=_parse_named_paths(args.candidate),
            probe_paths=_parse_named_paths(args.probe),
            lifted_verification_path=Path(args.lifted_verification) if args.lifted_verification else None,
            compression_path=Path(args.compression) if args.compression else None,
            theorem_candidate_path=Path(args.theorem_candidate) if args.theorem_candidate else None,
            proof_graph_path=Path(args.proof_graph) if args.proof_graph else None,
            proof_policy_report_path=Path(args.proof_policy_report) if args.proof_policy_report else None,
            proof_action_eval_path=Path(args.proof_action_eval) if args.proof_action_eval else None,
            frontier_search_eval_path=Path(args.frontier_search_eval) if args.frontier_search_eval else None,
            hard_trace_mining_path=Path(args.hard_trace_mining) if args.hard_trace_mining else None,
            hard_retrain_eval_path=Path(args.hard_retrain_eval) if args.hard_retrain_eval else None,
            proof_attempt_path=proof_attempt_path if proof_attempt_path.exists() else None,
            proof_evaluation_path=proof_evaluation_path if proof_evaluation_path.exists() else None,
            artifacts=artifact_paths,
        )
        paths = _write_result_bundle(
            result,
            Path(args.out_root),
            runs_md=Path(args.runs_md),
            append_runs=args.append_runs,
        )
        console.print({"run_id": result.run_id, **paths})
        return

    if args.command == "postprocess-lifted":
        summary = summarize_lifted_certificates_file(
            args.verification,
            out=args.out,
            compression_path=args.compression,
        )
        console.print({"out": args.out, "verified_leaf_count": summary["verified_leaf_count"]})
        return


if __name__ == "__main__":
    main()
