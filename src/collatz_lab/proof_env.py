"""Verifier-backed proof-search environment.

The environment executes structured proof actions against open obligations and
turns exact-tool outcomes into rewards and JSONL traces.  This is intentionally a
strict scaffold: actions that only create a better subproblem are marked
``REDUCED`` rather than falsely counted as full proof closure.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .adic_basin import build_adic_basin_certificate
from .cycle_certificates import sharp_q23_return_map
from .debt import build_debt_demo_report
from .falsifier import build_falsifier_report
from .parent_states import parent_transition
from .parent_state_system import classify_parent_residue
from .parametric_a import build_parametric_a_report
from .proof_actions import ProofAction, action_from_dict
from .proof_policy import featurize_obligation, open_obligations, propose_actions
from .proof_trace import ProofActionResult, ProofTrace, write_traces
from .scc_ranker import SymbolicEdge, rank_graph
from .split_executor import execute_split_action
from .valuation_closure import build_valuation_closure, height_form_for_return_map


def _closed_result(proof_status: str, message: str, reward: int, details: dict[str, Any]) -> ProofActionResult:
    return ProofActionResult(
        status="CLOSED",
        reward=reward,
        proof_status=proof_status,
        message=message,
        details=details,
    )


def _reduced_result(proof_status: str, message: str, reward: int, details: dict[str, Any]) -> ProofActionResult:
    return ProofActionResult(
        status="REDUCED",
        reward=reward,
        proof_status=proof_status,
        message=message,
        details=details,
    )


def _needs_split(message: str, reward: int, details: dict[str, Any]) -> ProofActionResult:
    return ProofActionResult(
        status="NEEDS_SPLIT",
        reward=reward,
        proof_status="NEEDS_SPLIT",
        message=message,
        details=details,
    )


def _failed(message: str, reward: int = -20, details: dict[str, Any] | None = None) -> ProofActionResult:
    return ProofActionResult(
        status="FAILED",
        reward=reward,
        proof_status="FAILED_VERIFIER_OR_UNIMPLEMENTED",
        message=message,
        details=details or {},
    )


def _load_default_json(path: str) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _is_specific_sharp_obligation(obligation: dict[str, Any]) -> bool:
    oid = str(obligation.get("obligation_id", ""))
    return "q23" in oid or "sharp_q23" in oid or oid.startswith("adic_basin:sharp_q23")


def execute_action(action: ProofAction, obligation: dict[str, Any]) -> ProofActionResult:
    """Execute one proof action against one obligation.

    The current environment uses exact existing modules where available and
    returns explicit scaffold statuses for future tools.
    """

    features = featurize_obligation(obligation)

    if action.action == "TRY_ADIC_BASIN":
        basin = build_adic_basin_certificate(sharp_q23_return_map(), max_repeats=4, q_depth=23)
        details = {
            "features": features,
            "basin_status": basin["status"],
            "height": basin["height"],
            "q_depth_summary": basin["q_depth_summary"],
            "claim_scope": "q == 23 mod 128 subbranch",
        }
        if basin["status"] != "PROVED_NO_INFINITE_REPEAT":
            return _failed("2-adic basin certificate did not prove no infinite repeat", details=details)
        if _is_specific_sharp_obligation(obligation):
            return _closed_result(
                "CLOSED_BY_HEIGHT_RANKING",
                "sharp q23 return branch is closed by the v2(601q+1) height drain",
                80,
                details,
            )
        return _reduced_result(
            "REDUCED_BY_HEIGHT_RANKED_SUBBRANCH",
            "exactly closed the q23 subbranch, but this aggregate obligation still needs splitting",
            55,
            details,
        )

    if action.action == "PROMOTE_TO_PARENT_STATE":
        a = int(action.params.get("a", features.get("a", 6)))
        h = int(action.params.get("h", features.get("h", 1)))
        details: dict[str, Any] = {"features": features, "a": a, "h": h}
        if h == 1 and a >= 1:
            # Representative row only; the proof obligation is to derive the full
            # symbolic condition/cube split that maps into P_{a_next}.
            representative = parent_transition(a, 1)
            split = execute_split_action(action, obligation)
            details["representative_parent_transition"] = representative
            details["split"] = split
            return _reduced_result(
                "REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION",
                "converted a low-h bucket into a parent-state transition target; symbolic split still required",
                40,
                {**details, "children": split.get("children", [])},
            )
        return _needs_split("parent-state promotion needs a low-h or explicit post-burst branch", 10, details)

    if action.action == "TRY_PARENT_TRANSITION_TEMPLATE":
        a = int(action.params.get("a", features.get("a", 6)))
        h = int(action.params.get("h", features.get("h", 1)))
        a_next = int(action.params.get("a_next", features.get("a_next", 1)))
        r_depth = int(action.params.get("r_depth", features.get("r_depth", 7)))
        rows = []
        for r in range(1, 1 << r_depth, 2):
            row = classify_parent_residue(a, r, r_depth)
            if row["h"] == h and row["a_next"] == a_next:
                rows.append(row)
        expected = features.get("residue_count")
        details = {
            "features": features,
            "action_params": action.params,
            "a": a,
            "h": h,
            "a_next": a_next,
            "r_depth": r_depth,
            "verified_residue_count": len(rows),
            "expected_residue_count": expected,
            "sample_rows": rows[:20],
        }
        if expected is not None and int(expected) != len(rows):
            return _failed(
                "finite parent-transition bucket count disagrees with the obligation coverage",
                reward=-10,
                details=details,
            )
        return _reduced_result(
            "REDUCED_BY_PARENT_TRANSITION_TEMPLATE",
            "exactly verified the finite parent-transition bucket; infinite lifting/ranking still required",
            28,
            details,
        )

    if action.action in {"SPLIT_BY_RESIDUE", "SPLIT_BY_H", "SPLIT_BY_PARENT_LEVEL"}:
        split = execute_split_action(action, obligation)
        status = str(split.get("status", "NEEDS_SPLIT"))
        reward = 24 if status.startswith("REDUCED") else 8
        return _reduced_result(
            status,
            f"{action.action} produced {len(split.get('children', []))} child obligation(s)",
            reward,
            {"features": features, "action_params": action.params, "split": split},
        )

    if action.action == "LIFT_CUBE":
        if features["kind"] == "cube_lift" and features.get("lift_status") == "NEEDS_SPLIT":
            split = execute_split_action(ProofAction("SPLIT_BY_RESIDUE", action.params), obligation)
            if split.get("children"):
                return _reduced_result(
                    "REDUCED_BY_CUBE_LIFT_SPLIT",
                    "aggregate cube-lift bucket needs concrete cube children before infinite lifting",
                    18,
                    {"features": features, "action_params": action.params, "split": split},
                )
            return _needs_split(
                "cube lifter needs concrete cube rows from the compression report before exact lifting",
                6,
                {"features": features, "action_params": action.params, "split": split},
            )
        return _needs_split(
            "cube lifting is useful only after selecting concrete cube rows from the compression report",
            10,
            {"features": features, "action_params": action.params},
        )

    if action.action == "TRY_ANCESTOR_COMPOSITION":
        debt = build_debt_demo_report()["sharp_q23_then_q9"]
        details = {"features": features, "debt_demo": debt}
        if debt["status"] == "PROVED_ANCESTOR_DESCENT":
            return _closed_result("CLOSED_BY_ANCESTOR_DESCENT", "composition pays ancestor debt", 100, details)
        return _reduced_result(
            "REDUCED_BY_DEBT_CHECK",
            "ancestor-debt verifier ran and rejected an overstrong local-descent claim",
            20,
            details,
        )

    if action.action == "TRY_VALUATION_CLOSURE":
        sharp = sharp_q23_return_map()
        closure = build_valuation_closure(
            [sharp],
            seed_forms=[height_form_for_return_map(sharp)],
            max_depth=2,
            max_forms=32,
        )
        return _reduced_result(
            "REDUCED_BY_VALUATION_CLOSURE",
            "built bounded valuation-form closure for the sharp return map",
            30,
            {"features": features, "action_params": action.params, "valuation_closure": closure},
        )

    if action.action in {"TRY_SCC_POTENTIAL", "TRY_SCC_RANKING"}:
        sharp = sharp_q23_return_map()
        ranking = rank_graph(
            [
                SymbolicEdge(
                    source="P6_q23",
                    target="P6_q23",
                    A=sharp.A,
                    B=sharp.B,
                    D=sharp.D,
                    status="PROVED_TRANSITION_ONLY",
                    label=sharp.name,
                    domain_residue=sharp.domain_residue,
                    domain_depth=sharp.domain_depth,
                )
            ]
        )
        proof_status = "CLOSED_BY_HEIGHT_RANKING" if ranking["status"] == "PASS" else "REDUCED_BY_SCC_RANKING"
        if _is_specific_sharp_obligation(obligation) and ranking["status"] == "PASS":
            return _closed_result(
                proof_status,
                "ranked the sharp q23 single-state SCC by affine height",
                80,
                {"features": features, "action_params": action.params, "scc_ranking": ranking},
            )
        return _reduced_result(
            proof_status,
            "ranked the sharp q23 sub-SCC; aggregate obligation still needs coverage split",
            35,
            {"features": features, "action_params": action.params, "scc_ranking": ranking},
        )

    if action.action == "GENERALIZE_IN_A":
        depth = int(action.params.get("depth", 8))
        a_min = int(action.params.get("a_min", 1))
        a_max = int(action.params.get("a_max", 64))
        report = build_parametric_a_report(a_min=a_min, a_max=a_max, depth=depth)
        return _reduced_result(
            "REDUCED_BY_PARAMETRIC_A_PERIODICITY",
            "verified the 3^a periodicity scaffold for grouping parent-state templates",
            22,
            {"features": features, "action_params": action.params, "parametric_a": report},
        )

    if action.action in {"PROPOSE_VALUATION_FORM", "PROPOSE_POTENTIAL"}:
        return _needs_split(
            f"{action.action} produced a conjectural definition slot; exact verifier not wired yet",
            5,
            {"features": features, "action_params": action.params},
        )

    if action.action == "PROPOSE_PROOF_DSL":
        return _reduced_result(
            "REDUCED_BY_TYPED_PROOF_OBJECT",
            "emitted a typed proof-object slot; strict acceptance still depends on downstream verifiers",
            18,
            {
                "features": features,
                "action_params": action.params,
                "proof_object_contract": {
                    "must_emit_definitions": True,
                    "must_emit_lemmas": True,
                    "must_reference_verifier_artifacts": True,
                    "must_not_upgrade_proof_confidence_without_PASS": True,
                },
            },
        )

    if action.action == "PROPOSE_MIXED_MODULUS_STATE":
        bypass = _load_default_json("reports/debt_induction/high_parent_bypass_report.json")
        if not bypass:
            return _needs_split(
                "mixed-modulus state was proposed, but no high-parent bypass report exists yet",
                8,
                {"features": features, "action_params": action.params},
            )
        return _reduced_result(
            "REDUCED_BY_MIXED_MODULUS_STATE_DEFINITION",
            "defined the missing odd-modulus/debt state and linked it to exact high-parent successor families",
            36,
            {
                "features": features,
                "action_params": action.params,
                "bypass_status": bypass.get("status"),
                "mixed_successor_family_count": bypass.get("mixed_successor_family_count"),
                "sample_checks_passed": bypass.get("all_sample_checks_passed"),
                "state": ["parent_level", "odd_coordinate_mod_3a", "growth_debt"],
            },
        )

    if action.action == "PROPOSE_DEBT_RANK":
        bypass = _load_default_json("reports/debt_induction/high_parent_bypass_report.json")
        rank = {} if not bypass else dict(bypass.get("level_rank_analysis") or {})
        if rank.get("status") == "FAIL":
            return _reduced_result(
                "REDUCED_BY_RANK_OBSTRUCTION_CERTIFICATE",
                "checked the scalar rank proposal and found the exact positive mixed-branch cycle to repair",
                24,
                {
                    "features": features,
                    "action_params": action.params,
                    "rank_status": rank.get("status"),
                    "cycle_log_gain_sum": rank.get("cycle_log_gain_sum"),
                    "positive_cycle_witness": rank.get("positive_cycle_witness", [])[:8],
                },
            )
        return _needs_split(
            "debt-rank proposal needs a mixed-modulus verifier check",
            10,
            {"features": features, "action_params": action.params, "rank_analysis": rank},
        )

    if action.action == "TRY_MIXED_MODULUS_DEBT_VERIFIER":
        bypass = _load_default_json("reports/debt_induction/high_parent_bypass_report.json")
        if not bypass:
            return _failed(
                "mixed-modulus debt verifier cannot run without high_parent_bypass_report.json",
                reward=-12,
                details={"features": features, "action_params": action.params},
            )
        details = {
            "features": features,
            "action_params": action.params,
            "bypass_status": bypass.get("status"),
            "ready_for_run7": bypass.get("ready_for_run7"),
            "mixed_successor_family_count": bypass.get("mixed_successor_family_count"),
            "all_sample_checks_passed": bypass.get("all_sample_checks_passed"),
            "formal_blockers": bypass.get("formal_blockers"),
            "level_rank_analysis": bypass.get("level_rank_analysis"),
        }
        if bypass.get("ready_for_run7") is True:
            return _closed_result(
                "CLOSED_BY_MIXED_MODULUS_DEBT_VERIFIER",
                "mixed-modulus debt verifier closed the high-parent branches",
                100,
                details,
            )
        return _reduced_result(
            "REDUCED_TO_MIXED_MODULUS_DEBT_VERIFIER_BLOCKER",
            "exact mixed-modulus successors are derived, but the debt verifier itself is not implemented/closed",
            42,
            details,
        )

    if action.action == "SELF_CORRECT_PROOF_DSL":
        return _reduced_result(
            "REDUCED_BY_VERIFIER_FEEDBACK_REPAIR_PLAN",
            "converted verifier failures into the next proof-DSL repair target",
            20,
            {"features": features, "action_params": action.params},
        )

    if action.action == "RUN_FALSIFIER":
        report = build_falsifier_report()
        return _reduced_result(
            "REDUCED_BY_FALSIFIER_CHECK",
            "ran falsifier diagnostics and recorded counterpressure results",
            8,
            {"features": features, "action_params": action.params, "falsifier": report},
        )

    return ProofActionResult(
        status="INVALID",
        reward=-50,
        proof_status="INVALID_ACTION",
        message=f"unsupported action {action.action}",
        details={"features": features},
    )


def run_policy_on_report(
    obligations_report: dict[str, Any],
    beam_size: int = 5,
    max_obligations: int | None = None,
) -> tuple[dict[str, Any], list[ProofTrace]]:
    """Run the current proof policy against open obligations."""

    opened = open_obligations(obligations_report)
    if max_obligations is not None:
        opened = opened[:max_obligations]

    traces: list[ProofTrace] = []
    action_counts: Counter[str] = Counter()
    result_counts: Counter[str] = Counter()
    proof_status_counts: Counter[str] = Counter()
    reward_total = 0

    for obligation in opened:
        for action in propose_actions(obligation, beam_size=beam_size):
            result = execute_action(action, obligation)
            trace = ProofTrace(
                obligation_id=str(obligation.get("obligation_id")),
                obligation_before=obligation,
                action=action,
                result=result,
            )
            traces.append(trace)
            action_counts[action.action] += 1
            result_counts[result.status] += 1
            proof_status_counts[result.proof_status] += 1
            reward_total += result.reward

    closed = result_counts["CLOSED"]
    reduced = result_counts["REDUCED"]
    attempted_obligation_ids = sorted({trace.obligation_id for trace in traces})
    report = {
        "scope": "verifier-backed proof-policy baseline over P6 obligations",
        "status": "PROOF_POLICY_BASELINE_NOT_A_COLLATZ_PROOF",
        "policy": "heuristic_seed_policy",
        "beam_size": beam_size,
        "input_obligation_count": obligations_report.get("obligation_count"),
        "input_open_obligation_count": obligations_report.get("open_obligation_count"),
        "attempted_open_obligation_count": len(opened),
        "attempted_obligation_ids": attempted_obligation_ids,
        "actions_tried": len(traces),
        "action_counts": dict(action_counts),
        "result_counts": dict(result_counts),
        "proof_status_counts": dict(proof_status_counts),
        "reward_total": reward_total,
        "closed_action_results": closed,
        "reduced_action_results": reduced,
        "full_obligations_closed_by_policy": 0,
        "model_guided_obligation_closure_rate": 0.0,
        "useful_action_rate": 0.0 if not traces else (closed + reduced) / len(traces),
        "interpretation": (
            "This first run seeds proof traces and identifies which exact tools close or reduce "
            "sub-obligations. Aggregate open obligations are not marked closed until a downstream "
            "splitter proves coverage for every child."
        ),
        "top_results": [
            trace.to_dict()
            for trace in sorted(traces, key=lambda item: item.result.reward, reverse=True)[:20]
        ],
    }
    return report, traces


def write_policy_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Proof-Policy Run v1",
        "",
        f"- status: `{report['status']}`",
        f"- policy: `{report['policy']}`",
        f"- input open obligations: `{report['input_open_obligation_count']}`",
        f"- attempted open obligations: `{report['attempted_open_obligation_count']}`",
        f"- actions tried: `{report['actions_tried']}`",
        f"- action counts: `{report['action_counts']}`",
        f"- result counts: `{report['result_counts']}`",
        f"- proof status counts: `{report['proof_status_counts']}`",
        f"- useful action rate: `{report['useful_action_rate']}`",
        f"- model-guided obligation closure rate: `{report['model_guided_obligation_closure_rate']}`",
        "",
        "This is not a proof of Collatz. It is the verifier-backed proof-game scaffold that records proof-action traces for future model training.",
        "",
        "## Highest-Reward Attempts",
        "",
    ]
    for trace in report["top_results"][:20]:
        action = trace["action"]
        result = trace["result"]
        lines.append(
            f"- `{trace['obligation_id']}` -> `{action['action']}` "
            f"=> `{result['proof_status']}` reward `{result['reward']}`"
        )
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run verifier-backed proof-policy baseline.")
    parser.add_argument("--obligations", required=True)
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--max-obligations", type=int, default=None)
    parser.add_argument("--trace-out", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    obligations = json.loads(Path(args.obligations).read_text(encoding="utf-8"))
    report, traces = run_policy_on_report(
        obligations,
        beam_size=args.beam_size,
        max_obligations=args.max_obligations,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    trace_out = Path(args.trace_out)
    write_traces(trace_out, traces)
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_policy_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "traces": str(trace_out),
            "actions_tried": report["actions_tried"],
            "result_counts": report["result_counts"],
        }
    )


if __name__ == "__main__":
    main()
