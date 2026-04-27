"""Train and run a bootstrap Collatz proof-inventor model.

The scalable target is a shared proof/dynamics Transformer, but local RUN-009
readiness needs a fast baseline that consumes the same corpus and emits the same
typed proof objects.  This module trains a retrieval/classifier proof inventor:
it learns task/action/outcome labels from proof-corpus examples and uses nearest
training examples to assemble a verifier-checkable proof proposal beam.
"""

from __future__ import annotations

import argparse
import json
import pickle
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors

from .proof_dsl_model import (
    MODEL_PROOF_PROPOSAL_SCHEMA,
    build_model_proof_proposal,
    verify_model_proof_proposal,
    write_proposal_markdown,
    write_verification_markdown,
)


PROOF_INVENTOR_MODEL_SCHEMA = "collatz_lab.proof_inventor_model"
PROOF_INVENTOR_REPORT_SCHEMA = "collatz_lab.proof_inventor_training_report"


def _jsonl_rows(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _text(row: dict[str, Any]) -> str:
    tags = " ".join(str(tag) for tag in row.get("tags", []))
    return "\n".join(
        [
            f"task={row.get('task')}",
            f"source={row.get('source')}",
            f"tags={tags}",
            f"verifier_status={row.get('verifier_status')}",
            str(row.get("prompt", "")),
        ]
    )


def _train_classifier(x: Any, labels: list[str]) -> tuple[LogisticRegression | None, dict[str, Any]]:
    counts = Counter(labels)
    if len(counts) < 2:
        return None, {"status": "SKIPPED_SINGLE_CLASS", "label_counts": dict(counts)}
    model = LogisticRegression(max_iter=2000, solver="lbfgs")
    model.fit(x, labels)
    train_acc = float(accuracy_score(labels, model.predict(x)))
    heldout_acc = None
    if len(labels) >= 8:
        stratify = labels if min(counts.values()) >= 2 else None
        x_train, x_test, y_train, y_test = train_test_split(
            x,
            labels,
            test_size=0.30,
            random_state=9,
            stratify=stratify,
        )
        heldout = LogisticRegression(max_iter=2000, solver="lbfgs")
        heldout.fit(x_train, y_train)
        heldout_acc = float(accuracy_score(y_test, heldout.predict(x_test)))
    return model, {
        "status": "TRAINED",
        "label_counts": dict(counts),
        "train_accuracy": train_acc,
        "heldout_accuracy": heldout_acc,
    }


def train_proof_inventor(
    corpus_path: str | Path,
    max_features: int = 12000,
    max_examples: int | None = None,
) -> dict[str, Any]:
    examples = _jsonl_rows(corpus_path)
    if max_examples is not None:
        examples = examples[:max_examples]
    if not examples:
        raise ValueError("proof-inventor corpus is empty")
    texts = [_text(row) for row in examples]
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 6),
        max_features=max_features,
        lowercase=False,
    )
    x = vectorizer.fit_transform(texts)
    action_model, action_metrics = _train_classifier(x, [str(row.get("label", "UNKNOWN")) for row in examples])
    task_model, task_metrics = _train_classifier(x, [str(row.get("task", "UNKNOWN")) for row in examples])
    outcome_model, outcome_metrics = _train_classifier(x, [str(row.get("verifier_status", "UNKNOWN")) for row in examples])
    neighbors = NearestNeighbors(n_neighbors=min(8, len(examples)), metric="cosine")
    neighbors.fit(x)
    return {
        "schema": PROOF_INVENTOR_MODEL_SCHEMA,
        "version": 1,
        "status": "TRAINED_BOOTSTRAP_COLLATZ_PROOF_INVENTOR",
        "model_kind": "Tfidf char n-gram retrieval + LogisticRegression task/action/outcome heads",
        "architecture_target": (
            "shared Transformer over proof DSL, verifier traces, and Collatz structure; "
            "this local model is a fast baseline over the same corpus schema"
        ),
        "corpus_path": str(corpus_path),
        "example_count": len(examples),
        "task_counts": dict(Counter(str(row.get("task")) for row in examples)),
        "source_counts": dict(Counter(str(row.get("source")) for row in examples)),
        "action_metrics": action_metrics,
        "task_metrics": task_metrics,
        "outcome_metrics": outcome_metrics,
        "vectorizer": vectorizer,
        "action_model": action_model,
        "task_model": task_model,
        "outcome_model": outcome_model,
        "neighbors": neighbors,
        "examples": examples,
        "texts": texts,
    }


def save_model(bundle: dict[str, Any], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as handle:
        pickle.dump(bundle, handle)


def load_model(path: str | Path) -> dict[str, Any]:
    with Path(path).open("rb") as handle:
        return pickle.load(handle)


def serializable_training_report(bundle: dict[str, Any]) -> dict[str, Any]:
    source_counts = bundle["source_counts"]
    collatz_structural_count = (
        source_counts.get("high_parent_bypass", 0)
        + source_counts.get("cycle_mining", 0)
        + source_counts.get("mixed_modulus_debt_verifier", 0)
        + source_counts.get("synthetic_high_parent_successor", 0)
    )
    verifier_replay_count = (
        source_counts.get("proof_attempt_replay", 0)
        + source_counts.get("mixed_modulus_debt_verifier", 0)
        + source_counts.get("synthetic_verifier_replay", 0)
        + source_counts.get("strict_theorem_verifier", 0)
        + source_counts.get("run_preflight", 0)
    )
    return {
        "schema": PROOF_INVENTOR_REPORT_SCHEMA,
        "version": 1,
        "status": bundle["status"],
        "model_kind": bundle["model_kind"],
        "architecture_target": bundle["architecture_target"],
        "corpus_path": bundle["corpus_path"],
        "example_count": bundle["example_count"],
        "task_counts": bundle["task_counts"],
        "source_counts": bundle["source_counts"],
        "action_metrics": bundle["action_metrics"],
        "task_metrics": bundle["task_metrics"],
        "outcome_metrics": bundle["outcome_metrics"],
        "scaling_law_readiness": {
            "has_general_proof_stream": any("formal" in source for source in source_counts),
            "has_collatz_structural_stream": collatz_structural_count > 0,
            "has_verifier_replay_stream": verifier_replay_count > 0,
            "collatz_structural_count": collatz_structural_count,
            "verifier_replay_count": verifier_replay_count,
            "shared_target": "proof DSL + repair action + verifier outcome",
        },
    }


def _predict_head(bundle: dict[str, Any], model_name: str, text: str, top_k: int = 6) -> list[dict[str, Any]]:
    model = bundle.get(model_name)
    vectorizer = bundle["vectorizer"]
    x = vectorizer.transform([text])
    if model is None:
        return []
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(x)[0]
        return [
            {"label": str(label), "score": float(score)}
            for label, score in sorted(zip(model.classes_, probs, strict=True), key=lambda row: row[1], reverse=True)[:top_k]
        ]
    return [{"label": str(model.predict(x)[0]), "score": 1.0}]


def nearest_examples(bundle: dict[str, Any], prompt: str, top_k: int = 5) -> list[dict[str, Any]]:
    vectorizer = bundle["vectorizer"]
    x = vectorizer.transform([prompt])
    distances, indices = bundle["neighbors"].kneighbors(x, n_neighbors=min(top_k, len(bundle["examples"])))
    rows = []
    for distance, index in zip(distances[0], indices[0], strict=True):
        example = dict(bundle["examples"][int(index)])
        rows.append(
            {
                "example_id": example.get("example_id"),
                "source": example.get("source"),
                "task": example.get("task"),
                "label": example.get("label"),
                "verifier_status": example.get("verifier_status"),
                "distance": float(distance),
                "target": example.get("target"),
            }
        )
    return rows


def build_run9_prompt(high_parent_bypass: dict[str, Any] | None, preflight: dict[str, Any] | None) -> str:
    rank = {} if not high_parent_bypass else dict(high_parent_bypass.get("level_rank_analysis") or {})
    return "\n".join(
        [
            "<TASK=RUN9_PROOF_INVENTION>",
            "<GOAL=generate new typed proof program>",
            f"high_parent_status={None if not high_parent_bypass else high_parent_bypass.get('status')}",
            f"mixed_successor_family_count={0 if not high_parent_bypass else high_parent_bypass.get('mixed_successor_family_count')}",
            f"rank_status={rank.get('status')}",
            f"cycle_log_gain_sum={rank.get('cycle_log_gain_sum')}",
            f"blocking_checks={[] if not preflight else preflight.get('blocking_checks', [])}",
            "emit definitions, lemmas, debt update law target, proof actions, and verifier expectations",
        ]
    )


def propose_proof(
    bundle: dict[str, Any],
    run_id: str,
    high_parent_bypass: dict[str, Any] | None,
    preflight: dict[str, Any] | None,
    theorem_candidate: dict[str, Any] | None,
    beam_size: int = 6,
) -> dict[str, Any]:
    prompt = build_run9_prompt(high_parent_bypass, preflight)
    action_predictions = _predict_head(bundle, "action_model", prompt, top_k=beam_size)
    task_predictions = _predict_head(bundle, "task_model", prompt, top_k=beam_size)
    outcome_predictions = _predict_head(bundle, "outcome_model", prompt, top_k=beam_size)
    neighbors = nearest_examples(bundle, prompt, top_k=beam_size)
    proposal = build_model_proof_proposal(run_id, bundle, high_parent_bypass, preflight)
    proposal["schema"] = MODEL_PROOF_PROPOSAL_SCHEMA
    proposal["author"] = "collatz_proof_inventor_v1"
    proposal["model_status"] = bundle["status"]
    proposal["proof_text"] = (
        "Proof-inventor proposal: combine retrieved exact high-parent successor proofs, "
        "return-map height proof patterns, and verifier replay failures.  The next proof object "
        "keeps the mixed-modulus state from RUN-008, but explicitly makes the missing target a "
        "debt update law over M(a,rho,m,delta), because scalar parent-level ranking is already falsified."
    )
    proposal["proof_dsl"]["strategy"] = {
        "model": "collatz_proof_inventor_v1",
        "action_predictions": action_predictions,
        "task_predictions": task_predictions,
        "outcome_predictions": outcome_predictions,
        "nearest_training_examples": neighbors,
        "beam_size": beam_size,
    }
    proposal["proof_dsl"]["lemmas"].insert(
        3,
        {
            "lemma_id": "L-MM3b-debt-update-law-target",
            "kind": "missing_symbolic_program",
            "statement": (
                "Find an exact update law delta' = F(delta,a,rho,m,T) such that the mixed-modulus "
                "rank decreases on every high-parent successor family, including the P20/P23 cycle."
            ),
            "evidence_refs": ["reports/debt_induction/high_parent_bypass_report.json"],
            "expected_verifier_status": "OPEN_TARGET_FOR_RUN9",
            "retrieval_support": neighbors[:3],
        },
    )
    verification = verify_model_proof_proposal(proposal, high_parent_bypass, theorem_candidate)
    verification["proof_inventor_predictions"] = {
        "actions": action_predictions,
        "tasks": task_predictions,
        "outcomes": outcome_predictions,
        "nearest_examples": neighbors,
    }
    return {"proposal": proposal, "verification": verification}


def write_training_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Collatz Proof Inventor",
        "",
        f"- status: `{report['status']}`",
        f"- model kind: `{report['model_kind']}`",
        f"- examples: `{report['example_count']}`",
        f"- task counts: `{report['task_counts']}`",
        f"- source counts: `{report['source_counts']}`",
        f"- action metrics: `{report['action_metrics']}`",
        f"- task metrics: `{report['task_metrics']}`",
        f"- outcome metrics: `{report['outcome_metrics']}`",
        f"- scaling readiness: `{report['scaling_law_readiness']}`",
        "",
    ]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train/run a bootstrap Collatz proof-inventor model.")
    sub = parser.add_subparsers(dest="command", required=True)

    train = sub.add_parser("train")
    train.add_argument("--corpus", required=True)
    train.add_argument("--model-out", required=True)
    train.add_argument("--report-out", required=True)
    train.add_argument("--report-md", default=None)
    train.add_argument("--max-features", type=int, default=12000)
    train.add_argument("--max-examples", type=int, default=None)

    propose = sub.add_parser("propose")
    propose.add_argument("--model", required=True)
    propose.add_argument("--run-id", default="RUN-009-collatz-proof-inventor-v1")
    propose.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    propose.add_argument("--preflight", default="reports/run7_preflight.json")
    propose.add_argument("--theorem-candidate", default="reports/collatz_descent_theorem_candidate.json")
    propose.add_argument("--beam-size", type=int, default=6)
    propose.add_argument("--out-dir", required=True)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.command == "train":
        bundle = train_proof_inventor(args.corpus, max_features=args.max_features, max_examples=args.max_examples)
        save_model(bundle, args.model_out)
        report = serializable_training_report(bundle)
        report["model_path"] = str(args.model_out)
        out = Path(args.report_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_training_markdown(report, args.report_md or out.with_suffix(".md"))
        Console().print({"model": args.model_out, "report": args.report_out, "examples": report["example_count"]})
        return

    if args.command == "propose":
        bundle = load_model(args.model)
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        result = propose_proof(
            bundle,
            run_id=args.run_id,
            high_parent_bypass=_load_json(args.high_parent_bypass),
            preflight=_load_json(args.preflight),
            theorem_candidate=_load_json(args.theorem_candidate),
            beam_size=args.beam_size,
        )
        proposal_path = out_dir / "proof_inventor_proposal.json"
        verification_path = out_dir / "proof_inventor_verification.json"
        proposal_path.write_text(json.dumps(result["proposal"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        verification_path.write_text(json.dumps(result["verification"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_proposal_markdown(result["proposal"], out_dir / "proof_inventor_proposal.md")
        write_verification_markdown(result["verification"], out_dir / "proof_inventor_verification.md")
        Console().print(
            {
                "proposal": str(proposal_path),
                "verification": str(verification_path),
                "accepted_claims": result["verification"]["accepted_claim_count"],
                "proof_confidence": result["verification"]["proof_confidence_percent"],
            }
        )
        return


if __name__ == "__main__":
    main()
