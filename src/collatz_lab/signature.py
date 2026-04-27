"""Exact symbolic signatures for Collatz descent certificates.

The verifier proves local descent rules for the standard Collatz map ``C``.
This module keeps those standard-map certificates intact, then adds derived
shortcut-map views that are useful for structure mining. In particular,
classes with ``n == -1 mod 2**a`` get explicit ``q`` coordinates via
``n = 2**a * q - 1``.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal

from .collatz import collatz_step, parity_prefix, shortcut_step, v2
from .burst import burst_division_exponent, burst_post_division_value, decompose_q, h_star
from .utils import load_jsonl
from .verifier import affine_for_parity_prefix

MapKind = Literal["standard", "shortcut"]


def _is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def log2_power(value: int) -> int:
    """Return ``p`` for ``value == 2**p``."""

    if not _is_power_of_two(value):
        raise ValueError(f"Expected a power of two, got {value}")
    return value.bit_length() - 1


def min_in_residue_class(modulus: int, residue: int, min_value: int = 1) -> int:
    """Return the smallest ``n >= min_value`` with ``n == residue mod modulus``."""

    if modulus <= 0:
        raise ValueError("modulus must be positive")
    residue %= modulus
    if min_value <= residue and residue > 0:
        return residue
    if residue == 0:
        quotient = max(1, (min_value + modulus - 1) // modulus)
    else:
        quotient = max(0, (min_value - residue + modulus - 1) // modulus)
    return residue + quotient * modulus


def bits_to_string(bits: Iterable[int]) -> str:
    return "".join("1" if int(bit) else "0" for bit in bits)


def parity_word(n: int, k: int) -> str:
    """Return the standard Collatz parity word for ``k`` steps."""

    return bits_to_string(parity_prefix(n, k))


def parity_runs(word: str) -> tuple[tuple[str, int], ...]:
    """Return run-length encoding for a string parity word."""

    runs: list[tuple[str, int]] = []
    for char in word:
        if char not in {"0", "1"}:
            raise ValueError("parity words contain only '0' and '1'")
        if runs and runs[-1][0] == char:
            runs[-1] = (char, runs[-1][1] + 1)
        else:
            runs.append((char, 1))
    return tuple(runs)


def affine_for_parity_word(word: str) -> tuple[int, int, int]:
    """Return ``(A, B, D)`` for a standard Collatz parity word."""

    a, b, d = 1, 0, 1
    for char in word:
        if char == "0":
            d *= 2
        elif char == "1":
            a = 3 * a
            b = 3 * b + d
        else:
            raise ValueError("parity words contain only '0' and '1'")
    return a, b, d


def apply_affine(a: int, b: int, d: int, n: int) -> int:
    """Apply an exact affine Collatz block to ``n``."""

    numerator = a * n + b
    if numerator % d != 0:
        raise AssertionError("affine block is not integral for this n")
    return numerator // d


def descent_slack(a: int, d: int) -> float:
    """Return ``log(D) - log(A)`` for reporting only."""

    return math.log(d) - math.log(a)


def _iterate_standard(n: int, k: int) -> int:
    current = n
    for _ in range(k):
        current = collatz_step(current)
    return current


def signature_for_n(n: int, k: int) -> dict[str, Any]:
    """Return exact standard-map signature fields for a trajectory block."""

    if n < 1:
        raise ValueError("n must be positive")
    if k < 0:
        raise ValueError("k must be non-negative")
    word = parity_word(n, k)
    a, b, d = affine_for_parity_word(word)
    threshold = None if a >= d else {"num": b, "den": d - a}
    image = apply_affine(a, b, d, n)
    actual = _iterate_standard(n, k)
    if image != actual:
        raise AssertionError("affine form disagrees with Collatz iteration")
    return {
        "n": n,
        "k": k,
        "parity_word": word,
        "parity_runs": parity_runs(word),
        "parity_run_string": ",".join(f"{bit}x{length}" for bit, length in parity_runs(word)),
        "odd_count": word.count("1"),
        "A": a,
        "B": b,
        "D": d,
        "affine_A": a,
        "affine_B": b,
        "affine_D": d,
        "image": image,
        "descent_threshold_if_A_lt_D": threshold,
        "slack_float": descent_slack(a, d),
    }


def signature_for_q(q: int, k: int) -> dict[str, Any]:
    """Return signature fields for ``n = 64*q - 1``."""

    if q <= 0:
        raise ValueError("q must be positive")
    n = 64 * q - 1
    row = signature_for_n(n, k)
    t, a, r = decompose_q(q)
    h = burst_division_exponent(a, r)
    row.update(
        {
            "q": q,
            "t": t,
            "a": a,
            "r": r,
            "h": h,
            "h_star": h_star(a),
            "burst_escape": h >= h_star(a),
            "returns_to_parent": burst_post_division_value(a, r) % 64 == 63,
        }
    )
    return row


def run_length_encode(bits: Iterable[int]) -> list[dict[str, int]]:
    """Return run-length encoding for a parity word."""

    encoded: list[dict[str, int]] = []
    for raw_bit in bits:
        bit = int(raw_bit)
        if bit not in {0, 1}:
            raise ValueError("Parity words contain only 0/1 values")
        if encoded and encoded[-1]["bit"] == bit:
            encoded[-1]["length"] += 1
        else:
            encoded.append({"bit": bit, "length": 1})
    return encoded


def runs_to_string(runs: Iterable[dict[str, int]]) -> str:
    return ",".join(f"{int(run['bit'])}x{int(run['length'])}" for run in runs)


def affine_for_shortcut_prefix(prefix: list[int]) -> tuple[int, int, int]:
    """Return ``A, B, D`` with ``T^m(n) = (A*n + B) / D``.

    ``T`` is the one-division shortcut map: even values map to ``n/2`` and
    odd values map to ``(3*n + 1)/2``. Unlike the standard map, every shortcut
    step contributes one factor of two to the denominator.
    """

    a, b, d = 1, 0, 1
    for bit in prefix:
        if bit == 0:
            d *= 2
        elif bit == 1:
            a = 3 * a
            b = 3 * b + d
            d *= 2
        else:
            raise ValueError("Parity prefixes contain only 0/1 values")
    return a, b, d


def shortcut_parity_prefix(n: int, steps: int) -> list[int]:
    if n < 1:
        raise ValueError("shortcut signatures require positive integers")
    if steps < 0:
        raise ValueError("steps must be non-negative")
    current = n
    bits: list[int] = []
    for _ in range(steps):
        bits.append(current & 1)
        current = shortcut_step(current)
    return bits


def apply_shortcut_steps(n: int, steps: int) -> int:
    if n < 1:
        raise ValueError("shortcut signatures require positive integers")
    current = n
    for _ in range(steps):
        current = shortcut_step(current)
    return current


def shortcut_prefix_for_standard_steps(n: int, standard_steps: int) -> tuple[list[int], bool, int]:
    """Compress a standard ``C`` prefix into shortcut ``T`` steps.

    Returns ``(shortcut_bits, aligned, consumed_standard_steps)``. Alignment is
    false only when the standard prefix ends immediately after an odd standard
    step, before the forced division by two that is bundled into ``T``.
    """

    if standard_steps < 0:
        raise ValueError("standard_steps must be non-negative")
    current = n
    consumed = 0
    bits: list[int] = []
    while consumed < standard_steps:
        bit = current & 1
        cost = 2 if bit else 1
        if consumed + cost > standard_steps:
            return bits, False, consumed
        bits.append(bit)
        current = shortcut_step(current)
        consumed += cost
    return bits, True, consumed


def shortcut_burst_standard_cost(n: int, shortcut_steps: int) -> tuple[int, int, bool]:
    """Apply shortcut steps and report the equivalent standard-step cost."""

    current = n
    consumed = 0
    all_odd = True
    for _ in range(shortcut_steps):
        bit = current & 1
        all_odd = all_odd and bit == 1
        consumed += 2 if bit else 1
        current = shortcut_step(current)
    return current, consumed, all_odd


def initial_odd_burst_length(n: int) -> int:
    """Return the forced initial odd-burst length for the shortcut map.

    For ``n = 2**a * q - 1`` with ``q`` odd, the first ``a`` shortcut steps are
    odd. This is exactly ``v2(n + 1)`` for positive ``n``.
    """

    if n < 1:
        raise ValueError("initial odd burst requires a positive integer")
    return v2(n + 1)


def post_burst_coordinates(
    residue: int,
    modulus: int,
    burst_length: int,
) -> tuple[int, int] | None:
    """Return ``(q_residue, q_modulus)`` for ``n = 2**a*q - 1``.

    The coordinates are defined only when the whole residue class is contained
    in ``-1 mod 2**a`` and the modulus is divisible by ``2**a``.
    """

    if burst_length < 0:
        raise ValueError("burst_length must be non-negative")
    scale = 1 << burst_length
    if modulus % scale != 0:
        return None
    residue %= modulus
    if (residue + 1) % scale != 0:
        return None
    q_modulus = modulus // scale
    q_residue = ((residue + 1) // scale) % q_modulus if q_modulus else 0
    return q_residue, q_modulus


def odd_only_exponent_vector(n: int, max_standard_steps: int) -> list[int]:
    """Return ``v2(3*x+1)`` values for odd states encountered in a prefix."""

    if n < 1:
        raise ValueError("odd-only exponent vectors require positive integers")
    if max_standard_steps < 0:
        raise ValueError("max_standard_steps must be non-negative")
    current = n
    exponents: list[int] = []
    for _ in range(max_standard_steps):
        if current & 1:
            exponents.append(v2(3 * current + 1))
        current = collatz_step(current)
    return exponents


def descent_threshold_parts(a: int, b: int, d: int) -> tuple[int, int] | None:
    """Return the exact threshold ``B / (D - A)`` as numerator/denominator."""

    if d <= a:
        return None
    return b, d - a


def descent_slack_log2(a: int, d: int) -> float:
    """Return ``log2(D) - log2(A)`` for an affine form."""

    return math.log2(d) - math.log2(a)


@dataclass(frozen=True)
class AffineSignature:
    map_kind: MapKind
    steps: int
    parity_word: str
    parity_runs: list[dict[str, int]]
    odd_steps: int
    affine_A: int
    affine_B: int
    affine_D: int
    descent_threshold_num: int | None
    descent_threshold_den: int | None
    descent_threshold: float | None
    descent_slack: float

    @classmethod
    def from_prefix(cls, map_kind: MapKind, prefix: list[int]) -> "AffineSignature":
        if map_kind == "standard":
            a, b, d = affine_for_parity_prefix(prefix)
        elif map_kind == "shortcut":
            a, b, d = affine_for_shortcut_prefix(prefix)
        else:
            raise ValueError(f"Unknown map_kind: {map_kind}")
        threshold = descent_threshold_parts(a, b, d)
        threshold_value = None if threshold is None else threshold[0] / threshold[1]
        runs = run_length_encode(prefix)
        return cls(
            map_kind=map_kind,
            steps=len(prefix),
            parity_word=bits_to_string(prefix),
            parity_runs=runs,
            odd_steps=sum(prefix),
            affine_A=a,
            affine_B=b,
            affine_D=d,
            descent_threshold_num=None if threshold is None else threshold[0],
            descent_threshold_den=None if threshold is None else threshold[1],
            descent_threshold=threshold_value,
            descent_slack=descent_slack_log2(a, d),
        )

    @property
    def parity_run_string(self) -> str:
        return runs_to_string(self.parity_runs)

    @property
    def affine_signature_id(self) -> str:
        return f"{self.map_kind}:A={self.affine_A}:B={self.affine_B}:D={self.affine_D}"

    def to_dict(self, prefix: str = "") -> dict[str, Any]:
        return {
            f"{prefix}map_kind": self.map_kind,
            f"{prefix}steps": self.steps,
            f"{prefix}parity_word": self.parity_word,
            f"{prefix}parity_runs": self.parity_runs,
            f"{prefix}parity_run_string": self.parity_run_string,
            f"{prefix}odd_steps": self.odd_steps,
            f"{prefix}affine_A": self.affine_A,
            f"{prefix}affine_B": self.affine_B,
            f"{prefix}affine_D": self.affine_D,
            f"{prefix}descent_threshold_num": self.descent_threshold_num,
            f"{prefix}descent_threshold_den": self.descent_threshold_den,
            f"{prefix}descent_threshold": self.descent_threshold,
            f"{prefix}descent_slack": self.descent_slack,
            f"{prefix}affine_signature_id": self.affine_signature_id,
        }


def signature_for_rule(
    rule: dict[str, Any],
    burst_length: int = 6,
    min_value: int = 2,
) -> dict[str, Any]:
    """Turn a verified residue certificate into exact symbolic features."""

    modulus = int(rule["modulus"])
    residue = int(rule["residue"]) % modulus
    k = int(rule.get("suggested_k") or rule.get("k") or rule.get("max_t"))
    if modulus <= 0 or k <= 0:
        raise ValueError("rules require positive modulus and k")
    representative = min_in_residue_class(modulus, residue, min_value=min_value)

    standard_prefix = parity_prefix(representative, k)
    standard = AffineSignature.from_prefix("standard", standard_prefix)

    shortcut_prefix, shortcut_aligned, consumed = shortcut_prefix_for_standard_steps(representative, k)
    shortcut = AffineSignature.from_prefix("shortcut", shortcut_prefix)

    q_coords = post_burst_coordinates(residue, modulus, burst_length)
    after_burst_word = ""
    after_burst_runs: list[dict[str, int]] = []
    after_burst_exponents: list[int] = []
    after_burst_q_residue: int | None = None
    after_burst_q_modulus: int | None = None
    burst_all_odd = False
    burst_standard_cost = 0
    if q_coords is not None:
        after_burst_q_residue, after_burst_q_modulus = q_coords
        after_burst_value, burst_standard_cost, burst_all_odd = shortcut_burst_standard_cost(
            representative,
            burst_length,
        )
        if shortcut_aligned and len(shortcut_prefix) >= burst_length:
            after_burst_bits = shortcut_prefix[burst_length:]
            after_burst_word = bits_to_string(after_burst_bits)
            after_burst_runs = run_length_encode(after_burst_bits)
        remaining_standard_steps = max(0, k - burst_standard_cost)
        after_burst_exponents = odd_only_exponent_vector(after_burst_value, remaining_standard_steps)

    row: dict[str, Any] = {
        "n_residue": residue,
        "n_modulus": modulus,
        "n_mod_power": log2_power(modulus) if _is_power_of_two(modulus) else None,
        "k": k,
        "min_n": representative,
        "sample_n": int(rule.get("sample_n", representative)),
        "source": rule.get("source"),
        "cluster": rule.get("cluster"),
        "support": rule.get("support"),
        "parent_residue_mod_64": int(rule.get("parent_residue_mod_64", residue % 64)),
        "parent_residue_mod_1024": int(rule.get("parent_residue_mod_1024", residue % 1024)),
        "initial_odd_burst_length": initial_odd_burst_length(representative),
        "focus_burst_length": burst_length,
        "burst_all_odd": burst_all_odd,
        "burst_standard_cost": burst_standard_cost,
        "q_residue": after_burst_q_residue,
        "q_modulus": after_burst_q_modulus,
        "q_mod_power": (
            log2_power(after_burst_q_modulus)
            if after_burst_q_modulus is not None and _is_power_of_two(after_burst_q_modulus)
            else None
        ),
        "parity_word_after_first_6_steps": after_burst_word,
        "parity_runs_after_first_6_steps": after_burst_runs,
        "parity_run_string_after_first_6_steps": runs_to_string(after_burst_runs),
        "odd_only_exponent_vector_after_first_6_steps": after_burst_exponents,
        "odd_only_exponent_string_after_first_6_steps": ",".join(map(str, after_burst_exponents)),
        "shortcut_aligned_with_standard_k": shortcut_aligned,
        "shortcut_standard_steps_consumed": consumed,
    }
    row.update(standard.to_dict(prefix="standard_"))
    row.update(shortcut.to_dict(prefix="shortcut_"))

    # Compatibility aliases for the table proposed in the research note.
    row["affine_A"] = standard.affine_A
    row["affine_B"] = standard.affine_B
    row["affine_D"] = standard.affine_D
    row["descent_threshold"] = standard.descent_threshold
    row["slack"] = standard.descent_slack
    row["parity_word"] = standard.parity_word
    row["parity_runs"] = standard.parity_runs
    row["odd_only_exponent_vector"] = odd_only_exponent_vector(representative, k)
    return row


def load_rule_records(path: str | Path, pass_only: bool = True) -> list[dict[str, Any]]:
    """Load rules from a candidates JSONL file or verifier JSON output."""

    path = Path(path)
    if path.suffix == ".jsonl":
        return load_jsonl(path)
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Expected a list of rules or verification rows")
    rules: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict) and "rule" in row:
            if pass_only and row.get("exact", {}).get("status") != "PASS":
                continue
            rules.append(row["rule"])
        elif isinstance(row, dict):
            rules.append(row)
        else:
            raise ValueError("Expected dictionary rows")
    return rules


def signatures_for_rules(
    rules: Iterable[dict[str, Any]],
    burst_length: int = 6,
    min_value: int = 2,
) -> list[dict[str, Any]]:
    return [signature_for_rule(rule, burst_length=burst_length, min_value=min_value) for rule in rules]


def _collect_residual_signature_rows(
    q_depth: int,
    set_name: str,
    sample_or_all: str,
    candidate: dict[str, Any] | None,
    burst_length: int = 6,
    max_steps: int = 120,
    show_progress: bool = False,
) -> list[dict[str, Any]]:
    from .frontier_strata import classify_all_q, representative_q
    from .residual_frontier import STATUS_CERTIFIED_RESIDUAL_DESCENT

    statuses, certified_results = classify_all_q(
        q_depth,
        burst_length=burst_length,
        max_steps=max_steps,
        candidate=candidate,
        show_progress=show_progress,
    )
    if set_name == "residual_certified":
        residues = sorted(q for q, status in enumerate(statuses) if status == STATUS_CERTIFIED_RESIDUAL_DESCENT)
    elif set_name.startswith("k") and set_name[1:].isdigit():
        k = int(set_name[1:])
        residues = sorted(q for q, row in certified_results.items() if int(row["k"]) == k)
    else:
        raise ValueError("signature frontier mode currently supports residual_certified and kN sets")

    if sample_or_all != "all":
        sample_count = int(sample_or_all)
        residues = residues[:sample_count]

    rows = []
    for q_residue in residues:
        result = certified_results[q_residue]
        q = representative_q(q_residue, q_depth)
        row = signature_for_q(q, int(result["k"]))
        row["q_residue"] = q_residue
        row["q_depth"] = q_depth
        row["q_zero_residue_represented_by_modulus"] = q_residue == 0
        row["certifier_status"] = result["status"]
        row["standard_affine_signature_id"] = result["standard_affine_signature_id"]
        rows.append(row)
    return rows


def summarize_signature_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def top(counter: Counter[Any], limit: int = 30) -> list[dict[str, Any]]:
        return [
            {"value": value, "count": count}
            for value, count in sorted(counter.items(), key=lambda item: (-item[1], str(item[0])))[:limit]
        ]

    return {
        "row_count": len(rows),
        "by_k": top(Counter(row["k"] for row in rows)),
        "by_a": top(Counter(row["a"] for row in rows)),
        "by_h": top(Counter(row["h"] for row in rows)),
        "by_a_h": top(Counter(f"a={row['a']},h={row['h']}" for row in rows)),
        "by_parity_runs": top(Counter(row["parity_run_string"] for row in rows)),
        "by_affine_A_D": top(Counter(f"A={row['A']},D={row['D']}" for row in rows)),
        "by_burst_escape": top(Counter(str(row["burst_escape"]) for row in rows)),
        "by_returns_to_parent": top(Counter(str(row["returns_to_parent"]) for row in rows)),
    }


def rows_for_tabular_output(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return rows with nested values serialized for Parquet/CSV-style tables."""

    flat_rows: list[dict[str, Any]] = []
    for row in rows:
        flat: dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, (dict, list, tuple)):
                flat[key] = json.dumps(value, sort_keys=True)
            else:
                flat[key] = value
        flat_rows.append(flat)
    return flat_rows


def write_signature_summary_markdown(summary: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Signature Summary",
        "",
        f"- rows: `{summary['row_count']}`",
        "",
    ]
    for key in [
        "by_k",
        "by_a",
        "by_h",
        "by_a_h",
        "by_parity_runs",
        "by_affine_A_D",
        "by_burst_escape",
        "by_returns_to_parent",
    ]:
        lines.extend([f"## {key}", "", f"`{summary[key][:20]}`", ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract exact symbolic Collatz certificate signatures.")
    parser.add_argument("--rules", default=None, help="Verifier JSON or candidate JSONL file.")
    parser.add_argument("--out-jsonl", default=None)
    parser.add_argument("--out-parquet", default=None)
    parser.add_argument("--out", default=None, help="Parquet output path for residual frontier mode.")
    parser.add_argument("--burst-length", type=int, default=6)
    parser.add_argument("--include-non-pass", action="store_true")
    parser.add_argument("--min-value", type=int, default=2)
    parser.add_argument("--residual-report", default=None, help="Accepted for pipeline compatibility; statuses are recomputed.")
    parser.add_argument("--theorem-candidate", default=None)
    parser.add_argument("--q-depth", type=int, default=None)
    parser.add_argument("--set", dest="set_name", default="residual_certified")
    parser.add_argument("--sample-or-all", default="all")
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--summary-json", default=None)
    parser.add_argument("--summary-md", default=None)
    parser.add_argument("--no-progress", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.residual_report or args.q_depth is not None:
        from .frontier_strata import load_candidate

        if args.q_depth is None:
            raise ValueError("--q-depth is required in residual frontier mode")
        candidate = load_candidate(args.theorem_candidate)
        rows = _collect_residual_signature_rows(
            q_depth=args.q_depth,
            set_name=args.set_name,
            sample_or_all=args.sample_or_all,
            candidate=candidate,
            burst_length=args.burst_length,
            max_steps=args.max_steps,
            show_progress=not args.no_progress,
        )
        parquet_out = args.out or args.out_parquet
        if parquet_out:
            import pandas as pd

            path = Path(parquet_out)
            path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows_for_tabular_output(rows)).to_parquet(path)
        elif args.out_jsonl:
            path = Path(args.out_jsonl)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row, sort_keys=True))
                    f.write("\n")
        else:
            print(json.dumps(rows[:100], indent=2, sort_keys=True))

        summary = summarize_signature_rows(rows)
        summary_json = Path(args.summary_json) if args.summary_json else (
            Path(parquet_out).with_name(f"signature_summary_{args.set_name}_q{args.q_depth}.json")
            if parquet_out
            else None
        )
        if summary_json:
            summary_json.parent.mkdir(parents=True, exist_ok=True)
            summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary_md = Path(args.summary_md) if args.summary_md else (
            summary_json.with_suffix(".md") if summary_json else None
        )
        if summary_md:
            write_signature_summary_markdown(summary, summary_md)
        return

    if args.rules is None:
        raise ValueError("Provide --rules or residual frontier arguments")
    rules = load_rule_records(args.rules, pass_only=not args.include_non_pass)
    rows = signatures_for_rules(rules, burst_length=args.burst_length, min_value=args.min_value)
    if args.out_jsonl:
        path = Path(args.out_jsonl)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True))
                f.write("\n")
    if args.out_parquet:
        import pandas as pd

        path = Path(args.out_parquet)
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_parquet(path)
    if not args.out_jsonl and not args.out_parquet:
        print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
