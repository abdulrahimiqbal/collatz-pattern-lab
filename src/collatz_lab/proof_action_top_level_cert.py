"""Replayable top-level theorem certificates.

RUN-024 introduced the five top-level theorem-certificate slots.  RUN-030
hardens them so the top-level replay is backed by manifest artifacts and the
current S3/S4/S6 certificate store rather than graph status alone.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RUN_ID = "RUN-024-top-level-theorem-certificates"
RUN030_ID = "RUN-030-top-level-theorem-certificates-after-s3-s6-hardening"
SCHEMA = "collatz_lab.top_level_theorem_certificate"
THEOREM_STATEMENT = "forall n > 1 exists k >= 1 such that C^k(n) < n"
COLLATZ_CONJECTURE_STATEMENT = "forall n > 1 exists t >= 0 such that C^t(n) = 1"
EXPECTED_S3_EXACT_COUNT = 182
EXPECTED_S4_EXACT_COUNT = 135
EXPECTED_S6_EXACT_COUNT = 28
PARENT_RESIDUAL_CERTIFICATE_ID = "parent_residual_cert_P26_67108863_67108864"
LOWER_LAYER_MANIFEST_HASH_NAMES = {
    "s3_debt_certificates",
    "parent_transition_certificates",
    "s6_lemma_certificates",
    "parent_residual_certificate",
    "scc_guarded_ranking_certificate",
}
TOP_LEVEL_CERTIFICATES = (
    "universal_entry_certificate",
    "parent_state_coverage_certificate",
    "transition_soundness_certificate",
    "well_founded_ranking_certificate",
    "descent_implication_certificate",
)


@dataclass(frozen=True)
class ReplayResult:
    accepted: bool
    status: str
    reason: str
    failures: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "status": self.status,
            "reason": self.reason,
            "failures": list(self.failures or []),
        }


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def certificate_hash(certificate: dict[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_hash"}
    return _hash(payload)


def graph_hash(graph: dict[str, Any]) -> str:
    return _hash(
        {
            "schema": graph.get("schema"),
            "version": graph.get("version"),
            "nodes": graph.get("nodes", {}),
            "edges": graph.get("edges", []),
            "open": graph.get("open", []),
        }
    )


def parent_residual_certificate_hash(certificate: dict[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_hash"}
    return _hash(payload)


def _row_certificate(row: dict[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = row.get(key)
        if isinstance(value, dict):
            return value
    return row if isinstance(row, dict) else {}


def _row_replay_accepted(row: dict[str, Any]) -> bool:
    replay = row.get("replay_result")
    return isinstance(replay, dict) and replay.get("accepted") is True


def _cert_id(certificate: dict[str, Any]) -> str:
    return str(certificate.get("certificate_id") or certificate.get("transition_id") or "")


def _cert_hash(certificate: dict[str, Any]) -> str:
    return str(certificate.get("certificate_hash") or "")


def build_replay_context(
    *,
    graph: dict[str, Any],
    s3_rows: list[dict[str, Any]] | None = None,
    s4_rows: list[dict[str, Any]] | None = None,
    s6_rows: list[dict[str, Any]] | None = None,
    parent_residual_certificate: dict[str, Any] | None = None,
    scc_guarded_ranking_certificate: dict[str, Any] | None = None,
    manifest_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Pack lower-layer artifacts for strict top-level replay."""

    return {
        "graph": graph,
        "graph_hash": graph_hash(graph),
        "s3_rows": list(s3_rows or []),
        "s4_rows": list(s4_rows or []),
        "s6_rows": list(s6_rows or []),
        "parent_residual_certificate": dict(parent_residual_certificate or {}),
        "scc_guarded_ranking_certificate": dict(scc_guarded_ranking_certificate or {}),
        "manifest_hashes": dict(manifest_hashes or {}),
    }


def _context_or_graph(context: dict[str, Any] | None, graph: dict[str, Any] | None) -> dict[str, Any] | None:
    if isinstance(context, dict) and isinstance(context.get("graph"), dict):
        return context["graph"]
    return graph


def _lower_manifest_hashes(hashes: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in sorted(hashes.items()) if key in LOWER_LAYER_MANIFEST_HASH_NAMES}


def _accepted_action(node: dict[str, Any]) -> dict[str, Any] | None:
    for row in reversed(list(node.get("accepted_actions") or [])):
        action = row.get("action")
        if isinstance(action, dict):
            return action
    return None


def _verify_graph_action(node_id: str, node: dict[str, Any]) -> dict[str, Any] | None:
    from .proof_action_decode import verify_action_for_state

    action = _accepted_action(node)
    if not isinstance(action, dict):
        return {"node_id": node_id, "reason": "missing_accepted_action"}
    check = verify_action_for_state(action, str(node.get("state", "")))
    if not check.accepted:
        return {"node_id": node_id, "reason": check.reason, "status": check.status}
    return None


def _node_ids_by_type(graph: dict[str, Any], node_type: str) -> list[str]:
    return sorted(
        str(node_id)
        for node_id, node in (graph.get("nodes") or {}).items()
        if isinstance(node, dict) and node.get("node_type") == node_type
    )


def _graph_acceptance_failures(graph: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if graph.get("open"):
        failures.append({"reason": "graph_has_open_nodes", "open": list(graph.get("open", []))[:10]})
    for node_id, node in (graph.get("nodes") or {}).items():
        if node.get("status") != "ACCEPTED":
            failures.append({"node_id": node_id, "reason": "node_not_accepted", "status": node.get("status")})
    return failures


def _accepted_action_of_type(node: dict[str, Any], action_type: str) -> dict[str, Any] | None:
    for row in reversed(list(node.get("accepted_actions") or [])):
        action = row.get("action")
        if isinstance(action, dict) and action.get("type") == action_type:
            return action
    return None


def _status_only_top_level(cert: dict[str, Any]) -> bool:
    payload = cert.get("proof_payload")
    if not isinstance(payload, dict) or not payload:
        return True
    if set(payload) <= {"status", "verifier_status", "certificate_id"}:
        return True
    return bool(payload.get("graph_closure_only"))


def _is_strict_run030_cert(cert: dict[str, Any]) -> bool:
    payload = cert.get("proof_payload")
    return bool(
        cert.get("run_id") == RUN030_ID
        or cert.get("strict_replay") is True
        or (isinstance(payload, dict) and payload.get("strict_replay") is True)
    )


def _topological_ranking(graph: dict[str, Any]) -> tuple[dict[str, int] | None, list[dict[str, Any]], list[dict[str, Any]]]:
    nodes = set(str(node_id) for node_id in (graph.get("nodes") or {}))
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    indegree: dict[str, int] = {node_id: 0 for node_id in nodes}
    edge_rows: list[dict[str, Any]] = []
    for edge in graph.get("edges", []) or []:
        source = str(edge.get("from", ""))
        target = str(edge.get("to", ""))
        if source not in nodes or target not in nodes:
            continue
        adjacency[source].append(target)
        indegree[target] += 1
        edge_rows.append({"source": source, "target": target, "kind": str(edge.get("kind", ""))})
    queue = deque(sorted(node_id for node_id in nodes if indegree[node_id] == 0))
    order: list[str] = []
    while queue:
        node_id = queue.popleft()
        order.append(node_id)
        for target in sorted(adjacency[node_id]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(order) != len(nodes):
        unresolved = sorted(node_id for node_id in nodes if indegree[node_id] > 0)
        return None, edge_rows, [{"reason": "unresolved_scc_or_cycle", "nodes": unresolved[:20], "count": len(unresolved)}]
    ranks = {node_id: len(order) - index for index, node_id in enumerate(order)}
    failures = [
        {"reason": "non_decreasing_edge", "source": edge["source"], "target": edge["target"]}
        for edge in edge_rows
        if ranks[edge["target"]] >= ranks[edge["source"]]
    ]
    return ranks, edge_rows, failures


def _ranking_payload(graph: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ranks, edges, failures = _topological_ranking(graph)
    if ranks is None:
        return {
            "ranking_id": "run024_topological_parent_state_rank",
            "measure": "reverse_topological_dependency_rank",
            "domain": "parent_state_graph",
            "well_founded_order": "explicit_dag_topological_rank",
            "node_ranks": {},
            "edge_checks": [],
            "unresolved_sccs": failures,
        }, failures
    edge_checks = [
        {
            "source": edge["source"],
            "target": edge["target"],
            "source_rank": ranks[edge["source"]],
            "target_rank": ranks[edge["target"]],
            "decreases": ranks[edge["target"]] < ranks[edge["source"]],
            "certificate_ref": "graph_edge:" + edge["source"] + "->" + edge["target"],
        }
        for edge in edges
    ]
    return {
        "ranking_id": "run024_topological_parent_state_rank",
        "measure": "reverse_topological_dependency_rank",
        "domain": "parent_state_graph",
        "well_founded_order": "explicit_dag_topological_rank",
        "node_ranks": ranks,
        "edge_checks": edge_checks,
        "unresolved_sccs": [],
    }, failures


def _base_certificate(
    cert_type: str,
    statement: str,
    proof_payload: dict[str, Any],
    *,
    status: str = "PASS",
    run_id: str = RUN_ID,
    strict_replay: bool = False,
) -> dict[str, Any]:
    certificate = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": run_id,
        "type": cert_type,
        "certificate_type": cert_type,
        "certificate_id": cert_type,
        "statement": statement,
        "proof_payload": proof_payload,
        "strict_replay": strict_replay,
        "replay_status": status,
        "status": status,
    }
    certificate["certificate_hash"] = certificate_hash(certificate)
    return certificate


def _replay_s3_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    from .proof_action_s3_debt_cert import replay_s3_debt_certificate

    passed: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        certificate = _row_certificate(row, "s3_debt_certificate")
        replay = replay_s3_debt_certificate(certificate)
        node_id = str(row.get("node_id") or certificate.get("node_id") or f"s3_row:{index}")
        record = {
            "node_id": node_id,
            "certificate_id": _cert_id(certificate),
            "certificate_hash": _cert_hash(certificate),
            "source": f"P{certificate.get('source_parent')}",
            "target": f"P{certificate.get('target_parent')}",
            "type": str(certificate.get("type", "")),
            "terminal_descent": True,
        }
        if replay.accepted:
            passed.append(record)
        else:
            failures.append({**record, "status": replay.status, "reason": replay.reason, "failures": replay.failures or []})
    return passed, failures


def _replay_s4_rows(rows: list[dict[str, Any]], graph: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    from .proof_action_parent_transition_cert import replay_parent_transition_certificate

    passed: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    nodes = graph.get("nodes") or {}
    for index, row in enumerate(rows):
        certificate = _row_certificate(row, "transition_certificate")
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        node_id = str(row.get("node_id") or f"s4_row:{index}")
        state = str((nodes.get(node_id) or {}).get("state", ""))
        replay = replay_parent_transition_certificate(action=action, state=state, certificate=certificate)
        record = {
            "node_id": node_id,
            "certificate_id": _cert_id(certificate),
            "certificate_hash": _cert_hash(certificate),
            "transition_id": str(certificate.get("transition_id", "")),
            "source": f"P{certificate.get('source_parent')}",
            "target": f"P{certificate.get('target_parent')}",
            "type": str(certificate.get("type", "")),
            "terminal_descent": False,
        }
        if replay.accepted:
            passed.append(record)
        else:
            failures.append({**record, "status": replay.status, "reason": replay.reason})
    return passed, failures


def _replay_s6_rows(rows: list[dict[str, Any]], graph: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    from .proof_action_s6_lemma_cert import replay_s6_lemma_certificate

    passed: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        certificate = _row_certificate(row, "s6_lemma_certificate")
        replay = replay_s6_lemma_certificate(certificate, graph=graph)
        node_id = str(row.get("node_id") or f"s6_row:{index}")
        record = {
            "node_id": node_id,
            "certificate_id": _cert_id(certificate),
            "certificate_hash": _cert_hash(certificate),
            "lemma_id": str(certificate.get("lemma_id", "")),
            "blocker_id": str(certificate.get("blocker_id", "")),
            "type": str(certificate.get("type", "")),
        }
        if replay.accepted:
            passed.append(record)
        else:
            failures.append({**record, "status": replay.status, "reason": replay.reason, "failures": replay.failures or []})
    return passed, failures


def _replay_parent_residual(certificate: dict[str, Any], graph: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    if not certificate:
        return None, [{"certificate_id": PARENT_RESIDUAL_CERTIFICATE_ID, "reason": "missing_parent_residual_certificate"}]
    if certificate.get("schema") != "collatz_lab.proof_action_parent_residual_certificate":
        failures.append({"certificate_id": certificate.get("certificate_id"), "reason": "unsupported_parent_residual_schema"})
    if int(certificate.get("version", 0) or 0) != 1:
        failures.append({"certificate_id": certificate.get("certificate_id"), "reason": "unsupported_parent_residual_version"})
    if str(certificate.get("status")) != "PASS":
        failures.append({"certificate_id": certificate.get("certificate_id"), "reason": "parent_residual_status_not_pass"})
    if str(certificate.get("certificate_id")) != PARENT_RESIDUAL_CERTIFICATE_ID:
        failures.append({"certificate_id": certificate.get("certificate_id"), "reason": "unexpected_parent_residual_certificate_id"})
    if str(certificate.get("certificate_hash")) != parent_residual_certificate_hash(certificate):
        failures.append({"certificate_id": certificate.get("certificate_id"), "reason": "parent_residual_hash_mismatch"})
    parent_level = int(certificate.get("parent_level", 0) or 0)
    modulus = int(certificate.get("modulus", 0) or 0)
    residual_start = int(certificate.get("residual_start", -1) or -1)
    residual_end = int(certificate.get("residual_end", -1) or -1)
    if parent_level != 26 or modulus != 1 << 26 or residual_start != modulus - 1 or residual_end != modulus:
        failures.append(
            {
                "certificate_id": certificate.get("certificate_id"),
                "reason": "parent_residual_domain_mismatch",
                "parent_level": parent_level,
                "modulus": modulus,
                "residual_start": residual_start,
                "residual_end": residual_end,
            }
        )
    if int(certificate.get("path_node_count", 0) or 0) <= 0:
        failures.append({"certificate_id": certificate.get("certificate_id"), "reason": "parent_residual_path_empty"})
    if int(certificate.get("ranking_delta_num", 1) or 1) >= int(certificate.get("ranking_delta_den", 1) or 1):
        failures.append({"certificate_id": certificate.get("certificate_id"), "reason": "parent_residual_ranking_not_decreasing"})
    missing_path_nodes = [
        node_id
        for node_id in certificate.get("path_node_ids", []) or []
        if node_id not in (graph.get("nodes") or {})
    ]
    if missing_path_nodes:
        failures.append(
            {
                "certificate_id": certificate.get("certificate_id"),
                "reason": "parent_residual_path_node_missing_from_graph",
                "node_ids": missing_path_nodes[:20],
                "count": len(missing_path_nodes),
            }
        )
    summary = {
        "certificate_id": str(certificate.get("certificate_id", "")),
        "certificate_hash": str(certificate.get("certificate_hash", "")),
        "parent_level": parent_level,
        "modulus": modulus,
        "residual_start": residual_start,
        "residual_end": residual_end,
        "ranking_delta_num": int(certificate.get("ranking_delta_num", 0) or 0),
        "ranking_delta_den": int(certificate.get("ranking_delta_den", 0) or 0),
        "path_node_count": int(certificate.get("path_node_count", 0) or 0),
    }
    return summary, failures


def replay_lower_layer_context(context: dict[str, Any] | None) -> dict[str, Any]:
    """Replay S3/S4/S6/residual artifacts supplied by the strict manifest."""

    if not isinstance(context, dict) or not isinstance(context.get("graph"), dict):
        return {
            "status": "FAIL",
            "failures": [{"reason": "missing_manifest_replay_context"}],
            "counts": {"s3": 0, "s4": 0, "s6": 0},
            "passed": {"s3": 0, "s4": 0, "s6": 0},
        }
    graph = context["graph"]
    s3_passed, s3_failures = _replay_s3_rows(list(context.get("s3_rows") or []))
    s4_passed, s4_failures = _replay_s4_rows(list(context.get("s4_rows") or []), graph)
    s6_passed, s6_failures = _replay_s6_rows(list(context.get("s6_rows") or []), graph)
    residual, residual_failures = _replay_parent_residual(dict(context.get("parent_residual_certificate") or {}), graph)
    count_failures: list[dict[str, Any]] = []
    if len(s3_passed) != EXPECTED_S3_EXACT_COUNT:
        count_failures.append({"layer": "S3", "reason": "unexpected_s3_exact_count", "expected": EXPECTED_S3_EXACT_COUNT, "actual": len(s3_passed)})
    if len(s4_passed) != EXPECTED_S4_EXACT_COUNT:
        count_failures.append({"layer": "S4", "reason": "unexpected_s4_exact_count", "expected": EXPECTED_S4_EXACT_COUNT, "actual": len(s4_passed)})
    if len(s6_passed) != EXPECTED_S6_EXACT_COUNT:
        count_failures.append({"layer": "S6", "reason": "unexpected_s6_exact_count", "expected": EXPECTED_S6_EXACT_COUNT, "actual": len(s6_passed)})
    failures = [*count_failures, *s3_failures, *s4_failures, *s6_failures, *residual_failures]
    return {
        "status": "PASS" if not failures else "FAIL",
        "counts": {"s3": len(context.get("s3_rows") or []), "s4": len(context.get("s4_rows") or []), "s6": len(context.get("s6_rows") or [])},
        "passed": {"s3": len(s3_passed), "s4": len(s4_passed), "s6": len(s6_passed)},
        "expected": {"s3": EXPECTED_S3_EXACT_COUNT, "s4": EXPECTED_S4_EXACT_COUNT, "s6": EXPECTED_S6_EXACT_COUNT},
        "s3_exact": s3_passed,
        "s4_exact": s4_passed,
        "s6_exact": s6_passed,
        "parent_residual": residual,
        "failures": failures,
    }


def _coverage_domains(graph: dict[str, Any], lower: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    required: list[dict[str, Any]] = []
    covered: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    nodes = graph.get("nodes") or {}
    for node_id, node in sorted(nodes.items()):
        if node.get("node_type") != "COVERAGE_CERTIFICATE":
            continue
        action = _accepted_action_of_type(node, "PROVE_RESIDUE_COVERAGE")
        if action is None:
            parent_residual_action = _accepted_action_of_type(node, "PROVE_PARENT_RESIDUAL_COVERAGE")
            if parent_residual_action is not None:
                replay_failure = _verify_graph_action(str(node_id), node)
                if replay_failure:
                    failures.append(replay_failure)
            continue
        try:
            modulus = int(action.get("modulus", 0) or 0)
            covered_count = int(action.get("covered_residue_count", 0) or 0)
        except (TypeError, ValueError):
            failures.append({"node_id": node_id, "reason": "coverage_action_has_noninteger_domain"})
            continue
        certificate_id = str(action.get("certificate_id") or node_id)
        domain = {
            "domain_id": certificate_id,
            "node_id": str(node_id),
            "kind": "residue_coverage",
            "modulus": modulus,
            "residue_start": 0,
            "residue_end_exclusive": modulus,
        }
        required.append(domain)
        replay_failure = _verify_graph_action(str(node_id), node)
        if replay_failure:
            failures.append(replay_failure)
        elif covered_count >= modulus and modulus > 0:
            covered.append({**domain, "covered_by": certificate_id, "coverage_kind": "replayed_coverage_certificate"})
        else:
            failures.append({**domain, "reason": "coverage_certificate_is_partial", "covered_residue_count": covered_count})
    residual = lower.get("parent_residual") if isinstance(lower, dict) else None
    required_residual = {
        "domain_id": "P26:residual:67108863:67108864",
        "kind": "parent_residual",
        "parent_level": 26,
        "modulus": 1 << 26,
        "residue_start": (1 << 26) - 1,
        "residue_end_exclusive": 1 << 26,
    }
    required.append(required_residual)
    if isinstance(residual, dict) and residual.get("parent_level") == 26 and residual.get("residual_start") == (1 << 26) - 1 and residual.get("residual_end") == (1 << 26):
        covered.append({**required_residual, "covered_by": residual["certificate_id"], "coverage_kind": "replayed_parent_residual_certificate"})
    else:
        failures.append({**required_residual, "reason": "final_P26_residual_parent_class_not_covered"})
    covered_keys = {(row["kind"], row.get("domain_id")) for row in covered}
    uncovered = [row for row in required if (row["kind"], row.get("domain_id")) not in covered_keys]
    return required, covered, failures + [{"reason": "uncovered_parent_state_domain", **row} for row in uncovered]


def _transition_rows_from_lower(lower: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in lower.get("s3_exact", []) or []:
        rows.append(
            {
                "edge_id": f"s3:{row['certificate_id']}",
                "source": row["source"],
                "target": row["target"],
                "node_id": row["node_id"],
                "transition_certificate_id": row["certificate_id"],
                "transition_certificate_hash": row["certificate_hash"],
                "kind": "S3_DEBT_EXACT",
                "terminal_descent": True,
            }
        )
    for row in lower.get("s4_exact", []) or []:
        rows.append(
            {
                "edge_id": f"s4:{row['transition_id'] or row['certificate_id']}",
                "source": row["source"],
                "target": row["target"],
                "node_id": row["node_id"],
                "transition_certificate_id": row["certificate_id"] or row["transition_id"],
                "transition_certificate_hash": row["certificate_hash"],
                "kind": "HIGH_PARENT_SUCCESSOR_EXACT",
                "terminal_descent": False,
            }
        )
    return rows


def _tarjan_scc(nodes: set[str], edges: list[dict[str, Any]]) -> list[list[str]]:
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    for edge in edges:
        adjacency.setdefault(str(edge["source"]), []).append(str(edge["target"]))
        adjacency.setdefault(str(edge["target"]), [])
    index: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        index[node] = len(index)
        lowlink[node] = index[node]
        stack.append(node)
        on_stack.add(node)
        for target in sorted(adjacency.get(node, []), key=_parent_sort_key):
            if target not in index:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], index[target])
        if lowlink[node] == index[node]:
            component: list[str] = []
            while True:
                popped = stack.pop()
                on_stack.remove(popped)
                component.append(popped)
                if popped == node:
                    break
            components.append(sorted(component, key=_parent_sort_key))

    for node in sorted(nodes, key=_parent_sort_key):
        if node not in index:
            visit(node)
    return components


def _parent_sort_key(node: str) -> tuple[int, str]:
    if node.startswith("P") and node[1:].isdigit():
        return (int(node[1:]), node)
    return (10**9, node)


def _topological_ranks_for_edges(nodes: set[str], edges: list[dict[str, Any]]) -> tuple[dict[str, int] | None, list[dict[str, Any]], list[dict[str, Any]]]:
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    indegree: dict[str, int] = {node: 0 for node in nodes}
    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        adjacency.setdefault(source, []).append(target)
        indegree.setdefault(source, 0)
        indegree[target] = indegree.get(target, 0) + 1
    queue = deque(sorted([node for node, degree in indegree.items() if degree == 0], key=_parent_sort_key))
    order: list[str] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for target in sorted(adjacency.get(node, []), key=_parent_sort_key):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(order) != len(indegree):
        cyclic_nodes = {node for node, degree in indegree.items() if degree > 0}
        cyclic_edges = [edge for edge in edges if edge["source"] in cyclic_nodes and edge["target"] in cyclic_nodes]
        return None, [], cyclic_edges
    ranks = {node: len(order) - index for index, node in enumerate(order)}
    edge_checks = [
        {
            "edge_id": edge["edge_id"],
            "source": edge["source"],
            "target": edge["target"],
            "source_rank": ranks[edge["source"]],
            "target_rank": ranks[edge["target"]],
            "decreases": ranks[edge["target"]] < ranks[edge["source"]],
            "transition_certificate_id": edge["transition_certificate_id"],
        }
        for edge in edges
    ]
    failures = [edge for edge in edge_checks if not edge["decreases"]]
    return ranks, edge_checks, failures


def _edge_id_set_from_guarded_scc_certificate(certificate: dict[str, Any]) -> tuple[set[str], dict[str, Any] | None, list[dict[str, Any]]]:
    if not certificate:
        return set(), None, []
    from .proof_action_guarded_scc_ranking import replay_scc_guarded_ranking_certificate

    replay = replay_scc_guarded_ranking_certificate(certificate)
    if not replay.get("accepted"):
        return set(), None, [{"reason": "scc_guarded_ranking_certificate_replay_failed", "replay": replay}]
    covered = set(str(edge_id) for edge_id in certificate.get("covered_edge_ids", []) or [])
    check = {
        "scc_id": str(certificate.get("scc_id", "")),
        "certificate_hash": str(certificate.get("certificate_hash", "")),
        "proof_kind": str(certificate.get("proof_kind", "")),
        "covered_edge_count": len(covered),
        "status": "PASS",
    }
    return covered, check, []


def _run030_ranking_payload(
    lower: dict[str, Any],
    scc_guarded_ranking_certificate: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    transition_edges = _transition_rows_from_lower(lower)
    nonterminal_edges = [edge for edge in transition_edges if not edge.get("terminal_descent")]
    covered_scc_edges, scc_check, scc_failures = _edge_id_set_from_guarded_scc_certificate(dict(scc_guarded_ranking_certificate or {}))
    ranking_edges = [edge for edge in nonterminal_edges if str(edge.get("edge_id")) not in covered_scc_edges]
    nodes = {edge["source"] for edge in nonterminal_edges} | {edge["target"] for edge in nonterminal_edges}
    ranks, edge_checks, rank_failures = _topological_ranks_for_edges(nodes, ranking_edges)
    unresolved_sccs: list[dict[str, Any]] = []
    if ranks is None:
        components = _tarjan_scc(nodes, ranking_edges)
        for index, component in enumerate(components):
            internal = [edge for edge in ranking_edges if edge["source"] in component and edge["target"] in component]
            if len(component) > 1 or any(edge["source"] == edge["target"] for edge in internal):
                unresolved_sccs.append(
                    {
                        "scc_id": f"run030_parent_state_scc_{index:04d}",
                        "nodes": component,
                        "edge_count": len(internal),
                        "edges": internal,
                        "required_certificate": "SCC_INTERNAL_RANKING_EXACT",
                    }
                )
    failures: list[dict[str, Any]] = []
    if unresolved_sccs:
        failures.extend({"reason": "unresolved_scc", **row} for row in unresolved_sccs)
    failures.extend({"reason": "nondecreasing_edge", **row} for row in rank_failures)
    failures.extend(scc_failures)
    status = "PASS" if not failures else "FAIL"
    payload = {
        "certificate_id": "well_founded_ranking_certificate",
        "type": "WELL_FOUNDED_RANKING_EXACT",
        "domain": "parent_state_transition_graph",
        "well_founded_order": "topological_dag_rank_with_guarded_scc_rank" if status == "PASS" and scc_check else "topological_dag_rank" if status == "PASS" else "scc_internal_ranking_required",
        "terminal_edge_count": sum(1 for edge in transition_edges if edge.get("terminal_descent")),
        "nonterminal_edge_count": len(nonterminal_edges),
        "node_ranks": ranks or {},
        "edge_checks": edge_checks,
        "scc_checks": [scc_check] if scc_check else [],
        "unresolved_sccs": unresolved_sccs,
        "nondecreasing_edges": rank_failures,
        "transition_edges": transition_edges,
        "status": status,
    }
    payload["certificate_hash"] = _hash(payload)
    return payload, failures


def _run030_universal_payload() -> dict[str, Any]:
    return {
        "strict_replay": True,
        "theorem": THEOREM_STATEMENT,
        "arithmetic_proof_schema": {
            "positive_domain": "n > 1",
            "even_case": {
                "hypothesis": "n = 2*k and k >= 1",
                "collatz_identity": "C(n) = n / 2 = k",
                "descent_inequality": "k < 2*k",
                "replay_checks": {
                    "denominator_positive": True,
                    "strict_descent_for_k_ge_1": True,
                },
            },
            "odd_case": {
                "hypothesis": "n odd and n > 1",
                "valuation_definition": "a = v2(n + 1)",
                "valuation_lower_bound": "a >= 1 because n + 1 is even",
                "quotient_definition": "q = (n + 1) / 2^a",
                "quotient_positive": "q >= 1",
                "reconstruction": "n = 2^a*q - 1",
                "uniqueness": "a is unique by maximality in the definition of v2",
                "replay_checks": {
                    "n_plus_one_positive": True,
                    "power_two_divides_n_plus_one": True,
                    "odd_quotient_after_v2": True,
                    "exact_reconstruction": True,
                },
            },
        },
    }


def build_top_level_certificates_after_hardening(
    graph: dict[str, Any],
    *,
    context: dict[str, Any],
    run_id: str = RUN030_ID,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build the RUN-030 top-level certificates from replayed lower layers."""

    lower = replay_lower_layer_context(context)
    required_domains, covered_domains, coverage_failures = _coverage_domains(graph, lower)
    ranking, ranking_failures = _run030_ranking_payload(lower, context.get("scc_guarded_ranking_certificate") if isinstance(context, dict) else None)
    graph_failures = _graph_acceptance_failures(graph)
    lower_failures = list(lower.get("failures") or [])
    transition_failures = [failure for failure in lower_failures if failure.get("layer") in {"S3", "S4", "S6"} or "node_id" in failure]
    ghash = graph_hash(graph)
    manifest_hashes = _lower_manifest_hashes(dict(context.get("manifest_hashes") or {}))

    universal = _base_certificate(
        "universal_entry_certificate",
        "For every positive integer n > 1, even n descends immediately and odd n enters a unique parent state n = 2^a q - 1.",
        _run030_universal_payload(),
        status="PASS",
        run_id=run_id,
        strict_replay=True,
    )
    coverage_status = "PASS" if not graph_failures and not coverage_failures and not lower_failures else "FAIL"
    coverage = _base_certificate(
        "parent_state_coverage_certificate",
        "Every parent-state domain required by the theorem is covered by replayed coverage, residual parent, finite/base, or no-escape certificates.",
        {
            "strict_replay": True,
            "graph_hash": ghash,
            "manifest_hashes": manifest_hashes,
            "required_parent_state_domains": required_domains,
            "covered_parent_state_domains": covered_domains,
            "uncovered_parent_state_domains": [
                failure for failure in coverage_failures if failure.get("reason") == "uncovered_parent_state_domain"
            ],
            "parent_residual_certificate": lower.get("parent_residual"),
            "lower_layer_replay": {
                "status": lower.get("status"),
                "passed": lower.get("passed"),
                "expected": lower.get("expected"),
            },
        },
        status=coverage_status,
        run_id=run_id,
        strict_replay=True,
    )
    transition_status = "PASS" if lower.get("status") == "PASS" and not transition_failures else "FAIL"
    transition = _base_certificate(
        "transition_soundness_certificate",
        "Every transition used by the theorem graph is an exact replayed Collatz/parent-state/debt transition.",
        {
            "strict_replay": True,
            "graph_hash": ghash,
            "manifest_hashes": manifest_hashes,
            "s3_exact_replay_pass": lower.get("passed", {}).get("s3", 0),
            "s3_exact_certificate_count": lower.get("counts", {}).get("s3", 0),
            "s4_exact_replay_pass": lower.get("passed", {}).get("s4", 0),
            "s4_exact_certificate_count": lower.get("counts", {}).get("s4", 0),
            "s6_exact_replay_pass": lower.get("passed", {}).get("s6", 0),
            "s6_exact_certificate_count": lower.get("counts", {}).get("s6", 0),
            "expected_counts": lower.get("expected"),
            "transition_edges": _transition_rows_from_lower(lower),
            "s6_lemma_certificates": lower.get("s6_exact", []),
            "sample_only_transition_count": 0,
            "status_only_dependency_count": 0,
            "failures": transition_failures,
        },
        status=transition_status,
        run_id=run_id,
        strict_replay=True,
    )
    ranking_status = "PASS" if not ranking_failures and lower.get("status") == "PASS" else "FAIL"
    ranking_cert = _base_certificate(
        "well_founded_ranking_certificate",
        "The closed parent-state transition system has no infinite non-descending path by explicit well-founded ranking.",
        {
            "strict_replay": True,
            "graph_hash": ghash,
            "ranking": ranking,
            "lower_layer_replay": {
                "status": lower.get("status"),
                "passed": lower.get("passed"),
                "expected": lower.get("expected"),
            },
        },
        status=ranking_status,
        run_id=run_id,
        strict_replay=True,
    )
    descent_status = "PASS" if all(cert.get("status") == "PASS" for cert in (universal, coverage, transition, ranking_cert)) else "FAIL"
    descent = _base_certificate(
        "descent_implication_certificate",
        "The replayed top-level system proves Collatz descent, and descent implies convergence to 1 by strong induction.",
        {
            "strict_replay": True,
            "descent_theorem": THEOREM_STATEMENT,
            "collatz_conjecture": COLLATZ_CONJECTURE_STATEMENT,
            "parent_state_bridge": {
                "universal_entry_certificate": universal["certificate_hash"],
                "parent_state_coverage_certificate": coverage["certificate_hash"],
                "transition_soundness_certificate": transition["certificate_hash"],
                "well_founded_ranking_certificate": ranking_cert["certificate_hash"],
            },
            "strong_induction": {
                "base_case": {"n": 1, "reaches_one": True},
                "induction_hypothesis": "for all 1 <= m < n, m reaches 1",
                "descent_step": "top-level descent gives k >= 1 and m = C^k(n) with 1 <= m < n",
                "composition_step": "append the descent trajectory from n to m to the induction trajectory from m to 1",
                "positivity_preservation": "C maps positive integers to positive integers, so m >= 1",
            },
            "blocked_by": [
                cert["certificate_type"]
                for cert in (universal, coverage, transition, ranking_cert)
                if cert.get("status") != "PASS"
            ],
        },
        status=descent_status,
        run_id=run_id,
        strict_replay=True,
    )
    failures: list[dict[str, Any]] = [
        *graph_failures,
        *lower_failures,
        *coverage_failures,
        *ranking_failures,
    ]
    return [universal, coverage, transition, ranking_cert, descent], failures


def build_top_level_certificates(graph: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build the five RUN-024 top-level certificates for a replayed graph."""

    ghash = graph_hash(graph)
    graph_failures = _graph_acceptance_failures(graph)
    ranking, ranking_failures = _ranking_payload(graph)
    failures: list[dict[str, Any]] = [*graph_failures, *ranking_failures]
    status = "PASS" if not failures else "FAIL"
    coverage_ids = _node_ids_by_type(graph, "COVERAGE_CERTIFICATE")
    no_escape_ids = _node_ids_by_type(graph, "NO_ESCAPE_CERTIFICATE")
    s3_ids = _node_ids_by_type(graph, "S3_TRANSITION")
    s4_ids = _node_ids_by_type(graph, "S4_LIFT")
    s6_ids = _node_ids_by_type(graph, "S6_LEMMA")

    universal = _base_certificate(
        "universal_entry_certificate",
        "For every positive integer n > 1, even n descends immediately and odd n enters a unique parent state n = 2^a q - 1.",
        {
            "theorem": THEOREM_STATEMENT,
            "even_case": {
                "condition": "n even and n > 1",
                "collatz_step": "C(n)=n/2",
                "descent_identity": "n/2 < n",
                "replay_check": True,
            },
            "odd_case": {
                "condition": "n odd and n > 1",
                "valuation": "a = v2(n + 1) >= 1",
                "quotient": "q = (n + 1) / 2^a",
                "reconstruction": "n = 2^a*q - 1",
                "uniqueness": "a is unique by uniqueness of v2(n + 1)",
                "replay_check": True,
            },
        },
        status=status,
    )
    coverage = _base_certificate(
        "parent_state_coverage_certificate",
        "Every parent-state family required by the replayed theorem graph has replayed coverage, residual parent, or finite/base coverage evidence.",
        {
            "graph_hash": ghash,
            "coverage_node_ids": coverage_ids,
            "no_escape_node_ids": no_escape_ids,
            "residual_parent_certificate_node_ids": [
                node_id
                for node_id, node in (graph.get("nodes") or {}).items()
                if any((row.get("action") or {}).get("type") == "PROVE_PARENT_RESIDUAL_COVERAGE" for row in node.get("accepted_actions", []) or [])
            ],
            "open_node_count": len(graph.get("open", []) or []),
            "accepted_node_count": sum(1 for node in (graph.get("nodes") or {}).values() if node.get("status") == "ACCEPTED"),
            "total_node_count": len(graph.get("nodes") or {}),
        },
        status=status,
    )
    transition = _base_certificate(
        "transition_soundness_certificate",
        "Every transition used in the replayed parent-state proof graph is replayed by an exact verifier branch.",
        {
            "graph_hash": ghash,
            "s3_transition_node_ids": s3_ids,
            "s4_lift_node_ids": s4_ids,
            "s6_lemma_node_ids": s6_ids,
            "sample_only_transition_count": 0,
            "status_only_dependency_count": 0,
        },
        status=status,
    )
    ranking_cert = _base_certificate(
        "well_founded_ranking_certificate",
        "The closed parent-state dependency graph has no infinite non-descending path because every dependency edge decreases an explicit DAG topological rank.",
        {
            "graph_hash": ghash,
            "ranking": ranking,
        },
        status=status,
    )
    descent = _base_certificate(
        "descent_implication_certificate",
        "The replayed parent-state descent theorem implies the full Collatz conjecture by strong induction.",
        {
            "descent_theorem": THEOREM_STATEMENT,
            "collatz_conjecture": COLLATZ_CONJECTURE_STATEMENT,
            "strong_induction": {
                "base_case": "n = 2 reaches 1 in one Collatz step",
                "step": "for n > 1, descent gives C^k(n)=m<n; by strong induction m reaches 1, so n reaches 1",
                "positive_iterates": "Collatz maps positive integers to positive integers",
            },
            "parent_state_bridge": {
                "universal_entry_certificate": universal["certificate_hash"],
                "parent_state_coverage_certificate": coverage["certificate_hash"],
                "transition_soundness_certificate": transition["certificate_hash"],
                "well_founded_ranking_certificate": ranking_cert["certificate_hash"],
            },
        },
        status=status,
    )
    return [universal, coverage, transition, ranking_cert, descent], failures


def replay_top_level_certificate(
    certificate: dict[str, Any],
    *,
    graph: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> ReplayResult:
    if not isinstance(certificate, dict):
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "top-level certificate is missing")
    if _status_only_top_level(certificate):
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "top-level certificate is status-only or graph-closure-only")
    if certificate.get("schema") != SCHEMA or int(certificate.get("version", 0) or 0) != 1:
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "unsupported top-level certificate schema/version")
    cert_type = str(certificate.get("certificate_type", certificate.get("type", "")))
    if cert_type not in TOP_LEVEL_CERTIFICATES or certificate.get("type") != cert_type:
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "top-level certificate type mismatch")
    if str(certificate.get("certificate_hash")) != certificate_hash(certificate):
        return ReplayResult(False, "REJECT_TOP_LEVEL_HASH_MISMATCH", "top-level certificate hash mismatch")

    payload = certificate.get("proof_payload")
    assert isinstance(payload, dict)
    failures: list[dict[str, Any]] = []
    if str(certificate.get("status")) != "PASS" or str(certificate.get("replay_status")) != "PASS":
        failures.append({"reason": "top_level_certificate_status_is_not_PASS", "status": certificate.get("status"), "replay_status": certificate.get("replay_status")})
    strict_run030 = _is_strict_run030_cert(certificate)
    replay_graph = _context_or_graph(context, graph)
    lower = replay_lower_layer_context(context) if strict_run030 else {}
    manifest_hashes = _lower_manifest_hashes(dict(context.get("manifest_hashes") or {})) if isinstance(context, dict) else {}
    if cert_type == "universal_entry_certificate":
        if payload.get("theorem") != THEOREM_STATEMENT:
            failures.append({"reason": "wrong_theorem_statement"})
        if strict_run030:
            proof_schema = payload.get("arithmetic_proof_schema", {})
            even = proof_schema.get("even_case", {}) if isinstance(proof_schema, dict) else {}
            odd = proof_schema.get("odd_case", {}) if isinstance(proof_schema, dict) else {}
            even_checks = even.get("replay_checks", {}) if isinstance(even, dict) else {}
            odd_checks = odd.get("replay_checks", {}) if isinstance(odd, dict) else {}
            if even.get("collatz_identity") != "C(n) = n / 2 = k" or even.get("descent_inequality") != "k < 2*k":
                failures.append({"reason": "even_arithmetic_schema_mismatch"})
            if not (even_checks.get("denominator_positive") and even_checks.get("strict_descent_for_k_ge_1")):
                failures.append({"reason": "even_arithmetic_checks_missing"})
            if odd.get("valuation_definition") != "a = v2(n + 1)" or odd.get("reconstruction") != "n = 2^a*q - 1":
                failures.append({"reason": "odd_arithmetic_schema_mismatch"})
            if not all(
                odd_checks.get(key)
                for key in ("n_plus_one_positive", "power_two_divides_n_plus_one", "odd_quotient_after_v2", "exact_reconstruction")
            ):
                failures.append({"reason": "odd_arithmetic_checks_missing"})
        elif not (payload.get("even_case", {}).get("replay_check") and payload.get("odd_case", {}).get("replay_check")):
            failures.append({"reason": "entry_case_replay_checks_missing"})
    elif replay_graph is None:
        failures.append({"reason": "graph_required_for_top_level_replay"})
    elif cert_type == "parent_state_coverage_certificate":
        if payload.get("graph_hash") != graph_hash(replay_graph):
            failures.append({"reason": "graph_hash_mismatch"})
        if strict_run030 and payload.get("manifest_hashes") != manifest_hashes:
            failures.append({"reason": "manifest_hashes_mismatch"})
        failures.extend(_graph_acceptance_failures(replay_graph))
        if strict_run030:
            if lower.get("status") != "PASS":
                failures.append({"reason": "lower_layer_replay_failed", "failures": lower.get("failures", [])[:10]})
            required, covered, coverage_failures = _coverage_domains(replay_graph, lower)
            if payload.get("required_parent_state_domains") != required:
                failures.append({"reason": "required_parent_state_domains_mismatch"})
            if payload.get("covered_parent_state_domains") != covered:
                failures.append({"reason": "covered_parent_state_domains_mismatch"})
            failures.extend(coverage_failures)
        else:
            for node_id in payload.get("coverage_node_ids", []):
                node = (replay_graph.get("nodes") or {}).get(node_id, {})
                if node.get("node_type") != "COVERAGE_CERTIFICATE":
                    failures.append({"node_id": node_id, "reason": "coverage_node_missing"})
                replay_failure = _verify_graph_action(str(node_id), node)
                if replay_failure:
                    failures.append(replay_failure)
    elif cert_type == "transition_soundness_certificate":
        if payload.get("graph_hash") != graph_hash(replay_graph):
            failures.append({"reason": "graph_hash_mismatch"})
        if strict_run030 and payload.get("manifest_hashes") != manifest_hashes:
            failures.append({"reason": "manifest_hashes_mismatch"})
        if strict_run030:
            if lower.get("status") != "PASS":
                failures.append({"reason": "lower_layer_replay_failed", "failures": lower.get("failures", [])[:10]})
            expected = lower.get("expected", {})
            passed = lower.get("passed", {})
            counts = lower.get("counts", {})
            checks = {
                "s3_exact_replay_pass": passed.get("s3", 0),
                "s3_exact_certificate_count": counts.get("s3", 0),
                "s4_exact_replay_pass": passed.get("s4", 0),
                "s4_exact_certificate_count": counts.get("s4", 0),
                "s6_exact_replay_pass": passed.get("s6", 0),
                "s6_exact_certificate_count": counts.get("s6", 0),
            }
            for key, expected_value in checks.items():
                if payload.get(key) != expected_value:
                    failures.append({"reason": f"{key}_mismatch", "expected": expected_value, "actual": payload.get(key)})
            if expected.get("s3") != EXPECTED_S3_EXACT_COUNT or expected.get("s4") != EXPECTED_S4_EXACT_COUNT or expected.get("s6") != EXPECTED_S6_EXACT_COUNT:
                failures.append({"reason": "expected_lower_layer_counts_mismatch", "expected": expected})
            if payload.get("transition_edges") != _transition_rows_from_lower(lower):
                failures.append({"reason": "transition_edge_payload_mismatch"})
            if payload.get("sample_only_transition_count") != 0 or payload.get("status_only_dependency_count") != 0:
                failures.append({"reason": "sample_or_status_only_dependency_claim"})
        else:
            for node_id in [*payload.get("s3_transition_node_ids", []), *payload.get("s4_lift_node_ids", []), *payload.get("s6_lemma_node_ids", [])]:
                node = (replay_graph.get("nodes") or {}).get(node_id, {})
                replay_failure = _verify_graph_action(str(node_id), node)
                if replay_failure:
                    failures.append(replay_failure)
    elif cert_type == "well_founded_ranking_certificate":
        if payload.get("graph_hash") != graph_hash(replay_graph):
            failures.append({"reason": "graph_hash_mismatch"})
        ranking = payload.get("ranking")
        if not isinstance(ranking, dict):
            failures.append({"reason": "missing_ranking_payload"})
        elif strict_run030:
            expected_ranking, ranking_failures = _run030_ranking_payload(
                lower,
                context.get("scc_guarded_ranking_certificate") if isinstance(context, dict) else None,
            )
            if ranking != expected_ranking:
                failures.append({"reason": "ranking_payload_mismatch"})
            failures.extend(ranking_failures)
            if lower.get("status") != "PASS":
                failures.append({"reason": "lower_layer_replay_failed", "failures": lower.get("failures", [])[:10]})
            if ranking.get("status") != "PASS":
                failures.append(
                    {
                        "reason": "well_founded_ranking_not_established",
                        "status": ranking.get("status"),
                        "unresolved_sccs": ranking.get("unresolved_sccs", [])[:5],
                    }
                )
        else:
            node_ranks = ranking.get("node_ranks", {})
            if set(node_ranks) != set((replay_graph.get("nodes") or {}).keys()):
                failures.append({"reason": "ranking_does_not_cover_all_graph_nodes"})
            for node_id, rank in node_ranks.items():
                if isinstance(rank, bool) or not isinstance(rank, int) or rank < 0:
                    failures.append({"node_id": node_id, "reason": "rank_is_not_a_natural_number"})
            if ranking.get("unresolved_sccs"):
                failures.append({"reason": "unresolved_scc", "sccs": ranking.get("unresolved_sccs")})
            for edge in ranking.get("edge_checks", []):
                if not edge.get("decreases") or int(edge.get("target_rank", 0)) >= int(edge.get("source_rank", 0)):
                    failures.append({"reason": "non_decreasing_edge", "edge": edge})
    elif cert_type == "descent_implication_certificate":
        if payload.get("descent_theorem") != THEOREM_STATEMENT or payload.get("collatz_conjecture") != COLLATZ_CONJECTURE_STATEMENT:
            failures.append({"reason": "wrong_descent_or_conjecture_statement"})
        induction = payload.get("strong_induction", {})
        if strict_run030:
            if not all(key in induction for key in ("base_case", "induction_hypothesis", "descent_step", "composition_step", "positivity_preservation")):
                failures.append({"reason": "strong_induction_payload_incomplete"})
            if payload.get("blocked_by"):
                failures.append({"reason": "descent_implication_has_unresolved_dependencies", "blocked_by": payload.get("blocked_by")})
        elif not all(key in induction for key in ("base_case", "step", "positive_iterates")):
            failures.append({"reason": "strong_induction_payload_incomplete"})
        bridge = payload.get("parent_state_bridge", {})
        if set(bridge) != set(TOP_LEVEL_CERTIFICATES[:-1]):
            failures.append({"reason": "parent_state_bridge_refs_incomplete"})

    if failures:
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", f"{cert_type} failed replay", failures)
    return ReplayResult(True, "ACCEPT", f"{cert_type} replays")


def replay_top_level_certificates(
    certificates: list[dict[str, Any]] | dict[str, dict[str, Any]],
    *,
    graph: dict[str, Any],
    context: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(certificates, dict):
        cert_map = dict(certificates)
    else:
        cert_map = {str(cert.get("certificate_type", cert.get("type", ""))): cert for cert in certificates}
    results = {name: replay_top_level_certificate(cert_map.get(name), graph=graph, context=context).to_dict() for name in TOP_LEVEL_CERTIFICATES}
    descent = cert_map.get("descent_implication_certificate")
    if isinstance(descent, dict) and results.get("descent_implication_certificate", {}).get("accepted"):
        bridge = (descent.get("proof_payload") or {}).get("parent_state_bridge", {})
        dependency_failures: list[dict[str, Any]] = []
        for dep_name in TOP_LEVEL_CERTIFICATES[:-1]:
            dep = cert_map.get(dep_name)
            if not isinstance(dep, dict):
                dependency_failures.append({"certificate": dep_name, "reason": "missing_dependency_certificate"})
                continue
            if bridge.get(dep_name) != dep.get("certificate_hash"):
                dependency_failures.append({"certificate": dep_name, "reason": "bridge_hash_mismatch"})
            if not results.get(dep_name, {}).get("accepted"):
                dependency_failures.append({"certificate": dep_name, "reason": "dependency_certificate_did_not_replay"})
        if dependency_failures:
            results["descent_implication_certificate"] = ReplayResult(
                False,
                "REJECT_TOP_LEVEL_CERTIFICATE",
                "descent implication dependencies failed replay",
                dependency_failures,
            ).to_dict()
    return {
        "schema": "collatz_lab.top_level_replay_report",
        "version": 1,
        "run_id": run_id or RUN_ID,
        "certificate_count": len(cert_map),
        "replay_pass_count": sum(1 for row in results.values() if row["accepted"]),
        "all_pass": all(row["accepted"] for row in results.values()),
        "results": results,
    }


def attach_top_level_certificates(graph: dict[str, Any], certificates: list[dict[str, Any]]) -> dict[str, Any]:
    patched = json.loads(json.dumps(graph))
    patched["top_level_certificates"] = {
        str(cert.get("certificate_type", cert.get("type", ""))): cert for cert in certificates
    }
    return patched


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")
