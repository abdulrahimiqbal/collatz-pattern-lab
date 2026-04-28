"""Shared helpers for listwise proof-action candidate selection."""

from __future__ import annotations

import json
from typing import Any


SELECTOR_OUTCOME_CLASSES = (
    "REJECTED",
    "ACCEPTED_NO_PROGRESS",
    "ACCEPTED_REDUCED",
    "ACCEPTED_DEAD_END",
    "BRANCH_EXPLOSION",
    "CLOSED_LOCAL",
    "GATE_PROGRESS",
    "S6_BLOCKER_REDUCED",
    "S6_LEMMA_ACCEPTED_AND_USED",
)

SELECTOR_OUTCOME_TO_ID = {name: index for index, name in enumerate(SELECTOR_OUTCOME_CLASSES)}

SELECTOR_UTILITY = {
    "REJECTED": -1.0,
    "ACCEPTED_NO_PROGRESS": 0.0,
    "ACCEPTED_REDUCED": 0.15,
    "ACCEPTED_DEAD_END": -0.5,
    "BRANCH_EXPLOSION": -0.75,
    "CLOSED_LOCAL": 0.75,
    "GATE_PROGRESS": 1.25,
    "S6_BLOCKER_REDUCED": 1.5,
    "S6_LEMMA_ACCEPTED_AND_USED": 1.75,
}

LOW_UTILITY_OUTCOMES = {"ACCEPTED_NO_PROGRESS", "ACCEPTED_REDUCED", "ACCEPTED_DEAD_END", "BRANCH_EXPLOSION"}
GATE_PROGRESS_OUTCOMES = {"GATE_PROGRESS", "S6_BLOCKER_REDUCED", "S6_LEMMA_ACCEPTED_AND_USED"}
TARGET_OBJECTIVES = (
    "LOCAL_CLOSE",
    "LOCAL_REDUCE",
    "GATE_PROGRESS",
    "S6_BLOCKER_REDUCE",
    "TRAP_AVOIDANCE",
    "S6_LEMMA_USE",
)


def infer_target_objective(row: dict[str, Any]) -> str:
    gate = str(row.get("gate", ""))
    frontier_kind = str(row.get("frontier_kind", ""))
    difficulty = str(row.get("difficulty", ""))

    if frontier_kind == "trap_states" or difficulty == "trap":
        return "TRAP_AVOIDANCE"
    if gate == "S6" or frontier_kind.startswith("s6_"):
        return "S6_BLOCKER_REDUCE"
    if gate in {"S3", "S4"} or frontier_kind.startswith(("s3_", "s4_")):
        return "GATE_PROGRESS"
    if "close" in frontier_kind or "one_step" in frontier_kind:
        return "LOCAL_CLOSE"
    return "LOCAL_REDUCE"


def objective_threshold(target_objective: str) -> float:
    if target_objective == "S6_BLOCKER_REDUCE":
        return 1.0
    if target_objective == "GATE_PROGRESS":
        return 1.0
    if target_objective == "TRAP_AVOIDANCE":
        return 1.0
    if target_objective == "LOCAL_CLOSE":
        return 0.75
    if target_objective == "S6_LEMMA_USE":
        return 1.0
    return 0.25


def format_candidate_pair_input(state: str, action_text: str) -> str:
    return f"<STATE>\n{state}\n</STATE>\n<CANDIDATE_ACTION>\n{action_text}\n</CANDIDATE_ACTION>"


def _action_type_from_text(action_text: str) -> str:
    try:
        parsed = json.loads(action_text)
    except Exception:
        return ""
    return str(parsed.get("type", "")) if isinstance(parsed, dict) else ""


def selector_outcome_from_candidate(candidate: dict[str, Any], *, gate: str | None = None) -> str:
    """Map verifier/downstream labels into selector outcome classes."""

    action_text = str(candidate.get("action_text") or candidate.get("action") or "")
    action_type = str(candidate.get("action_type") or _action_type_from_text(action_text))
    downstream = str(candidate.get("downstream_outcome", ""))
    outcome = candidate.get("outcome") if isinstance(candidate.get("outcome"), dict) else {}
    local = str(candidate.get("local_outcome") or outcome.get("outcome_class") or candidate.get("outcome_class") or "")
    accepted = bool(candidate.get("accepted") or candidate.get("verifier_status") == "ACCEPT" or outcome.get("accepted"))
    gate_name = str(gate or candidate.get("gate") or "")
    gate_delta = float(candidate.get("gate_progress_delta", outcome.get("gate_progress_delta", 0.0)) or 0.0)

    if not accepted:
        return "REJECTED"
    if downstream == "BRANCH_EXPLOSION":
        return "BRANCH_EXPLOSION"
    if downstream == "DEAD_END":
        return "ACCEPTED_DEAD_END"
    if downstream == "GATE_PROGRESS" or gate_delta > 0 or local == "VERIFIER_ACCEPTED_GATE_PROGRESS":
        if gate_name.startswith("S6") or action_type in {
            "CLOSE_STRICT_THEOREM_BLOCKER",
            "PROVE_RESIDUE_COVERAGE",
            "CLOSE_WELL_FOUNDED_INDUCTION",
            "CERTIFY_NO_ESCAPE_BRANCH",
            "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM",
            "COMPOSE_GATE_PROOF",
        }:
            if action_type in {"VERIFY_S6_LEMMA", "COMPOSE_GATE_PROOF"}:
                return "S6_LEMMA_ACCEPTED_AND_USED"
            return "S6_BLOCKER_REDUCED"
        return "GATE_PROGRESS"
    if bool(candidate.get("closed_obligation") or outcome.get("closed_obligation")):
        return "CLOSED_LOCAL"
    if local == "VERIFIER_ACCEPTED_CLOSED_LOCAL":
        return "CLOSED_LOCAL"
    if local in {"VERIFIER_ACCEPTED_REDUCED", "VERIFIER_ACCEPTED_NEW_LEMMA"}:
        return "ACCEPTED_REDUCED"
    return "ACCEPTED_NO_PROGRESS"


def utility_for_selector_outcome(outcome_class: str) -> float:
    return float(SELECTOR_UTILITY.get(outcome_class, 0.0))


def _candidate_action_text(candidate: dict[str, Any]) -> str:
    action = candidate.get("action")
    if isinstance(action, dict):
        try:
            return json.dumps(action, sort_keys=True)
        except Exception:
            return str(action)
    return str(candidate.get("action_text") or action or "")


def candidate_utility(candidate: dict[str, Any], target_objective: str) -> float:
    outcome_data = candidate.get("outcome") if isinstance(candidate.get("outcome"), dict) else {}
    outcome = str(
        candidate.get("outcome_class")
        or candidate.get("local_outcome")
        or candidate.get("selector_outcome_class")
        or outcome_data.get("outcome_class")
        or ""
    )
    downstream = str(candidate.get("downstream_outcome") or "")
    accepted = bool(candidate.get("accepted") or candidate.get("verifier_status") == "ACCEPT" or outcome_data.get("accepted"))
    if outcome in SELECTOR_OUTCOME_CLASSES and outcome != "REJECTED":
        accepted = True
    gate_delta = float(
        candidate.get(
            "gate_progress_delta",
            candidate.get("effective_gate_progress_delta", outcome_data.get("gate_progress_delta", 0.0)),
        )
        or 0.0
    )
    action_text = _candidate_action_text(candidate)

    if not accepted:
        return -1.0

    if downstream in {"DEAD_END", "BRANCH_EXPLOSION"} or outcome in {"ACCEPTED_DEAD_END", "BRANCH_EXPLOSION"}:
        return -0.75

    if target_objective == "GATE_PROGRESS":
        if downstream == "GATE_PROGRESS" or gate_delta > 0 or outcome in GATE_PROGRESS_OUTCOMES:
            return 1.25
        if "CLOSED" in outcome:
            return 0.75
        if "REDUCED" in outcome:
            return 0.10
        return 0.0

    if target_objective == "S6_BLOCKER_REDUCE":
        if downstream == "GATE_PROGRESS" or gate_delta > 0 or outcome in {"S6_BLOCKER_REDUCED", "S6_LEMMA_ACCEPTED_AND_USED"}:
            return 1.50
        if "CLOSE_STRICT" in action_text:
            return 1.25
        if "VERIFY_S6_LEMMA" in action_text:
            return 1.00
        if "REDUCED" in outcome:
            return 0.10
        return 0.0

    if target_objective == "S6_LEMMA_USE":
        if outcome == "S6_LEMMA_ACCEPTED_AND_USED" or "VERIFY_S6_LEMMA" in action_text:
            return 1.75
        if outcome == "S6_BLOCKER_REDUCED" or downstream == "GATE_PROGRESS" or gate_delta > 0:
            return 1.25
        if "REDUCED" in outcome:
            return 0.10
        return 0.0

    if target_objective == "TRAP_AVOIDANCE":
        if downstream in {"GATE_PROGRESS", "CLOSED"} or outcome in {"GATE_PROGRESS", "CLOSED_LOCAL"}:
            return 1.25
        if downstream in {"DEAD_END", "BRANCH_EXPLOSION"} or outcome in {"ACCEPTED_DEAD_END", "BRANCH_EXPLOSION"}:
            return -1.0
        return 0.1

    if target_objective == "LOCAL_CLOSE":
        if "CLOSED" in outcome or downstream == "CLOSED":
            return 1.0
        if "REDUCED" in outcome:
            return 0.25
        return 0.0

    if "CLOSED" in outcome:
        return 1.0
    if "REDUCED" in outcome:
        return 0.5
    return 0.05


def selector_candidate_record(
    candidate: dict[str, Any],
    *,
    gate: str | None = None,
    target_objective: str | None = None,
) -> dict[str, Any]:
    outcome_class = selector_outcome_from_candidate(candidate, gate=gate)
    objective = target_objective or infer_target_objective(candidate)
    utility_candidate = {**candidate, "selector_outcome_class": outcome_class}
    return {
        "action_text": _candidate_action_text(candidate),
        "outcome_class": outcome_class,
        "utility": candidate_utility(utility_candidate, objective),
    }
