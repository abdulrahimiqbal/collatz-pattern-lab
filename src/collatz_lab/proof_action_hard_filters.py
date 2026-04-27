"""Hard-positive filters for mined proof-action traces.

RUN-013 is meant to separate genuinely useful frontier traces from easy local
closures.  The filters here are deliberately conservative and operate only on
verifier-checked trace metadata.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from typing import Any


HARD_GATES = {"S3", "S4", "S6"}
S6_ACTION_TYPES = {
    "PROVE_RESIDUE_COVERAGE",
    "PROVE_GLOBAL_DESCENT_INDUCTION",
    "CLOSE_WELL_FOUNDED_INDUCTION",
    "CERTIFY_NO_ESCAPE_BRANCH",
    "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM",
    "LIFT_LOCAL_TO_PARAMETRIC_FAMILY",
    "CLOSE_STRICT_THEOREM_BLOCKER",
    "PROPOSE_S6_LEMMA",
    "VERIFY_S6_LEMMA",
    "COMPOSE_GATE_PROOF",
}


@dataclass(frozen=True)
class HardFilterResult:
    accepted: bool
    reasons: tuple[str, ...]
    rejects: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"accepted": self.accepted, "reasons": list(self.reasons), "rejects": list(self.rejects)}


def state_hash(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def trace_signature(trace: dict[str, Any]) -> str:
    actions = [str(step.get("action", "")) for step in trace.get("actions") or []]
    payload = {
        "gate": trace.get("gate"),
        "start_state_hash": state_hash(str(trace.get("start_state", ""))),
        "actions": actions,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _action_type(step: dict[str, Any]) -> str:
    action = step.get("action")
    if isinstance(action, dict):
        return str(action.get("type", "UNKNOWN"))
    text = str(action)
    marker = '"type":"'
    if marker in text:
        return text.split(marker, 1)[1].split('"', 1)[0]
    return "UNKNOWN"


def _accepted_steps(trace: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for step in trace.get("actions") or [] if str(step.get("verifier_status", "")).startswith("ACCEPT")]


def is_hard_positive_trace(
    trace: dict[str, Any],
    *,
    min_depth: int = 8,
    require_no_one_step_close: bool = True,
    require_baseline_separation: bool = True,
    min_gate_progress_total: float = 0.1,
    reject_near_duplicates: bool = True,
) -> HardFilterResult:
    """Classify one verified trace as a hard positive or a reject."""

    reasons: list[str] = []
    rejects: list[str] = []
    gate = str(trace.get("gate", "UNKNOWN"))
    depth = int(trace.get("depth", len(trace.get("actions") or [])) or 0)
    accepted = _accepted_steps(trace)
    gate_progress = float(trace.get("gate_progress_total", 0.0) or 0.0)
    closed = bool(trace.get("closed_branch") or trace.get("closed_obligation"))
    no_one_step_close = not bool(trace.get("one_step_close_from_start", False))
    random_failed = not bool(trace.get("baseline_random_success_at_same_budget", False))
    heuristic_failed = not bool(trace.get("baseline_heuristic_success_at_same_budget", False))
    heuristic_calls = float(trace.get("baseline_heuristic_verifier_calls", 0.0) or 0.0)
    verifier_calls = float(trace.get("verifier_calls", 1.0) or 1.0)
    novelty = trace.get("novelty") if isinstance(trace.get("novelty"), dict) else {}

    if gate not in HARD_GATES:
        rejects.append("not_frontier_gate")
    if not accepted:
        rejects.append("no_accepted_steps")
    if depth <= 1 and closed:
        rejects.append("one_step_local_closure")
    if any(_action_type(step) == "ABANDON_BRANCH" for step in accepted) and depth <= 2:
        rejects.append("control_only_trace")
    if gate_progress <= 0 and not closed:
        rejects.append("no_downstream_closure_or_gate_progress")
    if reject_near_duplicates and bool(novelty.get("near_duplicate_trace")):
        rejects.append("near_duplicate_trace")
    if bool(novelty.get("exact_state_overlap")):
        rejects.append("exact_state_overlap")
    if require_no_one_step_close and not no_one_step_close:
        rejects.append("start_has_one_step_close")
    if require_baseline_separation and not random_failed:
        rejects.append("random_succeeds_at_same_budget")

    if depth >= min_depth and closed and no_one_step_close:
        reasons.append("long_horizon_closure")
    if gate in HARD_GATES and gate_progress > min_gate_progress_total and len(accepted) >= 3:
        reasons.append("frontier_progress")
    if random_failed and (heuristic_failed or (heuristic_calls >= 3.0 * verifier_calls > 0)):
        reasons.append("baseline_separation")
    if gate == "S6":
        action_types = {_action_type(step) for step in accepted}
        s6_delta = float(trace.get("s6_obligation_delta", 0.0) or 0.0)
        if action_types & S6_ACTION_TYPES or s6_delta < 0 or gate_progress > 0:
            reasons.append("s6_theorem_closure_progress")

    accepted_hard = bool(reasons) and not rejects
    return HardFilterResult(accepted=accepted_hard, reasons=tuple(reasons), rejects=tuple(rejects))


def hard_filter_summary(traces: list[dict[str, Any]]) -> dict[str, Any]:
    results = [is_hard_positive_trace(trace) for trace in traces]
    accepted = [trace for trace, result in zip(traces, results, strict=True) if result.accepted]
    depths = sorted(int(trace.get("depth", 0) or 0) for trace in accepted)
    gate_counts = Counter(str(trace.get("gate", "UNKNOWN")) for trace in accepted)
    reason_counts = Counter(reason for result in results for reason in result.reasons)
    reject_counts = Counter(reject for result in results for reject in result.rejects)
    median_depth = depths[len(depths) // 2] if depths else 0
    return {
        "schema": "collatz_lab.proof_action_hard_filter_summary",
        "version": 1,
        "trace_count": len(traces),
        "accepted_hard_positive_count": len(accepted),
        "rejected_trace_count": len(traces) - len(accepted),
        "median_trace_depth": median_depth,
        "gate_counts": dict(gate_counts),
        "reason_counts": dict(reason_counts),
        "reject_counts": dict(reject_counts),
    }
