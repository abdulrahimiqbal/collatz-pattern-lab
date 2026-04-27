"""Convert mined RUN-013 hard traces into policy/value/ranker rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import parse_action, serialize_action
from .proof_action_outcome import classify_action_outcome


def _digest(data: Any, size: int = 16) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:size]


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _policy_row(trace: dict[str, Any], step: dict[str, Any], *, step_index: int, split: str) -> dict[str, Any]:
    action = parse_action(str(step["action"]))
    check = verify_action_for_state(action, str(step["state_before"]))
    outcome = classify_action_outcome(action, str(step["state_before"]), check, closed_branch=bool(step.get("closed_branch"))).to_dict()
    distance = max(0, int(trace.get("depth", 0) or 0) - step_index)
    return {
        "schema": "collatz_lab.proof_action_hard_trace_row",
        "version": 1,
        "example_id": f"hard_policy:{_digest({'trace': trace['trace_id'], 'step': step_index})}",
        "split": split,
        "gate": trace["gate"],
        "trace_id": trace["trace_id"],
        "state": str(step["state_before"]),
        "target_action": action,
        "target_action_text": serialize_action(action),
        "verifier_status": "ACCEPT" if check.accepted else "REJECT",
        "outcome_class": outcome["outcome_class"],
        "closure_reward": outcome["closure_reward"],
        "reward": outcome["closure_reward"],
        "closed_obligation": bool(outcome["closed_obligation"]),
        "closed_branch": bool(outcome["closed_branch"]),
        "eventually_closed": bool(trace.get("closed_branch") or trace.get("closed_obligation") or trace.get("gate_progress_total", 0.0)),
        "distance_to_close": distance,
        "gate_progress_delta": float(outcome.get("gate_progress_delta", 0.0) or 0.0),
        "net_goal_delta": int(outcome.get("net_goal_delta", 0) or 0),
        "source": "hard_trace_miner",
        "frontier_kind": trace.get("frontier_kind"),
    }


def _candidate_text(action: dict[str, Any]) -> str | None:
    try:
        return serialize_action(action)
    except Exception:
        return None


def _pair_rows(trace: dict[str, Any], policy_row: dict[str, Any], *, split: str, max_pairs: int = 3) -> list[dict[str, Any]]:
    state = str(policy_row["state"])
    better = str(policy_row["target_action_text"])
    pairs: list[dict[str, Any]] = []
    emitted = 0
    for action in legal_action_candidates_from_state(state, max_candidates=40):
        worse = _candidate_text(action)
        if not worse or worse == better:
            continue
        check = verify_action_for_state(action, state)
        outcome = classify_action_outcome(action, state, check).to_dict()
        if check.accepted and float(outcome.get("gate_progress_delta", 0.0) or 0.0) > float(policy_row.get("gate_progress_delta", 0.0) or 0.0):
            continue
        reason = "accepted_good_vs_accepted_dead_end" if check.accepted else "accepted_vs_rejected"
        if policy_row.get("closed_obligation") or policy_row.get("closed_branch"):
            reason = "closed_vs_reduced"
        pairs.append(
            {
                "schema": "collatz_lab.proof_action_hard_pair",
                "version": 1,
                "example_id": f"hard_pair:{_digest({'trace': trace['trace_id'], 'better': better, 'worse': worse})}",
                "split": split,
                "gate": trace["gate"],
                "trace_id": trace["trace_id"],
                "state": state,
                "better_action": better,
                "worse_action": worse,
                "better_outcome_class": policy_row["outcome_class"],
                "worse_outcome_class": outcome["outcome_class"],
                "better_closure_reward": float(policy_row["closure_reward"]),
                "worse_closure_reward": float(outcome["closure_reward"]),
                "reason": reason,
            }
        )
        emitted += 1
        if emitted >= max_pairs:
            break
    return pairs


def build_hard_trace_dataset(
    *,
    traces: str | Path = "data/proof_action_v2_hard_traces/mined_hard_traces.jsonl",
    out: str | Path = "data/proof_action_v2_hard_traces",
    holdout_fraction: float = 0.2,
) -> dict[str, Any]:
    trace_rows = _load_jsonl(traces)
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    policy: list[dict[str, Any]] = []
    value: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    holdout: list[dict[str, Any]] = []
    for trace_index, trace in enumerate(trace_rows):
        split = "challenge" if (trace_index % max(2, int(1 / max(holdout_fraction, 0.01)))) == 0 else "train"
        if split == "challenge":
            holdout.append(
                {
                    "schema": "collatz_lab.proof_action_hard_holdout",
                    "version": 1,
                    "trace_id": trace["trace_id"],
                    "gate": trace["gate"],
                    "frontier_kind": trace.get("frontier_kind"),
                    "state": trace["start_state"],
                    "depth": trace["depth"],
                    "gate_progress_total": trace["gate_progress_total"],
                }
            )
        for step_index, step in enumerate(trace.get("actions") or [], start=1):
            row = _policy_row(trace, step, step_index=step_index, split=split)
            value.append(row)
            if split == "train":
                policy.append(row)
                pairs.extend(_pair_rows(trace, row, split=split))

    _write_jsonl(out_dir / "train_policy.jsonl", policy)
    _write_jsonl(out_dir / "train_value.jsonl", value)
    _write_jsonl(out_dir / "train_pairs.jsonl", pairs)
    _write_jsonl(out_dir / "challenge_holdout.jsonl", holdout)
    summary = {
        "schema": "collatz_lab.proof_action_hard_trace_dataset_summary",
        "version": 1,
        "trace_count": len(trace_rows),
        "train_policy_rows": len(policy),
        "train_value_rows": len(value),
        "train_pair_rows": len(pairs),
        "challenge_holdout_rows": len(holdout),
        "gate_counts": dict(Counter(trace.get("gate", "UNKNOWN") for trace in trace_rows)),
        "pair_reason_counts": dict(Counter(pair["reason"] for pair in pairs)),
        "paths": {
            "train_policy": str(out_dir / "train_policy.jsonl"),
            "train_value": str(out_dir / "train_value.jsonl"),
            "train_pairs": str(out_dir / "train_pairs.jsonl"),
            "challenge_holdout": str(out_dir / "challenge_holdout.jsonl"),
        },
    }
    (out_dir / "hard_trace_dataset_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "mining_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build policy/value/ranker rows from mined hard traces.")
    parser.add_argument("--traces", default="data/proof_action_v2_hard_traces/mined_hard_traces.jsonl")
    parser.add_argument("--out", default="data/proof_action_v2_hard_traces")
    parser.add_argument("--holdout-fraction", type=float, default=0.2)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(build_hard_trace_dataset(traces=args.traces, out=args.out, holdout_fraction=args.holdout_fraction))


if __name__ == "__main__":
    main()
