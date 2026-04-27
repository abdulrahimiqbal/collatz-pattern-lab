"""Adaptive refinement of hard q-families inside ``n = 64*q - 1``."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console
from tqdm import tqdm

from .frontier_strata import burst_features_for_q_residue, load_candidate
from .residual_frontier import STATUS_COVERED_BY_EXISTING_CUBE, classify_q_residue, mark_existing_cube_coverage


def _parse_optional_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
    raise ValueError("boolean filters must be true/false")


def feature_filter_matches(features: dict[str, Any], feature_filter: dict[str, Any] | None) -> bool:
    """Return whether burst features satisfy all non-None filter fields."""

    if not feature_filter:
        return True
    for key, expected in feature_filter.items():
        if expected is None:
            continue
        if features.get(key) != expected:
            return False
    return True


def build_refinement_report(
    focus_depth: int,
    focus_residue: int,
    extra_depth: int,
    candidate: dict[str, Any] | None = None,
    burst_length: int = 6,
    max_steps: int = 120,
    feature_filter: dict[str, Any] | None = None,
    show_progress: bool = False,
) -> dict[str, Any]:
    if focus_depth < 0 or extra_depth < 0:
        raise ValueError("depths must be non-negative")
    focus_residue %= 1 << focus_depth
    final_depth = focus_depth + extra_depth
    total = 1 << extra_depth
    statuses = bytearray(1 << final_depth)
    if candidate is not None:
        statuses, _ = mark_existing_cube_coverage(candidate, final_depth)

    counts: Counter[str] = Counter()
    examples: dict[str, list[int]] = {
        "certified_by_existing": [],
        "certified_by_burst": [],
        "certified_by_affine": [],
        "returns_to_parent": [],
        "unknown": [],
        "excluded_by_filter": [],
    }
    iterator = range(total)
    if show_progress:
        iterator = tqdm(iterator, desc=f"refine q={focus_residue} mod 2^{focus_depth}")  # type: ignore[assignment]
    for high in iterator:
        q_residue = focus_residue | (high << focus_depth)
        features = burst_features_for_q_residue(q_residue, final_depth)
        if not feature_filter_matches(features, feature_filter):
            bucket = "excluded_by_filter"
            counts[bucket] += 1
            if len(examples[bucket]) < 32:
                examples[bucket].append(q_residue)
            continue
        if statuses[q_residue] == STATUS_COVERED_BY_EXISTING_CUBE:
            bucket = "certified_by_existing"
        else:
            if features["burst_escape"]:
                bucket = "certified_by_burst"
            else:
                result = classify_q_residue(q_residue, final_depth, burst_length=burst_length, max_steps=max_steps)
                if result["status"] == "CERTIFIED_DESCENT":
                    bucket = "certified_by_affine"
                elif features["returns_to_parent"]:
                    bucket = "returns_to_parent"
                else:
                    bucket = "unknown"
        counts[bucket] += 1
        if len(examples[bucket]) < 32:
            examples[bucket].append(q_residue)

    unknown = counts["unknown"]
    matching = total - counts["excluded_by_filter"]
    certified_total = counts["certified_by_existing"] + counts["certified_by_burst"] + counts["certified_by_affine"]
    unresolved_after_refinement = counts["returns_to_parent"] + counts["unknown"]
    return {
        "scope": "adaptive q-family refinement inside n = 64*q - 1",
        "parent": "63mod64",
        "focus_depth": focus_depth,
        "focus_residue": focus_residue,
        "extra_depth": extra_depth,
        "final_q_depth": final_depth,
        "feature_filter": feature_filter or {},
        "total_refinements": total,
        "matching_refinements": matching,
        "excluded_by_filter": counts["excluded_by_filter"],
        "certified_by_existing": counts["certified_by_existing"],
        "certified_by_burst": counts["certified_by_burst"],
        "certified_by_affine": counts["certified_by_affine"],
        "certified_total": certified_total,
        "returns_to_parent": counts["returns_to_parent"],
        "unknown": unknown,
        "unresolved_after_refinement": unresolved_after_refinement,
        "unknown_percent": 0.0 if matching == 0 else unknown / matching * 100.0,
        "unresolved_after_refinement_percent": (
            0.0 if matching == 0 else unresolved_after_refinement / matching * 100.0
        ),
        "counts_sum": sum(counts.values()),
        "examples": examples,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adaptively refine a hard q-family.")
    parser.add_argument("--parent", default="63mod64")
    parser.add_argument("--focus-depth", type=int, required=True)
    parser.add_argument("--focus-residue", type=int, required=True)
    parser.add_argument("--extra-depth", type=int, required=True)
    parser.add_argument("--theorem-candidate", default=None)
    parser.add_argument("--burst-length", type=int, default=6)
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--require-a", type=int, default=None)
    parser.add_argument("--require-h", type=int, default=None)
    parser.add_argument("--require-post-burst-mod64", type=int, default=None)
    parser.add_argument("--require-returns-to-parent", choices=["true", "false"], default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--no-progress", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.parent != "63mod64":
        raise ValueError("only --parent 63mod64 is currently supported")
    candidate = load_candidate(args.theorem_candidate)
    feature_filter = {
        "a": args.require_a,
        "h": args.require_h,
        "post_burst_mod_64": (
            None if args.require_post_burst_mod64 is None else args.require_post_burst_mod64 % 64
        ),
        "returns_to_parent": _parse_optional_bool(args.require_returns_to_parent),
    }
    report = build_refinement_report(
        focus_depth=args.focus_depth,
        focus_residue=args.focus_residue,
        extra_depth=args.extra_depth,
        candidate=candidate,
        burst_length=args.burst_length,
        max_steps=args.max_steps,
        feature_filter=feature_filter,
        show_progress=not args.no_progress,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print(report)


if __name__ == "__main__":
    main()
