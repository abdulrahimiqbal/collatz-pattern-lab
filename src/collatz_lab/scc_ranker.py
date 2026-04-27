"""Exact SCC ranking scaffold for symbolic transition graphs."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console

from .cycle_certificates import (
    AffineReturnMap,
    certify_affine_return_map,
    compose_affine_return_maps,
    sharp_q23_return_map,
)


@dataclass(frozen=True)
class SymbolicEdge:
    source: str
    target: str
    A: int = 1
    B: int = 0
    D: int = 1
    status: str = "UNKNOWN"
    label: str = ""
    domain_residue: int | None = None
    domain_depth: int | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def as_return_map(self) -> AffineReturnMap:
        return AffineReturnMap(
            name=self.label or f"{self.source}->{self.target}",
            A=self.A,
            B=self.B,
            D=self.D,
            domain_residue=self.domain_residue,
            domain_depth=self.domain_depth,
            description=f"{self.source}->{self.target}",
        )


def strongly_connected_components(edges: list[SymbolicEdge]) -> list[list[str]]:
    """Tarjan SCC decomposition."""

    nodes = sorted({edge.source for edge in edges} | {edge.target for edge in edges})
    adjacency = {node: [] for node in nodes}
    for edge in edges:
        adjacency[edge.source].append(edge.target)

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indexes: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indexes[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in adjacency[node]:
            if target not in indexes:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[target])
        if lowlinks[node] == indexes[node]:
            component = []
            while True:
                current = stack.pop()
                on_stack.remove(current)
                component.append(current)
                if current == node:
                    break
            components.append(sorted(component))

    for node in nodes:
        if node not in indexes:
            visit(node)
    return components


def rank_scc(component: list[str], edges: list[SymbolicEdge]) -> dict[str, Any]:
    """Try to close one SCC with exact ranking certificates."""

    members = set(component)
    internal = [edge for edge in edges if edge.source in members and edge.target in members]
    if not internal:
        return {
            "scc": component,
            "status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE",
            "ranking_kind": "acyclic/no_internal_edges",
            "internal_edge_count": 0,
        }
    if all(edge.status == "CLOSED_BY_ANCESTOR_DESCENT" for edge in internal):
        return {
            "scc": component,
            "status": "CLOSED_BY_ANCESTOR_DESCENT",
            "ranking_kind": "all_internal_edges_descend",
            "internal_edge_count": len(internal),
        }
    if len(component) == 1:
        self_loops = [edge for edge in internal if edge.source == edge.target]
        certificates = []
        for edge in self_loops:
            cert = certify_affine_return_map(edge.as_return_map())
            certificates.append(cert)
            if cert["status"] == "PROVED_HEIGHT_DECREASE_ON_REPEAT":
                return {
                    "scc": component,
                    "status": "CLOSED_BY_HEIGHT_RANKING",
                    "ranking_kind": "single_state_affine_height",
                    "internal_edge_count": len(internal),
                    "certificate": cert,
                }
        return {
            "scc": component,
            "status": "NEEDS_SPLIT",
            "ranking_kind": "single_state_unranked",
            "internal_edge_count": len(internal),
            "certificates": certificates,
        }
    composed = _compose_single_cycle_if_present(component, internal)
    if composed is not None:
        cert = certify_affine_return_map(composed)
        if cert["status"] == "PROVED_HEIGHT_DECREASE_ON_REPEAT":
            return {
                "scc": component,
                "status": "CLOSED_BY_HEIGHT_RANKING",
                "ranking_kind": "multi_state_affine_cycle_height",
                "internal_edge_count": len(internal),
                "certificate": cert,
            }
    return {
        "scc": component,
        "status": "NEEDS_SPLIT",
        "ranking_kind": "multi_state_scc_requires_valuation_closure",
        "internal_edge_count": len(internal),
        "internal_edges": [edge.to_dict() for edge in internal],
    }


def _compose_single_cycle_if_present(
    component: list[str],
    internal: list[SymbolicEdge],
) -> AffineReturnMap | None:
    """Compose a deterministic simple cycle through every state, if present.

    This is the first exact mixed-SCC accelerator.  It deliberately handles only
    the strict one-outgoing/one-incoming case; more complicated SCCs remain
    split/ranking obligations instead of being overclaimed.
    """

    members = set(component)
    outgoing: dict[str, list[SymbolicEdge]] = {node: [] for node in members}
    incoming_count: dict[str, int] = {node: 0 for node in members}
    for edge in internal:
        outgoing[edge.source].append(edge)
        incoming_count[edge.target] += 1
    if any(len(rows) != 1 for rows in outgoing.values()):
        return None
    if any(count != 1 for count in incoming_count.values()):
        return None

    ordered: list[SymbolicEdge] = []
    start = min(component)
    seen: set[str] = set()
    current = start
    while current not in seen:
        seen.add(current)
        edge = outgoing[current][0]
        ordered.append(edge)
        current = edge.target
    if current != start or seen != members or len(ordered) != len(component):
        return None
    return compose_affine_return_maps(
        [edge.as_return_map() for edge in ordered],
        name="mixed_scc_cycle:" + "->".join(edge.source for edge in ordered),
    )


def rank_graph(edges: list[SymbolicEdge]) -> dict[str, Any]:
    components = strongly_connected_components(edges)
    rankings = [rank_scc(component, edges) for component in components]
    open_rankings = [row for row in rankings if row["status"] in {"NEEDS_SPLIT", "UNKNOWN"}]
    return {
        "scope": "symbolic SCC ranking",
        "status": "PASS" if not open_rankings else "INCOMPLETE_OPEN_SCCS",
        "node_count": len({edge.source for edge in edges} | {edge.target for edge in edges}),
        "edge_count": len(edges),
        "scc_count": len(components),
        "open_scc_count": len(open_rankings),
        "rankings": rankings,
    }


def _edge_from_dict(row: dict[str, Any]) -> SymbolicEdge:
    return SymbolicEdge(
        source=str(row["source"]),
        target=str(row["target"]),
        A=int(row.get("A", 1)),
        B=int(row.get("B", 0)),
        D=int(row.get("D", 1)),
        status=str(row.get("status", "UNKNOWN")),
        label=str(row.get("label", "")),
        domain_residue=row.get("domain_residue"),
        domain_depth=row.get("domain_depth"),
        details=dict(row.get("details", {})),
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank SCCs in a symbolic transition graph.")
    parser.add_argument("--graph", default=None, help="JSON with an 'edges' list.")
    parser.add_argument("--sharp-q23", action="store_true", help="Use the built-in sharp q23 self-loop graph.")
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.sharp_q23:
        sharp = sharp_q23_return_map()
        edges = [
            SymbolicEdge(
                "P6_q23",
                "P6_q23",
                A=sharp.A,
                B=sharp.B,
                D=sharp.D,
                label=sharp.name,
                domain_residue=sharp.domain_residue,
                domain_depth=sharp.domain_depth,
            )
        ]
    elif args.graph:
        payload = json.loads(Path(args.graph).read_text(encoding="utf-8"))
        edges = [_edge_from_dict(row) for row in payload.get("edges", [])]
    else:
        raise ValueError("provide --graph or --sharp-q23")
    report = rank_graph(edges)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print({"out": str(out), "status": report["status"], "open_sccs": report["open_scc_count"]})


if __name__ == "__main__":
    main()
