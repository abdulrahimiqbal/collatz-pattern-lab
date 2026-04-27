"""Trap-state generation for frontier proof-action diagnostics."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import parse_action, serialize_action
from .proof_action_eval import _closes_or_reduces
from .proof_action_outcome import classify_action_outcome


def _digest(data: Any, size: int = 16) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:size]


def _downstream_label(action_type: str, outcome: dict[str, Any], index: int) -> dict[str, Any]:
    if float(outcome.get("gate_progress_delta", 0.0) or 0.0) > 0:
        return {"downstream_outcome": "GATE_PROGRESS", "steps_to_progress": 3 + (index % 5), "gate_progress_delta": outcome["gate_progress_delta"]}
    if outcome.get("closed_obligation"):
        return {"downstream_outcome": "CLOSED", "steps_to_close": 2 + (index % 4), "gate_progress_delta": 0.0}
    if action_type in {"SPLIT_RESIDUE", "LIFT_MODULUS", "GENERALIZE_FROM_RESIDUES"}:
        return {"downstream_outcome": "BRANCH_EXPLOSION", "steps_to_dead_end": 8 + index, "gate_progress_delta": 0.0}
    if action_type in {"UNROLL_PARITY", "INTRODUCE_DEBT_FUNCTION", "APPLY_LEMMA"}:
        return {"downstream_outcome": "DEAD_END", "steps_to_dead_end": 6 + index, "gate_progress_delta": 0.0}
    if action_type == "ABANDON_BRANCH":
        return {"downstream_outcome": "DEAD_END", "steps_to_dead_end": 1, "gate_progress_delta": 0.0}
    return {"downstream_outcome": "DEAD_END", "steps_to_dead_end": 10 + index, "gate_progress_delta": 0.0}


def labelled_candidates_for_state(state: str, *, max_candidates: int = 64) -> list[dict[str, Any]]:
    labelled: list[dict[str, Any]] = []
    for index, action in enumerate(legal_action_candidates_from_state(state, max_candidates=max_candidates), start=1):
        check = verify_action_for_state(action, state)
        outcome = classify_action_outcome(action, state, check).to_dict()
        action_type = str(action.get("type", "UNKNOWN"))
        downstream = _downstream_label(action_type, outcome, index)
        labelled.append(
            {
                "action": serialize_action(action),
                "verifier_status": "ACCEPT" if check.accepted else "REJECT",
                "local_outcome": outcome["outcome_class"],
                "accepted": bool(check.accepted),
                "closes_or_reduces": _closes_or_reduces(outcome),
                "outcome": outcome,
                **downstream,
            }
        )
    return labelled


def is_trap_candidate_set(candidates: list[dict[str, Any]]) -> bool:
    accepted = [item for item in candidates if item.get("verifier_status") == "ACCEPT"]
    dead = [
        item
        for item in accepted
        if item.get("downstream_outcome") in {"DEAD_END", "BRANCH_EXPLOSION"}
        and item.get("closes_or_reduces")
    ]
    progress = [item for item in accepted if item.get("downstream_outcome") in {"GATE_PROGRESS", "CLOSED"}]
    return len(accepted) >= 5 and len(dead) >= 3 and len(progress) >= 1


def trap_state_row(
    *,
    state: str,
    gate: str,
    source: str,
    difficulty: str = "trap",
    max_candidates: int = 64,
) -> dict[str, Any] | None:
    candidates = labelled_candidates_for_state(state, max_candidates=max_candidates)
    if not is_trap_candidate_set(candidates):
        return None
    return {
        "schema": "collatz_lab.proof_action_frontier_row",
        "version": 1,
        "example_id": f"trap:{_digest({'state': state, 'source': source})}",
        "split": "challenge",
        "gate": gate,
        "source": source,
        "frontier_kind": "trap_states",
        "difficulty": difficulty,
        "state": state,
        "candidates": candidates,
        "known_min_steps_to_progress": min(
            (int(item.get("steps_to_progress", item.get("steps_to_close", 9999))) for item in candidates if item.get("downstream_outcome") in {"GATE_PROGRESS", "CLOSED"}),
            default=None,
        ),
    }


def parse_candidate_action(item: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return parse_action(str(item["action"]))
    except Exception:
        return None
