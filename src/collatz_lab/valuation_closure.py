"""Closure of linear 2-adic valuation forms across affine transitions."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console

from .burst import v2_int
from .cycle_certificates import AffineReturnMap
from .cycle_miner import affine_return_from_parent_return_row


@dataclass(frozen=True)
class LinearForm:
    """Represent ``offset + v2(u*q + v)``."""

    u: int
    v: int
    offset: int = 0
    label: str = ""

    def __post_init__(self) -> None:
        if self.u == 0 and self.v == 0:
            raise ValueError("zero linear form has infinite valuation")

    @property
    def key(self) -> tuple[int, int, int]:
        return (self.u, self.v, self.offset)

    def value(self, q: int) -> int:
        return self.u * q + self.v

    def valuation(self, q: int) -> int:
        return self.offset + v2_int(self.value(q))

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["expression"] = f"{self.offset} + v2({self.u}*q + {self.v})"
        return row


def normalize_form(u: int, v: int, offset: int = 0, label: str = "") -> LinearForm:
    """Normalize a linear form up to odd scaling.

    Common powers of two become a valuation offset; common odd factors are
    removed because they do not affect 2-adic valuation.
    """

    if u == 0 and v == 0:
        raise ValueError("zero linear form has infinite valuation")
    g = math.gcd(abs(u), abs(v))
    if g:
        two_offset = v2_int(g) if g else 0
        u //= g
        v //= g
        offset += two_offset
    if u < 0 or (u == 0 and v < 0):
        u = -u
        v = -v
    return LinearForm(u=u, v=v, offset=offset, label=label)


def height_form_for_return_map(return_map: AffineReturnMap) -> LinearForm:
    """Return the natural cycle height ``v2((A-D)q+B)``."""

    return normalize_form(
        return_map.A - return_map.D,
        return_map.B,
        label=f"height:{return_map.name}",
    )


def pullback_form_through_map(form: LinearForm, return_map: AffineReturnMap) -> dict[str, Any]:
    """Pull a target-side form backward through ``q'=(Aq+B)/D``.

    If ``L(q') = u*q' + v``, then

        L(q') = (u*A*q + u*B + v*D) / D.

    So the target valuation equals the pullback valuation minus ``log2(D)``.
    """

    raw_u = form.u * return_map.A
    raw_v = form.u * return_map.B + form.v * return_map.D
    pullback = normalize_form(raw_u, raw_v, offset=form.offset, label=f"pullback:{form.label}:{return_map.name}")
    return {
        "source_form": pullback.to_dict(),
        "target_form": form.to_dict(),
        "map": return_map.to_dict(),
        "valuation_delta": pullback.offset - form.offset - return_map.d_power,
        "identity": "v2(L(target q')) = v2(pullback_L(source q)) - log2(D)",
    }


def _dedupe_forms(forms: Iterable[LinearForm]) -> list[LinearForm]:
    rows: dict[tuple[int, int], LinearForm] = {}
    for form in forms:
        key = (form.u, form.v)
        if key not in rows or form.offset < rows[key].offset:
            rows[key] = form
    return sorted(rows.values(), key=lambda row: (abs(row.u) + abs(row.v), row.u, row.v, row.offset))


def build_valuation_closure(
    return_maps: list[AffineReturnMap],
    seed_forms: list[LinearForm] | None = None,
    max_depth: int = 2,
    max_forms: int = 2000,
) -> dict[str, Any]:
    """Build a bounded valuation-form closure report."""

    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    seeds = seed_forms or [height_form_for_return_map(row) for row in return_maps]
    known = _dedupe_forms(seeds)
    transfer_rows: list[dict[str, Any]] = []
    frontier = known
    for depth in range(1, max_depth + 1):
        next_forms: list[LinearForm] = []
        for form in frontier:
            for return_map in return_maps:
                transfer = pullback_form_through_map(form, return_map)
                next_form = LinearForm(**{k: transfer["source_form"][k] for k in ["u", "v", "offset", "label"]})
                transfer_rows.append({**transfer, "closure_depth": depth})
                next_forms.append(next_form)
                if len(transfer_rows) >= max_forms:
                    break
            if len(transfer_rows) >= max_forms:
                break
        combined = _dedupe_forms([*known, *next_forms])
        if len(combined) > max_forms:
            combined = combined[:max_forms]
        known_keys = {row.key for row in known}
        frontier = [row for row in combined if row.key not in known_keys]
        known = combined
        if not frontier or len(transfer_rows) >= max_forms:
            break
    return {
        "scope": "linear 2-adic valuation closure",
        "status": "VALUATION_CLOSURE_SCAFFOLD",
        "return_map_count": len(return_maps),
        "seed_form_count": len(seeds),
        "form_count": len(known),
        "transfer_count": len(transfer_rows),
        "max_depth": max_depth,
        "forms": [row.to_dict() for row in known],
        "transfers": transfer_rows[:max_forms],
    }


def _load_return_maps(path: str | Path) -> list[AffineReturnMap]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [affine_return_from_parent_return_row(row) for row in payload.get("maps", [])]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build 2-adic valuation-form closure.")
    parser.add_argument("--return-report", required=True)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-forms", type=int, default=2000)
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_valuation_closure(
        _load_return_maps(args.return_report),
        max_depth=args.max_depth,
        max_forms=args.max_forms,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print({"out": str(out), "forms": report["form_count"], "transfers": report["transfer_count"]})


if __name__ == "__main__":
    main()
