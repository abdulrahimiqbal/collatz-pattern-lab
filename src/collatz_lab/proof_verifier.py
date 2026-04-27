"""Final proof-object assembly and strict verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_schema import CLOSED_STATUSES


REQUIRED_KEYS = {
    "theorem",
    "coverage",
    "states",
    "transitions",
    "scc_rankings",
    "ancestor_descent_certificates",
    "finite_exceptions",
    "unknown_obligations",
    "verifier_status",
}


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def verify_proof_object(proof: dict[str, Any]) -> dict[str, Any]:
    """Strictly verify whether a canonical proof object proves Collatz descent."""

    errors: list[str] = []
    missing = sorted(REQUIRED_KEYS - set(proof))
    if missing:
        errors.append(f"missing required keys: {missing}")
    unknowns = proof.get("unknown_obligations", [])
    if unknowns:
        errors.append(f"unknown obligations remain: {len(unknowns)}")
    coverage = proof.get("coverage", {})
    if coverage.get("status") != "UNIVERSAL_PARENT_STATES":
        errors.append("coverage is not universal over all parent states P_a")
    for row in proof.get("transitions", []):
        status = row.get("status", "UNKNOWN")
        if status not in CLOSED_STATUSES and status != "PROVED_TRANSITION_ONLY":
            errors.append(f"transition {row.get('transition_id')} is not closed: {status}")
    for row in proof.get("scc_rankings", []):
        status = row.get("status", "UNKNOWN")
        if status not in CLOSED_STATUSES:
            errors.append(f"SCC ranking {row.get('scc_id', row.get('scc'))} is not closed: {status}")
    for row in proof.get("ancestor_descent_certificates", []):
        status = row.get("status", "")
        if status not in {"PROVED_INFINITE_ANCESTOR_DESCENT", "CLOSED_BY_ANCESTOR_DESCENT"}:
            errors.append(f"ancestor certificate {row.get('certificate_id', row.get('claim'))} is not exact: {status}")
    return {
        "verifier_status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "unknown_count": len(unknowns),
    }


def build_collatz_descent_theorem_candidate(
    proof_obligations: dict[str, Any] | None = None,
    proof_graph: dict[str, Any] | None = None,
    parent_state_system: dict[str, Any] | None = None,
    scc_rankings: dict[str, Any] | None = None,
    valuation_closure: dict[str, Any] | None = None,
    falsifier: dict[str, Any] | None = None,
    global_obligations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the canonical theorem candidate from current reports."""

    unknowns: list[dict[str, Any]] = [
        {
            "obligation_id": "universal_parent_state_coverage",
            "status": "UNKNOWN",
            "reason": "current parent-state report is finite-depth and finite-a only",
        }
    ]
    certs: list[dict[str, Any]] = [
        {
            "certificate_id": "P6_q9_mod16",
            "status": "PROVED_INFINITE_ANCESTOR_DESCENT",
            "claim": "n=64*q-1 and q == 9 mod 16 implies C^16(n)<n",
        }
    ]
    rankings: list[dict[str, Any]] = []
    states: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []

    if proof_obligations is not None and proof_graph is None:
        for row in proof_obligations.get("obligations", []):
            if row.get("scc_status") not in CLOSED_STATUSES:
                unknowns.append(row)
    if proof_graph is not None:
        for node_id in proof_graph.get("open", []):
            node = proof_graph.get("nodes", {}).get(node_id, {})
            unknowns.append(
                {
                    "obligation_id": node_id,
                    "status": node.get("status", "UNKNOWN"),
                    "scope": node.get("scope", "persistent proof graph"),
                    "coverage": node.get("coverage", {}),
                    "reason": "persistent proof graph node remains open",
                }
            )
    if global_obligations is not None:
        for row in global_obligations.get("minimal_blocking_set", []):
            unknowns.append(
                {
                    **row,
                    "reason": "global parent-state obligation remains open",
                }
            )
    if parent_state_system is not None:
        for a in range(int(parent_state_system.get("a_min", 1)), int(parent_state_system.get("a_max", 0)) + 1):
            states.append({"state_id": f"P_{a}", "kind": "parent_state", "parameters": {"a": a}})
        for row in parent_state_system.get("transition_counts", []):
            transitions.append(
                {
                    "transition_id": row["transition"],
                    "source_state": row["transition"].split("->")[0],
                    "target_state": row["transition"].split("->")[1],
                    "status": "PROVED_TRANSITION_ONLY",
                    "count": row["count"],
                    "scope": "finite-depth diagnostic count, not universal closure",
                }
            )
    if scc_rankings is not None:
        rankings.extend(scc_rankings.get("rankings", []))
        if scc_rankings.get("open_scc_count", 0):
            unknowns.append(
                {
                    "obligation_id": "open_symbolic_sccs",
                    "status": "UNKNOWN",
                    "count": scc_rankings.get("open_scc_count"),
                }
            )

    coverage = {
        "status": "FINITE_PARENT_STATE_DIAGNOSTIC",
        "evens": "C(n)=n/2 gives immediate descent for even n>2",
        "odds": "Every odd n can be written as P_a, but current report covers only sampled finite a/r-depth.",
    }
    if global_obligations is not None:
        coverage = dict(global_obligations.get("coverage", coverage))

    proof = {
        "theorem": "forall n > 1 exists k >= 1 such that C^k(n) < n",
        "coverage": coverage,
        "states": states,
        "transitions": transitions,
        "scc_rankings": rankings,
        "ancestor_descent_certificates": certs,
        "finite_exceptions": [],
        "unknown_obligations": unknowns,
        "minimal_blocking_set": _minimal_blocking_set(unknowns),
        "supporting_reports": {
            "proof_obligations_loaded": proof_obligations is not None,
            "proof_graph_loaded": proof_graph is not None,
            "parent_state_system_loaded": parent_state_system is not None,
            "scc_rankings_loaded": scc_rankings is not None,
            "valuation_closure_loaded": valuation_closure is not None,
            "falsifier_loaded": falsifier is not None,
            "global_obligations_loaded": global_obligations is not None,
        },
        "verifier_status": "PENDING",
    }
    verification = verify_proof_object(proof)
    proof["verifier_status"] = verification["verifier_status"]
    proof["verification"] = verification
    return proof


def _minimal_blocking_set(unknowns: list[dict[str, Any]], limit: int = 30) -> list[dict[str, Any]]:
    """Return a deterministic high-measure blocking set summary."""

    def weight(row: dict[str, Any]) -> int:
        coverage = row.get("coverage", {})
        if not isinstance(coverage, dict):
            return 0
        for key in (
            "residual_unknown_q_classes",
            "count_unknown",
            "cube_count",
            "sequence_count",
            "residue_count",
            "row_count",
        ):
            value = coverage.get(key)
            if isinstance(value, int):
                return value
        return 0

    return sorted(unknowns, key=lambda row: (-weight(row), str(row.get("obligation_id", ""))))[:limit]


def write_proof_markdown(proof: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Collatz Descent Theorem Candidate",
        "",
        f"- verifier status: `{proof['verifier_status']}`",
        f"- theorem: `{proof['theorem']}`",
        f"- states: `{len(proof['states'])}`",
        f"- transitions: `{len(proof['transitions'])}`",
        f"- ancestor descent certificates: `{len(proof['ancestor_descent_certificates'])}`",
        f"- unknown obligations: `{len(proof['unknown_obligations'])}`",
        "",
        "This is not a proof unless `verifier_status` is `PASS`.",
        "",
        "## Verification Errors",
        "",
    ]
    for error in proof.get("verification", {}).get("errors", []):
        lines.append(f"- {error}")
    lines.extend(["", "## Known Exact Ancestor Descent Certificates", ""])
    for cert in proof["ancestor_descent_certificates"]:
        lines.append(f"- `{cert['status']}`: {cert['claim']}")
    lines.extend(["", "## First Unknown Obligations", ""])
    for row in proof.get("minimal_blocking_set", proof["unknown_obligations"][:30]):
        lines.append(f"- `{row.get('obligation_id')}`: `{row.get('status', row.get('scc_status'))}`")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assemble and verify canonical Collatz descent proof object.")
    parser.add_argument("--proof-obligations", default="reports/proof_obligations_parent_P6.json")
    parser.add_argument("--proof-graph", default=None)
    parser.add_argument("--parent-state-system", default="reports/parent_state_system_a1_a20_r7.json")
    parser.add_argument("--scc-rankings", default="reports/scc_ranker_smoke.json")
    parser.add_argument("--valuation-closure", default="reports/valuation_closure_q23.json")
    parser.add_argument("--falsifier", default="reports/falsifier_report.json")
    parser.add_argument("--global-obligations", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    proof = build_collatz_descent_theorem_candidate(
        proof_obligations=_load_optional(Path(args.proof_obligations)),
        proof_graph=_load_optional(Path(args.proof_graph)) if args.proof_graph else None,
        parent_state_system=_load_optional(Path(args.parent_state_system)),
        scc_rankings=_load_optional(Path(args.scc_rankings)),
        valuation_closure=_load_optional(Path(args.valuation_closure)),
        falsifier=_load_optional(Path(args.falsifier)),
        global_obligations=_load_optional(Path(args.global_obligations)) if args.global_obligations else None,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_proof_markdown(proof, md_out)
    Console().print({"out": str(out), "markdown": str(md_out), "verifier_status": proof["verifier_status"]})


if __name__ == "__main__":
    main()
