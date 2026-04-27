"""Variable-depth parent-state transition certificates.

The older debt-induction search used a same-depth residue projection.  That is
useful for diagnostics but not exact: after dividing by a variable power of two,
the image residue may only be determined at a lower depth.  This module builds
an exact variable-depth transition graph where a source state
``P_a:r mod 2^d`` maps to ``P_b:r' mod 2^(d-h-b)`` when the available source
bits prove the division exponent and next parent level.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import h_star, is_burst_descent
from .parent_states import parent_transition
from .potential import PotentialTransition, find_log_potential
from .top_bucket_closure import parent_burst_affine_on_n


def _state_id(a: int, r_residue: int, r_depth: int) -> str:
    return f"P{a}:r{r_residue}:d{r_depth}"


def _min_odd_residue(r_residue: int, r_depth: int) -> int:
    modulus = 1 << r_depth
    residue = r_residue % modulus
    if residue == 0:
        residue = modulus
    if residue % 2 == 0:
        residue += modulus
    return residue


def _min_n(a: int, r_residue: int, r_depth: int) -> int:
    return (1 << a) * _min_odd_residue(r_residue, r_depth) - 1


def exact_variable_depth_transition(a: int, r_residue: int, r_depth: int) -> dict[str, Any]:
    """Return the exact variable-depth transition for one source residue class."""

    if a < 1:
        raise ValueError("a must be positive")
    if r_depth < 1:
        raise ValueError("r_depth must be positive")
    if r_residue % 2 != 1:
        raise ValueError("r_residue must be odd")
    r = r_residue % (1 << r_depth)
    row = parent_transition(a, r)
    h = int(row["h"])
    threshold = h_star(a)
    if h >= threshold:
        if r_depth >= threshold:
            return {
                "status": "CLOSED_BY_DIRECT_BURST_DESCENT",
                "a": a,
                "r_residue": r,
                "r_depth": r_depth,
                "h": h,
                "h_star": threshold,
                "exactness": {
                    "h_ge_h_star_is_constant": True,
                    "required_source_depth": threshold,
                    "available_source_depth": r_depth,
                },
                "terminal": True,
                "reason": "source residue proves h>=h_star, so every member descends directly",
            }
        return {
            "status": "NEEDS_DEEPER_SOURCE_SPLIT",
            "a": a,
            "r_residue": r,
            "r_depth": r_depth,
            "h": h,
            "h_star": threshold,
            "required_source_depth": threshold,
            "terminal": False,
            "reason": "representative descends, but source depth is too shallow to prove h>=h_star for the whole class",
        }

    a_next = int(row["a_next"])
    required_source_depth = h + a_next + 1
    if r_depth < required_source_depth:
        return {
            "status": "NEEDS_DEEPER_SOURCE_SPLIT",
            "a": a,
            "r_residue": r,
            "r_depth": r_depth,
            "h": h,
            "a_next": a_next,
            "required_source_depth": required_source_depth,
            "terminal": False,
            "reason": "source depth does not prove both h and the next parent level for the whole class",
        }
    target_depth = r_depth - h - a_next
    if target_depth < 1:
        return {
            "status": "TARGET_DEPTH_EXHAUSTED",
            "a": a,
            "r_residue": r,
            "r_depth": r_depth,
            "h": h,
            "a_next": a_next,
            "terminal": False,
            "reason": "transition is exact but leaves no positive target residue depth for induction",
        }
    target_residue = int(row["r_next"]) % (1 << target_depth)
    if target_residue % 2 != 1:
        raise AssertionError("target residue should remain odd")
    block = parent_burst_affine_on_n(a, h)
    return {
        "status": "PROVED_EXACT_VARIABLE_DEPTH_TRANSITION",
        "a": a,
        "r_residue": r,
        "r_depth": r_depth,
        "h": h,
        "a_next": a_next,
        "r_next_residue": target_residue,
        "target_depth": target_depth,
        "target_state": _state_id(a_next, target_residue, target_depth),
        "terminal": False,
        "exactness": {
            "required_source_depth": required_source_depth,
            "available_source_depth": r_depth,
            "target_depth_formula": "r_depth - h - a_next",
            "identity": "r_next = (3^a*r + 2^h - 1) / 2^(h+a_next)",
        },
        "parent_burst_affine_on_n": block,
    }


def _target_pairs(weighted_report: dict[str, Any], top_n: int) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for bucket in list(weighted_report.get("target_buckets") or [])[:top_n]:
        pair = (int(bucket["a"]), int(bucket["h"]))
        if pair in seen:
            continue
        seen.add(pair)
        pairs.append(pair)
    return pairs


def build_variable_depth_certificate(
    weighted_report: dict[str, Any],
    top_n: int = 10,
    source_depth: int = 14,
    max_refinement_depth: int | None = None,
    min_target_depth: int = 1,
    epsilon: float = 1e-9,
    max_states: int = 250_000,
) -> dict[str, Any]:
    """Build a bounded exact variable-depth transition certificate attempt."""

    refinement_depth = source_depth if max_refinement_depth is None else max_refinement_depth
    if refinement_depth < source_depth:
        raise ValueError("max_refinement_depth must be >= source_depth")
    starts: list[tuple[int, int, int]] = []
    for a, h in _target_pairs(weighted_report, top_n=top_n):
        for r in range(1, 1 << source_depth, 2):
            if int(parent_transition(a, r)["h"]) == h:
                starts.append((a, r, source_depth))
    queue: deque[tuple[int, int, int]] = deque(starts)
    seen: set[tuple[int, int, int]] = set(starts)
    edges: list[PotentialTransition] = []
    transition_rows: list[dict[str, Any]] = []
    bad_states: list[dict[str, Any]] = []
    refinement_rows: list[dict[str, Any]] = []
    terminal_counts: Counter[str] = Counter()

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
        a, r, depth = queue.popleft()
        if depth < min_target_depth:
            bad_states.append(
                {
                    "status": "TARGET_DEPTH_BELOW_MINIMUM",
                    "a": a,
                    "r_residue": r,
                    "r_depth": depth,
                    "min_target_depth": min_target_depth,
                }
            )
            continue
        transition = exact_variable_depth_transition(a, r, depth)
        transition_rows.append(transition)
        status = str(transition["status"])
        if transition.get("terminal"):
            terminal_counts[status] += 1
            continue
        if status != "PROVED_EXACT_VARIABLE_DEPTH_TRANSITION":
            required_depth = int(transition.get("required_source_depth", depth + 1) or depth + 1)
            if status == "NEEDS_DEEPER_SOURCE_SPLIT" and required_depth <= refinement_depth:
                factor = 1 << (required_depth - depth)
                children = [
                    (a, r + offset * (1 << depth), required_depth)
                    for offset in range(factor)
                ]
                refinement_rows.append(
                    {
                        "from_state": _state_id(a, r, depth),
                        "required_source_depth": required_depth,
                        "child_count": len(children),
                        "reason": transition.get("reason"),
                    }
                )
                for child in children:
                    if child not in seen:
                        seen.add(child)
                        queue.append(child)
                continue
            bad_states.append(transition)
            continue
        target = (
            int(transition["a_next"]),
            int(transition["r_next_residue"]),
            int(transition["target_depth"]),
        )
        block = transition["parent_burst_affine_on_n"]
        edges.append(
            PotentialTransition(
                from_state=_state_id(a, r, depth),
                to_state=str(transition["target_state"]),
                affine_A=int(block["A"]),
                affine_B=int(block["B"]),
                affine_D=int(block["D"]),
                min_n=_min_n(a, r, depth),
                label=f"P{a}:r={r}:d={depth}:h={transition['h']}->P{transition['a_next']}:d{transition['target_depth']}",
            )
        )
        if target not in seen:
            seen.add(target)
            queue.append(target)

    potential = find_log_potential(edges, epsilon=epsilon) if edges else {"status": "UNKNOWN", "reason": "no nonterminal edges"}
    exact_projection_passed = not bad_states
    potential_passed = potential.get("status") == "PASS"
    ready = exact_projection_passed and potential_passed and bool(starts)
    return {
        "scope": "variable-depth parent-state transition certificate",
        "status": "EXACT_VARIABLE_DEPTH_POTENTIAL_PASS" if ready else "VARIABLE_DEPTH_CERTIFICATE_NOT_READY",
        "ready_for_run7": ready,
        "top_n": top_n,
        "source_depth": source_depth,
        "max_refinement_depth": refinement_depth,
        "min_target_depth": min_target_depth,
        "start_state_count": len(starts),
        "reachable_state_count": len(seen),
        "edge_count": len(edges),
        "terminal_counts": dict(terminal_counts),
        "bad_state_count": len(bad_states),
        "bad_states": bad_states,
        "bad_states_sample": bad_states[:40],
        "exact_projection_passed": exact_projection_passed,
        "potential_status": potential.get("status"),
        "potential_reason": potential.get("reason"),
        "potential_tight_transitions": potential.get("tight_transitions", [])[:20],
        "negative_cycle_witness": potential.get("negative_cycle_witness", [])[:20]
        if isinstance(potential.get("negative_cycle_witness"), list)
        else [],
        "transition_status_counts": dict(Counter(str(row.get("status")) for row in transition_rows)),
        "refinement_count": len(refinement_rows),
        "refinement_sample": refinement_rows[:40],
        "transition_sample": transition_rows[:50],
        "formal_blockers": []
        if ready
        else [
            "variable-depth exact projection still has blocked states" if bad_states else "variable-depth exact projection passed",
            "log-potential/ranking over exact variable-depth graph did not pass" if not potential_passed else "log-potential/ranking passed",
            "bounded certificate still needs audit before theorem promotion",
        ],
        "next_step": (
            "Refine blocked variable-depth states by increasing source depth or adding a richer rank/debt state; "
            "RUN-007 remains blocked until ready_for_run7 is true."
        ),
    }


def write_variable_depth_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Variable-Depth Transition Certificate",
        "",
        f"- status: `{report['status']}`",
        f"- ready for RUN-007: `{report['ready_for_run7']}`",
        f"- source depth: `{report['source_depth']}`",
        f"- max refinement depth: `{report['max_refinement_depth']}`",
        f"- start states: `{report['start_state_count']}`",
        f"- reachable states: `{report['reachable_state_count']}`",
        f"- exact projection passed: `{report['exact_projection_passed']}`",
        f"- potential status: `{report['potential_status']}`",
        f"- bad states: `{report['bad_state_count']}`",
        f"- transition status counts: `{report['transition_status_counts']}`",
        f"- refinement count: `{report['refinement_count']}`",
        "",
        "## Formal Blockers",
        "",
    ]
    for blocker in report["formal_blockers"]:
        lines.append(f"- {blocker}")
    if report.get("bad_states_sample"):
        lines.extend(["", "## Bad State Sample", ""])
        for row in report["bad_states_sample"][:12]:
            lines.append(f"- `{row.get('status')}`: P{row.get('a')}:r{row.get('r_residue')}:d{row.get('r_depth')} - {row.get('reason')}")
    lines.extend(["", "## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build variable-depth parent-state transition certificate attempt.")
    parser.add_argument("--weighted-report", required=True)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--source-depth", type=int, default=14)
    parser.add_argument("--max-refinement-depth", type=int, default=None)
    parser.add_argument("--min-target-depth", type=int, default=1)
    parser.add_argument("--epsilon", type=float, default=1e-9)
    parser.add_argument("--max-states", type=int, default=250_000)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    weighted = json.loads(Path(args.weighted_report).read_text(encoding="utf-8"))
    report = build_variable_depth_certificate(
        weighted,
        top_n=args.top_n,
        source_depth=args.source_depth,
        max_refinement_depth=args.max_refinement_depth,
        min_target_depth=args.min_target_depth,
        epsilon=args.epsilon,
        max_states=args.max_states,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_variable_depth_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "status": report["status"],
            "ready_for_run7": report["ready_for_run7"],
            "bad_states": report["bad_state_count"],
        }
    )


if __name__ == "__main__":
    main()
