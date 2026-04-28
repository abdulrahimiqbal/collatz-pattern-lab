"""Build listwise candidate-selector datasets for proof-action frontier states."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_candidate_selector import (
    LOW_UTILITY_OUTCOMES,
    candidate_utility,
    infer_target_objective,
    objective_threshold,
    selector_candidate_record,
)
from .proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import serialize_action
from .proof_action_outcome import classify_action_outcome
from .proof_action_trap_states import parse_candidate_action


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _read_dir_jsonl(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    root = Path(path)
    if not root.exists():
        return []
    if root.is_file():
        return _read_jsonl(root)
    rows: list[dict[str, Any]] = []
    for file_path in sorted(root.glob("*.jsonl")):
        rows.extend(_read_jsonl(file_path))
    return rows


def _normalise_candidate(
    item: dict[str, Any],
    *,
    state: str,
    gate: str,
    target_objective: str,
) -> dict[str, Any] | None:
    action = parse_candidate_action(item) if "action" in item else item
    if action is None:
        return None
    action_text = serialize_action(action)
    check = verify_action_for_state(action, state)
    outcome = classify_action_outcome(action, state, check).to_dict()
    enriched = {
        **item,
        "action": action_text,
        "action_text": action_text,
        "accepted": bool(check.accepted),
        "verifier_status": "ACCEPT" if check.accepted else "REJECT",
        "outcome": item.get("outcome") if isinstance(item.get("outcome"), dict) else outcome,
        "gate": gate,
    }
    record = selector_candidate_record(enriched, gate=gate, target_objective=target_objective)
    if not record["action_text"]:
        return None
    return record


def candidate_set_from_frontier_row(
    row: dict[str, Any],
    *,
    min_candidates: int = 5,
    require_gate_progress_candidate: bool = True,
    require_accepted_low_utility_candidate: bool = True,
    require_oracle_gap: float = 0.75,
) -> dict[str, Any] | None:
    if str(row.get("difficulty", "")).lower() == "easy":
        return None
    state = str(row.get("state") or row.get("start_state") or "")
    if not state:
        return None
    gate = str(row.get("gate", "UNKNOWN"))
    target_objective = infer_target_objective(row)
    raw_candidates = [item for item in row.get("candidates") or [] if isinstance(item, dict)]
    if not raw_candidates:
        raw_candidates = [{"action": serialize_action(action)} for action in legal_action_candidates_from_state(state, max_candidates=80)]

    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_candidates:
        record = _normalise_candidate(item, state=state, gate=gate, target_objective=target_objective)
        if record is None or record["action_text"] in seen:
            continue
        seen.add(record["action_text"])
        candidates.append(record)

    if len(candidates) < min_candidates:
        return None
    accepted = [item for item in candidates if float(item["utility"]) > -1.0]
    low_utility = [item for item in accepted if item["outcome_class"] in LOW_UTILITY_OUTCOMES]
    objective_good = [
        item
        for item in candidates
        if candidate_utility(item, target_objective) >= objective_threshold(target_objective)
    ]
    if len(accepted) < 2:
        return None
    if require_accepted_low_utility_candidate and not low_utility:
        return None
    if require_gate_progress_candidate and not objective_good:
        return None

    accepted_utilities = [float(item["utility"]) for item in accepted]
    best_utility = max(float(item["utility"]) for item in candidates)
    median_accepted_utility = float(statistics.median(accepted_utilities))
    if best_utility - median_accepted_utility < require_oracle_gap:
        return None
    best_index = max(range(len(candidates)), key=lambda index: float(candidates[index]["utility"]))
    return {
        "schema": "collatz_lab.proof_action_candidate_selector_set",
        "version": 1,
        "state": state,
        "gate": gate,
        "target_objective": target_objective,
        "frontier_kind": row.get("frontier_kind"),
        "source_example_id": row.get("example_id") or row.get("trace_id") or row.get("blocker_id"),
        "candidates": candidates,
        "best_candidate_index": best_index,
        "oracle_best_utility": best_utility,
        "median_accepted_utility": median_accepted_utility,
        "oracle_gap": best_utility - median_accepted_utility,
    }


def _candidate_sets_from_s6_rows(rows: list[dict[str, Any]], **filters: Any) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if "candidate_actions" not in row:
            continue
        synthetic = {
            "state": row.get("state", ""),
            "gate": row.get("gate", "S6"),
            "frontier_kind": "s6_blocker",
            "example_id": row.get("blocker_id"),
            "candidates": [{"action": serialize_action(action)} for action in row.get("candidate_actions") or []],
        }
        built = candidate_set_from_frontier_row(synthetic, **filters)
        if built is not None:
            out.append(built)
    return out


def build_candidate_selector_dataset(
    *,
    frontier_dir: str | Path,
    hard_trace_dir: str | Path | None,
    s6_dir: str | Path | None,
    out: str | Path,
    min_candidates: int = 5,
    require_gate_progress_candidate: bool = True,
    require_accepted_low_utility_candidate: bool = True,
    require_oracle_gap: float = 0.75,
    seed: int = 1337,
) -> dict[str, Any]:
    filters = {
        "min_candidates": min_candidates,
        "require_gate_progress_candidate": require_gate_progress_candidate,
        "require_accepted_low_utility_candidate": require_accepted_low_utility_candidate,
        "require_oracle_gap": require_oracle_gap,
    }
    rows = _read_dir_jsonl(frontier_dir)
    rows.extend(_read_dir_jsonl(hard_trace_dir))
    candidate_sets = [built for row in rows if (built := candidate_set_from_frontier_row(row, **filters)) is not None]
    candidate_sets.extend(_candidate_sets_from_s6_rows(_read_dir_jsonl(s6_dir), **filters))

    rng = random.Random(seed)
    rng.shuffle(candidate_sets)
    train_cut = int(0.8 * len(candidate_sets))
    val_cut = int(0.9 * len(candidate_sets))
    splits = {
        "train": candidate_sets[:train_cut],
        "val": candidate_sets[train_cut:val_cut],
        "hard_holdout": candidate_sets[val_cut:],
    }
    for split, split_rows in splits.items():
        for row in split_rows:
            row["split"] = "challenge" if split == "hard_holdout" else split

    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "train": out_dir / "train_candidate_sets.jsonl",
        "val": out_dir / "val_candidate_sets.jsonl",
        "hard_holdout": out_dir / "hard_holdout_candidate_sets.jsonl",
    }
    for split, path in paths.items():
        rows_for_split = splits[split]
        path.write_text(
            "\n".join(json.dumps(row, sort_keys=True) for row in rows_for_split) + ("\n" if rows_for_split else ""),
            encoding="utf-8",
        )

    summary = {
        "schema": "collatz_lab.proof_action_candidate_selector_dataset_summary",
        "version": 1,
        "candidate_set_count": len(candidate_sets),
        "train_candidate_sets": len(splits["train"]),
        "val_candidate_sets": len(splits["val"]),
        "hard_holdout_candidate_sets": len(splits["hard_holdout"]),
        "min_candidates": min_candidates,
        "require_gate_progress_candidate": require_gate_progress_candidate,
        "require_accepted_low_utility_candidate": require_accepted_low_utility_candidate,
        "require_oracle_gap": require_oracle_gap,
        "target_objective_counts": dict(Counter(str(row.get("target_objective", "UNKNOWN")) for row in candidate_sets)),
        "paths": {key: str(path) for key, path in paths.items()},
    }
    (out_dir / "candidate_selector_dataset_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _bool_arg(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "y"}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build proof-action listwise candidate selector data.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--frontier-dir", required=True)
    build.add_argument("--hard-trace-dir")
    build.add_argument("--s6-dir")
    build.add_argument("--out", required=True)
    build.add_argument("--min-candidates", type=int, default=5)
    build.add_argument("--require-gate-progress-candidate", type=_bool_arg, default=True)
    build.add_argument("--require-accepted-low-utility-candidate", type=_bool_arg, default=True)
    build.add_argument("--require-oracle-gap", type=float, default=0.75)
    build.add_argument("--seed", type=int, default=1337)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.command == "build":
        summary = build_candidate_selector_dataset(
            frontier_dir=args.frontier_dir,
            hard_trace_dir=args.hard_trace_dir,
            s6_dir=args.s6_dir,
            out=args.out,
            min_candidates=args.min_candidates,
            require_gate_progress_candidate=args.require_gate_progress_candidate,
            require_accepted_low_utility_candidate=args.require_accepted_low_utility_candidate,
            require_oracle_gap=args.require_oracle_gap,
            seed=args.seed,
        )
        Console().print(summary)


if __name__ == "__main__":
    main()
