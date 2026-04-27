"""Leakage checks for proof-action frontier evaluation sets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_dsl import parse_action, serialize_action
from .proof_action_state import parse_state_facts


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_eval_rows(eval_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(eval_dir)
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.jsonl")):
        for row in _load_jsonl(path):
            copied = dict(row)
            copied.setdefault("eval_file", path.name)
            rows.append(copied)
    return rows


def _state(row: dict[str, Any]) -> str:
    return str(row.get("state", ""))


def _state_hash(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def _action_texts(row: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    if row.get("target_action_text"):
        out.add(str(row["target_action_text"]))
    if row.get("target_action"):
        try:
            out.add(serialize_action(row["target_action"]))
        except Exception:
            pass
    for item in row.get("candidates") or []:
        action = item.get("action")
        if isinstance(action, str):
            try:
                out.add(serialize_action(parse_action(action)))
            except Exception:
                out.add(action.strip())
        elif isinstance(action, dict):
            try:
                out.add(serialize_action(action))
            except Exception:
                pass
    return out


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_.:-]*|\d+", text))


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / max(len(left | right), 1)


def _fact_sets(rows: list[dict[str, Any]]) -> dict[str, set[Any]]:
    facts = {"residue": set(), "modulus": set(), "branch_id": set(), "lemma_id": set()}
    for row in rows:
        parsed = parse_state_facts(_state(row))
        for key in facts:
            if key in parsed:
                facts[key].add(parsed[key])
        for lemma in parsed.get("known_lemmas", []):
            facts["lemma_id"].add(str(lemma))
        for item in row.get("candidates") or []:
            action = item.get("action")
            try:
                parsed_action = parse_action(action) if isinstance(action, str) else action
            except Exception:
                continue
            for key in ("residue", "modulus", "branch_id", "lemma_id"):
                if key in parsed_action:
                    facts[key].add(parsed_action[key])
    return facts


def leakage_report(
    *,
    train_rows: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
    near_duplicate_threshold: float = 0.92,
) -> dict[str, Any]:
    train_states = {_state_hash(_state(row)) for row in train_rows}
    eval_states = [_state_hash(_state(row)) for row in eval_rows]
    train_actions = set().union(*(_action_texts(row) for row in train_rows)) if train_rows else set()
    eval_actions = set().union(*(_action_texts(row) for row in eval_rows)) if eval_rows else set()
    train_facts = _fact_sets(train_rows)
    eval_facts = _fact_sets(eval_rows)
    train_tokens = [_token_set(_state(row)) for row in train_rows]
    near_duplicates = 0
    for row in eval_rows:
        tokens = _token_set(_state(row))
        if any(_jaccard(tokens, train) >= near_duplicate_threshold for train in train_tokens[:5000]):
            near_duplicates += 1
    trace_duplicates = 0
    train_trace_sets = [_action_texts(row) for row in train_rows if _action_texts(row)]
    for row in eval_rows:
        actions = _action_texts(row)
        if actions and any(_jaccard(actions, train_actions_for_row) >= near_duplicate_threshold for train_actions_for_row in train_trace_sets[:5000]):
            trace_duplicates += 1
    exact_state_overlap = len(set(eval_states) & train_states)
    report = {
        "schema": "collatz_lab.proof_action_leakage_report",
        "version": 1,
        "train_row_count": len(train_rows),
        "eval_row_count": len(eval_rows),
        "exact_state_hash_overlap": exact_state_overlap,
        "exact_state_hash_overlap_rate": exact_state_overlap / max(len(eval_rows), 1),
        "exact_action_overlap": len(train_actions & eval_actions),
        "exact_action_overlap_rate": len(train_actions & eval_actions) / max(len(eval_actions), 1),
        "residue_overlap": len(train_facts["residue"] & eval_facts["residue"]),
        "modulus_overlap": len(train_facts["modulus"] & eval_facts["modulus"]),
        "branch_id_overlap": len(train_facts["branch_id"] & eval_facts["branch_id"]),
        "lemma_id_overlap": len(train_facts["lemma_id"] & eval_facts["lemma_id"]),
        "near_duplicate_state_rate": near_duplicates / max(len(eval_rows), 1),
        "near_duplicate_trace_rate": trace_duplicates / max(len(eval_rows), 1),
        "challenge_state_overlap_ok": exact_state_overlap == 0,
    }
    return report


def run_leakage_check(train: str | Path, eval_dir: str | Path, out: str | Path | None = None) -> dict[str, Any]:
    report = leakage_report(train_rows=_load_jsonl(train), eval_rows=load_eval_rows(eval_dir))
    if out:
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check train/eval leakage for proof-action frontier sets.")
    parser.add_argument("--train", default="data/proof_action_v2_ranker/train.jsonl")
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(run_leakage_check(args.train, args.eval_dir, args.out))


if __name__ == "__main__":
    main()
