"""Counterpressure search for proof candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .adic_basin import fixed_point_residue_mod_power
from .cycle_certificates import AffineReturnMap, apply_affine_return, sharp_q23_return_map
from .debt import AffineBlock, ancestor_descent_status, apply_affine_block


def high_risk_qs_for_return_map(return_map: AffineReturnMap, q_depth: int, limit: int = 32) -> list[int]:
    """Generate q values near the 2-adic fixed point and domain boundary."""

    rows: list[int] = []
    if return_map.domain_residue is not None and return_map.domain_depth is not None:
        modulus = 1 << return_map.domain_depth
        residue = return_map.domain_residue % modulus
        start = residue if residue > 0 else modulus
        rows.extend(start + modulus * i for i in range(limit // 2 + 1))
    if return_map.height_alpha % 2:
        depth = max(1, min(q_depth, 24))
        residue = fixed_point_residue_mod_power(return_map, depth)
        modulus = 1 << depth
        start = residue if residue > 0 else modulus
        rows.extend(start + modulus * i for i in range(limit // 2 + 1))
    deduped = []
    seen = set()
    for q in rows:
        if q > 0 and q not in seen:
            deduped.append(q)
            seen.add(q)
        if len(deduped) >= limit:
            break
    return deduped


def falsify_ancestor_descent_claim(
    block: AffineBlock,
    q_residue: int,
    q_depth: int,
    burst_length: int = 6,
    sample_count: int = 32,
) -> dict[str, Any]:
    """Try to falsify an ancestor-descent affine claim."""

    exact = ancestor_descent_status(block, q_residue, q_depth, burst_length=burst_length)
    modulus = 1 << q_depth
    samples = []
    for i in range(sample_count):
        q = q_residue + modulus * i
        if q <= 0:
            q += modulus
        n = (1 << burst_length) * q - 1
        try:
            image = apply_affine_block(block, n)
            ok = image < n
            samples.append({"q": q, "n": n, "image": image, "ancestor_descent": ok})
            if not ok:
                return {
                    "status": "COUNTEREXAMPLE_FOUND",
                    "exact_status": exact["status"],
                    "counterexample": samples[-1],
                    "samples": samples,
                }
        except ValueError as exc:
            samples.append({"q": q, "n": n, "error": str(exc), "ancestor_descent": False})
            return {
                "status": "COUNTEREXAMPLE_FOUND",
                "exact_status": exact["status"],
                "counterexample": samples[-1],
                "samples": samples,
            }
    return {
        "status": "NO_COUNTEREXAMPLE_FOUND" if exact["ancestor_descent"] else "NO_SAMPLE_COUNTEREXAMPLE_BUT_NOT_PROVED",
        "exact_status": exact["status"],
        "samples": samples,
    }


def falsify_return_map_integrality(return_map: AffineReturnMap, q_depth: int = 23, limit: int = 32) -> dict[str, Any]:
    """Check high-risk q samples for return-map integrality and positivity."""

    samples = []
    for q in high_risk_qs_for_return_map(return_map, q_depth=q_depth, limit=limit):
        try:
            q_next = apply_affine_return(return_map, q)
            samples.append({"q": q, "q_next": q_next, "ok": q_next > 0})
        except ValueError as exc:
            samples.append({"q": q, "error": str(exc), "ok": False})
            return {"status": "COUNTEREXAMPLE_FOUND", "counterexample": samples[-1], "samples": samples}
    return {"status": "NO_COUNTEREXAMPLE_FOUND", "samples": samples}


def build_falsifier_report() -> dict[str, Any]:
    sharp = sharp_q23_return_map()
    local_not_enough = AffineBlock(729 * 729, 729 * 665 + 665 * 128, 128 * 1024, "sharp_then_q9")
    return {
        "scope": "proof-candidate counterpressure search",
        "status": "FALSIFIER_SCAFFOLD",
        "sharp_return_integrality": falsify_return_map_integrality(sharp),
        "sharp_then_q9_ancestor_debt": falsify_ancestor_descent_claim(
            local_not_enough,
            q_residue=791,
            q_depth=11,
        ),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run proof-candidate falsifier diagnostics.")
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_falsifier_report()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print({"out": str(out), "status": report["status"]})


if __name__ == "__main__":
    main()
