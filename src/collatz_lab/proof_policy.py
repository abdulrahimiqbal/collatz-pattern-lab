"""Proof-action policy over open proof obligations.

This is the model insertion point.  The current implementation is a deterministic
heuristic baseline that emits structured actions; later a neural policy can rank
the same action objects from the same obligation features.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .proof_actions import ProofAction


OPEN_STATUSES = {"NEEDS_SPLIT", "UNKNOWN"}

_UNRESOLVED_RE = re.compile(r"unresolved_bucket:t=(?P<t>\d+):a=(?P<a>\d+):h=(?P<h>\d+)")
_CUBE_RE = re.compile(r"cube_lift:(?P<set_name>[^:]+):(?P<lift_status>[^:]+)")
_PARENT_TRANSITION_RE = re.compile(
    r"P(?P<a>\d+):h=(?P<h>\d+):to=P(?P<a_next>\d+):rdepth=(?P<r_depth>\d+)(?:#\d+)?"
)


def open_obligations(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return obligations that are not closed by the current proof report."""

    return [
        row
        for row in report.get("obligations", [])
        if str(row.get("scc_status", row.get("status", "UNKNOWN"))) in OPEN_STATUSES
    ]


def featurize_obligation(obligation: dict[str, Any]) -> dict[str, Any]:
    """Convert one obligation into symbolic features for a proof policy."""

    oid = str(obligation.get("obligation_id", ""))
    coverage = obligation.get("coverage") if isinstance(obligation.get("coverage"), dict) else {}
    features: dict[str, Any] = {
        "obligation_id": oid,
        "scope": obligation.get("scope"),
        "scc_status": obligation.get("scc_status", obligation.get("status")),
        "transition_rule": obligation.get("transition_rule"),
        "ancestor_descent": bool(obligation.get("ancestor_descent")),
        "kind": "other",
    }

    cube_match = _CUBE_RE.fullmatch(oid)
    unresolved_match = _UNRESOLVED_RE.fullmatch(oid)
    parent_transition_match = _PARENT_TRANSITION_RE.fullmatch(oid)
    if oid == "P6_q20_finite_frontier_coverage":
        features.update(
            {
                "kind": "finite_frontier",
                "total_q_classes": coverage.get("total_q_classes"),
                "residual_unknown_q_classes": coverage.get("residual_unknown_q_classes"),
                "unknown_within_parent_percent": coverage.get("unknown_within_parent_percent"),
            }
        )
    elif oid == "universal_parent_state_coverage":
        features.update({"kind": "universal_parent_coverage"})
    elif oid == "parent_state_transition_templates":
        features.update(
            {
                "kind": "parent_state_templates",
                "a_min": coverage.get("a_min"),
                "a_max": coverage.get("a_max"),
                "r_depth": coverage.get("r_depth"),
                "row_count": coverage.get("row_count"),
                "state_count": coverage.get("state_count"),
            }
        )
    elif oid == "parametric_a_templates":
        features.update(
            {
                "kind": "parametric_a_templates",
                "depth": coverage.get("depth"),
                "period": coverage.get("period"),
                "group_count": coverage.get("group_count"),
                "sample_period_check_passed": coverage.get("sample_period_check_passed"),
            }
        )
    elif cube_match is not None:
        features.update(
            {
                "kind": "cube_lift",
                "set_name": cube_match.group("set_name"),
                "lift_status": cube_match.group("lift_status"),
                "cube_count": coverage.get("cube_count"),
            }
        )
    elif parent_transition_match is not None:
        features.update(
            {
                "kind": "parent_transition_bucket",
                "a": int(parent_transition_match.group("a")),
                "h": int(parent_transition_match.group("h")),
                "a_next": int(parent_transition_match.group("a_next")),
                "r_depth": int(parent_transition_match.group("r_depth")),
                "residue_count": coverage.get("residue_count"),
            }
        )
    elif unresolved_match is not None:
        t = int(unresolved_match.group("t"))
        a = int(unresolved_match.group("a"))
        h = int(unresolved_match.group("h"))
        features.update(
            {
                "kind": "unresolved_bucket",
                "t": t,
                "a": a,
                "h": h,
                "count_unknown": coverage.get("count_unknown"),
                "unknown_percent": coverage.get("unknown_percent"),
                "is_low_h": h <= 2,
                "is_p6": a == 6,
                "is_sharp_return_candidate": a == 6 and h == 1,
            }
        )
    return features


def _add_action(
    actions: list[ProofAction],
    action: str,
    score: float,
    rationale: str,
    **params: Any,
) -> None:
    candidate = ProofAction(action=action, params=params, score=score, rationale=rationale)
    key = (candidate.action, json.dumps(candidate.params, sort_keys=True))
    existing = {
        (row.action, json.dumps(row.params, sort_keys=True)): index
        for index, row in enumerate(actions)
    }
    if key in existing:
        index = existing[key]
        if candidate.score > actions[index].score:
            actions[index] = candidate
        return
    actions.append(candidate)


def propose_actions(
    obligation: dict[str, Any],
    model: Any | None = None,
    beam_size: int = 32,
) -> list[ProofAction]:
    """Return ranked proof actions for one obligation.

    ``model`` is accepted as a future hook.  A model should return action-like
    rows that can be converted to ``ProofAction``; until then the heuristic
    policy is deliberately explicit and deterministic.
    """

    if beam_size <= 0:
        return []
    features = featurize_obligation(obligation)
    if features["scc_status"] not in OPEN_STATUSES:
        return []

    actions: list[ProofAction] = []
    kind = features["kind"]

    if kind == "finite_frontier":
        _add_action(
            actions,
            "SPLIT_BY_H",
            0.96,
            "finite q-depth coverage is diagnostic; split the residual mass by exact burst h",
            target="residual_frontier",
        )
        _add_action(
            actions,
            "LIFT_CUBE",
            0.88,
            "attempt to turn compressed finite frontier cubes into infinite claims",
            sets=["residual_certified", "unknown"],
        )
        _add_action(
            actions,
            "TRY_SCC_RANKING",
            0.72,
            "frontier still has recursive components; try SCC termination ranking",
        )
        _add_action(
            actions,
            "TRY_VALUATION_CLOSURE",
            0.68,
            "frontier still has recursive components; derive transferable 2-adic forms",
        )
        _add_action(
            actions,
            "RUN_FALSIFIER",
            0.45,
            "stress-test broad finite-depth claims before treating them as theorem candidates",
        )

    elif kind == "cube_lift":
        set_name = str(features.get("set_name"))
        _add_action(
            actions,
            "SPLIT_BY_RESIDUE",
            0.92,
            "cube did not lift as-is; refine by one or more low residue bits",
            set_name=set_name,
            current_cube_count=features.get("cube_count"),
            extra_depth=1,
        )
        _add_action(
            actions,
            "SPLIT_BY_H",
            0.84,
            "separate cube by forced-burst division exponent h",
            set_name=set_name,
        )
        _add_action(
            actions,
            "TRY_ANCESTOR_COMPOSITION",
            0.70,
            "check whether local certificates after a return pay ancestor expansion debt",
            set_name=set_name,
        )
        _add_action(
            actions,
            "RUN_FALSIFIER",
            0.38,
            "sample boundary and high-valuation representatives in the cube",
            set_name=set_name,
        )

    elif kind == "unresolved_bucket":
        a = int(features["a"])
        h = int(features["h"])
        _add_action(
            actions,
            "SPLIT_BY_PARENT_LEVEL",
            0.86 if h <= 2 else 0.62,
            "promote leave-parent branches into exact P_a -> P_b transitions",
            a=a,
            h=h,
        )
        _add_action(
            actions,
            "SPLIT_BY_RESIDUE",
            0.78,
            "refine the unresolved stratum by low q bits",
            a=a,
            h=h,
            extra_depth=1,
        )
        _add_action(
            actions,
            "SPLIT_BY_H",
            0.66,
            "separate the bucket into finer h or h-threshold cases",
            a=a,
            h=h,
        )
        if h == 1:
            _add_action(
                actions,
                "PROMOTE_TO_PARENT_STATE",
                0.93,
                "h=1 often leaves P6 for another parent level instead of being generic unknown",
                a=a,
                h=h,
            )
            _add_action(
                actions,
                "TRY_VALUATION_CLOSURE",
                0.74,
                "low-h recursive branches need transferable 2-adic height forms",
                a=a,
                h=h,
            )
            _add_action(
                actions,
                "TRY_SCC_RANKING",
                0.70,
                "low-h branches may be recursive SCCs that need ranking",
                a=a,
                h=h,
            )
        if a == 6 and h == 1:
            _add_action(
                actions,
                "TRY_ADIC_BASIN",
                0.91,
                "the q23 sharp return subbranch has the exact height v2(601q+1)",
                map_name="sharp_q23_R23",
                form={"u": 601, "v": 1},
                closes_subbranch_only=True,
            )
        if h <= 3:
            _add_action(
                actions,
                "PROPOSE_VALUATION_FORM",
                0.55,
                "derive a candidate linear 2-adic form from nearby affine return maps",
                a=a,
                h=h,
                template="cycle_fixed_point",
            )
        if h <= 3:
            _add_action(
                actions,
                "PROPOSE_MIXED_MODULUS_STATE",
                0.81,
                "high-parent valuation branches lose information unless odd-modulus state is carried",
                a=a,
                h=h,
                state=["parent_level", "odd_coordinate_mod_3a", "growth_debt"],
            )
            _add_action(
                actions,
                "TRY_MIXED_MODULUS_DEBT_VERIFIER",
                0.79,
                "test the mixed-modulus debt state against the exact high-parent bypass report",
                a=a,
                h=h,
            )

    elif kind == "universal_parent_coverage":
        _add_action(
            actions,
            "GENERALIZE_IN_A",
            0.88,
            "universal coverage now depends on all parent-state transition templates",
            depth=8,
            a_min=1,
            a_max=64,
        )
        _add_action(
            actions,
            "TRY_SCC_POTENTIAL",
            0.72,
            "search a ranking over parent-state transitions instead of mining more local leaves",
        )
        _add_action(
            actions,
            "RUN_FALSIFIER",
            0.40,
            "stress-test universal parent-state assumptions before promoting them",
        )

    elif kind == "parent_state_templates":
        a_min = int(features.get("a_min") or 1)
        a_max = int(features.get("a_max") or 64)
        r_depth = int(features.get("r_depth") or 8)
        _add_action(
            actions,
            "GENERALIZE_IN_A",
            0.94,
            "derive periodic-in-a transition templates before any larger sequence model",
            depth=max(8, r_depth),
            a_min=a_min,
            a_max=max(a_max, 64),
        )
        _add_action(
            actions,
            "TRY_SCC_POTENTIAL",
            0.82,
            "try a global ranking certificate over parent-state transitions",
            a_min=a_min,
            a_max=a_max,
            r_depth=r_depth,
        )
        _add_action(
            actions,
            "PROPOSE_POTENTIAL",
            0.64,
            "create a verifier slot for a new parent-state potential family",
            template="parent_state_log_potential",
        )
        _add_action(
            actions,
            "PROPOSE_MIXED_MODULUS_STATE",
            0.86,
            "global parent templates now need odd-modulus state for high-parent valuation branches",
            state=["parent_level", "odd_coordinate_mod_3a", "growth_debt"],
        )
        _add_action(
            actions,
            "TRY_MIXED_MODULUS_DEBT_VERIFIER",
            0.83,
            "run the exact mixed-modulus high-parent verifier slot before promoting debt induction",
        )
        _add_action(
            actions,
            "RUN_FALSIFIER",
            0.38,
            "look for finite-depth counterpressure before template promotion",
        )

    elif kind == "parametric_a_templates":
        depth = int(features.get("depth") or 8)
        _add_action(
            actions,
            "GENERALIZE_IN_A",
            0.90,
            "extend the exact 3^a periodicity scaffold and train on its failures",
            depth=max(depth, 10),
            a_min=1,
            a_max=128,
        )
        _add_action(
            actions,
            "PROPOSE_POTENTIAL",
            0.70,
            "turn periodic template classes into a concrete potential search",
            template="periodic_a_parent_potential",
        )
        _add_action(
            actions,
            "PROPOSE_PROOF_DSL",
            0.74,
            "emit a typed lemma/program object so verifier feedback can train proof generation",
            target="parametric_lifting",
        )
        _add_action(
            actions,
            "TRY_SCC_POTENTIAL",
            0.60,
            "test whether the current periodic classes admit a ranking",
        )

    elif kind == "parent_transition_bucket":
        a = int(features["a"])
        h = int(features["h"])
        a_next = int(features["a_next"])
        r_depth = int(features["r_depth"])
        _add_action(
            actions,
            "TRY_PARENT_TRANSITION_TEMPLATE",
            0.93,
            "verify the exact finite parent-transition bucket before proposing a theorem template",
            a=a,
            h=h,
            a_next=a_next,
            r_depth=r_depth,
        )
        _add_action(
            actions,
            "GENERALIZE_IN_A",
            0.72,
            "look for periodic-in-a structure shared by this transition bucket",
            depth=max(8, r_depth),
            a_min=max(1, a - 4),
            a_max=a + 64,
        )
        _add_action(
            actions,
            "PROPOSE_POTENTIAL",
            0.62,
            "turn this transition bucket into a concrete ranking/potential search target",
            template="parent_transition_bucket",
            a=a,
            h=h,
            a_next=a_next,
        )
        _add_action(
            actions,
            "PROPOSE_DEBT_RANK",
            0.58,
            "propose a debt rank and immediately check it for positive mixed-branch cycles",
            a=a,
            h=h,
            a_next=a_next,
        )
        _add_action(
            actions,
            "RUN_FALSIFIER",
            0.22,
            "sample representatives only after exact bucket verification",
            a=a,
            h=h,
            a_next=a_next,
        )

    else:
        _add_action(
            actions,
            "RUN_FALSIFIER",
            0.30,
            "unknown obligation type; search for counterpressure before adding theorem claims",
        )

    if model is not None:
        model_rows = model(features)  # pragma: no cover - hook for future learned policies.
        for row in model_rows:
            if isinstance(row, ProofAction):
                actions.append(row)
            else:
                actions.append(ProofAction(**row))

    actions.sort(key=lambda row: row.score, reverse=True)
    return actions[:beam_size]
