"""RUN-017 repair pass for rejected S6 lemmas from theorem composition.

RUN-017 is deliberately not a training run.  It reads the RUN-016 fixed-point
report, classifies rejected S6 lemmas, emits exact residual/atomic obligations,
rewrites only repairable S6 blocker inputs, and reruns the theorem composer.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_decode import verify_action_for_state
from .proof_action_dsl import serialize_action
from .proof_action_s6_analyzer import _candidate_actions as _s6_candidate_actions
from .proof_action_s6_analyzer import blocker_state
from .proof_action_theorem_composer import run_theorem_composer
from .utils import load_yaml


ATOMIC_S6_ACTION_TYPES = {
    "PROVE_RESIDUE_COVERAGE",
    "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM",
    "LIFT_LOCAL_TO_PARAMETRIC_FAMILY",
    "CERTIFY_NO_ESCAPE_BRANCH",
    "CLOSE_WELL_FOUNDED_INDUCTION",
    "COMPOSE_GATE_PROOF",
}


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def rejected_s6_lemma_blockers(run016_report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in run016_report.get("minimal_blocker_report", [])
        if row.get("node_type") == "S6_LEMMA" and row.get("status") != "ACCEPTED"
    ]


def classify_s6_lemma_rejection(blocker_report: dict[str, Any], source_blocker: dict[str, Any] | None = None) -> str:
    last = blocker_report.get("last_rejection") if isinstance(blocker_report.get("last_rejection"), dict) else {}
    status = str(last.get("status", ""))
    reason = str(last.get("reason", ""))
    if source_blocker is not None:
        modulus = int(source_blocker.get("coverage_modulus", 0) or 0)
        covered = int(source_blocker.get("covered_residue_count", 0) or 0)
        if modulus > 0 and covered < modulus:
            return "partial_coverage"
    if status == "REJECT_INCOMPLETE_COVERAGE" or "partial" in reason.lower():
        return "partial_coverage"
    if status == "REJECT_STRICT_VERIFIER":
        return "circular_strict_verifier_dependency"
    if status == "REJECT_S6_LEMMA":
        return "explicit_lemma_rejection"
    return "explicit_lemma_rejection"


def residual_coverage_obligation(blocker: dict[str, Any]) -> dict[str, Any] | None:
    modulus = int(blocker.get("coverage_modulus", 0) or 0)
    covered = int(blocker.get("covered_residue_count", 0) or 0)
    if modulus <= 0 or covered >= modulus:
        return None
    certificate_id = str(blocker["coverage_certificate"])
    return {
        "obligation_id": f"residual_coverage:{certificate_id}:{covered}:{modulus}",
        "kind": "RESIDUAL_COVERAGE_CERTIFICATE",
        "source_blocker_id": blocker["blocker_id"],
        "lemma_id": blocker["lemma_id"],
        "coverage_certificate": certificate_id,
        "required_domain": {"modulus": modulus, "residue_start": 0, "residue_end_exclusive": modulus},
        "covered_domain": {
            "modulus": modulus,
            "residue_count": covered,
            "assumed_residue_start": 0,
            "assumed_residue_end_exclusive": covered,
        },
        "residual_domain": {
            "modulus": modulus,
            "residue_start": covered,
            "residue_end_exclusive": modulus,
            "residue_count": modulus - covered,
        },
        "missing_certificate_id": f"{certificate_id}:residual:{covered}:{modulus}",
    }


def atomic_sublemma_checks(blocker: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    state = str(blocker["state"])
    for action in blocker.get("candidate_actions") or []:
        if str(action.get("type", "")) not in ATOMIC_S6_ACTION_TYPES:
            continue
        check = verify_action_for_state(action, state)
        rows.append(
            {
                "source_blocker_id": blocker["blocker_id"],
                "lemma_id": blocker["lemma_id"],
                "atom_id": f"{blocker['lemma_id']}:{action['type']}",
                "action_type": action["type"],
                "action_text": serialize_action(action),
                "accepted": bool(check.accepted),
                "verifier_check": check.to_dict(),
            }
        )
    return rows


def _source_blocker_map(s6_dir: str | Path) -> dict[str, dict[str, Any]]:
    blockers = _load_jsonl(Path(s6_dir) / "s6_blockers.jsonl")
    out: dict[str, dict[str, Any]] = {}
    for blocker in blockers:
        out[str(blocker.get("lemma_id"))] = blocker
        out[str(blocker.get("blocker_id"))] = blocker
    return out


def _mark_blocker_repaired(blocker: dict[str, Any], repair: dict[str, Any]) -> dict[str, Any]:
    repaired = dict(blocker)
    repaired["verifier_status"] = "ACCEPT"
    repaired["repair_status"] = "REPAIRED_BY_RUN_017_ATOMIC_S6_CERTIFICATES"
    repaired["repair"] = repair
    repaired["candidate_actions"] = _s6_candidate_actions(repaired)
    repaired["state"] = blocker_state(repaired)
    return repaired


def repair_s6_blockers(
    *,
    run016_report_path: str | Path,
    s6_dir: str | Path,
    out_dir: str | Path,
) -> dict[str, Any]:
    run016 = _load_json(run016_report_path)
    source_blockers = _load_jsonl(Path(s6_dir) / "s6_blockers.jsonl")
    blocker_by_key = _source_blocker_map(s6_dir)
    rejected = rejected_s6_lemma_blockers(run016)

    classifications: list[dict[str, Any]] = []
    residuals: list[dict[str, Any]] = []
    atoms: list[dict[str, Any]] = []
    repaired_by_lemma: dict[str, dict[str, Any]] = {}
    root_missing_certificates: list[dict[str, Any]] = []

    for blocker_report in rejected:
        lemma_id = str((blocker_report.get("evidence") or {}).get("lemma_id") or blocker_report["node_id"].split(":", 1)[-1])
        source = blocker_by_key.get(lemma_id)
        if source is None:
            root_missing_certificates.append(
                {
                    "kind": "MISSING_SOURCE_S6_BLOCKER",
                    "lemma_id": lemma_id,
                    "node_id": blocker_report.get("node_id"),
                }
            )
            continue

        classification = classify_s6_lemma_rejection(blocker_report, source)
        row = {
            "node_id": blocker_report.get("node_id"),
            "lemma_id": lemma_id,
            "source_blocker_id": source["blocker_id"],
            "blocker_type": source.get("blocker_type"),
            "classification": classification,
            "last_rejection": blocker_report.get("last_rejection"),
        }
        classifications.append(row)

        if classification == "partial_coverage":
            residual = residual_coverage_obligation(source)
            if residual is not None:
                residuals.append(residual)
                root_missing_certificates.append(
                    {
                        "kind": "RESIDUAL_COVERAGE_CERTIFICATE",
                        "lemma_id": lemma_id,
                        "source_blocker_id": source["blocker_id"],
                        "missing_certificate_id": residual["missing_certificate_id"],
                        "residual_domain": residual["residual_domain"],
                    }
                )
            continue

        atom_rows = atomic_sublemma_checks(source)
        atoms.extend(atom_rows)
        accepted_types = {atom["action_type"] for atom in atom_rows if atom["accepted"]}
        rejected_atoms = [atom for atom in atom_rows if not atom["accepted"]]
        missing_types = sorted(ATOMIC_S6_ACTION_TYPES - accepted_types)
        if not missing_types and not rejected_atoms:
            repaired_by_lemma[lemma_id] = _mark_blocker_repaired(
                source,
                {
                    "classification": classification,
                    "accepted_atom_action_types": sorted(accepted_types),
                    "accepted_atom_count": len(atom_rows),
                },
            )
        else:
            for atom in rejected_atoms:
                root_missing_certificates.append(
                    {
                        "kind": "REJECTED_ATOMIC_S6_CERTIFICATE",
                        "lemma_id": lemma_id,
                        "source_blocker_id": source["blocker_id"],
                        "action_type": atom["action_type"],
                        "status": atom["verifier_check"]["status"],
                        "reason": atom["verifier_check"]["reason"],
                    }
                )
            for action_type in missing_types:
                root_missing_certificates.append(
                    {
                        "kind": "MISSING_ATOMIC_S6_CERTIFICATE",
                        "lemma_id": lemma_id,
                        "source_blocker_id": source["blocker_id"],
                        "action_type": action_type,
                    }
                )

    repaired_blockers: list[dict[str, Any]] = []
    for blocker in source_blockers:
        repaired_blockers.append(repaired_by_lemma.get(str(blocker.get("lemma_id")), blocker))

    out = Path(out_dir)
    repaired_s6_dir = out / "repaired_s6"
    repaired_s6_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(repaired_s6_dir / "s6_blockers.jsonl", repaired_blockers)
    _write_jsonl(out / "s6_lemma_rejection_classifications.jsonl", classifications)
    _write_jsonl(out / "s6_residual_coverage_obligations.jsonl", residuals)
    _write_jsonl(out / "s6_atomic_sublemmas.jsonl", atoms)
    _write_jsonl(out / "root_missing_certificates.jsonl", root_missing_certificates)

    repair_summary = {
        "schema": "collatz_lab.proof_action_s6_lemma_repair_summary",
        "version": 1,
        "run_id": "RUN-017-proof-action-v2-s6-lemma-repair",
        "run016_report_path": str(run016_report_path),
        "source_s6_dir": str(s6_dir),
        "repaired_s6_dir": str(repaired_s6_dir),
        "rejected_s6_lemma_count": len(rejected),
        "classification_counts": dict(Counter(row["classification"] for row in classifications)),
        "residual_coverage_obligation_count": len(residuals),
        "atomic_sublemma_count": len(atoms),
        "accepted_atomic_sublemma_count": sum(1 for atom in atoms if atom["accepted"]),
        "repaired_lemma_count": len(repaired_by_lemma),
        "root_missing_certificate_count": len(root_missing_certificates),
        "root_missing_certificates": root_missing_certificates,
        "artifacts": {
            "classifications": str(out / "s6_lemma_rejection_classifications.jsonl"),
            "residual_coverage_obligations": str(out / "s6_residual_coverage_obligations.jsonl"),
            "atomic_sublemmas": str(out / "s6_atomic_sublemmas.jsonl"),
            "root_missing_certificates": str(out / "root_missing_certificates.jsonl"),
            "repaired_s6_dir": str(repaired_s6_dir),
        },
    }
    (out / "s6_lemma_repair_report.json").write_text(json.dumps(repair_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return repair_summary


def _config(path: str | Path, *, out: str | None = None) -> dict[str, Any]:
    cfg = load_yaml(path)
    repair = cfg.get("repair", {})
    model = cfg.get("model", {})
    composer = cfg.get("composer", {})
    return {
        "config_path": str(path),
        "checkpoint": str(model.get("checkpoint") or cfg.get("evaluation", {}).get("checkpoint")),
        "frontier_dir": str(composer.get("frontier_eval_dir") or cfg.get("evaluation", {}).get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval"),
        "source_s6_dir": str(repair.get("source_s6_dir") or composer.get("s6_dir") or "data/proof_action_v2_s6"),
        "run016_report": str(repair.get("run016_report") or "reports/runs/RUN-016-proof-action-v2-theorem-composer/theorem_composition_report.json"),
        "out_dir": str(out or repair.get("out_dir") or "reports/runs/RUN-017-proof-action-v2-s6-lemma-repair"),
        "composer_config": str(repair.get("composer_config") or "configs/collatz_proof_action_v2_theorem_composer_run016.yaml"),
    }


def run_s6_lemma_repair(config_path: str | Path, *, out: str | None = None) -> dict[str, Any]:
    cfg = _config(config_path, out=out)
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    repair_summary = repair_s6_blockers(
        run016_report_path=cfg["run016_report"],
        s6_dir=cfg["source_s6_dir"],
        out_dir=out_dir,
    )
    composer_out = out_dir / "theorem_composer"
    composer_summary = run_theorem_composer(
        cfg["composer_config"],
        checkpoint=cfg["checkpoint"],
        frontier_dir=cfg["frontier_dir"],
        s6_dir=repair_summary["repaired_s6_dir"],
        out=str(composer_out),
    )
    final_root_missing = list(repair_summary["root_missing_certificates"])
    rooted_lemmas = {str(item.get("lemma_id", "")) for item in final_root_missing if item.get("lemma_id")}
    for blocker in composer_summary.get("minimal_blocker_report", []):
        if blocker.get("missing_kind") == "blocked_dependency":
            continue
        if blocker.get("node_type") == "S6_LEMMA":
            lemma_id = str((blocker.get("evidence") or {}).get("lemma_id") or "")
            if lemma_id in rooted_lemmas:
                continue
            final_root_missing.append(
                {
                    "kind": "UNREPAIRED_S6_LEMMA",
                    "node_id": blocker.get("node_id"),
                    "lemma_id": lemma_id,
                    "status": (blocker.get("last_rejection") or {}).get("status"),
                    "reason": (blocker.get("last_rejection") or {}).get("reason"),
                }
            )
    final_report = {
        "schema": "collatz_lab.run_result.s6_lemma_repair",
        "version": 1,
        "run_id": "RUN-017-proof-action-v2-s6-lemma-repair",
        "training_launched": False,
        "big_model_launched": False,
        "policy_checkpoint": cfg["checkpoint"],
        "repair_summary": repair_summary,
        "composer_summary": composer_summary,
        "strict_theorem_verifier_result": composer_summary["strict_theorem_verifier_result"],
        "proof_confidence_percent": composer_summary["proof_confidence_percent"],
        "status": "STRICT_VERIFIER_PASS" if composer_summary["strict_theorem_verifier_result"] == "PASS" else "MINIMAL_ROOT_MISSING_CERTIFICATES",
        "root_missing_certificates": final_root_missing,
        "root_missing_certificate_count": len(final_root_missing),
        "artifacts": {
            "s6_lemma_repair_report": str(out_dir / "s6_lemma_repair_report.json"),
            "theorem_composition_report": str(composer_out / "theorem_composition_report.json"),
            "root_missing_certificates": str(out_dir / "root_missing_certificates.jsonl"),
        },
    }
    (out_dir / "run_result.json").write_text(json.dumps(final_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return final_report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run RUN-017 S6 lemma repair and theorem recomposition.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    result = run_s6_lemma_repair(args.config, out=args.out)
    Console().print(
        {
            "status": result["status"],
            "strict_theorem_verifier_result": result["strict_theorem_verifier_result"],
            "root_missing_certificate_count": result["root_missing_certificate_count"],
            "run_result": str(Path(result["artifacts"]["s6_lemma_repair_report"]).parent / "run_result.json"),
        }
    )


if __name__ == "__main__":
    main()
