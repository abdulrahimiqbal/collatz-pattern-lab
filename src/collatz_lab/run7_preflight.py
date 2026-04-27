"""RUN-007 readiness gate.

This gate is intentionally conservative.  It does not certify Collatz; it only
decides whether the repo has the exact artifacts needed to justify launching
RUN-007 instead of repeating the same failed proof attempt.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console


RUN7_PREFLIGHT_SCHEMA = "collatz_lab.run7_preflight"


def _load(path: str | Path) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _jsonl_rows(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _check(name: str, passed: bool, required: bool = True, **details: Any) -> dict[str, Any]:
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "required": required,
        "details": details,
    }


def build_run7_preflight(
    run_id: str = "RUN-006-top10-parent-debt-audit",
    run_dir: str | Path = "reports/runs/RUN-006-top10-parent-debt-audit",
    central_attempts_log: str | Path = "proof_attempts.jsonl",
    replay_report_path: str | Path = "reports/proof_replay_training_report.json",
    debt_gate_path: str | Path = "reports/debt_induction/top10_gate.json",
    variable_depth_path: str | Path = "reports/debt_induction/variable_depth_transition_certificate.json",
    high_parent_branch_path: str | Path = "reports/debt_induction/high_parent_branch_report.json",
    high_parent_bypass_path: str | Path = "reports/debt_induction/high_parent_bypass_report.json",
    force_diagnostic_run: bool = False,
) -> dict[str, Any]:
    run_root = Path(run_dir)
    proof_attempt_search = _load(run_root / "proof_attempt_search.json")
    run_attempt_rows = _jsonl_rows(run_root / "proof_attempts.jsonl")
    central_rows = _jsonl_rows(central_attempts_log)
    replay_report = _load(replay_report_path)
    debt_gate = _load(debt_gate_path)
    variable_depth = _load(variable_depth_path)
    high_parent_branch = _load(high_parent_branch_path)
    high_parent_bypass = _load(high_parent_bypass_path)

    selected = {}
    if proof_attempt_search and proof_attempt_search.get("ranked_attempts"):
        selected = dict(proof_attempt_search["ranked_attempts"][0])
    central_run_rows = [row for row in central_rows if row.get("run_id") == run_id]
    replay_actions = set((replay_report or {}).get("repair_action_counts", {}))

    checks = [
        _check(
            "proof_attempt_beam_exists",
            bool(proof_attempt_search)
            and int(proof_attempt_search.get("attempt_count", 0)) >= 5
            and bool(proof_attempt_search.get("selected_attempt_id")),
            attempt_count=None if proof_attempt_search is None else proof_attempt_search.get("attempt_count"),
            selected_attempt_id=None if proof_attempt_search is None else proof_attempt_search.get("selected_attempt_id"),
        ),
        _check(
            "per_run_attempt_ledger_updated",
            len(run_attempt_rows) >= 5,
            row_count=len(run_attempt_rows),
            path=str(run_root / "proof_attempts.jsonl"),
        ),
        _check(
            "central_attempt_ledger_updated",
            len(central_run_rows) >= 5,
            central_row_count=len(central_rows),
            rows_for_run=len(central_run_rows),
            path=str(central_attempts_log),
        ),
        _check(
            "proof_replay_training_ready",
            bool(replay_report)
            and int(replay_report.get("example_count", 0)) > 0
            and {
                "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE",
                "PROVE_PARAMETRIC_LIFTING_LEMMA",
                "PROVE_DEBT_CARRYING_INDUCTION",
            }.issubset(replay_actions),
            example_count=None if replay_report is None else replay_report.get("example_count"),
            repair_action_counts=None if replay_report is None else replay_report.get("repair_action_counts"),
        ),
        _check(
            "debt_induction_gate_ready",
            bool(debt_gate) and debt_gate.get("ready_for_run7") is True,
            status=None if debt_gate is None else debt_gate.get("status"),
            ready_for_run7=None if debt_gate is None else debt_gate.get("ready_for_run7"),
            formal_blockers=None if debt_gate is None else debt_gate.get("formal_blockers"),
        ),
        _check(
            "variable_depth_certificate_ready",
            bool(variable_depth) and variable_depth.get("ready_for_run7") is True,
            status=None if variable_depth is None else variable_depth.get("status"),
            ready_for_run7=None if variable_depth is None else variable_depth.get("ready_for_run7"),
            bad_state_count=None if variable_depth is None else variable_depth.get("bad_state_count"),
            potential_status=None if variable_depth is None else variable_depth.get("potential_status"),
            formal_blockers=None if variable_depth is None else variable_depth.get("formal_blockers"),
        ),
        _check(
            "symbolic_high_parent_branch_executor_built",
            bool(high_parent_branch)
            and int(high_parent_branch.get("branch_count", 0)) >= 0
            and high_parent_branch.get("schema") == "collatz_lab.high_parent_branch",
            required=False,
            status=None if high_parent_branch is None else high_parent_branch.get("status"),
            branch_count=None if high_parent_branch is None else high_parent_branch.get("branch_count"),
            open_branch_count=None if high_parent_branch is None else high_parent_branch.get("open_branch_count"),
        ),
        _check(
            "symbolic_high_parent_branches_closed",
            bool(variable_depth and variable_depth.get("ready_for_run7") is True)
            or bool(high_parent_branch and high_parent_branch.get("ready_for_run7") is True),
            status=None if high_parent_branch is None else high_parent_branch.get("status"),
            ready_for_run7=None if high_parent_branch is None else high_parent_branch.get("ready_for_run7"),
            formal_blockers=None if high_parent_branch is None else high_parent_branch.get("formal_blockers"),
        ),
        _check(
            "mixed_modulus_high_parent_bypass_built",
            bool(high_parent_bypass)
            and high_parent_bypass.get("schema") == "collatz_lab.high_parent_bypass"
            and high_parent_bypass.get("status") == "MIXED_MODULUS_BYPASS_BUILT",
            required=False,
            status=None if high_parent_bypass is None else high_parent_bypass.get("status"),
            mixed_successor_family_count=None
            if high_parent_bypass is None
            else high_parent_bypass.get("mixed_successor_family_count"),
            all_sample_checks_passed=None
            if high_parent_bypass is None
            else high_parent_bypass.get("all_sample_checks_passed"),
        ),
        _check(
            "mixed_modulus_debt_verifier_ready",
            bool(variable_depth and variable_depth.get("ready_for_run7") is True)
            or bool(high_parent_bypass and high_parent_bypass.get("ready_for_run7") is True),
            status=None if high_parent_bypass is None else high_parent_bypass.get("status"),
            ready_for_run7=None if high_parent_bypass is None else high_parent_bypass.get("ready_for_run7"),
            formal_blockers=None if high_parent_bypass is None else high_parent_bypass.get("formal_blockers"),
        ),
        _check(
            "selected_attempt_has_new_exact_evidence",
            selected.get("focus_step") not in {"S3-global-parent-transitions", "S4-parametric-lifting", "S5-debt-induction"}
            or bool(variable_depth and variable_depth.get("ready_for_run7") is True),
            selected_variant=selected.get("variant_id"),
            selected_focus_step=selected.get("focus_step"),
            selected_blocking_steps=selected.get("blocking_steps"),
        ),
    ]
    failed_required = [row for row in checks if row["required"] and row["status"] != "PASS"]
    status = (
        "READY_FOR_RUN7"
        if not failed_required
        else "FORCED_DIAGNOSTIC_RUN_ALLOWED_WITH_BLOCKERS"
        if force_diagnostic_run
        else "NOT_READY_FOR_RUN7"
    )
    blockers = [row["name"] for row in failed_required]
    return {
        "schema": RUN7_PREFLIGHT_SCHEMA,
        "version": 1,
        "run_id": run_id,
        "status": status,
        "ready_for_run7": status == "READY_FOR_RUN7",
        "diagnostic_run_allowed": status in {"READY_FOR_RUN7", "FORCED_DIAGNOSTIC_RUN_ALLOWED_WITH_BLOCKERS"},
        "force_diagnostic_run": force_diagnostic_run,
        "checks": checks,
        "blocking_checks": blockers,
        "next_step": (
            "Launch RUN-007 with the selected proof-attempt beam."
            if status == "READY_FOR_RUN7"
            else "Launch only as a diagnostic run; proof confidence must remain 0 until strict verification passes."
            if status == "FORCED_DIAGNOSTIC_RUN_ALLOWED_WITH_BLOCKERS"
            else "Do not launch RUN-007; fix the failing required preflight checks first."
        ),
    }


def write_preflight_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# RUN-007 Preflight",
        "",
        f"- status: `{report['status']}`",
        f"- ready for RUN-007: `{report['ready_for_run7']}`",
        f"- diagnostic run allowed: `{report['diagnostic_run_allowed']}`",
        f"- force diagnostic run: `{report['force_diagnostic_run']}`",
        f"- blocking checks: `{report['blocking_checks']}`",
        "",
        "## Checks",
        "",
    ]
    for row in report["checks"]:
        lines.append(f"- `{row['name']}`: `{row['status']}`")
    lines.extend(["", "## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the conservative RUN-007 readiness gate.")
    parser.add_argument("--run-id", default="RUN-006-top10-parent-debt-audit")
    parser.add_argument("--run-dir", default="reports/runs/RUN-006-top10-parent-debt-audit")
    parser.add_argument("--central-attempts-log", default="proof_attempts.jsonl")
    parser.add_argument("--replay-report", default="reports/proof_replay_training_report.json")
    parser.add_argument("--debt-gate", default="reports/debt_induction/top10_gate.json")
    parser.add_argument("--variable-depth", default="reports/debt_induction/variable_depth_transition_certificate.json")
    parser.add_argument("--high-parent-branch", default="reports/debt_induction/high_parent_branch_report.json")
    parser.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    parser.add_argument("--force-diagnostic-run", action="store_true")
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_run7_preflight(
        run_id=args.run_id,
        run_dir=args.run_dir,
        central_attempts_log=args.central_attempts_log,
        replay_report_path=args.replay_report,
        debt_gate_path=args.debt_gate,
        variable_depth_path=args.variable_depth,
        high_parent_branch_path=args.high_parent_branch,
        high_parent_bypass_path=args.high_parent_bypass,
        force_diagnostic_run=args.force_diagnostic_run,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_preflight_markdown(report, md_out)
    Console().print({"out": str(out), "status": report["status"], "ready_for_run7": report["ready_for_run7"]})


if __name__ == "__main__":
    main()
