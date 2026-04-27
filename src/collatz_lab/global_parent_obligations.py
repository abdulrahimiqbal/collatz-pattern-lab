"""Global parent-state proof obligations.

This report is the bridge from the P6 laboratory to the universal theorem.  It
records the exact coverage identity for odd integers, but it remains open until
the transition templates for all parent states ``P_a`` are proven and ranked.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console


def _load_optional(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def build_global_parent_obligations(
    parent_state_system: dict[str, Any] | None = None,
    parametric_a: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build universal ``P_a`` obligations and current blocking set."""

    obligations: list[dict[str, Any]] = [
        {
            "obligation_id": "even_descent",
            "status": "CLOSED_BY_ANCESTOR_DESCENT",
            "scope": "all even n>2",
            "claim": "C(n)=n/2<n for even n>2",
            "coverage": {"universal": True},
        },
        {
            "obligation_id": "odd_parent_state_cover",
            "status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE",
            "scope": "all odd n",
            "claim": "Every odd n can be written uniquely as n=2^a*r-1 with a>=1 and r odd.",
            "coverage": {"universal": True},
        },
    ]

    if parent_state_system is None:
        obligations.append(
            {
                "obligation_id": "parent_state_transition_templates",
                "status": "UNKNOWN",
                "scope": "all P_a transitions",
                "claim": "No parent-state transition diagnostic report was loaded.",
                "coverage": {},
            }
        )
    else:
        obligations.append(
            {
                "obligation_id": "parent_state_transition_templates",
                "status": "UNKNOWN",
                "scope": "all P_a transitions",
                "claim": "Current parent-state transition report is finite in a and finite in r-depth.",
                "coverage": {
                    "a_min": parent_state_system.get("a_min"),
                    "a_max": parent_state_system.get("a_max"),
                    "r_depth": parent_state_system.get("r_depth"),
                    "row_count": parent_state_system.get("row_count"),
                    "state_count": parent_state_system.get("state_count"),
                },
            }
        )

    if parametric_a is None:
        obligations.append(
            {
                "obligation_id": "parametric_a_templates",
                "status": "NEEDS_SPLIT",
                "scope": "a-periodic transition templates",
                "claim": "No parametric-a periodicity scaffold was loaded.",
                "coverage": {},
            }
        )
    else:
        obligations.append(
            {
                "obligation_id": "parametric_a_templates",
                "status": "NEEDS_SPLIT",
                "scope": "a-periodic transition templates",
                "claim": "3^a periodicity is verified at fixed 2-adic depth, but transition templates still need exact lifting.",
                "coverage": {
                    "depth": parametric_a.get("depth"),
                    "period": parametric_a.get("period"),
                    "group_count": parametric_a.get("group_count"),
                    "sample_period_check_passed": parametric_a.get("sample_period_check_passed"),
                },
            }
        )

    open_rows = [row for row in obligations if not str(row["status"]).startswith("CLOSED_BY_")]
    return {
        "scope": "global Collatz parent-state obligations",
        "status": "INCOMPLETE_OPEN_OBLIGATIONS" if open_rows else "PASS",
        "coverage": {
            "evens": "closed by immediate descent",
            "odds": "covered by P_a representation",
            "status": "UNIVERSAL_ENTRY_COVERAGE_ONLY" if open_rows else "UNIVERSAL_PARENT_STATES",
        },
        "obligation_count": len(obligations),
        "open_obligation_count": len(open_rows),
        "closed_obligation_count": len(obligations) - len(open_rows),
        "obligations": obligations,
        "minimal_blocking_set": open_rows,
    }


def build_global_theorem_candidate(global_obligations: dict[str, Any]) -> dict[str, Any]:
    """Build a small theorem-candidate wrapper around global obligations."""

    unknowns = global_obligations.get("minimal_blocking_set", [])
    return {
        "theorem": "forall n > 1 exists k >= 1 such that C^k(n) < n",
        "coverage": global_obligations.get("coverage", {}),
        "status": "PASS" if not unknowns else "FAIL",
        "verifier_status": "PASS" if not unknowns else "FAIL",
        "unknown_obligations": unknowns,
        "supporting_report": "parent_state_global_obligations.json",
    }


def write_global_parent_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Global Parent-State Obligations",
        "",
        f"- status: `{report['status']}`",
        f"- open obligations: `{report['open_obligation_count']}`",
        f"- coverage status: `{report['coverage']['status']}`",
        "",
        "This report is universal only for entry into parent states. Transition closure remains a mathematical obligation until every open row is closed.",
        "",
        "## Obligations",
        "",
    ]
    for row in report["obligations"]:
        lines.append(f"- `{row['obligation_id']}`: `{row['status']}` - {row['claim']}")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build global parent-state proof obligations.")
    parser.add_argument("--parent-state-system", default="reports/parent_state_system_a1_a20_r7.json")
    parser.add_argument("--parametric-a", default="reports/parametric_a_depth8.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--theorem-out", default=None)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_global_parent_obligations(
        _load_optional(args.parent_state_system),
        _load_optional(args.parametric_a),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_global_parent_markdown(report, md_out)
    theorem_out = Path(args.theorem_out) if args.theorem_out else None
    if theorem_out is not None:
        theorem_out.parent.mkdir(parents=True, exist_ok=True)
        theorem_out.write_text(
            json.dumps(build_global_theorem_candidate(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    Console().print({"out": str(out), "status": report["status"], "open": report["open_obligation_count"]})


if __name__ == "__main__":
    main()
