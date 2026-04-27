"""Compress and summarize verified lifted Collatz descent certificates."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console

from .collatz import parity_prefix
from .verifier import affine_for_parity_prefix


@dataclass
class TrieNode:
    terminal: bool = False
    children: dict[int, "TrieNode"] = field(default_factory=dict)


def _is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def _log2_power(value: int) -> int:
    if not _is_power_of_two(value):
        raise ValueError(f"Expected a power of two, got {value}")
    return value.bit_length() - 1


def _bits_lsb_first(residue: int, depth: int) -> list[int]:
    return [(residue >> bit) & 1 for bit in range(depth)]


def insert_rule(root: TrieNode, residue: int, depth: int) -> None:
    node = root
    for bit in _bits_lsb_first(residue, depth):
        if node.terminal:
            return
        node = node.children.setdefault(bit, TrieNode())
    node.terminal = True
    node.children.clear()


def compressed_terminals(root: TrieNode) -> list[int]:
    """Return depths of the exact union's compressed trie leaves."""

    def walk(node: TrieNode, depth: int) -> tuple[bool, list[int]]:
        if node.terminal:
            return True, [depth]
        left_full, left_terms = walk(node.children[0], depth + 1) if 0 in node.children else (False, [])
        right_full, right_terms = walk(node.children[1], depth + 1) if 1 in node.children else (False, [])
        if left_full and right_full:
            return True, [depth]
        return False, left_terms + right_terms

    _, terminals = walk(root, 0)
    return terminals


def union_density(rules: list[dict[str, Any]]) -> float:
    root = TrieNode()
    for rule in rules:
        modulus = int(rule["modulus"])
        depth = _log2_power(modulus)
        insert_rule(root, int(rule["residue"]) % modulus, depth)
    return sum(2.0 ** -depth for depth in compressed_terminals(root))


def load_verified_pass_rules(verification_path: str | Path) -> list[dict[str, Any]]:
    rows = json.loads(Path(verification_path).read_text(encoding="utf-8"))
    return [row["rule"] for row in rows if row.get("exact", {}).get("status") == "PASS"]


def _top_counts(values: list[int], limit: int = 12) -> list[dict[str, int]]:
    counts: dict[int, int] = {}
    for value in values:
        counts[int(value)] = counts.get(int(value), 0) + 1
    return [
        {"value": int(value), "count": int(count)}
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _bit_biases(rules: list[dict[str, Any]], start_bit: int = 0, end_bit: int = 34) -> list[dict[str, Any]]:
    biases: list[dict[str, Any]] = []
    for bit in range(start_bit, end_bit):
        available = [
            (int(rule["residue"]) >> bit) & 1
            for rule in rules
            if _log2_power(int(rule["modulus"])) > bit
        ]
        if not available:
            continue
        ones = sum(available)
        zeros = len(available) - ones
        majority = 1 if ones >= zeros else 0
        biases.append(
            {
                "bit": bit,
                "available": len(available),
                "majority": majority,
                "majority_fraction": max(ones, zeros) / len(available),
                "ones": ones,
                "zeros": zeros,
            }
        )
    return biases


def _affine_summaries(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for rule in rules:
        k = int(rule["suggested_k"])
        sample_n = int(rule.get("sample_n", rule["residue"]))
        prefix = parity_prefix(sample_n, k)
        a, b, d = affine_for_parity_prefix(prefix)
        odd_steps = sum(prefix)
        summaries.append(
            {
                "suggested_k": k,
                "odd_steps": odd_steps,
                "contraction_log2_margin": float(k - odd_steps * math.log2(3)),
                "a": a,
                "b": b,
                "d": d,
            }
        )
    return summaries


def compression_report(
    verification_path: str | Path,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    parent_p_values: list[int] | None = None,
) -> dict[str, Any]:
    rules = load_verified_pass_rules(verification_path)
    parent_p_values = parent_p_values or [6, 8, 10, 12, 16]
    root = TrieNode()
    for rule in rules:
        modulus = int(rule["modulus"])
        insert_rule(root, int(rule["residue"]) % modulus, _log2_power(modulus))
    terminal_depths = compressed_terminals(root)
    exact_density = sum(2.0 ** -depth for depth in terminal_depths)
    parent_groups: dict[str, Any] = {}
    for p in parent_p_values:
        groups: dict[int, list[dict[str, Any]]] = {}
        for rule in rules:
            if _log2_power(int(rule["modulus"])) < p:
                continue
            parent = int(rule["residue"]) % (1 << p)
            groups.setdefault(parent, []).append(rule)
        parent_groups[f"mod_2^{p}"] = [
            {
                "residue": residue,
                "count": len(group),
                "union_density_all_integers": union_density(group),
                "coverage_within_parent": union_density(group) / (2.0 ** -p),
                "k_values": _top_counts([int(rule["suggested_k"]) for rule in group], limit=8),
            }
            for residue, group in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))[:20]
        ]

    affine = _affine_summaries(rules)
    report: dict[str, Any] = {
        "pass_rules": len(rules),
        "raw_leaf_count": len(rules),
        "compressed_leaf_count": len(terminal_depths),
        "merged_leaf_count": len(rules) - len(terminal_depths),
        "union_density_all_integers": exact_density,
        "union_density_percent": exact_density * 100.0,
        "equivalent_full_mod_2_34_residues": exact_density * (2**34),
        "k_values": _top_counts([int(rule["suggested_k"]) for rule in rules]),
        "parent_residue_mod_64": _top_counts([int(rule.get("parent_residue_mod_64", int(rule["residue"]) % 64)) for rule in rules]),
        "parent_residue_mod_1024": _top_counts([int(rule.get("parent_residue_mod_1024", int(rule["residue"]) % 1024)) for rule in rules]),
        "clusters": _top_counts([int(rule.get("cluster", -1)) for rule in rules]),
        "bit_biases": _bit_biases(rules, start_bit=0, end_bit=max([int(rule["suggested_k"]) for rule in rules], default=0)),
        "strong_bit_biases": [
            row for row in _bit_biases(rules, start_bit=0, end_bit=max([int(rule["suggested_k"]) for rule in rules], default=0))
            if row["majority_fraction"] >= 0.95
        ],
        "odd_step_counts": _top_counts([row["odd_steps"] for row in affine]),
        "contraction_log2_margin": {
            "min": min((row["contraction_log2_margin"] for row in affine), default=None),
            "max": max((row["contraction_log2_margin"] for row in affine), default=None),
            "mean": sum(row["contraction_log2_margin"] for row in affine) / max(len(affine), 1),
        },
        "parent_groups": parent_groups,
    }

    if out_json:
        path = Path(out_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if out_md:
        write_markdown_compression_report(report, out_md)
    return report


def write_markdown_compression_report(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Lifted Certificate Compression Report",
        "",
        f"- verified PASS rules: `{report['pass_rules']}`",
        f"- compressed leaves: `{report['compressed_leaf_count']}`",
        f"- merged leaves: `{report['merged_leaf_count']}`",
        f"- union density over all positive integers: `{report['union_density_all_integers']}`",
        f"- equivalent residues modulo `2^34`: `{report['equivalent_full_mod_2_34_residues']}`",
        "",
        "## Dominant Parent Classes",
        "",
        f"- mod 64: `{report['parent_residue_mod_64'][:8]}`",
        f"- mod 1024: `{report['parent_residue_mod_1024'][:8]}`",
        "",
        "## Descent Lengths",
        "",
        f"- k values: `{report['k_values']}`",
        f"- odd step counts: `{report['odd_step_counts']}`",
        f"- contraction margin log2: `{report['contraction_log2_margin']}`",
        "",
        "## Strong Fixed Bit Biases",
        "",
        "Bits are indexed from the least significant bit.",
        "",
        f"`{report['strong_bit_biases'][:32]}`",
        "",
        "## Interpretation",
        "",
        (
            "These certificates are exact local descent proofs, but they still cover "
            "a tiny 2-adic density. Compression is considered successful only when "
            "many lifted leaves merge into shorter residue families or when a compact "
            "symbolic rule explains a large parent class."
        ),
        "",
    ]
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compress verified lifted Collatz certificates.")
    parser.add_argument("--verification", required=True)
    parser.add_argument("--out-json", default=None)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = compression_report(args.verification, out_json=args.out_json, out_md=args.out_md)
    Console().print(report)


if __name__ == "__main__":
    main()
