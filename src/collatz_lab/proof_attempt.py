"""Structured proof attempts and verifier-backed proof-progress evaluation.

Runs should emit a proof attempt, not only model/eval diagnostics.  This module
turns current proof artifacts into a theorem-shaped attempt, evaluates each
proof step against exact gates, and computes the run's proof-progress metric
from that evaluated attempt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from rich.console import Console


PROOF_ATTEMPT_SCHEMA = "collatz_lab.proof_attempt"
PROOF_EVALUATION_SCHEMA = "collatz_lab.proof_attempt_evaluation"
PROOF_ATTEMPT_RECORD_SCHEMA = "collatz_lab.proof_attempt_record"

STEP_WEIGHTS = {
    "universal_entry": 10.0,
    "p6_local_frontier": 40.0,
    "global_parent_transitions": 25.0,
    "parametric_lifting": 15.0,
    "strict_theorem_verifier": 10.0,
}


def _load_optional(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _status_is_closed(status: str | None) -> bool:
    return str(status or "").startswith("CLOSED_BY_") or str(status or "") in {
        "PASS",
        "PROVED_INFINITE_ANCESTOR_DESCENT",
        "PROVED_DEBT_CARRYING_PARENT_INDUCTION",
    }


def _global_obligation(global_obligations: dict[str, Any] | None, obligation_id: str) -> dict[str, Any] | None:
    for row in (global_obligations or {}).get("obligations", []):
        if row.get("obligation_id") == obligation_id:
            return row
    return None


def _selected_progress(progress_report: dict[str, Any] | None) -> dict[str, Any]:
    if not progress_report:
        return {
            "metric": "missing_local_frontier_report",
            "numerator": 0,
            "denominator": 0,
            "percent": 0.0,
            "status": "MISSING",
        }
    breakdown = progress_report.get("proof_progress_breakdown")
    if isinstance(breakdown, dict) and isinstance(breakdown.get("selected"), dict):
        return dict(breakdown["selected"])
    if isinstance(progress_report.get("proof_progress_percent"), (int, float)):
        return {
            "metric": progress_report.get("proof_progress_metric", "proof_progress_percent"),
            "numerator": progress_report.get("baseline_certified_q_classes"),
            "denominator": progress_report.get("denominator_q_classes"),
            "percent": float(progress_report["proof_progress_percent"]),
            "status": progress_report.get("status", "DIAGNOSTIC"),
        }
    return {
        "metric": "unrecognized_progress_report",
        "numerator": 0,
        "denominator": 0,
        "percent": 0.0,
        "status": "UNKNOWN",
    }


def build_proof_attempt(
    run_id: str,
    theorem_candidate: dict[str, Any] | None = None,
    progress_report: dict[str, Any] | None = None,
    global_obligations: dict[str, Any] | None = None,
    debt_induction: dict[str, Any] | None = None,
    author: str = "model/system",
) -> dict[str, Any]:
    """Build a structured proof attempt from the run's current artifacts."""

    theorem_candidate = theorem_candidate or {}
    progress = _selected_progress(progress_report)
    even = _global_obligation(global_obligations, "even_descent")
    odd = _global_obligation(global_obligations, "odd_parent_state_cover")
    parent_templates = _global_obligation(global_obligations, "parent_state_transition_templates")
    parametric = _global_obligation(global_obligations, "parametric_a_templates")

    steps = [
        {
            "step_id": "S1-universal-entry",
            "kind": "universal_entry",
            "claim": "Even n descend immediately and odd n enter a unique parent state P_a.",
            "weight": STEP_WEIGHTS["universal_entry"],
            "evidence": {
                "even_descent_status": None if even is None else even.get("status"),
                "odd_parent_state_cover_status": None if odd is None else odd.get("status"),
            },
        },
        {
            "step_id": "S2-p6-local-frontier",
            "kind": "p6_local_frontier",
            "claim": "The current P6 laboratory frontier has verified exact descent certificates for a finite q-depth slice.",
            "weight": STEP_WEIGHTS["p6_local_frontier"],
            "evidence": progress,
        },
        {
            "step_id": "S3-global-parent-transitions",
            "kind": "global_parent_transitions",
            "claim": "All parent-state transition templates P_a are exact and ranked.",
            "weight": STEP_WEIGHTS["global_parent_transitions"],
            "evidence": {} if parent_templates is None else parent_templates,
        },
        {
            "step_id": "S4-parametric-lifting",
            "kind": "parametric_lifting",
            "claim": "The finite parent-state templates lift uniformly in a and 2-adic depth.",
            "weight": STEP_WEIGHTS["parametric_lifting"],
            "evidence": {} if parametric is None else parametric,
        },
        {
            "step_id": "S5-debt-induction",
            "kind": "global_parent_transitions",
            "claim": "Low-h expanding transitions are closed by a debt-carrying parent-state induction.",
            "weight": 0.0,
            "evidence": debt_induction or {"status": "MISSING"},
        },
        {
            "step_id": "S6-strict-theorem-verifier",
            "kind": "strict_theorem_verifier",
            "claim": "The assembled theorem candidate verifies as a complete Collatz descent proof.",
            "weight": STEP_WEIGHTS["strict_theorem_verifier"],
            "evidence": {
                "verifier_status": theorem_candidate.get("verifier_status", "UNKNOWN"),
                "verification": theorem_candidate.get("verification", {}),
                "unknown_obligations": len(theorem_candidate.get("unknown_obligations", [])),
            },
        },
    ]
    return {
        "schema": PROOF_ATTEMPT_SCHEMA,
        "version": 1,
        "run_id": run_id,
        "author": author,
        "theorem": theorem_candidate.get(
            "theorem",
            "forall n > 1 exists k >= 1 such that C^k(n) < n",
        ),
        "proof_style": "structured verifier-backed proof attempt",
        "proof_text": (
            "Attempt: reduce every n>1 to a smaller ancestor by even descent, "
            "universal parent-state coverage, exact P6/frontier certificates, "
            "global parent transition templates, parametric lifting, and a "
            "final strict theorem verifier."
        ),
        "steps": steps,
        "source_status": {
            "theorem_verifier_status": theorem_candidate.get("verifier_status", "UNKNOWN"),
            "coverage_status": (theorem_candidate.get("coverage") or {}).get("status"),
        },
    }


def evaluate_proof_attempt(proof_attempt: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a proof attempt and compute proof progress from proof steps."""

    theorem_status = str(proof_attempt.get("source_status", {}).get("theorem_verifier_status", "UNKNOWN"))
    step_results: list[dict[str, Any]] = []
    total_weight = 0.0
    verified_weight = 0.0
    blockers: list[str] = []

    for step in proof_attempt.get("steps", []):
        kind = str(step.get("kind"))
        weight = float(step.get("weight", 0.0) or 0.0)
        evidence = step.get("evidence") if isinstance(step.get("evidence"), dict) else {}
        total_weight += weight
        fraction = 0.0
        status = "UNKNOWN"
        reason = ""

        if kind == "universal_entry":
            even_ok = _status_is_closed(evidence.get("even_descent_status"))
            odd_ok = _status_is_closed(evidence.get("odd_parent_state_cover_status"))
            fraction = 1.0 if even_ok and odd_ok else 0.0
            status = "PASS" if fraction == 1.0 else "FAIL"
            reason = "even descent and odd parent-state entry are both closed" if fraction == 1.0 else "universal entry is incomplete"
        elif kind == "p6_local_frontier":
            percent = float(evidence.get("percent", 0.0) or 0.0)
            fraction = max(0.0, min(1.0, percent / 100.0))
            status = "PARTIAL" if 0.0 < fraction < 1.0 else ("PASS" if fraction >= 1.0 else "FAIL")
            reason = "finite P6 frontier coverage is local evidence, not universal proof"
        elif kind == "global_parent_transitions":
            if evidence.get("ready_for_run7") is True and evidence.get("status") == "PROVED_DEBT_CARRYING_PARENT_INDUCTION":
                fraction = 1.0
                status = "PASS"
                reason = "debt-carrying induction certificate is ready"
            else:
                fraction = 1.0 if _status_is_closed(evidence.get("status")) else 0.0
                status = "PASS" if fraction == 1.0 else "FAIL"
                reason = str(evidence.get("claim") or evidence.get("formal_blockers") or "global transition proof is open")
        elif kind == "parametric_lifting":
            fraction = 1.0 if _status_is_closed(evidence.get("status")) else 0.0
            status = "PASS" if fraction == 1.0 else "FAIL"
            reason = str(evidence.get("claim") or "parametric lifting is open")
        elif kind == "strict_theorem_verifier":
            fraction = 1.0 if evidence.get("verifier_status") == "PASS" else 0.0
            status = "PASS" if fraction == 1.0 else "FAIL"
            reason = "; ".join(evidence.get("verification", {}).get("errors", [])) or "strict verifier has not passed"
        else:
            status = "UNKNOWN"
            reason = f"unknown proof step kind {kind!r}"

        contribution = weight * fraction
        verified_weight += contribution
        if status != "PASS":
            blockers.append(str(step.get("step_id")))
        step_results.append(
            {
                "step_id": step.get("step_id"),
                "kind": kind,
                "status": status,
                "weight": weight,
                "verified_fraction": fraction,
                "verified_weight": contribution,
                "reason": reason,
            }
        )

    progress = 100.0 if theorem_status == "PASS" else (0.0 if total_weight == 0 else verified_weight / total_weight * 100.0)
    return {
        "schema": PROOF_EVALUATION_SCHEMA,
        "version": 1,
        "run_id": proof_attempt.get("run_id"),
        "status": "PASS" if theorem_status == "PASS" else "FAIL",
        "verifier_status": theorem_status,
        "proof_confidence_percent": 100.0 if theorem_status == "PASS" else 0.0,
        "proof_progress_metric": "evaluated_proof_attempt_weighted_gate_score",
        "proof_progress_percent": progress,
        "verified_weight": verified_weight,
        "total_weight": total_weight,
        "blocking_steps": blockers,
        "step_results": step_results,
        "proof_progress_breakdown": {
            "selected": {
                "metric": "evaluated_proof_attempt_weighted_gate_score",
                "numerator": verified_weight,
                "denominator": total_weight,
                "percent": progress,
                "source": "proof_attempt.json",
                "status": "proof_attempt_evaluation_not_proof_confidence",
            },
        },
        "next_step": _next_step_from_results(step_results),
        "useful_action_rate": 0.0,
        "model_guided_obligation_closure_rate": 0.0,
    }


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _utc_stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_proof_attempt_record(
    proof_attempt: dict[str, Any],
    evaluation: dict[str, Any],
    artifacts: dict[str, str] | None = None,
    critic: dict[str, Any] | None = None,
    search: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build one JSONL record for failed/successful proof-attempt replay."""

    run_id = str(proof_attempt.get("run_id") or evaluation.get("run_id") or "UNKNOWN")
    digest = hashlib.sha256(_canonical_json({"proof_attempt": proof_attempt, "evaluation": evaluation}).encode("utf-8"))
    attempt_id = f"{run_id}:{digest.hexdigest()[:16]}"
    return {
        "schema": PROOF_ATTEMPT_RECORD_SCHEMA,
        "version": 1,
        "attempt_id": attempt_id,
        "run_id": run_id,
        "created_at": created_at or _utc_stamp(),
        "status": evaluation.get("status", "UNKNOWN"),
        "verifier_status": evaluation.get("verifier_status", "UNKNOWN"),
        "proof_confidence_percent": evaluation.get("proof_confidence_percent", 0.0),
        "proof_progress_metric": evaluation.get("proof_progress_metric"),
        "proof_progress_percent": evaluation.get("proof_progress_percent", 0.0),
        "blocking_steps": list(evaluation.get("blocking_steps", [])),
        "next_step": evaluation.get("next_step"),
        "artifacts": dict(artifacts or {}),
        "proof_critic": dict(critic or {}),
        "proof_search": dict(search or {}),
        "proof_attempt": proof_attempt,
        "proof_evaluation": evaluation,
    }


def append_proof_attempt_record(record: dict[str, Any], path: str | Path) -> bool:
    """Append a proof-attempt record unless the same attempt id is already logged."""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    attempt_id = str(record.get("attempt_id", ""))
    if out.exists() and attempt_id:
        for line in out.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                existing = json.loads(line)
            except json.JSONDecodeError:
                continue
            if existing.get("attempt_id") == attempt_id:
                return False
    with out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return True


def append_proof_attempt_record_to_logs(record: dict[str, Any], paths: list[str | Path | None]) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for path in paths:
        if path is None:
            continue
        results[str(path)] = append_proof_attempt_record(record, path)
    return results


def _next_step_from_results(step_results: list[dict[str, Any]]) -> str:
    for step_id in (
        "S3-global-parent-transitions",
        "S5-debt-induction",
        "S4-parametric-lifting",
        "S2-p6-local-frontier",
        "S6-strict-theorem-verifier",
    ):
        row = next((item for item in step_results if item.get("step_id") == step_id), None)
        if row and row.get("status") != "PASS":
            if step_id == "S3-global-parent-transitions":
                return "Prove exact global parent-state transition templates; local P6 coverage is not enough."
            if step_id == "S5-debt-induction":
                return "Prove the variable-depth debt-carrying parent-state induction certificate."
            if step_id == "S4-parametric-lifting":
                return "Lift parent-state templates uniformly in a and 2-adic depth."
            if step_id == "S2-p6-local-frontier":
                return "Close more evaluated P6 proof obligations with exact certificates."
            return "Remove all unknown obligations and rerun the strict theorem verifier."
    return "Freeze and independently audit the completed proof object."


def write_proof_attempt_markdown(proof_attempt: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Proof Attempt",
        "",
        f"- run id: `{proof_attempt['run_id']}`",
        f"- author: `{proof_attempt['author']}`",
        f"- theorem: `{proof_attempt['theorem']}`",
        "",
        proof_attempt["proof_text"],
        "",
        "## Steps",
        "",
    ]
    for step in proof_attempt.get("steps", []):
        lines.append(f"- `{step['step_id']}` ({step['kind']}): {step['claim']}")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_evaluation_markdown(evaluation: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Proof Attempt Evaluation",
        "",
        f"- status: `{evaluation['status']}`",
        f"- verifier status: `{evaluation['verifier_status']}`",
        f"- proof confidence: `{evaluation['proof_confidence_percent']}`%",
        f"- proof progress metric: `{evaluation['proof_progress_metric']}`",
        f"- proof progress: `{evaluation['proof_progress_percent']}`%",
        f"- verified weight: `{evaluation['verified_weight']}` / `{evaluation['total_weight']}`",
        "",
        "## Step Results",
        "",
    ]
    for row in evaluation.get("step_results", []):
        lines.append(
            f"- `{row['step_id']}`: `{row['status']}`, "
            f"fraction `{row['verified_fraction']}`, weight `{row['verified_weight']}` / `{row['weight']}`"
        )
    lines.extend(["", "## Next Step", "", evaluation["next_step"], ""])
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and evaluate a structured Collatz proof attempt.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--theorem-candidate", default="reports/collatz_descent_theorem_candidate.json")
    parser.add_argument("--progress-report", default=None)
    parser.add_argument("--global-obligations", default="reports/parent_state_global_obligations.json")
    parser.add_argument("--debt-induction", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    parser.add_argument("--eval-out", required=True)
    parser.add_argument("--eval-md", default=None)
    parser.add_argument("--attempts-log", default=None, help="Optional per-run proof_attempts.jsonl path.")
    parser.add_argument("--central-attempts-log", default=None, help="Optional central proof_attempts.jsonl path.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    attempt = build_proof_attempt(
        run_id=args.run_id,
        theorem_candidate=_load_optional(args.theorem_candidate),
        progress_report=_load_optional(args.progress_report),
        global_obligations=_load_optional(args.global_obligations),
        debt_induction=_load_optional(args.debt_induction),
    )
    evaluation = evaluate_proof_attempt(attempt)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    eval_out = Path(args.eval_out)
    eval_out.parent.mkdir(parents=True, exist_ok=True)
    eval_out.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    attempt_md = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    evaluation_md = Path(args.eval_md) if args.eval_md else eval_out.with_suffix(".md")
    write_proof_attempt_markdown(attempt, attempt_md)
    write_evaluation_markdown(evaluation, evaluation_md)
    record = build_proof_attempt_record(
        attempt,
        evaluation,
        artifacts={
            "proof_attempt": str(out),
            "proof_evaluation": str(eval_out),
            "proof_attempt_markdown": str(attempt_md),
            "proof_evaluation_markdown": str(evaluation_md),
        },
    )
    logs = append_proof_attempt_record_to_logs(record, [args.attempts_log, args.central_attempts_log])
    Console().print(
        {
            "proof_attempt": str(out),
            "proof_evaluation": str(eval_out),
            "attempt_id": record["attempt_id"],
            "proof_attempt_logs": logs,
            "proof_progress_percent": evaluation["proof_progress_percent"],
            "verifier_status": evaluation["verifier_status"],
        }
    )


if __name__ == "__main__":
    main()
