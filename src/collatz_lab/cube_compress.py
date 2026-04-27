"""Compress fixed-depth q-residue sets into disjoint bit cubes."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from .frontier_strata import classify_all_q, load_candidate
from .residual_frontier import (
    STATUS_CERTIFIED_RESIDUAL_DESCENT,
    STATUS_COVERED_BY_EXISTING_CUBE,
    STATUS_UNKNOWN_RESIDUAL,
)


@dataclass(frozen=True)
class Cube:
    bits: str
    depth: int
    bit_order: str = "lsb"

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["count_covered"] = cube_count(self)
        row["condition_human"] = cube_to_condition(self)
        return row


class _TrieNode:
    __slots__ = ("children",)

    def __init__(self) -> None:
        self.children: list[_TrieNode | None] = [None, None]


def _bit_at(x: int, bit_index: int, depth: int, bit_order: str) -> int:
    if bit_order == "lsb":
        return (x >> bit_index) & 1
    if bit_order == "msb":
        return (x >> (depth - 1 - bit_index)) & 1
    raise ValueError("bit_order must be 'lsb' or 'msb'")


def residues_to_cubes(residues: set[int], depth: int, bit_order: str = "lsb") -> list[Cube]:
    """Return disjoint cubes covering exactly ``residues`` at depth ``depth``."""

    if depth < 0:
        raise ValueError("depth must be non-negative")
    if bit_order not in {"lsb", "msb"}:
        raise ValueError("bit_order must be 'lsb' or 'msb'")
    modulus = 1 << depth
    if not residues:
        return []
    root = _TrieNode()
    for residue in residues:
        if residue < 0 or residue >= modulus:
            raise ValueError(f"residue {residue} outside depth {depth}")
        node = root
        for bit_index in range(depth):
            bit = _bit_at(residue, bit_index, depth, bit_order)
            child = node.children[bit]
            if child is None:
                child = _TrieNode()
                node.children[bit] = child
            node = child

    def emit(node: _TrieNode | None, bit_index: int, prefix: list[str]) -> tuple[bool, list[Cube]]:
        if node is None:
            return False, []
        if bit_index == depth:
            return True, [Cube("".join(prefix), depth=depth, bit_order=bit_order)]
        child_rows: list[Cube] = []
        full_children: list[bool] = []
        for bit in (0, 1):
            prefix.append(str(bit))
            full, rows = emit(node.children[bit], bit_index + 1, prefix)
            prefix.pop()
            full_children.append(full)
            child_rows.extend(rows)
        if full_children == [True, True]:
            return True, [Cube("".join(prefix) + "*" * (depth - bit_index), depth=depth, bit_order=bit_order)]
        return False, child_rows

    _, cubes = emit(root, 0, [])
    cubes.sort(key=lambda cube: (-cube_count(cube), cube.bits))
    return cubes


def cube_count(cube: Cube) -> int:
    return 1 << cube.bits.count("*")


def cube_contains(cube: Cube, x: int) -> bool:
    if x < 0 or x >= (1 << cube.depth):
        return False
    for index, char in enumerate(cube.bits):
        if char == "*":
            continue
        if _bit_at(x, index, cube.depth, cube.bit_order) != int(char):
            return False
    return True


def cube_to_condition(cube: Cube) -> str:
    fixed = [(index, char) for index, char in enumerate(cube.bits) if char != "*"]
    if not fixed:
        return f"all q modulo 2^{cube.depth}"
    if cube.bit_order == "lsb":
        contiguous = [index for index, _ in fixed] == list(range(len(fixed)))
        if contiguous:
            residue = sum(int(char) << index for index, char in fixed)
            return f"q == {residue} mod 2^{len(fixed)}"
        return " and ".join(f"bit {index} == {char}" for index, char in fixed)
    return " and ".join(f"msb-index {index} == {char}" for index, char in fixed)


def expand_cubes(cubes: list[Cube]) -> set[int]:
    if not cubes:
        return set()
    depth = cubes[0].depth
    return {x for x in range(1 << depth) if any(cube_contains(cube, x) for cube in cubes)}


def _selected_sets(
    q_depth: int,
    statuses: bytearray,
    certified_results: dict[int, dict[str, Any]],
    names: list[str],
) -> dict[str, set[int]]:
    selected: dict[str, set[int]] = {}
    for name in names:
        if name == "residual_certified":
            selected[name] = {q for q, status in enumerate(statuses) if status == STATUS_CERTIFIED_RESIDUAL_DESCENT}
        elif name == "unknown":
            selected[name] = {q for q, status in enumerate(statuses) if status == STATUS_UNKNOWN_RESIDUAL}
        elif name == "already_cube_covered":
            selected[name] = {q for q, status in enumerate(statuses) if status == STATUS_COVERED_BY_EXISTING_CUBE}
        elif name.startswith("k") and name[1:].isdigit():
            k = int(name[1:])
            selected[name] = {q for q, row in certified_results.items() if int(row["k"]) == k}
        else:
            raise ValueError(f"unknown set name: {name}")
    return selected


def build_cube_compression_report(
    q_depth: int,
    set_names: list[str],
    candidate: dict[str, Any] | None = None,
    burst_length: int = 6,
    max_steps: int = 120,
    bit_order: str = "lsb",
    show_progress: bool = False,
) -> dict[str, Any]:
    statuses, certified_results = classify_all_q(
        q_depth,
        burst_length=burst_length,
        max_steps=max_steps,
        candidate=candidate,
        show_progress=show_progress,
    )
    selected = _selected_sets(q_depth, statuses, certified_results, set_names)
    reports: dict[str, Any] = {}
    for name, residues in selected.items():
        cubes = residues_to_cubes(residues, q_depth, bit_order=bit_order)
        reports[name] = {
            "raw_residue_count": len(residues),
            "cube_count": len(cubes),
            "compression_ratio_raw_to_cubes": None if not cubes else len(residues) / len(cubes),
            "cubes": [cube.to_dict() for cube in cubes],
            "largest_cubes": [cube.to_dict() for cube in cubes[:20]],
            "top_conditions": [cube_to_condition(cube) for cube in cubes[:20]],
        }
    return {
        "scope": "q residue sets inside n = 64*q - 1",
        "q_depth": q_depth,
        "burst_length": burst_length,
        "max_steps": max_steps,
        "bit_order": bit_order,
        "sets": reports,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compress q-residue sets into bit cubes.")
    parser.add_argument("--residual-report", default=None, help="Accepted for pipeline compatibility; statuses are recomputed.")
    parser.add_argument("--theorem-candidate", default=None)
    parser.add_argument("--q-depth", type=int, required=True)
    parser.add_argument("--sets", required=True, help="Comma-separated set names.")
    parser.add_argument("--burst-length", type=int, default=6)
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--bit-order", choices=["lsb", "msb"], default="lsb")
    parser.add_argument("--out", required=True)
    parser.add_argument("--no-progress", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    candidate = load_candidate(args.theorem_candidate)
    report = build_cube_compression_report(
        q_depth=args.q_depth,
        set_names=[name.strip() for name in args.sets.split(",") if name.strip()],
        candidate=candidate,
        burst_length=args.burst_length,
        max_steps=args.max_steps,
        bit_order=args.bit_order,
        show_progress=not args.no_progress,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print(
        {
            name: {
                "raw": row["raw_residue_count"],
                "cubes": row["cube_count"],
                "ratio": row["compression_ratio_raw_to_cubes"],
            }
            for name, row in report["sets"].items()
        }
    )


if __name__ == "__main__":
    main()
