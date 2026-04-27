"""Executable proof-obligation split actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .cube_compress import Cube
from .parent_state_system import classify_parent_residue
from .proof_actions import ProofAction, action_from_dict


def split_cube_by_first_star(cube_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Split a cube by its first wildcard bit."""

    bits = str(cube_row["bits"])
    if "*" not in bits:
        return [cube_row]
    index = bits.index("*")
    children = []
    for bit in "01":
        child_bits = bits[:index] + bit + bits[index + 1 :]
        child = Cube(child_bits, depth=int(cube_row["depth"]), bit_order=str(cube_row.get("bit_order", "lsb")))
        children.append(child.to_dict())
    return children


def split_cube_obligation_by_residue(obligation: dict[str, Any]) -> dict[str, Any]:
    cube = obligation.get("cube") or obligation.get("coverage", {}).get("cube")
    if not cube:
        return {
            "status": "NEEDS_SPLIT",
            "reason": "obligation does not carry a concrete cube",
            "children": [],
        }
    children = split_cube_by_first_star(cube)
    return {
        "status": "REDUCED_BY_RESIDUE_SPLIT",
        "children": [
            {
                "obligation_id": f"{obligation.get('obligation_id', 'obligation')}:bit_split:{idx}",
                "status": "NEEDS_SPLIT",
                "scope": obligation.get("scope", "cube split"),
                "cube": child,
            }
            for idx, child in enumerate(children)
        ],
    }


def split_parent_bucket_by_parent_level(
    a: int,
    h: int | None = None,
    r_depth: int = 7,
) -> dict[str, Any]:
    """Split a parent bucket by finite-depth next parent level."""

    buckets: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for r in range(1, 1 << r_depth, 2):
        row = classify_parent_residue(a, r, r_depth)
        if h is not None and row["h"] != h:
            continue
        buckets.setdefault((row["h"], row["a_next"]), []).append(row)
    children = []
    for (child_h, a_next), rows in sorted(buckets.items()):
        children.append(
            {
                "obligation_id": f"P{a}:h={child_h}:to=P{a_next}:rdepth={r_depth}",
                "status": "NEEDS_SPLIT",
                "scope": "finite-depth parent-state split",
                "coverage": {
                    "a": a,
                    "h": child_h,
                    "a_next": a_next,
                    "r_depth": r_depth,
                    "residue_count": len(rows),
                },
                "transition_rule": f"P_{a}->P_{a_next}",
            }
        )
    return {
        "status": "REDUCED_BY_PARENT_LEVEL_SPLIT",
        "a": a,
        "h_filter": h,
        "r_depth": r_depth,
        "child_count": len(children),
        "children": children,
    }


def execute_split_action(action: ProofAction, obligation: dict[str, Any]) -> dict[str, Any]:
    """Execute a split action and return child obligations."""

    if action.action == "SPLIT_BY_RESIDUE":
        return split_cube_obligation_by_residue(obligation)
    if action.action in {"SPLIT_BY_H", "SPLIT_BY_PARENT_LEVEL", "PROMOTE_TO_PARENT_STATE"}:
        coverage = obligation.get("coverage") if isinstance(obligation.get("coverage"), dict) else {}
        a = int(action.params.get("a", coverage.get("a", 6)))
        h_value = action.params.get("h", coverage.get("h"))
        h = None if h_value is None else int(h_value)
        r_depth = int(action.params.get("r_depth", 7))
        return split_parent_bucket_by_parent_level(a=a, h=h, r_depth=r_depth)
    return {"status": "UNKNOWN_SPLIT_ACTION", "children": []}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute a proof split action against one obligation JSON.")
    parser.add_argument("--action-json", required=True)
    parser.add_argument("--obligation-json", required=True)
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    action = action_from_dict(json.loads(args.action_json))
    obligation = json.loads(args.obligation_json)
    report = execute_split_action(action, obligation)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print({"out": str(out), "status": report["status"], "children": len(report.get("children", []))})


if __name__ == "__main__":
    main()
