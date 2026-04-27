"""Mine affine cycle certificates from parent return maps."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console

from .cycle_certificates import (
    AffineReturnMap,
    apply_affine_return,
    certify_affine_return_map,
    compose_affine_return_maps,
)
from .residual_frontier import normalize_residue


def affine_return_from_parent_return_row(row: dict[str, Any]) -> AffineReturnMap:
    """Convert a ``return_maps.py`` row into an affine q-return map."""

    a = int(row["a"])
    t = int(row["t"])
    h = int(row["h"])
    d_power = int(row["q_condition_depth"])
    return AffineReturnMap(
        name=f"P6_return:a={a}:h={h}",
        A=3**a,
        B=(1 << t) * ((1 << h) - 1),
        D=1 << d_power,
        domain_residue=int(row["q_condition_residue"]),
        domain_depth=d_power,
        step_count=2 * a + h,
        description=f"P6 return map from a={a}, h={h}",
    )


def _append_domain_condition(
    current_residue: int,
    current_depth: int,
    current_affine: AffineReturnMap,
    next_map: AffineReturnMap,
) -> tuple[int, int]:
    """Refine source domain so ``current_affine(q)`` lies in ``next_map`` domain."""

    if next_map.domain_residue is None or next_map.domain_depth is None:
        raise ValueError("next map needs a finite residue domain")
    next_depth = next_map.domain_depth
    next_modulus = 1 << next_depth
    current_modulus = 1 << current_depth
    numerator_at_residue = current_affine.A * current_residue + current_affine.B
    if numerator_at_residue % current_affine.D != 0:
        raise AssertionError("current affine is not integral on its source residue")
    base = numerator_at_residue // current_affine.D
    multiplier = current_affine.A * current_modulus // current_affine.D
    if multiplier % 2 != 1:
        raise AssertionError("expected odd multiplier when appending affine domain")
    needed = (normalize_residue(next_map.domain_residue, next_depth) - base) % next_modulus
    s_residue = (pow(multiplier, -1, next_modulus) * needed) % next_modulus
    new_depth = current_depth + next_depth
    new_residue = normalize_residue(current_residue + current_modulus * s_residue, new_depth)
    return new_residue, new_depth


def compose_return_sequence(sequence: list[AffineReturnMap], name: str | None = None) -> AffineReturnMap:
    """Compose a sequence of P6 return maps and compute its exact source domain."""

    if not sequence:
        raise ValueError("sequence must be non-empty")
    first = sequence[0]
    if first.domain_residue is None or first.domain_depth is None:
        raise ValueError("first map needs a finite residue domain")
    source_residue = normalize_residue(first.domain_residue, first.domain_depth)
    source_depth = first.domain_depth
    current = first
    for next_map in sequence[1:]:
        source_residue, source_depth = _append_domain_condition(
            source_residue,
            source_depth,
            current,
            next_map,
        )
        current = compose_affine_return_maps([current, next_map], name="partial")
        current = AffineReturnMap(
            name=current.name,
            A=current.A,
            B=current.B,
            D=current.D,
            domain_residue=source_residue,
            domain_depth=source_depth,
            step_count=current.step_count,
            description=current.description,
        )
    composed = compose_affine_return_maps(sequence, name=name or "->".join(row.name for row in sequence))
    return AffineReturnMap(
        name=composed.name,
        A=composed.A,
        B=composed.B,
        D=composed.D,
        domain_residue=source_residue,
        domain_depth=source_depth,
        step_count=composed.step_count,
        description=composed.description,
    )


def sample_qs_for_domain(return_map: AffineReturnMap, count: int = 8) -> list[int]:
    if return_map.domain_residue is None or return_map.domain_depth is None:
        return []
    modulus = 1 << return_map.domain_depth
    residue = normalize_residue(return_map.domain_residue, return_map.domain_depth)
    start = residue if residue > 0 else modulus
    return [start + modulus * i for i in range(count)]


def return_count_at_depth(return_map: AffineReturnMap, q_depth: int) -> int:
    if return_map.domain_depth is None:
        return 0
    if return_map.domain_depth > q_depth:
        return 0
    return 1 << (q_depth - return_map.domain_depth)


def _sequence_rows(
    maps: list[AffineReturnMap],
    length: int,
    q_depth: int,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if length == 1:
        sequences = [[row] for row in maps]
    elif length == 2:
        sequences = ([left, right] for left in maps for right in maps)
    else:
        raise ValueError("only lengths 1 and 2 are currently supported")

    for sequence in sequences:
        try:
            composed = compose_return_sequence(sequence)
        except (AssertionError, ValueError) as exc:
            rows.append(
                {
                    "status": "COMPOSITION_FAILED",
                    "sequence": [row.name for row in sequence],
                    "error": str(exc),
                }
            )
            continue
        count = return_count_at_depth(composed, q_depth)
        if count == 0:
            continue
        cert = certify_affine_return_map(composed, sample_qs=sample_qs_for_domain(composed, count=4))
        rows.append(
            {
                "status": cert["status"],
                "sequence": [row.name for row in sequence],
                "cycle_length": length,
                "source_q_residue": composed.domain_residue,
                "source_q_depth": composed.domain_depth,
                "count_at_q_depth": count,
                "map": composed.to_dict(),
                "height": cert["height"],
                "fixed_point": cert["fixed_point"],
                "sample_height_drop_passed": cert["sample_height_drop_passed"],
            }
        )
        if limit is not None and len(rows) >= limit:
            break
    rows.sort(
        key=lambda row: (
            0 if row.get("status") == "PROVED_HEIGHT_DECREASE_ON_REPEAT" else 1,
            -int(row.get("count_at_q_depth", 0)),
            str(row.get("sequence")),
        )
    )
    return rows


def build_cycle_mining_report(
    return_report: dict[str, Any],
    q_depth: int,
    max_cycle_length: int = 2,
) -> dict[str, Any]:
    maps = [affine_return_from_parent_return_row(row) for row in return_report.get("maps", [])]
    maps_in_depth = [row for row in maps if row.domain_depth is not None and row.domain_depth <= q_depth]
    sequence_reports: dict[str, Any] = {}
    status_counts: Counter[str] = Counter()
    total_sequences = 0
    for length in range(1, max_cycle_length + 1):
        if length > 2:
            break
        rows = _sequence_rows(maps_in_depth, length=length, q_depth=q_depth)
        total_sequences += len(rows)
        status_counts.update(row["status"] for row in rows)
        sequence_reports[f"length_{length}"] = {
            "sequence_count": len(rows),
            "status_counts": dict(Counter(row["status"] for row in rows)),
            "top_certified_by_coverage": [
                row for row in rows if row["status"] == "PROVED_HEIGHT_DECREASE_ON_REPEAT"
            ][:40],
        }
    return {
        "scope": "P6 return-map affine cycle mining",
        "q_depth": q_depth,
        "max_cycle_length": max_cycle_length,
        "return_map_count": len(maps),
        "return_map_count_with_domain_at_depth": len(maps_in_depth),
        "total_sequence_rows": total_sequences,
        "overall_status_counts": dict(status_counts),
        "sequence_reports": sequence_reports,
        "claim_status": "PROOF_SCAFFOLD_WITH_EXACT_CYCLE_CERTIFICATES",
    }


def write_cycle_mining_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Parent Return Cycle Mining",
        "",
        f"- q-depth: `{report['q_depth']}`",
        f"- return maps: `{report['return_map_count']}`",
        f"- return maps in depth: `{report['return_map_count_with_domain_at_depth']}`",
        f"- status counts: `{report['overall_status_counts']}`",
        "",
    ]
    for name, section in report["sequence_reports"].items():
        lines.extend([f"## {name}", "", f"- sequence count: `{section['sequence_count']}`", ""])
        for row in section["top_certified_by_coverage"][:20]:
            lines.append(
                f"- `{row['status']}` `{row['sequence']}` count `{row['count_at_q_depth']}` "
                f"height `v2({row['height']['linear_form']})`"
            )
        lines.append("")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mine cycle certificates from P6 return maps.")
    parser.add_argument("--return-report", required=True)
    parser.add_argument("--q-depth", type=int, default=23)
    parser.add_argument("--max-cycle-length", type=int, default=2)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    return_report = json.loads(Path(args.return_report).read_text(encoding="utf-8"))
    report = build_cycle_mining_report(return_report, args.q_depth, max_cycle_length=args.max_cycle_length)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_cycle_mining_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "status_counts": report["overall_status_counts"],
            "return_maps_in_depth": report["return_map_count_with_domain_at_depth"],
        }
    )


if __name__ == "__main__":
    main()
