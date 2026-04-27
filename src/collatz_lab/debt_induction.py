"""Debt-carrying parent-state induction search.

The top weighted P6 buckets are blocked because their low-h forced bursts
usually move to lower parent states while still expanding the ancestor value.
This module searches for a finite-state debt potential that might pay that
expansion, but it does not promote the result to proof closure unless the
certificate passes exactness gates.

The current search intentionally records a same-depth residue projection as a
diagnostic only.  If the diagnostic potential passes at one depth but fails at
another, that is evidence that the proposed state space is under-refined, not a
proof.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import h_star
from .parent_states import parent_transition
from .potential import PotentialTransition, find_log_potential
from .top_bucket_closure import parent_burst_affine_on_n


def _target_pairs(target_buckets: list[dict[str, Any]]) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for bucket in target_buckets:
        pair = (int(bucket["a"]), int(bucket["h"]))
        if pair in seen:
            continue
        seen.add(pair)
        pairs.append(pair)
    return pairs


def _state_id(a: int, r_residue: int) -> str:
    return f"P{a}:r{r_residue}"


def _min_n_for_state(a: int, r_residue: int, r_depth: int) -> int:
    modulus = 1 << (a + r_depth)
    residue = ((1 << a) * r_residue - 1) % modulus
    return residue if residue > 0 else modulus


def build_same_depth_residue_potential_search(
    target_buckets: list[dict[str, Any]],
    r_depth: int,
    epsilon: float = 1e-9,
    max_states: int = 250_000,
) -> dict[str, Any]:
    """Build a same-depth residue graph and try a log potential.

    The projection ``r_next mod 2**r_depth`` is useful for finding candidate
    rankings, but it is not an exact universal transition certificate because
    image residues can require additional source bits after division.  The
    returned ``claim_status`` therefore remains diagnostic even on PASS.
    """

    if r_depth < 1:
        raise ValueError("r_depth must be positive")
    starts: list[tuple[int, int]] = []
    for a, h in _target_pairs(target_buckets):
        for r in range(1, 1 << r_depth, 2):
            row = parent_transition(a, r)
            if int(row["h"]) == h:
                starts.append((a, r))

    seen: set[tuple[int, int]] = set(starts)
    queue: deque[tuple[int, int]] = deque(starts)
    edges: list[PotentialTransition] = []
    terminal_counts: Counter[str] = Counter()
    bad_states: list[dict[str, Any]] = []

    while queue:
        if len(seen) > max_states:
            bad_states.append(
                {
                    "status": "STATE_LIMIT_EXCEEDED",
                    "max_states": max_states,
                    "seen_states": len(seen),
                }
            )
            break
        a, r = queue.popleft()
        min_n = _min_n_for_state(a, r, r_depth)
        if min_n <= 1:
            terminal_counts["finite_exception_n1"] += 1
            continue

        row = parent_transition(a, r)
        h = int(row["h"])
        if h >= r_depth:
            if h_star(a) <= r_depth:
                terminal_counts["high_h_direct_burst_escape"] += 1
                continue
            bad_states.append(
                {
                    "status": "HIGH_H_REQUIRES_DEEPER_SPLIT",
                    "a": a,
                    "r_residue": r,
                    "r_depth": r_depth,
                    "h": h,
                    "h_star": h_star(a),
                }
            )
            continue

        block = parent_burst_affine_on_n(a, h)
        a_next = int(row["a_next"])
        r_next = int(row["r_next"]) % (1 << r_depth)
        target = (a_next, r_next)
        edges.append(
            PotentialTransition(
                from_state=_state_id(a, r),
                to_state=_state_id(a_next, r_next),
                affine_A=int(block["A"]),
                affine_B=int(block["B"]),
                affine_D=int(block["D"]),
                min_n=min_n,
                label=f"P{a}:r={r}:h={h}->P{a_next}",
            )
        )
        if target not in seen:
            seen.add(target)
            queue.append(target)

    potential = find_log_potential(edges, epsilon=epsilon) if edges else {"status": "UNKNOWN", "reason": "no edges"}
    witness = potential.get("negative_cycle_witness", [])
    return {
        "claim_status": "DIAGNOSTIC_NOT_PROOF",
        "projection": "same_depth_r_residue",
        "r_depth": r_depth,
        "epsilon": epsilon,
        "start_state_count": len(starts),
        "reachable_state_count": len(seen),
        "edge_count": len(edges),
        "terminal_counts": dict(terminal_counts),
        "bad_state_count": len(bad_states),
        "bad_states_sample": bad_states[:20],
        "potential_status": potential.get("status"),
        "potential_reason": potential.get("reason"),
        "potential_tight_transitions": potential.get("tight_transitions", [])[:20],
        "negative_cycle_witness": witness[:20] if isinstance(witness, list) else [],
        "formal_exactness_passed": False,
        "formal_exactness_blocker": (
            "same-depth projection is not an exact universal transition certificate; "
            "image residues after division can require deeper source bits"
        ),
    }


def build_debt_induction_report(
    weighted_report: dict[str, Any],
    top_n: int = 10,
    r_depths: list[int] | None = None,
    epsilon: float = 1e-9,
    max_states: int = 250_000,
    variable_depth_certificate: dict[str, Any] | None = None,
    high_parent_branch_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target_buckets = list(weighted_report.get("target_buckets") or [])[:top_n]
    depths = r_depths or [7, 8, 9, 10, 11, 12, 13]
    depth_reports = [
        build_same_depth_residue_potential_search(
            target_buckets,
            r_depth=depth,
            epsilon=epsilon,
            max_states=max_states,
        )
        for depth in depths
    ]
    failing_depths = [
        row["r_depth"]
        for row in depth_reports
        if row.get("potential_status") != "PASS" or row.get("bad_state_count", 0)
    ]
    passing_depths = [
        row["r_depth"]
        for row in depth_reports
        if row.get("potential_status") == "PASS" and not row.get("bad_state_count", 0)
    ]
    exact_depths = [row["r_depth"] for row in depth_reports if row.get("formal_exactness_passed")]
    variable_depth_ready = bool(
        variable_depth_certificate
        and variable_depth_certificate.get("status") == "EXACT_VARIABLE_DEPTH_POTENTIAL_PASS"
        and variable_depth_certificate.get("ready_for_run7") is True
    )
    high_parent_ready = (
        None
        if high_parent_branch_report is None
        else bool(high_parent_branch_report.get("ready_for_run7") is True)
    )
    formal_certificate_sources = []
    if variable_depth_ready:
        formal_certificate_sources.append("variable_depth_transition_certificate")
    if high_parent_ready:
        formal_certificate_sources.append("high_parent_branch_report")
    ready = variable_depth_ready
    first_failure = next(
        (
            row
            for row in depth_reports
            if row.get("potential_status") != "PASS" or row.get("bad_state_count", 0)
        ),
        None,
    )
    formal_blockers = []
    if not ready:
        formal_blockers.extend(
            [
                "no exact debt-carrying induction certificate has been verified",
                "same-depth residue potentials are diagnostic only",
            ]
        )
        if variable_depth_certificate is None:
            formal_blockers.append("missing variable-depth transition certificate")
        elif not variable_depth_ready:
            formal_blockers.extend(variable_depth_certificate.get("formal_blockers") or [])
        if high_parent_branch_report is not None and not high_parent_ready:
            formal_blockers.extend(high_parent_branch_report.get("formal_blockers") or [])
        if failing_depths:
            formal_blockers.append("same-depth candidate potentials are unstable across checked depths")
        elif not variable_depth_ready:
            formal_blockers.append("candidate potential still lacks exact image-depth lifting")
    return {
        "status": "PROVED_DEBT_CARRYING_PARENT_INDUCTION" if ready else "DEBT_INDUCTION_NOT_FIXED",
        "ready_for_run7": ready,
        "top_n": top_n,
        "target_obligations": [str(row.get("obligation_id")) for row in target_buckets],
        "r_depths_checked": depths,
        "passing_diagnostic_depths": passing_depths,
        "failing_or_blocked_depths": failing_depths,
        "formal_exact_depths": exact_depths,
        "formal_certificate_sources": formal_certificate_sources,
        "variable_depth_certificate_status": None
        if variable_depth_certificate is None
        else variable_depth_certificate.get("status"),
        "variable_depth_ready_for_run7": None
        if variable_depth_certificate is None
        else variable_depth_certificate.get("ready_for_run7"),
        "high_parent_branch_status": None
        if high_parent_branch_report is None
        else high_parent_branch_report.get("status"),
        "high_parent_branch_ready_for_run7": high_parent_ready,
        "formal_blockers": [] if ready else list(dict.fromkeys(str(item) for item in formal_blockers)),
        "first_failure": first_failure,
        "depth_reports": depth_reports,
        "next_step": (
            "Apply the verified variable-depth transition certificate to the top weighted buckets."
            if ready
            else (
                "Close the symbolic high-parent valuation branches exposed by the variable-depth "
                "certificate, then rerun this debt-induction gate. Do not run RUN-007 until "
                "ready_for_run7 is true."
            )
        ),
    }


def write_debt_induction_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Debt-Carrying Parent Induction Gate",
        "",
        f"- status: `{report['status']}`",
        f"- ready for RUN-007: `{report['ready_for_run7']}`",
        f"- checked depths: `{report['r_depths_checked']}`",
        f"- passing diagnostic depths: `{report['passing_diagnostic_depths']}`",
        f"- failing or blocked depths: `{report['failing_or_blocked_depths']}`",
        f"- formal exact depths: `{report['formal_exact_depths']}`",
        f"- formal certificate sources: `{report['formal_certificate_sources']}`",
        f"- variable-depth status: `{report['variable_depth_certificate_status']}`",
        f"- high-parent branch status: `{report['high_parent_branch_status']}`",
        "",
        "## Formal Blockers",
        "",
    ]
    for blocker in report["formal_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Depth Results", ""])
    for row in report["depth_reports"]:
        lines.append(
            f"- r_depth `{row['r_depth']}`: potential `{row['potential_status']}`, "
            f"states `{row['reachable_state_count']}`, edges `{row['edge_count']}`, "
            f"bad states `{row['bad_state_count']}`"
        )
    lines.extend(["", "## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search/gate debt-carrying parent-state induction certificates.")
    parser.add_argument("--weighted-report", required=True)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--r-depths", default="7,8,9,10,11,12,13")
    parser.add_argument("--epsilon", type=float, default=1e-9)
    parser.add_argument("--max-states", type=int, default=250_000)
    parser.add_argument("--variable-depth-certificate", default=None)
    parser.add_argument("--high-parent-branch-report", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    weighted = json.loads(Path(args.weighted_report).read_text(encoding="utf-8"))
    depths = [int(item.strip()) for item in args.r_depths.split(",") if item.strip()]
    report = build_debt_induction_report(
        weighted,
        top_n=args.top_n,
        r_depths=depths,
        epsilon=args.epsilon,
        max_states=args.max_states,
        variable_depth_certificate=(
            json.loads(Path(args.variable_depth_certificate).read_text(encoding="utf-8"))
            if args.variable_depth_certificate
            else None
        ),
        high_parent_branch_report=(
            json.loads(Path(args.high_parent_branch_report).read_text(encoding="utf-8"))
            if args.high_parent_branch_report
            else None
        ),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_debt_induction_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "status": report["status"],
            "ready_for_run7": report["ready_for_run7"],
        }
    )


if __name__ == "__main__":
    main()
