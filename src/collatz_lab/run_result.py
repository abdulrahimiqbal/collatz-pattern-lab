"""Run records and scoring for proof-discovery experiments.

The central accounting rule is intentionally conservative: learned models can
raise discovery/progress diagnostics, but only the strict proof verifier can
raise proof confidence to 100%.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


RUN_RESULT_SCHEMA = "collatz_lab.run_result"
RUN_RESULT_VERSION = 1


@dataclass(frozen=True)
class ProofScore:
    verifier_status: str
    proof_confidence_percent: float
    proof_progress_percent: float
    model_discovery_score_percent: float
    blocking_obligations: list[str] = field(default_factory=list)
    components: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProofScore":
        return cls(
            verifier_status=str(data.get("verifier_status", "UNKNOWN")),
            proof_confidence_percent=float(data.get("proof_confidence_percent", 0.0)),
            proof_progress_percent=float(data.get("proof_progress_percent", 0.0)),
            model_discovery_score_percent=float(data.get("model_discovery_score_percent", 0.0)),
            blocking_obligations=[str(item) for item in data.get("blocking_obligations", [])],
            components={str(key): float(value) for key, value in data.get("components", {}).items()},
        )


@dataclass(frozen=True)
class RunResult:
    run_id: str
    title: str
    created_at: str
    config_path: str | None
    checkpoint_path: str | None
    commands: list[str]
    artifacts: dict[str, str]
    eval_metrics: dict[str, Any]
    discovery_metrics: dict[str, Any]
    verification_metrics: dict[str, Any]
    postprocess_metrics: dict[str, Any]
    proof_graph_summary: dict[str, Any]
    theorem_verifier_status: str
    score: ProofScore
    next_step_recommendation: str
    notes: list[str] = field(default_factory=list)
    schema: str = RUN_RESULT_SCHEMA
    version: int = RUN_RESULT_VERSION

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["score"] = self.score.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunResult":
        return cls(
            schema=str(data.get("schema", RUN_RESULT_SCHEMA)),
            version=int(data.get("version", RUN_RESULT_VERSION)),
            run_id=str(data["run_id"]),
            title=str(data.get("title", data["run_id"])),
            created_at=str(data.get("created_at", "")),
            config_path=data.get("config_path"),
            checkpoint_path=data.get("checkpoint_path"),
            commands=[str(item) for item in data.get("commands", [])],
            artifacts={str(key): str(value) for key, value in data.get("artifacts", {}).items()},
            eval_metrics=dict(data.get("eval_metrics", {})),
            discovery_metrics=dict(data.get("discovery_metrics", {})),
            verification_metrics=dict(data.get("verification_metrics", {})),
            postprocess_metrics=dict(data.get("postprocess_metrics", {})),
            proof_graph_summary=dict(data.get("proof_graph_summary", {})),
            theorem_verifier_status=str(data.get("theorem_verifier_status", "UNKNOWN")),
            score=ProofScore.from_dict(dict(data.get("score", {}))),
            next_step_recommendation=str(data.get("next_step_recommendation", "")),
            notes=[str(item) for item in data.get("notes", [])],
        )


def utc_stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_run_result(result: RunResult, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_run_result(path: str | Path) -> RunResult:
    return RunResult.from_dict(load_json(path))


def clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, value))


def proof_confidence_from_verifier(verifier_status: str) -> float:
    """Return proof confidence under the strict verifier-gated policy."""

    return 100.0 if verifier_status == "PASS" else 0.0


def summarize_proof_graph(graph: dict[str, Any] | None) -> dict[str, Any]:
    if not graph:
        return {"node_count": 0, "closed_count": 0, "open_count": 0, "action_count": 0}
    summary = dict(graph.get("summary") or {})
    if not summary:
        summary = {
            "node_count": len(graph.get("nodes", {})),
            "closed_count": len(graph.get("closed", [])),
            "open_count": len(graph.get("open", [])),
            "action_count": len(graph.get("actions", [])),
        }
    summary.setdefault("node_count", 0)
    summary.setdefault("closed_count", 0)
    summary.setdefault("open_count", 0)
    summary.setdefault("action_count", 0)
    return summary


def proof_progress_from_graph(summary: dict[str, Any]) -> float:
    total = int(summary.get("node_count") or 0)
    closed = int(summary.get("closed_count") or 0)
    if total <= 0:
        return 0.0
    return clamp_percent(100.0 * closed / total)


def proof_progress_from_report_or_graph(
    proof_policy_report: dict[str, Any] | None,
    graph_summary: dict[str, Any],
) -> float:
    """Return the selected proof-progress diagnostic with explicit fallback."""

    if isinstance((proof_policy_report or {}).get("proof_progress_percent"), (int, float)):
        return clamp_percent(float((proof_policy_report or {})["proof_progress_percent"]))
    return proof_progress_from_graph(graph_summary)


def summarize_verification_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize verifier output rows from ``collatz_lab.verifier``."""

    exact_counts: dict[str, int] = {}
    sampling_counts: dict[str, int] = {}
    for row in results:
        exact_status = str(dict(row.get("exact", {})).get("status", "MISSING"))
        sampling_status = str(dict(row.get("sampling", {})).get("status", "MISSING"))
        exact_counts[exact_status] = exact_counts.get(exact_status, 0) + 1
        sampling_counts[sampling_status] = sampling_counts.get(sampling_status, 0) + 1
    total = len(results)
    pass_count = exact_counts.get("PASS", 0)
    fail_count = exact_counts.get("FAIL_WITH_COUNTEREXAMPLE", 0)
    unknown_count = total - pass_count - fail_count
    return {
        "total": total,
        "exact_status_counts": exact_counts,
        "sampling_status_counts": sampling_counts,
        "exact_pass_count": pass_count,
        "exact_fail_count": fail_count,
        "exact_unknown_count": unknown_count,
        "exact_pass_rate": 0.0 if total == 0 else pass_count / total,
    }


def summarize_verification_file(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of verification rows in {path}")
    return summarize_verification_results(data)


def summarize_eval_files(paths: dict[str, str | Path]) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for name, path in paths.items():
        row = load_json(path)
        summaries[name] = {
            key: row.get(key)
            for key in (
                "examples",
                "exact_sequence_accuracy",
                "token_accuracy",
                "v2_accuracy",
                "descent_bucket_accuracy",
                "hard_case_accuracy",
                "parity_bit_accuracy",
                "parity_prefix_accuracy",
                "negative_cycle_accuracy",
                "hybrid_v2_syracuse_accuracy",
                "ood_accuracy_larger_bits",
                "hard_case_sequence_accuracy",
            )
            if key in row
        }
    return summaries


def _mean(values: list[float]) -> float:
    clean = [float(value) for value in values if value is not None]
    return 0.0 if not clean else sum(clean) / len(clean)


def score_model_discovery(
    eval_metrics: dict[str, Any] | None = None,
    verification_metrics: dict[str, Any] | None = None,
    postprocess_metrics: dict[str, Any] | None = None,
    proof_policy_report: dict[str, Any] | None = None,
) -> tuple[float, dict[str, float]]:
    """Score discovery usefulness without implying proof confidence."""

    eval_metrics = eval_metrics or {}
    verification_metrics = verification_metrics or {}
    postprocess_metrics = postprocess_metrics or {}
    proof_policy_report = proof_policy_report or {}

    eval_rows = [row for row in eval_metrics.values() if isinstance(row, dict)]
    ood_values = [
        float(row[key])
        for row in eval_rows
        for key in ("hybrid_v2_syracuse_accuracy", "ood_accuracy_larger_bits")
        if isinstance(row.get(key), (int, float))
    ]
    exact_values = [
        float(row["exact_sequence_accuracy"])
        for row in eval_rows
        if isinstance(row.get("exact_sequence_accuracy"), (int, float))
    ]
    dynamics_component = 100.0 * (0.7 * _mean(ood_values) + 0.3 * _mean(exact_values))

    verification_rows = [row for row in verification_metrics.values() if isinstance(row, dict)]
    exact_pass_rate = _mean([float(row.get("exact_pass_rate", 0.0)) for row in verification_rows])
    verification_component = 100.0 * exact_pass_rate

    raw = float(postprocess_metrics.get("raw_leaf_count", postprocess_metrics.get("verified_leaf_count", 0)) or 0)
    merged = float(postprocess_metrics.get("merged_leaf_count", 0) or 0)
    if raw > 0:
        compression_component = 100.0 * min(1.0, max(0.0, merged / raw))
    else:
        compression_component = 0.0

    useful_action_rate = float(proof_policy_report.get("useful_action_rate", 0.0) or 0.0)
    closure_rate = float(proof_policy_report.get("model_guided_obligation_closure_rate", 0.0) or 0.0)
    proof_action_component = 100.0 * max(useful_action_rate, closure_rate)

    components = {
        "dynamics": clamp_percent(dynamics_component),
        "exact_candidate_verification": clamp_percent(verification_component),
        "certificate_compression": clamp_percent(compression_component),
        "verifier_backed_actions": clamp_percent(proof_action_component),
    }
    score = (
        0.30 * components["dynamics"]
        + 0.35 * components["exact_candidate_verification"]
        + 0.25 * components["certificate_compression"]
        + 0.10 * components["verifier_backed_actions"]
    )
    return clamp_percent(score), components


def build_proof_score(
    theorem_candidate: dict[str, Any] | None,
    proof_graph: dict[str, Any] | None,
    eval_metrics: dict[str, Any] | None = None,
    verification_metrics: dict[str, Any] | None = None,
    postprocess_metrics: dict[str, Any] | None = None,
    proof_policy_report: dict[str, Any] | None = None,
    proof_attempt_evaluation: dict[str, Any] | None = None,
) -> ProofScore:
    verifier_status = str((theorem_candidate or {}).get("verifier_status", "UNKNOWN"))
    graph_summary = summarize_proof_graph(proof_graph)
    model_score, components = score_model_discovery(
        eval_metrics=eval_metrics,
        verification_metrics=verification_metrics,
        postprocess_metrics=postprocess_metrics,
        proof_policy_report=proof_policy_report,
    )
    blockers = [
        str(row.get("obligation_id"))
        for row in (theorem_candidate or {}).get("minimal_blocking_set", [])[:10]
        if row.get("obligation_id") is not None
    ]
    if proof_attempt_evaluation:
        for step_id in proof_attempt_evaluation.get("blocking_steps", [])[:10]:
            step = str(step_id)
            if step not in blockers:
                blockers.append(step)
    return ProofScore(
        verifier_status=verifier_status,
        proof_confidence_percent=proof_confidence_from_verifier(verifier_status),
        proof_progress_percent=proof_progress_from_report_or_graph(
            proof_attempt_evaluation or proof_policy_report,
            graph_summary,
        ),
        model_discovery_score_percent=model_score,
        blocking_obligations=blockers,
        components=components,
    )


def recommend_next_step(score: ProofScore, postprocess_metrics: dict[str, Any]) -> str:
    if score.verifier_status == "PASS":
        return "Freeze the proof object, independently audit every exact certificate, then prepare a human-readable proof report."
    exact_component = score.components.get("exact_candidate_verification", 0.0)
    compression_component = score.components.get("certificate_compression", 0.0)
    dynamics_component = score.components.get("dynamics", 0.0)
    proof_action_component = score.components.get("verifier_backed_actions", 0.0)
    raw = int(postprocess_metrics.get("raw_leaf_count", postprocess_metrics.get("verified_leaf_count", 0)) or 0)
    merged = int(postprocess_metrics.get("merged_leaf_count", 0) or 0)
    if proof_action_component > 0.0 and exact_component == 0.0 and compression_component == 0.0:
        return "Expand exact proof-action executors for the blocking obligations; do not spend more on local certificate mining until an existing graph node closes."
    if raw > 0 and merged == 0:
        return "Prioritize symbolic compression of verified lifted certificates before spending more on scale."
    if dynamics_component >= 70.0 and exact_component < 20.0:
        return "Shift objective design toward verifier-backed candidate generation rather than larger sequence prediction."
    if dynamics_component >= 70.0 and exact_component >= 50.0 and compression_component > 0.0:
        return "Scale to an A100 run while preserving the same verifier and compression gates."
    return "Improve candidate mining and proof-obligation targeting, then rerun the reference pipeline."


def render_run_result_markdown(result: RunResult) -> str:
    score = result.score
    lines = [
        f"# {result.run_id}: {result.title}",
        "",
        f"- created: `{result.created_at}`",
        f"- verifier status: `{score.verifier_status}`",
        f"- proof confidence: `{score.proof_confidence_percent:.2f}%`",
        f"- proof progress: `{score.proof_progress_percent:.2f}%`",
        f"- model discovery score: `{score.model_discovery_score_percent:.2f}%`",
        f"- checkpoint: `{result.checkpoint_path or 'n/a'}`",
        "",
        "## Scores",
        "",
    ]
    for key, value in score.components.items():
        lines.append(f"- {key}: `{value:.2f}%`")
    if result.artifacts:
        lines.extend(["", "## Artifacts", ""])
        for key, value in sorted(result.artifacts.items()):
            lines.append(f"- {key}: `{value}`")
    progress_breakdown = result.discovery_metrics.get("proof_progress_breakdown")
    if isinstance(progress_breakdown, dict):
        selected = progress_breakdown.get("selected", {})
        lines.extend(
            [
                "",
                "## Proof Progress Breakdown",
                "",
                f"- selected metric: `{result.discovery_metrics.get('proof_progress_metric', selected.get('metric', 'unknown'))}`",
                f"- selected numerator: `{selected.get('numerator')}`",
                f"- selected denominator: `{selected.get('denominator')}`",
                f"- selected source: `{selected.get('source')}`",
                f"- selected status: `{selected.get('status')}`",
            ]
        )
        strict = progress_breakdown.get("strict_graph")
        if isinstance(strict, dict):
            lines.extend(
                [
                    f"- strict graph comparator: `{strict.get('numerator')}` / `{strict.get('denominator')}` = `{float(strict.get('percent', 0.0)):.2f}%`",
                    f"- strict graph source: `{strict.get('source')}`",
                ]
            )
        canonical = progress_breakdown.get("canonicalized_graph")
        if isinstance(canonical, dict):
            lines.extend(
                [
                    f"- canonicalized graph comparator: `{canonical.get('canonical_closed_count')}` / `{canonical.get('canonical_node_count')}` = `{float(canonical.get('canonical_progress_percent', 0.0)):.2f}%`",
                    f"- duplicate graph groups: `{canonical.get('duplicate_group_count')}`",
                ]
            )
    proof_eval = result.discovery_metrics.get("proof_attempt_evaluation")
    if isinstance(proof_eval, dict):
        lines.extend(["", "## Proof Attempt Evaluation", ""])
        lines.append(f"- metric: `{proof_eval.get('proof_progress_metric')}`")
        lines.append(f"- verified weight: `{proof_eval.get('verified_weight')}` / `{proof_eval.get('total_weight')}`")
        lines.append(f"- blocking steps: `{proof_eval.get('blocking_steps')}`")
    proof_action_eval = result.discovery_metrics.get("proof_action_eval")
    if isinstance(proof_action_eval, dict):
        lines.extend(["", "## Proof Action Evaluation", ""])
        for key in (
            "syntax_valid_rate",
            "action_parse_rate",
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
            "strict_theorem_verifier_result",
            "go_no_go",
        ):
            lines.append(f"- {key}: `{proof_action_eval.get(key)}`")
    frontier_eval = result.discovery_metrics.get("proof_action_frontier_search")
    if isinstance(frontier_eval, dict):
        lines.extend(["", "## Proof Action Frontier Search", ""])
        for key in (
            "raw_model_top1_accept_rate",
            "raw_model_top5_accept_rate",
            "raw_model_top10_accept_rate",
            "raw_model_top1_close_rate",
            "raw_model_top5_close_rate",
            "raw_model_top10_close_rate",
            "raw_model_top5_gate_progress_rate",
            "raw_mrr_first_gate_progress_action",
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
            "go_no_go",
        ):
            lines.append(f"- {key}: `{frontier_eval.get(key)}`")
    hard_trace = result.discovery_metrics.get("proof_action_hard_trace_mining")
    if isinstance(hard_trace, dict):
        lines.extend(["", "## Proof Action Hard Trace Mining", ""])
        for key in (
            "mined_hard_traces_count",
            "median_trace_depth",
            "trace_depth_min",
            "trace_depth_max",
            "s3_trace_count",
            "s4_trace_count",
            "s6_trace_count",
            "random_success_rate_at_same_budget",
            "heuristic_success_rate_at_same_budget",
            "accepted_hard_positive_count",
            "exact_state_hash_overlap",
            "near_duplicate_trace_rate",
            "strict_theorem_verifier_result",
            "proof_confidence_percent",
            "go_no_go_run014",
        ):
            lines.append(f"- {key}: `{hard_trace.get(key)}`")
    hard_retrain = result.discovery_metrics.get("proof_action_hard_retrain_eval")
    if isinstance(hard_retrain, dict):
        lines.extend(["", "## Proof Action Hard Retrain", ""])
        for key in (
            "syntax_valid_rate",
            "action_parse_rate",
            "original_eval_regression_vs_RUN011",
            "raw_top5_gate_progress_rate",
            "raw_mrr_first_gate_progress_action",
            "closure_at_1000_calls",
            "gate_delta_per_1000_calls",
            "s3_gate_delta_per_1000_calls",
            "s4_gate_delta_per_1000_calls",
            "s6_gate_delta_per_1000_calls",
            "hard_holdout_closure_at_1000_calls",
            "hard_holdout_improvement_vs_random",
            "hard_holdout_improvement_vs_heuristic",
            "s6_blockers_reduced",
            "s6_new_accepted_lemmas_not_in_train",
            "strict_theorem_verifier",
            "proof_confidence",
            "go_no_go_big",
        ):
            lines.append(f"- {key}: `{hard_retrain.get(key)}`")
    lines.extend(["", "## Blocking Obligations", ""])
    for obligation_id in score.blocking_obligations[:10]:
        lines.append(f"- `{obligation_id}`")
    if not score.blocking_obligations:
        lines.append("- none")
    lines.extend(["", "## Next Step", "", result.next_step_recommendation, ""])
    if result.commands:
        lines.extend(["## Commands", ""])
        for command in result.commands:
            lines.append(f"- `{command}`")
        lines.append("")
    if result.notes:
        lines.extend(["## Notes", ""])
        for note in result.notes:
            lines.append(f"- {note}")
        lines.append("")
    return "\n".join(lines)


def write_run_result_markdown(result: RunResult, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_run_result_markdown(result), encoding="utf-8")


def run_table_row(result: RunResult) -> str:
    return (
        f"| {result.run_id} | {result.title} | {result.score.verifier_status} | "
        f"{result.score.proof_confidence_percent:.2f}% | "
        f"{result.score.proof_progress_percent:.2f}% | "
        f"{result.score.model_discovery_score_percent:.2f}% | "
        f"{result.next_step_recommendation} |"
    )


def run_template_markdown() -> str:
    return """## Run Template

- run id:
- model/config:
- data:
- commands:
- checkpoint:
- eval metrics:
- candidate counts:
- verifier result:
- proof attempt:
- proof attempt evaluation:
- proof confidence:
- proof progress:
- model discovery score:
- what worked:
- what failed:
- exact next step:
"""


def append_run_to_runs_md(result: RunResult, path: str | Path = "runs.md") -> None:
    out = Path(path)
    detail = render_run_result_markdown(result).replace("# ", "## ", 1)
    if not out.exists():
        text = "\n".join(
            [
                "# Collatz Proof-Discovery Runs",
                "",
                "| Run | Title | Verifier | Proof Confidence | Proof Progress | Discovery Score | Next Step |",
                "| --- | --- | --- | ---: | ---: | ---: | --- |",
                run_table_row(result),
                "",
                run_template_markdown().rstrip(),
                "",
                "## Run Details",
                "",
                detail,
                "",
            ]
        )
        out.write_text(text, encoding="utf-8")
        return

    text = out.read_text(encoding="utf-8")
    if result.run_id in text:
        return
    lines = text.splitlines()
    separator_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith("| ---") and "Proof Confidence" in "\n".join(lines[max(0, index - 2) : index])
        ),
        None,
    )
    if separator_index is not None:
        lines.insert(separator_index + 1, run_table_row(result))
        text = "\n".join(lines) + "\n"
    if "## Run Details" not in text:
        text = text.rstrip() + "\n\n## Run Details\n"
    text = text.rstrip() + "\n\n" + detail + "\n"
    out.write_text(text, encoding="utf-8")
