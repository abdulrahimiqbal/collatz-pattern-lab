"""Build training corpora for Collatz proof-invention models.

The proof-inventor model needs more than Collatz trajectories.  It needs a
single corpus that mixes general proof patterns, Collatz structural algebra,
verifier outcomes, failed proof attempts, and repair targets.  This module
turns existing exact reports into a JSONL training set with one stable schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console


PROOF_CORPUS_EXAMPLE_SCHEMA = "collatz_lab.proof_corpus_example"
PROOF_CORPUS_REPORT_SCHEMA = "collatz_lab.proof_corpus_report"


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


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _example_id(source: str, task: str, payload: Any) -> str:
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()[:16]
    return f"{source}:{task}:{digest}"


def _example(
    *,
    source: str,
    task: str,
    prompt: str,
    target: dict[str, Any] | str,
    label: str,
    tags: list[str] | None = None,
    verifier_status: str = "UNKNOWN",
    weight: float = 1.0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "source": source,
        "task": task,
        "prompt": prompt,
        "target": target,
        "label": label,
        "metadata": metadata or {},
    }
    return {
        "schema": PROOF_CORPUS_EXAMPLE_SCHEMA,
        "version": 1,
        "example_id": _example_id(source, task, payload),
        "source": source,
        "task": task,
        "tags": sorted(set(tags or [])),
        "prompt": prompt,
        "target": target if isinstance(target, str) else json.dumps(target, sort_keys=True),
        "target_object": target if isinstance(target, dict) else None,
        "label": label,
        "verifier_status": verifier_status,
        "weight": float(weight),
        "metadata": metadata or {},
    }


def _dedupe(examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in examples:
        example_id = str(row["example_id"])
        if example_id in seen:
            continue
        seen.add(example_id)
        deduped.append(row)
    return deduped


def high_parent_bypass_examples(report: dict[str, Any] | None, limit: int | None = None) -> list[dict[str, Any]]:
    if not report:
        return []
    rows = list(report.get("mixed_successor_families") or [])
    if limit is not None:
        rows = rows[:limit]
    examples: list[dict[str, Any]] = []
    for row in rows:
        samples = row.get("valuation_family_samples") or []
        first = samples[0] if samples else {}
        prompt = "\n".join(
            [
                "<TASK=PROOF_DSL>",
                "<BLOCKER=HIGH_PARENT_MIXED_MODULUS>",
                f"branch={row.get('branch_id')}",
                f"a={row.get('a')} r={row.get('r_residue')} d={row.get('r_depth')} h={row.get('h')}",
                f"floor={row.get('known_target_parent_floor')}",
                f"z_family={row.get('z_family')}",
                "emit exact successor lemma and verifier action",
            ]
        )
        target = {
            "definition": "high_parent_successor_family",
            "lemma": row.get("successor_family_rule"),
            "target_family_T0": first.get("target_family"),
            "proof_action": "PROPOSE_MIXED_MODULUS_STATE",
            "verifier": "high_parent_bypass_exact_successor_checker",
        }
        examples.append(
            _example(
                source="high_parent_bypass",
                task="collatz_structure_to_proof_dsl",
                prompt=prompt,
                target=target,
                label="PROPOSE_MIXED_MODULUS_STATE",
                tags=["collatz", "mixed_modulus", "high_parent", "exact_successor"],
                verifier_status="PASS" if row.get("sample_checks_passed") else "UNKNOWN",
                weight=1.5,
                metadata={
                    "branch_id": row.get("branch_id"),
                    "odd_coordinate_descent_sufficient": row.get("odd_coordinate_descent_sufficient"),
                },
            )
        )
        examples.append(
            _example(
                source="high_parent_bypass",
                task="successor_family_to_debt_verifier_target",
                prompt="\n".join(
                    [
                        "<TASK=NEXT_VERIFIER_TARGET>",
                        "<KNOWN=HIGH_PARENT_SUCCESSOR_FAMILY_PASS>",
                        f"branch={row.get('branch_id')}",
                        f"z_family={row.get('z_family')}",
                        "mixed-modulus state is already derived; emit the next verifier target",
                    ]
                ),
                target={
                    "proof_action": "TRY_MIXED_MODULUS_DEBT_VERIFIER",
                    "required_state": ["parent_level", "odd_coordinate_mod_3a", "growth_debt"],
                    "next_missing_object": "exact debt update law and decreasing mixed-modulus rank",
                },
                label="TRY_MIXED_MODULUS_DEBT_VERIFIER",
                tags=["collatz", "mixed_modulus", "debt_verifier", "next_target"],
                verifier_status="REDUCED",
                weight=1.4,
                metadata={"branch_id": row.get("branch_id")},
            )
        )
    rank = report.get("level_rank_analysis") or {}
    if rank.get("positive_cycle_witness"):
        prompt = "\n".join(
            [
                "<TASK=RANK_REPAIR>",
                "<FAILURE=SCALAR_PARENT_LEVEL_RANK>",
                f"cycle_log_gain_sum={rank.get('cycle_log_gain_sum')}",
                f"cycle={json.dumps(rank.get('positive_cycle_witness', [])[:4], sort_keys=True)}",
                "emit a repair target that uses mixed modulus residue and growth debt",
            ]
        )
        target = {
            "definition": "mixed_modulus_debt_rank",
            "rejected_rank": "scalar parent-level Phi(a)",
            "repair": "rank must depend on parent level, odd residue modulo 3^a, and growth debt",
            "proof_action": "PROPOSE_DEBT_RANK",
            "verifier": "scalar_parent_level_rank_checker",
        }
        examples.append(
            _example(
                source="high_parent_bypass",
                task="rank_repair_from_counterexample",
                prompt=prompt,
                target=target,
                label="PROPOSE_DEBT_RANK",
                tags=["collatz", "rank_repair", "positive_cycle", "mixed_modulus"],
                verifier_status="FAIL_REQUIRES_REPAIR",
                weight=2.0,
                metadata={"cycle_log_gain_sum": rank.get("cycle_log_gain_sum")},
            )
        )
    return examples


def return_cycle_examples(report: dict[str, Any] | None, limit: int = 40) -> list[dict[str, Any]]:
    if not report:
        return []
    examples: list[dict[str, Any]] = []
    sections = report.get("sequence_reports") or {}
    for section_name in sorted(sections):
        rows = list((sections[section_name] or {}).get("top_certified_by_coverage") or [])
        for row in rows[:limit]:
            prompt = "\n".join(
                [
                    "<TASK=AFFINE_RETURN_HEIGHT_CERTIFICATE>",
                    f"sequence={row.get('sequence')}",
                    f"map={json.dumps(row.get('map'), sort_keys=True)}",
                    "emit height-decrease certificate",
                ]
            )
            target = {
                "lemma": "affine return map has decreasing 2-adic height on repeat unless fixed point",
                "height": row.get("height"),
                "fixed_point": row.get("fixed_point"),
                "proof_action": "TRY_SCC_RANKING",
            }
            examples.append(
                _example(
                    source="cycle_mining",
                    task="affine_height_proof_dsl",
                    prompt=prompt,
                    target=target,
                    label="TRY_SCC_RANKING",
                    tags=["collatz", "return_map", "height_rank", "proof_pattern"],
                    verifier_status=str(row.get("status", "UNKNOWN")),
                    weight=1.2,
                    metadata={"section": section_name, "count_at_q_depth": row.get("count_at_q_depth")},
                )
            )
    return examples


def proof_attempt_replay_examples(rows: list[dict[str, Any]], limit: int | None = None) -> list[dict[str, Any]]:
    if limit is not None:
        rows = rows[:limit]
    examples: list[dict[str, Any]] = []
    for record in rows:
        blocking_steps = list(record.get("blocking_steps") or [])
        for step in blocking_steps:
            label = REPAIR_LABELS.get(str(step), "SELF_CORRECT_PROOF_DSL")
            prompt = "\n".join(
                [
                    "<TASK=PROOF_REPAIR_ACTION>",
                    f"run_id={record.get('run_id')}",
                    f"proof_progress={record.get('proof_progress_percent')}",
                    f"blocking_step={step}",
                    f"next_step={record.get('next_step')}",
                    "emit the next proof action",
                ]
            )
            target = {
                "repair_action": label,
                "blocking_step": step,
                "must_keep_proof_confidence_zero_unless_strict_pass": True,
            }
            examples.append(
                _example(
                    source="proof_attempt_replay",
                    task="verifier_feedback_to_repair_action",
                    prompt=prompt,
                    target=target,
                    label=label,
                    tags=["proof_replay", "verifier_feedback", "repair"],
                    verifier_status=str(record.get("verifier_status", "UNKNOWN")),
                    weight=1.0,
                    metadata={"run_id": record.get("run_id"), "attempt_id": record.get("attempt_id")},
                )
            )
    return examples


def mixed_modulus_debt_examples(report: dict[str, Any] | None, limit: int | None = None) -> list[dict[str, Any]]:
    """Convert exact mixed-modulus debt verifier traces into proof-model examples."""

    if not report:
        return []
    rows = list(report.get("transitions") or [])
    if limit is not None:
        rows = rows[:limit]
    examples: list[dict[str, Any]] = []
    for row in rows:
        source = row.get("source_state") or {}
        target = row.get("target_state") or {}
        gain = row.get("gain_bound") or {}
        status = str(row.get("status", "UNKNOWN"))
        label = (
            "VERIFY_MIXED_MODULUS_DEBT_TRANSITION"
            if status == "PASS"
            else "REPAIR_MIXED_MODULUS_DEBT_RANK"
        )
        prompt = "\n".join(
            [
                "<TASK=MIXED_MODULUS_DEBT_TRACE>",
                f"branch={row.get('branch_id')}",
                f"source_parent={source.get('parent_level')} source_residue={source.get('odd_coordinate_residue')} mod {source.get('odd_coordinate_modulus')}",
                f"target_parent={target.get('parent_level')} valuation={target.get('valuation')}",
                f"target_rho={target.get('odd_coordinate_residue_mod_3a')} mod {target.get('odd_coordinate_modulus_3a')}",
                f"gain_bound={gain.get('numerator')}/{gain.get('denominator')}",
                f"local_descent_passed={row.get('local_descent_passed')}",
                "emit the verifier-backed proof action or rank repair",
            ]
        )
        target_obj = {
            "proof_action": label,
            "mixed_state": row.get("mixed_state"),
            "gain_bound": gain,
            "status": status,
            "next_obligation": row.get("proof_obligation"),
        }
        examples.append(
            _example(
                source="mixed_modulus_debt_verifier",
                task="mixed_modulus_debt_transition_trace",
                prompt=prompt,
                target=target_obj,
                label=label,
                tags=["collatz", "mixed_modulus", "debt_verifier", "verifier_trace"],
                verifier_status=status,
                weight=1.6 if status != "PASS" else 1.2,
                metadata={
                    "branch_id": row.get("branch_id"),
                    "valuation": target.get("valuation"),
                    "local_descent_passed": row.get("local_descent_passed"),
                },
            )
        )

    for blocker in report.get("blocking_obligations", []):
        label = (
            "PROVE_UNBOUNDED_VALUATION_CLOSURE"
            if "unbounded valuation" in blocker
            else "MAP_MIXED_STATE_TO_GLOBAL_OBLIGATION"
            if "global theorem obligation" in blocker
            else "REPAIR_MIXED_MODULUS_DEBT_RANK"
        )
        examples.append(
            _example(
                source="mixed_modulus_debt_verifier",
                task="mixed_modulus_debt_blocker_to_repair_action",
                prompt="\n".join(
                    [
                        "<TASK=MIXED_MODULUS_DEBT_BLOCKER_REPAIR>",
                        f"verifier_status={report.get('verifier_status')}",
                        f"proof_closed={report.get('proof_closed')}",
                        f"blocking_obligation={blocker}",
                        "emit the next proof-system repair action",
                    ]
                ),
                target={"repair_action": label, "blocking_obligation": blocker},
                label=label,
                tags=["collatz", "mixed_modulus", "proof_repair", "verifier_feedback"],
                verifier_status="FAIL",
                weight=1.7,
            )
        )
    return examples


def theorem_failure_examples(theorem_candidate: dict[str, Any] | None, preflight: dict[str, Any] | None) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    if theorem_candidate:
        unknowns = theorem_candidate.get("unknown_obligations") or []
        prompt = "\n".join(
            [
                "<TASK=STRICT_THEOREM_REPAIR>",
                f"verifier_status={theorem_candidate.get('verifier_status')}",
                f"unknown_count={len(unknowns)}",
                f"unknown_sample={json.dumps(unknowns[:8], sort_keys=True)}",
                "emit compiler repair plan",
            ]
        )
        examples.append(
            _example(
                source="strict_theorem_verifier",
                task="strict_theorem_repair",
                prompt=prompt,
                target={
                    "repair_action": "STRICT_THEOREM_COMPILER_REPAIR",
                    "rule": "do not accept theorem until all obligations close and strict verifier PASS",
                    "unknown_obligation_count": len(unknowns),
                },
                label="STRICT_THEOREM_COMPILER_REPAIR",
                tags=["strict_verifier", "proof_repair"],
                verifier_status=str(theorem_candidate.get("verifier_status", "UNKNOWN")),
                weight=1.0,
            )
        )
    if preflight:
        for blocker in preflight.get("blocking_checks", []):
            label = "TRY_MIXED_MODULUS_DEBT_VERIFIER" if blocker == "mixed_modulus_debt_verifier_ready" else "SELF_CORRECT_PROOF_DSL"
            examples.append(
                _example(
                    source="run_preflight",
                    task="preflight_blocker_to_repair_action",
                    prompt="\n".join(
                        [
                            "<TASK=PREFLIGHT_REPAIR>",
                            f"status={preflight.get('status')}",
                            f"blocking_check={blocker}",
                            "emit required repair action",
                        ]
                    ),
                    target={"repair_action": label, "blocking_check": blocker},
                    label=label,
                    tags=["preflight", "repair"],
                    verifier_status="FAIL",
                    weight=1.0,
                )
            )
    return examples


def external_formal_examples(path: str | Path | None, limit: int | None = None) -> list[dict[str, Any]]:
    """Adapt optional external proof rows into the common schema.

    Expected row fields are intentionally permissive: ``prompt``/``state`` and
    ``target``/``proof`` are enough for a usable example.
    """

    examples: list[dict[str, Any]] = []
    for index, row in enumerate(_jsonl_rows(path)):
        if limit is not None and index >= limit:
            break
        prompt = str(row.get("prompt") or row.get("state") or row.get("theorem") or "")
        target = str(row.get("target") or row.get("proof") or row.get("tactic") or "")
        if not prompt or not target:
            continue
        examples.append(
            _example(
                source=str(row.get("source", "external_formal_proof")),
                task="general_formal_proof_pattern",
                prompt=prompt,
                target=target,
                label=str(row.get("label", "PROPOSE_PROOF_DSL")),
                tags=["external_formal_proof", "general_proof"],
                verifier_status=str(row.get("verifier_status", "UNKNOWN")),
                weight=float(row.get("weight", 0.8)),
                metadata={"external_index": index},
            )
        )
    return examples


def formal_seed_examples() -> list[dict[str, Any]]:
    """Small built-in proof-pattern seed corpus.

    This is not a substitute for Lean/mathlib scale.  It gives the local
    bootstrap model explicit proof idioms while the external adapter remains the
    real path to large proof corpora.
    """

    rows = [
        (
            "modular_inverse_successor",
            "<TASK=GENERAL_PROOF_PATTERN>\nGiven odd A and z(k)=c+A*k, prove z(k)/2^T has residue c*2^{-T} mod A.",
            {
                "proof_pattern": "reduce congruence modulo odd A; A*k vanishes; multiply by inverse of 2^T",
                "uses": ["modular inverse", "congruence rewriting"],
            },
            "PROPOSE_PROOF_DSL",
        ),
        (
            "height_drop_affine_return",
            "<TASK=GENERAL_PROOF_PATTERN>\nFor q'=(Aq+B)/D, prove v2((A-D)q'+B)=v2((A-D)q+B)-log2(D).",
            {
                "proof_pattern": "substitute affine return map; factor A/D out of the height linear form",
                "uses": ["affine algebra", "valuation drop"],
            },
            "TRY_SCC_RANKING",
        ),
        (
            "well_founded_rank_induction",
            "<TASK=GENERAL_PROOF_PATTERN>\nGiven a transition system and rank R that strictly decreases, prove no infinite path.",
            {
                "proof_pattern": "well-founded induction on rank; every transition moves to smaller rank",
                "uses": ["well-founded induction", "ranking function"],
            },
            "PROPOSE_DEBT_RANK",
        ),
        (
            "counterexample_guided_rank_repair",
            "<TASK=GENERAL_PROOF_PATTERN>\nA proposed potential has a positive cycle. Emit repair variables that separate the cycle.",
            {
                "proof_pattern": "read the cycle witness; add state dimensions that distinguish the repeated states",
                "uses": ["counterexample guided abstraction refinement"],
            },
            "SELF_CORRECT_PROOF_DSL",
        ),
        (
            "crt_parity_odd_modulus",
            "<TASK=GENERAL_PROOF_PATTERN>\nCombine odd residue r mod m with oddness into a residue mod 2m.",
            {
                "proof_pattern": "Chinese remainder theorem with moduli 2 and odd m",
                "uses": ["CRT", "parity"],
            },
            "PROPOSE_PROOF_DSL",
        ),
        (
            "strict_compiler_gate",
            "<TASK=GENERAL_PROOF_PATTERN>\nA proof has local lemmas but global theorem verifier fails. Decide confidence.",
            {
                "proof_pattern": "proof confidence is 100 only when strict verifier PASS; local lemmas are progress only",
                "uses": ["proof audit", "soundness gate"],
            },
            "STRICT_THEOREM_COMPILER_REPAIR",
        ),
    ]
    return [
        _example(
            source="formal_proof_seed",
            task="general_formal_proof_pattern",
            prompt=prompt,
            target=target,
            label=label,
            tags=["general_proof", "formal_seed", name],
            verifier_status="PROOF_PATTERN",
            weight=0.6,
            metadata={"pattern_id": name},
        )
        for name, prompt, target, label in rows
    ]


def build_proof_corpus(
    *,
    proof_attempts_log: str | Path | None = "proof_attempts.jsonl",
    high_parent_bypass_path: str | Path | None = "reports/debt_induction/high_parent_bypass_report.json",
    mixed_modulus_debt_path: str | Path | None = "reports/debt_induction/mixed_modulus_debt_verifier.json",
    cycle_mining_path: str | Path | None = "reports/cycle_mining_parent_returns_q30.json",
    theorem_candidate_path: str | Path | None = "reports/collatz_descent_theorem_candidate.json",
    preflight_path: str | Path | None = "reports/run7_preflight.json",
    external_formal_jsonl: str | Path | None = None,
    include_formal_seed: bool = True,
    max_high_parent_examples: int | None = None,
    max_mixed_debt_examples: int | None = None,
    max_return_cycle_examples: int = 40,
    max_replay_examples: int | None = None,
    max_external_examples: int | None = None,
) -> dict[str, Any]:
    high_parent_bypass = _load_json(high_parent_bypass_path)
    mixed_modulus_debt = _load_json(mixed_modulus_debt_path)
    cycle_mining = _load_json(cycle_mining_path)
    theorem_candidate = _load_json(theorem_candidate_path)
    preflight = _load_json(preflight_path)
    attempt_rows = _jsonl_rows(proof_attempts_log)

    examples = []
    examples.extend(high_parent_bypass_examples(high_parent_bypass, limit=max_high_parent_examples))
    examples.extend(mixed_modulus_debt_examples(mixed_modulus_debt, limit=max_mixed_debt_examples))
    examples.extend(return_cycle_examples(cycle_mining, limit=max_return_cycle_examples))
    examples.extend(proof_attempt_replay_examples(attempt_rows, limit=max_replay_examples))
    examples.extend(theorem_failure_examples(theorem_candidate, preflight))
    if include_formal_seed:
        examples.extend(formal_seed_examples())
    examples.extend(external_formal_examples(external_formal_jsonl, limit=max_external_examples))
    examples = _dedupe(examples)
    task_counts = Counter(row["task"] for row in examples)
    source_counts = Counter(row["source"] for row in examples)
    label_counts = Counter(row["label"] for row in examples)
    verifier_counts = Counter(row["verifier_status"] for row in examples)
    return {
        "schema": PROOF_CORPUS_REPORT_SCHEMA,
        "version": 1,
        "status": "PROOF_CORPUS_BUILT",
        "example_count": len(examples),
        "task_counts": dict(task_counts),
        "source_counts": dict(source_counts),
        "label_counts": dict(label_counts),
        "verifier_status_counts": dict(verifier_counts),
        "stream_mix": {
            "general_formal_proof": source_counts.get("external_formal_proof", 0)
            + sum(count for source, count in source_counts.items() if "formal" in source),
            "collatz_structural": source_counts.get("high_parent_bypass", 0) + source_counts.get("cycle_mining", 0),
            "verifier_replay": source_counts.get("proof_attempt_replay", 0)
            + source_counts.get("mixed_modulus_debt_verifier", 0)
            + source_counts.get("strict_theorem_verifier", 0)
            + source_counts.get("run_preflight", 0),
        },
        "scaling_law_target": (
            "predict typed proof programs and repair actions from exact mathematical state plus verifier feedback"
        ),
        "examples": examples,
    }


def write_jsonl(examples: list[dict[str, Any]], out: str | Path) -> None:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in examples) + "\n", encoding="utf-8")


def write_report_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Proof-Inventor Corpus",
        "",
        f"- status: `{report['status']}`",
        f"- examples: `{report['example_count']}`",
        f"- task counts: `{report['task_counts']}`",
        f"- source counts: `{report['source_counts']}`",
        f"- label counts: `{report['label_counts']}`",
        f"- verifier status counts: `{report['verifier_status_counts']}`",
        f"- stream mix: `{report['stream_mix']}`",
        "",
        "## Scaling Target",
        "",
        str(report["scaling_law_target"]),
        "",
    ]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a proof-inventor training corpus.")
    parser.add_argument("--proof-attempts-log", default="proof_attempts.jsonl")
    parser.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    parser.add_argument("--mixed-modulus-debt", default="reports/debt_induction/mixed_modulus_debt_verifier.json")
    parser.add_argument("--cycle-mining", default="reports/cycle_mining_parent_returns_q30.json")
    parser.add_argument("--theorem-candidate", default="reports/collatz_descent_theorem_candidate.json")
    parser.add_argument("--preflight", default="reports/run7_preflight.json")
    parser.add_argument("--external-formal-jsonl", default=None)
    parser.add_argument("--no-formal-seed", action="store_true")
    parser.add_argument("--max-high-parent-examples", type=int, default=None)
    parser.add_argument("--max-mixed-debt-examples", type=int, default=None)
    parser.add_argument("--max-return-cycle-examples", type=int, default=40)
    parser.add_argument("--max-replay-examples", type=int, default=None)
    parser.add_argument("--max-external-examples", type=int, default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report-out", required=True)
    parser.add_argument("--report-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_proof_corpus(
        proof_attempts_log=args.proof_attempts_log,
        high_parent_bypass_path=args.high_parent_bypass,
        mixed_modulus_debt_path=args.mixed_modulus_debt,
        cycle_mining_path=args.cycle_mining,
        theorem_candidate_path=args.theorem_candidate,
        preflight_path=args.preflight,
        external_formal_jsonl=args.external_formal_jsonl,
        include_formal_seed=not args.no_formal_seed,
        max_high_parent_examples=args.max_high_parent_examples,
        max_mixed_debt_examples=args.max_mixed_debt_examples,
        max_return_cycle_examples=args.max_return_cycle_examples,
        max_replay_examples=args.max_replay_examples,
        max_external_examples=args.max_external_examples,
    )
    write_jsonl(report["examples"], args.out)
    serializable = {key: value for key, value in report.items() if key != "examples"}
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report_markdown(serializable, args.report_md or report_out.with_suffix(".md"))
    Console().print({"out": args.out, "report": str(report_out), "examples": report["example_count"]})


if __name__ == "__main__":
    main()
