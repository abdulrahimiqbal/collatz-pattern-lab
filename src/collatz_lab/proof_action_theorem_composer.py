"""RUN-016 theorem composition with a frozen proof-action selector.

This module does not train a policy.  It loads the current RUN-015A selector,
builds an explicit theorem dependency graph, asks the selector to order actions
for open graph nodes, verifier-checks every proposed action, and reruns the
strict theorem verifier after each accepted action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import torch
from rich.console import Console

from .proof_action_decode import dedupe_candidates, legal_action_candidates_from_state, verify_action_for_state
from .proof_action_dsl import ProofActionError, parse_action, serialize_action
from .proof_action_model import load_checkpoint, score_candidate_selector_components
from .proof_action_s6_analyzer import analyze_s6_blockers
from .proof_verifier import build_collatz_descent_theorem_candidate
from .utils import load_yaml


GRAPH_NODE_TYPES = (
    "S3_TRANSITION",
    "S4_LIFT",
    "S6_LEMMA",
    "COVERAGE_CERTIFICATE",
    "INDUCTION_CLOSURE",
    "NO_ESCAPE_CERTIFICATE",
    "STRICT_THEOREM_BLOCKER",
)

REQUIRED_ACTION_TYPES = {
    "S3_TRANSITION": {"CHECK_DEBT_DECREASE"},
    "S4_LIFT": {"DERIVE_PARENT_TRANSITION", "LIFT_LOCAL_TO_PARAMETRIC_FAMILY"},
    "S6_LEMMA": {"VERIFY_S6_LEMMA"},
    "COVERAGE_CERTIFICATE": {"PROVE_RESIDUE_COVERAGE", "PROVE_RESIDUAL_COVERAGE", "PROVE_PARENT_RESIDUAL_COVERAGE"},
    "INDUCTION_CLOSURE": {"CLOSE_WELL_FOUNDED_INDUCTION", "PROVE_GLOBAL_DESCENT_INDUCTION"},
    "NO_ESCAPE_CERTIFICATE": {"CERTIFY_NO_ESCAPE_BRANCH"},
    "STRICT_THEOREM_BLOCKER": {"CLOSE_STRICT_THEOREM_BLOCKER", "COMPOSE_GATE_PROOF"},
}


def _digest(data: Any, size: int = 16) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:size]


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _parse_candidate_action(item: dict[str, Any]) -> dict[str, Any] | None:
    action = item.get("action", item)
    try:
        if isinstance(action, str):
            return parse_action(action)
        if isinstance(action, dict):
            return parse_action(serialize_action(action))
    except (ProofActionError, TypeError, ValueError):
        return None
    return None


def _row_candidate_actions(row: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for item in row.get("candidate_actions") or []:
        if isinstance(item, dict):
            action = _parse_candidate_action(item)
            if action is not None:
                actions.append(action)
    for item in row.get("candidates") or []:
        if isinstance(item, dict):
            action = _parse_candidate_action(item)
            if action is not None:
                actions.append(action)
    return actions


def _has_verifiable_required_action(row: dict[str, Any], required_action_types: set[str]) -> bool:
    state = str(row.get("state", ""))
    for action in _row_candidate_actions(row):
        if str(action.get("type", "")) not in required_action_types:
            continue
        if verify_action_for_state(action, state).accepted:
            return True
    return False


def _node(
    *,
    node_id: str,
    node_type: str,
    state: str,
    candidate_actions: list[dict[str, Any]],
    source: dict[str, Any],
    depends_on: list[str] | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if node_type not in GRAPH_NODE_TYPES:
        raise ValueError(f"unknown theorem graph node type: {node_type}")
    return {
        "node_id": node_id,
        "node_type": node_type,
        "status": "OPEN",
        "depends_on": list(depends_on or []),
        "state": state,
        "candidate_actions": dedupe_candidates(candidate_actions),
        "required_action_types": sorted(REQUIRED_ACTION_TYPES[node_type]),
        "source": source,
        "evidence": dict(evidence or {}),
        "accepted_actions": [],
        "rejected_actions": [],
        "tried_action_texts": [],
    }


def _add_node(graph: dict[str, Any], node: dict[str, Any]) -> None:
    graph["nodes"][node["node_id"]] = node
    for dep in node.get("depends_on", []):
        graph["edges"].append({"from": dep, "to": node["node_id"], "kind": "requires"})


def build_theorem_dependency_graph(
    *,
    frontier_dir: str | Path = "data/proof_action_v2_frontier_eval",
    s6_dir: str | Path = "data/proof_action_v2_s6",
    max_s3_nodes: int | None = None,
    max_s4_nodes: int | None = None,
    max_s6_blockers: int | None = None,
) -> dict[str, Any]:
    """Build the typed theorem dependency graph consumed by RUN-016."""

    frontier = Path(frontier_dir)
    s6_path = Path(s6_dir)
    if not (s6_path / "s6_blockers.jsonl").exists():
        analyze_s6_blockers(out=s6_path)

    graph: dict[str, Any] = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {},
        "edges": [],
        "sources": {
            "frontier_dir": str(frontier),
            "s6_dir": str(s6_path),
        },
    }

    for row in _load_jsonl(frontier / "s3_frontier.jsonl")[:max_s3_nodes]:
        if not _has_verifiable_required_action(row, REQUIRED_ACTION_TYPES["S3_TRANSITION"]):
            continue
        node_id = f"s3:{row.get('example_id') or _digest(row)}"
        _add_node(
            graph,
            _node(
                node_id=node_id,
                node_type="S3_TRANSITION",
                state=str(row["state"]),
                candidate_actions=_row_candidate_actions(row),
                source={"kind": "frontier_row", "gate": "S3", "example_id": row.get("example_id")},
                evidence={"target_action_text": row.get("target_action_text")},
            ),
        )

    for row in _load_jsonl(frontier / "s4_lifting_frontier.jsonl")[:max_s4_nodes]:
        if not _has_verifiable_required_action(row, REQUIRED_ACTION_TYPES["S4_LIFT"]):
            continue
        node_id = f"s4:{row.get('example_id') or _digest(row)}"
        _add_node(
            graph,
            _node(
                node_id=node_id,
                node_type="S4_LIFT",
                state=str(row["state"]),
                candidate_actions=_row_candidate_actions(row),
                source={"kind": "frontier_row", "gate": "S4", "example_id": row.get("example_id")},
                evidence={"target_action_text": row.get("target_action_text")},
            ),
        )

    for blocker in _load_jsonl(s6_path / "s6_blockers.jsonl")[:max_s6_blockers]:
        blocker_id = str(blocker["blocker_id"])
        lemma_id = str(blocker["lemma_id"])
        coverage_id = str(blocker["coverage_certificate"])
        lift_id = str(blocker["lifting_certificate"])
        induction_id = str(blocker["base_case_certificate"])
        no_escape_id = str(blocker["no_escape_certificate"])
        actions = _row_candidate_actions(blocker)
        common_source = {
            "kind": "s6_blocker",
            "blocker_id": blocker_id,
            "blocker_type": blocker.get("blocker_type"),
            "target": blocker.get("target"),
        }
        common_evidence = {
            "lemma_id": lemma_id,
            "coverage_certificate": coverage_id,
            "lifting_certificate": lift_id,
            "base_case_certificate": induction_id,
            "no_escape_certificate": no_escape_id,
        }

        lemma_node = f"s6_lemma:{lemma_id}"
        coverage_node = f"coverage:{coverage_id}"
        lift_node = f"s6_lift:{lift_id}"
        induction_node = f"induction:{induction_id}"
        no_escape_node = f"no_escape:{no_escape_id}"
        strict_node = f"strict_blocker:{blocker_id}"

        _add_node(
            graph,
            _node(
                node_id=lemma_node,
                node_type="S6_LEMMA",
                state=str(blocker["state"]),
                candidate_actions=actions,
                source=common_source,
                evidence=common_evidence,
            ),
        )
        _add_node(
            graph,
            _node(
                node_id=coverage_node,
                node_type="COVERAGE_CERTIFICATE",
                state=str(blocker["state"]),
                candidate_actions=actions,
                source=common_source,
                evidence=common_evidence,
            ),
        )
        _add_node(
            graph,
            _node(
                node_id=lift_node,
                node_type="S4_LIFT",
                state=str(blocker["state"]),
                candidate_actions=actions,
                source=common_source,
                evidence=common_evidence,
            ),
        )
        _add_node(
            graph,
            _node(
                node_id=induction_node,
                node_type="INDUCTION_CLOSURE",
                state=str(blocker["state"]),
                candidate_actions=actions,
                source=common_source,
                depends_on=[lemma_node],
                evidence=common_evidence,
            ),
        )
        _add_node(
            graph,
            _node(
                node_id=no_escape_node,
                node_type="NO_ESCAPE_CERTIFICATE",
                state=str(blocker["state"]),
                candidate_actions=actions,
                source=common_source,
                evidence=common_evidence,
            ),
        )
        _add_node(
            graph,
            _node(
                node_id=strict_node,
                node_type="STRICT_THEOREM_BLOCKER",
                state=str(blocker["state"]),
                candidate_actions=actions,
                source=common_source,
                depends_on=[lemma_node, coverage_node, lift_node, induction_node, no_escape_node],
                evidence={**common_evidence, "strict_blocker_id": blocker_id},
            ),
        )

    return graph


def _candidate_pool(node: dict[str, Any], *, beam_width: int, candidates_per_node: int) -> list[dict[str, Any]]:
    candidates = list(node.get("candidate_actions") or [])
    candidates.extend(legal_action_candidates_from_state(str(node["state"]), max_candidates=beam_width))
    return dedupe_candidates(candidates, max_candidates=candidates_per_node)


def selector_order_for_node(
    *,
    model: Any,
    tokenizer: Any,
    node: dict[str, Any],
    beam_width: int,
    candidates_per_node: int,
    max_candidate_pair_len: int,
) -> list[dict[str, Any]]:
    """Order one graph node's candidate actions with the frozen selector."""

    actions = _candidate_pool(node, beam_width=beam_width, candidates_per_node=candidates_per_node)
    texts = [serialize_action(action) for action in actions]
    if not texts:
        return []
    components = score_candidate_selector_components(
        model,
        tokenizer,
        str(node["state"]),
        texts,
        max_candidate_pair_len=max_candidate_pair_len,
    )
    ordered = []
    for action, text, scores in zip(actions, texts, components, strict=True):
        ordered.append(
            {
                "action": action,
                "action_text": text,
                "score": float(scores.get("selector_score", 0.0) or 0.0),
                "model_scores": scores,
            }
        )
    ordered.sort(key=lambda item: item["score"], reverse=True)
    return ordered


def _deps_satisfied(graph: dict[str, Any], node: dict[str, Any]) -> bool:
    nodes = graph["nodes"]
    return all(nodes.get(dep, {}).get("status") == "ACCEPTED" for dep in node.get("depends_on", []))


def _action_solves_node(node: dict[str, Any], action: dict[str, Any], check: Any) -> bool:
    action_type = str(action.get("type", ""))
    required = REQUIRED_ACTION_TYPES[str(node["node_type"])]
    if action_type not in required or not check.accepted:
        return False
    if node["node_type"] == "S6_LEMMA":
        return action_type == "VERIFY_S6_LEMMA" and float(check.progress or 0.0) >= 0.8
    if node["node_type"] == "NO_ESCAPE_CERTIFICATE":
        return action_type == "CERTIFY_NO_ESCAPE_BRANCH" and float(check.progress or 0.0) >= 0.6
    if node["node_type"] == "COVERAGE_CERTIFICATE":
        return action_type in {"PROVE_RESIDUE_COVERAGE", "PROVE_RESIDUAL_COVERAGE", "PROVE_PARENT_RESIDUAL_COVERAGE"} and float(check.progress or 0.0) >= 0.7
    return float(check.progress or 0.0) > 0.0


def _open_node_ids(graph: dict[str, Any]) -> list[str]:
    return [node_id for node_id, node in graph["nodes"].items() if node.get("status") != "ACCEPTED"]


def run_strict_theorem_verifier(graph: dict[str, Any]) -> dict[str, Any]:
    """Run the existing strict theorem verifier over the current graph state."""

    proof_graph = {
        "schema": graph["schema"],
        "version": graph["version"],
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "open": _open_node_ids(graph),
    }
    proof = build_collatz_descent_theorem_candidate(proof_graph=proof_graph)
    verification = proof.get("verification", {})
    return {
        "verifier_status": proof.get("verifier_status", verification.get("verifier_status", "FAIL")),
        "proof_confidence_percent": 100.0 if proof.get("verifier_status") == "PASS" else 0.0,
        "unknown_count": verification.get("unknown_count", len(proof.get("unknown_obligations", []))),
        "errors": list(verification.get("errors", [])),
        "minimal_blocking_set": list(proof.get("minimal_blocking_set", [])),
        "proof": proof,
    }


def _graph_fingerprint(graph: dict[str, Any]) -> str:
    compact = {
        node_id: {
            "status": node.get("status"),
            "accepted": [item.get("action_text") for item in node.get("accepted_actions", [])],
            "rejected": [item.get("action_text") for item in node.get("rejected_actions", [])],
        }
        for node_id, node in graph["nodes"].items()
    }
    return _digest(compact, size=32)


def compose_theorem_graph(
    *,
    graph: dict[str, Any],
    model: Any,
    tokenizer: Any,
    beam_width: int = 64,
    candidates_per_node: int = 50,
    max_candidate_pair_len: int = 2176,
    max_actions_per_node: int = 12,
    max_iterations: int = 8,
) -> dict[str, Any]:
    """Run selector-guided, verifier-checked theorem composition to fixed point."""

    verifier_history: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    proposal_rows: list[dict[str, Any]] = []
    initial = run_strict_theorem_verifier(graph)
    verifier_history.append({"iteration": 0, "after_action": None, **{key: value for key, value in initial.items() if key != "proof"}})
    if initial["verifier_status"] == "PASS":
        return {
            "status": "STRICT_VERIFIER_PASS",
            "graph": graph,
            "accepted_actions": accepted_rows,
            "rejected_actions": rejected_rows,
            "proposal_trace": proposal_rows,
            "strict_theorem_verifier_history": verifier_history,
            "final_verifier": initial,
            "iterations": 0,
            "fixed_point": False,
        }

    previous_fingerprint = _graph_fingerprint(graph)
    exhausted_nodes: set[str] = set()
    for iteration in range(1, max_iterations + 1):
        accepted_node_count_before = sum(1 for node in graph["nodes"].values() if node.get("status") == "ACCEPTED")
        for node_id, node in list(graph["nodes"].items()):
            if node.get("status") == "ACCEPTED" or node_id in exhausted_nodes:
                continue
            if not _deps_satisfied(graph, node):
                node["status"] = "BLOCKED"
                continue
            if node.get("status") == "BLOCKED":
                node["status"] = "OPEN"

            ordered = selector_order_for_node(
                model=model,
                tokenizer=tokenizer,
                node=node,
                beam_width=beam_width,
                candidates_per_node=candidates_per_node,
                max_candidate_pair_len=max_candidate_pair_len,
            )
            tried = set(node.get("tried_action_texts", []))
            unchecked = [item for item in ordered if item["action_text"] not in tried]
            if not unchecked:
                exhausted_nodes.add(node_id)
                continue
            checked_this_node = 0
            for item in unchecked:
                if checked_this_node >= max_actions_per_node:
                    break
                checked_this_node += 1
                action = item["action"]
                action_text = item["action_text"]
                check = verify_action_for_state(action, str(node["state"]))
                record = {
                    "iteration": iteration,
                    "node_id": node_id,
                    "node_type": node["node_type"],
                    "rank": checked_this_node,
                    "action": action,
                    "action_text": action_text,
                    "selector_score": item["score"],
                    "model_scores": item["model_scores"],
                    "verifier_check": check.to_dict(),
                }
                proposal_rows.append(record)
                node.setdefault("tried_action_texts", []).append(action_text)
                if check.accepted:
                    node.setdefault("accepted_actions", []).append(record)
                    accepted_rows.append(record)
                    if _action_solves_node(node, action, check):
                        node["status"] = "ACCEPTED"
                        node["accepted_action_text"] = action_text
                    verifier = run_strict_theorem_verifier(graph)
                    verifier_history.append(
                        {
                            "iteration": iteration,
                            "after_action": action_text,
                            "node_id": node_id,
                            **{key: value for key, value in verifier.items() if key != "proof"},
                        }
                    )
                    if verifier["verifier_status"] == "PASS":
                        return {
                            "status": "STRICT_VERIFIER_PASS",
                            "graph": graph,
                            "accepted_actions": accepted_rows,
                            "rejected_actions": rejected_rows,
                            "proposal_trace": proposal_rows,
                            "strict_theorem_verifier_history": verifier_history,
                            "final_verifier": verifier,
                            "iterations": iteration,
                            "fixed_point": False,
                        }
                    if node.get("status") == "ACCEPTED":
                        break
                else:
                    node.setdefault("rejected_actions", []).append(record)
                    rejected_rows.append(record)
            if node.get("status") != "ACCEPTED" and checked_this_node < max_actions_per_node:
                exhausted_nodes.add(node_id)

        current_fingerprint = _graph_fingerprint(graph)
        accepted_node_count_after = sum(1 for node in graph["nodes"].values() if node.get("status") == "ACCEPTED")
        no_node_progress = accepted_node_count_after == accepted_node_count_before
        if current_fingerprint == previous_fingerprint or (no_node_progress and len(exhausted_nodes) >= len(_open_node_ids(graph))):
            break
        previous_fingerprint = current_fingerprint

    final_verifier = run_strict_theorem_verifier(graph)
    return {
        "status": "FIXED_POINT",
        "graph": graph,
        "accepted_actions": accepted_rows,
        "rejected_actions": rejected_rows,
        "proposal_trace": proposal_rows,
        "strict_theorem_verifier_history": verifier_history,
        "final_verifier": final_verifier,
        "iterations": max_iterations,
        "fixed_point": True,
    }


def minimal_blocker_report(graph: dict[str, Any], final_verifier: dict[str, Any], *, limit: int = 40) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    nodes = graph["nodes"]
    for node_id, node in nodes.items():
        if node.get("status") == "ACCEPTED":
            continue
        missing_deps = [dep for dep in node.get("depends_on", []) if nodes.get(dep, {}).get("status") != "ACCEPTED"]
        rejected = list(node.get("rejected_actions") or [])
        accepted = list(node.get("accepted_actions") or [])
        last_rejection = rejected[-1]["verifier_check"] if rejected else None
        if missing_deps:
            missing_kind = "blocked_dependency"
        elif rejected:
            missing_kind = "verifier_rejected_required_action"
        elif accepted:
            missing_kind = "accepted_action_did_not_discharge_node"
        else:
            missing_kind = "no_verified_candidate_checked"
        blockers.append(
            {
                "node_id": node_id,
                "node_type": node.get("node_type"),
                "status": node.get("status"),
                "missing_kind": missing_kind,
                "missing_dependency_ids": missing_deps,
                "missing_dependency_types": [nodes.get(dep, {}).get("node_type") for dep in missing_deps],
                "required_action_types": node.get("required_action_types", []),
                "candidate_count": len(node.get("candidate_actions") or []),
                "accepted_action_count": len(accepted),
                "rejected_action_count": len(rejected),
                "last_rejection": last_rejection,
                "evidence": node.get("evidence", {}),
                "source": node.get("source", {}),
            }
        )
    if not blockers:
        for item in final_verifier.get("minimal_blocking_set", []):
            blockers.append(
                {
                    "node_id": item.get("obligation_id", "strict_theorem_verifier"),
                    "node_type": "STRICT_THEOREM_BLOCKER",
                    "status": item.get("status", "UNKNOWN"),
                    "missing_kind": "strict_theorem_verifier_unknown_obligation",
                    "missing_dependency_ids": [],
                    "required_action_types": [],
                    "candidate_count": 0,
                    "accepted_action_count": 0,
                    "rejected_action_count": 0,
                    "last_rejection": None,
                    "evidence": item,
                    "source": {"kind": "strict_theorem_verifier"},
                }
            )
    return blockers[:limit]


def _config(path: str | Path, *, checkpoint: str | None = None, frontier_dir: str | None = None, s6_dir: str | None = None, out: str | None = None) -> dict[str, Any]:
    cfg = load_yaml(path)
    run = cfg.get("run", {})
    model = cfg.get("model", {})
    composer = cfg.get("composer", {})
    evaluation = cfg.get("evaluation", cfg.get("eval", {}))
    output = cfg.get("output", {})
    return {
        "run_id": str(run.get("name") or run.get("id") or "RUN-016-proof-action-v2-theorem-composer"),
        "config_path": str(path),
        "checkpoint": str(checkpoint or model.get("checkpoint") or evaluation.get("checkpoint")),
        "frontier_dir": str(frontier_dir or composer.get("frontier_eval_dir") or evaluation.get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval"),
        "s6_dir": str(s6_dir or composer.get("s6_dir") or "data/proof_action_v2_s6"),
        "out_dir": str(out or composer.get("out_dir") or output.get("dir") or "reports/runs/RUN-016-proof-action-v2-theorem-composer"),
        "beam_width": int(composer.get("beam_width", cfg.get("search", {}).get("beam_width", 64))),
        "candidates_per_node": int(composer.get("candidates_per_node", cfg.get("search", {}).get("candidates_per_state", 50))),
        "max_actions_per_node": int(composer.get("max_actions_per_node", 12)),
        "max_iterations": int(composer.get("max_iterations", 8)),
        "max_candidate_pair_len": int(model.get("max_candidate_pair_len", 2176)),
        "max_s3_nodes": composer.get("max_s3_nodes"),
        "max_s4_nodes": composer.get("max_s4_nodes"),
        "max_s6_blockers": composer.get("max_s6_blockers"),
    }


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def run_theorem_composer(
    config_path: str | Path,
    *,
    checkpoint: str | None = None,
    frontier_dir: str | None = None,
    s6_dir: str | None = None,
    out: str | None = None,
) -> dict[str, Any]:
    cfg = _config(config_path, checkpoint=checkpoint, frontier_dir=frontier_dir, s6_dir=s6_dir, out=out)
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = build_theorem_dependency_graph(
        frontier_dir=cfg["frontier_dir"],
        s6_dir=cfg["s6_dir"],
        max_s3_nodes=_optional_int(cfg["max_s3_nodes"]),
        max_s4_nodes=_optional_int(cfg["max_s4_nodes"]),
        max_s6_blockers=_optional_int(cfg["max_s6_blockers"]),
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, tokenizer, _checkpoint_payload = load_checkpoint(cfg["checkpoint"], device=device)
    result = compose_theorem_graph(
        graph=graph,
        model=model,
        tokenizer=tokenizer,
        beam_width=cfg["beam_width"],
        candidates_per_node=cfg["candidates_per_node"],
        max_candidate_pair_len=cfg["max_candidate_pair_len"],
        max_actions_per_node=cfg["max_actions_per_node"],
        max_iterations=cfg["max_iterations"],
    )
    final_verifier = result["final_verifier"]
    blockers = minimal_blocker_report(result["graph"], final_verifier)
    node_type_counts = Counter(node["node_type"] for node in result["graph"]["nodes"].values())
    accepted_node_type_counts = Counter(
        node["node_type"] for node in result["graph"]["nodes"].values() if node.get("status") == "ACCEPTED"
    )
    summary = {
        "schema": "collatz_lab.proof_action_theorem_composer_summary",
        "version": 1,
        "run_id": cfg["run_id"],
        "config_path": cfg["config_path"],
        "policy_checkpoint": cfg["checkpoint"],
        "policy_run": "RUN-015A-proof-action-v2-listwise-selector-small-a100",
        "training_launched": False,
        "big_model_launched": False,
        "status": result["status"],
        "fixed_point": bool(result["fixed_point"]),
        "iterations": result["iterations"],
        "strict_theorem_verifier_result": final_verifier["verifier_status"],
        "proof_confidence_percent": final_verifier["proof_confidence_percent"],
        "graph_node_count": len(result["graph"]["nodes"]),
        "accepted_node_count": sum(1 for node in result["graph"]["nodes"].values() if node.get("status") == "ACCEPTED"),
        "open_blocker_count": len(_open_node_ids(result["graph"])),
        "node_type_counts": dict(node_type_counts),
        "accepted_node_type_counts": dict(accepted_node_type_counts),
        "accepted_action_count": len(result["accepted_actions"]),
        "rejected_action_count": len(result["rejected_actions"]),
        "minimal_blocker_report": blockers,
        "artifacts": {
            "theorem_composition_report": str(out_dir / "theorem_composition_report.json"),
            "theorem_dependency_graph": str(out_dir / "theorem_dependency_graph.json"),
            "verified_composition_actions": str(out_dir / "verified_composition_actions.jsonl"),
            "rejected_composition_actions": str(out_dir / "rejected_composition_actions.jsonl"),
            "composition_proposal_trace": str(out_dir / "composition_proposal_trace.jsonl"),
            "strict_theorem_verifier_history": str(out_dir / "strict_theorem_verifier_history.jsonl"),
        },
    }

    graph_for_disk = {**result["graph"], "open": _open_node_ids(result["graph"])}
    (out_dir / "theorem_dependency_graph.json").write_text(json.dumps(graph_for_disk, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "theorem_composition_report.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_jsonl(out_dir / "verified_composition_actions.jsonl", result["accepted_actions"])
    _write_jsonl(out_dir / "rejected_composition_actions.jsonl", result["rejected_actions"])
    _write_jsonl(out_dir / "composition_proposal_trace.jsonl", result["proposal_trace"])
    _write_jsonl(out_dir / "strict_theorem_verifier_history.jsonl", result["strict_theorem_verifier_history"])
    _write_markdown_report(summary, out_dir / "theorem_composition_report.md")
    return summary


def _write_markdown_report(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# RUN-016 Theorem Composition Report",
        "",
        f"- run id: `{summary['run_id']}`",
        f"- policy checkpoint: `{summary['policy_checkpoint']}`",
        f"- status: `{summary['status']}`",
        f"- strict theorem verifier: `{summary['strict_theorem_verifier_result']}`",
        f"- proof confidence: `{summary['proof_confidence_percent']}`%",
        f"- accepted graph nodes: `{summary['accepted_node_count']}` / `{summary['graph_node_count']}`",
        f"- open blockers: `{summary['open_blocker_count']}`",
        "",
        "## Minimal Blockers",
        "",
    ]
    for blocker in summary.get("minimal_blocker_report", [])[:20]:
        lines.append(
            f"- `{blocker['node_id']}` ({blocker['node_type']}): "
            f"`{blocker['missing_kind']}`; required `{','.join(blocker.get('required_action_types', []))}`"
        )
    lines.extend(["", "This report was produced without selector retraining or big-model launch.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run RUN-016 proof-action theorem composition.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--frontier-dir", default=None)
    parser.add_argument("--s6-dir", default=None)
    parser.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    summary = run_theorem_composer(
        args.config,
        checkpoint=args.checkpoint,
        frontier_dir=args.frontier_dir,
        s6_dir=args.s6_dir,
        out=args.out,
    )
    Console().print(
        {
            "theorem_composition_report": summary["artifacts"]["theorem_composition_report"],
            "status": summary["status"],
            "strict_theorem_verifier_result": summary["strict_theorem_verifier_result"],
            "open_blocker_count": summary["open_blocker_count"],
        }
    )


if __name__ == "__main__":
    main()
