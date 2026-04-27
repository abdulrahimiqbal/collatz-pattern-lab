"""Persistent proof-obligation closure graph.

The proof controller is allowed to reduce obligations into children, but a
reduction is not proof closure.  This module keeps that accounting durable:
nodes close only by a direct exact certificate or when every child dependency is
closed.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .proof_schema import CLOSED_STATUSES, OPEN_STATUSES, status_is_closed
from .proof_trace import ProofTrace


GRAPH_VERSION = 1


def _node_status(row: dict[str, Any]) -> str:
    return str(row.get("status") or row.get("scc_status") or "UNKNOWN")


def _node_claim(row: dict[str, Any]) -> str:
    return str(row.get("claim") or row.get("transition_rule") or row.get("scope") or "")


def _node_scope(row: dict[str, Any]) -> str:
    return str(row.get("scope") or row.get("claim") or "")


def _normalise_child_status(child: dict[str, Any]) -> str:
    status = _node_status(child)
    if status in CLOSED_STATUSES or status in OPEN_STATUSES:
        return status
    if status.startswith("CLOSED_BY_"):
        return status
    return "NEEDS_SPLIT"


def normalise_obligation(row: dict[str, Any]) -> dict[str, Any]:
    """Convert an obligation-like row into a graph node."""

    oid = str(row.get("obligation_id") or row.get("node_id") or row.get("id"))
    if not oid or oid == "None":
        raise ValueError("obligation row is missing obligation_id")
    status = _node_status(row)
    return {
        "obligation_id": oid,
        "status": status,
        "claim": _node_claim(row),
        "scope": _node_scope(row),
        "coverage": deepcopy(row.get("coverage", {})),
        "children": list(row.get("children", [])),
        "dependencies": list(row.get("dependencies", [])),
        "certificates": list(row.get("certificates", [])),
        "actions": list(row.get("actions", [])),
        "source": deepcopy(row),
    }


def build_graph_from_obligations(report: dict[str, Any]) -> dict[str, Any]:
    """Create a durable graph from a proof-obligation report."""

    nodes: dict[str, dict[str, Any]] = {}
    for row in report.get("obligations", []):
        node = normalise_obligation(row)
        nodes[node["obligation_id"]] = node
    graph = {
        "schema": "collatz_lab.proof_graph",
        "version": GRAPH_VERSION,
        "source_scope": report.get("scope", "proof obligations"),
        "nodes": nodes,
        "actions": [],
        "closed": [],
        "open": [],
        "status": "PENDING",
    }
    refresh_graph_indices(graph)
    return graph


def node_to_obligation(node: dict[str, Any]) -> dict[str, Any]:
    """Return an obligation-shaped row for policy/action execution."""

    source = dict(node.get("source", {}))
    source.setdefault("obligation_id", node["obligation_id"])
    source["scc_status"] = node["status"]
    source["status"] = node["status"]
    source.setdefault("scope", node.get("scope", ""))
    source.setdefault("coverage", node.get("coverage", {}))
    source.setdefault("transition_rule", node.get("claim", ""))
    return source


def open_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Return graph nodes that still represent open proof obligations."""

    return [
        node
        for node in graph.get("nodes", {}).values()
        if node.get("status") in OPEN_STATUSES or str(node.get("status", "")).startswith("NEEDS_")
    ]


def _children_from_trace(trace: ProofTrace) -> list[dict[str, Any]]:
    result = trace.result
    children: list[dict[str, Any]] = []
    children.extend(deepcopy(result.new_obligations))
    details = result.details or {}
    direct = details.get("children", [])
    if isinstance(direct, list):
        children.extend(deepcopy(direct))
    split = details.get("split", {})
    if isinstance(split, dict) and isinstance(split.get("children"), list):
        children.extend(deepcopy(split["children"]))
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for child in children:
        key = str(child.get("obligation_id") or json.dumps(child, sort_keys=True))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(child)
    return deduped


def _unique_child_id(graph: dict[str, Any], base: str) -> str:
    if base not in graph["nodes"]:
        return base
    index = 2
    while f"{base}#{index}" in graph["nodes"]:
        index += 1
    return f"{base}#{index}"


def _add_child_node(graph: dict[str, Any], parent_id: str, child: dict[str, Any]) -> str:
    base_id = str(child.get("obligation_id") or f"{parent_id}:child:{len(graph['nodes'])}")
    child_id = _unique_child_id(graph, base_id)
    row = dict(child)
    row["obligation_id"] = child_id
    row["status"] = _normalise_child_status(row)
    row.setdefault("scope", child.get("scope", f"child of {parent_id}"))
    row.setdefault("claim", child.get("transition_rule", "generated proof sub-obligation"))
    row.setdefault("coverage", child.get("coverage", {}))
    row["dependencies"] = sorted(set(list(row.get("dependencies", [])) + [parent_id]))
    node = normalise_obligation(row)
    graph["nodes"][child_id] = node
    parent = graph["nodes"][parent_id]
    if child_id not in parent["children"]:
        parent["children"].append(child_id)
    return child_id


def _propagate_child_closure(graph: dict[str, Any]) -> bool:
    changed = False
    while True:
        pass_changed = False
        for node in graph["nodes"].values():
            if status_is_closed(str(node.get("status"))):
                continue
            children = node.get("children", [])
            if children and all(status_is_closed(str(graph["nodes"][child]["status"])) for child in children):
                node["status"] = "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"
                node["certificates"].append(
                    {
                        "certificate_id": f"{node['obligation_id']}:children_closed",
                        "status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE",
                        "claim": "all child obligations are closed",
                        "children": list(children),
                    }
                )
                pass_changed = True
                changed = True
        if not pass_changed:
            break
    return changed


def apply_trace_to_graph(graph: dict[str, Any], trace: ProofTrace) -> dict[str, Any]:
    """Apply one verifier trace to the persistent graph."""

    if trace.obligation_id not in graph["nodes"]:
        graph["nodes"][trace.obligation_id] = normalise_obligation(trace.obligation_before)
    node = graph["nodes"][trace.obligation_id]
    action_record = {
        "obligation_id": trace.obligation_id,
        "action": trace.action.to_dict(),
        "result": trace.result.to_dict(),
        "created_at": trace.created_at,
    }
    graph["actions"].append(action_record)
    node["actions"].append(len(graph["actions"]) - 1)

    if trace.result.status == "CLOSED":
        node["status"] = trace.result.proof_status
        node["certificates"].append(
            {
                "certificate_id": f"{trace.obligation_id}:action:{len(node['actions'])}",
                "status": trace.result.proof_status,
                "claim": trace.result.message,
                "details": deepcopy(trace.result.details),
            }
        )
    elif trace.result.status == "REDUCED":
        for child in _children_from_trace(trace):
            _add_child_node(graph, trace.obligation_id, child)
    elif trace.result.status in {"NEEDS_SPLIT", "FAILED", "INVALID"}:
        # Record the failed/split request as evidence, but do not close or
        # replace the node.
        node.setdefault("verifier_reasons", []).append(
            {
                "status": trace.result.status,
                "proof_status": trace.result.proof_status,
                "message": trace.result.message,
            }
        )

    _propagate_child_closure(graph)
    refresh_graph_indices(graph)
    return graph


def refresh_graph_indices(graph: dict[str, Any]) -> None:
    """Refresh derived open/closed lists and graph status."""

    closed = []
    opened = []
    for node_id, node in sorted(graph.get("nodes", {}).items()):
        if status_is_closed(str(node.get("status"))):
            closed.append(node_id)
        else:
            opened.append(node_id)
    graph["closed"] = closed
    graph["open"] = opened
    graph["status"] = "PASS" if not opened else "INCOMPLETE_OPEN_OBLIGATIONS"
    graph["summary"] = graph_summary(graph)


def graph_summary(graph: dict[str, Any]) -> dict[str, Any]:
    """Return compact graph statistics."""

    status_counts: dict[str, int] = {}
    for node in graph.get("nodes", {}).values():
        status = str(node.get("status", "UNKNOWN"))
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "node_count": len(graph.get("nodes", {})),
        "action_count": len(graph.get("actions", [])),
        "closed_count": len(graph.get("closed", [])),
        "open_count": len(graph.get("open", [])),
        "status_counts": status_counts,
    }


def write_graph_json(graph: dict[str, Any], out: str | Path) -> None:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_graph_markdown(graph: dict[str, Any], out: str | Path) -> None:
    summary = graph_summary(graph)
    lines = [
        "# Persistent Proof Graph",
        "",
        f"- status: `{graph['status']}`",
        f"- nodes: `{summary['node_count']}`",
        f"- actions: `{summary['action_count']}`",
        f"- closed: `{summary['closed_count']}`",
        f"- open: `{summary['open_count']}`",
        f"- status counts: `{summary['status_counts']}`",
        "",
        "A `REDUCED` action is recorded as progress only when it creates child obligations; it never closes its parent by itself.",
        "",
        "## Open Nodes",
        "",
    ]
    for node_id in graph.get("open", [])[:80]:
        node = graph["nodes"][node_id]
        lines.append(f"- `{node_id}`: `{node['status']}` - {node.get('scope', '')}")
    lines.extend(["", "## Closed Nodes", ""])
    for node_id in graph.get("closed", [])[:80]:
        node = graph["nodes"][node_id]
        lines.append(f"- `{node_id}`: `{node['status']}`")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
