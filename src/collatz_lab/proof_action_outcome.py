"""Outcome taxonomy for verifier-checked proof actions.

The proof-action policy is useful only when verifier-accepted actions move a
branch toward closure.  This module gives dataset building, eval, and search a
single vocabulary for distinguishing "valid but idle" from "actually closes or
strictly reduces an obligation".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .proof_action_dsl import ProofActionError, parse_action, serialize_action, validate_action
from .proof_action_state import parse_state_facts


INVALID_SYNTAX = "INVALID_SYNTAX"
PARSE_VALID_BUT_REJECTED = "PARSE_VALID_BUT_REJECTED"
VERIFIER_ACCEPTED_NO_PROGRESS = "VERIFIER_ACCEPTED_NO_PROGRESS"
VERIFIER_ACCEPTED_REDUCED = "VERIFIER_ACCEPTED_REDUCED"
VERIFIER_ACCEPTED_CLOSED_LOCAL = "VERIFIER_ACCEPTED_CLOSED_LOCAL"
VERIFIER_ACCEPTED_CLOSED_BRANCH = "VERIFIER_ACCEPTED_CLOSED_BRANCH"
VERIFIER_ACCEPTED_NEW_LEMMA = "VERIFIER_ACCEPTED_NEW_LEMMA"
VERIFIER_ACCEPTED_GATE_PROGRESS = "VERIFIER_ACCEPTED_GATE_PROGRESS"

OUTCOME_CLASSES = (
    INVALID_SYNTAX,
    PARSE_VALID_BUT_REJECTED,
    VERIFIER_ACCEPTED_NO_PROGRESS,
    VERIFIER_ACCEPTED_REDUCED,
    VERIFIER_ACCEPTED_CLOSED_LOCAL,
    VERIFIER_ACCEPTED_CLOSED_BRANCH,
    VERIFIER_ACCEPTED_NEW_LEMMA,
    VERIFIER_ACCEPTED_GATE_PROGRESS,
)

_REWARDS = {
    INVALID_SYNTAX: -1.0,
    PARSE_VALID_BUT_REJECTED: -0.5,
    VERIFIER_ACCEPTED_NO_PROGRESS: 0.05,
    VERIFIER_ACCEPTED_REDUCED: 0.25,
    VERIFIER_ACCEPTED_CLOSED_LOCAL: 0.75,
    VERIFIER_ACCEPTED_CLOSED_BRANCH: 1.0,
    VERIFIER_ACCEPTED_NEW_LEMMA: 0.45,
    VERIFIER_ACCEPTED_GATE_PROGRESS: 1.25,
}


@dataclass(frozen=True)
class ActionOutcome:
    accepted: bool
    closed_obligation: bool
    closed_branch: bool
    num_goals_before: int
    num_goals_after: int
    goals_closed: int
    goals_created: int
    net_goal_delta: int
    gate_progress_delta: float
    strict_progress: bool
    outcome_class: str
    closure_reward: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "closed_obligation": self.closed_obligation,
            "closed_branch": self.closed_branch,
            "num_goals_before": self.num_goals_before,
            "num_goals_after": self.num_goals_after,
            "goals_closed": self.goals_closed,
            "goals_created": self.goals_created,
            "net_goal_delta": self.net_goal_delta,
            "gate_progress_delta": self.gate_progress_delta,
            "strict_progress": self.strict_progress,
            "outcome_class": self.outcome_class,
            "closure_reward": self.closure_reward,
        }


def _goal_count(state: str) -> int:
    facts = parse_state_facts(state)
    obligations = [item for item in facts.get("open_obligations", []) if item]
    return max(1, len(dict.fromkeys(obligations)))


def _parse_action(action: dict[str, Any] | str) -> dict[str, Any] | None:
    try:
        return parse_action(action) if isinstance(action, str) else validate_action(action)
    except ProofActionError:
        return None


def _reward(outcome_class: str, *, goals_created: int = 0, downstream_closed: bool = True) -> float:
    reward = float(_REWARDS[outcome_class])
    if goals_created > 0 and not downstream_closed:
        reward = min(reward, 0.1)
    return reward


def classify_action_outcome(
    action: dict[str, Any] | str,
    state: str,
    verifier_check: Any | None = None,
    *,
    closed_branch: bool | None = None,
    eventually_closed: bool | None = None,
    distance_to_close: int | None = None,
) -> ActionOutcome:
    """Classify one action in one canonical state after verifier checking."""

    parsed = _parse_action(action)
    goals_before = _goal_count(state)
    if parsed is None:
        return ActionOutcome(
            accepted=False,
            closed_obligation=False,
            closed_branch=False,
            num_goals_before=goals_before,
            num_goals_after=goals_before,
            goals_closed=0,
            goals_created=0,
            net_goal_delta=0,
            gate_progress_delta=0.0,
            strict_progress=False,
            outcome_class=INVALID_SYNTAX,
            closure_reward=_reward(INVALID_SYNTAX),
        )

    accepted = bool(getattr(verifier_check, "accepted", False))
    closed_obligation = bool(getattr(verifier_check, "closed_obligation", False))
    progress = float(getattr(verifier_check, "progress", 0.0) or 0.0)
    facts = parse_state_facts(state)
    gate = str(facts.get("gate", ""))
    action_type = str(parsed.get("type"))

    if not accepted:
        return ActionOutcome(
            accepted=False,
            closed_obligation=False,
            closed_branch=False,
            num_goals_before=goals_before,
            num_goals_after=goals_before,
            goals_closed=0,
            goals_created=0,
            net_goal_delta=0,
            gate_progress_delta=0.0,
            strict_progress=False,
            outcome_class=PARSE_VALID_BUT_REJECTED,
            closure_reward=_reward(PARSE_VALID_BUT_REJECTED),
        )

    gate_progress_delta = 0.0
    outcome_class = VERIFIER_ACCEPTED_NO_PROGRESS
    goals_created = 0
    goals_closed = 0
    strict_progress = False
    is_closed_branch = bool(closed_branch) if closed_branch is not None else False

    if action_type in {"SPLIT_RESIDUE", "LIFT_MODULUS", "GENERALIZE_FROM_RESIDUES"}:
        goals_created = 1
    if action_type in {"UNROLL_PARITY", "INTRODUCE_DEBT_FUNCTION", "SPLIT_RESIDUE", "LIFT_MODULUS", "GENERALIZE_FROM_RESIDUES"} and progress > 0:
        outcome_class = VERIFIER_ACCEPTED_REDUCED
        strict_progress = action_type in {"UNROLL_PARITY", "INTRODUCE_DEBT_FUNCTION"}
    if action_type == "APPLY_LEMMA" and progress > 0:
        outcome_class = VERIFIER_ACCEPTED_NEW_LEMMA
        strict_progress = True
    s6_progress_actions = {
        "PROVE_RESIDUE_COVERAGE",
        "PROVE_GLOBAL_DESCENT_INDUCTION",
        "CLOSE_WELL_FOUNDED_INDUCTION",
        "CERTIFY_NO_ESCAPE_BRANCH",
        "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM",
        "LIFT_LOCAL_TO_PARAMETRIC_FAMILY",
        "CLOSE_STRICT_THEOREM_BLOCKER",
        "VERIFY_S6_LEMMA",
        "COMPOSE_GATE_PROOF",
    }
    if action_type == "DERIVE_PARENT_TRANSITION" and progress > 0:
        outcome_class = VERIFIER_ACCEPTED_GATE_PROGRESS
        gate_progress_delta = 0.6 if gate.startswith(("S4", "S6")) else 0.25
        strict_progress = True
    if action_type in s6_progress_actions and gate.startswith("S6") and progress > 0:
        outcome_class = VERIFIER_ACCEPTED_GATE_PROGRESS
        gate_progress_delta = max(gate_progress_delta, min(1.0, progress))
        strict_progress = True
    if closed_obligation:
        goals_closed = min(1, goals_before)
        strict_progress = True
        if gate.startswith(("S3", "S4", "S6")):
            outcome_class = VERIFIER_ACCEPTED_GATE_PROGRESS
            gate_progress_delta = max(gate_progress_delta, 1.0)
        else:
            outcome_class = VERIFIER_ACCEPTED_CLOSED_LOCAL
    if is_closed_branch:
        goals_closed = goals_before
        outcome_class = VERIFIER_ACCEPTED_CLOSED_BRANCH
        strict_progress = True
    if action_type == "ABANDON_BRANCH":
        outcome_class = VERIFIER_ACCEPTED_NO_PROGRESS
        strict_progress = False

    num_goals_after = max(0, goals_before - goals_closed + goals_created)
    reward = _reward(outcome_class, goals_created=goals_created, downstream_closed=bool(eventually_closed))
    if distance_to_close is not None and distance_to_close > 1 and reward > 0:
        reward = max(0.05, reward - min(0.2, 0.02 * distance_to_close))

    return ActionOutcome(
        accepted=True,
        closed_obligation=closed_obligation,
        closed_branch=is_closed_branch,
        num_goals_before=goals_before,
        num_goals_after=num_goals_after,
        goals_closed=goals_closed,
        goals_created=goals_created,
        net_goal_delta=num_goals_after - goals_before,
        gate_progress_delta=gate_progress_delta,
        strict_progress=strict_progress,
        outcome_class=outcome_class,
        closure_reward=reward,
    )


def outcome_rank(data: dict[str, Any]) -> tuple[float, int, int, float]:
    """Sort key where larger means more proof-useful."""

    reward = float(data.get("closure_reward", data.get("reward", 0.0)) or 0.0)
    closed = 1 if data.get("closed_branch") or data.get("closed_obligation") else 0
    strict = 1 if data.get("strict_progress") else 0
    gate_delta = float(data.get("gate_progress_delta", 0.0) or 0.0)
    return (reward, closed, strict, gate_delta)


def outcome_fields_for_row(action: dict[str, Any], state: str, verifier_check: Any) -> dict[str, Any]:
    """Return JSON fields that dataset/eval rows attach to verifier checks."""

    outcome = classify_action_outcome(action, state, verifier_check)
    return outcome.to_dict()


def canonical_action_text(action: dict[str, Any] | str) -> str:
    """Return canonical text if possible, otherwise the stripped raw action text."""

    if isinstance(action, str):
        try:
            return serialize_action(parse_action(action))
        except ProofActionError:
            return action.strip()
    return serialize_action(action)
