"""RUN-009 proof-inventor readiness gate.

RUN-009 is meant to test whether the system can train on enough proof and
Collatz structure to emit serious proof candidates.  This gate separates a
working local smoke test from a scaling-law-ready run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console


RUN9_PREFLIGHT_SCHEMA = "collatz_lab.run9_preflight"

DEFAULT_MIN_EXAMPLES = 10_000_000
DEFAULT_MIN_GENERAL_FORMAL = 1_000_000
DEFAULT_MIN_COLLATZ_STRUCTURAL = 6_000_000
DEFAULT_MIN_VERIFIER_REPLAY = 2_000_000
DEFAULT_MIN_MODEL_PARAMETERS = 100_000_000
DEFAULT_MIN_TRAIN_STEPS = 10_000


def _load(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _jsonl_count(path: str | Path | None) -> int | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    if source.is_dir():
        return sum(
            1
            for file_path in sorted(source.glob("*.jsonl"))
            for line in file_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return sum(1 for line in source.read_text(encoding="utf-8").splitlines() if line.strip())


def _exists(path: str | Path | None) -> bool:
    return path is not None and Path(path).exists()


def _check(name: str, passed: bool, required: bool = True, **details: Any) -> dict[str, Any]:
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "required": required,
        "details": details,
    }


def _stream_count(corpus_report: dict[str, Any] | None, name: str) -> int:
    if not corpus_report:
        return 0
    return int((corpus_report.get("stream_mix") or {}).get(name, 0))


def _top_action_labels(verification: dict[str, Any] | None) -> list[str]:
    if not verification:
        return []
    predictions = verification.get("proof_inventor_predictions") or {}
    return [str(row.get("label")) for row in predictions.get("actions") or []]


def _proof_confidence_is_honest(verification: dict[str, Any] | None) -> bool:
    if not verification:
        return False
    status = str(verification.get("status"))
    confidence = float(verification.get("proof_confidence_percent", -1))
    if status == "PASS":
        return confidence == 100.0
    return confidence == 0.0


def _is_large_proof_model(
    model_report: dict[str, Any] | None,
    min_model_parameters: int,
    min_train_steps: int,
) -> bool:
    if not model_report:
        return False
    kind = str(model_report.get("model_kind", "")).lower()
    status = str(model_report.get("status", "")).lower()
    if "tfidf" in kind or "logisticregression" in kind or "bootstrap" in status:
        return False
    is_target_architecture = "transformer" in kind or "language model" in kind or "proof model" in kind
    parameters = int(model_report.get("parameter_count", 0) or 0)
    train_steps = int(
        model_report.get("train_steps_completed", model_report.get("training_steps", model_report.get("step", 0))) or 0
    )
    return is_target_architecture and parameters >= min_model_parameters and train_steps >= min_train_steps


def _debt_verifier_ready(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    return (
        report.get("schema") == "collatz_lab.mixed_modulus_debt_verifier"
        and report.get("verifier_available") is True
        and report.get("ready_for_run9") is True
        and report.get("exact_transition_checks_passed") is True
        and int(report.get("transition_count", 0) or 0) > 0
    )


def build_run9_preflight(
    corpus_jsonl: str | Path = "data/proof_corpus/collatz_proof_inventor_v1.jsonl",
    corpus_report_path: str | Path = "reports/proof_corpus/collatz_proof_inventor_v1.json",
    model_report_path: str | Path = "reports/proof_inventor/collatz_proof_inventor_v1.json",
    proposal_path: str | Path = "reports/proof_inventor/RUN-009-dryrun-proposal/proof_inventor_proposal.json",
    verification_path: str | Path = "reports/proof_inventor/RUN-009-dryrun-proposal/proof_inventor_verification.json",
    high_parent_bypass_path: str | Path = "reports/debt_induction/high_parent_bypass_report.json",
    mixed_modulus_debt_verifier_path: str | Path = "reports/debt_induction/mixed_modulus_debt_verifier.json",
    min_examples: int = DEFAULT_MIN_EXAMPLES,
    min_general_formal: int = DEFAULT_MIN_GENERAL_FORMAL,
    min_collatz_structural: int = DEFAULT_MIN_COLLATZ_STRUCTURAL,
    min_verifier_replay: int = DEFAULT_MIN_VERIFIER_REPLAY,
    min_model_parameters: int = DEFAULT_MIN_MODEL_PARAMETERS,
    min_train_steps: int = DEFAULT_MIN_TRAIN_STEPS,
    allow_bootstrap_model: bool = False,
) -> dict[str, Any]:
    corpus_report = _load(corpus_report_path)
    model_report = _load(model_report_path)
    proposal = _load(proposal_path)
    verification = _load(verification_path)
    high_parent_bypass = _load(high_parent_bypass_path)
    debt_verifier = _load(mixed_modulus_debt_verifier_path)
    row_count = _jsonl_count(corpus_jsonl)

    corpus_examples = int((corpus_report or {}).get("example_count", 0))
    model_examples = int((model_report or {}).get("example_count", 0))
    model_path = None if not model_report else model_report.get("model_path")
    top_actions = _top_action_labels(verification)
    scaling_readiness = (model_report or {}).get("scaling_law_readiness") or {}
    accepted_claims = int((verification or {}).get("accepted_claim_count", 0))
    total_claims = int((verification or {}).get("total_claim_count", 0))

    has_large_model = _is_large_proof_model(model_report, min_model_parameters, min_train_steps)
    checks = [
        _check(
            "proof_corpus_report_exists",
            bool(corpus_report)
            and corpus_report.get("schema")
            in {"collatz_lab.proof_corpus_report", "collatz_lab.scaled_proof_corpus_report"},
            path=str(corpus_report_path),
            schema=None if corpus_report is None else corpus_report.get("schema"),
        ),
        _check(
            "proof_corpus_jsonl_matches_report",
            row_count is not None and row_count == corpus_examples,
            path=str(corpus_jsonl),
            jsonl_rows=row_count,
            report_examples=corpus_examples,
        ),
        _check(
            "proof_corpus_large_enough_for_scaling_run",
            corpus_examples >= min_examples,
            examples=corpus_examples,
            minimum=min_examples,
        ),
        _check(
            "general_formal_proof_stream_large_enough",
            _stream_count(corpus_report, "general_formal_proof") >= min_general_formal,
            examples=_stream_count(corpus_report, "general_formal_proof"),
            minimum=min_general_formal,
        ),
        _check(
            "collatz_structural_stream_large_enough",
            _stream_count(corpus_report, "collatz_structural") >= min_collatz_structural,
            examples=_stream_count(corpus_report, "collatz_structural"),
            minimum=min_collatz_structural,
        ),
        _check(
            "verifier_replay_stream_large_enough",
            _stream_count(corpus_report, "verifier_replay") >= min_verifier_replay,
            examples=_stream_count(corpus_report, "verifier_replay"),
            minimum=min_verifier_replay,
        ),
        _check(
            "proof_inventor_training_report_exists",
            bool(model_report)
            and model_report.get("schema")
            in {
                "collatz_lab.proof_inventor_training_report",
                "collatz_lab.proof_transformer_training_report",
            },
            path=str(model_report_path),
            schema=None if model_report is None else model_report.get("schema"),
            status=None if model_report is None else model_report.get("status"),
        ),
        _check(
            "proof_inventor_checkpoint_exists",
            _exists(model_path),
            path=model_path,
        ),
        _check(
            "trained_on_same_corpus_size",
            bool(model_report) and model_examples == corpus_examples and model_examples > 0,
            corpus_examples=corpus_examples,
            model_examples=model_examples,
        ),
        _check(
            "proof_model_is_scaling_target_not_bootstrap",
            allow_bootstrap_model or has_large_model,
            model_kind=None if model_report is None else model_report.get("model_kind"),
            status=None if model_report is None else model_report.get("status"),
            parameter_count=None if model_report is None else model_report.get("parameter_count"),
            train_steps_completed=None
            if model_report is None
            else model_report.get("train_steps_completed", model_report.get("training_steps", model_report.get("step"))),
            min_model_parameters=min_model_parameters,
            min_train_steps=min_train_steps,
            allow_bootstrap_model=allow_bootstrap_model,
        ),
        _check(
            "all_training_streams_present",
            all(
                bool(scaling_readiness.get(key))
                for key in [
                    "has_general_proof_stream",
                    "has_collatz_structural_stream",
                    "has_verifier_replay_stream",
                ]
            ),
            scaling_law_readiness=scaling_readiness,
        ),
        _check(
            "dry_run_proposal_exists",
            bool(proposal)
            and proposal.get("schema") == "collatz_lab.model_proof_proposal"
            and bool(proposal.get("proof_text")),
            path=str(proposal_path),
            schema=None if proposal is None else proposal.get("schema"),
        ),
        _check(
            "dry_run_verification_exists",
            bool(verification) and verification.get("schema") == "collatz_lab.model_proof_verification",
            path=str(verification_path),
            schema=None if verification is None else verification.get("schema"),
            status=None if verification is None else verification.get("status"),
        ),
        _check(
            "proof_confidence_is_verifier_gated",
            _proof_confidence_is_honest(verification),
            verifier_status=None if verification is None else verification.get("status"),
            proof_confidence_percent=None if verification is None else verification.get("proof_confidence_percent"),
        ),
        _check(
            "proof_candidate_has_verifier_accepted_claim",
            accepted_claims > 0 and total_claims >= accepted_claims,
            accepted_claim_count=accepted_claims,
            total_claim_count=total_claims,
        ),
        _check(
            "model_targets_current_math_blocker",
            "TRY_MIXED_MODULUS_DEBT_VERIFIER" in top_actions[:3],
            top_actions=top_actions[:6],
        ),
        _check(
            "exact_high_parent_successor_family_available",
            bool(high_parent_bypass)
            and high_parent_bypass.get("schema") == "collatz_lab.high_parent_bypass"
            and high_parent_bypass.get("status") == "MIXED_MODULUS_BYPASS_BUILT"
            and high_parent_bypass.get("all_sample_checks_passed") is True,
            path=str(high_parent_bypass_path),
            status=None if high_parent_bypass is None else high_parent_bypass.get("status"),
            mixed_successor_family_count=None
            if high_parent_bypass is None
            else high_parent_bypass.get("mixed_successor_family_count"),
            all_sample_checks_passed=None
            if high_parent_bypass is None
            else high_parent_bypass.get("all_sample_checks_passed"),
        ),
        _check(
            "mixed_modulus_debt_verifier_available",
            _debt_verifier_ready(debt_verifier),
            path=str(mixed_modulus_debt_verifier_path),
            schema=None if debt_verifier is None else debt_verifier.get("schema"),
            status=None if debt_verifier is None else debt_verifier.get("status"),
            verifier_available=None if debt_verifier is None else debt_verifier.get("verifier_available"),
            ready_for_run9=None if debt_verifier is None else debt_verifier.get("ready_for_run9"),
            proof_closed=None if debt_verifier is None else debt_verifier.get("proof_closed"),
            transition_count=None if debt_verifier is None else debt_verifier.get("transition_count"),
            exact_transition_checks_passed=None
            if debt_verifier is None
            else debt_verifier.get("exact_transition_checks_passed"),
        ),
    ]

    failed_required = [row for row in checks if row["required"] and row["status"] != "PASS"]
    local_smoke_ready = all(
        row["status"] == "PASS"
        for row in checks
        if row["name"]
        in {
            "proof_corpus_report_exists",
            "proof_corpus_jsonl_matches_report",
            "proof_inventor_training_report_exists",
            "proof_inventor_checkpoint_exists",
            "trained_on_same_corpus_size",
            "all_training_streams_present",
            "dry_run_proposal_exists",
            "dry_run_verification_exists",
            "proof_confidence_is_verifier_gated",
            "proof_candidate_has_verifier_accepted_claim",
            "model_targets_current_math_blocker",
            "exact_high_parent_successor_family_available",
        }
    )
    status = "READY_FOR_RUN9" if not failed_required else "NOT_READY_FOR_RUN9"
    blocking = [row["name"] for row in failed_required]
    if status == "READY_FOR_RUN9":
        next_step = "Launch RUN-009 with the trained proof model and exact proof-evaluation loop."
    elif set(blocking).issubset({"trained_on_same_corpus_size", "proof_model_is_scaling_target_not_bootstrap"}):
        next_step = (
            "Train the full RUN-009 proof Transformer on the scaled corpus until it meets the "
            "parameter-count and training-step gates, then rerun this preflight."
        )
    elif "mixed_modulus_debt_verifier_available" in blocking:
        next_step = (
            "Build the mixed-modulus debt verifier before the serious run, then train the proof model "
            "on its PASS/FAIL/repair traces."
        )
    elif any(name.endswith("_large_enough") or name == "proof_corpus_large_enough_for_scaling_run" for name in blocking):
        next_step = (
            "Expand the proof corpus to the stream thresholds, train a non-bootstrap proof model, "
            "then rerun this preflight."
        )
    else:
        next_step = "Fix the failing RUN-009 readiness checks before treating the next run as scaling-law-ready."
    return {
        "schema": RUN9_PREFLIGHT_SCHEMA,
        "version": 1,
        "status": status,
        "ready_for_run9": status == "READY_FOR_RUN9",
        "local_smoke_ready": local_smoke_ready,
        "thresholds": {
            "min_examples": min_examples,
            "min_general_formal": min_general_formal,
            "min_collatz_structural": min_collatz_structural,
            "min_verifier_replay": min_verifier_replay,
            "min_model_parameters": min_model_parameters,
            "min_train_steps": min_train_steps,
            "allow_bootstrap_model": allow_bootstrap_model,
        },
        "observed": {
            "corpus_examples": corpus_examples,
            "jsonl_rows": row_count,
            "stream_mix": {} if corpus_report is None else corpus_report.get("stream_mix", {}),
            "model_kind": None if model_report is None else model_report.get("model_kind"),
            "model_status": None if model_report is None else model_report.get("status"),
            "top_actions": top_actions[:6],
            "accepted_claim_count": accepted_claims,
            "total_claim_count": total_claims,
            "proof_confidence_percent": None
            if verification is None
            else verification.get("proof_confidence_percent"),
        },
        "checks": checks,
        "blocking_checks": blocking,
        "next_step": next_step,
    }


def write_preflight_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# RUN-009 Preflight",
        "",
        f"- status: `{report['status']}`",
        f"- ready for RUN-009: `{report['ready_for_run9']}`",
        f"- local smoke ready: `{report['local_smoke_ready']}`",
        f"- blocking checks: `{report['blocking_checks']}`",
        f"- thresholds: `{report['thresholds']}`",
        f"- observed: `{report['observed']}`",
        "",
        "## Checks",
        "",
    ]
    for row in report["checks"]:
        lines.append(f"- `{row['name']}`: `{row['status']}`")
    lines.extend(["", "## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the conservative RUN-009 proof-inventor readiness gate.")
    parser.add_argument("--corpus-jsonl", default="data/proof_corpus/collatz_proof_inventor_v1.jsonl")
    parser.add_argument("--corpus-report", default="reports/proof_corpus/collatz_proof_inventor_v1.json")
    parser.add_argument("--model-report", default="reports/proof_inventor/collatz_proof_inventor_v1.json")
    parser.add_argument("--proposal", default="reports/proof_inventor/RUN-009-dryrun-proposal/proof_inventor_proposal.json")
    parser.add_argument(
        "--verification",
        default="reports/proof_inventor/RUN-009-dryrun-proposal/proof_inventor_verification.json",
    )
    parser.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    parser.add_argument("--mixed-modulus-debt-verifier", default="reports/debt_induction/mixed_modulus_debt_verifier.json")
    parser.add_argument("--min-examples", type=int, default=DEFAULT_MIN_EXAMPLES)
    parser.add_argument("--min-general-formal", type=int, default=DEFAULT_MIN_GENERAL_FORMAL)
    parser.add_argument("--min-collatz-structural", type=int, default=DEFAULT_MIN_COLLATZ_STRUCTURAL)
    parser.add_argument("--min-verifier-replay", type=int, default=DEFAULT_MIN_VERIFIER_REPLAY)
    parser.add_argument("--min-model-parameters", type=int, default=DEFAULT_MIN_MODEL_PARAMETERS)
    parser.add_argument("--min-train-steps", type=int, default=DEFAULT_MIN_TRAIN_STEPS)
    parser.add_argument("--allow-bootstrap-model", action="store_true")
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_run9_preflight(
        corpus_jsonl=args.corpus_jsonl,
        corpus_report_path=args.corpus_report,
        model_report_path=args.model_report,
        proposal_path=args.proposal,
        verification_path=args.verification,
        high_parent_bypass_path=args.high_parent_bypass,
        mixed_modulus_debt_verifier_path=args.mixed_modulus_debt_verifier,
        min_examples=args.min_examples,
        min_general_formal=args.min_general_formal,
        min_collatz_structural=args.min_collatz_structural,
        min_verifier_replay=args.min_verifier_replay,
        min_model_parameters=args.min_model_parameters,
        min_train_steps=args.min_train_steps,
        allow_bootstrap_model=args.allow_bootstrap_model,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_preflight_markdown(report, args.out_md or out.with_suffix(".md"))
    Console().print(
        {
            "out": str(out),
            "status": report["status"],
            "ready_for_run9": report["ready_for_run9"],
            "local_smoke_ready": report["local_smoke_ready"],
            "blocking_checks": report["blocking_checks"],
        }
    )


if __name__ == "__main__":
    main()
