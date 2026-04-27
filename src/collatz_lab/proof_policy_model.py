"""Train/evaluate a lightweight proof-action policy from verifier traces."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
from typing import Any

from rich.console import Console
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split

from .proof_actions import ProofAction
from .proof_policy import featurize_obligation
from .proof_trace import ProofTrace, load_traces


def _flatten(prefix: str, value: Any, out: dict[str, Any]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _flatten(f"{prefix}.{key}" if prefix else str(key), child, out)
    elif isinstance(value, (str, int, float, bool)) or value is None:
        out[prefix] = "None" if value is None else value


def trace_features(trace: ProofTrace) -> dict[str, Any]:
    """Return model features for an obligation/action training example."""

    return obligation_action_features(trace.obligation_before, trace.action)


def obligation_action_features(obligation: dict[str, Any], action: ProofAction) -> dict[str, Any]:
    """Return model features for one obligation/action pair."""

    features: dict[str, Any] = {}
    _flatten("obligation", featurize_obligation(obligation), features)
    features["action"] = action.action
    for key, value in action.params.items():
        if isinstance(value, (str, int, float, bool)):
            features[f"action_param.{key}"] = value
    return features


def train_policy_from_traces(traces: list[ProofTrace]) -> dict[str, Any]:
    """Train action and reward predictors from proof traces."""

    if not traces:
        raise ValueError("at least one trace is required")
    features = [trace_features(trace) for trace in traces]
    actions = [trace.action.action for trace in traces]
    rewards = [trace.result.reward for trace in traces]
    vectorizer = DictVectorizer(sparse=True)
    x = vectorizer.fit_transform(features)
    if len(set(actions)) < 2:
        action_model = None
        action_accuracy = None
    else:
        stratify = actions if min(actions.count(label) for label in set(actions)) >= 2 else None
        x_train, x_test, y_train, y_test = train_test_split(
            x,
            actions,
            test_size=0.25,
            random_state=0,
            stratify=stratify,
        )
        action_model = OneVsRestClassifier(LogisticRegression(max_iter=2000, solver="liblinear"))
        action_model.fit(x_train, y_train)
        action_accuracy = float(accuracy_score(y_test, action_model.predict(x_test)))

    x_train, x_test, r_train, r_test = train_test_split(x, rewards, test_size=0.25, random_state=0)
    value_model = Ridge(alpha=1.0)
    value_model.fit(x_train, r_train)
    reward_mae = float(mean_absolute_error(r_test, value_model.predict(x_test)))
    return {
        "status": "TRAINED_PROOF_POLICY_BASELINE",
        "trace_count": len(traces),
        "action_classes": sorted(set(actions)),
        "action_accuracy": action_accuracy,
        "reward_mae": reward_mae,
        "vectorizer": vectorizer,
        "action_model": action_model,
        "value_model": value_model,
    }


def save_policy_model(path: str | Path, model_bundle: dict[str, Any]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as handle:
        pickle.dump(model_bundle, handle)


def load_policy_model(path: str | Path) -> dict[str, Any]:
    with Path(path).open("rb") as handle:
        return pickle.load(handle)


def predict_action_rewards(
    model_bundle: dict[str, Any],
    obligation: dict[str, Any],
    actions: list[ProofAction],
) -> list[float]:
    """Predict verifier reward for candidate proof actions."""

    if not actions:
        return []
    vectorizer = model_bundle.get("vectorizer")
    value_model = model_bundle.get("value_model")
    if vectorizer is None or value_model is None:
        return [0.0 for _ in actions]
    features = [obligation_action_features(obligation, action) for action in actions]
    x = vectorizer.transform(features)
    return [float(value) for value in value_model.predict(x)]


def rerank_actions_with_value_model(
    model_bundle: dict[str, Any],
    obligation: dict[str, Any],
    actions: list[ProofAction],
) -> list[ProofAction]:
    """Return actions sorted by learned reward, preserving the action DSL."""

    predictions = predict_action_rewards(model_bundle, obligation, actions)
    rescored = [
        ProofAction(
            action=action.action,
            params=action.params,
            score=float(predicted),
            rationale=(
                f"value_model_reward={predicted:.3f}; heuristic_score={action.score:.3f}; "
                f"{action.rationale}"
            ),
        )
        for action, predicted in zip(actions, predictions)
    ]
    rescored.sort(key=lambda action: action.score, reverse=True)
    return rescored


def build_training_report(model_bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": model_bundle["status"],
        "trace_count": model_bundle["trace_count"],
        "action_classes": model_bundle["action_classes"],
        "action_accuracy": model_bundle["action_accuracy"],
        "reward_mae": model_bundle["reward_mae"],
        "model_kind": "DictVectorizer + OneVsRest(LogisticRegression)/Ridge baseline",
        "proof_progress_metric": "verified action/reward prediction, not Collatz sequence accuracy",
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a lightweight proof-policy model from JSONL traces.")
    parser.add_argument("--traces", required=True)
    parser.add_argument("--model-out", required=True)
    parser.add_argument("--report-out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    bundle = train_policy_from_traces(load_traces(args.traces))
    save_policy_model(args.model_out, bundle)
    report = build_training_report(bundle)
    out = Path(args.report_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print(report)


if __name__ == "__main__":
    main()
