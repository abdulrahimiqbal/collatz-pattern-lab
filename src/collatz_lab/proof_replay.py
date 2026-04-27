"""Build proof-repair training examples from failed proof-attempt ledgers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console


PROOF_REPLAY_EXAMPLE_SCHEMA = "collatz_lab.proof_replay_example"
PROOF_REPLAY_REPORT_SCHEMA = "collatz_lab.proof_replay_report"


REPAIR_ACTIONS = {
    "S2-p6-local-frontier": "REFINE_LOCAL_FRONTIER_CERTIFICATES",
    "S3-global-parent-transitions": "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE",
    "S4-parametric-lifting": "PROVE_PARAMETRIC_LIFTING_LEMMA",
    "S5-debt-induction": "PROVE_DEBT_CARRYING_INDUCTION",
    "S6-strict-theorem-verifier": "REPAIR_STRICT_THEOREM_CANDIDATE",
}


def load_attempt_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _first_blocker(record: dict[str, Any]) -> str:
    for blocker in record.get("blocking_steps", []):
        if str(blocker) in REPAIR_ACTIONS:
            return str(blocker)
    return "UNKNOWN"


def record_to_replay_example(record: dict[str, Any]) -> dict[str, Any]:
    """Convert one proof-attempt record into one proof-repair example."""

    first_blocker = _first_blocker(record)
    critic = record.get("proof_critic") if isinstance(record.get("proof_critic"), dict) else {}
    issues = critic.get("issues") if isinstance(critic.get("issues"), list) else []
    attempt = record.get("proof_attempt") if isinstance(record.get("proof_attempt"), dict) else {}
    evaluation = record.get("proof_evaluation") if isinstance(record.get("proof_evaluation"), dict) else {}
    dsl = attempt.get("proof_dsl") if isinstance(attempt.get("proof_dsl"), dict) else {}
    return {
        "schema": PROOF_REPLAY_EXAMPLE_SCHEMA,
        "version": 1,
        "attempt_id": record.get("attempt_id"),
        "run_id": record.get("run_id"),
        "variant_id": record.get("proof_search", {}).get("variant", {}).get("variant_id"),
        "input": {
            "theorem": attempt.get("theorem"),
            "proof_text": attempt.get("proof_text"),
            "proof_dsl": dsl,
            "step_results": evaluation.get("step_results", []),
            "critic_issues": issues,
            "proof_progress_percent": record.get("proof_progress_percent"),
            "proof_confidence_percent": record.get("proof_confidence_percent"),
        },
        "target": {
            "first_blocker": first_blocker,
            "repair_action": REPAIR_ACTIONS.get(first_blocker, "INSPECT_UNKNOWN_BLOCKER"),
            "next_step": record.get("next_step"),
            "must_not_claim_proof": record.get("verifier_status") != "PASS",
        },
    }


def build_replay_examples(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record_to_replay_example(record) for record in records]


def write_replay_examples(examples: list[dict[str, Any]], out: str | Path) -> None:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in examples) + ("\n" if examples else ""), encoding="utf-8")


def summarize_replay_examples(examples: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts: dict[str, int] = {}
    blocker_counts: dict[str, int] = {}
    for row in examples:
        action = str(row.get("target", {}).get("repair_action", "UNKNOWN"))
        blocker = str(row.get("target", {}).get("first_blocker", "UNKNOWN"))
        action_counts[action] = action_counts.get(action, 0) + 1
        blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    return {
        "schema": PROOF_REPLAY_REPORT_SCHEMA,
        "version": 1,
        "example_count": len(examples),
        "repair_action_counts": action_counts,
        "first_blocker_counts": blocker_counts,
        "training_objective": (
            "Given a failed typed proof attempt, critic issues, and exact step results, "
            "predict the next proof-repair action without claiming proof confidence."
        ),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export proof-repair replay data from proof_attempts.jsonl.")
    parser.add_argument("--attempts-log", default="proof_attempts.jsonl")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report-out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    examples = build_replay_examples(load_attempt_records(args.attempts_log))
    write_replay_examples(examples, args.out)
    report = summarize_replay_examples(examples)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print(report)


if __name__ == "__main__":
    main()
