"""Ancestor-debt accounting for composed Collatz affine certificates."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console

from .residual_frontier import normalize_residue


@dataclass(frozen=True)
class AffineBlock:
    A: int
    B: int
    D: int
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["log_growth_weight"] = math.log(self.A / self.D)
        return row


def compose_blocks(blocks: Iterable[AffineBlock], label: str = "composed") -> AffineBlock:
    """Compose affine blocks in application order."""

    a_total, b_total, d_total = 1, 0, 1
    labels: list[str] = []
    for block in blocks:
        a_total, b_total, d_total = (
            block.A * a_total,
            block.A * b_total + block.B * d_total,
            block.D * d_total,
        )
        if block.label:
            labels.append(block.label)
    return AffineBlock(a_total, b_total, d_total, label=label or " then ".join(labels))


def apply_affine_block(block: AffineBlock, n: int) -> int:
    numerator = block.A * n + block.B
    if numerator % block.D != 0:
        raise ValueError("affine block is not integral for n")
    return numerator // block.D


def ancestor_descent_status(block: AffineBlock, q_residue: int, q_depth: int, burst_length: int = 6) -> dict[str, Any]:
    """Check whether ``(A*n+B)/D < n`` for all ``n = 2**burst*q-1`` in a class."""

    n_depth = q_depth + burst_length
    n_modulus = 1 << n_depth
    n_residue = normalize_residue((1 << burst_length) * q_residue - 1, n_depth)
    min_n = n_residue if n_residue > 0 else n_modulus
    coeff = block.A - block.D
    value_at_min = coeff * min_n + block.B
    if coeff < 0:
        status = "PROVED_ANCESTOR_DESCENT" if value_at_min < 0 else "ANCESTOR_DESCENT_AFTER_THRESHOLD_ONLY"
    elif coeff == 0:
        status = "PROVED_ANCESTOR_DESCENT" if block.B < 0 else "DEBT_UNPAID"
    else:
        status = "DEBT_UNPAID"
    return {
        "status": status,
        "block": block.to_dict(),
        "q_residue": q_residue,
        "q_depth": q_depth,
        "burst_length": burst_length,
        "min_n": min_n,
        "inequality": "(A-D)*n + B < 0",
        "inequality_value_at_min_n": value_at_min,
        "growth_multiplier_A": block.A,
        "growth_multiplier_D": block.D,
        "log_debt_created": math.log(block.A / block.D),
        "ancestor_descent": status == "PROVED_ANCESTOR_DESCENT",
        "debt_paid": status == "PROVED_ANCESTOR_DESCENT",
    }


def classify_certificate_after_expansion(
    expansion: AffineBlock,
    local_certificate: AffineBlock,
    q_residue: int,
    q_depth: int,
    burst_length: int = 6,
) -> dict[str, Any]:
    """Compose expansion and local certificate, then classify ancestor debt."""

    composed = compose_blocks([expansion, local_certificate], label=f"{expansion.label}+{local_certificate.label}")
    result = ancestor_descent_status(composed, q_residue, q_depth, burst_length=burst_length)
    local_status = ancestor_descent_status(local_certificate, 0, 0, burst_length=0)
    result.update(
        {
            "expansion": expansion.to_dict(),
            "local_certificate": local_certificate.to_dict(),
            "local_certificate_status": (
                "PROVED_LOCAL_DESCENT" if local_certificate.A < local_certificate.D else local_status["status"]
            ),
            "ancestor_certificate_status": result["status"],
        }
    )
    return result


def build_debt_demo_report() -> dict[str, Any]:
    sharp_return = AffineBlock(729, 665, 128, label="sharp_return_n")
    q9_local = AffineBlock(729, 665, 1024, label="q9_local_descent")
    return {
        "scope": "ancestor debt accounting demo",
        "sharp_q23_then_q9": classify_certificate_after_expansion(
            sharp_return,
            q9_local,
            q_residue=791,
            q_depth=11,
        ),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build ancestor debt accounting report.")
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_debt_demo_report()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print({"out": str(out), "status": report["sharp_q23_then_q9"]["status"]})


if __name__ == "__main__":
    main()
