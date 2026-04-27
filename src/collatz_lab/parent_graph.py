"""Recursive transition graph scaffold for the ``n = 64*q - 1`` parent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .residual_frontier import normalize_residue


def tarjan_scc(graph: dict[str, set[str]]) -> list[list[str]]:
    """Return strongly connected components using Tarjan's algorithm."""

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in graph.get(node, set()):
            if target not in indices:
                strongconnect(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])

        if lowlinks[node] == indices[node]:
            component: list[str] = []
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.append(target)
                if target == node:
                    break
            components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            strongconnect(node)
    components.sort(key=lambda comp: (-len(comp), comp))
    return components


def _add_edge(graph: dict[str, set[str]], edges: list[dict[str, Any]], source: str, target: str, **payload: Any) -> None:
    graph.setdefault(source, set()).add(target)
    graph.setdefault(target, set())
    edges.append({"source": source, "target": target, **payload})


def _burst_affine_transition(a: int, h: int) -> dict[str, int]:
    return {
        "A": 3**a,
        "B": 3**a - (1 << a),
        "D": 1 << (a + h),
        "n_min": (1 << a) - 1,
    }


def build_parent_transition_graph(
    q_depth: int,
    residual_report: dict[str, Any],
    burst_report: dict[str, Any],
    return_report: dict[str, Any],
) -> dict[str, Any]:
    graph: dict[str, set[str]] = {}
    edges: list[dict[str, Any]] = []
    nodes: dict[str, dict[str, Any]] = {}
    potential_transitions: list[dict[str, Any]] = []

    root = f"parent:q_depth={q_depth}"
    nodes[root] = {"node_id": root, "type": "PARENT_FRONTIER", "q_depth": q_depth}
    graph.setdefault(root, set())

    certified = "terminal:residual_certified"
    unknown = "terminal:unknown"
    leaves = "terminal:leaves_parent"
    for node_id, node_type in [
        (certified, "RESIDUAL_CERTIFIED"),
        (unknown, "UNKNOWN"),
        (leaves, "LEAVES_PARENT"),
    ]:
        nodes[node_id] = {"node_id": node_id, "type": node_type}
        graph.setdefault(node_id, set())

    _add_edge(graph, edges, root, certified, kind="aggregate_status")
    _add_edge(graph, edges, root, unknown, kind="aggregate_status")

    for family in burst_report.get("families", []):
        node_id = f"burst_escape:a={family['a']}:q={family['q_residue']}mod2^{family['q_depth']}"
        nodes[node_id] = {"node_id": node_id, "type": "BURST_ESCAPE", **family}
        transition = _burst_affine_transition(int(family["a"]), int(family["h_star"]))
        _add_edge(graph, edges, root, node_id, kind="burst_escape", **transition)
        potential_transitions.append(
            {
                "source_state": root,
                "target_state": node_id,
                **transition,
                "description": f"burst escape a={family['a']}",
            }
        )

    for row in return_report.get("maps", []):
        node_id = f"return:a={row['a']}:h={row['h']}"
        nodes[node_id] = {"node_id": node_id, "type": "RETURN_TO_PARENT", **row}
        transition = _burst_affine_transition(int(row["a"]), int(row["h"]))
        _add_edge(graph, edges, root, node_id, kind="return_to_parent", **transition)
        _add_edge(graph, edges, node_id, root, kind="parent_q_prime")
        potential_transitions.append(
            {
                "source_state": root,
                "target_state": node_id,
                **transition,
                "description": f"return map a={row['a']} h={row['h']}",
            }
        )

    top_unknown = []
    for row in residual_report.get("unknown_q_mod_64", []):
        residue = normalize_residue(int(row["value"]), 6)
        node_id = f"unknown:qmod64={residue}"
        payload = {"node_id": node_id, "type": "UNKNOWN_BUCKET", "q_mod_depth": 6, "q_mod_residue": residue, "count": row["count"]}
        nodes[node_id] = payload
        _add_edge(graph, edges, root, node_id, kind="unknown_bucket")
        _add_edge(graph, edges, node_id, unknown, kind="unresolved")
        top_unknown.append(payload)

    components = tarjan_scc(graph)
    unresolved_components = [
        comp
        for comp in components
        if any(nodes[node]["type"] in {"UNKNOWN", "UNKNOWN_BUCKET", "RETURN_TO_PARENT"} for node in comp)
    ]
    largest = unresolved_components[0] if unresolved_components else []
    return {
        "scope": "parent n = 64*q - 1",
        "q_depth": q_depth,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "terminal_burst_escape_nodes": sum(1 for node in nodes.values() if node["type"] == "BURST_ESCAPE"),
        "return_to_parent_edges": sum(1 for edge in edges if edge["kind"] == "return_to_parent"),
        "leaves_parent_edges": sum(1 for edge in edges if edge["target"] == leaves),
        "unknown_nodes": sum(1 for node in nodes.values() if node["type"] in {"UNKNOWN", "UNKNOWN_BUCKET"}),
        "nodes": list(nodes.values()),
        "edges": edges,
        "strongly_connected_components": components,
        "largest_unresolved_scc": largest,
        "largest_unresolved_scc_size": len(largest),
        "top_unresolved_q_classes": top_unknown[:32],
        "potential_transitions": potential_transitions,
        "claim_status": "GRAPH_SCAFFOLD_EXACT_LOCAL_EDGES_NOT_GLOBAL_PROOF",
    }


def write_parent_graph_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Parent Transition Graph",
        "",
        f"- nodes: `{report['node_count']}`",
        f"- edges: `{report['edge_count']}`",
        f"- burst escape nodes: `{report['terminal_burst_escape_nodes']}`",
        f"- return-to-parent edges: `{report['return_to_parent_edges']}`",
        f"- unknown nodes: `{report['unknown_nodes']}`",
        f"- largest unresolved SCC size: `{report['largest_unresolved_scc_size']}`",
        "",
        "## Top Unresolved q Classes",
        "",
    ]
    for row in report["top_unresolved_q_classes"][:20]:
        lines.append(f"- `q == {row['q_mod_residue']} mod 64`: `{row['count']}`")
    lines.extend(["", "## Largest Unresolved SCC", "", f"`{report['largest_unresolved_scc']}`", ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build parent transition graph scaffold.")
    parser.add_argument("--q-depth", type=int, required=True)
    parser.add_argument("--residual-report", required=True)
    parser.add_argument("--burst-report", required=True)
    parser.add_argument("--return-report", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    residual = json.loads(Path(args.residual_report).read_text(encoding="utf-8"))
    burst = json.loads(Path(args.burst_report).read_text(encoding="utf-8"))
    returns = json.loads(Path(args.return_report).read_text(encoding="utf-8"))
    report = build_parent_transition_graph(args.q_depth, residual, burst, returns)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_parent_graph_markdown(report, md_out)
    Console().print(
        {
            "nodes": report["node_count"],
            "edges": report["edge_count"],
            "largest_unresolved_scc_size": report["largest_unresolved_scc_size"],
            "out": str(out),
        }
    )


if __name__ == "__main__":
    main()
