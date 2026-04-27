"""Generate, critique, and rank structured proof attempts.

This module is deliberately upstream of the strict verifier.  It improves the
system's ability to propose theorem-shaped proof objects, but it never upgrades
proof confidence; exact verifier status remains authoritative.
"""

from __future__ import annotations

import json
from typing import Any

from .proof_attempt import build_proof_attempt, evaluate_proof_attempt


PROOF_DSL_SCHEMA = "collatz_lab.proof_dsl"
PROOF_CRITIC_SCHEMA = "collatz_lab.proof_critic"
PROOF_ATTEMPT_SEARCH_SCHEMA = "collatz_lab.proof_attempt_search"


VARIANT_SPECS = [
    {
        "variant_id": "global-template-first",
        "title": "Global parent-state template proof",
        "focus_step": "S3-global-parent-transitions",
        "strategy": [
            "S1-universal-entry",
            "S3-global-parent-transitions",
            "S4-parametric-lifting",
            "S5-debt-induction",
            "S2-p6-local-frontier",
            "S6-strict-theorem-verifier",
        ],
        "proof_text": (
            "Attempt: prove universal entry, derive exact parent-state transition "
            "templates for all P_a, lift those templates uniformly in a and "
            "2-adic depth, then use local P6 certificates only as supporting "
            "evidence before the strict theorem verifier."
        ),
    },
    {
        "variant_id": "parametric-lift-first",
        "title": "Parametric lifting proof",
        "focus_step": "S4-parametric-lifting",
        "strategy": [
            "S1-universal-entry",
            "S4-parametric-lifting",
            "S3-global-parent-transitions",
            "S5-debt-induction",
            "S2-p6-local-frontier",
            "S6-strict-theorem-verifier",
        ],
        "proof_text": (
            "Attempt: start from the observed 3^a periodicity, propose a uniform "
            "lifting lemma across a and 2-adic depth, then use it to close the "
            "global parent-state transition templates."
        ),
    },
    {
        "variant_id": "debt-induction-first",
        "title": "Debt-carrying induction proof",
        "focus_step": "S5-debt-induction",
        "strategy": [
            "S1-universal-entry",
            "S5-debt-induction",
            "S3-global-parent-transitions",
            "S4-parametric-lifting",
            "S2-p6-local-frontier",
            "S6-strict-theorem-verifier",
        ],
        "proof_text": (
            "Attempt: define a debt-carrying rank that pays low-h expansion, "
            "prove every parent transition decreases the rank after carrying "
            "debt, then compile the theorem candidate."
        ),
    },
    {
        "variant_id": "finite-frontier-honest",
        "title": "Finite frontier support proof",
        "focus_step": "S2-p6-local-frontier",
        "strategy": [
            "S1-universal-entry",
            "S2-p6-local-frontier",
            "S3-global-parent-transitions",
            "S4-parametric-lifting",
            "S5-debt-induction",
            "S6-strict-theorem-verifier",
        ],
        "proof_text": (
            "Attempt: state the finite P6 frontier exactly as local evidence, "
            "avoid treating it as global coverage, and identify the missing "
            "template and lifting lemmas needed for a real proof."
        ),
    },
    {
        "variant_id": "strict-compiler-repair",
        "title": "Strict compiler repair proof",
        "focus_step": "S6-strict-theorem-verifier",
        "strategy": [
            "S1-universal-entry",
            "S3-global-parent-transitions",
            "S4-parametric-lifting",
            "S5-debt-induction",
            "S6-strict-theorem-verifier",
            "S2-p6-local-frontier",
        ],
        "proof_text": (
            "Attempt: work backward from the strict theorem verifier errors, "
            "turn every unknown obligation into a typed lemma, and only accept "
            "the proof when the compiler reports PASS."
        ),
    },
]


def _clone(data: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(data))


def _step_map(proof_attempt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(step.get("step_id")): step for step in proof_attempt.get("steps", [])}


def _ordered_steps(proof_attempt: dict[str, Any], strategy: list[str]) -> list[dict[str, Any]]:
    by_id = _step_map(proof_attempt)
    used: set[str] = set()
    ordered: list[dict[str, Any]] = []
    for step_id in strategy:
        if step_id in by_id:
            ordered.append(by_id[step_id])
            used.add(step_id)
    for step in proof_attempt.get("steps", []):
        step_id = str(step.get("step_id"))
        if step_id not in used:
            ordered.append(step)
    return ordered


def _lemma(
    lemma_id: str,
    kind: str,
    statement: str,
    quantifiers: list[str],
    evidence_refs: list[str],
    proof_obligations: list[str],
    expected_status: str,
) -> dict[str, Any]:
    return {
        "lemma_id": lemma_id,
        "kind": kind,
        "statement": statement,
        "quantifiers": quantifiers,
        "evidence_refs": evidence_refs,
        "proof_obligations": proof_obligations,
        "expected_status": expected_status,
    }


def build_proof_dsl(proof_attempt: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    """Build a typed proof DSL object for one proof-attempt variant."""

    return {
        "schema": PROOF_DSL_SCHEMA,
        "version": 1,
        "theorem": {
            "theorem_id": "collatz_eventual_descent",
            "statement": proof_attempt.get("theorem"),
            "quantifiers": ["forall n in Z, n > 1"],
            "conclusion": "exists k >= 1 such that C^k(n) < n",
        },
        "definitions": [
            {
                "definition_id": "collatz_step",
                "symbol": "C(n)",
                "definition": "C(n)=n/2 if n is even, and C(n)=3n+1 if n is odd",
            },
            {
                "definition_id": "parent_state",
                "symbol": "P_a(r)",
                "definition": "odd n represented as n=2^a*r-1 with a>=1 and r odd",
            },
            {
                "definition_id": "debt_rank",
                "symbol": "R(n,state,debt)",
                "definition": "candidate rank that must decrease across expanding low-h transitions",
            },
        ],
        "lemmas": [
            _lemma(
                "L1-universal-entry",
                "entry",
                "Every n>1 either descends immediately if even or enters a unique parent state if odd.",
                ["forall n in Z, n > 1"],
                ["S1-universal-entry"],
                ["even_descent", "odd_parent_state_cover"],
                "closed",
            ),
            _lemma(
                "L2-finite-p6-frontier",
                "local_certificate_family",
                "The current P6 q-depth frontier has exact local descent certificates for the stated finite slice.",
                ["forall q in the reported finite q-depth domain"],
                ["S2-p6-local-frontier"],
                ["P6_q20_finite_frontier_coverage"],
                "partial",
            ),
            _lemma(
                "L3-global-parent-transitions",
                "transition_template",
                "Every parent-state transition P_a has an exact affine template and a decreasing rank target.",
                ["forall a >= 1", "forall odd r", "forall admissible h"],
                ["S3-global-parent-transitions"],
                ["parent_state_transition_templates"],
                "open",
            ),
            _lemma(
                "L4-parametric-lifting",
                "parametric_lift",
                "Finite-depth transition templates lift uniformly in a and 2-adic depth.",
                ["forall a >= 1", "forall depth >= d0"],
                ["S4-parametric-lifting"],
                ["parametric_a_templates"],
                "open",
            ),
            _lemma(
                "L5-debt-induction",
                "induction",
                "Low-h expanding transitions are paid by a debt-carrying parent-state induction.",
                ["forall parent states in the low-h transition graph"],
                ["S5-debt-induction"],
                ["debt_carrying_parent_induction"],
                "open",
            ),
            _lemma(
                "L6-theorem-assembly",
                "theorem_compiler",
                "The prior lemmas assemble into a strict verifier PASS for eventual descent.",
                ["all theorem obligations are closed"],
                ["S6-strict-theorem-verifier"],
                ["strict_theorem_verifier"],
                "open",
            ),
        ],
        "strategy": {
            "variant_id": variant["variant_id"],
            "title": variant["title"],
            "focus_step": variant["focus_step"],
            "step_order": list(variant["strategy"]),
        },
    }


def generate_proof_attempt_variants(
    run_id: str,
    theorem_candidate: dict[str, Any] | None = None,
    progress_report: dict[str, Any] | None = None,
    global_obligations: dict[str, Any] | None = None,
    debt_induction: dict[str, Any] | None = None,
    max_attempts: int = 5,
) -> list[dict[str, Any]]:
    """Generate deterministic theorem-shaped proof-attempt variants."""

    if max_attempts <= 0:
        return []
    base = build_proof_attempt(
        run_id=run_id,
        theorem_candidate=theorem_candidate,
        progress_report=progress_report,
        global_obligations=global_obligations,
        debt_induction=debt_induction,
        author="model/system:proof_dsl_generator",
    )
    attempts: list[dict[str, Any]] = []
    for index, variant in enumerate(VARIANT_SPECS[:max_attempts]):
        attempt = _clone(base)
        attempt["proof_text"] = variant["proof_text"]
        attempt["steps"] = _ordered_steps(attempt, variant["strategy"])
        attempt["attempt_variant"] = {
            "variant_id": variant["variant_id"],
            "title": variant["title"],
            "focus_step": variant["focus_step"],
            "rank_seed": index,
        }
        attempt["proof_dsl"] = build_proof_dsl(attempt, variant)
        attempts.append(attempt)
    return attempts


def critique_proof_attempt(
    proof_attempt: dict[str, Any],
    evaluation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Critique proof shape before strict verification or training replay."""

    evaluation = evaluation or evaluate_proof_attempt(proof_attempt)
    issues: list[dict[str, Any]] = []
    dsl = proof_attempt.get("proof_dsl")
    if not isinstance(dsl, dict) or dsl.get("schema") != PROOF_DSL_SCHEMA:
        issues.append(
            {
                "severity": "ERROR",
                "code": "missing_typed_proof_dsl",
                "message": "proof attempt does not expose the typed proof DSL",
            }
        )
    else:
        theorem = dsl.get("theorem") if isinstance(dsl.get("theorem"), dict) else {}
        if not theorem.get("quantifiers"):
            issues.append(
                {
                    "severity": "ERROR",
                    "code": "missing_theorem_quantifiers",
                    "message": "the theorem lacks explicit quantifiers",
                }
            )
        for lemma in dsl.get("lemmas", []):
            if not lemma.get("quantifiers"):
                issues.append(
                    {
                        "severity": "ERROR",
                        "code": "missing_lemma_quantifiers",
                        "lemma_id": lemma.get("lemma_id"),
                        "message": "lemma lacks explicit quantifiers",
                    }
                )
            if not lemma.get("evidence_refs"):
                issues.append(
                    {
                        "severity": "ERROR",
                        "code": "missing_lemma_evidence",
                        "lemma_id": lemma.get("lemma_id"),
                        "message": "lemma does not cite a proof step/evidence source",
                    }
                )

    for row in evaluation.get("step_results", []):
        status = row.get("status")
        if status == "PASS":
            continue
        severity = "WARNING" if status == "PARTIAL" else "ERROR"
        if row.get("kind") == "strict_theorem_verifier":
            severity = "CRITICAL"
        issues.append(
            {
                "severity": severity,
                "code": "unverified_proof_step",
                "step_id": row.get("step_id"),
                "message": row.get("reason"),
            }
        )
    if "S2-p6-local-frontier" in evaluation.get("blocking_steps", []):
        issues.append(
            {
                "severity": "WARNING",
                "code": "finite_local_evidence_only",
                "step_id": "S2-p6-local-frontier",
                "message": "finite P6 coverage may guide search but cannot be used as a universal proof step",
            }
        )
    if "S3-global-parent-transitions" in evaluation.get("blocking_steps", []):
        issues.append(
            {
                "severity": "ERROR",
                "code": "local_to_global_gap",
                "step_id": "S3-global-parent-transitions",
                "message": "global parent-state transitions are not yet exact or ranked",
            }
        )
    if "S4-parametric-lifting" in evaluation.get("blocking_steps", []):
        issues.append(
            {
                "severity": "ERROR",
                "code": "missing_parametric_lift",
                "step_id": "S4-parametric-lifting",
                "message": "finite templates have not been lifted uniformly in a and 2-adic depth",
            }
        )

    penalty = 0.0
    for issue in issues:
        penalty += {
            "INFO": 1.0,
            "WARNING": 4.0,
            "ERROR": 12.0,
            "CRITICAL": 20.0,
        }.get(str(issue.get("severity")), 8.0)
    score = max(0.0, 100.0 - penalty)
    hard_issue_count = sum(1 for issue in issues if issue.get("severity") in {"ERROR", "CRITICAL"})
    return {
        "schema": PROOF_CRITIC_SCHEMA,
        "version": 1,
        "status": "REJECTED_BY_CRITIC" if hard_issue_count else "CRITIC_WARNINGS_ONLY",
        "critic_score_percent": score,
        "hard_issue_count": hard_issue_count,
        "issue_count": len(issues),
        "issues": issues,
        "accepted_for_strict_claim": hard_issue_count == 0 and evaluation.get("status") == "PASS",
    }


def rank_proof_attempts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Evaluate, critique, and rank generated proof attempts."""

    ranked: list[dict[str, Any]] = []
    for attempt in attempts:
        evaluation = evaluate_proof_attempt(attempt)
        critic = critique_proof_attempt(attempt, evaluation)
        focus_step = str(attempt.get("attempt_variant", {}).get("focus_step", ""))
        focus_bonus = 5.0 if focus_step and focus_step in evaluation.get("blocking_steps", []) else 0.0
        rank_score = (
            float(evaluation.get("proof_progress_percent", 0.0))
            + 0.10 * float(critic.get("critic_score_percent", 0.0))
            + focus_bonus
        )
        ranked.append(
            {
                "attempt": attempt,
                "evaluation": evaluation,
                "critic": critic,
                "rank_score": rank_score,
                "focus_bonus": focus_bonus,
            }
        )
    ranked.sort(
        key=lambda row: (
            row["rank_score"],
            row["evaluation"].get("proof_progress_percent", 0.0),
            -row["critic"].get("hard_issue_count", 0),
        ),
        reverse=True,
    )
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
        row["selected"] = index == 1
    return ranked


def build_ranked_proof_attempts(
    run_id: str,
    theorem_candidate: dict[str, Any] | None = None,
    progress_report: dict[str, Any] | None = None,
    global_obligations: dict[str, Any] | None = None,
    debt_induction: dict[str, Any] | None = None,
    max_attempts: int = 5,
) -> list[dict[str, Any]]:
    attempts = generate_proof_attempt_variants(
        run_id=run_id,
        theorem_candidate=theorem_candidate,
        progress_report=progress_report,
        global_obligations=global_obligations,
        debt_induction=debt_induction,
        max_attempts=max_attempts,
    )
    return rank_proof_attempts(attempts)


def summarize_ranked_attempts(ranked_attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": PROOF_ATTEMPT_SEARCH_SCHEMA,
        "version": 1,
        "attempt_count": len(ranked_attempts),
        "selected_attempt_id": None,
        "ranked_attempts": [
            {
                "rank": row["rank"],
                "selected": row["selected"],
                "variant_id": row["attempt"].get("attempt_variant", {}).get("variant_id"),
                "focus_step": row["attempt"].get("attempt_variant", {}).get("focus_step"),
                "rank_score": row["rank_score"],
                "proof_progress_percent": row["evaluation"].get("proof_progress_percent"),
                "proof_confidence_percent": row["evaluation"].get("proof_confidence_percent"),
                "critic_status": row["critic"].get("status"),
                "critic_score_percent": row["critic"].get("critic_score_percent"),
                "hard_issue_count": row["critic"].get("hard_issue_count"),
                "blocking_steps": row["evaluation"].get("blocking_steps", []),
                "next_step": row["evaluation"].get("next_step"),
            }
            for row in ranked_attempts
        ],
    }
