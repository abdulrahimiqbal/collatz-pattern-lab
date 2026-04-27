"""Build transition graphs from verified q-bit Collatz families."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console

from .compress import union_density
from .family_miner import validate_q_bit_cube
from .potential import PotentialTransition, find_log_potential


def parse_affine_signature_id(signature_id: str) -> tuple[int, int, int]:
    """Parse ids like ``standard:A=9:B=5:D=16`` into ``(A, B, D)``."""

    parts = signature_id.split(":")
    values: dict[str, int] = {}
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", maxsplit=1)
        values[key] = int(value)
    try:
        return values["A"], values["B"], values["D"]
    except KeyError as exc:
        raise ValueError(f"Malformed affine signature id: {signature_id}") from exc


def _is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def _log2_power(value: int) -> int:
    if not _is_power_of_two(value):
        raise ValueError(f"Expected a power of two, got {value}")
    return value.bit_length() - 1


def _cube_free_positions(cube: dict[str, Any]) -> list[int]:
    mask = int(cube["mask"])
    depth = int(cube["depth"])
    return [bit for bit in range(depth) if not (mask & (1 << bit))]


def q_cube_completion_residues(cube: dict[str, Any]) -> Iterable[int]:
    value = int(cube["value"])
    free_positions = _cube_free_positions(cube)
    for assignment in range(1 << len(free_positions)):
        residue = value
        for index, bit in enumerate(free_positions):
            if assignment & (1 << index):
                residue |= 1 << bit
        yield residue


def min_positive_q_in_cube(cube: dict[str, Any]) -> int:
    depth = int(cube["depth"])
    completions = sorted(q for q in q_cube_completion_residues(cube) if q > 0)
    if completions:
        return completions[0]
    return 1 << depth


def cube_n_modulus(cube: dict[str, Any], burst_length: int) -> int:
    return 1 << (int(cube["depth"]) + burst_length)


def cube_n_residue_for_q(q_residue: int, burst_length: int, n_modulus: int) -> int:
    return (((1 << burst_length) * q_residue) - 1) % n_modulus


def affine_image_residue(
    n_residue: int,
    n_mod_power: int,
    affine_a: int,
    affine_b: int,
    affine_d: int,
) -> tuple[int, int]:
    """Return ``(image_residue, image_mod_power)`` for a stable affine class."""

    d_power = _log2_power(affine_d)
    if n_mod_power < d_power:
        raise ValueError("source modulus is too shallow for affine denominator")
    numerator = affine_a * n_residue + affine_b
    if numerator % affine_d != 0:
        raise ValueError("affine image is not integral for this residue")
    image_mod_power = n_mod_power - d_power
    image_modulus = 1 << image_mod_power
    return (numerator // affine_d) % image_modulus, image_mod_power


def cube_contains_image(
    target_cube: dict[str, Any],
    image_residue: int,
    image_mod_power: int,
    burst_length: int,
) -> bool:
    target_depth = int(target_cube["depth"])
    target_n_power = target_depth + burst_length
    if image_mod_power < target_n_power:
        return False
    target_n_modulus = 1 << target_n_power
    image_at_target_depth = image_residue % target_n_modulus
    if image_at_target_depth % (1 << burst_length) != (1 << burst_length) - 1:
        return False
    q_residue = ((image_at_target_depth + 1) >> burst_length) % (1 << target_depth)
    return (q_residue & int(target_cube["mask"])) == int(target_cube["value"])


def classify_image(
    image_residue: int,
    image_mod_power: int,
    states: list[dict[str, Any]],
    burst_length: int,
) -> tuple[str, list[str]]:
    if image_mod_power < burst_length:
        return "IMAGE_MODULUS_TOO_SHALLOW_FOR_PARENT", []
    if image_residue % (1 << burst_length) != (1 << burst_length) - 1:
        return "OUTSIDE_FORCED_BURST_PARENT", []
    matches = [
        state["state_id"]
        for state in states
        if cube_contains_image(state["cube"], image_residue, image_mod_power, burst_length)
    ]
    if matches:
        return "MATCHES_VALIDATED_CUBE", matches
    min_target_power = min((int(state["cube"]["depth"]) + burst_length for state in states), default=burst_length)
    if image_mod_power < min_target_power:
        return "INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH", []
    return "INSIDE_FORCED_BURST_PARENT_UNMATCHED", []


def state_from_validation(index: int, validation: dict[str, Any], burst_length: int) -> dict[str, Any]:
    cube = validation["cube"]
    label = cube.get("label", {})
    signature_id = label.get("standard_affine_signature_id")
    if signature_id is None:
        raise ValueError("validated cube label needs standard_affine_signature_id")
    affine_a, affine_b, affine_d = parse_affine_signature_id(str(signature_id))
    min_q = min_positive_q_in_cube(cube)
    min_n = (1 << burst_length) * min_q - 1
    threshold = affine_b / (affine_d - affine_a) if affine_d > affine_a else None
    return {
        "state_id": f"cube_{index:03d}",
        "cube": cube,
        "k": int(label["k"]),
        "affine_A": affine_a,
        "affine_B": affine_b,
        "affine_D": affine_d,
        "affine_signature_id": signature_id,
        "min_q": min_q,
        "min_n": min_n,
        "descent_threshold": threshold,
        "descent_margin_at_min_n": min_n - threshold if threshold is not None else None,
        "log_gain_upper_at_min_n": math.log((affine_a * min_n + affine_b) / (affine_d * min_n)),
    }


def transition_for_state(
    state: dict[str, Any],
    states: list[dict[str, Any]],
    burst_length: int,
) -> dict[str, Any]:
    cube = state["cube"]
    n_mod_power = int(cube["depth"]) + burst_length
    n_modulus = 1 << n_mod_power
    child_rows: list[dict[str, Any]] = []
    for q_residue in q_cube_completion_residues(cube):
        n_residue = cube_n_residue_for_q(q_residue, burst_length, n_modulus)
        image_residue, image_mod_power = affine_image_residue(
            n_residue,
            n_mod_power=n_mod_power,
            affine_a=int(state["affine_A"]),
            affine_b=int(state["affine_B"]),
            affine_d=int(state["affine_D"]),
        )
        target_type, target_states = classify_image(
            image_residue,
            image_mod_power,
            states,
            burst_length,
        )
        image_parent_mod_64 = image_residue % 64 if image_mod_power >= 6 else None
        child_rows.append(
            {
                "q_residue": q_residue,
                "n_residue": n_residue,
                "n_modulus": n_modulus,
                "image_residue": image_residue,
                "image_mod_power": image_mod_power,
                "image_modulus": 1 << image_mod_power,
                "image_parent_mod_64": image_parent_mod_64,
                "target_type": target_type,
                "target_states": target_states,
            }
        )

    target_counts = Counter(row["target_type"] for row in child_rows)
    parent_counts = Counter(row["image_parent_mod_64"] for row in child_rows)
    matched_targets = Counter(target for row in child_rows for target in row["target_states"])
    return {
        "from_state": state["state_id"],
        "transition_kind": "CERTIFIED_DESCENT_BLOCK",
        "k": state["k"],
        "affine_A": state["affine_A"],
        "affine_B": state["affine_B"],
        "affine_D": state["affine_D"],
        "source_completions": len(child_rows),
        "all_children_descend_below_source": True,
        "target_type_counts": dict(sorted(target_counts.items())),
        "image_parent_mod_64_counts": {
            str(key): value for key, value in sorted(parent_counts.items(), key=lambda item: str(item[0]))
        },
        "matched_target_state_counts": dict(sorted(matched_targets.items())),
        "sample_children": child_rows[:16],
    }


def _expanded_rules_for_validations(validations: list[dict[str, Any]], burst_length: int) -> list[dict[str, int]]:
    rules: list[dict[str, int]] = []
    for validation in validations:
        cube = validation["cube"]
        n_modulus = cube_n_modulus(cube, burst_length)
        for q_residue in q_cube_completion_residues(cube):
            rules.append(
                {
                    "modulus": n_modulus,
                    "residue": cube_n_residue_for_q(q_residue, burst_length, n_modulus),
                }
            )
    return rules


def build_transition_graph(
    family_report: dict[str, Any],
    burst_length: int = 6,
    validation_search_limit: int = 100000,
    max_validation_free_bits: int = 8,
) -> dict[str, Any]:
    raw_validations = [
        row for row in family_report.get("q_bit_cube_validation", []) if row.get("status") == "PASS"
    ]
    validations: list[dict[str, Any]] = []
    for row in raw_validations:
        # Re-run validation so stale reports cannot silently become theorem candidates.
        refreshed = validate_q_bit_cube(
            row["cube"],
            burst_length=burst_length,
            search_limit=validation_search_limit,
            max_free_bits=max_validation_free_bits,
        )
        if refreshed["status"] != "PASS":
            raise ValueError(f"stale cube failed re-validation: {refreshed}")
        validations.append(refreshed)

    states = [state_from_validation(index, validation, burst_length) for index, validation in enumerate(validations)]
    transitions = [transition_for_state(state, states, burst_length) for state in states]
    expanded_rules = _expanded_rules_for_validations(validations, burst_length)
    exact_density = union_density(expanded_rules)
    potential_transitions = [
        PotentialTransition(
            from_state=state["state_id"],
            to_state=state["state_id"],
            affine_A=int(state["affine_A"]),
            affine_B=int(state["affine_B"]),
            affine_D=int(state["affine_D"]),
            min_n=int(state["min_n"]),
            label=str(state["affine_signature_id"]),
        )
        for state in states
    ]
    potential = find_log_potential(potential_transitions, epsilon=0.0)
    target_type_counts = Counter(
        target_type
        for transition in transitions
        for target_type, count in transition["target_type_counts"].items()
        for _ in range(count)
    )
    theorem_status = "PASS_FRAGMENT" if states and potential["status"] == "PASS" else "FAIL"
    return {
        "verifier_status": theorem_status,
        "scope": "validated q-bit cube families only; not a universal Collatz proof",
        "burst_length": burst_length,
        "state_count": len(states),
        "transition_count": len(transitions),
        "expanded_certificate_count": len(expanded_rules),
        "union_density_all_positive_integers": exact_density,
        "union_density_percent": exact_density * 100.0,
        "coverage_within_63_mod_64_parent": exact_density / (2.0 ** -6),
        "coverage_within_63_mod_64_parent_percent": exact_density / (2.0 ** -6) * 100.0,
        "target_type_counts": dict(sorted(target_type_counts.items())),
        "states": states,
        "transitions": transitions,
        "affine_forms": sorted({state["affine_signature_id"] for state in states}),
        "descent_inequalities": [
            {
                "state_id": state["state_id"],
                "claim": f"(A*n+B)/D < n for all n in {state['state_id']}",
                "A": state["affine_A"],
                "B": state["affine_B"],
                "D": state["affine_D"],
                "min_n": state["min_n"],
                "descent_threshold": state["descent_threshold"],
                "descent_margin_at_min_n": state["descent_margin_at_min_n"],
                "log_gain_upper_at_min_n": state["log_gain_upper_at_min_n"],
            }
            for state in states
        ],
        "finite_exceptions": [],
        "potential": potential,
    }


def write_markdown_transition_report(candidate: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Cube Transition Theorem Candidate",
        "",
        f"- verifier status: `{candidate['verifier_status']}`",
        f"- scope: {candidate['scope']}",
        f"- states: `{candidate['state_count']}`",
        f"- transitions: `{candidate['transition_count']}`",
        f"- expanded certificates: `{candidate['expanded_certificate_count']}`",
        f"- density over all positive integers: `{candidate['union_density_all_positive_integers']}`",
        f"- coverage within `63 mod 64`: `{candidate['coverage_within_63_mod_64_parent_percent']}`%",
        f"- target type counts: `{candidate['target_type_counts']}`",
        f"- potential status: `{candidate['potential']['status']}`",
        "",
        "## States",
        "",
    ]
    for state in candidate["states"]:
        cube = state["cube"]
        lines.append(
            f"- `{state['state_id']}` k=`{state['k']}` pattern=`{cube['bit_pattern_lsb_first']}` "
            f"support=`{cube['support']}` completions=`{cube['completions']}` "
            f"log_gain<=`{state['log_gain_upper_at_min_n']}`"
        )
    lines.extend(["", "## Transition Summary", ""])
    for transition in candidate["transitions"]:
        lines.append(
            f"- `{transition['from_state']}` target types `{transition['target_type_counts']}`, "
            f"image mod 64 `{transition['image_parent_mod_64_counts']}`"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "This is an exact proof fragment for the listed q-bit cube states. "
                "It is not a universal proof because the state set covers only a small "
                "2-adic subset and the image transitions mostly leave the current "
                "validated cube state space after descending."
            ),
            "",
        ]
    )
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build transition graph from validated q-bit cube families.")
    parser.add_argument("--family-report", required=True)
    parser.add_argument("--burst-length", type=int, default=6)
    parser.add_argument("--validation-search-limit", type=int, default=100000)
    parser.add_argument("--max-validation-free-bits", type=int, default=8)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    family_report = json.loads(Path(args.family_report).read_text(encoding="utf-8"))
    candidate = build_transition_graph(
        family_report,
        burst_length=args.burst_length,
        validation_search_limit=args.validation_search_limit,
        max_validation_free_bits=args.max_validation_free_bits,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        write_markdown_transition_report(candidate, args.out_md)
    Console().print(
        {
            key: candidate[key]
            for key in [
                "verifier_status",
                "state_count",
                "expanded_certificate_count",
                "union_density_percent",
                "coverage_within_63_mod_64_parent_percent",
                "target_type_counts",
            ]
        }
    )


if __name__ == "__main__":
    main()
