"""Generate verifier-checkable S6 candidate lemmas from blockers."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_decode import verify_action_for_state
from .proof_action_dsl import serialize_action
from .proof_action_s6_analyzer import analyze_s6_blockers


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def generate_s6_candidate_lemmas(
    *,
    blockers_path: str | Path = "data/proof_action_v2_s6/s6_blockers.jsonl",
    out: str | Path = "data/proof_action_v2_s6/s6_candidate_lemmas.jsonl",
    min_lemmas: int = 10,
) -> dict[str, Any]:
    blockers = _load_jsonl(blockers_path)
    if len(blockers) < min_lemmas:
        analyze_s6_blockers(out=Path(blockers_path).parent, min_blockers=max(min_lemmas, 28))
        blockers = _load_jsonl(blockers_path)

    rows: list[dict[str, Any]] = []
    for index, blocker in enumerate(blockers[: max(min_lemmas, len(blockers))]):
        state = str(blocker["state"])
        propose = {
            "type": "PROPOSE_S6_LEMMA",
            "target": str(blocker["target"]),
            "lemma_id": str(blocker["lemma_id"]),
            "statement": str(blocker["statement"]),
        }
        verify = {
            "type": "VERIFY_S6_LEMMA",
            "target": str(blocker["target"]),
            "lemma_id": str(blocker["lemma_id"]),
            "verifier": "strict_theorem_verifier",
            "status": str(blocker.get("verifier_status", "PENDING")),
        }
        propose_check = verify_action_for_state(propose, state)
        verify_check = verify_action_for_state(verify, state)
        rows.append(
            {
                "schema": "collatz_lab.proof_action_s6_candidate_lemma",
                "version": 1,
                "lemma_id": str(blocker["lemma_id"]),
                "statement": str(blocker["statement"]),
                "depends_on": [
                    str(blocker["coverage_certificate"]),
                    str(blocker["lifting_certificate"]),
                    str(blocker["base_case_certificate"]),
                ],
                "candidate_action": propose,
                "candidate_action_text": serialize_action(propose),
                "verify_action": verify,
                "verify_action_text": serialize_action(verify),
                "propose_verifier_status": "ACCEPT" if propose_check.accepted else "REJECT",
                "verifier_status": "ACCEPT" if verify_check.accepted else "REJECT",
                "verifier_reason": verify_check.reason,
                "blocker_id": blocker["blocker_id"],
                "blocker_type": blocker["blocker_type"],
                "gate": "S6",
                "state": state,
                "rank": index + 1,
            }
        )

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl(out_path, rows)
    summary = {
        "schema": "collatz_lab.proof_action_s6_candidate_lemma_summary",
        "version": 1,
        "candidate_lemma_count": len(rows),
        "verifier_status_counts": dict(Counter(row["verifier_status"] for row in rows)),
        "blocker_type_counts": dict(Counter(row["blocker_type"] for row in rows)),
        "path": str(out_path),
    }
    (out_path.parent / "s6_candidate_lemma_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate S6 candidate lemmas from blocker obligations.")
    parser.add_argument("--blockers-path", default="data/proof_action_v2_s6/s6_blockers.jsonl")
    parser.add_argument("--out", default="data/proof_action_v2_s6/s6_candidate_lemmas.jsonl")
    parser.add_argument("--min-lemmas", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    Console().print(generate_s6_candidate_lemmas(blockers_path=args.blockers_path, out=args.out, min_lemmas=args.min_lemmas))


if __name__ == "__main__":
    main()
