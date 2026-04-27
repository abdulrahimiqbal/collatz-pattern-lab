"""Residual q-frontier analysis after subtracting verified escape cubes."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console
from tqdm import tqdm

from .collatz import collatz_step
from .transitions import (
    affine_image_residue,
    classify_image,
    cube_n_residue_for_q,
    q_cube_completion_residues,
)

STATUS_COVERED_BY_EXISTING_CUBE = 1
STATUS_CERTIFIED_RESIDUAL_DESCENT = 2
STATUS_UNKNOWN_RESIDUAL = 3


def normalize_residue(residue: int, depth: int) -> int:
    """Return ``residue`` normalized modulo ``2**depth``.

    Report fields named ``*_depth`` use depth to mean modulus ``2**depth``.
    Therefore serialized residues for those fields must live in
    ``0 <= residue < 2**depth``. Use a separate ``raw_*`` field when callers
    need to preserve an unnormalized intermediate.
    """

    if depth < 0:
        raise ValueError("depth must be non-negative")
    return residue % (1 << depth)


def _append_affine_step(a: int, b: int, d: int, bit: int) -> tuple[int, int, int]:
    if bit == 0:
        return a, b, d * 2
    if bit == 1:
        return 3 * a, 3 * b + d, d
    raise ValueError("Parity prefixes contain only 0/1 values")


def _bits_to_string(bits: Iterable[int]) -> str:
    return "".join("1" if bit else "0" for bit in bits)


def _affine_signature_id(a: int, b: int, d: int) -> str:
    return f"standard:A={a}:B={b}:D={d}"


def classify_q_residue(
    q_residue: int,
    q_depth: int,
    burst_length: int = 6,
    max_steps: int = 120,
) -> dict[str, Any]:
    """Classify one q-class inside ``n = 2**burst*q - 1``."""

    n_mod_power = q_depth + burst_length
    n_modulus = 1 << n_mod_power
    n_residue = cube_n_residue_for_q(q_residue, burst_length, n_modulus)
    min_n = n_residue if n_residue > 0 else n_modulus
    checked_steps = min(max_steps, n_mod_power)

    current = min_n
    prefix: list[int] = []
    a, b, d = 1, 0, 1
    for k in range(1, checked_steps + 1):
        bit = current & 1
        prefix.append(bit)
        a, b, d = _append_affine_step(a, b, d, bit)
        current = collatz_step(current)
        if d > a and a * min_n + b < d * min_n:
            return {
                "status": "CERTIFIED_DESCENT",
                "q_residue": q_residue,
                "q_depth": q_depth,
                "n_residue": n_residue,
                "n_modulus": n_modulus,
                "k": k,
                "affine_A": a,
                "affine_B": b,
                "affine_D": d,
                "standard_affine_signature_id": _affine_signature_id(a, b, d),
                "parity_word": _bits_to_string(prefix),
                "min_n": min_n,
            }

    return {
        "status": "UNKNOWN",
        "q_residue": q_residue,
        "q_depth": q_depth,
        "n_residue": n_residue,
        "n_modulus": n_modulus,
        "checked_steps": checked_steps,
        "min_n": min_n,
        "reason": "no stable affine descent proof found at this q-depth and step cap",
    }


def cube_residues_at_depth(cube: dict[str, Any], q_depth: int) -> Iterable[int]:
    cube_depth = int(cube["depth"])
    if cube_depth > q_depth:
        raise ValueError(f"cube depth {cube_depth} exceeds requested q-depth {q_depth}")
    high_free = q_depth - cube_depth
    for base_q in q_cube_completion_residues(cube):
        for high in range(1 << high_free):
            yield base_q | (high << cube_depth)


def mark_existing_cube_coverage(candidate: dict[str, Any], q_depth: int) -> tuple[bytearray, int]:
    statuses = bytearray(1 << q_depth)
    covered = 0
    for state in candidate.get("states", []):
        cube = state["cube"]
        for q_residue in cube_residues_at_depth(cube, q_depth):
            if statuses[q_residue] == 0:
                statuses[q_residue] = STATUS_COVERED_BY_EXISTING_CUBE
                covered += 1
    return statuses, covered


def _top_counts(counter: Counter[Any], limit: int = 20) -> list[dict[str, Any]]:
    return [
        {"value": value, "count": count}
        for value, count in sorted(counter.items(), key=lambda item: (-item[1], str(item[0])))[:limit]
    ]


def _inside_parent_image_classes(candidate: dict[str, Any], burst_length: int) -> list[dict[str, Any]]:
    states = candidate.get("states", [])
    rows: list[dict[str, Any]] = []
    for state in states:
        if not {"affine_A", "affine_B", "affine_D"}.issubset(state):
            continue
        cube = state["cube"]
        n_mod_power = int(cube["depth"]) + burst_length
        n_modulus = 1 << n_mod_power
        for q_residue in q_cube_completion_residues(cube):
            n_residue = cube_n_residue_for_q(q_residue, burst_length, n_modulus)
            image_residue, image_mod_power = affine_image_residue(
                n_residue,
                n_mod_power=n_mod_power,
                affine_a=int(state["affine_A"]),
                affine_b=int(state["affine_B"]),
                affine_d=int(state["affine_D"]),
            )
            target_type, _ = classify_image(image_residue, image_mod_power, states, burst_length)
            if target_type != "INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH":
                continue
            q_image_depth = image_mod_power - burst_length
            raw_q_image_residue = (image_residue + 1) >> burst_length
            q_image_residue = normalize_residue(raw_q_image_residue, q_image_depth)
            rows.append(
                {
                    "from_state": state["state_id"],
                    "source_q_residue": q_residue,
                    "image_residue": image_residue,
                    "image_mod_power": image_mod_power,
                    "q_image_depth": q_image_depth,
                    "q_image_residue": q_image_residue,
                    "raw_q_image_residue": raw_q_image_residue,
                }
            )
    return rows


def summarize_inside_parent_images(
    candidate: dict[str, Any],
    statuses: bytearray,
    q_depth: int,
    burst_length: int,
    limit: int = 32,
) -> dict[str, Any]:
    image_rows = _inside_parent_image_classes(candidate, burst_length)
    grouped: dict[tuple[int, int], dict[str, Any]] = {}
    for row in image_rows:
        key = (int(row["q_image_depth"]), int(row["q_image_residue"]))
        payload = grouped.setdefault(
            key,
            {
                "q_image_depth": key[0],
                "q_image_residue": key[1],
                "multiplicity": 0,
                "source_states": Counter(),
                "refinement_status_counts": Counter(),
            },
        )
        payload["multiplicity"] += 1
        payload["source_states"][row["from_state"]] += 1

    for (image_depth, image_residue), payload in grouped.items():
        if image_depth > q_depth:
            continue
        image_residue = normalize_residue(image_residue, image_depth)
        for high in range(1 << (q_depth - image_depth)):
            q_residue = image_residue | (high << image_depth)
            payload["refinement_status_counts"][int(statuses[q_residue])] += 1

    status_names = {
        STATUS_COVERED_BY_EXISTING_CUBE: "COVERED_BY_EXISTING_CUBE",
        STATUS_CERTIFIED_RESIDUAL_DESCENT: "CERTIFIED_RESIDUAL_DESCENT",
        STATUS_UNKNOWN_RESIDUAL: "UNKNOWN_RESIDUAL",
        0: "UNCLASSIFIED",
    }
    classes = []
    for payload in grouped.values():
        counts = {
            status_names.get(status, str(status)): count
            for status, count in sorted(payload["refinement_status_counts"].items())
        }
        classes.append(
            {
                "q_image_depth": payload["q_image_depth"],
                "q_image_residue": payload["q_image_residue"],
                "multiplicity": payload["multiplicity"],
                "source_states": dict(sorted(payload["source_states"].items())),
                "refinement_status_counts": counts,
            }
        )
    classes.sort(key=lambda row: (-row["multiplicity"], row["q_image_depth"], row["q_image_residue"]))
    return {
        "inside_parent_image_count": len(image_rows),
        "unique_inside_parent_image_classes": len(classes),
        "by_q_image_depth": _top_counts(Counter(row["q_image_depth"] for row in image_rows), limit=12),
        "all_classes": classes,
        "top_classes": classes[:limit],
    }


def build_residual_frontier(
    candidate: dict[str, Any],
    q_depth: int = 20,
    burst_length: int = 6,
    max_steps: int = 120,
    show_progress: bool = True,
) -> dict[str, Any]:
    """Subtract current cubes and classify the remaining q-frontier."""

    statuses, existing_covered = mark_existing_cube_coverage(candidate, q_depth)
    total = 1 << q_depth
    certified_count = 0
    unknown_count = 0
    k_counts: Counter[int] = Counter()
    affine_counts: Counter[str] = Counter()
    unknown_mod_64: Counter[int] = Counter()
    unknown_mod_1024: Counter[int] = Counter()
    unknown_examples: list[int] = []
    certified_examples: list[dict[str, Any]] = []

    iterator = range(total)
    if show_progress:
        iterator = tqdm(iterator, desc=f"residual q-frontier 2^{q_depth}")  # type: ignore[assignment]

    for q_residue in iterator:
        if statuses[q_residue] == STATUS_COVERED_BY_EXISTING_CUBE:
            continue
        result = classify_q_residue(
            q_residue,
            q_depth=q_depth,
            burst_length=burst_length,
            max_steps=max_steps,
        )
        if result["status"] == "CERTIFIED_DESCENT":
            statuses[q_residue] = STATUS_CERTIFIED_RESIDUAL_DESCENT
            certified_count += 1
            k_counts[int(result["k"])] += 1
            affine_counts[str(result["standard_affine_signature_id"])] += 1
            if len(certified_examples) < 32:
                certified_examples.append(result)
        else:
            statuses[q_residue] = STATUS_UNKNOWN_RESIDUAL
            unknown_count += 1
            unknown_mod_64[q_residue % 64] += 1
            unknown_mod_1024[q_residue % 1024] += 1
            if len(unknown_examples) < 128:
                unknown_examples.append(q_residue)

    total_certified = existing_covered + certified_count
    inside_images = summarize_inside_parent_images(candidate, statuses, q_depth, burst_length)
    return {
        "q_depth": q_depth,
        "burst_length": burst_length,
        "max_steps": max_steps,
        "total_q_classes": total,
        "existing_cube_covered_q_classes": existing_covered,
        "residual_q_classes": total - existing_covered,
        "residual_certified_q_classes": certified_count,
        "residual_unknown_q_classes": unknown_count,
        "total_certified_q_classes": total_certified,
        "existing_cube_coverage_within_parent_percent": existing_covered / total * 100.0,
        "residual_certified_within_parent_percent": certified_count / total * 100.0,
        "total_certified_within_parent_percent": total_certified / total * 100.0,
        "unknown_within_parent_percent": unknown_count / total * 100.0,
        "total_certified_density_all_positive_integers": total_certified / (1 << (q_depth + burst_length)),
        "total_certified_density_percent_all_positive_integers": total_certified / (1 << (q_depth + burst_length)) * 100.0,
        "residual_certified_k_counts": _top_counts(k_counts, limit=32),
        "residual_certified_affine_counts": _top_counts(affine_counts, limit=24),
        "unknown_q_mod_64": _top_counts(unknown_mod_64, limit=32),
        "unknown_q_mod_1024": _top_counts(unknown_mod_1024, limit=32),
        "unknown_examples": unknown_examples,
        "certified_examples": certified_examples,
        "inside_parent_images": inside_images,
    }


def write_markdown_residual_report(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Residual 63 mod 64 q-Frontier",
        "",
        f"- q-depth: `{report['q_depth']}`",
        f"- total q classes: `{report['total_q_classes']}`",
        f"- existing cube covered q classes: `{report['existing_cube_covered_q_classes']}`",
        f"- residual certified q classes: `{report['residual_certified_q_classes']}`",
        f"- residual unknown q classes: `{report['residual_unknown_q_classes']}`",
        f"- total certified within parent: `{report['total_certified_within_parent_percent']}`%",
        f"- unknown within parent: `{report['unknown_within_parent_percent']}`%",
        "",
        "## Residual Descent Lengths",
        "",
        f"`{report['residual_certified_k_counts']}`",
        "",
        "## Unknown Concentration",
        "",
        f"- q mod 64: `{report['unknown_q_mod_64']}`",
        f"- q mod 1024: `{report['unknown_q_mod_1024'][:16]}`",
        "",
        "## Inside-Parent Images",
        "",
        f"- image count: `{report['inside_parent_images']['inside_parent_image_count']}`",
        f"- unique classes: `{report['inside_parent_images']['unique_inside_parent_image_classes']}`",
        f"- by q-image depth: `{report['inside_parent_images']['by_q_image_depth']}`",
        f"- top classes: `{report['inside_parent_images']['top_classes'][:12]}`",
        "",
        "## Interpretation",
        "",
        (
            "This report subtracts the current verified escape cubes and classifies "
            "the remaining finite q-frontier at the requested depth. Unknown rows "
            "are not counterexamples; they need a deeper q-depth, longer blocks, or "
            "a different symbolic family."
        ),
        "",
    ]
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze the residual q-frontier after verified cube subtraction.")
    parser.add_argument("--theorem-candidate", required=True)
    parser.add_argument("--q-depth", type=int, default=20)
    parser.add_argument("--burst-length", type=int, default=6)
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", default=None)
    parser.add_argument("--no-progress", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    candidate = json.loads(Path(args.theorem_candidate).read_text(encoding="utf-8"))
    report = build_residual_frontier(
        candidate,
        q_depth=args.q_depth,
        burst_length=args.burst_length,
        max_steps=args.max_steps,
        show_progress=not args.no_progress,
    )
    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        write_markdown_residual_report(report, args.out_md)
    Console().print(
        {
            key: report[key]
            for key in [
                "q_depth",
                "total_q_classes",
                "existing_cube_covered_q_classes",
                "residual_certified_q_classes",
                "residual_unknown_q_classes",
                "total_certified_within_parent_percent",
                "unknown_within_parent_percent",
            ]
        }
    )


if __name__ == "__main__":
    main()
