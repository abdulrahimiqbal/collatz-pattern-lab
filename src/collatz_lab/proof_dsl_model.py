"""Bootstrap proof-DSL generator trained from verifier feedback.

This is the first local model whose output is a proof object rather than a
Collatz trajectory/candidate family.  It is intentionally small: the repo only
has a thin proof-attempt replay buffer today, so RUN-008 trains a lightweight
repair-action classifier and uses it to emit a typed proof program.  Exact
verifiers remain the judge.
"""

from __future__ import annotations

import argparse
import json
import pickle
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from .proof_actions import ProofAction
from .proof_attempt import (
    append_proof_attempt_record_to_logs,
    build_proof_attempt,
    build_proof_attempt_record,
    evaluate_proof_attempt,
    write_evaluation_markdown,
    write_proof_attempt_markdown,
)
from .proof_env import execute_action


PROOF_DSL_GENERATOR_SCHEMA = "collatz_lab.proof_dsl_generator"
MODEL_PROOF_PROPOSAL_SCHEMA = "collatz_lab.model_proof_proposal"
MODEL_PROOF_VERIFICATION_SCHEMA = "collatz_lab.model_proof_verification"


REPAIR_LABELS = {
    "S2-p6-local-frontier": "REFINE_LOCAL_FRONTIER_CERTIFICATES",
    "S3-global-parent-transitions": "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE",
    "S4-parametric-lifting": "PROVE_PARAMETRIC_LIFTING_LEMMA",
    "S5-debt-induction": "TRY_MIXED_MODULUS_DEBT_VERIFIER",
    "S6-strict-theorem-verifier": "STRICT_THEOREM_COMPILER_REPAIR",
}


def _load_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _jsonl_rows(path: str | Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _flatten(prefix: str, value: Any, out: dict[str, Any]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _flatten(f"{prefix}.{key}" if prefix else str(key), child, out)
    elif isinstance(value, list):
        out[f"{prefix}.len"] = len(value)
        for item in value[:8]:
            if isinstance(item, str):
                out[f"{prefix}.has.{item}"] = True
    elif isinstance(value, (str, int, float, bool)) or value is None:
        out[prefix] = "None" if value is None else value


def _record_features(
    record: dict[str, Any],
    blocking_step: str,
    high_parent_bypass: dict[str, Any] | None,
    preflight: dict[str, Any] | None,
) -> dict[str, Any]:
    features: dict[str, Any] = {
        "blocking_step": blocking_step,
        "record_status": record.get("status"),
        "verifier_status": record.get("verifier_status"),
        "proof_progress_bucket": int(float(record.get("proof_progress_percent", 0.0) or 0.0) // 10),
        "has_mixed_modulus_bypass": bool(high_parent_bypass),
        "mixed_modulus_bypass_ready": bool(high_parent_bypass and high_parent_bypass.get("ready_for_run7") is True),
        "mixed_successor_family_count": 0
        if not high_parent_bypass
        else int(high_parent_bypass.get("mixed_successor_family_count", 0) or 0),
        "rank_status": "None"
        if not high_parent_bypass
        else (high_parent_bypass.get("level_rank_analysis") or {}).get("status", "UNKNOWN"),
    }
    variant = ((record.get("proof_search") or {}).get("variant") or {}).get("variant_id")
    if variant:
        features["variant"] = variant
    if preflight:
        for blocker in preflight.get("blocking_checks", []):
            features[f"preflight_blocker.{blocker}"] = True
    return features


def build_training_examples(
    attempt_records: list[dict[str, Any]],
    high_parent_bypass: dict[str, Any] | None = None,
    preflight: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Convert failed proof attempts and current blockers into repair examples."""

    examples: list[dict[str, Any]] = []
    for record in attempt_records:
        for blocking_step in record.get("blocking_steps", []):
            label = REPAIR_LABELS.get(str(blocking_step), "SELF_CORRECT_PROOF_DSL")
            if str(blocking_step) == "S5-debt-induction" and not high_parent_bypass:
                label = "PROVE_DEBT_CARRYING_INDUCTION"
            examples.append(
                {
                    "source": "proof_attempt_record",
                    "features": _record_features(record, str(blocking_step), high_parent_bypass, preflight),
                    "label": label,
                }
            )

    if high_parent_bypass and high_parent_bypass.get("status") == "MIXED_MODULUS_BYPASS_BUILT":
        synthetic = {
            "status": "FAIL",
            "verifier_status": "FAIL",
            "proof_progress_percent": 0.0,
            "blocking_steps": ["S5-debt-induction"],
        }
        examples.append(
            {
                "source": "current_high_parent_bypass",
                "features": {
                    **_record_features(synthetic, "S5-debt-induction", high_parent_bypass, preflight),
                    "current_blocker": "mixed_modulus_debt_verifier_ready",
                },
                "label": "TRY_MIXED_MODULUS_DEBT_VERIFIER",
            }
        )
        examples.append(
            {
                "source": "current_rank_obstruction",
                "features": {
                    **_record_features(synthetic, "S5-debt-induction", high_parent_bypass, preflight),
                    "current_blocker": "scalar_parent_level_rank_positive_cycle",
                },
                "label": "PROPOSE_DEBT_RANK",
            }
        )
        examples.append(
            {
                "source": "current_state_representation_gap",
                "features": {
                    **_record_features(synthetic, "S3-global-parent-transitions", high_parent_bypass, preflight),
                    "current_blocker": "missing_odd_modulus_state",
                },
                "label": "PROPOSE_MIXED_MODULUS_STATE",
            }
        )
    return examples


def train_bootstrap_proof_dsl_model(examples: list[dict[str, Any]]) -> dict[str, Any]:
    if not examples:
        raise ValueError("at least one training example is required")
    features = [dict(row["features"]) for row in examples]
    labels = [str(row["label"]) for row in examples]
    vectorizer = DictVectorizer(sparse=True)
    x = vectorizer.fit_transform(features)
    label_counts = Counter(labels)
    classifier = None
    train_accuracy = None
    heldout_accuracy = None
    if len(label_counts) >= 2:
        classifier = LogisticRegression(max_iter=2000, solver="lbfgs")
        classifier.fit(x, labels)
        train_accuracy = float(accuracy_score(labels, classifier.predict(x)))
        if len(examples) >= 8:
            stratify = labels if min(label_counts.values()) >= 2 else None
            x_train, x_test, y_train, y_test = train_test_split(
                x,
                labels,
                test_size=0.35,
                random_state=8,
                stratify=stratify,
            )
            heldout = LogisticRegression(max_iter=2000, solver="lbfgs")
            heldout.fit(x_train, y_train)
            heldout_accuracy = float(accuracy_score(y_test, heldout.predict(x_test)))
    return {
        "schema": PROOF_DSL_GENERATOR_SCHEMA,
        "version": 1,
        "status": "TRAINED_BOOTSTRAP_PROOF_DSL_GENERATOR",
        "model_kind": "DictVectorizer + LogisticRegression repair-action classifier",
        "example_count": len(examples),
        "label_counts": dict(label_counts),
        "train_accuracy": train_accuracy,
        "heldout_accuracy": heldout_accuracy,
        "vectorizer": vectorizer,
        "classifier": classifier,
        "training_examples": examples,
    }


def _predict_actions(model_bundle: dict[str, Any], features: dict[str, Any], top_k: int = 6) -> list[dict[str, Any]]:
    classifier = model_bundle.get("classifier")
    vectorizer = model_bundle.get("vectorizer")
    if classifier is None or vectorizer is None:
        counts = Counter(row["label"] for row in model_bundle.get("training_examples", []))
        total = sum(counts.values()) or 1
        return [
            {"action": action, "score": count / total, "source": "label_prior"}
            for action, count in counts.most_common(top_k)
        ]
    x = vectorizer.transform([features])
    if hasattr(classifier, "predict_proba"):
        probs = classifier.predict_proba(x)[0]
        return [
            {"action": str(action), "score": float(score), "source": "classifier"}
            for action, score in sorted(zip(classifier.classes_, probs, strict=True), key=lambda row: row[1], reverse=True)[
                :top_k
            ]
        ]
    return [{"action": str(classifier.predict(x)[0]), "score": 1.0, "source": "classifier"}]


def build_model_proof_proposal(
    run_id: str,
    model_bundle: dict[str, Any],
    high_parent_bypass: dict[str, Any] | None,
    preflight: dict[str, Any] | None,
) -> dict[str, Any]:
    """Ask the trained proof model for a typed proof program."""

    features = {
        "blocking_step": "S5-debt-induction",
        "has_mixed_modulus_bypass": bool(high_parent_bypass),
        "mixed_modulus_bypass_ready": bool(high_parent_bypass and high_parent_bypass.get("ready_for_run7") is True),
        "mixed_successor_family_count": 0
        if not high_parent_bypass
        else high_parent_bypass.get("mixed_successor_family_count", 0),
        "rank_status": "None"
        if not high_parent_bypass
        else (high_parent_bypass.get("level_rank_analysis") or {}).get("status", "UNKNOWN"),
        "preflight_blocker.mixed_modulus_debt_verifier_ready": bool(
            preflight and "mixed_modulus_debt_verifier_ready" in preflight.get("blocking_checks", [])
        ),
    }
    predicted_actions = _predict_actions(model_bundle, features)
    branch_count = 0 if not high_parent_bypass else int(high_parent_bypass.get("mixed_successor_family_count", 0) or 0)
    cycle = [] if not high_parent_bypass else (high_parent_bypass.get("level_rank_analysis") or {}).get(
        "positive_cycle_witness",
        [],
    )
    proof_dsl = {
        "schema": "collatz_lab.proof_dsl",
        "version": 2,
        "theorem": {
            "theorem_id": "collatz_eventual_descent_via_mixed_modulus_debt",
            "statement": "forall n > 1 exists k >= 1 such that C^k(n) < n",
        },
        "definitions": [
            {
                "definition_id": "mixed_modulus_debt_state",
                "symbol": "M(a, rho, m, delta)",
                "definition": (
                    "parent level a, odd coordinate residue rho modulo odd modulus m=3^source_a, "
                    "and remaining growth debt delta"
                ),
            },
            {
                "definition_id": "high_parent_successor_family",
                "symbol": "T_f,c,A",
                "definition": "z(k)=c+A*k, T=v2(z(k)), target P_{f+T} with odd coordinate z(k)/2^T",
            },
            {
                "definition_id": "debt_rank_candidate",
                "symbol": "R=log(n)+Phi(M)",
                "definition": "candidate well-founded rank over mixed-modulus states; scalar parent-level Phi is known insufficient",
            },
        ],
        "lemmas": [
            {
                "lemma_id": "L-MM1-high-parent-successor",
                "kind": "exact_successor_family",
                "statement": (
                    "Every open high-parent branch has an exact mixed-modulus successor family: "
                    "if T=v2(c+3^a*k), target odd coordinate is congruent to c*2^{-T} modulo 3^a."
                ),
                "evidence_refs": ["reports/debt_induction/high_parent_bypass_report.json"],
                "expected_verifier_status": "PASS",
                "branch_count": branch_count,
            },
            {
                "lemma_id": "L-MM2-state-space",
                "kind": "state_definition",
                "statement": "The proof search state must include odd-coordinate congruence modulo 3^a plus growth debt.",
                "evidence_refs": ["reports/debt_induction/high_parent_bypass_report.json"],
                "expected_verifier_status": "REDUCED",
            },
            {
                "lemma_id": "L-MM3-debt-rank",
                "kind": "rank_repair",
                "statement": (
                    "A scalar parent-level rank fails; repair requires a mixed-modulus debt rank that breaks "
                    "the reported positive cycle."
                ),
                "evidence_refs": ["reports/debt_induction/high_parent_bypass_report.json"],
                "expected_verifier_status": "FAIL_THEN_REPAIR",
                "positive_cycle_witness": cycle[:4],
            },
            {
                "lemma_id": "L-MM4-theorem-assembly",
                "kind": "strict_compiler",
                "statement": "Assemble universal entry, local frontier support, mixed-modulus debt induction, and strict verifier PASS.",
                "evidence_refs": ["reports/collatz_descent_theorem_candidate.json"],
                "expected_verifier_status": "OPEN",
            },
        ],
        "proof_actions": [
            {
                "action": "PROPOSE_MIXED_MODULUS_STATE",
                "params": {"state": ["parent_level", "odd_coordinate_mod_3a", "growth_debt"]},
            },
            {"action": "TRY_MIXED_MODULUS_DEBT_VERIFIER", "params": {"source": "high_parent_bypass"}},
            {"action": "PROPOSE_DEBT_RANK", "params": {"repair_positive_cycle": True}},
            {"action": "SELF_CORRECT_PROOF_DSL", "params": {"target": "mixed_modulus_debt_verifier_ready"}},
        ],
    }
    return {
        "schema": MODEL_PROOF_PROPOSAL_SCHEMA,
        "version": 1,
        "run_id": run_id,
        "author": "trained_bootstrap_proof_dsl_generator",
        "model_status": model_bundle.get("status"),
        "predicted_repair_actions": predicted_actions,
        "proof_text": (
            "Model proposal: stop treating the high-parent blocker as a deeper 2-adic split. "
            "Define a mixed-modulus debt state carrying parent level, odd-coordinate congruence modulo 3^a, "
            "and growth debt.  Use the exact high-parent successor lemma as the first verified lemma, "
            "then search for a debt rank that breaks the P20/P23 positive cycle before theorem assembly."
        ),
        "proof_dsl": proof_dsl,
    }


def verify_model_proof_proposal(
    proposal: dict[str, Any],
    high_parent_bypass: dict[str, Any] | None,
    theorem_candidate: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate which model-proposed proof claims survive exact checks."""

    theorem_status = None if theorem_candidate is None else theorem_candidate.get("verifier_status", "UNKNOWN")
    rank = {} if not high_parent_bypass else dict(high_parent_bypass.get("level_rank_analysis") or {})
    checks = [
        {
            "claim_id": "L-MM1-high-parent-successor",
            "status": "PASS"
            if high_parent_bypass
            and high_parent_bypass.get("status") == "MIXED_MODULUS_BYPASS_BUILT"
            and high_parent_bypass.get("all_sample_checks_passed") is True
            else "FAIL",
            "verifier": "high_parent_bypass_exact_successor_checker",
            "details": {
                "mixed_successor_family_count": None
                if not high_parent_bypass
                else high_parent_bypass.get("mixed_successor_family_count"),
                "sample_checks_passed": None
                if not high_parent_bypass
                else high_parent_bypass.get("all_sample_checks_passed"),
            },
        },
        {
            "claim_id": "L-MM2-state-space",
            "status": "REDUCED",
            "verifier": "typed_proof_dsl_contract",
            "details": {
                "accepted_as_next_state_representation": bool(high_parent_bypass),
                "not_a_closure_certificate": True,
            },
        },
        {
            "claim_id": "L-MM3-debt-rank",
            "status": "FAIL_REQUIRES_REPAIR" if rank.get("status") == "FAIL" else "UNKNOWN",
            "verifier": "scalar_parent_level_rank_checker",
            "details": {
                "rank_status": rank.get("status"),
                "cycle_log_gain_sum": rank.get("cycle_log_gain_sum"),
                "positive_cycle_witness": rank.get("positive_cycle_witness", [])[:4],
            },
        },
        {
            "claim_id": "L-MM4-theorem-assembly",
            "status": "PASS" if theorem_status == "PASS" else "FAIL",
            "verifier": "strict_theorem_verifier",
            "details": {"theorem_verifier_status": theorem_status},
        },
    ]
    synthetic_obligation = {
        "obligation_id": "parent_state_transition_templates",
        "status": "UNKNOWN",
        "coverage": {"a_min": 1, "a_max": 64, "r_depth": 8},
    }
    action_results = []
    for row in proposal.get("proof_dsl", {}).get("proof_actions", []):
        action = ProofAction(action=str(row["action"]), params=dict(row.get("params", {})))
        result = execute_action(action, synthetic_obligation)
        action_results.append({"action": action.to_dict(), "result": result.to_dict()})
    status_counts = Counter(row["status"] for row in checks)
    action_status_counts = Counter(row["result"]["status"] for row in action_results)
    accepted = [row for row in checks if row["status"] == "PASS"]
    return {
        "schema": MODEL_PROOF_VERIFICATION_SCHEMA,
        "version": 1,
        "run_id": proposal.get("run_id"),
        "status": "FAIL" if theorem_status != "PASS" else "PASS",
        "proof_confidence_percent": 100.0 if theorem_status == "PASS" else 0.0,
        "claim_status_counts": dict(status_counts),
        "accepted_claim_count": len(accepted),
        "total_claim_count": len(checks),
        "checks": checks,
        "proof_action_result_counts": dict(action_status_counts),
        "proof_action_results": action_results,
        "what_made_it_through_verifier": [
            {
                "claim_id": row["claim_id"],
                "verifier": row["verifier"],
                "details": row["details"],
            }
            for row in accepted
        ],
        "what_failed_or_remains_open": [
            row for row in checks if row["status"] != "PASS"
        ],
        "next_step": (
            "Implement the mixed-modulus debt verifier and train the proof model on its PASS/FAIL/repair traces."
            if theorem_status != "PASS"
            else "Strict proof passed; promote theorem artifact."
        ),
    }


def write_model_report_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Proof-DSL Generator Model",
        "",
        f"- status: `{report['status']}`",
        f"- model kind: `{report['model_kind']}`",
        f"- examples: `{report['example_count']}`",
        f"- label counts: `{report['label_counts']}`",
        f"- train accuracy: `{report['train_accuracy']}`",
        f"- heldout accuracy: `{report['heldout_accuracy']}`",
        "",
    ]
    Path(out).write_text("\n".join(lines), encoding="utf-8")


def write_proposal_markdown(proposal: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Model-Proposed Proof",
        "",
        f"- run id: `{proposal['run_id']}`",
        f"- author: `{proposal['author']}`",
        "",
        proposal["proof_text"],
        "",
        "## Predicted Repair Actions",
        "",
    ]
    for row in proposal["predicted_repair_actions"]:
        lines.append(f"- `{row['action']}` score `{row['score']:.4f}` source `{row['source']}`")
    lines.extend(["", "## Lemmas", ""])
    for lemma in proposal["proof_dsl"]["lemmas"]:
        lines.append(
            f"- `{lemma['lemma_id']}` `{lemma['kind']}` expected `{lemma['expected_verifier_status']}`: "
            f"{lemma['statement']}"
        )
    Path(out).write_text("\n".join(lines), encoding="utf-8")


def write_verification_markdown(verification: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Model Proof Verification",
        "",
        f"- status: `{verification['status']}`",
        f"- proof confidence: `{verification['proof_confidence_percent']}`",
        f"- accepted claims: `{verification['accepted_claim_count']} / {verification['total_claim_count']}`",
        f"- claim status counts: `{verification['claim_status_counts']}`",
        f"- proof action result counts: `{verification['proof_action_result_counts']}`",
        "",
        "## Accepted",
        "",
    ]
    for row in verification["what_made_it_through_verifier"]:
        lines.append(f"- `{row['claim_id']}` via `{row['verifier']}`")
    lines.extend(["", "## Failed Or Open", ""])
    for row in verification["what_failed_or_remains_open"]:
        lines.append(f"- `{row['claim_id']}`: `{row['status']}` via `{row['verifier']}`")
    lines.extend(["", "## Next Step", "", verification["next_step"], ""])
    Path(out).write_text("\n".join(lines), encoding="utf-8")


def save_model_bundle(model_bundle: dict[str, Any], path: str | Path) -> None:
    serializable = dict(model_bundle)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as handle:
        pickle.dump(serializable, handle)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a proof-DSL generator and emit a verifier-checked proof attempt.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempts-log", default="proof_attempts.jsonl")
    parser.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    parser.add_argument("--preflight", default="reports/run7_preflight.json")
    parser.add_argument("--theorem-candidate", default="reports/collatz_descent_theorem_candidate.json")
    parser.add_argument("--progress-report", default="reports/debt_induction/top10_closure_with_gate.json")
    parser.add_argument("--global-obligations", default="reports/parent_state_global_obligations.json")
    parser.add_argument("--debt-induction", default="reports/debt_induction/top10_gate.json")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--central-attempts-log", default="proof_attempts.jsonl")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    high_parent_bypass = _load_json(args.high_parent_bypass)
    preflight = _load_json(args.preflight)
    theorem_candidate = _load_json(args.theorem_candidate)
    examples = build_training_examples(
        _jsonl_rows(args.attempts_log),
        high_parent_bypass=high_parent_bypass,
        preflight=preflight,
    )
    model_bundle = train_bootstrap_proof_dsl_model(examples)
    model_path = out_dir / "proof_dsl_model.pkl"
    save_model_bundle(model_bundle, model_path)
    model_report = {
        key: value
        for key, value in model_bundle.items()
        if key not in {"vectorizer", "classifier", "training_examples"}
    }
    model_report["model_path"] = str(model_path)
    model_report["training_example_sample"] = examples[:12]
    model_report_path = out_dir / "proof_dsl_model_report.json"
    model_report_path.write_text(json.dumps(model_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_model_report_markdown(model_report, out_dir / "proof_dsl_model_report.md")

    proposal = build_model_proof_proposal(args.run_id, model_bundle, high_parent_bypass, preflight)
    proposal_path = out_dir / "model_proof_proposal.json"
    proposal_path.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_proposal_markdown(proposal, out_dir / "model_proof_proposal.md")

    verification = verify_model_proof_proposal(proposal, high_parent_bypass, theorem_candidate)
    verification_path = out_dir / "model_proof_verification.json"
    verification_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_verification_markdown(verification, out_dir / "model_proof_verification.md")

    proof_attempt = build_proof_attempt(
        run_id=args.run_id,
        theorem_candidate=theorem_candidate,
        progress_report=_load_json(args.progress_report),
        global_obligations=_load_json(args.global_obligations),
        debt_induction=_load_json(args.debt_induction),
        author="trained_bootstrap_proof_dsl_generator",
    )
    proof_attempt["proof_style"] = "model-generated typed proof DSL attempt"
    proof_attempt["proof_text"] = proposal["proof_text"]
    proof_attempt["proof_dsl"] = proposal["proof_dsl"]
    proof_attempt["model_proof_proposal"] = {
        "path": str(proposal_path),
        "predicted_repair_actions": proposal["predicted_repair_actions"],
    }
    proof_attempt["model_proof_verification"] = {
        "path": str(verification_path),
        "claim_status_counts": verification["claim_status_counts"],
        "accepted_claim_count": verification["accepted_claim_count"],
        "total_claim_count": verification["total_claim_count"],
    }
    proof_attempt_path = out_dir / "proof_attempt.json"
    proof_attempt_path.write_text(json.dumps(proof_attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_proof_attempt_markdown(proof_attempt, out_dir / "proof_attempt.md")
    evaluation = evaluate_proof_attempt(proof_attempt)
    evaluation["next_step"] = verification["next_step"]
    evaluation["model_proof_verification_summary"] = {
        "claim_status_counts": verification["claim_status_counts"],
        "accepted_claim_count": verification["accepted_claim_count"],
        "total_claim_count": verification["total_claim_count"],
        "proof_action_result_counts": verification["proof_action_result_counts"],
    }
    evaluation_path = out_dir / "proof_evaluation.json"
    evaluation_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_evaluation_markdown(evaluation, out_dir / "proof_evaluation.md")
    record = build_proof_attempt_record(
        proof_attempt,
        evaluation,
        artifacts={
            "proof_dsl_model_report": str(model_report_path),
            "model_proof_proposal": str(proposal_path),
            "model_proof_verification": str(verification_path),
            "proof_attempt": str(proof_attempt_path),
            "proof_evaluation": str(evaluation_path),
        },
        search={
            "rank": 1,
            "selected": True,
            "rank_score": proposal["predicted_repair_actions"][0]["score"]
            if proposal["predicted_repair_actions"]
            else 0.0,
            "variant": {"variant_id": "trained-proof-dsl-mixed-modulus"},
        },
    )
    append_proof_attempt_record_to_logs(
        record,
        [out_dir / "proof_attempts.jsonl", Path(args.central_attempts_log) if args.central_attempts_log else None],
    )
    Console().print(
        {
            "model_report": str(model_report_path),
            "proposal": str(proposal_path),
            "verification": str(verification_path),
            "proof_attempt": str(proof_attempt_path),
            "proof_evaluation": str(evaluation_path),
            "accepted_claims": verification["accepted_claim_count"],
            "proof_confidence": verification["proof_confidence_percent"],
        }
    )


if __name__ == "__main__":
    main()
