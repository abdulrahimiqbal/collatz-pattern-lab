"""Compress verified Collatz certificates into symbolic families."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console

from .compress import TrieNode, compressed_terminals, insert_rule
from .signature import load_rule_records, log2_power, signatures_for_rules
from .verifier import verify_fixed_residue_descent_exhaustive


@dataclass(frozen=True)
class QBitCube:
    """A finite q-space bit predicate.

    Bits are indexed from the least significant q-bit. ``mask`` marks fixed
    positions and ``value`` stores their values. The cube covers all
    ``q mod 2**depth`` with ``(q & mask) == value``.
    """

    depth: int
    mask: int
    value: int
    label: tuple[Any, ...]
    label_keys: tuple[str, ...]
    support: int
    known_matches: int
    free_bits: int

    @property
    def fixed_bits(self) -> int:
        return self.mask.bit_count()

    @property
    def completions(self) -> int:
        return 1 << self.free_bits

    @property
    def density_within_q_depth(self) -> float:
        return 2.0 ** -self.fixed_bits

    @property
    def bit_pattern_lsb_first(self) -> str:
        chars = []
        for bit in range(self.depth):
            bit_mask = 1 << bit
            if self.mask & bit_mask:
                chars.append("1" if self.value & bit_mask else "0")
            else:
                chars.append("?")
        return "".join(chars)

    @property
    def fixed_bit_conditions(self) -> list[dict[str, int]]:
        return [
            {"bit": bit, "value": 1 if self.value & (1 << bit) else 0}
            for bit in range(self.depth)
            if self.mask & (1 << bit)
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "depth": self.depth,
            "mask": self.mask,
            "value": self.value,
            "label": {key: value for key, value in zip(self.label_keys, self.label, strict=True)},
            "support": self.support,
            "known_matches": self.known_matches,
            "fixed_bits": self.fixed_bits,
            "free_bits": self.free_bits,
            "completions": self.completions,
            "density_within_q_depth": self.density_within_q_depth,
            "bit_pattern_lsb_first": self.bit_pattern_lsb_first,
            "fixed_bit_conditions": self.fixed_bit_conditions,
        }


def _top_counts(values: Iterable[Any], limit: int = 20) -> list[dict[str, Any]]:
    counts = Counter(values)
    return [
        {"value": value, "count": count}
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))[:limit]
    ]


def _trie_compression(rows: list[dict[str, Any]], residue_key: str, modulus_key: str) -> dict[str, Any]:
    root = TrieNode()
    inserted = 0
    raw_density = 0.0
    depths: list[int] = []
    for row in rows:
        residue = row.get(residue_key)
        modulus = row.get(modulus_key)
        if residue is None or modulus is None:
            continue
        modulus = int(modulus)
        if modulus <= 0:
            continue
        depth = log2_power(modulus)
        insert_rule(root, int(residue) % modulus, depth)
        raw_density += 2.0 ** -depth
        depths.append(depth)
        inserted += 1
    terminal_depths = compressed_terminals(root) if inserted else []
    compressed_density = sum(2.0 ** -depth for depth in terminal_depths)
    return {
        "raw_leaf_count": inserted,
        "compressed_leaf_count": len(terminal_depths),
        "merged_leaf_count": inserted - len(terminal_depths),
        "raw_density": raw_density,
        "compressed_density": compressed_density,
        "depths": _top_counts(depths),
        "compressed_depths": _top_counts(terminal_depths),
    }


def _group_summary(rows: list[dict[str, Any]], keys: list[str], limit: int = 24) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(key) for key in keys)].append(row)
    summaries: list[dict[str, Any]] = []
    for values, group in groups.items():
        payload = {key: value for key, value in zip(keys, values, strict=True)}
        payload.update(
            {
                "count": len(group),
                "k_values": _top_counts([row["k"] for row in group], limit=8),
                "q_depths": _top_counts([row.get("q_mod_power") for row in group], limit=8),
                "parent_mod_1024": _top_counts([row.get("parent_residue_mod_1024") for row in group], limit=8),
            }
        )
        summaries.append(payload)
    summaries.sort(key=lambda row: (-int(row["count"]), json.dumps(row, sort_keys=True, default=str)))
    return summaries[:limit]


def _q_parent_groups(rows: list[dict[str, Any]], p_values: list[int]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    q_rows = [row for row in rows if row.get("q_residue") is not None and row.get("q_modulus") is not None]
    for p in p_values:
        groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
        modulus = 1 << p
        for row in q_rows:
            q_modulus = int(row["q_modulus"])
            if q_modulus < modulus:
                continue
            groups[int(row["q_residue"]) % modulus].append(row)
        output[f"q_mod_2^{p}"] = [
            {
                "q_residue": residue,
                "count": len(group),
                "k_values": _top_counts([row["k"] for row in group], limit=8),
                "post_burst_grammar": _top_counts(
                    [row.get("parity_run_string_after_first_6_steps", "") for row in group],
                    limit=8,
                ),
            }
            for residue, group in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))[:20]
        ]
    return output


def _parse_key_list(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return ["k", "standard_affine_signature_id"]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(part) for part in value]


def _cube_label(row: dict[str, Any], label_keys: list[str]) -> tuple[Any, ...]:
    return tuple(row.get(key) for key in label_keys)


def _matching_projected_rows(
    projected_rows: list[dict[str, Any]],
    mask: int,
    value: int,
) -> list[dict[str, Any]]:
    return [row for row in projected_rows if (int(row["_q_projected"]) & mask) == value]


def _is_pure_cube(
    projected_rows: list[dict[str, Any]],
    mask: int,
    value: int,
    label: tuple[Any, ...],
) -> tuple[bool, int, int]:
    matches = _matching_projected_rows(projected_rows, mask, value)
    support = sum(1 for row in matches if row["_label"] == label)
    conflicts = len(matches) - support
    return conflicts == 0 and support > 0, support, len(matches)


def _generalize_seed_cube(
    projected_rows: list[dict[str, Any]],
    seed_residue: int,
    label: tuple[Any, ...],
    depth: int,
    max_free_bits: int,
) -> QBitCube:
    mask = (1 << depth) - 1
    value = seed_residue & mask
    _, support, known_matches = _is_pure_cube(projected_rows, mask, value, label)

    while depth - mask.bit_count() < max_free_bits:
        best: tuple[int, int, int, int] | None = None
        for bit in range(depth):
            bit_mask = 1 << bit
            if not mask & bit_mask:
                continue
            candidate_mask = mask & ~bit_mask
            candidate_value = value & candidate_mask
            pure, candidate_support, candidate_matches = _is_pure_cube(
                projected_rows,
                candidate_mask,
                candidate_value,
                label,
            )
            if not pure:
                continue
            # Prefer larger support, then more free bits, then lower masks for determinism.
            score = (candidate_support, depth - candidate_mask.bit_count(), -candidate_mask, -bit)
            if best is None or score > best:
                best = score
                best_mask = candidate_mask
                best_value = candidate_value
                best_support = candidate_support
                best_matches = candidate_matches
        if best is None:
            break
        mask = best_mask
        value = best_value
        support = best_support
        known_matches = best_matches

    return QBitCube(
        depth=depth,
        mask=mask,
        value=value,
        label=label,
        label_keys=tuple(row_key for row_key in projected_rows[0]["_label_keys"]),
        support=support,
        known_matches=known_matches,
        free_bits=depth - mask.bit_count(),
    )


def mine_q_bit_cubes(
    rows: list[dict[str, Any]],
    label_keys: str | Iterable[str] | None = None,
    depths: list[int] | None = None,
    min_support: int = 3,
    max_free_bits: int = 8,
    limit: int = 48,
    validation_burst_length: int | None = None,
) -> list[dict[str, Any]]:
    """Mine pure-on-known q-bit predicates for repeated symbolic labels.

    These are discovery candidates, not proofs. A cube becomes exact only after
    ``validate_q_bit_cube`` expands all finite completions and verifies them.
    """

    parsed_label_keys = _parse_key_list(label_keys)
    q_rows = [
        row
        for row in rows
        if row.get("q_residue") is not None and row.get("q_mod_power") is not None
    ]
    if depths is None:
        depths = sorted({int(row["q_mod_power"]) for row in q_rows})

    cubes: dict[tuple[int, int, int, tuple[Any, ...]], QBitCube] = {}
    for depth in depths:
        if depth < 0:
            raise ValueError("cube depths must be non-negative")
        modulus_mask = (1 << depth) - 1
        projected_rows: list[dict[str, Any]] = []
        for row in q_rows:
            if int(row["q_mod_power"]) < depth:
                continue
            if validation_burst_length is not None and row.get("k") is not None:
                if depth + validation_burst_length < int(row["k"]):
                    continue
            label = _cube_label(row, parsed_label_keys)
            projected_rows.append(
                {
                    **row,
                    "_q_projected": int(row["q_residue"]) & modulus_mask,
                    "_label": label,
                    "_label_keys": tuple(parsed_label_keys),
                }
            )
        if not projected_rows:
            continue
        for row in projected_rows:
            cube = _generalize_seed_cube(
                projected_rows,
                seed_residue=int(row["_q_projected"]),
                label=row["_label"],
                depth=depth,
                max_free_bits=max_free_bits,
            )
            if cube.support < min_support:
                continue
            key = (cube.depth, cube.mask, cube.value, cube.label)
            existing = cubes.get(key)
            if existing is None or (cube.support, cube.free_bits) > (existing.support, existing.free_bits):
                cubes[key] = cube

    ordered = sorted(
        cubes.values(),
        key=lambda cube: (-cube.support, -cube.free_bits, cube.depth, cube.mask, cube.value, str(cube.label)),
    )
    return [cube.to_dict() for cube in ordered[:limit]]


def _cube_free_positions(cube: dict[str, Any]) -> list[int]:
    mask = int(cube["mask"])
    depth = int(cube["depth"])
    return [bit for bit in range(depth) if not (mask & (1 << bit))]


def _cube_completion_residues(cube: dict[str, Any]) -> Iterable[int]:
    value = int(cube["value"])
    free_positions = _cube_free_positions(cube)
    for assignment in range(1 << len(free_positions)):
        residue = value
        for index, bit in enumerate(free_positions):
            if assignment & (1 << index):
                residue |= 1 << bit
        yield residue


def validate_q_bit_cube(
    cube: dict[str, Any],
    burst_length: int = 6,
    search_limit: int = 100000,
    max_free_bits: int = 8,
) -> dict[str, Any]:
    """Verify a q-cube by expanding every finite completion to n-space."""

    free_bits = int(cube["free_bits"])
    if free_bits > max_free_bits:
        return {
            "status": "SKIPPED_TOO_MANY_COMPLETIONS",
            "reason": f"cube has {free_bits} free bits; validation cap is {max_free_bits}",
            "cube": cube,
        }

    label = cube.get("label", {})
    k = label.get("k")
    if k is None:
        return {
            "status": "SKIPPED_MISSING_K",
            "reason": "cube label does not include k",
            "cube": cube,
        }
    k = int(k)
    depth = int(cube["depth"])
    n_mod_power = depth + burst_length
    if n_mod_power < k:
        return {
            "status": "UNKNOWN_NEEDS_LARGER_MODULUS",
            "reason": f"q depth {depth} plus burst {burst_length} is too shallow for k={k}",
            "cube": cube,
        }

    n_modulus = 1 << n_mod_power
    burst_scale = 1 << burst_length
    verified = 0
    for q_residue in _cube_completion_residues(cube):
        n_residue = (burst_scale * q_residue - 1) % n_modulus
        result = verify_fixed_residue_descent_exhaustive(
            modulus=n_modulus,
            residue=n_residue,
            k=k,
            t_limit=search_limit,
        )
        if result.status != "PASS":
            return {
                "status": result.status,
                "reason": result.reason,
                "q_residue": q_residue,
                "n_residue": n_residue,
                "n_modulus": n_modulus,
                "k": k,
                "verified_children": verified,
                "cube": cube,
                "counterexample": result.counterexample,
            }
        verified += 1

    return {
        "status": "PASS",
        "reason": "all q-cube completions verify as exact standard-map descent certificates",
        "k": k,
        "q_modulus": 1 << depth,
        "n_modulus": n_modulus,
        "verified_children": verified,
        "cube": cube,
    }


def validate_q_bit_cubes(
    cubes: list[dict[str, Any]],
    burst_length: int = 6,
    search_limit: int = 100000,
    max_free_bits: int = 8,
    limit: int = 24,
) -> list[dict[str, Any]]:
    return [
        validate_q_bit_cube(
            cube,
            burst_length=burst_length,
            search_limit=search_limit,
            max_free_bits=max_free_bits,
        )
        for cube in cubes[:limit]
    ]


def mine_families_from_signatures(
    rows: list[dict[str, Any]],
    focus_burst: int = 6,
    q_parent_p_values: list[int] | None = None,
    cube_label_keys: str | Iterable[str] | None = None,
    cube_depths: list[int] | None = None,
    min_cube_support: int = 3,
    max_cube_free_bits: int = 8,
    max_cubes: int = 48,
    validation_ready_cubes_only: bool = True,
    validate_cubes: bool = True,
    max_validation_free_bits: int = 8,
    validation_limit: int = 24,
    validation_search_limit: int = 100000,
) -> dict[str, Any]:
    """Summarize compression in residue, q, affine, and parity-grammar space."""

    q_parent_p_values = q_parent_p_values or [4, 6, 8, 10, 12]
    focus_rows = [row for row in rows if int(row.get("focus_burst_length", focus_burst)) == focus_burst]
    q_rows = [
        row
        for row in focus_rows
        if row.get("q_residue") is not None and row.get("q_modulus") is not None
    ]
    report: dict[str, Any] = {
        "signature_rows": len(rows),
        "focus_burst": focus_burst,
        "focus_rows": len(focus_rows),
        "q_coordinate_rows": len(q_rows),
        "initial_odd_burst_lengths": _top_counts([row.get("initial_odd_burst_length") for row in rows]),
        "parent_residue_mod_64": _top_counts([row.get("parent_residue_mod_64") for row in rows]),
        "clusters": _top_counts([row.get("cluster") for row in rows]),
        "k_values": _top_counts([row.get("k") for row in rows]),
        "standard_affine_groups": _group_summary(rows, ["standard_affine_signature_id"], limit=16),
        "shortcut_affine_groups": _group_summary(rows, ["shortcut_affine_signature_id"], limit=16),
        "post_burst_parity_grammar_groups": _group_summary(
            q_rows,
            ["parity_run_string_after_first_6_steps"],
            limit=24,
        ),
        "post_burst_exponent_groups": _group_summary(
            q_rows,
            ["odd_only_exponent_string_after_first_6_steps"],
            limit=24,
        ),
        "n_space_trie_compression": _trie_compression(rows, "n_residue", "n_modulus"),
        "q_space_trie_compression": _trie_compression(q_rows, "q_residue", "q_modulus"),
        "q_parent_groups": _q_parent_groups(q_rows, q_parent_p_values),
    }

    q_bit_cubes = mine_q_bit_cubes(
        q_rows,
        label_keys=cube_label_keys,
        depths=cube_depths,
        min_support=min_cube_support,
        max_free_bits=max_cube_free_bits,
        limit=max_cubes,
        validation_burst_length=focus_burst if validation_ready_cubes_only else None,
    )
    report["q_bit_cube_candidates"] = q_bit_cubes
    report["q_bit_cube_summary"] = {
        "candidate_count": len(q_bit_cubes),
        "label_keys": _parse_key_list(cube_label_keys),
        "min_support": min_cube_support,
        "max_free_bits": max_cube_free_bits,
        "validation_ready_only": validation_ready_cubes_only,
        "top_supports": _top_counts([cube["support"] for cube in q_bit_cubes], limit=12),
        "top_free_bits": _top_counts([cube["free_bits"] for cube in q_bit_cubes], limit=12),
    }
    if validate_cubes:
        validations = validate_q_bit_cubes(
            q_bit_cubes,
            burst_length=focus_burst,
            search_limit=validation_search_limit,
            max_free_bits=max_validation_free_bits,
            limit=validation_limit,
        )
        report["q_bit_cube_validation"] = validations
        report["q_bit_cube_validation_summary"] = _top_counts([row["status"] for row in validations], limit=12)

    if q_rows:
        report["q_residue_values"] = _top_counts([row["q_residue"] for row in q_rows], limit=24)
        report["q_mod_powers"] = _top_counts([row.get("q_mod_power") for row in q_rows], limit=16)
    return report


def write_markdown_family_report(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Symbolic Family Mining Report",
        "",
        f"- signature rows: `{report['signature_rows']}`",
        f"- focus burst: `{report['focus_burst']}` shortcut steps",
        f"- rows with q-coordinates: `{report['q_coordinate_rows']}`",
        "",
        "## Dominant Coordinates",
        "",
        f"- initial odd burst lengths: `{report['initial_odd_burst_lengths'][:10]}`",
        f"- parent residues mod 64: `{report['parent_residue_mod_64'][:10]}`",
        f"- clusters: `{report['clusters'][:10]}`",
        f"- k values: `{report['k_values'][:10]}`",
        "",
        "## Trie Compression",
        "",
        f"- n-space: `{report['n_space_trie_compression']}`",
        f"- q-space after burst: `{report['q_space_trie_compression']}`",
        "",
        "## Q-Bit Cubes",
        "",
        f"- summary: `{report.get('q_bit_cube_summary', {})}`",
        f"- top candidates: `{report.get('q_bit_cube_candidates', [])[:12]}`",
        f"- validation: `{report.get('q_bit_cube_validation_summary', [])}`",
        "",
        "## Post-Burst Grammar",
        "",
        f"- parity run groups: `{report['post_burst_parity_grammar_groups'][:12]}`",
        f"- exponent-vector groups: `{report['post_burst_exponent_groups'][:12]}`",
        "",
        "## Affine Groups",
        "",
        f"- standard map: `{report['standard_affine_groups'][:8]}`",
        f"- shortcut map: `{report['shortcut_affine_groups'][:8]}`",
        "",
        "## Interpretation",
        "",
        (
            "Good news here would be many raw leaves merging after the q-coordinate "
            "rewrite or a small number of repeated post-burst parity/exponent "
            "grammars. No merge is still useful: it says the current leaves are "
            "not yet the right symbolic family boundary."
        ),
        "",
    ]
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def mine_families(
    verification_path: str | Path,
    burst_length: int = 6,
    min_value: int = 2,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    out_table: str | Path | None = None,
    cube_label_keys: str | Iterable[str] | None = None,
    cube_depths: list[int] | None = None,
    min_cube_support: int = 3,
    max_cube_free_bits: int = 8,
    max_cubes: int = 48,
    validation_ready_cubes_only: bool = True,
    validate_cubes: bool = True,
    max_validation_free_bits: int = 8,
    validation_limit: int = 24,
    validation_search_limit: int = 100000,
) -> dict[str, Any]:
    rules = load_rule_records(verification_path, pass_only=True)
    rows = signatures_for_rules(rules, burst_length=burst_length, min_value=min_value)
    report = mine_families_from_signatures(
        rows,
        focus_burst=burst_length,
        cube_label_keys=cube_label_keys,
        cube_depths=cube_depths,
        min_cube_support=min_cube_support,
        max_cube_free_bits=max_cube_free_bits,
        max_cubes=max_cubes,
        validation_ready_cubes_only=validation_ready_cubes_only,
        validate_cubes=validate_cubes,
        max_validation_free_bits=max_validation_free_bits,
        validation_limit=validation_limit,
        validation_search_limit=validation_search_limit,
    )

    if out_table:
        import pandas as pd

        path = Path(out_table)
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_parquet(path)
    if out_json:
        path = Path(out_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if out_md:
        write_markdown_family_report(report, out_md)
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mine compressed symbolic families from verified certificates.")
    parser.add_argument("--verification", required=True, help="Verifier JSON output or candidate JSONL.")
    parser.add_argument("--burst-length", type=int, default=6)
    parser.add_argument("--min-value", type=int, default=2)
    parser.add_argument("--cube-label-keys", default="k,standard_affine_signature_id")
    parser.add_argument("--cube-depths", default=None, help="Comma-separated q-depths to mine; default uses observed depths.")
    parser.add_argument("--min-cube-support", type=int, default=3)
    parser.add_argument("--max-cube-free-bits", type=int, default=8)
    parser.add_argument("--max-cubes", type=int, default=48)
    parser.add_argument(
        "--include-validation-unready-cubes",
        action="store_true",
        help="Also mine shallow projected q-cubes that cannot yet be verified at their k.",
    )
    parser.add_argument("--skip-cube-validation", action="store_true")
    parser.add_argument("--max-validation-free-bits", type=int, default=8)
    parser.add_argument("--validation-limit", type=int, default=24)
    parser.add_argument("--validation-search-limit", type=int, default=100000)
    parser.add_argument("--out-json", default=None)
    parser.add_argument("--out-md", default=None)
    parser.add_argument("--out-table", default=None, help="Optional parquet table of per-certificate signatures.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    cube_depths = None
    if args.cube_depths:
        cube_depths = [int(part.strip()) for part in args.cube_depths.split(",") if part.strip()]
    report = mine_families(
        args.verification,
        burst_length=args.burst_length,
        min_value=args.min_value,
        cube_label_keys=args.cube_label_keys,
        cube_depths=cube_depths,
        min_cube_support=args.min_cube_support,
        max_cube_free_bits=args.max_cube_free_bits,
        max_cubes=args.max_cubes,
        validation_ready_cubes_only=not args.include_validation_unready_cubes,
        validate_cubes=not args.skip_cube_validation,
        max_validation_free_bits=args.max_validation_free_bits,
        validation_limit=args.validation_limit,
        validation_search_limit=args.validation_search_limit,
        out_json=args.out_json,
        out_md=args.out_md,
        out_table=args.out_table,
    )
    Console().print(report)


if __name__ == "__main__":
    main()
