"""Exact and symbolic checks for candidate Collatz descent rules."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from rich.console import Console

from .collatz import collatz_step, first_descent_time, parity_prefix
from .utils import load_jsonl

VerifierStatus = Literal[
    "PASS",
    "FAIL_WITH_COUNTEREXAMPLE",
    "UNKNOWN_NEEDS_SYMBOLIC_CHECK",
    "UNKNOWN_NEEDS_LARGER_MODULUS",
]


@dataclass(frozen=True)
class VerificationResult:
    status: VerifierStatus
    modulus: int
    residue: int
    k: int
    counterexample: int | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "modulus": self.modulus,
            "residue": self.residue,
            "k": self.k,
            "counterexample": self.counterexample,
            "reason": self.reason,
        }


def _min_positive_in_residue(modulus: int, residue: int) -> int:
    residue %= modulus
    return residue if residue > 0 else modulus


def _rule_parts(rule: dict[str, Any]) -> tuple[int, int, int]:
    modulus = int(rule["modulus"])
    residue = int(rule["residue"]) % modulus
    k = int(rule.get("suggested_k") or rule.get("k") or rule.get("max_t"))
    if modulus <= 0 or k <= 0:
        raise ValueError("Rules require positive modulus and k")
    return modulus, residue, k


def check_rule_by_sampling(
    rule: dict[str, Any],
    samples_per_rule: int,
    max_t: int,
    seed: int = 0,
) -> VerificationResult:
    """Randomly sample a residue class and check descent exactly."""

    modulus, residue, k = _rule_parts(rule)
    limit_t = min(k, max_t)
    rng = random.Random(seed)
    for _ in range(samples_per_rule):
        multiplier = rng.randrange(0, max(samples_per_rule * 100, 1))
        n = residue + modulus * multiplier
        if n <= 0:
            n += modulus
        descent = first_descent_time(n, max_steps=limit_t)
        if descent is None:
            return VerificationResult(
                "FAIL_WITH_COUNTEREXAMPLE",
                modulus,
                residue,
                limit_t,
                counterexample=n,
                reason="sample did not descend within the requested time",
            )
    return VerificationResult(
        "UNKNOWN_NEEDS_SYMBOLIC_CHECK",
        modulus,
        residue,
        limit_t,
        reason="sampling found no counterexample, but sampling is not proof",
    )


def find_counterexample(rule: dict[str, Any], search_limit: int) -> int | None:
    """Search positive members of the residue class up to ``search_limit``."""

    modulus, residue, k = _rule_parts(rule)
    n = _min_positive_in_residue(modulus, residue)
    while n <= search_limit:
        if first_descent_time(n, max_steps=k) is None:
            return n
        n += modulus
    return None


def affine_for_parity_prefix(prefix: list[int]) -> tuple[int, int, int]:
    """Return ``A, B, D`` with ``C^m(n) = (A*n + B) / D`` for a parity prefix.

    The prefix says which branch is applied at each step. It does not by itself
    prove that every integer in a residue class follows that prefix; callers
    must separately establish prefix stability.
    """

    a, b, d = 1, 0, 1
    for bit in prefix:
        if bit == 0:
            d *= 2
        elif bit == 1:
            a = 3 * a
            b = 3 * b + d
        else:
            raise ValueError("Parity prefixes contain only 0/1 values")
    return a, b, d


def verify_fixed_residue_descent_exhaustive(
    modulus: int,
    residue: int,
    k: int,
    t_limit: int,
) -> VerificationResult:
    """Try to verify a fixed residue descent rule.

    First, exact finite testing searches the class up to ``t_limit``. Then, if
    the modulus is divisible by ``2**k``, the first ``k`` Collatz parity bits are
    stable across the whole residue class and a symbolic affine inequality can
    prove descent at exactly step ``k`` for all positive members of the class.
    """

    if modulus <= 0 or k <= 0:
        raise ValueError("modulus and k must be positive")
    residue %= modulus
    candidate = find_counterexample(
        {"modulus": modulus, "residue": residue, "suggested_k": k},
        search_limit=t_limit,
    )
    if candidate is not None:
        return VerificationResult(
            "FAIL_WITH_COUNTEREXAMPLE",
            modulus,
            residue,
            k,
            counterexample=candidate,
            reason=f"finite exact search up to {t_limit} found a counterexample",
        )

    required_modulus = 1 << k
    if modulus % required_modulus != 0:
        return VerificationResult(
            "UNKNOWN_NEEDS_LARGER_MODULUS",
            modulus,
            residue,
            k,
            reason=(
                "parity prefix of length k is determined modulo 2^k; "
                f"modulus {modulus} is not divisible by {required_modulus}"
            ),
        )

    representative = _min_positive_in_residue(modulus, residue)
    prefix = parity_prefix(representative, k)
    a, b, d = affine_for_parity_prefix(prefix)

    # To prove (A*n + B)/D < n for every positive n in the class, it is enough
    # to have D > A and check the smallest positive representative. The left
    # side then grows with slope A/D < 1 while n grows with slope 1.
    min_n = representative
    if d > a and a * min_n + b < d * min_n:
        return VerificationResult(
            "PASS",
            modulus,
            residue,
            k,
            reason="symbolic affine inequality proves descent at step k",
        )

    return VerificationResult(
        "UNKNOWN_NEEDS_SYMBOLIC_CHECK",
        modulus,
        residue,
        k,
        reason="finite search passed, but the simple affine inequality did not prove the rule",
    )


def verify_rules_file(
    rules_path: str | Path,
    samples_per_rule: int,
    max_t: int,
    search_limit: int,
) -> list[dict[str, Any]]:
    rules = load_jsonl(rules_path)
    results: list[dict[str, Any]] = []
    for rule in rules:
        sampled = check_rule_by_sampling(rule, samples_per_rule=samples_per_rule, max_t=max_t)
        modulus, residue, k = _rule_parts(rule)
        exact = verify_fixed_residue_descent_exhaustive(
            modulus=modulus,
            residue=residue,
            k=min(k, max_t),
            t_limit=search_limit,
        )
        results.append({"rule": rule, "sampling": sampled.to_dict(), "exact": exact.to_dict()})
    return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify candidate Collatz rules exactly where possible.")
    parser.add_argument("--rules", required=True)
    parser.add_argument("--samples-per-rule", type=int, default=1000)
    parser.add_argument("--max-t", type=int, default=120)
    parser.add_argument("--search-limit", type=int, default=100000)
    parser.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    results = verify_rules_file(args.rules, args.samples_per_rule, args.max_t, args.search_limit)
    console = Console()
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.out).open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            f.write("\n")
    console.print(results)


if __name__ == "__main__":
    main()

