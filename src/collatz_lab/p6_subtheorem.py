"""Assemble the current P6 descent subtheorem candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_schema import CLOSED_STATUSES


def _load_optional(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _open_from_obligations(report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if report is None:
        return []
    return [
        row
        for row in report.get("obligations", [])
        if row.get("scc_status") not in CLOSED_STATUSES
    ]


def _open_from_graph(graph: dict[str, Any] | None) -> list[dict[str, Any]]:
    if graph is None:
        return []
    rows = []
    for node_id in graph.get("open", []):
        node = graph.get("nodes", {}).get(node_id, {})
        rows.append(
            {
                "obligation_id": node_id,
                "status": node.get("status", "UNKNOWN"),
                "scope": node.get("scope", ""),
                "coverage": node.get("coverage", {}),
            }
        )
    return rows


def build_p6_subtheorem_report(
    proof_obligations: dict[str, Any] | None,
    proof_graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the strict P6 acceptance-gate report."""

    open_obligations = _open_from_obligations(proof_obligations)
    graph_open = _open_from_graph(proof_graph)
    graph_available = proof_graph is not None
    open_count = len(graph_open) if graph_available else len(open_obligations)
    blockers = graph_open if graph_available else open_obligations
    status = "PASS" if open_count == 0 else "INCOMPLETE_OPEN_OBLIGATIONS"
    return {
        "scope": "P6 parent subsystem descent subtheorem",
        "theorem": "For all q>0 in the P6 parent n=64q-1, the system proves ancestor descent or controlled transition.",
        "status": status,
        "verifier_status": "PASS" if status == "PASS" else "FAIL",
        "proof_bar": [
            "CLOSED_BY_ANCESTOR_DESCENT",
            "CLOSED_BY_TRANSITION_TO_CLOSED_STATE",
            "CLOSED_BY_HEIGHT_RANKING",
            "CLOSED_BY_EXACT_POTENTIAL",
        ],
        "proof_obligations_loaded": proof_obligations is not None,
        "proof_graph_loaded": graph_available,
        "initial_open_obligations": None if proof_obligations is None else proof_obligations.get("open_obligation_count"),
        "graph_open_obligations": None if proof_graph is None else len(proof_graph.get("open", [])),
        "open_obligation_count": open_count,
        "closed_obligation_count": None
        if proof_graph is None
        else len(proof_graph.get("closed", [])),
        "blocking_set": blockers[:100],
        "known_exact_highlights": [
            {
                "status": "CLOSED_BY_ANCESTOR_DESCENT",
                "claim": "q == 9 mod 16 in n=64q-1 descends by C^16(n)<n",
            },
            {
                "status": "CLOSED_BY_HEIGHT_RANKING",
                "claim": "q == 23 mod 128 has R23(q)=(729q+1)/128 and v2(601R23(q)+1)=v2(601q+1)-7",
            },
        ],
    }


def write_p6_subtheorem_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# P6 Descent Subtheorem Candidate",
        "",
        f"- verifier status: `{report['verifier_status']}`",
        f"- status: `{report['status']}`",
        f"- open obligations: `{report['open_obligation_count']}`",
        "",
        "This is accepted only when every P6 branch is closed by ancestor descent, transition to a closed state, height ranking, or exact potential.",
        "",
        "## Known Exact Highlights",
        "",
    ]
    for row in report["known_exact_highlights"]:
        lines.append(f"- `{row['status']}`: {row['claim']}")
    lines.extend(["", "## Blocking Set", ""])
    for row in report["blocking_set"][:80]:
        lines.append(f"- `{row.get('obligation_id')}`: `{row.get('status', row.get('scc_status'))}`")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the P6 descent subtheorem candidate report.")
    parser.add_argument("--proof-obligations", default="reports/proof_obligations_parent_P6.json")
    parser.add_argument("--proof-graph", default="reports/proof_graph_latest.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_p6_subtheorem_report(
        _load_optional(args.proof_obligations),
        _load_optional(args.proof_graph),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_p6_subtheorem_markdown(report, md_out)
    Console().print({"out": str(out), "status": report["status"], "open": report["open_obligation_count"]})


if __name__ == "__main__":
    main()
