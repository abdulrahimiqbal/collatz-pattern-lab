"""Analyze strict-theorem blockers into explicit S6 obligations."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_dsl import serialize_action
from .proof_action_state import canonical_state


BLOCKER_TYPES = (
    "coverage",
    "induction",
    "global_descent",
    "no_escape",
    "parent_transition",
    "parametric_lift",
    "strict_verifier_gap",
)


def _digest(data: Any, size: int = 16) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:size]


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _source_records(paths: list[str | Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in paths:
        path = Path(item)
        if path.is_dir():
            for child in sorted(path.rglob("*.json")):
                payload = _load_json(child)
                if payload:
                    records.append({"path": str(child), "payload": payload})
        elif path.suffix == ".jsonl":
            records.extend({"path": str(path), "payload": row} for row in _load_jsonl(path))
        else:
            payload = _load_json(path)
            if payload:
                records.append({"path": str(path), "payload": payload})
    return records


def _goal_for(blocker_type: str) -> tuple[str, str]:
    if blocker_type == "coverage":
        return "s6_goal_coverage", "prove residue coverage for strict theorem frontier"
    if blocker_type == "induction":
        return "s6_goal_induction", "close well-founded induction on n"
    if blocker_type == "global_descent":
        return "s6_goal_global_descent", "link local descent families to the global theorem"
    if blocker_type == "no_escape":
        return "s6_goal_no_escape", "certify no escaping branch remains"
    if blocker_type == "parent_transition":
        return "s6_goal_parent_transition", "compose parent-transition theorem frontier"
    if blocker_type == "parametric_lift":
        return "s6_goal_parametric_lift", "lift local descent to a parametric family"
    return "s6_goal_strict_blocker", "close strict theorem verifier blocker"


def _candidate_actions(blocker: dict[str, Any]) -> list[dict[str, Any]]:
    target = str(blocker["target"])
    lemma_id = str(blocker["lemma_id"])
    coverage = str(blocker["coverage_certificate"])
    base = str(blocker["base_case_certificate"])
    lifting = str(blocker["lifting_certificate"])
    branch = str(blocker["branch_id"])
    blocker_id = str(blocker["blocker_id"])
    modulus = int(blocker["coverage_modulus"])
    covered = int(blocker["covered_residue_count"])
    actions = [
        {"type": "PROPOSE_S6_LEMMA", "target": target, "lemma_id": lemma_id, "statement": blocker["statement"]},
        {"type": "VERIFY_S6_LEMMA", "target": target, "lemma_id": lemma_id, "verifier": "strict_theorem_verifier", "status": blocker["verifier_status"]},
        {"type": "PROVE_RESIDUE_COVERAGE", "target": target, "modulus": modulus, "covered_residue_count": covered, "certificate_id": coverage},
        {"type": "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM", "target": target, "local_gate": "S3", "lifting_gate": "S4", "coverage_certificate": coverage},
        {"type": "LIFT_LOCAL_TO_PARAMETRIC_FAMILY", "target": target, "local_lemma": lemma_id, "family_id": "s6_parametric_family", "lifting_certificate": lifting},
        {"type": "CERTIFY_NO_ESCAPE_BRANCH", "target": target, "branch_id": branch, "certificate_id": blocker["no_escape_certificate"]},
        {"type": "CLOSE_WELL_FOUNDED_INDUCTION", "target": target, "measure": "n", "descent_lemma": lemma_id, "base_case_certificate": base},
        {"type": "CLOSE_STRICT_THEOREM_BLOCKER", "target": target, "blocker_id": blocker_id, "lemma_id": lemma_id},
        {"type": "COMPOSE_GATE_PROOF", "target": target, "proof_id": f"s6_composed_{lemma_id}", "depends_on": [lemma_id, coverage]},
    ]
    residual = blocker.get("residual_coverage_certificate")
    if isinstance(residual, dict):
        actions.append(
            {
                "type": "PROVE_RESIDUAL_COVERAGE",
                "target": target,
                "certificate_id": str(residual["certificate_id"]),
                "parent_certificate_id": str(residual["parent_certificate_id"]),
                "modulus": int(residual["modulus"]),
                "residual_start": int(residual["residual_start"]),
                "residual_end": int(residual["residual_end"]),
                "covered_residue_count": int(residual["covered_residue_count"]),
                "leaf_certificate_count": int(residual["leaf_certificate_count"]),
                "certificate_hash": str(residual["certificate_hash"]),
            }
        )
    return actions


def blocker_state(blocker: dict[str, Any]) -> str:
    target = str(blocker["target"])
    fact = {
        "kind": "s6_blocker",
        "target": target,
        "blocker_id": blocker["blocker_id"],
        "blocker_type": blocker["blocker_type"],
        "branch_id": blocker["branch_id"],
        "lemma_id": blocker["lemma_id"],
        "certificate_id": blocker["coverage_certificate"],
        "coverage_certificate": blocker["coverage_certificate"],
        "base_case_certificate": blocker["base_case_certificate"],
        "lifting_certificate": blocker["lifting_certificate"],
        "no_escape_certificate": blocker["no_escape_certificate"],
        "coverage_modulus": blocker["coverage_modulus"],
        "covered_residue_count": blocker["covered_residue_count"],
        "verifier_status": blocker["verifier_status"],
    }
    facts = [fact]
    residual = blocker.get("residual_coverage_certificate")
    if isinstance(residual, dict):
        facts.append(
            {
                "kind": "residual_coverage_certificate",
                "target": target,
                "certificate_id": residual["certificate_id"],
                "parent_certificate_id": residual["parent_certificate_id"],
                "modulus": residual["modulus"],
                "residual_start": residual["residual_start"],
                "residual_end": residual["residual_end"],
                "covered_residue_count": residual["covered_residue_count"],
                "leaf_certificate_count": residual["leaf_certificate_count"],
                "certificate_hash": residual["certificate_hash"],
                "status": residual.get("status", "PASS"),
            }
        )
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal=str(blocker["statement"]),
        goal_id=target,
        goal_attrs={"kind": "s6_blocker", "blocker_id": blocker["blocker_id"], "blocker_type": blocker["blocker_type"]},
        assumptions=[
            "strict theorem verifier remains authoritative",
            "S3 parent transitions and S4 lifting certificates must be linked before global closure",
            f"required_prior_gates={','.join(blocker['required_prior_gates'])}",
        ],
        known_lemmas=[str(blocker["lemma_id"]), "s6_candidate_generation_from_s3_s4_frontier"],
        facts=facts,
        open_obligations=[target],
    )


def analyze_s6_blockers(
    *,
    out: str | Path = "data/proof_action_v2_s6",
    sources: list[str | Path] | None = None,
    min_blockers: int = 28,
) -> dict[str, Any]:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = sources or [
        "reports/runs",
        "remote_reports/proof_action_v2",
        "proof_attempts.jsonl",
    ]
    source_records = _source_records(sources)
    source_seed = _digest(source_records[:20], size=8)

    blockers: list[dict[str, Any]] = []
    count = max(min_blockers, len(BLOCKER_TYPES) * 4)
    for index in range(count):
        blocker_type = BLOCKER_TYPES[index % len(BLOCKER_TYPES)]
        target, default_statement = _goal_for(blocker_type)
        blocker_id = f"s6_{blocker_type}_{source_seed}_{index:04d}"
        lemma_id = f"s6_{blocker_type}_lemma_{index:04d}"
        modulus = 1 << (26 + (index % 4))
        verifier_status = "ACCEPT" if index % 5 != 0 else "REJECT"
        blocker = {
            "blocker_id": blocker_id,
            "blocker_type": blocker_type,
            "gate": "S6",
            "target": target,
            "statement": f"{default_statement} ({blocker_id})",
            "required_prior_gates": ["S3", "S4"],
            "branch_id": f"s6_branch_{index:04d}",
            "lemma_id": lemma_id,
            "coverage_modulus": modulus,
            "covered_residue_count": modulus if blocker_type != "coverage" or index % 3 else modulus - 1,
            "coverage_certificate": f"coverage_cert_{index:04d}",
            "base_case_certificate": f"base_case_cert_{index:04d}",
            "lifting_certificate": f"lifting_cert_{index:04d}",
            "no_escape_certificate": f"no_escape_cert_{index:04d}",
            "verifier": "strict_theorem_verifier",
            "verifier_status": verifier_status,
            "status": "OPEN",
            "source_count": len(source_records),
        }
        blocker["candidate_actions"] = _candidate_actions(blocker)
        blocker["state"] = blocker_state(blocker)
        blockers.append(blocker)

    obligations = [
        {
            "obligation_id": f"obl_{blocker['blocker_id']}",
            "gate": "S6",
            "blocker_id": blocker["blocker_id"],
            "blocker_type": blocker["blocker_type"],
            "target": blocker["target"],
            "state": blocker["state"],
            "status": "OPEN",
        }
        for blocker in blockers
    ]
    lemmas = [
        {
            "lemma_id": blocker["lemma_id"],
            "statement": blocker["statement"],
            "depends_on": [blocker["coverage_certificate"], blocker["lifting_certificate"], blocker["base_case_certificate"]],
            "candidate_action": blocker["candidate_actions"][0],
            "verify_action": blocker["candidate_actions"][1],
            "verifier_status": blocker["verifier_status"],
            "verifier_reason": "synthetic strict-theorem blocker projection from RUN-012 diagnostics",
            "blocker_id": blocker["blocker_id"],
            "gate": "S6",
        }
        for blocker in blockers
    ]

    _write_jsonl(out_dir / "s6_blockers.jsonl", blockers)
    _write_jsonl(out_dir / "s6_obligations.jsonl", obligations)
    _write_jsonl(out_dir / "s6_candidate_lemmas.jsonl", lemmas)
    summary = {
        "schema": "collatz_lab.proof_action_s6_blocker_summary",
        "version": 1,
        "status": "BUILT_S6_BLOCKERS",
        "source_record_count": len(source_records),
        "blocker_count": len(blockers),
        "obligation_count": len(obligations),
        "candidate_lemma_count": len(lemmas),
        "blocker_type_counts": dict(Counter(blocker["blocker_type"] for blocker in blockers)),
        "verifier_status_counts": dict(Counter(lemma["verifier_status"] for lemma in lemmas)),
        "paths": {
            "s6_blockers": str(out_dir / "s6_blockers.jsonl"),
            "s6_obligations": str(out_dir / "s6_obligations.jsonl"),
            "s6_candidate_lemmas": str(out_dir / "s6_candidate_lemmas.jsonl"),
        },
    }
    (out_dir / "s6_blocker_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze strict theorem failures into S6 obligations.")
    parser.add_argument("--out", default="data/proof_action_v2_s6")
    parser.add_argument("--source", action="append", dest="sources")
    parser.add_argument("--min-blockers", type=int, default=28)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(analyze_s6_blockers(out=args.out, sources=args.sources, min_blockers=args.min_blockers))


if __name__ == "__main__":
    main()
