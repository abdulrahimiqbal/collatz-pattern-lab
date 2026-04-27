"""Evaluate a trained proof Transformer as a proof-attempt generator.

The proof Transformer emits text.  This module keeps the accounting strict:
generated text is parsed into recognizable proof actions/claims, those claims
are checked against existing exact artifacts, and proof confidence remains zero
unless the strict theorem verifier has already passed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import torch
from rich.console import Console

from .proof_attempt import (
    append_proof_attempt_record_to_logs,
    build_proof_attempt,
    build_proof_attempt_record,
    evaluate_proof_attempt,
    write_evaluation_markdown,
    write_proof_attempt_markdown,
)
from .proof_transformer import generate_proof_text, load_proof_transformer_checkpoint


PROOF_TRANSFORMER_EVAL_SCHEMA = "collatz_lab.proof_transformer_evaluation"
MODEL_PROOF_PROPOSAL_SCHEMA = "collatz_lab.proof_transformer_model_proof_proposal"
MODEL_PROOF_VERIFICATION_SCHEMA = "collatz_lab.proof_transformer_model_proof_verification"

KNOWN_ACTIONS = [
    "PROPOSE_PROOF_DSL",
    "PROPOSE_MIXED_MODULUS_STATE",
    "TRY_MIXED_MODULUS_DEBT_VERIFIER",
    "PROPOSE_DEBT_RANK",
    "SELF_CORRECT_PROOF_DSL",
    "STRICT_THEOREM_COMPILER_REPAIR",
    "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE",
    "PROVE_PARAMETRIC_LIFTING_LEMMA",
]


def _load_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _prompt_rows() -> list[dict[str, Any]]:
    return [
        {
            "source": "run9_live_eval",
            "task": "collatz_theorem_proof_attempt",
            "label": "PROPOSE_PROOF_DSL",
            "verifier_status": "UNKNOWN",
            "tags": ["collatz", "proof", "theorem", "strict_verifier"],
            "prompt": "\n".join(
                [
                    "Emit a concise proof-DSL attempt for Collatz eventual descent.",
                    "Required theorem: forall n > 1 exists k >= 1 such that C^k(n) < n.",
                    "Use only verifier-checkable claims and identify open obligations.",
                ]
            ),
        },
        {
            "source": "run9_live_eval",
            "task": "mixed_modulus_high_parent_successor",
            "label": "PROPOSE_MIXED_MODULUS_STATE",
            "verifier_status": "UNKNOWN",
            "tags": ["collatz", "mixed_modulus", "successor", "debt"],
            "prompt": "\n".join(
                [
                    "Define mixed-modulus debt state M(a,rho,m,delta).",
                    "Use high-parent successor z(k)=c+3^a*k, T=v2(z(k)).",
                    "State the target parent and target odd-coordinate congruence modulo 3^a.",
                ]
            ),
        },
        {
            "source": "run9_live_eval",
            "task": "debt_rank_repair",
            "label": "PROPOSE_DEBT_RANK",
            "verifier_status": "FAIL_REQUIRES_REPAIR",
            "tags": ["rank", "positive_cycle", "repair", "well_founded"],
            "prompt": "\n".join(
                [
                    "The scalar parent-level rank has a positive cycle.",
                    "Propose a repaired well-founded rank over mixed-modulus debt states.",
                    "Explain which exact verifier would reject or accept it.",
                ]
            ),
        },
        {
            "source": "run9_live_eval",
            "task": "strict_theorem_compiler_repair",
            "label": "STRICT_THEOREM_COMPILER_REPAIR",
            "verifier_status": "FAIL",
            "tags": ["strict_theorem", "unknown_obligations", "repair"],
            "prompt": "\n".join(
                [
                    "The strict theorem compiler still reports unknown obligations.",
                    "Generate the next proof object patch and list the exact blockers.",
                    "Do not claim PASS unless all obligations are closed.",
                ]
            ),
        },
    ]


def extract_actions(text: str) -> list[str]:
    return [action for action in KNOWN_ACTIONS if action in text]


def extract_claims(text: str) -> list[str]:
    lower = text.lower()
    claims: list[str] = []
    if "z(k)" in lower and ("v2" in lower or "2^" in lower) and ("mod" in lower or "rho" in lower):
        claims.append("high_parent_successor")
    if ("mixed" in lower or "modulus" in lower or "rho" in lower) and ("debt" in lower or "delta" in lower):
        claims.append("mixed_modulus_state")
    if "rank" in lower and ("debt" in lower or "well-founded" in lower or "positive cycle" in lower):
        claims.append("debt_rank")
    if "collatz" in lower or "forall n" in lower or "strict theorem" in lower:
        claims.append("theorem_assembly")
    return claims


def _candidate_score(candidate: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(candidate["verification_summary"].get("accepted_claim_count", 0)),
        len(candidate.get("recognized_claims", [])),
        len(candidate.get("recognized_actions", [])),
    )


def verify_generated_claims(
    *,
    run_id: str,
    candidates: list[dict[str, Any]],
    high_parent_bypass: dict[str, Any] | None,
    mixed_modulus_debt: dict[str, Any] | None,
    theorem_candidate: dict[str, Any] | None,
) -> dict[str, Any]:
    theorem_status = str((theorem_candidate or {}).get("verifier_status", "UNKNOWN"))
    rank_status = str((mixed_modulus_debt or {}).get("status", "UNKNOWN"))
    claim_checks = []
    for candidate in candidates:
        claims = set(candidate.get("recognized_claims", []))
        checks = []
        if "high_parent_successor" in claims:
            checks.append(
                {
                    "claim_id": "high_parent_successor",
                    "status": "PASS"
                    if high_parent_bypass
                    and high_parent_bypass.get("status") == "MIXED_MODULUS_BYPASS_BUILT"
                    and high_parent_bypass.get("all_sample_checks_passed") is True
                    else "FAIL",
                    "verifier": "high_parent_bypass_exact_successor_checker",
                    "details": {
                        "generated_claim_was_recognized": True,
                        "mixed_successor_family_count": None
                        if not high_parent_bypass
                        else high_parent_bypass.get("mixed_successor_family_count"),
                    },
                }
            )
        if "mixed_modulus_state" in claims:
            checks.append(
                {
                    "claim_id": "mixed_modulus_state",
                    "status": "REDUCED",
                    "verifier": "typed_state_contract",
                    "details": {
                        "generated_claim_was_recognized": True,
                        "meaning": "useful state representation, not proof closure",
                    },
                }
            )
        if "debt_rank" in claims:
            checks.append(
                {
                    "claim_id": "debt_rank",
                    "status": "FAIL_REQUIRES_REPAIR"
                    if (mixed_modulus_debt or {}).get("proof_closed") is not True
                    else "PASS",
                    "verifier": "mixed_modulus_debt_verifier",
                    "details": {
                        "generated_claim_was_recognized": True,
                        "debt_verifier_status": rank_status,
                        "local_descent_pass_rate": None
                        if not mixed_modulus_debt
                        else mixed_modulus_debt.get("local_descent_pass_rate"),
                    },
                }
            )
        if "theorem_assembly" in claims:
            checks.append(
                {
                    "claim_id": "theorem_assembly",
                    "status": "PASS" if theorem_status == "PASS" else "FAIL",
                    "verifier": "strict_theorem_verifier",
                    "details": {
                        "generated_claim_was_recognized": True,
                        "theorem_verifier_status": theorem_status,
                        "unknown_obligations": len((theorem_candidate or {}).get("unknown_obligations", [])),
                    },
                }
            )
        status_counts = Counter(row["status"] for row in checks)
        accepted = [row for row in checks if row["status"] == "PASS"]
        candidate["verification_summary"] = {
            "claim_status_counts": dict(status_counts),
            "accepted_claim_count": len(accepted),
            "total_claim_count": len(checks),
        }
        claim_checks.append({"candidate_id": candidate["candidate_id"], "checks": checks})

    selected = max(candidates, key=_candidate_score) if candidates else None
    selected_checks = []
    if selected:
        selected_checks = next(row["checks"] for row in claim_checks if row["candidate_id"] == selected["candidate_id"])
    selected_status_counts = Counter(row["status"] for row in selected_checks)
    accepted_selected = [row for row in selected_checks if row["status"] == "PASS"]
    return {
        "schema": MODEL_PROOF_VERIFICATION_SCHEMA,
        "version": 1,
        "run_id": run_id,
        "status": "PASS" if theorem_status == "PASS" else "FAIL",
        "proof_confidence_percent": 100.0 if theorem_status == "PASS" else 0.0,
        "selected_candidate_id": None if selected is None else selected["candidate_id"],
        "selected_claim_status_counts": dict(selected_status_counts),
        "accepted_claim_count": len(accepted_selected),
        "total_claim_count": len(selected_checks),
        "candidate_checks": claim_checks,
        "what_made_it_through_verifier": [
            {"claim_id": row["claim_id"], "verifier": row["verifier"], "details": row["details"]}
            for row in accepted_selected
        ],
        "what_failed_or_remains_open": [row for row in selected_checks if row["status"] != "PASS"],
        "next_step": (
            "Do not continue blind GPU scaling. Improve proof-targeted objectives and symbolic parsing; "
            "the partial Transformer must first generate verifier-actionable mixed-modulus debt-rank claims."
        )
        if theorem_status != "PASS"
        else "Strict proof passed; promote theorem artifact.",
    }


def evaluate_checkpoint(
    *,
    run_id: str,
    checkpoint_path: str | Path,
    out_dir: str | Path,
    high_parent_bypass_path: str | Path = "reports/debt_induction/high_parent_bypass_report.json",
    mixed_modulus_debt_path: str | Path = "reports/debt_induction/mixed_modulus_debt_verifier.json",
    theorem_candidate_path: str | Path = "reports/collatz_descent_theorem_candidate.json",
    progress_report_path: str | Path = "reports/proof_policy_run_v1.json",
    global_obligations_path: str | Path = "reports/parent_state_global_obligations.json",
    debt_induction_path: str | Path = "reports/debt_induction/mixed_modulus_debt_verifier.json",
    progress_path: str | Path | None = None,
    central_attempts_log_path: str | Path | None = "proof_attempts.jsonl",
    max_new_tokens: int = 220,
    device: str = "auto",
) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    target_device = None if device == "auto" else torch.device(device)
    model, vocab, checkpoint = load_proof_transformer_checkpoint(checkpoint_path, device=target_device)
    config = dict(checkpoint.get("config") or {})

    candidates = []
    prefixes = ["", "<ACTION="]
    candidate_index = 0
    for prompt_index, row in enumerate(_prompt_rows(), start=1):
        for prefix in prefixes:
            candidate_index += 1
            text = generate_proof_text(
                model,
                vocab,
                row,
                max_input_len=int(config.get("max_input_len", 768)),
                max_new_tokens=max_new_tokens,
                temperature=0.0,
                seed=9 + candidate_index,
                decoder_prefix=prefix,
            )
            candidates.append(
                {
                    "candidate_id": f"{run_id}:proof-transformer:{candidate_index}",
                    "prompt_index": prompt_index,
                    "decoder_prefix": prefix,
                    "prompt": row,
                    "generated_text": text,
                    "recognized_actions": extract_actions(text),
                    "recognized_claims": extract_claims(text),
                }
            )

    high_parent_bypass = _load_json(high_parent_bypass_path)
    mixed_modulus_debt = _load_json(mixed_modulus_debt_path)
    theorem_candidate = _load_json(theorem_candidate_path)
    verification = verify_generated_claims(
        run_id=run_id,
        candidates=candidates,
        high_parent_bypass=high_parent_bypass,
        mixed_modulus_debt=mixed_modulus_debt,
        theorem_candidate=theorem_candidate,
    )
    selected_candidate_id = verification["selected_candidate_id"]
    selected = next((row for row in candidates if row["candidate_id"] == selected_candidate_id), candidates[0])
    progress = _load_json(progress_path)
    proposal = {
        "schema": MODEL_PROOF_PROPOSAL_SCHEMA,
        "version": 1,
        "run_id": run_id,
        "author": "partial_a100_proof_transformer",
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_step": checkpoint.get("step"),
        "training_progress": progress,
        "selected_candidate_id": selected_candidate_id,
        "generated_candidates": candidates,
    }
    proposal_path = out / "model_proof_proposal.json"
    proposal_path.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verification_path = out / "model_proof_verification.json"
    verification_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    attempt = build_proof_attempt(
        run_id=run_id,
        theorem_candidate=theorem_candidate,
        progress_report=_load_json(progress_report_path),
        global_obligations=_load_json(global_obligations_path),
        debt_induction=_load_json(debt_induction_path),
        author="partial_a100_proof_transformer",
    )
    attempt["proof_style"] = "partial A100 proof-transformer generated text attempt"
    attempt["proof_text"] = selected["generated_text"] or "<EMPTY_GENERATION>"
    attempt["proof_dsl"] = {
        "schema": "collatz_lab.proof_transformer_raw_proof_dsl",
        "version": 1,
        "selected_candidate_id": selected_candidate_id,
        "recognized_actions": selected.get("recognized_actions", []),
        "recognized_claims": selected.get("recognized_claims", []),
        "raw_generation": selected["generated_text"],
        "note": "Raw generated text is not accepted as proof unless extracted claims pass exact verifier gates.",
    }
    attempt["model_proof_proposal"] = {
        "path": str(proposal_path),
        "selected_candidate_id": selected_candidate_id,
        "checkpoint_step": checkpoint.get("step"),
        "recognized_actions": selected.get("recognized_actions", []),
        "recognized_claims": selected.get("recognized_claims", []),
    }
    attempt["model_proof_verification"] = {
        "path": str(verification_path),
        "claim_status_counts": verification["selected_claim_status_counts"],
        "accepted_claim_count": verification["accepted_claim_count"],
        "total_claim_count": verification["total_claim_count"],
    }
    attempt_path = out / "proof_attempt.json"
    attempt_path.write_text(json.dumps(attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_proof_attempt_markdown(attempt, out / "proof_attempt.md")

    evaluation = evaluate_proof_attempt(attempt)
    evaluation["next_step"] = verification["next_step"]
    evaluation["model_proof_verification_summary"] = {
        "claim_status_counts": verification["selected_claim_status_counts"],
        "accepted_claim_count": verification["accepted_claim_count"],
        "total_claim_count": verification["total_claim_count"],
        "what_made_it_through_verifier": verification["what_made_it_through_verifier"],
        "what_failed_or_remains_open": verification["what_failed_or_remains_open"],
    }
    evaluation_path = out / "proof_evaluation.json"
    evaluation_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_evaluation_markdown(evaluation, out / "proof_evaluation.md")

    record = build_proof_attempt_record(
        attempt,
        evaluation,
        artifacts={
            "model_proof_proposal": str(proposal_path),
            "model_proof_verification": str(verification_path),
            "proof_attempt": str(attempt_path),
            "proof_evaluation": str(evaluation_path),
        },
        search={
            "rank": 1,
            "selected": True,
            "rank_score": float(_candidate_score(selected)[0]),
            "variant": {"variant_id": "partial-a100-proof-transformer-raw-generation"},
        },
    )
    log_results = append_proof_attempt_record_to_logs(
        record,
        [out / "proof_attempts.jsonl", Path(central_attempts_log_path) if central_attempts_log_path else None],
    )

    report = {
        "schema": PROOF_TRANSFORMER_EVAL_SCHEMA,
        "version": 1,
        "run_id": run_id,
        "status": "EVALUATED_PARTIAL_PROOF_TRANSFORMER",
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_step": checkpoint.get("step"),
        "device": str(next(model.parameters()).device),
        "proposal_path": str(proposal_path),
        "verification_path": str(verification_path),
        "proof_attempt_path": str(attempt_path),
        "proof_evaluation_path": str(evaluation_path),
        "proof_attempt_logs": log_results,
        "proof_confidence_percent": evaluation["proof_confidence_percent"],
        "proof_progress_percent": evaluation["proof_progress_percent"],
        "selected_candidate_id": selected_candidate_id,
        "selected_generated_text": selected["generated_text"],
        "selected_recognized_actions": selected.get("recognized_actions", []),
        "selected_recognized_claims": selected.get("recognized_claims", []),
        "model_claim_verification": verification,
    }
    report_path = out / "proof_transformer_evaluation.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a proof Transformer checkpoint as a proof-attempt generator.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    parser.add_argument("--mixed-modulus-debt", default="reports/debt_induction/mixed_modulus_debt_verifier.json")
    parser.add_argument("--theorem-candidate", default="reports/collatz_descent_theorem_candidate.json")
    parser.add_argument("--progress-report", default="reports/proof_policy_run_v1.json")
    parser.add_argument("--global-obligations", default="reports/parent_state_global_obligations.json")
    parser.add_argument("--debt-induction", default="reports/debt_induction/mixed_modulus_debt_verifier.json")
    parser.add_argument("--training-progress", default=None)
    parser.add_argument("--central-attempts-log", default="proof_attempts.jsonl")
    parser.add_argument("--max-new-tokens", type=int, default=220)
    parser.add_argument("--device", default="auto")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = evaluate_checkpoint(
        run_id=args.run_id,
        checkpoint_path=args.checkpoint,
        out_dir=args.out_dir,
        high_parent_bypass_path=args.high_parent_bypass,
        mixed_modulus_debt_path=args.mixed_modulus_debt,
        theorem_candidate_path=args.theorem_candidate,
        progress_report_path=args.progress_report,
        global_obligations_path=args.global_obligations,
        debt_induction_path=args.debt_induction,
        progress_path=args.training_progress,
        central_attempts_log_path=args.central_attempts_log,
        max_new_tokens=args.max_new_tokens,
        device=args.device,
    )
    Console().print(
        {
            "report": str(Path(args.out_dir) / "proof_transformer_evaluation.json"),
            "proof_confidence_percent": report["proof_confidence_percent"],
            "proof_progress_percent": report["proof_progress_percent"],
            "selected_recognized_claims": report["selected_recognized_claims"],
        }
    )


if __name__ == "__main__":
    main()
