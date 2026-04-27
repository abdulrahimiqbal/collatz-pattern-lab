"""Lift compressed finite q-cubes into infinite proof obligations."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .adic_basin import build_adic_basin_certificate
from .cube_compress import Cube
from .cycle_miner import affine_return_from_parent_return_row
from .residual_frontier import classify_q_residue, normalize_residue


def cube_from_dict(row: dict[str, Any]) -> Cube:
    return Cube(bits=str(row["bits"]), depth=int(row["depth"]), bit_order=str(row.get("bit_order", "lsb")))


def low_congruence_from_cube(cube: Cube) -> tuple[int, int] | None:
    """Return ``(residue, depth)`` if the cube is a low-bit congruence."""

    if cube.bit_order != "lsb":
        return None
    fixed = [(index, char) for index, char in enumerate(cube.bits) if char != "*"]
    if not fixed:
        return 0, 0
    indexes = [index for index, _ in fixed]
    if indexes != list(range(len(indexes))):
        return None
    depth = len(indexes)
    residue = sum(int(char) << index for index, char in fixed)
    return residue, depth


def congruence_subsets(residue: int, depth: int, target_residue: int, target_depth: int) -> bool:
    """Return whether ``q == residue mod 2**depth`` implies target congruence."""

    if depth < target_depth:
        return False
    return normalize_residue(residue, target_depth) == normalize_residue(target_residue, target_depth)


def lift_cube(
    cube_row: dict[str, Any],
    set_name: str,
    burst_report: dict[str, Any],
    return_report: dict[str, Any],
    max_steps: int = 120,
) -> dict[str, Any]:
    cube = cube_from_dict(cube_row)
    congruence = low_congruence_from_cube(cube)
    base = {
        "set": set_name,
        "cube": cube_row,
        "count_covered": cube_row.get("count_covered"),
    }
    if congruence is None:
        return {**base, "status": "NEEDS_SPLIT", "reason": "cube is not a low-bit congruence"}
    residue, depth = congruence
    base.update({"q_residue": residue, "q_depth": depth, "condition": f"q == {residue} mod 2^{depth}"})

    for family in burst_report.get("families", []):
        if congruence_subsets(residue, depth, int(family["q_residue"]), int(family["q_depth"])):
            return {
                **base,
                "status": "PROVED_INFINITE_ANCESTOR_DESCENT",
                "mechanism": "forced_burst_family",
                "matched_family": family,
            }

    if set_name.startswith("k") or set_name == "residual_certified":
        result = classify_q_residue(residue, depth, max_steps=max_steps)
        if result["status"] == "CERTIFIED_DESCENT":
            return {
                **base,
                "status": "PROVED_INFINITE_ANCESTOR_DESCENT",
                "mechanism": "stable_affine_descent",
                "k": result["k"],
                "affine_A": result["affine_A"],
                "affine_B": result["affine_B"],
                "affine_D": result["affine_D"],
            }

    for row in return_report.get("maps", []):
        if congruence_subsets(residue, depth, int(row["q_condition_residue"]), int(row["q_condition_depth"])):
            return_map = affine_return_from_parent_return_row(row)
            basin = build_adic_basin_certificate(return_map, max_repeats=3, q_depth=max(depth, int(row["q_condition_depth"])))
            return {
                **base,
                "status": "PROVED_INFINITE_HEIGHT_RANKED_RETURN",
                "mechanism": "affine_return_adic_basin",
                "matched_return_map": row,
                "adic_basin": basin,
            }

    return {**base, "status": "NEEDS_SPLIT", "reason": "no infinite lift proof found"}


def build_cube_lift_report(
    cube_report: dict[str, Any],
    burst_report: dict[str, Any],
    return_report: dict[str, Any],
    max_steps: int = 120,
) -> dict[str, Any]:
    set_reports: dict[str, Any] = {}
    overall = Counter()
    for set_name, set_payload in cube_report.get("sets", {}).items():
        cube_rows = set_payload.get("cubes") or set_payload.get("largest_cubes") or []
        lifts = [lift_cube(row, set_name, burst_report, return_report, max_steps=max_steps) for row in cube_rows]
        counts = Counter(row["status"] for row in lifts)
        overall.update(counts)
        infinite = sum(count for status, count in counts.items() if status.startswith("PROVED_INFINITE"))
        set_reports[set_name] = {
            "cube_count": len(cube_rows),
            "status_counts": dict(counts),
            "infinite_lift_count": infinite,
            "infinite_lift_rate": 0.0 if not cube_rows else infinite / len(cube_rows),
            "lifts": lifts,
        }
    total_cubes = sum(row["cube_count"] for row in set_reports.values())
    total_lifted = sum(row["infinite_lift_count"] for row in set_reports.values())
    return {
        "scope": "P6 compressed cube infinite-lift report",
        "claim_status": "PROOF_OBLIGATION_LIFTER",
        "total_cubes": total_cubes,
        "overall_status_counts": dict(overall),
        "overall_infinite_lift_count": total_lifted,
        "overall_infinite_lift_rate": 0.0 if total_cubes == 0 else total_lifted / total_cubes,
        "sets": set_reports,
    }


def write_cube_lift_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# P6 Cube Infinite-Lift Report",
        "",
        f"- total cubes: `{report['total_cubes']}`",
        f"- infinite lift count: `{report['overall_infinite_lift_count']}`",
        f"- infinite lift rate: `{report['overall_infinite_lift_rate']:.4f}`",
        f"- status counts: `{report['overall_status_counts']}`",
        "",
    ]
    for set_name, row in report["sets"].items():
        lines.extend(
            [
                f"## {set_name}",
                "",
                f"- cubes: `{row['cube_count']}`",
                f"- infinite lift rate: `{row['infinite_lift_rate']:.4f}`",
                f"- statuses: `{row['status_counts']}`",
                "",
            ]
        )
        for lift in row["lifts"][:20]:
            lines.append(f"- `{lift['status']}` `{lift.get('condition')}` via `{lift.get('mechanism', lift.get('reason'))}`")
        lines.append("")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lift compressed q-cubes into infinite claims.")
    parser.add_argument("--cube-report", required=True)
    parser.add_argument("--burst-report", required=True)
    parser.add_argument("--return-report", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    cube_report = json.loads(Path(args.cube_report).read_text(encoding="utf-8"))
    burst_report = json.loads(Path(args.burst_report).read_text(encoding="utf-8"))
    return_report = json.loads(Path(args.return_report).read_text(encoding="utf-8"))
    report = build_cube_lift_report(cube_report, burst_report, return_report)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_cube_lift_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "overall_infinite_lift_rate": report["overall_infinite_lift_rate"],
            "status_counts": report["overall_status_counts"],
        }
    )


if __name__ == "__main__":
    main()
