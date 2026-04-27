"""Exact parent return maps for the ``n = 64*q - 1`` region."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import burst_post_division_value, forced_burst_image, v2_int
from .residual_frontier import normalize_residue


def parent_return_residue(a: int, h: int) -> dict[str, Any]:
    """Return the ``r`` congruence for returning to ``63 mod 64``.

    For ``n = 2**a*r - 1``, after the forced burst and exactly ``h``
    divisions, the post-burst value is
    ``y = (3**a*r - 1) / 2**h``. The condition ``y == -1 mod 64`` is
    equivalent to

        ``3**a*r == 1 - 2**h mod 2**(h+6)``.
    """

    if a < 0:
        raise ValueError("a must be non-negative")
    if h < 0:
        raise ValueError("h must be non-negative")
    depth = h + 6
    modulus = 1 << depth
    inv = pow(pow(3, a, modulus), -1, modulus)
    residue = ((1 - (1 << h)) * inv) % modulus
    return {
        "a": a,
        "h": h,
        "modulus_depth": depth,
        "modulus": modulus,
        "r_residue": residue,
        "valid_odd": residue % 2 == 1,
    }


def returns_to_parent(a: int, r: int) -> bool:
    """Return whether the post-burst value is ``63 mod 64``."""

    y = burst_post_division_value(a, r)
    return y % 64 == 63


def parent_q_prime(a: int, r: int) -> int:
    """Return ``q'`` when the burst/division block returns to the parent."""

    h = v2_int(forced_burst_image(a, r))
    y = burst_post_division_value(a, r)
    if y % 64 != 63:
        raise ValueError("post-burst value does not return to n = 64*q - 1")
    return (y + 1) // 64


def parent_q_prime_projection_for_map(
    row: dict[str, Any],
    q_depth: int,
    max_enumerated_depth: int = 12,
) -> dict[str, Any]:
    """Project a source return-map condition to image q'-classes.

    At fixed q-depth ``P``, a source condition has depth
    ``t+h+6``. The remaining ``P-(t+h+6)`` free source bits become image
    q'-bits under

        ``q' = base + 3**a * s``.

    Because ``3**a`` is odd, the projection covers every q'-residue at the
    resulting image depth.
    """

    if q_depth < 0:
        raise ValueError("q_depth must be non-negative")
    a = int(row["a"])
    h = int(row["h"])
    r_residue = int(row["r_residue"])
    source_depth = int(row["q_condition_depth"])
    if source_depth > q_depth:
        return {
            "a": a,
            "h": h,
            "source_q_depth": source_depth,
            "q_depth": q_depth,
            "status": "SOURCE_CONDITION_DEEPER_THAN_Q_DEPTH",
        }

    denominator = 1 << (h + 6)
    numerator = (3**a) * r_residue - 1 + (1 << h)
    if numerator % denominator != 0:
        raise AssertionError("return-map residue did not produce integral q' base")
    image_depth = q_depth - source_depth
    image_modulus = 1 << image_depth
    base = (numerator // denominator) % image_modulus
    multiplier = pow(3, a, image_modulus) if image_modulus > 1 else 0
    covers_all = image_modulus == 1 or multiplier % 2 == 1
    residues: list[int] | None = None
    if image_depth <= max_enumerated_depth:
        residues = sorted({(base + multiplier * s) % image_modulus for s in range(image_modulus)})
    return {
        "a": a,
        "h": h,
        "source_q_depth": source_depth,
        "source_q_residue": int(row["q_condition_residue"]),
        "q_depth": q_depth,
        "q_image_depth": image_depth,
        "q_prime_base": base,
        "q_prime_multiplier_mod": multiplier,
        "covers_all_residues_at_image_depth": covers_all,
        "projected_residue_count": image_modulus if covers_all else (None if residues is None else len(residues)),
        "projected_residues": residues,
        "status": "PROJECTED_IMAGE_CLASSES",
    }


def _sample_return_map(a: int, h: int, r_residue: int, r_depth: int, sample_limit: int = 16) -> bool:
    modulus = 1 << r_depth
    for i in range(sample_limit):
        r = r_residue + i * modulus
        if r <= 0 or r % 2 != 1:
            continue
        if v2_int(forced_burst_image(a, r)) != h:
            return False
        if not returns_to_parent(a, r):
            return False
        if parent_q_prime(a, r) < 0:
            return False
    return True


def derive_parent_return_maps(a_min: int, a_max: int, h_min: int, h_max: int) -> list[dict[str, Any]]:
    """Enumerate symbolic return-map conditions."""

    if a_min < 6:
        raise ValueError("a_min must be at least 6 for the 63 mod 64 parent")
    if a_max < a_min:
        raise ValueError("a_max must be >= a_min")
    if h_min < 0 or h_max < h_min:
        raise ValueError("invalid h range")

    rows: list[dict[str, Any]] = []
    for a in range(a_min, a_max + 1):
        t = a - 6
        for h in range(h_min, h_max + 1):
            residue = parent_return_residue(a, h)
            r_depth = int(residue["modulus_depth"])
            r_residue = int(residue["r_residue"])
            q_depth = t + r_depth
            q_residue = normalize_residue((1 << t) * r_residue, q_depth)
            row = {
                "a": a,
                "t": t,
                "h": h,
                "r_residue": r_residue,
                "r_depth": r_depth,
                "q_condition_residue": q_residue,
                "q_condition_depth": q_depth,
                "q_prime_formula": "(3^a*r - 1 + 2^h) / 2^(h+6)",
                "valid_odd": bool(residue["valid_odd"]),
                "sample_check_passed": _sample_return_map(a, h, r_residue, r_depth),
                "status": "PROVED_SYMBOLIC_CONGRUENCE",
            }
            rows.append(row)
    return rows


def compare_return_maps_to_residual_images(
    return_maps: list[dict[str, Any]],
    residual_report: dict[str, Any],
) -> dict[str, Any]:
    """Compare derived map source classes to observed shallow image classes.

    The residual report records observed *image* q-classes, while this module
    derives *source* q-conditions for return maps. The schemas are not the same,
    so this comparison is a conservative normalization check at matching
    depths rather than a proof of equality.
    """

    observed_rows = residual_report.get("inside_parent_images", {}).get("top_classes", [])
    observed = {
        (int(row["q_image_depth"]), normalize_residue(int(row["q_image_residue"]), int(row["q_image_depth"])))
        for row in observed_rows
    }
    derived = {
        (
            int(row["q_condition_depth"]),
            normalize_residue(int(row["q_condition_residue"]), int(row["q_condition_depth"])),
        )
        for row in return_maps
    }
    matched = observed & derived
    return {
        "comparison_note": (
            "Observed residual rows are image classes; derived rows are source "
            "conditions. Matching here only means an identical normalized "
            "q-class appears at the same depth."
        ),
        "derived_map_count": len(return_maps),
        "observed_image_count": len(observed),
        "matched_count": len(matched),
        "matched": [{"q_depth": depth, "q_residue": residue} for depth, residue in sorted(matched)],
        "unmatched_observed": [
            {"q_depth": depth, "q_residue": residue} for depth, residue in sorted(observed - matched)
        ],
        "unmatched_derived_at_depth": [
            {"q_depth": depth, "q_residue": residue}
            for depth, residue in sorted(derived - observed)
            if any(obs_depth == depth for obs_depth, _ in observed)
        ][:100],
    }


def compare_return_map_images_to_residual_images(
    return_maps: list[dict[str, Any]],
    residual_report: dict[str, Any],
    q_depth: int | None = None,
) -> dict[str, Any]:
    """Compare projected return-map images to observed residual image classes."""

    q_depth = int(q_depth if q_depth is not None else residual_report.get("q_depth", 20))
    observed_rows = residual_report.get("inside_parent_images", {}).get("all_classes")
    if observed_rows is None:
        observed_rows = residual_report.get("inside_parent_images", {}).get("top_classes", [])

    observed_by_depth: dict[int, set[int]] = {}
    for row in observed_rows:
        depth = int(row["q_image_depth"])
        residue = normalize_residue(int(row["q_image_residue"]), depth)
        observed_by_depth.setdefault(depth, set()).add(residue)

    projected_by_depth: dict[int, set[int]] = {depth: set() for depth in observed_by_depth}
    projection_rows = []
    reproducing_maps = []
    for row in return_maps:
        projection = parent_q_prime_projection_for_map(row, q_depth=q_depth)
        projection_rows.append(projection)
        if projection["status"] != "PROJECTED_IMAGE_CLASSES":
            continue
        depth = int(projection["q_image_depth"])
        if depth not in observed_by_depth:
            continue
        if projection["covers_all_residues_at_image_depth"]:
            residues = set(range(1 << depth))
        else:
            residues = set(projection.get("projected_residues") or [])
        projected_by_depth.setdefault(depth, set()).update(residues)
        if observed_by_depth[depth].issubset(residues):
            reproducing_maps.append(
                {
                    "a": projection["a"],
                    "h": projection["h"],
                    "q_image_depth": depth,
                    "observed_classes_reproduced": len(observed_by_depth[depth]),
                }
            )

    matched = {
        depth: observed_by_depth[depth] & projected_by_depth.get(depth, set())
        for depth in observed_by_depth
    }
    unmatched = {
        depth: observed_by_depth[depth] - projected_by_depth.get(depth, set())
        for depth in observed_by_depth
    }
    projected_depth_counts: dict[int, int] = {}
    skipped_projection_counts: dict[str, int] = {}
    for projection in projection_rows:
        if projection["status"] != "PROJECTED_IMAGE_CLASSES":
            status = str(projection["status"])
            skipped_projection_counts[status] = skipped_projection_counts.get(status, 0) + 1
            continue
        depth = int(projection["q_image_depth"])
        projected_depth_counts[depth] = projected_depth_counts.get(depth, 0) + 1

    return {
        "comparison_note": (
            "This projects each exact source return-map condition through q' and "
            "compares image-side q'-classes at the residual report q-depth."
        ),
        "q_depth": q_depth,
        "observed_image_class_count": sum(len(values) for values in observed_by_depth.values()),
        "matched_observed_image_class_count": sum(len(values) for values in matched.values()),
        "unmatched_observed_image_class_count": sum(len(values) for values in unmatched.values()),
        "observed_by_depth": [
            {"q_image_depth": depth, "count": len(values), "residues": sorted(values)}
            for depth, values in sorted(observed_by_depth.items())
        ],
        "projected_depth_counts": [
            {"q_image_depth": depth, "map_count": count}
            for depth, count in sorted(projected_depth_counts.items())
        ],
        "skipped_projection_counts": [
            {"status": status, "map_count": count}
            for status, count in sorted(skipped_projection_counts.items())
        ],
        "matched_by_depth": [
            {"q_image_depth": depth, "count": len(values), "residues": sorted(values)}
            for depth, values in sorted(matched.items())
        ],
        "unmatched_observed": [
            {"q_image_depth": depth, "q_image_residue": residue}
            for depth, values in sorted(unmatched.items())
            for residue in sorted(values)
        ],
        "maps_that_individually_reproduce_observed_depths": reproducing_maps[:100],
        "projection_examples": projection_rows[:40],
    }


def build_return_map_report(
    a_min: int,
    a_max: int,
    h_min: int,
    h_max: int,
    residual_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    maps = derive_parent_return_maps(a_min, a_max, h_min, h_max)
    report: dict[str, Any] = {
        "scope": "parent n = 64*q - 1",
        "a_min": a_min,
        "a_max": a_max,
        "h_min": h_min,
        "h_max": h_max,
        "map_count": len(maps),
        "maps": maps,
    }
    if residual_report is not None:
        report["source_condition_comparison"] = compare_return_maps_to_residual_images(maps, residual_report)
        report["residual_image_projection_comparison"] = compare_return_map_images_to_residual_images(
            maps,
            residual_report,
        )
    return report


def write_return_map_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Parent Return Maps",
        "",
        "These maps are exact congruence conditions for returning to `n = 64q - 1` after a forced burst.",
        "",
        f"- map count: `{report['map_count']}`",
        "",
        "## First Maps",
        "",
    ]
    for row in report["maps"][:40]:
        lines.append(
            f"- `a={row['a']}`, `h={row['h']}`: "
            f"`r == {row['r_residue']} mod 2^{row['r_depth']}`, "
            f"`q == {row['q_condition_residue']} mod 2^{row['q_condition_depth']}`, "
            f"sample check `{row['sample_check_passed']}`"
        )
    if "residual_image_projection_comparison" in report:
        comparison = report["residual_image_projection_comparison"]
        lines.extend(
            [
                "",
                "## Residual Image Projection Comparison",
                "",
                f"- observed image classes: `{comparison['observed_image_class_count']}`",
                f"- matched observed image classes: `{comparison['matched_observed_image_class_count']}`",
                f"- unmatched observed image classes: `{comparison['unmatched_observed_image_class_count']}`",
                f"- projected depth counts: `{comparison['projected_depth_counts']}`",
                "",
            ]
        )
    lines.append("")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Derive exact parent return maps.")
    parser.add_argument("--a-min", type=int, default=6)
    parser.add_argument("--a-max", type=int, default=20)
    parser.add_argument("--h-min", type=int, default=1)
    parser.add_argument("--h-max", type=int, default=20)
    parser.add_argument("--residual-report", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    residual = None
    if args.residual_report:
        residual = json.loads(Path(args.residual_report).read_text(encoding="utf-8"))
    report = build_return_map_report(args.a_min, args.a_max, args.h_min, args.h_max, residual_report=residual)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_return_map_markdown(report, md_out)
    Console().print({"map_count": report["map_count"], "out": str(out), "markdown": str(md_out)})


if __name__ == "__main__":
    main()
