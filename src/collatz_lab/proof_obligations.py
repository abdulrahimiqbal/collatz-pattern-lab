"""Master proof-obligation report for the P6 parent subsystem."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console


FINAL_STATUSES = {
    "CLOSED_BY_ANCESTOR_DESCENT",
    "CLOSED_BY_TRANSITION_TO_CLOSED_STATE",
    "CLOSED_BY_HEIGHT_RANKING",
    "CLOSED_BY_EXACT_POTENTIAL",
    "NEEDS_SPLIT",
    "UNKNOWN",
}


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _default_paths() -> dict[str, Path]:
    return {
        "residual": Path("reports/residual_frontier_63mod64_q20.json"),
        "cube_lift": Path("reports/P6_cube_lift_report.json"),
        "adic_basin": Path("reports/adic_basin_q23.json"),
        "cycle_mining": Path("reports/cycle_mining_parent_returns_q23.json"),
        "sharp_return": Path("reports/sharp_return_tower_q23.json"),
        "debt": Path("reports/debt_demo.json"),
        "frontier_strata": Path("reports/frontier_strata_63mod64_q20.json"),
    }


def _status_from_lift_status(status: str) -> str:
    if status == "PROVED_INFINITE_ANCESTOR_DESCENT":
        return "CLOSED_BY_ANCESTOR_DESCENT"
    if status == "PROVED_INFINITE_HEIGHT_RANKED_RETURN":
        return "CLOSED_BY_HEIGHT_RANKING"
    if status in {"PROVED_INFINITE_TRANSITION", "PROVED_INFINITE_LOCAL_DESCENT"}:
        return "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"
    if status == "NEEDS_SPLIT":
        return "NEEDS_SPLIT"
    return "UNKNOWN"


def build_proof_obligations_report(paths: dict[str, Path] | None = None) -> dict[str, Any]:
    paths = paths or _default_paths()
    loaded = {name: _load_optional(path) for name, path in paths.items()}
    obligations: list[dict[str, Any]] = []

    residual = loaded["residual"]
    if residual is not None:
        obligations.append(
            {
                "obligation_id": "P6_q20_finite_frontier_coverage",
                "scope": "finite q-depth diagnostic, not proof coverage",
                "coverage": {
                    key: residual.get(key)
                    for key in [
                        "total_q_classes",
                        "total_certified_q_classes",
                        "residual_unknown_q_classes",
                        "total_certified_within_parent_percent",
                        "unknown_within_parent_percent",
                    ]
                },
                "transition_rule": "finite-depth residual classifier",
                "ancestor_descent": residual.get("residual_unknown_q_classes", 1) == 0,
                "scc_status": "NEEDS_SPLIT" if residual.get("residual_unknown_q_classes", 0) else "CLOSED_BY_ANCESTOR_DESCENT",
            }
        )

    cube_lift = loaded["cube_lift"]
    if cube_lift is not None:
        for set_name, set_report in cube_lift.get("sets", {}).items():
            for status, count in set_report.get("status_counts", {}).items():
                obligations.append(
                    {
                        "obligation_id": f"cube_lift:{set_name}:{status}",
                        "scope": f"P6 compressed cubes set {set_name}",
                        "coverage": {"cube_count": count},
                        "transition_rule": status,
                        "ancestor_descent": status == "PROVED_INFINITE_ANCESTOR_DESCENT",
                        "scc_status": _status_from_lift_status(status),
                    }
                )

    adic = loaded["adic_basin"]
    if adic is not None:
        for basin in adic.get("basins", []):
            obligations.append(
                {
                    "obligation_id": f"adic_basin:{basin['cycle_map']['name']}",
                    "scope": basin["cycle_map"]["description"],
                    "coverage": basin.get("q_depth_summary"),
                    "transition_rule": basin["cycle_map"],
                    "ancestor_descent": False,
                    "scc_status": "CLOSED_BY_HEIGHT_RANKING" if basin["status"] == "PROVED_NO_INFINITE_REPEAT" else "UNKNOWN",
                }
            )

    sharp = loaded["sharp_return"]
    if sharp is not None:
        obligations.append(
            {
                "obligation_id": "sharp_q23_potential",
                "scope": sharp["scope"],
                "coverage": sharp["tower"],
                "transition_rule": sharp["R23"],
                "ancestor_descent": False,
                "scc_status": "CLOSED_BY_EXACT_POTENTIAL"
                if sharp["potential"]["status"] == "PROVED_POTENTIAL_DECREASE"
                else "UNKNOWN",
            }
        )

    cycle_mining = loaded["cycle_mining"]
    if cycle_mining is not None:
        for length_name, section in cycle_mining.get("sequence_reports", {}).items():
            for status, count in section.get("status_counts", {}).items():
                obligations.append(
                    {
                        "obligation_id": f"cycle_mining:{length_name}:{status}",
                        "scope": "P6 return-map SCC cycle diagnostics",
                        "coverage": {"sequence_count": count},
                        "transition_rule": status,
                        "ancestor_descent": False,
                        "scc_status": "CLOSED_BY_HEIGHT_RANKING"
                        if status == "PROVED_HEIGHT_DECREASE_ON_REPEAT"
                        else "UNKNOWN",
                    }
                )

    strata = loaded["frontier_strata"]
    if strata is not None:
        for row in strata.get("top_unresolved_buckets", [])[:20]:
            obligations.append(
                {
                    "obligation_id": f"unresolved_bucket:t={row['t']}:a={row['a']}:h={row['h']}",
                    "scope": "top unresolved P6 burst stratum",
                    "coverage": row,
                    "transition_rule": "not yet lifted to infinite theorem",
                    "ancestor_descent": False,
                    "scc_status": "NEEDS_SPLIT",
                }
            )

    status_counts = Counter(row["scc_status"] for row in obligations)
    unknownish = status_counts["UNKNOWN"] + status_counts["NEEDS_SPLIT"]
    return {
        "scope": "P6 proof obligations",
        "final_status_set": sorted(FINAL_STATUSES),
        "loaded_sources": {name: payload is not None for name, payload in loaded.items()},
        "obligation_count": len(obligations),
        "status_counts": dict(status_counts),
        "open_obligation_count": unknownish,
        "closed_obligation_count": len(obligations) - unknownish,
        "proof_status": "PASS" if unknownish == 0 else "INCOMPLETE_OPEN_OBLIGATIONS",
        "obligations": obligations,
    }


def write_proof_obligations_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# P6 Proof Obligations",
        "",
        f"- proof status: `{report['proof_status']}`",
        f"- obligations: `{report['obligation_count']}`",
        f"- closed obligations: `{report['closed_obligation_count']}`",
        f"- open obligations: `{report['open_obligation_count']}`",
        f"- status counts: `{report['status_counts']}`",
        "",
        "| obligation | coverage | transition rule | ancestor descent? | SCC status |",
        "|---|---:|---|---:|---|",
    ]
    for row in report["obligations"]:
        coverage = row.get("coverage")
        if isinstance(coverage, dict):
            count = coverage.get("cube_count") or coverage.get("sequence_count") or coverage.get("count_unknown") or coverage.get("residual_unknown_q_classes") or ""
        else:
            count = ""
        lines.append(
            f"| `{row['obligation_id']}` | `{count}` | `{row['transition_rule']}` | "
            f"`{row['ancestor_descent']}` | `{row['scc_status']}` |"
        )
    lines.append("")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build proof obligation report.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_proof_obligations_report()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_proof_obligations_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "proof_status": report["proof_status"],
            "status_counts": report["status_counts"],
        }
    )


if __name__ == "__main__":
    main()
