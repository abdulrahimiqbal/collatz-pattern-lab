"""2-adic basin acceleration for affine return cycles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .cycle_certificates import AffineReturnMap, certify_affine_return_map, sharp_q23_return_map


def fixed_point_residue_mod_power(return_map: AffineReturnMap, depth: int) -> int:
    """Return the 2-adic fixed-point residue modulo ``2**depth``."""

    if depth < 0:
        raise ValueError("depth must be non-negative")
    modulus = 1 << depth
    if modulus == 1:
        return 0
    alpha = return_map.height_alpha
    if alpha % 2 == 0:
        raise ValueError("A-D must be odd to have a unique 2-adic basin residue")
    return (-return_map.height_beta * pow(alpha, -1, modulus)) % modulus


def repeat_m_condition(return_map: AffineReturnMap, repeats: int) -> dict[str, Any]:
    """Return the cylinder condition for at least ``repeats`` cycle traversals."""

    if repeats < 1:
        raise ValueError("repeats must be positive")
    depth = return_map.d_power * repeats
    residue = fixed_point_residue_mod_power(return_map, depth)
    return {
        "repeats": repeats,
        "q_residue": residue,
        "q_depth": depth,
        "condition": f"q == {residue} mod 2^{depth}",
    }


def build_adic_basin_certificate(
    return_map: AffineReturnMap,
    max_repeats: int = 4,
    q_depth: int | None = None,
) -> dict[str, Any]:
    """Build a theorem-shaped 2-adic basin certificate."""

    cert = certify_affine_return_map(return_map)
    conditions = [repeat_m_condition(return_map, m) for m in range(1, max_repeats + 1)]
    rows = []
    if q_depth is not None:
        for index, row in enumerate(conditions):
            count_at_depth = 0 if row["q_depth"] > q_depth else 1 << (q_depth - row["q_depth"])
            next_count = (
                0
                if index + 1 >= len(conditions) or conditions[index + 1]["q_depth"] > q_depth
                else 1 << (q_depth - conditions[index + 1]["q_depth"])
            )
            rows.append(
                {
                    **row,
                    "count_at_q_depth": count_at_depth,
                    "exit_after_this_repeat_count": max(0, count_at_depth - next_count),
                }
            )

    status = (
        "PROVED_NO_INFINITE_REPEAT"
        if cert["status"] == "PROVED_HEIGHT_DECREASE_ON_REPEAT"
        else cert["status"]
    )
    return {
        "status": status,
        "cycle_map": return_map.to_dict(),
        "fixed_point_2adic": f"-{return_map.height_beta}/{return_map.height_alpha}",
        "fixed_point_residue_conditions": conditions,
        "height": cert["height"],
        "height_drop_per_repeat": cert["height"]["drop_per_repeat"],
        "positive_integer_fixed_point": cert["fixed_point"],
        "q_depth_summary": None if q_depth is None else {"q_depth": q_depth, "rows": rows},
        "underlying_cycle_certificate_status": cert["status"],
    }


def build_adic_basin_report(q_depth: int = 23, max_repeats: int = 4) -> dict[str, Any]:
    sharp = sharp_q23_return_map()
    return {
        "scope": "2-adic basin acceleration for affine return cycles",
        "claim_status": "PROOF_COMPILER_COMPONENT",
        "basins": [build_adic_basin_certificate(sharp, max_repeats=max_repeats, q_depth=q_depth)],
    }


def write_adic_basin_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = ["# 2-adic Basin Acceleration", "", f"- status: `{report['claim_status']}`", ""]
    for basin in report["basins"]:
        m = basin["cycle_map"]
        lines.extend(
            [
                f"## {m['name']}",
                "",
                f"- status: `{basin['status']}`",
                f"- map: `q -> ({m['A']}q + {m['B']})/{m['D']}`",
                f"- fixed point in Z_2: `{basin['fixed_point_2adic']}`",
                f"- height: `v2({basin['height']['linear_form']})`",
                f"- height drop per repeat: `{basin['height_drop_per_repeat']}`",
                f"- positive fixed point: `{basin['positive_integer_fixed_point']}`",
                "",
                "### Repeat Cylinders",
                "",
            ]
        )
        for row in basin["fixed_point_residue_conditions"]:
            lines.append(f"- repeat `{row['repeats']}`+: `{row['condition']}`")
        if basin["q_depth_summary"] is not None:
            lines.extend(["", "### Finite-depth Counts", ""])
            for row in basin["q_depth_summary"]["rows"]:
                lines.append(
                    f"- repeat `{row['repeats']}`+: count `{row['count_at_q_depth']}`, "
                    f"exit after this repeat `{row['exit_after_this_repeat_count']}`"
                )
        lines.append("")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build 2-adic basin acceleration reports.")
    parser.add_argument("--q-depth", type=int, default=23)
    parser.add_argument("--max-repeats", type=int, default=4)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_adic_basin_report(q_depth=args.q_depth, max_repeats=args.max_repeats)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_adic_basin_markdown(report, md_out)
    Console().print({"out": str(out), "markdown": str(md_out), "status": report["basins"][0]["status"]})


if __name__ == "__main__":
    main()
