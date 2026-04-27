"""Verifier-guided search loop for typed proof-action agents."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from rich.console import Console

from .proof_action_decode import dedupe_candidates, legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import serialize_action
from .proof_action_model import load_checkpoint, score_action_components
from .proof_action_outcome import classify_action_outcome
from .utils import load_yaml


def _load_rows(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _config(path: str | Path) -> dict[str, Any]:
    cfg = load_yaml(path)
    data = cfg.get("data", {})
    output = cfg.get("output", {})
    search = cfg.get("search", {})
    out_dir = str(output.get("dir") or cfg.get("output_dir") or "reports/proof_action_v2/run")
    return {
        "rows": str(data.get("rows") or data.get("dataset") or Path(data.get("dir", "data/proof_action_v2")) / "rows.jsonl"),
        "checkpoint": str(search.get("checkpoint") or Path(out_dir) / "final_checkpoint.pt"),
        "out_dir": out_dir,
        "max_states": int(search.get("max_states", 64)),
        "beam_size": int(search.get("beam_size", search.get("beam_width", 50))),
        "candidates_per_state": int(search.get("candidates_per_state", search.get("beam_size", 50))),
        "run_id": str((cfg.get("run") or {}).get("id", "RUN-010-proof-action-v2-small-a100")),
        "ranking": ranking_weights_from_config(cfg),
    }


def ranking_weights_from_config(cfg: dict[str, Any]) -> dict[str, float]:
    ranking = cfg.get("ranking", {})
    return {
        "verifier_accept_bonus": float(ranking.get("verifier_accept_bonus", 10.0)),
        "verifier_reject_penalty": float(ranking.get("verifier_reject_penalty", -10.0)),
        "closure_bonus": float(ranking.get("closure_bonus", 5.0)),
        "branch_close_bonus": float(ranking.get("branch_close_bonus", 8.0)),
        "gate_progress_weight": float(ranking.get("gate_progress_weight", 10.0)),
        "ranker_weight": float(ranking.get("ranker_weight", 2.0)),
        "value_weight": float(ranking.get("value_weight", 1.0)),
        "policy_weight": float(ranking.get("policy_weight", 0.2)),
        "goal_creation_penalty": float(ranking.get("goal_creation_penalty", 0.25)),
        "duplicate_action_penalty": float(ranking.get("duplicate_action_penalty", 2.0)),
    }


def score_ranked_candidate(components: dict[str, float], outcome: dict[str, Any], weights: dict[str, float]) -> float:
    score = weights["verifier_accept_bonus"] if outcome.get("accepted") else weights["verifier_reject_penalty"]
    if outcome.get("closed_obligation"):
        score += weights["closure_bonus"]
    if outcome.get("closed_branch"):
        score += weights["branch_close_bonus"]
    score += weights["gate_progress_weight"] * float(outcome.get("gate_progress_delta", 0.0) or 0.0)
    score += weights["ranker_weight"] * float(components.get("ranker_score", 0.0) or 0.0)
    score += weights["value_weight"] * float(components.get("value_score", 0.0) or 0.0)
    score += weights["policy_weight"] * float(components.get("policy_score", 0.0) or 0.0)
    score -= weights["goal_creation_penalty"] * max(0, int(outcome.get("net_goal_delta", 0) or 0))
    return float(score)


def rank_candidate_actions(
    *,
    model: Any,
    tokenizer: Any,
    state: str,
    candidates: list[dict[str, Any]],
    max_state_len: int,
    max_action_len: int,
    weights: dict[str, float],
    max_candidates: int | None = None,
) -> list[dict[str, Any]]:
    unique = dedupe_candidates(candidates, max_candidates=max_candidates)
    texts = [serialize_action(candidate) for candidate in unique]
    components = score_action_components(
        model,
        tokenizer,
        state,
        texts,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
    )
    ranked: list[dict[str, Any]] = []
    for candidate, text, model_parts in zip(unique, texts, components, strict=True):
        check = verify_action_for_state(candidate, state)
        outcome = classify_action_outcome(candidate, state, check).to_dict()
        ranked.append(
            {
                "action": candidate,
                "action_text": text,
                "model_scores": model_parts,
                "verifier_check": check.to_dict(),
                "outcome": outcome,
                "score": score_ranked_candidate(model_parts, outcome, weights),
            }
        )
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def run_search(config_path: str | Path) -> dict[str, Any]:
    cfg = _config(config_path)
    out = Path(cfg["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    model, tokenizer, checkpoint = load_checkpoint(cfg["checkpoint"], device=torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    model_cfg = dict(checkpoint.get("config") or {})
    rows = [row for row in _load_rows(cfg["rows"]) if row.get("split") in {"challenge", "test", "val"}]
    if not rows:
        rows = _load_rows(cfg["rows"])
    traces: list[dict[str, Any]] = []
    accepted = 0
    closed = 0
    for state_index, row in enumerate(rows[: cfg["max_states"]]):
        state = str(row["state"])
        candidates = legal_action_candidates_from_state(state, max_candidates=cfg["beam_size"])
        ranked = rank_candidate_actions(
            model=model,
            tokenizer=tokenizer,
            state=state,
            candidates=candidates,
            max_state_len=int(model_cfg.get("max_state_len", 2048)),
            max_action_len=int(model_cfg.get("max_action_len", 128)),
            weights=cfg["ranking"],
            max_candidates=cfg["candidates_per_state"],
        )
        for rank, item in enumerate(ranked, start=1):
            candidate = item["action"]
            check = verify_action_for_state(candidate, state)
            if check.accepted:
                accepted += 1
            if check.closed_obligation:
                closed += 1
            trace = {
                "state_index": state_index,
                "example_id": row.get("example_id"),
                "gate": row.get("gate"),
                "rank": rank,
                "score": item["score"],
                "model_scores": item["model_scores"],
                "action": candidate,
                "action_text": item["action_text"],
                "verifier_check": check.to_dict(),
                "outcome": item["outcome"],
            }
            traces.append(trace)
            if check.accepted:
                break
    (out / "verifier_checked_actions.jsonl").write_text(
        "\n".join(json.dumps(trace, sort_keys=True) for trace in traces) + ("\n" if traces else ""),
        encoding="utf-8",
    )
    attempt = {
        "schema": "collatz_lab.proof_action_search",
        "version": 1,
        "run_id": cfg["run_id"],
        "checkpoint": cfg["checkpoint"],
        "states_searched": min(len(rows), cfg["max_states"]),
        "candidate_checks": len(traces),
        "accepted_action_count": accepted,
        "closed_obligation_count": closed,
        "accepted_action_rate_per_state": accepted / max(min(len(rows), cfg["max_states"]), 1),
        "closed_obligation_rate_per_state": closed / max(min(len(rows), cfg["max_states"]), 1),
        "trace_path": str(out / "verifier_checked_actions.jsonl"),
    }
    (out / "proof_action_attempt.json").write_text(json.dumps(attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return attempt


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run verifier-guided proof-action search.")
    parser.add_argument("--config", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(run_search(args.config))


if __name__ == "__main__":
    main()
