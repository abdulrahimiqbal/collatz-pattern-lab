"""Verifier-guided search for compact lifted Collatz families.

Run 1 found exact lifted leaves.  This module asks a harder question: can a
leaf be widened into a lower-modulus mask family while still retaining an exact
proof after enumerating all parity-stable completions?
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from .collatz import parity_prefix
from .compress import _log2_power, union_density
from .verifier import affine_for_parity_prefix


@dataclass(frozen=True)
class ResidueProof:
    status: str
    residue: int
    k: int
    odd_steps: int | None = None
    affine_A: int | None = None
    affine_B: int | None = None
    affine_D: int | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "residue": self.residue,
            "k": self.k,
            "odd_steps": self.odd_steps,
            "affine_A": self.affine_A,
            "affine_B": self.affine_B,
            "affine_D": self.affine_D,
            "reason": self.reason,
        }


def load_verified_rules(verification_path: str | Path) -> list[dict[str, Any]]:
    rows = json.loads(Path(verification_path).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"Expected verifier rows in {verification_path}")
    rules: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int]] = set()
    for row in rows:
        if row.get("exact", {}).get("status") != "PASS":
            continue
        rule = dict(row["rule"])
        modulus = int(row.get("exact", {}).get("modulus", rule["modulus"]))
        residue = int(row.get("exact", {}).get("residue", rule["residue"])) % modulus
        k = int(row.get("exact", {}).get("k", rule.get("suggested_k")))
        key = (modulus, residue, k)
        if key in seen:
            continue
        seen.add(key)
        rule["modulus"] = modulus
        rule["residue"] = residue
        rule["suggested_k"] = k
        rules.append(rule)
    return rules


def verify_parity_residue(residue: int, k: int) -> ResidueProof:
    """Prove descent for one concrete residue modulo ``2^k`` by affine slope."""

    modulus = 1 << k
    residue %= modulus
    min_n = residue if residue > 0 else modulus
    prefix = parity_prefix(min_n, k)
    a, b, d = affine_for_parity_prefix(prefix)
    odd_steps = sum(prefix)
    if d > a and a * min_n + b < d * min_n:
        return ResidueProof(
            status="PASS",
            residue=residue,
            k=k,
            odd_steps=odd_steps,
            affine_A=a,
            affine_B=b,
            affine_D=d,
            reason="symbolic affine inequality proves descent at step k",
        )
    return ResidueProof(
        status="UNKNOWN_NEEDS_SYMBOLIC_CHECK",
        residue=residue,
        k=k,
        odd_steps=odd_steps,
        affine_A=a,
        affine_B=b,
        affine_D=d,
        reason="affine inequality did not prove descent at step k",
    )


def _completion_residues(prefix: int, mask_depth: int, proof_depth: int) -> list[int]:
    if mask_depth > proof_depth:
        raise ValueError("mask_depth cannot exceed proof_depth")
    free_bits = proof_depth - mask_depth
    return [prefix + (tail << mask_depth) for tail in range(1 << free_bits)]


def verify_mask_family(
    prefix: int,
    mask_depth: int,
    proof_depth: int,
    max_expansions: int = 4096,
    cache: dict[tuple[int, int], ResidueProof] | None = None,
    early_stop_on_failure: bool = True,
) -> dict[str, Any]:
    """Verify ``n == prefix mod 2^mask_depth`` by checking all mod ``2^k`` completions."""

    if mask_depth <= 0 or proof_depth <= 0:
        raise ValueError("mask_depth and proof_depth must be positive")
    if mask_depth > proof_depth:
        raise ValueError("mask_depth cannot exceed proof_depth")
    prefix %= 1 << mask_depth
    expansion_count = 1 << (proof_depth - mask_depth)
    if expansion_count > max_expansions:
        return {
            "status": "SKIPPED_TOO_MANY_COMPLETIONS",
            "prefix": prefix,
            "mask_depth": mask_depth,
            "proof_depth": proof_depth,
            "completion_count": expansion_count,
        }
    proof_cache = cache if cache is not None else {}
    status_counts: Counter[str] = Counter()
    odd_step_counts: Counter[int] = Counter()
    first_bad: dict[str, Any] | None = None
    checked_completion_count = 0
    for residue in _completion_residues(prefix, mask_depth, proof_depth):
        checked_completion_count += 1
        key = (proof_depth, residue)
        proof = proof_cache.get(key)
        if proof is None:
            proof = verify_parity_residue(residue, proof_depth)
            proof_cache[key] = proof
        status_counts[proof.status] += 1
        if proof.odd_steps is not None:
            odd_step_counts[int(proof.odd_steps)] += 1
        if proof.status != "PASS" and first_bad is None:
            first_bad = proof.to_dict()
            if early_stop_on_failure:
                break
    status = "PASS" if status_counts and set(status_counts) == {"PASS"} else "UNKNOWN_NEEDS_SYMBOLIC_CHECK"
    return {
        "status": status,
        "prefix": prefix,
        "modulus": 1 << mask_depth,
        "mask_depth": mask_depth,
        "proof_depth": proof_depth,
        "free_bits": proof_depth - mask_depth,
        "completion_count": expansion_count,
        "checked_completion_count": checked_completion_count,
        "status_counts": dict(status_counts),
        "odd_step_counts": [
            {"value": value, "count": count}
            for value, count in sorted(odd_step_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "first_bad_completion": first_bad,
        "claim": (
            f"for all n == {prefix} mod 2^{mask_depth}, "
            f"C^{proof_depth}(n) < n"
        ),
    }


def _top_counts(values: list[int], limit: int = 12) -> list[dict[str, int]]:
    counts = Counter(int(value) for value in values)
    return [
        {"value": int(value), "count": int(count)}
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _rules_as_leaf_ids(rules: list[dict[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    return {
        (int(rule["suggested_k"]), int(rule["residue"]) % int(rule["modulus"])): rule
        for rule in rules
    }


def _candidate_source_leaf_ids(
    rules: list[dict[str, Any]],
    prefix: int,
    mask_depth: int,
    proof_depth: int,
) -> list[tuple[int, int]]:
    modulus = 1 << mask_depth
    return [
        (proof_depth, int(rule["residue"]) % (1 << proof_depth))
        for rule in rules
        if int(rule["suggested_k"]) == proof_depth
        and int(rule["residue"]) % modulus == prefix % modulus
    ]


def _family_to_rule(family: dict[str, Any]) -> dict[str, Any]:
    return {
        "modulus": int(family["modulus"]),
        "residue": int(family["prefix"]),
        "suggested_k": int(family["proof_depth"]),
    }


def search_mask_families(
    verification_path: str | Path,
    max_free_bits: int = 10,
    max_expansions: int = 4096,
    max_candidates: int | None = None,
    selection_mode: str = "leaf_cover",
    max_selected_families: int | None = None,
    early_stop_on_failure: bool = True,
) -> dict[str, Any]:
    """Search exact lower-modulus families seeded by verified lifted leaves."""

    rules = load_verified_rules(verification_path)
    leaf_ids = _rules_as_leaf_ids(rules)
    candidate_keys: set[tuple[int, int, int]] = set()
    for rule in rules:
        proof_depth = int(rule["suggested_k"])
        residue = int(rule["residue"]) % (1 << proof_depth)
        for free_bits in range(1, max_free_bits + 1):
            if free_bits > proof_depth:
                break
            if (1 << free_bits) > max_expansions:
                break
            mask_depth = proof_depth - free_bits
            prefix = residue % (1 << mask_depth)
            candidate_keys.add((proof_depth, mask_depth, prefix))

    if selection_mode == "density":
        ordered_keys = sorted(
            candidate_keys,
            key=lambda item: (item[1], -(item[0] - item[1]), item[2], item[0]),
        )
    else:
        ordered_keys = sorted(
            candidate_keys,
            key=lambda item: (-(item[0] - item[1]), item[1], item[2], item[0]),
        )
    if max_candidates is not None:
        ordered_keys = ordered_keys[:max_candidates]

    proof_cache: dict[tuple[int, int], ResidueProof] = {}
    candidates: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    for proof_depth, mask_depth, prefix in ordered_keys:
        result = verify_mask_family(
            prefix=prefix,
            mask_depth=mask_depth,
            proof_depth=proof_depth,
            max_expansions=max_expansions,
            cache=proof_cache,
            early_stop_on_failure=early_stop_on_failure,
        )
        source_leaf_ids = _candidate_source_leaf_ids(rules, prefix, mask_depth, proof_depth)
        result["source_leaf_count"] = len(source_leaf_ids)
        result["source_leaf_ids"] = [f"k{k}:r{residue}" for k, residue in source_leaf_ids]
        result["density_all_integers"] = 2.0 ** -int(result["mask_depth"])
        result["density_percent"] = result["density_all_integers"] * 100.0
        status_counts[str(result["status"])] += 1
        candidates.append(result)

    passing = [row for row in candidates if row["status"] == "PASS"]
    passing.sort(key=_family_priority)

    if selection_mode == "leaf_cover":
        selected = _select_leaf_cover(passing, leaf_ids)
    elif selection_mode == "density":
        selected = _select_density_greedy(passing, max_selected_families=max_selected_families)
    else:
        raise ValueError("selection_mode must be 'leaf_cover' or 'density'")

    selected_rules = [_family_to_rule(row) for row in selected]
    selected_density = union_density(selected_rules) if selected_rules else 0.0
    raw_leaf_count = len(rules)
    compressed_leaf_count = len(selected)
    generalized = [row for row in selected if int(row.get("free_bits", 0)) > 0]
    report = {
        "status": "VERIFIER_GUIDED_FAMILY_SEARCH",
        "global_proof_closure": False,
        "verification_path": str(verification_path),
        "input_verified_leaf_count": raw_leaf_count,
        "raw_leaf_count": raw_leaf_count,
        "candidate_count": len(candidates),
        "candidate_status_counts": dict(status_counts),
        "candidate_pass_count": len(passing),
        "selected_family_count": compressed_leaf_count,
        "compressed_leaf_count": compressed_leaf_count,
        "merged_leaf_count": max(0, raw_leaf_count - compressed_leaf_count),
        "selected_generalized_family_count": len(generalized),
        "selected_union_density_all_integers": selected_density,
        "selected_union_density_percent": selected_density * 100.0,
        "selected_equivalent_full_mod_2_34_residues": selected_density * (2**34),
        "max_free_bits": max_free_bits,
        "max_expansions": max_expansions,
        "selection_mode": selection_mode,
        "max_selected_families": max_selected_families,
        "early_stop_on_failure": early_stop_on_failure,
        "k_values": _top_counts([int(rule["suggested_k"]) for rule in rules]),
        "selected_free_bits": _top_counts([int(row.get("free_bits", 0)) for row in selected]),
        "top_selected_families": selected[:50],
        "top_passing_candidates": passing[:50],
        "training_rows": [
            {
                "label": 1 if row["status"] == "PASS" else 0,
                "reward": _candidate_reward(row),
                "proof_depth": int(row["proof_depth"]),
                "mask_depth": int(row["mask_depth"]),
                "free_bits": int(row["free_bits"]),
                "completion_count": int(row["completion_count"]),
                "source_leaf_count": int(row.get("source_leaf_count", 0)),
                "density_all_integers": float(row.get("density_all_integers", 0.0)),
                "status": row["status"],
            }
            for row in candidates
        ],
        "interpretation": (
            "Accepted mask families are exact local descent certificates. They improve "
            "coverage/compression of lifted leaves, but they do not close a global "
            "Collatz proof obligation unless mapped into verified universal coverage."
        ),
    }
    return report


def _family_priority(row: dict[str, Any]) -> tuple[float, int, int, int, int]:
    return (
        -float(row["density_all_integers"]),
        -int(row["free_bits"]),
        -int(row["source_leaf_count"]),
        int(row["mask_depth"]),
        int(row["prefix"]),
    )


def _parse_source_ids(row: dict[str, Any]) -> set[tuple[int, int]]:
    return {
        (int(part.split(":r", 1)[0][1:]), int(part.split(":r", 1)[1]))
        for part in row.get("source_leaf_ids", [])
    }


def _singleton_family(proof_depth: int, residue: int) -> dict[str, Any]:
    return {
        "status": "PASS",
        "prefix": residue,
        "modulus": 1 << proof_depth,
        "mask_depth": proof_depth,
        "proof_depth": proof_depth,
        "free_bits": 0,
        "completion_count": 1,
        "source_leaf_count": 1,
        "new_source_leaf_count": 1,
        "density_all_integers": 2.0 ** -proof_depth,
        "density_percent": 100.0 * (2.0 ** -proof_depth),
        "claim": f"singleton lifted leaf n == {residue} mod 2^{proof_depth}",
    }


def _select_leaf_cover(
    passing: list[dict[str, Any]],
    leaf_ids: dict[tuple[int, int], dict[str, Any]],
) -> list[dict[str, Any]]:
    leaf_priority = sorted(
        passing,
        key=lambda row: (
            -int(row["source_leaf_count"]),
            -int(row["free_bits"]),
            -float(row["density_all_integers"]),
            int(row["mask_depth"]),
            int(row["prefix"]),
        ),
    )
    uncovered = set(leaf_ids)
    selected: list[dict[str, Any]] = []
    for candidate in leaf_priority:
        newly_covered = _parse_source_ids(candidate) & uncovered
        if not newly_covered:
            continue
        selected.append({**candidate, "new_source_leaf_count": len(newly_covered)})
        uncovered -= newly_covered
        if not uncovered:
            break
    for proof_depth, residue in sorted(uncovered):
        selected.append(_singleton_family(proof_depth, residue))
    return selected


def _select_density_greedy(
    passing: list[dict[str, Any]],
    max_selected_families: int | None = None,
) -> list[dict[str, Any]]:
    """Greedily select exact families by marginal union-density gain."""

    selected: list[dict[str, Any]] = []
    selected_rules: list[dict[str, Any]] = []
    current_density = 0.0
    for candidate in passing:
        rule = _family_to_rule(candidate)
        new_density = union_density(selected_rules + [rule])
        marginal_gain = new_density - current_density
        if marginal_gain <= 0.0:
            continue
        selected.append({**candidate, "marginal_density_gain": marginal_gain})
        selected_rules.append(rule)
        current_density = new_density
        if max_selected_families is not None and len(selected) >= max_selected_families:
            break
    return selected


def _candidate_reward(row: dict[str, Any]) -> float:
    if row.get("status") != "PASS":
        return -1.0
    free_bits = int(row.get("free_bits", 0))
    source_leaf_count = int(row.get("source_leaf_count", 0))
    completion_count = int(row.get("completion_count", 1))
    return float(1.0 + free_bits + math.log2(max(completion_count, 1)) + source_leaf_count)


def write_family_search_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Verifier-Guided Family Search",
        "",
        f"- status: `{report['status']}`",
        f"- input verified leaves: `{report['input_verified_leaf_count']}`",
        f"- candidates tested: `{report['candidate_count']}`",
        f"- candidate status counts: `{report['candidate_status_counts']}`",
        f"- passing candidates: `{report['candidate_pass_count']}`",
        f"- selected families: `{report['selected_family_count']}`",
        f"- selected generalized families: `{report['selected_generalized_family_count']}`",
        f"- merged leaves: `{report['merged_leaf_count']}`",
        f"- selected union density percent: `{report['selected_union_density_percent']}`",
        "",
        "## Top Selected Families",
        "",
    ]
    for family in report["top_selected_families"][:25]:
        lines.append(
            f"- `{family['claim']}`; free bits `{family.get('free_bits', 0)}`, "
            f"source leaves `{family.get('source_leaf_count', 0)}`, completions `{family.get('completion_count', 1)}`"
        )
    lines.extend(["", "## Interpretation", "", report["interpretation"], ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_training_jsonl(report: dict[str, Any], out: str | Path) -> None:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in report.get("training_rows", []):
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run verifier-guided search for compact lifted families.")
    parser.add_argument("--verification", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", default=None)
    parser.add_argument("--training-jsonl", default=None)
    parser.add_argument("--max-free-bits", type=int, default=10)
    parser.add_argument("--max-expansions", type=int, default=4096)
    parser.add_argument("--max-candidates", type=int, default=None)
    parser.add_argument("--selection-mode", choices=["leaf_cover", "density"], default="leaf_cover")
    parser.add_argument("--max-selected-families", type=int, default=None)
    parser.add_argument("--early-stop-on-failure", action=argparse.BooleanOptionalAction, default=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = search_mask_families(
        args.verification,
        max_free_bits=args.max_free_bits,
        max_expansions=args.max_expansions,
        max_candidates=args.max_candidates,
        selection_mode=args.selection_mode,
        max_selected_families=args.max_selected_families,
        early_stop_on_failure=args.early_stop_on_failure,
    )
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        write_family_search_markdown(report, args.out_md)
    if args.training_jsonl:
        write_training_jsonl(report, args.training_jsonl)
    Console().print(
        {
            "out": str(out_json),
            "candidate_count": report["candidate_count"],
            "candidate_pass_count": report["candidate_pass_count"],
            "selected_family_count": report["selected_family_count"],
            "merged_leaf_count": report["merged_leaf_count"],
            "selected_union_density_percent": report["selected_union_density_percent"],
        }
    )


if __name__ == "__main__":
    main()
