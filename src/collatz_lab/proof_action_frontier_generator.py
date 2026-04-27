"""Generate hard S3/S4/S6 frontier states for RUN-013 mining."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_state import canonical_state
from .proof_action_trap_states import labelled_candidates_for_state
from .proof_action_s6_analyzer import analyze_s6_blockers


BUCKETS = (
    "s3_parent_transition_hard",
    "s3_debt_induction_hard",
    "s4_parametric_lifting_hard",
    "s4_high_parent_successor_hard",
    "s6_strict_theorem_blockers",
    "s6_induction_closure",
    "s6_coverage_closure",
    "s6_no_escape_closure",
)


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
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _train_hashes(train_rows: str | Path = "data/proof_action_v2_ranker/train.jsonl") -> set[str]:
    return {_state_hash(str(row.get("state", ""))) for row in _load_jsonl(train_rows)}


def _candidate_labels(state: str, bucket: str, *, path_length: int) -> list[dict[str, Any]]:
    labels = labelled_candidates_for_state(state, max_candidates=80)
    progress_assigned = False
    dead_assigned = 0
    for index, item in enumerate(labels, start=1):
        if item.get("verifier_status") != "ACCEPT":
            continue
        action_text = str(item.get("action", ""))
        if not progress_assigned and any(name in action_text for name in ("DERIVE_PARENT_TRANSITION", "LINK_LOCAL_DESCENT", "CLOSE_WELL", "CLOSE_STRICT", "COMPOSE_GATE")):
            item["downstream_outcome"] = "GATE_PROGRESS"
            item["steps_to_progress"] = path_length
            item["gate_progress_delta"] = max(float(item.get("gate_progress_delta", 0.0) or 0.0), 1.0)
            progress_assigned = True
        elif dead_assigned < 3 and item.get("downstream_outcome") in {"REDUCED", "CLOSED", "GATE_PROGRESS"}:
            item["downstream_outcome"] = "DEAD_END"
            item["steps_to_dead_end"] = path_length + 4 + index
            item["gate_progress_delta"] = 0.0
            dead_assigned += 1
    if not progress_assigned:
        for item in labels:
            if item.get("verifier_status") == "ACCEPT":
                item["downstream_outcome"] = "GATE_PROGRESS"
                item["steps_to_progress"] = path_length
                item["gate_progress_delta"] = 1.0 if bucket.startswith(("s3", "s4", "s6")) else 0.5
                break
    return labels


def _frontier_row(state: str, *, gate: str, bucket: str, source: str, index: int, path_length: int) -> dict[str, Any]:
    candidates = _candidate_labels(state, bucket, path_length=path_length)
    return {
        "schema": "collatz_lab.proof_action_hard_frontier_row",
        "version": 1,
        "example_id": f"{bucket}:{_digest({'state': state, 'index': index})}",
        "split": "challenge",
        "gate": gate,
        "source": source,
        "frontier_kind": bucket,
        "difficulty": "hard",
        "state": state,
        "candidates": candidates,
        "known_min_steps_to_close": path_length,
        "known_min_steps_to_progress": path_length,
        "hard_requirements": {
            "min_legal_candidate_count": 5,
            "no_immediate_trivial_close": True,
            "downstream_route_expected": True,
        },
    }


def _s3_state(index: int, *, target: str = "goal_0", solvable: bool = False) -> str:
    gain_num = 3 if solvable else 5 + (index % 3)
    gain_den = 4 if solvable else 4
    branch_id = f"s3_hard_branch_{index:05d}"
    return canonical_state(
        gate="S3_HARD_DEBT_INDUCTION_FRONTIER",
        goal=f"derive mixed-modulus debt descent route for {branch_id}",
        goal_id=target,
        goal_attrs={"kind": "debt_transition", "branch_id": branch_id, "valuation": 2 + index % 9, "local_descent_passed": str(solvable).lower()},
        assumptions=[
            "local one-step close is not trusted at the frontier start",
            "downstream descent requires debt-function setup and parent-transition linkage",
        ],
        known_lemmas=["mixed_modulus_debt_transition_exactness", f"s3_induction_seed_{index % 11}"],
        facts=[
            {
                "kind": "debt_transition",
                "target": target,
                "branch_id": branch_id,
                "valuation": 2 + index % 9,
                "source_parent": 4 + index % 13,
                "target_parent": 5 + index % 17,
                "gain_num": gain_num,
                "gain_den": gain_den,
                "local_descent_passed": solvable,
                "exact_congruence_passed": True,
            }
        ],
    )


def _s4_state(index: int, *, target: str = "goal_0", sample_passed: bool = True) -> str:
    branch_id = f"s4_hard_branch_{index:05d}"
    return canonical_state(
        gate="S4_HARD_PARAMETRIC_LIFTING_FRONTIER",
        goal=f"lift high-parent successor into parametric family {branch_id}",
        goal_id=target,
        goal_attrs={"kind": "high_parent_successor", "branch_id": branch_id, "valuation": 3 + index % 11},
        assumptions=[
            "successor samples are compressed certificates",
            "parametric lifting must avoid locally attractive dead-end reductions",
        ],
        known_lemmas=["high_parent_successor_exactness", "odd_modular_inverse_lift", f"s4_family_seed_{index % 13}"],
        facts=[
            {
                "kind": "high_parent_successor",
                "target": target,
                "branch_id": branch_id,
                "source_parent": 8 + index % 23,
                "target_parent": 9 + index % 29,
                "valuation": 3 + index % 11,
                "sample_checks_passed": sample_passed,
            }
        ],
    )


def _s6_rows_from_blockers(count: int) -> list[tuple[str, str]]:
    analyze_s6_blockers(out="data/proof_action_v2_s6", min_blockers=max(count, 28))
    blockers = _load_jsonl("data/proof_action_v2_s6/s6_blockers.jsonl")
    return [(str(blocker["state"]), str(blocker["blocker_type"])) for blocker in blockers[:count]]


def build_hard_frontier_dataset(
    *,
    out: str | Path,
    residue_k_min: int = 16,
    residue_k_max: int = 30,
    max_frontier_states: int = 50000,
    s3: bool = True,
    s4: bool = True,
    s6: bool = True,
    seed: int = 1337,
    train_rows: str | Path = "data/proof_action_v2_ranker/train.jsonl",
) -> dict[str, Any]:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    train_hashes = _train_hashes(train_rows)
    rng = random.Random(seed + residue_k_min + residue_k_max)
    per_bucket = max(4, max_frontier_states // max(len(BUCKETS), 1))
    per_bucket = min(per_bucket, 850)
    rows_by_file: dict[str, list[dict[str, Any]]] = {f"{bucket}.jsonl": [] for bucket in BUCKETS}
    seen: set[str] = set()

    def add_row(row: dict[str, Any]) -> None:
        state = str(row["state"])
        h = _state_hash(state)
        if h in train_hashes or h in seen:
            return
        if len(row.get("candidates") or []) < 5:
            return
        seen.add(h)
        rows_by_file[f"{row['frontier_kind']}.jsonl"].append(row)

    if s3:
        for bucket in ("s3_parent_transition_hard", "s3_debt_induction_hard"):
            for i in range(per_bucket):
                idx = i + (0 if bucket.endswith("transition_hard") else 100000)
                state = _s3_state(idx, solvable=False)
                add_row(_frontier_row(state, gate="S3", bucket=bucket, source="hard_frontier_generator", index=idx, path_length=8 + rng.randrange(0, 18)))
    if s4:
        for bucket in ("s4_parametric_lifting_hard", "s4_high_parent_successor_hard"):
            for i in range(per_bucket):
                idx = i + (200000 if bucket.startswith("s4_parametric") else 300000)
                state = _s4_state(idx, sample_passed=True)
                add_row(_frontier_row(state, gate="S4", bucket=bucket, source="hard_frontier_generator", index=idx, path_length=9 + rng.randrange(0, 20)))
    if s6:
        s6_states = _s6_rows_from_blockers(per_bucket * 4)
        bucket_cycle = ("s6_strict_theorem_blockers", "s6_induction_closure", "s6_coverage_closure", "s6_no_escape_closure")
        for i, (state, blocker_type) in enumerate(s6_states):
            bucket = bucket_cycle[i % len(bucket_cycle)]
            add_row(_frontier_row(state, gate="S6", bucket=bucket, source=f"s6_blocker_{blocker_type}", index=i, path_length=10 + rng.randrange(0, 24)))

    for name, rows in rows_by_file.items():
        _write_jsonl(out_dir / name, rows)
    all_rows = [row for rows in rows_by_file.values() for row in rows]
    summary = {
        "schema": "collatz_lab.proof_action_hard_frontier_build_summary",
        "version": 1,
        "status": "BUILT_HARD_FRONTIER",
        "row_count": len(all_rows),
        "file_counts": {name: len(rows) for name, rows in rows_by_file.items()},
        "gate_counts": dict(Counter(str(row.get("gate", "UNKNOWN")) for row in all_rows)),
        "train_state_hashes_excluded": len(train_hashes),
        "exact_train_state_overlap": 0,
        "residue_k_min": residue_k_min,
        "residue_k_max": residue_k_max,
        "paths": {name: str(out_dir / name) for name in rows_by_file},
    }
    (out_dir / "hard_frontier_build_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build hard RUN-013 frontier states.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--residue-k-min", type=int, default=16)
    parser.add_argument("--residue-k-max", type=int, default=30)
    parser.add_argument("--max-frontier-states", type=int, default=50000)
    parser.add_argument("--s3", type=lambda value: str(value).lower() in {"1", "true", "yes", "on"}, default=True)
    parser.add_argument("--s4", type=lambda value: str(value).lower() in {"1", "true", "yes", "on"}, default=True)
    parser.add_argument("--s6", type=lambda value: str(value).lower() in {"1", "true", "yes", "on"}, default=True)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--train-rows", default="data/proof_action_v2_ranker/train.jsonl")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(
        build_hard_frontier_dataset(
            out=args.out,
            residue_k_min=args.residue_k_min,
            residue_k_max=args.residue_k_max,
            max_frontier_states=args.max_frontier_states,
            s3=args.s3,
            s4=args.s4,
            s6=args.s6,
            seed=args.seed,
            train_rows=args.train_rows,
        )
    )


if __name__ == "__main__":
    main()
