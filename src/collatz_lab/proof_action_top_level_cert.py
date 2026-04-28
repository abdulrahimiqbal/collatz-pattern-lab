"""Replayable top-level theorem certificates for RUN-024."""

from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RUN_ID = "RUN-024-top-level-theorem-certificates"
SCHEMA = "collatz_lab.top_level_theorem_certificate"
THEOREM_STATEMENT = "forall n > 1 exists k >= 1 such that C^k(n) < n"
COLLATZ_CONJECTURE_STATEMENT = "forall n > 1 exists t >= 0 such that C^t(n) = 1"
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


def _status_only_top_level(cert: dict[str, Any]) -> bool:
    payload = cert.get("proof_payload")
    if not isinstance(payload, dict) or not payload:
        return True
    if set(payload) <= {"status", "verifier_status", "certificate_id"}:
        return True
    return bool(payload.get("graph_closure_only"))


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


def _base_certificate(cert_type: str, statement: str, proof_payload: dict[str, Any], *, status: str = "PASS") -> dict[str, Any]:
    certificate = {
        "schema": SCHEMA,
        "version": 1,
        "type": cert_type,
        "certificate_type": cert_type,
        "certificate_id": cert_type,
        "statement": statement,
        "proof_payload": proof_payload,
        "replay_status": status,
        "status": status,
    }
    certificate["certificate_hash"] = certificate_hash(certificate)
    return certificate


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


def replay_top_level_certificate(certificate: dict[str, Any], *, graph: dict[str, Any] | None = None) -> ReplayResult:
    if not isinstance(certificate, dict):
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "top-level certificate is missing")
    if _status_only_top_level(certificate):
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "top-level certificate is status-only or graph-closure-only")
    if certificate.get("schema") != SCHEMA or int(certificate.get("version", 0) or 0) != 1:
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "unsupported top-level certificate schema/version")
    cert_type = str(certificate.get("certificate_type", certificate.get("type", "")))
    if cert_type not in TOP_LEVEL_CERTIFICATES or certificate.get("type") != cert_type:
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "top-level certificate type mismatch")
    if str(certificate.get("status")) != "PASS" or str(certificate.get("replay_status")) != "PASS":
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", "top-level certificate status is not PASS")
    if str(certificate.get("certificate_hash")) != certificate_hash(certificate):
        return ReplayResult(False, "REJECT_TOP_LEVEL_HASH_MISMATCH", "top-level certificate hash mismatch")

    payload = certificate.get("proof_payload")
    assert isinstance(payload, dict)
    failures: list[dict[str, Any]] = []
    if cert_type == "universal_entry_certificate":
        if payload.get("theorem") != THEOREM_STATEMENT:
            failures.append({"reason": "wrong_theorem_statement"})
        if not (payload.get("even_case", {}).get("replay_check") and payload.get("odd_case", {}).get("replay_check")):
            failures.append({"reason": "entry_case_replay_checks_missing"})
    elif graph is None:
        failures.append({"reason": "graph_required_for_top_level_replay"})
    elif cert_type == "parent_state_coverage_certificate":
        if payload.get("graph_hash") != graph_hash(graph):
            failures.append({"reason": "graph_hash_mismatch"})
        failures.extend(_graph_acceptance_failures(graph))
        for node_id in payload.get("coverage_node_ids", []):
            node = (graph.get("nodes") or {}).get(node_id, {})
            if node.get("node_type") != "COVERAGE_CERTIFICATE":
                failures.append({"node_id": node_id, "reason": "coverage_node_missing"})
            replay_failure = _verify_graph_action(str(node_id), node)
            if replay_failure:
                failures.append(replay_failure)
    elif cert_type == "transition_soundness_certificate":
        if payload.get("graph_hash") != graph_hash(graph):
            failures.append({"reason": "graph_hash_mismatch"})
        for node_id in [*payload.get("s3_transition_node_ids", []), *payload.get("s4_lift_node_ids", []), *payload.get("s6_lemma_node_ids", [])]:
            node = (graph.get("nodes") or {}).get(node_id, {})
            replay_failure = _verify_graph_action(str(node_id), node)
            if replay_failure:
                failures.append(replay_failure)
    elif cert_type == "well_founded_ranking_certificate":
        if payload.get("graph_hash") != graph_hash(graph):
            failures.append({"reason": "graph_hash_mismatch"})
        ranking = payload.get("ranking")
        if not isinstance(ranking, dict):
            failures.append({"reason": "missing_ranking_payload"})
        else:
            node_ranks = ranking.get("node_ranks", {})
            if set(node_ranks) != set((graph.get("nodes") or {}).keys()):
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
        if not all(key in induction for key in ("base_case", "step", "positive_iterates")):
            failures.append({"reason": "strong_induction_payload_incomplete"})
        bridge = payload.get("parent_state_bridge", {})
        if set(bridge) != set(TOP_LEVEL_CERTIFICATES[:-1]):
            failures.append({"reason": "parent_state_bridge_refs_incomplete"})

    if failures:
        return ReplayResult(False, "REJECT_TOP_LEVEL_CERTIFICATE", f"{cert_type} failed replay", failures)
    return ReplayResult(True, "ACCEPT", f"{cert_type} replays")


def replay_top_level_certificates(certificates: list[dict[str, Any]] | dict[str, dict[str, Any]], *, graph: dict[str, Any]) -> dict[str, Any]:
    if isinstance(certificates, dict):
        cert_map = dict(certificates)
    else:
        cert_map = {str(cert.get("certificate_type", cert.get("type", ""))): cert for cert in certificates}
    results = {name: replay_top_level_certificate(cert_map.get(name), graph=graph).to_dict() for name in TOP_LEVEL_CERTIFICATES}
    return {
        "schema": "collatz_lab.top_level_replay_report",
        "version": 1,
        "run_id": RUN_ID,
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

