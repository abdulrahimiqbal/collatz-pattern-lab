"""Build the RUN-014 hard-curriculum proof-action dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_decode import verify_action_for_state
from .proof_action_dsl import parse_action, serialize_action
from .proof_action_leakage import leakage_report
from .proof_action_outcome import classify_action_outcome
from .proof_action_trap_states import labelled_candidates_for_state
from .proof_action_trap_states import parse_candidate_action


def _digest(data: Any, size: int = 16) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:size]


def _state_hash(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _read_rows(directory: str | Path, *names: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    root = Path(directory)
    for name in names:
        rows.extend(_load_jsonl(root / name))
    return rows


def _with_mix_fields(
    row: dict[str, Any],
    *,
    source_family: str,
    sample_weight: float,
    split: str | None = None,
) -> dict[str, Any]:
    copied = dict(row)
    copied["mix_source"] = source_family
    copied["source_family"] = source_family
    copied["sample_weight"] = float(sample_weight)
    copied["split"] = split or str(copied.get("split", "train"))
    copied.setdefault("example_id", f"{source_family}:{_digest(copied)}")
    return copied


def _policy_from_s6_lemma(row: dict[str, Any], *, action_key: str, split: str, sample_weight: float) -> dict[str, Any] | None:
    action = row.get(action_key)
    state = str(row.get("state", ""))
    if not isinstance(action, dict) or not state:
        return None
    action_text = serialize_action(action)
    check = verify_action_for_state(action, state)
    outcome = classify_action_outcome(action, state, check).to_dict()
    return {
        "schema": "collatz_lab.proof_action_hard_mix_s6_row",
        "version": 1,
        "example_id": f"s6_mix:{_digest({'state': state, 'action': action_text})}",
        "split": split,
        "gate": "S6",
        "state": state,
        "target_action": action,
        "target_action_text": action_text,
        "verifier_status": "ACCEPT" if check.accepted else "REJECT",
        "reward": outcome["closure_reward"],
        "closure_reward": outcome["closure_reward"],
        "closed_obligation": outcome["closed_obligation"],
        "closed_branch": outcome["closed_branch"],
        "eventually_closed": bool(check.accepted and float(outcome.get("gate_progress_delta", 0.0) or 0.0) > 0),
        "distance_to_close": 1 if outcome["closed_obligation"] else None,
        "outcome_class": outcome["outcome_class"],
        "gate_progress_delta": outcome["gate_progress_delta"],
        "net_goal_delta": outcome["net_goal_delta"],
        "source": "s6_blocker_lemma",
        "mix_source": "s6_lemma",
        "source_family": "s6_lemma",
        "sample_weight": float(sample_weight),
        "blocker_id": row.get("blocker_id"),
        "lemma_id": row.get("lemma_id"),
        "blocker_type": row.get("blocker_type"),
    }


def _s6_pair(row: dict[str, Any], *, split: str, sample_weight: float) -> dict[str, Any] | None:
    better = row.get("verify_action_text")
    worse_action = dict(row.get("verify_action") or {})
    state = str(row.get("state", ""))
    if not better or not worse_action or not state:
        return None
    worse_action["status"] = "REJECT" if worse_action.get("status") == "ACCEPT" else "ACCEPT"
    try:
        worse = serialize_action(worse_action)
    except Exception:
        return None
    return {
        "schema": "collatz_lab.proof_action_hard_mix_pair",
        "version": 1,
        "example_id": f"s6_pair:{_digest({'state': state, 'better': better, 'worse': worse})}",
        "split": split,
        "gate": "S6",
        "state": state,
        "better_action": str(better),
        "worse_action": worse,
        "better_outcome_class": "VERIFIER_ACCEPTED_GATE_PROGRESS",
        "worse_outcome_class": "PARSE_VALID_BUT_REJECTED",
        "better_closure_reward": 1.25,
        "worse_closure_reward": -0.5,
        "reason": "s6_accepted_vs_rejected",
        "mix_source": "s6_lemma",
        "source_family": "s6_lemma",
        "sample_weight": float(sample_weight),
    }


def _candidate_distance(candidate: dict[str, Any]) -> int | None:
    for key in ("steps_to_progress", "steps_to_close", "steps_to_dead_end"):
        if candidate.get(key) is not None:
            try:
                return int(candidate[key])
            except Exception:
                return None
    return None


def _frontier_candidate_policy_row(
    *,
    source_row: dict[str, Any],
    candidate: dict[str, Any],
    source_family: str,
    sample_weight: float,
) -> dict[str, Any] | None:
    action = parse_candidate_action(candidate)
    state = str(source_row.get("state", ""))
    if action is None or not state:
        return None
    action_text = serialize_action(action)
    check = verify_action_for_state(action, state)
    outcome = classify_action_outcome(action, state, check).to_dict()
    downstream = str(candidate.get("downstream_outcome", ""))
    labelled_gate_delta = float(candidate.get("gate_progress_delta", outcome.get("gate_progress_delta", 0.0)) or 0.0)
    if downstream == "GATE_PROGRESS":
        labelled_gate_delta = max(labelled_gate_delta, 1.0)
        outcome["gate_progress_delta"] = labelled_gate_delta
        outcome["strict_progress"] = True
        outcome["outcome_class"] = "VERIFIER_ACCEPTED_GATE_PROGRESS"
        outcome["closure_reward"] = max(float(outcome.get("closure_reward", 0.0) or 0.0), 1.25)
    return {
        "schema": "collatz_lab.proof_action_hard_mix_frontier_row",
        "version": 1,
        "example_id": f"frontier_mix:{_digest({'state': state, 'action': action_text, 'source': source_row.get('example_id')})}",
        "split": "train",
        "gate": source_row.get("gate"),
        "state": state,
        "target_action": action,
        "target_action_text": action_text,
        "verifier_status": "ACCEPT" if check.accepted else "REJECT",
        "reward": outcome["closure_reward"],
        "closure_reward": outcome["closure_reward"],
        "closed_obligation": outcome["closed_obligation"],
        "closed_branch": outcome["closed_branch"],
        "eventually_closed": downstream in {"GATE_PROGRESS", "CLOSED"} or bool(outcome["closed_obligation"] or outcome["closed_branch"]),
        "distance_to_close": _candidate_distance(candidate),
        "outcome_class": outcome["outcome_class"],
        "gate_progress_delta": outcome["gate_progress_delta"],
        "net_goal_delta": outcome["net_goal_delta"],
        "source": "hard_frontier_candidate",
        "mix_source": source_family,
        "source_family": source_family,
        "sample_weight": float(sample_weight),
        "frontier_kind": source_row.get("frontier_kind"),
        "downstream_outcome": downstream,
    }


def _frontier_pair(
    *,
    source_row: dict[str, Any],
    better: dict[str, Any],
    worse: dict[str, Any],
    source_family: str,
    sample_weight: float,
) -> dict[str, Any] | None:
    better_action = parse_candidate_action(better)
    worse_action = parse_candidate_action(worse)
    state = str(source_row.get("state", ""))
    if better_action is None or worse_action is None or not state:
        return None
    better_text = serialize_action(better_action)
    worse_text = serialize_action(worse_action)
    worse_downstream = str(worse.get("downstream_outcome", ""))
    reason = "accepted_good_vs_accepted_dead_end" if worse_downstream in {"DEAD_END", "BRANCH_EXPLOSION"} else "gate_progress_vs_rejected"
    return {
        "schema": "collatz_lab.proof_action_hard_mix_frontier_pair",
        "version": 1,
        "example_id": f"frontier_pair:{_digest({'state': state, 'better': better_text, 'worse': worse_text})}",
        "split": "train",
        "gate": source_row.get("gate"),
        "state": state,
        "better_action": better_text,
        "worse_action": worse_text,
        "better_outcome_class": "VERIFIER_ACCEPTED_GATE_PROGRESS",
        "worse_outcome_class": str(worse.get("local_outcome", "UNKNOWN")),
        "better_closure_reward": 1.25,
        "worse_closure_reward": float((worse.get("outcome") or {}).get("closure_reward", -0.5) if isinstance(worse.get("outcome"), dict) else -0.5),
        "reason": reason,
        "mix_source": source_family,
        "source_family": source_family,
        "sample_weight": float(sample_weight),
        "frontier_kind": source_row.get("frontier_kind"),
    }


def _frontier_gate_progress_rows(
    frontier_dir: str | Path | None,
    *,
    sample_weight: float,
    max_rows: int | None,
    rng: random.Random,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not frontier_dir:
        return [], []
    root = Path(frontier_dir)
    if not root.exists():
        return [], []
    policy_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.jsonl")):
        source_rows.extend(_load_jsonl(path))
    rng.shuffle(source_rows)
    if max_rows is not None and max_rows > 0:
        source_rows = source_rows[:max_rows]
    for row in source_rows:
        candidates = [item for item in row.get("candidates") or [] if isinstance(item, dict)]
        progress = [
            item
            for item in candidates
            if item.get("verifier_status") == "ACCEPT"
            and (
                item.get("downstream_outcome") == "GATE_PROGRESS"
                or float(item.get("gate_progress_delta", 0.0) or 0.0) > 0
            )
        ]
        if not progress:
            continue
        dead_or_bad = [
            item
            for item in candidates
            if item not in progress
            and (
                item.get("verifier_status") != "ACCEPT"
                or item.get("downstream_outcome") in {"DEAD_END", "BRANCH_EXPLOSION"}
            )
        ]
        for item in progress[:2]:
            policy = _frontier_candidate_policy_row(
                source_row=row,
                candidate=item,
                source_family="frontier_gate_progress",
                sample_weight=sample_weight,
            )
            if policy is not None:
                policy_rows.append(policy)
            for worse in dead_or_bad[:4]:
                pair = _frontier_pair(
                    source_row=row,
                    better=item,
                    worse=worse,
                    source_family="frontier_gate_progress_pairwise",
                    sample_weight=sample_weight,
                )
                if pair is not None:
                    pair_rows.append(pair)
    return policy_rows, pair_rows


def _holdout_frontier_from_trace_holdout(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        state = str(row.get("state", ""))
        if not state:
            continue
        out.append(
            {
                "schema": "collatz_lab.proof_action_hard_mix_holdout",
                "version": 1,
                "example_id": f"hard_holdout:{_digest({'trace': row.get('trace_id'), 'state': state})}",
                "split": "challenge",
                "gate": row.get("gate"),
                "source": "run013_hard_trace_holdout",
                "frontier_kind": row.get("frontier_kind", "hard_trace_holdout"),
                "difficulty": "hard",
                "state": state,
                "depth": row.get("depth"),
                "gate_progress_total": row.get("gate_progress_total"),
                "candidates": labelled_candidates_for_state(state, max_candidates=80),
                "known_min_steps_to_progress": row.get("depth"),
                "known_min_steps_to_close": row.get("depth"),
            }
        )
    return out


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = (str(row.get("state", "")), str(row.get("target_action_text", "")), str(row.get("mix_source", row.get("source", ""))))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def build_hard_mix_dataset(
    *,
    original_dir: str | Path = "data/proof_action_v2",
    ranker_dir: str | Path = "data/proof_action_v2_ranker",
    hard_trace_dir: str | Path = "data/proof_action_v2_hard_traces",
    s6_dir: str | Path = "data/proof_action_v2_s6",
    frontier_dir: str | Path | None = None,
    out: str | Path = "data/proof_action_v2_hard_mix",
    hard_weight: float = 4.0,
    s6_weight: float = 5.0,
    ranker_weight: float = 2.0,
    frontier_gate_progress_weight: float = 12.0,
    max_frontier_gate_progress_rows: int | None = None,
    holdout_hard_traces: bool = True,
    seed: int = 1337,
) -> dict[str, Any]:
    rng = random.Random(seed)
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    hard_holdout_raw = _read_rows(hard_trace_dir, "challenge_holdout.jsonl") if holdout_hard_traces else []
    hard_holdout_hashes = {_state_hash(str(row.get("state", ""))) for row in hard_holdout_raw}

    original_rows = _read_rows(original_dir, "train_policy.jsonl", "train.jsonl")
    if not original_rows:
        original_rows = [row for row in _read_rows(original_dir, "rows.jsonl") if row.get("split") == "train"]
    original_val = _read_rows(original_dir, "val.jsonl")
    original_test = _read_rows(original_dir, "test.jsonl")

    ranker_value = _read_rows(ranker_dir, "train_value.jsonl", "train.jsonl")
    ranker_pairs = _read_rows(ranker_dir, "train_pairs.jsonl")
    hard_policy = [row for row in _read_rows(hard_trace_dir, "train_policy.jsonl") if row.get("split") == "train"]
    hard_value = [row for row in _read_rows(hard_trace_dir, "train_value.jsonl") if row.get("split") == "train"]
    hard_pairs = [row for row in _read_rows(hard_trace_dir, "train_pairs.jsonl") if row.get("split") == "train"]
    s6_rows = _read_rows(s6_dir, "s6_candidate_lemmas.jsonl")
    blockers_by_id = {str(row.get("blocker_id")): row for row in _read_rows(s6_dir, "s6_blockers.jsonl")}
    for row in s6_rows:
        blocker = blockers_by_id.get(str(row.get("blocker_id")))
        if blocker and not row.get("state"):
            row["state"] = blocker.get("state")
        if blocker and not row.get("blocker_type"):
            row["blocker_type"] = blocker.get("blocker_type")
    rng.shuffle(s6_rows)
    s6_holdout_source = s6_rows[: max(1, len(s6_rows) // 5)]
    s6_train_source = s6_rows[max(1, len(s6_rows) // 5) :]
    s6_holdout_lemma_ids = {str(row.get("lemma_id")) for row in s6_holdout_source}
    s6_holdout_hashes = {_state_hash(str(row.get("state", ""))) for row in s6_holdout_source}
    s6_train_policy = []
    s6_train_pairs = []
    for row in s6_train_source:
        split = "train"
        proposed = _policy_from_s6_lemma(row, action_key="candidate_action", split=split, sample_weight=s6_weight)
        verified = _policy_from_s6_lemma(row, action_key="verify_action", split=split, sample_weight=s6_weight)
        if proposed:
            s6_train_policy.append(proposed)
        if verified:
            s6_train_policy.append(verified)
        pair = _s6_pair(row, split=split, sample_weight=s6_weight)
        if pair:
            s6_train_pairs.append(pair)
    frontier_policy, frontier_pairs = _frontier_gate_progress_rows(
        frontier_dir,
        sample_weight=frontier_gate_progress_weight,
        max_rows=max_frontier_gate_progress_rows,
        rng=rng,
    )

    def keep_train(row: dict[str, Any]) -> bool:
        state_hash = _state_hash(str(row.get("state", "")))
        return state_hash not in hard_holdout_hashes and state_hash not in s6_holdout_hashes

    train_policy = []
    train_policy.extend(_with_mix_fields(row, source_family="original_v2", sample_weight=1.0) for row in original_rows if keep_train(row))
    train_policy.extend(_with_mix_fields(row, source_family="ranker_replay", sample_weight=ranker_weight, split="train") for row in ranker_value if row.get("verifier_status") == "ACCEPT" and keep_train(row))
    train_policy.extend(_with_mix_fields(row, source_family="hard_trace", sample_weight=hard_weight, split="train") for row in hard_policy if keep_train(row))
    train_policy.extend(row for row in s6_train_policy if keep_train(row))
    train_policy.extend(row for row in frontier_policy if keep_train(row))
    train_policy = _dedupe_rows(train_policy)

    train_value = []
    train_value.extend(_with_mix_fields(row, source_family="original_v2", sample_weight=1.0) for row in original_rows if keep_train(row))
    train_value.extend(_with_mix_fields(row, source_family="ranker_replay", sample_weight=ranker_weight, split="train") for row in ranker_value if keep_train(row))
    train_value.extend(_with_mix_fields(row, source_family="hard_trace", sample_weight=hard_weight, split="train") for row in hard_value if keep_train(row))
    train_value.extend(row for row in s6_train_policy if keep_train(row))
    train_value.extend(row for row in frontier_policy if keep_train(row))
    train_value = _dedupe_rows(train_value)

    def pair_keep(row: dict[str, Any]) -> bool:
        return _state_hash(str(row.get("state", ""))) not in hard_holdout_hashes

    train_pairs = []
    train_pairs.extend(_with_mix_fields(row, source_family="ranker_pairwise", sample_weight=ranker_weight, split="train") for row in ranker_pairs if pair_keep(row))
    for row in hard_pairs:
        weight = hard_weight
        if row.get("reason") == "accepted_good_vs_accepted_dead_end":
            weight *= 2.0
        train_pairs.append(_with_mix_fields(row, source_family="hard_trace_pairwise", sample_weight=weight, split="train"))
    train_pairs.extend(row for row in s6_train_pairs if pair_keep(row))
    train_pairs.extend(row for row in frontier_pairs if pair_keep(row))

    val = [_with_mix_fields(row, source_family="original_v2_val", sample_weight=1.0, split="val") for row in original_val]
    test = [_with_mix_fields(row, source_family="original_v2_test", sample_weight=1.0, split="test") for row in original_test]
    hard_holdout = _holdout_frontier_from_trace_holdout(hard_holdout_raw)
    s6_holdout = []
    for row in s6_holdout_source:
        state = str(row.get("state", ""))
        s6_holdout.append(
            {
                "schema": "collatz_lab.proof_action_s6_holdout",
                "version": 1,
                "example_id": f"s6_holdout:{_digest({'lemma': row.get('lemma_id'), 'state': state})}",
                "split": "challenge",
                "gate": "S6",
                "source": "s6_blocker_lemma_holdout",
                "frontier_kind": "s6_lemma_holdout",
                "difficulty": "challenge",
                "state": state,
                "lemma_id": row.get("lemma_id"),
                "blocker_id": row.get("blocker_id"),
                "blocker_type": row.get("blocker_type"),
                "candidate_action": row.get("candidate_action"),
                "verify_action": row.get("verify_action"),
                "verifier_status": row.get("verifier_status"),
                "candidates": labelled_candidates_for_state(state, max_candidates=80),
            }
        )

    _write_jsonl(out_dir / "train_policy.jsonl", train_policy)
    _write_jsonl(out_dir / "train_value.jsonl", train_value)
    _write_jsonl(out_dir / "train_pairs.jsonl", train_pairs)
    _write_jsonl(out_dir / "val.jsonl", val)
    _write_jsonl(out_dir / "test.jsonl", test)
    _write_jsonl(out_dir / "hard_challenge_holdout.jsonl", hard_holdout)
    _write_jsonl(out_dir / "s6_challenge_holdout.jsonl", s6_holdout)
    _write_jsonl(out_dir / "rows.jsonl", train_value + val + test)

    train_eval_rows = train_value + train_policy
    eval_rows = hard_holdout + s6_holdout
    leak = leakage_report(train_rows=train_eval_rows, eval_rows=eval_rows)
    leak["hard_holdout_state_count"] = len(hard_holdout)
    leak["s6_holdout_state_count"] = len(s6_holdout)
    leak["s6_holdout_lemma_overlap_with_train"] = len(
        s6_holdout_lemma_ids
        & {
            str(row.get("lemma_id"))
            for row in s6_train_policy
            if row.get("lemma_id")
        }
    )
    (out_dir / "leakage_report.json").write_text(json.dumps(leak, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "schema": "collatz_lab.proof_action_hard_mix_summary",
        "version": 1,
        "status": "BUILT_PROOF_ACTION_HARD_MIX",
        "seed": seed,
        "weights": {"original": 1.0, "ranker": ranker_weight, "hard": hard_weight, "s6": s6_weight, "frontier_gate_progress": frontier_gate_progress_weight},
        "train_policy_rows": len(train_policy),
        "train_value_rows": len(train_value),
        "train_pair_rows": len(train_pairs),
        "val_rows": len(val),
        "test_rows": len(test),
        "hard_challenge_holdout_rows": len(hard_holdout),
        "s6_challenge_holdout_rows": len(s6_holdout),
        "source_counts_policy": dict(Counter(str(row.get("mix_source")) for row in train_policy)),
        "source_counts_value": dict(Counter(str(row.get("mix_source")) for row in train_value)),
        "pair_reason_counts": dict(Counter(str(row.get("reason")) for row in train_pairs)),
        "gate_counts_policy": dict(Counter(str(row.get("gate", "UNKNOWN")) for row in train_policy)),
        "frontier_gate_progress_policy_rows": len(frontier_policy),
        "frontier_gate_progress_pair_rows": len(frontier_pairs),
        "leakage": leak,
        "paths": {
            "train_policy": str(out_dir / "train_policy.jsonl"),
            "train_value": str(out_dir / "train_value.jsonl"),
            "train_pairs": str(out_dir / "train_pairs.jsonl"),
            "hard_challenge_holdout": str(out_dir / "hard_challenge_holdout.jsonl"),
            "s6_challenge_holdout": str(out_dir / "s6_challenge_holdout.jsonl"),
        },
    }
    (out_dir / "mix_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _bool_arg(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"expected boolean, got {value!r}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build RUN-014 hard-curriculum proof-action data.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--original-dir", default="data/proof_action_v2")
    build.add_argument("--ranker-dir", default="data/proof_action_v2_ranker")
    build.add_argument("--hard-trace-dir", default="data/proof_action_v2_hard_traces")
    build.add_argument("--s6-dir", default="data/proof_action_v2_s6")
    build.add_argument("--frontier-dir", default=None)
    build.add_argument("--out", required=True)
    build.add_argument("--hard-weight", type=float, default=4.0)
    build.add_argument("--s6-weight", type=float, default=5.0)
    build.add_argument("--ranker-weight", type=float, default=2.0)
    build.add_argument("--frontier-gate-progress-weight", type=float, default=12.0)
    build.add_argument("--max-frontier-gate-progress-rows", type=int, default=None)
    build.add_argument("--holdout-hard-traces", type=_bool_arg, default=True)
    build.add_argument("--seed", type=int, default=1337)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.command == "build":
        report = build_hard_mix_dataset(
            original_dir=args.original_dir,
            ranker_dir=args.ranker_dir,
            hard_trace_dir=args.hard_trace_dir,
            s6_dir=args.s6_dir,
            frontier_dir=args.frontier_dir,
            out=args.out,
            hard_weight=args.hard_weight,
            s6_weight=args.s6_weight,
            ranker_weight=args.ranker_weight,
            frontier_gate_progress_weight=args.frontier_gate_progress_weight,
            max_frontier_gate_progress_rows=args.max_frontier_gate_progress_rows,
            holdout_hard_traces=args.holdout_hard_traces,
            seed=args.seed,
        )
        Console().print(report)


if __name__ == "__main__":
    main()
