"""Dataset generation CLI for exact Collatz labels."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any

import pandas as pd
from rich.console import Console
from tqdm.auto import tqdm

from .collatz import (
    first_descent_time,
    max_height_ratio,
    parity_prefix,
    signed_cycle_id,
    signed_parity_prefix,
    signed_syracuse_step_odd,
    signed_v2_3n_plus_1,
    syracuse_step_odd,
    total_stopping_time,
    v2,
)
from .encode import encode_int, encode_signed_int, validate_base
from .utils import parse_bool

TASKS = {"v2", "syracuse", "descent", "parity", "multitask"}
SPLITS = {"all_test", "all_train", "random", "range", "residue_holdout"}
SAMPLE_MODES = {"random", "high_v2", "hard_case", "mixed"}
SIGN_MODES = {"positive", "negative", "mixed"}


def sample_n(rng: random.Random, bits: int, require_odd: bool) -> int:
    if bits < 1:
        raise ValueError("bits must be positive")
    n = rng.randrange(1, 1 << bits)
    if require_odd:
        n |= 1
    return n


def sample_signed_n(rng: random.Random, bits: int, require_odd: bool, sign: int) -> int:
    if sign not in {-1, 1}:
        raise ValueError("sign must be -1 or 1")
    return sign * sample_n(rng, bits=bits, require_odd=require_odd)


def sample_n_with_exact_v2_3n_plus_1(rng: random.Random, bits: int, exponent: int) -> int:
    """Sample n with exact v2(3*n + 1) == exponent.

    For exponent e, exactness is the congruence
    ``3*n + 1 == 2**e (mod 2**(e + 1))``.
    """

    if bits < 1:
        raise ValueError("bits must be positive")
    if exponent < 0:
        raise ValueError("exponent must be non-negative")
    modulus = 1 << (exponent + 1)
    if modulus >= 1 << bits:
        raise ValueError("bits must be larger than exponent + 1")
    residue = (((1 << exponent) - 1) * pow(3, -1, modulus)) % modulus
    max_q = ((1 << bits) - 1 - residue) // modulus
    min_q = 1 if residue == 0 else 0
    if max_q < min_q:
        raise ValueError(f"No positive samples exist for bits={bits}, exponent={exponent}")
    return residue + modulus * rng.randint(min_q, max_q)


def assign_split(index: int, n: int, total: int, method: str, rng: random.Random) -> str:
    if method == "all_train":
        return "train"
    if method == "all_test":
        return "test"
    if method == "random":
        draw = rng.random()
        if draw < 0.8:
            return "train"
        if draw < 0.9:
            return "val"
        return "test"
    if method == "range":
        frac = index / max(total, 1)
        if frac < 0.8:
            return "train"
        if frac < 0.9:
            return "val"
        return "test"
    if method == "residue_holdout":
        residue = n % 16
        if residue == 15:
            return "test"
        if residue == 7:
            return "val"
        return "train"
    raise ValueError(f"Unknown split method: {method}")


def descent_bucket(descent: int | None) -> int:
    """Bucket first descent time into 10 classes."""

    if descent is None or descent < 0:
        return 9
    for idx, upper in enumerate([1, 2, 4, 8, 16, 32, 64, 128, 256]):
        if descent <= upper:
            return idx
    return 9


def row_for_n(
    n: int,
    task: str,
    base: int,
    bits: int,
    lsb_first: bool,
    split: str,
    parity_k: int,
    max_steps: int,
    signed: bool = False,
) -> dict[str, Any]:
    """Build one exact dataset row.

    Large integers are stored as strings. Sequence columns store model token ids
    with BOS/EOS and digit tokens offset by ``encode.DIGIT_OFFSET``.
    """

    if signed and n == 0:
        raise ValueError("signed datasets exclude zero")
    if not signed and n < 1:
        raise ValueError("unsigned datasets require positive n")

    three_n_plus_one = 3 * n + 1
    is_syracuse_task = task in {"syracuse", "multitask"}
    if is_syracuse_task:
        syracuse_next = signed_syracuse_step_odd(n) if signed else syracuse_step_odd(n)
    else:
        syracuse_next = None
    encoder = encode_signed_int if signed else encode_int
    target_digits = encoder(syracuse_next, base=base, lsb_first=lsb_first) if syracuse_next is not None else []
    is_positive = n > 0
    descent = first_descent_time(n, max_steps=max_steps) if is_positive else None
    stopping = total_stopping_time(n, max_steps=max_steps) if is_positive else None
    height = max_height_ratio(n, max_steps=max_steps) if is_positive else 0.0
    cycle_id, cycle_entry = signed_cycle_id(n, max_steps=max_steps) if signed and n < 0 else (-1, -1)
    parity = signed_parity_prefix(n, parity_k) if signed else parity_prefix(n, parity_k)
    return {
        "task": task,
        "n": str(n),
        "sign": -1 if n < 0 else 1,
        "abs_bit_length": abs(n).bit_length(),
        "base": base,
        "bits": bits,
        "lsb_first": lsb_first,
        "signed": signed,
        "input_digits": encoder(n, base=base, lsb_first=lsb_first),
        "target_digits": target_digits,
        "v2_3n_plus_1": signed_v2_3n_plus_1(n) if signed else v2(three_n_plus_one),
        "syracuse_next": str(syracuse_next) if syracuse_next is not None else "",
        "first_descent_time": descent if descent is not None else -1,
        "descent_bucket": descent_bucket(descent),
        "hard_case": 0 if is_positive else -1,
        "negative_cycle_id": cycle_id,
        "cycle_entry_time_capped": cycle_entry if signed and n < 0 else -1,
        "total_stopping_time_capped": stopping if stopping is not None else -1,
        "max_height_ratio": height,
        "parity_prefix": parity,
        "descent_label_mask": is_positive,
        "hard_case_label_mask": is_positive,
        "negative_cycle_label_mask": signed and n < 0,
        "split": split,
    }


def mark_hard_cases(rows: list[dict[str, Any]], quantile: float = 0.9, force: bool = False) -> None:
    positive = [row for row in rows if int(row.get("sign", 1)) > 0]
    if not positive:
        return
    if force:
        for row in positive:
            row["hard_case"] = 1
        return
    scores = sorted(
        (
            (
                int(row.get("first_descent_time", -1)),
                float(row.get("max_height_ratio", 0.0)),
            )
            for row in positive
        )
    )
    threshold_index = min(max(int(len(scores) * quantile), 0), len(scores) - 1)
    threshold = scores[threshold_index]
    for row in positive:
        score = (int(row.get("first_descent_time", -1)), float(row.get("max_height_ratio", 0.0)))
        row["hard_case"] = int(score >= threshold)


def generate_rows(
    task: str,
    base: int,
    bits: int,
    n_rows: int,
    lsb_first: bool = True,
    seed: int = 0,
    split_method: str = "random",
    parity_k: int = 32,
    max_steps: int = 10000,
    signed: bool = False,
    sign_mode: str = "positive",
    sample_mode: str = "random",
    positive_fraction: float = 0.5,
    v2_min: int = 8,
    v2_max: int = 16,
    hard_case_pool_multiplier: int = 8,
    show_progress: bool = True,
) -> list[dict[str, Any]]:
    if task not in TASKS:
        raise ValueError(f"task must be one of {sorted(TASKS)}")
    if split_method not in SPLITS:
        raise ValueError(f"split must be one of {sorted(SPLITS)}")
    if sign_mode not in SIGN_MODES:
        raise ValueError(f"sign_mode must be one of {sorted(SIGN_MODES)}")
    if sample_mode not in SAMPLE_MODES:
        raise ValueError(f"sample_mode must be one of {sorted(SAMPLE_MODES)}")
    if not 0.0 <= positive_fraction <= 1.0:
        raise ValueError("positive_fraction must be between 0 and 1")
    validate_base(base)
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    require_odd = task in {"syracuse", "multitask"}

    def build_row(index: int, value: int) -> dict[str, Any]:
        split = assign_split(index, value, n_rows, split_method, rng)
        return row_for_n(
            value,
            task=task,
            base=base,
            bits=bits,
            lsb_first=lsb_first,
            split=split,
            parity_k=parity_k,
            max_steps=max_steps,
            signed=signed,
        )

    def add_positive_random(count: int) -> None:
        for _ in range(count):
            rows.append(build_row(len(rows), sample_n(rng, bits=bits, require_odd=require_odd)))

    def add_positive_high_v2(count: int) -> None:
        classes = list(range(v2_min, v2_max + 1))
        for i in range(count):
            exponent = classes[i % len(classes)]
            rows.append(build_row(len(rows), sample_n_with_exact_v2_3n_plus_1(rng, bits=bits, exponent=exponent)))

    def add_positive_hard_cases(count: int) -> None:
        pool_size = max(count * hard_case_pool_multiplier, count)
        candidates = [
            build_row(len(rows) + i, sample_n(rng, bits=bits, require_odd=require_odd))
            for i in range(pool_size)
        ]
        candidates.sort(
            key=lambda row: (
                int(row.get("first_descent_time", -1)),
                float(row.get("max_height_ratio", 0.0)),
            ),
            reverse=True,
        )
        selected = candidates[:count]
        mark_hard_cases(selected, force=True)
        rows.extend(selected)

    def add_negative_random(count: int) -> None:
        for _ in range(count):
            rows.append(build_row(len(rows), sample_signed_n(rng, bits=bits, require_odd=require_odd, sign=-1)))

    if signed:
        if sign_mode == "positive":
            positive_count = n_rows
            negative_count = 0
        elif sign_mode == "negative":
            positive_count = 0
            negative_count = n_rows
        else:
            positive_count = int(round(n_rows * positive_fraction))
            negative_count = n_rows - positive_count

        iterator = range(1)
        if show_progress:
            iterator = tqdm(iterator, desc=f"generate signed {task}", unit="phase")
        for _ in iterator:
            if sample_mode == "high_v2":
                add_positive_high_v2(positive_count)
            elif sample_mode == "hard_case":
                add_positive_hard_cases(positive_count)
            elif sample_mode == "mixed":
                hard_count = int(round(positive_count * 0.1))
                high_count = int(round(positive_count * 0.2))
                random_count = positive_count - hard_count - high_count
                add_positive_random(random_count)
                add_positive_high_v2(high_count)
                add_positive_hard_cases(hard_count)
            else:
                add_positive_random(positive_count)
            add_negative_random(negative_count)
    else:
        iterator = range(n_rows)
        if show_progress:
            iterator = tqdm(iterator, desc=f"generate {task}", unit="row")
        for i in iterator:
            if sample_mode == "high_v2":
                exponent = v2_min + (i % (v2_max - v2_min + 1))
                value = sample_n_with_exact_v2_3n_plus_1(rng, bits=bits, exponent=exponent)
            else:
                value = sample_n(rng, bits=bits, require_odd=require_odd)
            rows.append(build_row(i, value))

    if sample_mode == "hard_case" and not signed:
        rows.sort(
            key=lambda row: (
                int(row.get("first_descent_time", -1)),
                float(row.get("max_height_ratio", 0.0)),
            ),
            reverse=True,
        )
        del rows[n_rows:]
        mark_hard_cases(rows, force=True)
    elif sample_mode != "hard_case":
        mark_hard_cases(rows)

    for index, row in enumerate(rows):
        row["split"] = assign_split(index, int(row["n"]), len(rows), split_method, rng)
    return rows


def generate_v2_targeted_rows(
    base: int,
    bits: int,
    n_rows: int,
    v2_min: int,
    v2_max: int,
    lsb_first: bool = True,
    seed: int = 0,
    split_method: str = "random",
    parity_k: int = 32,
    max_steps: int = 10000,
    show_progress: bool = True,
) -> list[dict[str, Any]]:
    if split_method not in SPLITS:
        raise ValueError(f"split must be one of {sorted(SPLITS)}")
    if v2_min < 0 or v2_max < v2_min:
        raise ValueError("Require 0 <= v2_min <= v2_max")
    validate_base(base)
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    classes = list(range(v2_min, v2_max + 1))
    iterator = range(n_rows)
    if show_progress:
        iterator = tqdm(iterator, desc=f"generate v2 exact {v2_min}..{v2_max}", unit="row")
    for i in iterator:
        exponent = classes[i % len(classes)]
        value = sample_n_with_exact_v2_3n_plus_1(rng, bits=bits, exponent=exponent)
        split = assign_split(i, value, n_rows, split_method, rng)
        rows.append(
            row_for_n(
                value,
                task="v2",
                base=base,
                bits=bits,
                lsb_first=lsb_first,
                split=split,
                parity_k=parity_k,
                max_steps=max_steps,
            )
        )
    return rows


def write_parquet(rows: list[dict[str, Any]], out: str | Path) -> None:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(out, index=False)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate exact Collatz dataset shards.")
    parser.add_argument("--task", choices=sorted(TASKS), required=True)
    parser.add_argument("--base", type=int, required=True)
    parser.add_argument("--bits", type=int, required=True)
    parser.add_argument("--n", type=int, required=True, dest="n_rows")
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--lsb-first", type=parse_bool, default=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--split", choices=sorted(SPLITS), default="random")
    parser.add_argument("--parity-k", type=int, default=32)
    parser.add_argument("--max-steps", type=int, default=10000)
    parser.add_argument("--signed", type=parse_bool, default=False)
    parser.add_argument("--sign-mode", choices=sorted(SIGN_MODES), default="positive")
    parser.add_argument("--sample-mode", choices=sorted(SAMPLE_MODES), default="random")
    parser.add_argument("--positive-fraction", type=float, default=0.5)
    parser.add_argument("--v2-min", type=int, default=None)
    parser.add_argument("--v2-max", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    console = Console()
    has_v2_bounds = args.v2_min is not None or args.v2_max is not None
    if has_v2_bounds and (args.v2_min is None or args.v2_max is None):
        raise ValueError("--v2-min and --v2-max must be provided together")
    if args.task == "v2" and has_v2_bounds and args.sample_mode == "random" and not args.signed:
        if args.v2_min is None or args.v2_max is None:
            raise ValueError("--v2-min and --v2-max must be provided together")
        rows = generate_v2_targeted_rows(
            base=args.base,
            bits=args.bits,
            n_rows=args.n_rows,
            v2_min=args.v2_min,
            v2_max=args.v2_max,
            lsb_first=args.lsb_first,
            seed=args.seed,
            split_method=args.split,
            parity_k=args.parity_k,
            max_steps=args.max_steps,
            signed=args.signed,
        )
    else:
        rows = generate_rows(
            task=args.task,
            base=args.base,
            bits=args.bits,
            n_rows=args.n_rows,
            lsb_first=args.lsb_first,
            seed=args.seed,
            split_method=args.split,
            parity_k=args.parity_k,
            max_steps=args.max_steps,
            signed=args.signed,
            sign_mode=args.sign_mode,
            sample_mode=args.sample_mode,
            positive_fraction=args.positive_fraction,
            v2_min=args.v2_min if args.v2_min is not None else 8,
            v2_max=args.v2_max if args.v2_max is not None else 16,
        )
    write_parquet(rows, args.out)
    console.print(f"[green]Wrote {len(rows)} rows to {args.out}[/green]")


if __name__ == "__main__":
    main()
