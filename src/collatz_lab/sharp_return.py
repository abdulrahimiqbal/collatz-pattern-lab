"""Exact renormalization subsystem for the sharp ``q == 23 mod 128`` branch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .burst import v2_int
from .residual_frontier import normalize_residue

SHARP_MODULUS_DEPTH = 7
SHARP_RESIDUE = 23
R23_A = 729
R23_D = 128
R23_N_AFFINE_A = 729
R23_N_AFFINE_B = 665
R23_N_AFFINE_D = 128
SHARP_HEIGHT_A = 601


def R23(q: int) -> int:
    """Return ``R(q) = (729*q + 1) / 128`` on ``q == 23 mod 128``."""

    if q <= 0:
        raise ValueError("q must be positive")
    if q % R23_D != SHARP_RESIDUE:
        raise ValueError("R23 only applies to q == 23 mod 128")
    numerator = R23_A * q + 1
    if numerator % R23_D != 0:
        raise AssertionError("sharp residue did not make R23 integral")
    return numerator // R23_D


def sharp_height(q: int) -> int:
    """Return ``J(q) = v2(601*q + 1)``."""

    if q <= 0:
        raise ValueError("q must be positive")
    return v2_int(SHARP_HEIGHT_A * q + 1)


def verify_sharp_height_drop(q: int) -> bool:
    """Return whether ``J(R23(q)) = J(q) - 7``."""

    return sharp_height(R23(q)) == sharp_height(q) - SHARP_MODULUS_DEPTH


def sharp_cylinder_residue(return_count: int) -> tuple[int, int]:
    """Return the cylinder for at least ``return_count`` sharp returns.

    ``m`` consecutive returns are equivalent to
    ``q == -601**-1 mod 2**(7*m)``.
    """

    if return_count < 1:
        raise ValueError("return_count must be positive")
    depth = SHARP_MODULUS_DEPTH * return_count
    modulus = 1 << depth
    residue = (-pow(SHARP_HEIGHT_A, -1, modulus)) % modulus
    return residue, depth


def sharp_return_count_lower_bound(q_depth: int) -> dict[str, Any]:
    """Summarize finite-depth sharp-return tower counts."""

    if q_depth < SHARP_MODULUS_DEPTH:
        raise ValueError("q_depth must be at least 7 for the sharp q23 branch")
    max_resolved_returns = q_depth // SHARP_MODULUS_DEPTH
    at_least = []
    for returns in range(1, max_resolved_returns + 1):
        residue, depth = sharp_cylinder_residue(returns)
        at_least.append(
            {
                "returns": returns,
                "q_residue": residue,
                "q_depth": depth,
                "count_at_q_depth": 1 << (q_depth - depth),
                "condition": f"q == {residue} mod 2^{depth}",
            }
        )

    exits = []
    for index, row in enumerate(at_least[:-1]):
        next_row = at_least[index + 1]
        exits.append(
            {
                "exit_after_returns": row["returns"],
                "count": row["count_at_q_depth"] - next_row["count_at_q_depth"],
            }
        )
    deeper = at_least[-1]["count_at_q_depth"]
    return {
        "q_depth": q_depth,
        "scope": "q == 23 mod 128 inside n = 64*q - 1",
        "sharp_branch_count": 1 << (q_depth - SHARP_MODULUS_DEPTH),
        "at_least_return_cylinders": at_least,
        "guaranteed_exit_counts": exits,
        "needs_deeper_bits": deeper,
        "needs_deeper_bits_after_at_least_returns": at_least[-1]["returns"],
        "limit_2adic": "q_* = -1/601 in Z_2",
        "positive_integer_forever_status": "IMPOSSIBLE_FOR_POSITIVE_INTEGER",
        "positive_integer_forever_reason": "Infinite sharp returns would force 601*q + 1 divisible by every power of 2.",
    }


def sharp_return_count(q: int) -> int:
    """Return the exact number of consecutive sharp returns for positive ``q``."""

    count = 0
    current = q
    while current % R23_D == SHARP_RESIDUE:
        count += 1
        current = R23(current)
    return count


def pushforward_q23_class(q_residue: int, q_depth: int) -> tuple[int, int]:
    """Push a q-class through the sharp return map.

    Input must satisfy ``q_residue == 23 mod 128``. The image depth is
    ``q_depth - 7``.
    """

    if q_depth < SHARP_MODULUS_DEPTH:
        raise ValueError("q_depth must be at least 7")
    if q_residue % R23_D != SHARP_RESIDUE:
        raise ValueError("source class must lie inside q == 23 mod 128")
    image_depth = q_depth - SHARP_MODULUS_DEPTH
    image_modulus = 1 << image_depth
    image_residue = ((R23_A * normalize_residue(q_residue, q_depth) + 1) // R23_D) % image_modulus
    return image_residue, image_depth


def pullback_q23_image_class(qp_residue: int, qp_depth: int) -> tuple[int, int]:
    """Pull an image q'-class back into the sharp branch."""

    if qp_depth < 0:
        raise ValueError("qp_depth must be non-negative")
    modulus = 1 << qp_depth
    if modulus == 1:
        s_residue = 0
    else:
        s_residue = (pow(R23_A, -1, modulus) * (normalize_residue(qp_residue, qp_depth) - 131)) % modulus
    q_depth = qp_depth + SHARP_MODULUS_DEPTH
    q_residue = normalize_residue((R23_D * s_residue) + SHARP_RESIDUE, q_depth)
    return q_residue, q_depth


def pullback_cube_under_q23_return(cube: dict[str, Any]) -> dict[str, Any]:
    """Pull back a low-bit residue cube when it is a full congruence class.

    General masked cubes do not stay masked under odd affine maps in a simple
    bitwise way. For now, this function returns an exact congruence pullback
    when the cube fixes all low bits of its depth; otherwise it returns an
    explicit symbolic predicate descriptor.
    """

    depth = int(cube["depth"])
    mask = int(cube.get("mask", (1 << depth) - 1))
    value = int(cube.get("value", cube.get("residue", 0)))
    full_low_mask = (1 << depth) - 1
    if mask == full_low_mask:
        residue, q_depth = pullback_q23_image_class(value, depth)
        return {
            "status": "EXACT_LOW_CONGRUENCE_PULLBACK",
            "q_residue": residue,
            "q_depth": q_depth,
            "mask": (1 << q_depth) - 1,
            "value": residue,
            "source_cube": cube,
        }
    return {
        "status": "SYMBOLIC_MASKED_PULLBACK",
        "q_depth": depth + SHARP_MODULUS_DEPTH,
        "predicate": "((729*((q-23)/128)+131) & mask) == value",
        "source_cube": cube,
    }


def sharp_phi(n: int, q: int) -> int:
    """Return ``Phi(n,q) = n**8 * 2**(3*J(q))``."""

    if n <= 0 or q <= 0:
        raise ValueError("sharp potential requires positive n and q")
    return (n**8) * (1 << (3 * sharp_height(q)))


def verify_sharp_phi_decreases(q: int) -> bool:
    """Return whether the exact sharp potential decreases under ``R23``."""

    q1 = R23(q)
    n0 = 64 * q - 1
    n1 = 64 * q1 - 1
    return sharp_phi(n1, q1) < sharp_phi(n0, q)


def sharp_potential_proof() -> dict[str, Any]:
    return {
        "status": "PROVED_POTENTIAL_DECREASE",
        "potential": "Phi(n,q)=n^8*2^(3*J(q)), J(q)=v2(601*q+1)",
        "height_identity": "J(R23(q)) = J(q) - 7",
        "growth_bound": "n'/n < 6 for positive q",
        "integer_inequality": "6^8 < 2^21",
        "six_power_8": 6**8,
        "two_power_21": 1 << 21,
        "conclusion": "Phi(64*R23(q)-1,R23(q)) < Phi(64*q-1,q)",
    }


def sharp_return_n_affine() -> tuple[int, int, int]:
    """Return ``(A,B,D)`` with ``C^13(n) = (A*n+B)/D`` on sharp branch."""

    return R23_N_AFFINE_A, R23_N_AFFINE_B, R23_N_AFFINE_D


def compose_affine(first: tuple[int, int, int], second: tuple[int, int, int]) -> tuple[int, int, int]:
    """Compose ``first`` then ``second`` affine maps."""

    a1, b1, d1 = first
    a2, b2, d2 = second
    return a2 * a1, a2 * b1 + b2 * d1, d2 * d1


def ancestor_descent_check(
    composed_affine: tuple[int, int, int],
    q_residue: int,
    q_depth: int,
) -> dict[str, Any]:
    """Check exactly whether composed affine image descends below ancestor."""

    a, b, d = composed_affine
    n_modulus = 1 << (q_depth + 6)
    n_residue = normalize_residue(64 * q_residue - 1, q_depth + 6)
    min_n = n_residue if n_residue > 0 else n_modulus
    lhs_coeff = a - d
    lhs_at_min = lhs_coeff * min_n + b
    if lhs_coeff < 0:
        status = "PROVED_ANCESTOR_DESCENT" if lhs_at_min < 0 else "ANCESTOR_DESCENT_AFTER_THRESHOLD_ONLY"
    elif lhs_coeff == 0:
        status = "PROVED_ANCESTOR_DESCENT" if b < 0 else "ANCESTOR_DEBT_UNPAID"
    else:
        status = "ANCESTOR_DEBT_UNPAID"
    return {
        "status": status,
        "affine_A": a,
        "affine_B": b,
        "affine_D": d,
        "q_residue": q_residue,
        "q_depth": q_depth,
        "min_n": min_n,
        "inequality_value_at_min_n": lhs_at_min,
        "growth_multiplier_A": a,
        "growth_multiplier_D": d,
        "debt_paid": status == "PROVED_ANCESTOR_DESCENT",
    }


def compose_return_with_certificate(return_map: dict[str, Any] | None, certificate: dict[str, Any]) -> dict[str, Any]:
    """Compose the sharp return with a local image certificate."""

    cert_affine = (
        int(certificate["affine_A"]),
        int(certificate["affine_B"]),
        int(certificate["affine_D"]),
    )
    composed = compose_affine(sharp_return_n_affine(), cert_affine)
    q_residue = int(certificate.get("preimage_q_residue", SHARP_RESIDUE))
    q_depth = int(certificate.get("preimage_q_depth", SHARP_MODULUS_DEPTH))
    result = ancestor_descent_check(composed, q_residue=q_residue, q_depth=q_depth)
    result.update(
        {
            "local_certificate_status": "PROVED_LOCAL_DESCENT",
            "return_status": "PROVED_TRANSITION_ONLY",
            "return_map": return_map or {"name": "R23"},
        }
    )
    return result


def q9_pullback_debt_example() -> dict[str, Any]:
    """Debt check for pulling back the known ``q' == 9 mod 16`` local family."""

    q_residue, q_depth = pullback_q23_image_class(9, 4)
    certificate = {
        "affine_A": 729,
        "affine_B": 665,
        "affine_D": 1024,
        "preimage_q_residue": q_residue,
        "preimage_q_depth": q_depth,
        "image_condition": "q' == 9 mod 16",
    }
    result = compose_return_with_certificate({"name": "R23"}, certificate)
    result["image_condition"] = certificate["image_condition"]
    result["preimage_condition"] = f"q == {q_residue} mod 2^{q_depth}"
    return result


def build_sharp_return_report(q_depth: int) -> dict[str, Any]:
    samples = [SHARP_RESIDUE + R23_D * i for i in range(16)]
    return {
        "scope": "sharp q == 23 mod 128 return branch inside n = 64*q - 1",
        "status": "PROVED_TRANSITION_ONLY_AND_PROVED_POTENTIAL_DECREASE",
        "R23": "R(q) = (729*q + 1) / 128",
        "domain": "q == 23 mod 128",
        "collatz_statement": "C^13(64*q-1) = 64*R(q)-1",
        "height": "J(q)=v2(601*q+1)",
        "height_identity": "J(R(q))=J(q)-7",
        "tower": sharp_return_count_lower_bound(q_depth),
        "potential": sharp_potential_proof(),
        "q9_pullback_debt_example": q9_pullback_debt_example(),
        "sample_checks": [
            {
                "q": q,
                "R23_q": R23(q),
                "J_q": sharp_height(q),
                "J_R23_q": sharp_height(R23(q)),
                "height_drop_ok": verify_sharp_height_drop(q),
                "phi_decreases": verify_sharp_phi_decreases(q),
                "sharp_return_count": sharp_return_count(q),
            }
            for q in samples
        ],
    }


def write_sharp_return_markdown(report: dict[str, Any], out: str | Path) -> None:
    tower = report["tower"]
    debt = report["q9_pullback_debt_example"]
    lines = [
        "# Sharp Return Subsystem",
        "",
        f"- status: `{report['status']}`",
        f"- domain: `{report['domain']}`",
        f"- transition: `{report['R23']}`",
        f"- Collatz statement: `{report['collatz_statement']}`",
        f"- height: `{report['height']}`",
        f"- identity: `{report['height_identity']}`",
        "",
        "## Tower Counts",
        "",
        f"- q-depth: `{tower['q_depth']}`",
        f"- sharp branch count: `{tower['sharp_branch_count']}`",
    ]
    for row in tower["guaranteed_exit_counts"]:
        lines.append(f"- guaranteed exit after `{row['exit_after_returns']}` return(s): `{row['count']}`")
    lines.extend(
        [
            f"- needs deeper bits after at least `{tower['needs_deeper_bits_after_at_least_returns']}` return(s): `{tower['needs_deeper_bits']}`",
            f"- forever status: `{tower['positive_integer_forever_status']}`",
            "",
            "## Cylinders",
            "",
        ]
    )
    for row in tower["at_least_return_cylinders"]:
        lines.append(f"- at least `{row['returns']}` return(s): `{row['condition']}` count `{row['count_at_q_depth']}`")
    lines.extend(
        [
            "",
            "## Potential",
            "",
            f"- status: `{report['potential']['status']}`",
            f"- proof: `{report['potential']['growth_bound']}` and `{report['potential']['integer_inequality']}`",
            "",
            "## Ancestor Debt Example",
            "",
            f"- image local family: `{debt['image_condition']}`",
            f"- preimage: `{debt['preimage_condition']}`",
            f"- ancestor status: `{debt['status']}`",
            f"- debt paid: `{debt['debt_paid']}`",
            "",
        ]
    )
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Report the exact sharp q23 return subsystem.")
    parser.add_argument("--q-depth", type=int, default=23)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_sharp_return_report(args.q_depth)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_sharp_return_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "tower": report["tower"]["guaranteed_exit_counts"],
            "needs_deeper_bits": report["tower"]["needs_deeper_bits"],
            "potential": report["potential"]["status"],
        }
    )


if __name__ == "__main__":
    main()
