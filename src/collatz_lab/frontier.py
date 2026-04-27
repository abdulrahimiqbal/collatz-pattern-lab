"""Build exact finite-modulus frontiers for Collatz descent search."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from rich.console import Console
from tqdm import tqdm

from .collatz import collatz_step
from .signature import bits_to_string, min_in_residue_class
from .verifier import affine_for_parity_prefix

FrontierStatus = Literal[
    "CERTIFIED_DESCENT",
    "CERTIFIED_EVENTUAL_DESCENT_TO_SMALLER_RESIDUE",
    "UNKNOWN",
    "COUNTEREXAMPLE_TO_CANDIDATE_RULE",
]


@dataclass(frozen=True)
class ResidueClassification:
    mod_power: int
    modulus: int
    residue: int
    status: FrontierStatus
    checked_steps: int
    max_steps: int
    descent_k: int | None = None
    transition_k: int | None = None
    image_residue: int | None = None
    min_n: int | None = None
    affine_A: int | None = None
    affine_B: int | None = None
    affine_D: int | None = None
    parity_word: str | None = None
    reason: str = ""
    child_count: int | None = None
    unknown_child_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mod_power": self.mod_power,
            "modulus": self.modulus,
            "residue": self.residue,
            "status": self.status,
            "checked_steps": self.checked_steps,
            "max_steps": self.max_steps,
            "descent_k": self.descent_k,
            "transition_k": self.transition_k,
            "image_residue": self.image_residue,
            "min_n": self.min_n,
            "affine_A": self.affine_A,
            "affine_B": self.affine_B,
            "affine_D": self.affine_D,
            "parity_word": self.parity_word,
            "reason": self.reason,
            "child_count": self.child_count,
            "unknown_child_count": self.unknown_child_count,
        }


def _append_affine_step(a: int, b: int, d: int, bit: int) -> tuple[int, int, int]:
    if bit == 0:
        return a, b, d * 2
    if bit == 1:
        return 3 * a, 3 * b + d, d
    raise ValueError("Parity prefixes contain only 0/1 values")


def _image_residue(modulus: int, residue: int, prefix: list[int]) -> int:
    a, b, d = affine_for_parity_prefix(prefix)
    value = a * (residue % modulus) + b
    if value % d != 0:
        raise ValueError("Affine image is not integral; prefix is not stable for this residue")
    return (value // d) % modulus


def classify_residue(
    mod_power: int,
    residue: int,
    max_steps: int,
    min_value: int = 2,
    include_eventual_residue: bool = True,
) -> ResidueClassification:
    """Classify one residue class modulo ``2**mod_power``.

    The direct descent part is a proof only up to ``min(max_steps, mod_power)``
    standard steps, because a parity prefix of length ``t`` is stable modulo
    ``2**t``. Use ``lift_power`` in ``classify_frontier`` to aggregate exact
    child classes when you want a deeper finite search.
    """

    if mod_power < 0:
        raise ValueError("mod_power must be non-negative")
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")
    modulus = 1 << mod_power
    residue %= modulus
    checked_steps = min(max_steps, mod_power)
    min_n = min_in_residue_class(modulus, residue, min_value=min_value)

    current = min_n
    prefix: list[int] = []
    a, b, d = 1, 0, 1
    for k in range(1, checked_steps + 1):
        bit = current & 1
        prefix.append(bit)
        a, b, d = _append_affine_step(a, b, d, bit)
        current = collatz_step(current)
        if d > a and a * min_n + b < d * min_n:
            return ResidueClassification(
                mod_power=mod_power,
                modulus=modulus,
                residue=residue,
                status="CERTIFIED_DESCENT",
                checked_steps=checked_steps,
                max_steps=max_steps,
                descent_k=k,
                min_n=min_n,
                affine_A=a,
                affine_B=b,
                affine_D=d,
                parity_word=bits_to_string(prefix),
                reason="stable affine inequality proves descent for the whole residue class",
            )

    if include_eventual_residue and checked_steps > 0:
        image = _image_residue(modulus, residue, prefix)
        image_min = min_in_residue_class(modulus, image, min_value=min_value)
        if image_min < min_n:
            return ResidueClassification(
                mod_power=mod_power,
                modulus=modulus,
                residue=residue,
                status="CERTIFIED_EVENTUAL_DESCENT_TO_SMALLER_RESIDUE",
                checked_steps=checked_steps,
                max_steps=max_steps,
                transition_k=checked_steps,
                image_residue=image,
                min_n=min_n,
                affine_A=a,
                affine_B=b,
                affine_D=d,
                parity_word=bits_to_string(prefix),
                reason="stable transition reaches a residue class with a smaller least representative",
            )

    reason = "no stable affine descent found within the checked prefix"
    if max_steps > checked_steps:
        reason += "; increase --lift-power to certify deeper steps exactly"
    return ResidueClassification(
        mod_power=mod_power,
        modulus=modulus,
        residue=residue,
        status="UNKNOWN",
        checked_steps=checked_steps,
        max_steps=max_steps,
        min_n=min_n,
        parity_word=bits_to_string(prefix),
        reason=reason,
    )


def _aggregate_children(
    child_rows: list[dict[str, Any]],
    parent_power: int,
    max_steps: int,
) -> list[dict[str, Any]]:
    parent_modulus = 1 << parent_power
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in child_rows:
        groups[int(row["residue"]) % parent_modulus].append(row)

    rows: list[dict[str, Any]] = []
    for parent_residue in range(parent_modulus):
        group = groups.get(parent_residue, [])
        unknown_count = sum(1 for row in group if row["status"] == "UNKNOWN")
        status: FrontierStatus
        direct_count = sum(1 for row in group if row["status"] == "CERTIFIED_DESCENT")
        if group and direct_count == len(group):
            status = "CERTIFIED_DESCENT"
            reason = "all lifted child residue classes have certified descent"
        elif group and unknown_count == 0:
            status = "CERTIFIED_EVENTUAL_DESCENT_TO_SMALLER_RESIDUE"
            reason = "all lifted child residue classes are certified by descent or residue descent"
        else:
            status = "UNKNOWN"
            reason = "at least one lifted child residue class remains unknown"
        descent_ks = [row.get("descent_k") for row in group if row.get("descent_k") is not None]
        rows.append(
            ResidueClassification(
                mod_power=parent_power,
                modulus=parent_modulus,
                residue=parent_residue,
                status=status,
                checked_steps=max(row.get("checked_steps", 0) for row in group) if group else 0,
                max_steps=max_steps,
                descent_k=max(descent_ks) if descent_ks else None,
                min_n=min_in_residue_class(parent_modulus, parent_residue, min_value=2),
                reason=reason,
                child_count=len(group),
                unknown_child_count=unknown_count,
            ).to_dict()
        )
    return rows


def classify_frontier(
    mod_power: int,
    max_steps: int,
    lift_power: int | None = None,
    min_value: int = 2,
    include_eventual_residue: bool = True,
    show_progress: bool = True,
) -> list[dict[str, Any]]:
    """Classify all residues modulo ``2**mod_power``.

    If ``lift_power`` is larger than ``mod_power``, the function classifies
    child residue classes modulo ``2**lift_power`` and aggregates them back to
    the requested frontier modulus.
    """

    class_power = mod_power if lift_power is None else lift_power
    if class_power < mod_power:
        raise ValueError("lift_power must be at least mod_power")
    total = 1 << class_power
    iterator = range(total)
    if show_progress:
        iterator = tqdm(iterator, desc=f"classify mod 2^{class_power}")  # type: ignore[assignment]
    child_rows = [
        classify_residue(
            class_power,
            residue,
            max_steps=max_steps,
            min_value=min_value,
            include_eventual_residue=include_eventual_residue,
        ).to_dict()
        for residue in iterator
    ]
    if class_power == mod_power:
        return child_rows
    return _aggregate_children(child_rows, parent_power=mod_power, max_steps=max_steps)


def summarize_frontier(rows: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(row["status"] for row in rows)
    unresolved = [row for row in rows if row["status"] == "UNKNOWN"]
    certified = [row for row in rows if row["status"] != "UNKNOWN"]
    return {
        "rows": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "coverage": len(certified) / max(len(rows), 1),
        "unresolved_count": len(unresolved),
        "unresolved_residues": [row["residue"] for row in unresolved[:64]],
        "descent_k_counts": dict(Counter(row.get("descent_k") for row in certified if row.get("descent_k"))),
        "checked_steps": sorted({row.get("checked_steps") for row in rows}),
    }


def write_outputs(
    rows: list[dict[str, Any]],
    out: str | Path,
    summary_out: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        import pandas as pd

        pd.DataFrame(rows).to_parquet(path)
    elif path.suffix == ".jsonl":
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True))
                f.write("\n")
    else:
        path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = summarize_frontier(rows)
    if summary_out:
        summary_path = Path(summary_out)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exhaustively classify a finite Collatz residue frontier.")
    parser.add_argument("--mod-power", type=int, required=True)
    parser.add_argument("--max-steps", type=int, required=True)
    parser.add_argument("--lift-power", type=int, default=None)
    parser.add_argument("--min-value", type=int, default=2)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary-out", default=None)
    parser.add_argument("--no-eventual-residue", action="store_true")
    parser.add_argument("--no-progress", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    rows = classify_frontier(
        mod_power=args.mod_power,
        max_steps=args.max_steps,
        lift_power=args.lift_power,
        min_value=args.min_value,
        include_eventual_residue=not args.no_eventual_residue,
        show_progress=not args.no_progress,
    )
    summary = write_outputs(rows, args.out, summary_out=args.summary_out)
    Console().print(summary)


if __name__ == "__main__":
    main()
