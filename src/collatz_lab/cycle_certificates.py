"""Generic certificates for affine recursive return cycles.

A return map of the form

    q' = (A*q + B) / D,  D = 2**d, A odd

has a natural linear 2-adic height

    H(q) = v2((A-D)*q + B).

Whenever the map is integral, the height satisfies

    H(q') = H(q) - d

unless the linear form is zero, i.e. unless q is a fixed point of the affine
map. This module packages that algebra as a reusable cycle-killing certificate.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console

from .burst import v2_int
from .residual_frontier import normalize_residue


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def log2_power(value: int) -> int:
    if not is_power_of_two(value):
        raise ValueError(f"expected power of two, got {value}")
    return value.bit_length() - 1


@dataclass(frozen=True)
class AffineReturnMap:
    name: str
    A: int
    B: int
    D: int
    domain_residue: int | None = None
    domain_depth: int | None = None
    step_count: int | None = None
    description: str = ""

    @property
    def d_power(self) -> int:
        return log2_power(self.D)

    @property
    def height_alpha(self) -> int:
        return self.A - self.D

    @property
    def height_beta(self) -> int:
        return self.B

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["d_power"] = self.d_power if is_power_of_two(self.D) else None
        row["height_linear_form"] = f"{self.height_alpha}*q + {self.height_beta}"
        return row


def apply_affine_return(return_map: AffineReturnMap, q: int) -> int:
    """Apply an affine return map exactly."""

    if q <= 0:
        raise ValueError("q must be positive")
    if return_map.domain_depth is not None and return_map.domain_residue is not None:
        if q % (1 << return_map.domain_depth) != normalize_residue(
            return_map.domain_residue,
            return_map.domain_depth,
        ):
            raise ValueError(f"q is outside the domain of {return_map.name}")
    numerator = return_map.A * q + return_map.B
    if numerator % return_map.D != 0:
        raise ValueError("affine return map is not integral on this q")
    return numerator // return_map.D


def cycle_height_value(return_map: AffineReturnMap, q: int) -> int:
    """Return ``v2((A-D)*q+B)``."""

    return v2_int(return_map.height_alpha * q + return_map.height_beta)


def fixed_point_info(return_map: AffineReturnMap) -> dict[str, Any]:
    """Return exact fixed-point information for ``q' = q``."""

    alpha = return_map.height_alpha
    beta = return_map.height_beta
    if alpha == 0:
        if beta == 0:
            return {
                "status": "EVERY_Q_FORMALLY_FIXED",
                "positive_integer_fixed_point": True,
                "q": None,
            }
        return {
            "status": "NO_FIXED_POINT",
            "positive_integer_fixed_point": False,
            "q": None,
        }
    numerator = -beta
    if numerator % alpha != 0:
        return {
            "status": "NO_INTEGER_FIXED_POINT",
            "positive_integer_fixed_point": False,
            "q": None,
        }
    q = numerator // alpha
    in_domain = True
    if q > 0 and return_map.domain_depth is not None and return_map.domain_residue is not None:
        in_domain = q % (1 << return_map.domain_depth) == normalize_residue(
            return_map.domain_residue,
            return_map.domain_depth,
        )
    return {
        "status": "INTEGER_FIXED_POINT" if q > 0 and in_domain else "NO_POSITIVE_DOMAIN_FIXED_POINT",
        "positive_integer_fixed_point": q > 0 and in_domain,
        "q": q,
        "in_domain": in_domain,
    }


def verify_height_drop(return_map: AffineReturnMap, q: int) -> bool:
    """Check ``H(f(q)) = H(q) - d`` for one sample q."""

    q_next = apply_affine_return(return_map, q)
    return cycle_height_value(return_map, q_next) == cycle_height_value(return_map, q) - return_map.d_power


def compose_affine_return_maps(maps: Iterable[AffineReturnMap], name: str = "composed") -> AffineReturnMap:
    """Compose affine q-maps in application order."""

    a_total, b_total, d_total = 1, 0, 1
    step_count = 0
    descriptions: list[str] = []
    for row in maps:
        a_total, b_total, d_total = (
            row.A * a_total,
            row.A * b_total + row.B * d_total,
            row.D * d_total,
        )
        if row.step_count is not None:
            step_count += row.step_count
        descriptions.append(row.name)
    return AffineReturnMap(
        name=name,
        A=a_total,
        B=b_total,
        D=d_total,
        step_count=step_count or None,
        description=" then ".join(descriptions),
    )


def certify_affine_return_map(
    return_map: AffineReturnMap,
    sample_qs: Iterable[int] | None = None,
) -> dict[str, Any]:
    """Return a reusable cycle-killing certificate for one affine map."""

    structural_errors: list[str] = []
    if return_map.A % 2 != 1:
        structural_errors.append("A must be odd")
    if not is_power_of_two(return_map.D):
        structural_errors.append("D must be a power of two")
    if return_map.D <= 0:
        structural_errors.append("D must be positive")

    fixed = fixed_point_info(return_map) if not structural_errors else None
    samples = []
    sample_passed = True
    for q in sample_qs or []:
        try:
            q_next = apply_affine_return(return_map, q)
            h0 = cycle_height_value(return_map, q)
            h1 = cycle_height_value(return_map, q_next)
            ok = h1 == h0 - return_map.d_power
            sample_passed = sample_passed and ok
            samples.append({"q": q, "q_next": q_next, "H_q": h0, "H_q_next": h1, "ok": ok})
        except ValueError as exc:
            sample_passed = False
            samples.append({"q": q, "error": str(exc), "ok": False})

    if structural_errors:
        status = "INVALID_AFFINE_RETURN_MAP"
    elif fixed is not None and fixed["positive_integer_fixed_point"]:
        status = "POSITIVE_FIXED_POINT_REQUIRES_EXCEPTION_CHECK"
    else:
        status = "PROVED_HEIGHT_DECREASE_ON_REPEAT"

    return {
        "status": status,
        "map": return_map.to_dict(),
        "height": {
            "linear_form_alpha": return_map.height_alpha,
            "linear_form_beta": return_map.height_beta,
            "linear_form": f"{return_map.height_alpha}*q + {return_map.height_beta}",
            "drop_per_repeat": None if structural_errors else return_map.d_power,
            "identity": (
                "L(q') = A*L(q)/D, hence v2(L(q')) = v2(L(q)) - log2(D) "
                "when L(q) != 0"
            ),
        },
        "fixed_point": fixed,
        "structural_errors": structural_errors,
        "sample_height_drop_passed": sample_passed,
        "sample_checks": samples,
        "proof_role": "cycle-killing/ranking argument for repeated affine return",
    }


def sharp_q23_return_map() -> AffineReturnMap:
    return AffineReturnMap(
        name="sharp_q23_R23",
        A=729,
        B=1,
        D=128,
        domain_residue=23,
        domain_depth=7,
        step_count=13,
        description="q == 23 mod 128 return inside n = 64*q - 1",
    )


def build_cycle_certificate_report() -> dict[str, Any]:
    sharp = sharp_q23_return_map()
    samples = [23 + 128 * i for i in range(16)]
    twice = compose_affine_return_maps([sharp, sharp], name="sharp_q23_R23_twice")
    return {
        "scope": "affine recursive return cycle certificates",
        "claim_status": "PROOF_SCAFFOLD_WITH_EXACT_CYCLE_CERTIFICATES",
        "certificates": [
            certify_affine_return_map(sharp, sample_qs=samples),
            certify_affine_return_map(twice, sample_qs=[6679 + (1 << 14) * i for i in range(4)]),
        ],
    }


def write_cycle_certificate_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Affine Cycle Certificates",
        "",
        f"- status: `{report['claim_status']}`",
        "",
    ]
    for cert in report["certificates"]:
        m = cert["map"]
        h = cert["height"]
        lines.extend(
            [
                f"## {m['name']}",
                "",
                f"- status: `{cert['status']}`",
                f"- map: `q -> ({m['A']}*q + {m['B']}) / {m['D']}`",
                f"- domain: `q == {m.get('domain_residue')} mod 2^{m.get('domain_depth')}`",
                f"- height: `v2({h['linear_form']})`",
                f"- drop per repeat: `{h['drop_per_repeat']}`",
                f"- fixed point: `{cert['fixed_point']}`",
                f"- sample height drop passed: `{cert['sample_height_drop_passed']}`",
                "",
            ]
        )
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build affine return cycle certificates.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_cycle_certificate_report()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_cycle_certificate_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "statuses": [row["status"] for row in report["certificates"]],
        }
    )


if __name__ == "__main__":
    main()
