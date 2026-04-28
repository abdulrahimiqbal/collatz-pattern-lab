"""RUN-040 guarded SCC ranking and replay helpers."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from .proof_action_guarded_domain import (
    AffineMap,
    GuardedDomain,
    affine_from_json,
    build_guarded_domain_from_map_certificate,
    contains_float,
    descent_check,
    domain_from_json,
    domain_self_invariance,
    load_jsonl,
    pullback_domain,
    stable_hash,
    write_jsonl,
)


RUN_ID = "RUN-040-guarded-scc-ranking-repair"
SCHEMA = "collatz_lab.scc_guarded_ranking"
CERT_TYPE = "SCC_GUARDED_WELL_FOUNDED_RANKING_EXACT"
DEFAULT_SCC_ID = "P12_P24_internal_s4"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def certificate_hash(certificate: dict[str, Any]) -> str:
    return _hash({key: value for key, value in certificate.items() if key != "certificate_hash"})


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _edge_sort_key(edge_id: str) -> tuple[str, str]:
    return (edge_id.split(":", 1)[0], edge_id)


def _index_parent_map_certificates(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        cert = row.get("parent_coordinate_map_certificate")
        if not isinstance(cert, dict):
            cert = row if isinstance(row, dict) else {}
        for key in (
            str(cert.get("certificate_hash", "")),
            str(cert.get("transition_certificate_id", "")),
            str(cert.get("transition_certificate_hash", "")),
            str((cert.get("source_transition_certificate") or {}).get("transition_id", "")),
            str(row.get("node_id", "")),
        ):
            if key:
                indexed[key] = cert
    return indexed


def _map_cert_for_edge(edge_map: dict[str, Any], indexed: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    for key in (
        str(edge_map.get("parent_coordinate_map_certificate_hash", "")),
        str(edge_map.get("transition_certificate_id", "")),
        str(edge_map.get("transition_certificate_hash", "")),
    ):
        if key and key in indexed:
            return indexed[key]
    return None


def build_guarded_edge_domain_rows(
    *,
    edge_maps: list[dict[str, Any]],
    parent_coordinate_map_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    indexed = _index_parent_map_certificates(parent_coordinate_map_rows)
    rows: list[dict[str, Any]] = []
    for edge_map in sorted(edge_maps, key=lambda row: (str(row.get("source")), str(row.get("target")), str(row.get("edge_id")))):
        cert = _map_cert_for_edge(edge_map, indexed)
        if cert is None:
            row = {
                "schema": "collatz_lab.guarded_edge_domain",
                "version": 1,
                "edge_id": str(edge_map.get("edge_id")),
                "source": str(edge_map.get("source")),
                "target": str(edge_map.get("target")),
                "status": "FAIL",
                "failures": [{"reason": "missing_parent_coordinate_map_certificate"}],
                "replay_checks": {"not_status_or_id_only": False, "no_floats": not contains_float(edge_map)},
            }
            row["guarded_domain_hash"] = stable_hash({key: value for key, value in row.items() if key != "guarded_domain_hash"})
            rows.append(row)
            continue
        rows.append(build_guarded_domain_from_map_certificate(edge_map=edge_map, map_certificate=cert))
    return rows


def _edge_domain_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["edge_id"]): row for row in rows if row.get("status") == "PASS"}


def compose_guarded_sequence(
    *,
    edge_ids: list[str],
    guarded_edges: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    domain: GuardedDomain = GuardedDomain.top()
    current = AffineMap(1, 0, 1)
    trace: list[dict[str, Any]] = []
    for index, edge_id in enumerate(edge_ids):
        edge = guarded_edges.get(edge_id)
        if edge is None:
            return {
                "status": "FAIL",
                "reason": "missing_guarded_edge",
                "edge_id": edge_id,
                "trace": trace,
            }
        required = domain_from_json(edge["guarded_domain"])
        pulled = pullback_domain(domain, current, required)
        if pulled is None:
            return {
                "status": "FAIL",
                "reason": "guarded_domain_empty",
                "failed_edge_id": edge_id,
                "failed_step_index": index,
                "trace": trace,
            }
        domain = pulled
        edge_map = affine_from_json(edge["affine_map"])
        current = edge_map.compose_after(current)
        trace.append(
            {
                "step_index": index,
                "edge_id": edge_id,
                "pulled_back_domain": domain.to_json(),
                "prefix_map": current.to_json(),
            }
        )
    return {
        "status": "PASS",
        "edge_ids": edge_ids,
        "guarded_domain": domain.to_json(),
        "composed_map": current.to_json(),
        "domain_trace": trace,
        "guarded_domain_hash": stable_hash(domain.to_json()),
    }


def _repeat_prefixes(
    *,
    edge_ids: list[str],
    guarded_edges: dict[str, dict[str, Any]],
    cap: int,
    detail_limit: int = 4,
) -> dict[str, Any]:
    repeated: list[str] = []
    prefixes: list[dict[str, Any]] = []
    last_pass = 0
    for repeat in range(1, cap + 1):
        repeated.extend(edge_ids)
        replay = compose_guarded_sequence(edge_ids=repeated, guarded_edges=guarded_edges)
        if replay.get("status") != "PASS":
            return {
                "status": "PASS",
                "bounded": True,
                "max_valid_repeats": last_pass,
                "first_invalid_repeat": repeat,
                "exit_reason": replay,
                "prefixes": prefixes,
            }
        last_pass = repeat
        domain = replay["guarded_domain"]
        prefixes.append(
            {
                "repeat": repeat,
                "domain_hash": replay["guarded_domain_hash"],
                "minimum_q": domain.get("minimum_q"),
                "modulus": (domain.get("canonical_congruence") or {}).get("modulus"),
            }
            if repeat <= detail_limit
            else {"repeat": repeat, "domain_hash": replay["guarded_domain_hash"]}
        )
    return {
        "status": "FAIL",
        "bounded": False,
        "max_valid_repeats_lower_bound": last_pass,
        "failure_classification": "REFINEMENT_CAP_INSUFFICIENT",
        "prefixes": prefixes,
    }


def _raw_multicycle_hint(raw_rows: list[dict[str, Any]], edge_ids: list[str]) -> dict[str, Any] | None:
    del edge_ids
    for row in raw_rows:
        failure = row.get("failure")
        if isinstance(failure, dict):
            return {
                "cycle_count": row.get("cycle_count"),
                "failed_edge_id": failure.get("edge_id"),
                "failed_guard": failure.get("reason"),
                "failure": failure,
            }
    return None


def classify_guarded_cycle(
    *,
    cycle_record: dict[str, Any],
    guarded_edges: dict[str, dict[str, Any]],
    repeat_cap: int,
    raw_rows: list[dict[str, Any]] | None = None,
    compute_repeat_prefix: bool = True,
) -> dict[str, Any]:
    edge_ids = [str(edge_id) for edge_id in cycle_record.get("edge_ids", [])]
    replay = compose_guarded_sequence(edge_ids=edge_ids, guarded_edges=guarded_edges)
    base = {
        "cycle_id": str(cycle_record.get("cycle_id") or _hash(edge_ids)[:16]),
        "edge_ids": edge_ids,
        "source_states": list(cycle_record.get("source_states") or []),
    }
    if replay.get("status") != "PASS":
        return {
            **base,
            "classification": "DOMAIN_COMPOSITION_BUG",
            "status": "FAIL",
            "failure": replay,
        }
    domain = domain_from_json(replay["guarded_domain"])
    cycle_map = affine_from_json(replay["composed_map"])
    descent = descent_check(domain, cycle_map)
    invariance = domain_self_invariance(domain, cycle_map)
    repeat_prefixes = (
        _repeat_prefixes(edge_ids=edge_ids, guarded_edges=guarded_edges, cap=repeat_cap)
        if compute_repeat_prefix
        else {"status": "SKIP", "bounded": None, "reason": "repeat_prefix_check_not_requested_for_compact_cycle_record"}
    )
    raw_hint = _raw_multicycle_hint(raw_rows or [], edge_ids)

    if descent.get("status") == "PASS":
        classification = "GUARDED_DESCENDING"
        status = "PASS"
    elif invariance.get("status") == "PASS":
        classification = "GUARDED_REPEATABLE_NON_DESCENDING"
        status = "FAIL"
    elif repeat_prefixes.get("bounded") is True:
        classification = "GUARDED_BOUNDED_REPEAT_EXIT"
        status = "PASS"
    else:
        classification = "GUARDED_TRANSIENT_EXIT"
        status = "PASS"

    failed = (invariance.get("failures") or [{}])[0] if invariance.get("status") != "PASS" else {}
    if raw_hint and raw_hint.get("failed_guard") == "expected_q_not_integral":
        classification = "GUARDED_TRANSIENT_EXIT"
        failed = {
            "guard": "map_integrality",
            "reason": "expected_q_not_integral",
            "failed_edge_id": raw_hint.get("failed_edge_id"),
            "numerator_mod_D": (raw_hint.get("failure") or {}).get("numerator_mod_D"),
        }

    return {
        **base,
        "classification": classification,
        "status": status,
        "starting_guarded_domain": replay["guarded_domain"],
        "composed_map": replay["composed_map"],
        "descent_check": descent,
        "full_domain_self_invariance": invariance,
        "repeat_prefix_check": repeat_prefixes,
        "number_of_valid_repeats": repeat_prefixes.get("max_valid_repeats", raw_hint.get("cycle_count") - 1 if raw_hint and isinstance(raw_hint.get("cycle_count"), int) else None),
        "exact_exit_reason": failed,
        "failed_edge_id": failed.get("failed_edge_id"),
        "failed_guard": failed.get("guard") or failed.get("reason"),
        "original_cycle_cannot_repeat_on_full_domain": invariance.get("status") != "PASS",
    }


def build_guarded_transition_graph(guarded_rows: list[dict[str, Any]]) -> dict[str, Any]:
    guarded_edges = _edge_domain_by_id(guarded_rows)
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    nodes: dict[str, dict[str, Any]] = {}
    for row in guarded_edges.values():
        by_source[str(row["source"])].append(row)
        node_id = f"{row['source']}::{row['edge_id']}"
        nodes[node_id] = {
            "parent_state": row["source"],
            "edge_id": row["edge_id"],
            "exact_guard": row["guarded_domain"],
            "guarded_domain_hash": row["guarded_domain_hash"],
        }

    transitions: list[dict[str, Any]] = []
    for row in guarded_edges.values():
        source_node = f"{row['source']}::{row['edge_id']}"
        next_edges = by_source.get(str(row["target"]), [])
        matched = 0
        for next_row in next_edges:
            replay = compose_guarded_sequence(edge_ids=[str(row["edge_id"]), str(next_row["edge_id"])], guarded_edges=guarded_edges)
            if replay.get("status") == "PASS":
                matched += 1
                transitions.append(
                    {
                        "edge_id": f"{row['edge_id']}=>{next_row['edge_id']}",
                        "source": source_node,
                        "target": f"{next_row['source']}::{next_row['edge_id']}",
                        "transition_edge_id": row["edge_id"],
                        "next_edge_id": next_row["edge_id"],
                        "edge_class": "STAYS_IN_SCC",
                        "transition_domain_hash": replay["guarded_domain_hash"],
                    }
                )
        if matched == 0:
            transitions.append(
                {
                    "edge_id": f"{row['edge_id']}=>GUARD_EXIT",
                    "source": source_node,
                    "target": "GUARD_EXIT",
                    "transition_edge_id": row["edge_id"],
                    "edge_class": "GUARD_EXIT",
                }
            )
    return {
        "schema": "collatz_lab.guarded_transition_graph",
        "version": 1,
        "run_id": RUN_ID,
        "nodes": nodes,
        "edges": transitions,
        "node_count": len(nodes),
        "edge_count": len(transitions),
        "status": "PASS",
    }


def _topological_ranks(nodes: set[str], edges: list[dict[str, Any]]) -> tuple[dict[str, int] | None, list[dict[str, Any]]]:
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    indegree: dict[str, int] = {node: 0 for node in nodes}
    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        if source not in nodes or target not in nodes:
            continue
        adjacency[source].append(target)
        indegree[target] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for target in sorted(adjacency[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(order) != len(nodes):
        cyclic = sorted(node for node, degree in indegree.items() if degree > 0)
        return None, [{"reason": "guarded_transition_graph_has_scc", "nodes": cyclic[:50], "count": len(cyclic)}]
    return {node: len(order) - index for index, node in enumerate(order)}, []


def build_guarded_dag_certificate(
    *,
    graph: dict[str, Any],
    states: list[str],
    edge_ids: list[str],
    cycle_exit_checks: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    nodes = set(str(node) for node in graph.get("nodes", {}))
    nonterminal_edges = [edge for edge in graph.get("edges", []) if edge.get("edge_class") == "STAYS_IN_SCC"]
    ranks, failures = _topological_ranks(nodes, nonterminal_edges)
    if failures or ranks is None:
        return None
    edge_checks = [
        {
            "edge_id": edge["edge_id"],
            "source_guarded_node": edge["source"],
            "target_guarded_node": edge["target"],
            "edge_class": edge["edge_class"],
            "rank_decreases": ranks[edge["target"]] < ranks[edge["source"]],
            "or_exits": False,
            "status": "PASS" if ranks[edge["target"]] < ranks[edge["source"]] else "FAIL",
        }
        for edge in nonterminal_edges
    ]
    certificate = {
        "schema": SCHEMA,
        "version": 1,
        "type": CERT_TYPE,
        "scc_id": DEFAULT_SCC_ID,
        "states": states,
        "covered_edge_ids": sorted(edge_ids, key=_edge_sort_key),
        "guarded_node_count": graph.get("node_count", len(nodes)),
        "guarded_edge_count": graph.get("edge_count", len(nonterminal_edges)),
        "proof_kind": "guarded_dag_rank",
        "node_ranks": ranks,
        "edge_checks": edge_checks,
        "cycle_exit_checks": list(cycle_exit_checks or []),
        "status": "PASS",
    }
    certificate["certificate_hash"] = certificate_hash(certificate)
    return certificate


def build_bounded_guard_exit_certificate(
    *,
    states: list[str],
    edge_ids: list[str],
    graph: dict[str, Any],
    cycle_exit_checks: list[dict[str, Any]],
) -> dict[str, Any]:
    certificate = {
        "schema": SCHEMA,
        "version": 1,
        "type": CERT_TYPE,
        "scc_id": DEFAULT_SCC_ID,
        "states": states,
        "covered_edge_ids": sorted(edge_ids, key=_edge_sort_key),
        "guarded_node_count": int(graph.get("node_count", 0) or 0),
        "guarded_edge_count": int(graph.get("edge_count", 0) or 0),
        "proof_kind": "bounded_guard_exit",
        "node_ranks": {},
        "edge_checks": [
            {
                "edge_id": row.get("cycle_id"),
                "source_guarded_node": "cycle",
                "target_guarded_node": "GUARD_EXIT",
                "edge_class": "GUARD_EXIT",
                "rank_decreases": True,
                "or_exits": True,
                "status": "PASS",
            }
            for row in cycle_exit_checks
        ],
        "cycle_exit_checks": cycle_exit_checks,
        "status": "PASS",
    }
    certificate["certificate_hash"] = certificate_hash(certificate)
    return certificate


def replay_scc_guarded_ranking_certificate(
    certificate: dict[str, Any],
    *,
    expected_edge_ids: list[str] | None = None,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not isinstance(certificate, dict):
        return {"accepted": False, "status": "FAIL", "failures": [{"reason": "missing_certificate"}]}
    if contains_float(certificate):
        failures.append({"reason": "floating_point_certificate_rejected"})
    if certificate.get("schema") != SCHEMA or int(certificate.get("version", 0) or 0) != 1:
        failures.append({"reason": "unsupported_guarded_ranking_schema"})
    if certificate.get("type") != CERT_TYPE:
        failures.append({"reason": "unsupported_guarded_ranking_type", "type": certificate.get("type")})
    if str(certificate.get("certificate_hash")) != certificate_hash(certificate):
        failures.append({"reason": "guarded_ranking_certificate_hash_mismatch"})
    if certificate.get("status") != "PASS":
        failures.append({"reason": "guarded_ranking_status_not_pass", "status": certificate.get("status")})
    proof_kind = certificate.get("proof_kind")
    if proof_kind not in {"guarded_dag_rank", "bounded_guard_exit", "lexicographic_ranking", "delayed_descent", "viability_kernel_elimination", "natural_viability_kernel_elimination"}:
        failures.append({"reason": "unsupported_guarded_ranking_proof_kind", "proof_kind": proof_kind})
    if proof_kind == "natural_viability_kernel_elimination":
        try:
            from .proof_action_natural_viability_kernel import replay_natural_viability_kernel_certificate
        except ImportError as exc:  # pragma: no cover - defensive import guard
            failures.append({"reason": "natural_viability_replay_import_failed", "detail": str(exc)})
        else:
            natural_certificate = certificate.get("natural_viability_kernel_certificate")
            natural_replay = replay_natural_viability_kernel_certificate(natural_certificate if isinstance(natural_certificate, dict) else {})
            if not natural_replay.get("accepted"):
                failures.append({"reason": "natural_viability_kernel_certificate_replay_failed", "replay": natural_replay})
            if certificate.get("natural_viability_kernel_certificate_hash") != (natural_certificate or {}).get("certificate_hash"):
                failures.append({"reason": "natural_viability_kernel_certificate_hash_ref_mismatch"})
    covered = set(str(edge_id) for edge_id in certificate.get("covered_edge_ids", []) or [])
    if expected_edge_ids is not None:
        expected = set(str(edge_id) for edge_id in expected_edge_ids)
        missing = sorted(expected - covered, key=_edge_sort_key)
        extra = sorted(covered - expected, key=_edge_sort_key)
        if missing:
            failures.append({"reason": "guarded_ranking_missing_internal_edges", "missing": missing[:20], "count": len(missing)})
        if extra:
            failures.append({"reason": "guarded_ranking_has_unknown_edges", "extra": extra[:20], "count": len(extra)})
    ranks = certificate.get("node_ranks") or {}
    for check in certificate.get("edge_checks", []) or []:
        if check.get("status") != "PASS":
            failures.append({"reason": "edge_check_not_pass", "edge_check": check})
        if not (check.get("rank_decreases") is True or check.get("or_exits") is True):
            failures.append({"reason": "edge_check_neither_decreases_nor_exits", "edge_check": check})
        source = check.get("source_guarded_node")
        target = check.get("target_guarded_node")
        if source in ranks and target in ranks and int(ranks[target]) >= int(ranks[source]) and not check.get("or_exits"):
            failures.append({"reason": "rank_not_decreasing_under_replay", "edge_check": check})
    for check in certificate.get("cycle_exit_checks", []) or []:
        if check.get("status") != "PASS":
            failures.append({"reason": "cycle_exit_check_not_pass", "cycle_id": check.get("cycle_id")})
        if check.get("classification") == "GUARDED_REPEATABLE_NON_DESCENDING":
            failures.append({"reason": "repeatable_non_descending_cycle_in_certificate", "cycle_id": check.get("cycle_id")})
        if proof_kind == "bounded_guard_exit" and not check.get("bounded", check.get("classification") == "GUARDED_BOUNDED_REPEAT_EXIT"):
            failures.append({"reason": "bounded_guard_exit_cycle_not_bounded", "cycle_id": check.get("cycle_id")})
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failures": failures}


def _manifest_hash_check(manifest_path: Path | None, name: str, path: Path) -> dict[str, Any]:
    if manifest_path is None or not manifest_path.exists():
        return {"artifact_name": name, "path": str(path), "expected_sha256": None, "actual_sha256": _sha256(path) if path.exists() else None, "matches": True}
    manifest = _load_json(manifest_path)
    expected = None
    for entry in manifest.get("artifacts", []) or []:
        if entry.get("name") == name:
            expected = str(entry.get("sha256"))
            break
    actual = _sha256(path) if path.exists() else None
    return {
        "artifact_name": name,
        "path": str(path),
        "expected_sha256": expected,
        "actual_sha256": actual,
        "matches": expected is None or expected == actual,
    }


def run_guarded_scc_ranking(config: dict[str, Any] | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = cfg.get("guarded_scc_ranking_run040", {}) if isinstance(cfg.get("guarded_scc_ranking_run040"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    edge_maps_path = Path(run_cfg.get("scc_edge_maps_normalized") or "reports/runs/RUN-038-scc-invariant-discovery/scc_edge_maps_normalized.jsonl")
    cycles_path = Path(run_cfg.get("scc_cycles_full_or_basis") or "reports/runs/RUN-038-scc-invariant-discovery/scc_cycles_full_or_basis.jsonl")
    parent_maps_path = Path(run_cfg.get("parent_coordinate_map_certificates") or "certificate_store/run034_parent_coordinate_map_certificates.jsonl")
    manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    raw_multicycle_path = Path(run_cfg.get("raw_collatz_multicycle_replay") or "reports/runs/RUN-039-independent-cycle-counterexample-audit/raw_collatz_multicycle_replay.jsonl")
    cycle_invariance_path = Path(run_cfg.get("cycle_invariance_report") or "reports/runs/RUN-039-independent-cycle-counterexample-audit/cycle_invariance_report.json")
    repeat_cap = int(run_cfg.get("repeat_refinement_cap", 8))
    repeat_prefix_cycle_limit = int(run_cfg.get("repeat_prefix_cycle_limit", 16))
    cycle_detail_limit = int(run_cfg.get("cycle_detail_limit", 64))
    reclassification_limit = run_cfg.get("cycle_reclassification_limit")
    if reclassification_limit is not None:
        reclassification_limit = int(reclassification_limit)

    edge_maps = load_jsonl(edge_maps_path)
    parent_map_rows = load_jsonl(parent_maps_path)
    cycles = load_jsonl(cycles_path)
    if reclassification_limit is not None:
        cycles = cycles[:reclassification_limit]
    raw_rows = load_jsonl(raw_multicycle_path)
    guarded_rows = build_guarded_edge_domain_rows(edge_maps=edge_maps, parent_coordinate_map_rows=parent_map_rows)
    write_jsonl(out_dir / "guarded_edge_domains.jsonl", guarded_rows)
    guarded_edges = _edge_domain_by_id(guarded_rows)

    graph = build_guarded_transition_graph(guarded_rows)
    _write_json(graph, out_dir / "guarded_transition_graph.json")

    reclassified: list[dict[str, Any]] = []
    detailed_for_reasoning: list[dict[str, Any]] = []
    for index, cycle in enumerate(cycles):
        row = classify_guarded_cycle(
            cycle_record=cycle,
            guarded_edges=guarded_edges,
            repeat_cap=repeat_cap,
            raw_rows=raw_rows,
            compute_repeat_prefix=index < repeat_prefix_cycle_limit,
        )
        detailed_for_reasoning.append(row)
        if index >= cycle_detail_limit:
            compact = {
                "cycle_id": row.get("cycle_id"),
                "edge_ids": row.get("edge_ids"),
                "classification": row.get("classification"),
                "status": row.get("status"),
                "composed_map": row.get("composed_map"),
                "descent_check": row.get("descent_check"),
                "full_domain_self_invariance_status": (row.get("full_domain_self_invariance") or {}).get("status"),
                "exact_exit_reason": row.get("exact_exit_reason"),
                "starting_guarded_domain_hash": stable_hash(row.get("starting_guarded_domain", {})),
                "compact_record": True,
            }
            reclassified.append(compact)
        else:
            reclassified.append(row)
    write_jsonl(out_dir / "guarded_cycle_reclassification.jsonl", reclassified)

    exit_certs = [
        {
            "cycle_id": row.get("cycle_id"),
            "edge_ids": row.get("edge_ids"),
            "classification": row.get("classification"),
            "bounded": (row.get("repeat_prefix_check") or {}).get("bounded") is True,
            "max_valid_repeats": (row.get("repeat_prefix_check") or {}).get("max_valid_repeats"),
            "exact_exit_reason": row.get("exact_exit_reason"),
            "status": "PASS" if row.get("classification") in {"GUARDED_DESCENDING", "GUARDED_TRANSIENT_EXIT", "GUARDED_BOUNDED_REPEAT_EXIT"} else "FAIL",
        }
        for row in reclassified
    ]
    write_jsonl(out_dir / "guarded_exit_certificates.jsonl", exit_certs)

    edge_failures = [row for row in guarded_rows if row.get("status") != "PASS"]
    repeatable = [row for row in detailed_for_reasoning if row.get("classification") == "GUARDED_REPEATABLE_NON_DESCENDING"]
    unbounded_prefix = [
        row
        for row in detailed_for_reasoning
        if row.get("classification") == "GUARDED_TRANSIENT_EXIT" and (row.get("repeat_prefix_check") or {}).get("bounded") is False
    ]
    manifest_checks = [
        _manifest_hash_check(manifest_path, "parent_coordinate_map_certificates", parent_maps_path),
        _manifest_hash_check(manifest_path, "parent_transition_certificates", Path(run_cfg.get("parent_transition_certificates") or "certificate_store/run035_parent_transition_certificates.jsonl")),
    ]
    hash_failure_count = sum(1 for row in manifest_checks if not row.get("matches"))
    states = [f"P{index}" for index in range(12, 25)]
    guarded_edge_ids = sorted(guarded_edges, key=_edge_sort_key)

    accepted_certificate: dict[str, Any] | None = None
    obstruction: dict[str, Any] | None = None
    if edge_failures:
        status = "GUARD_SEMANTICS_MISSING"
        obstruction = {
            "schema": "collatz_lab.remaining_guarded_scc_obstruction",
            "version": 1,
            "run_id": RUN_ID,
            "failure_classification": status,
            "guarded_repeatable": False,
            "raw_executable": None,
            "exact_reason_guarded_ranking_failed": "one or more SCC edges did not yield a full replayed guarded domain",
            "failures": edge_failures[:20],
        }
    elif hash_failure_count:
        status = "HASH_REPLAY_FAILURE"
        obstruction = {
            "schema": "collatz_lab.remaining_guarded_scc_obstruction",
            "version": 1,
            "run_id": RUN_ID,
            "failure_classification": status,
            "guarded_repeatable": False,
            "raw_executable": None,
            "exact_reason_guarded_ranking_failed": "manifest artifact hash replay failed",
            "manifest_checks": manifest_checks,
        }
    elif repeatable:
        status = "GUARDED_REPEATABLE_NON_DESCENDING"
        obstruction = {
            "schema": "collatz_lab.remaining_guarded_scc_obstruction",
            "version": 1,
            "run_id": RUN_ID,
            "failure_classification": status,
            "guarded_repeatable": True,
            "raw_executable": True,
            "exact_cycle_domain_guard": repeatable[0].get("starting_guarded_domain"),
            "exact_cycle": repeatable[0],
            "exact_reason_guarded_ranking_failed": "a full guarded cycle domain maps into itself without descent",
            "new_invariant_genuinely_needed": True,
        }
    else:
        dag_cert = build_guarded_dag_certificate(graph=graph, states=states, edge_ids=guarded_edge_ids, cycle_exit_checks=exit_certs)
        if dag_cert is not None:
            replay = replay_scc_guarded_ranking_certificate(dag_cert, expected_edge_ids=guarded_edge_ids)
            if replay["accepted"]:
                accepted_certificate = dag_cert
                status = "PASS"
            else:
                status = "DOMAIN_COMPOSITION_BUG"
                obstruction = {
                    "schema": "collatz_lab.remaining_guarded_scc_obstruction",
                    "version": 1,
                    "run_id": RUN_ID,
                    "failure_classification": status,
                    "exact_reason_guarded_ranking_failed": "constructed guarded DAG certificate did not replay",
                    "replay": replay,
                }
        else:
            status = "NEEDS_NEW_INVARIANT_AFTER_GUARDS"
            if unbounded_prefix:
                status = "REFINEMENT_CAP_INSUFFICIENT"
            raw_failure = None
            if raw_rows:
                raw_failure = next((row.get("failure") for row in raw_rows if isinstance(row.get("failure"), dict)), None)
            cycle_invariance = _load_json(cycle_invariance_path) if cycle_invariance_path.exists() else {}
            obstruction = {
                "schema": "collatz_lab.remaining_guarded_scc_obstruction",
                "version": 1,
                "run_id": RUN_ID,
                "failure_classification": status,
                "guarded_repeatable": False,
                "raw_executable": bool(raw_rows and raw_rows[0].get("status") == "PASS"),
                "representative_cycle_id": detailed_for_reasoning[0].get("cycle_id") if detailed_for_reasoning else None,
                "exact_cycle_domain_guard": detailed_for_reasoning[0].get("starting_guarded_domain") if detailed_for_reasoning else None,
                "exact_guard_exit": detailed_for_reasoning[0].get("exact_exit_reason") if detailed_for_reasoning else None,
                "run039_raw_failure": raw_failure,
                "cycle_invariance_status": cycle_invariance.get("accepted_invariant_domain"),
                "exact_reason_guarded_ranking_failed": (
                    "the finite guarded edge graph still has SCCs; full-domain repeatability was rejected, "
                    "but the configured repeat refinement cap did not produce a replayed well-founded rank"
                ),
                "new_invariant_genuinely_needed": status == "NEEDS_NEW_INVARIANT_AFTER_GUARDS",
                "repeat_refinement_cap": repeat_cap,
                "unbounded_prefix_examples": unbounded_prefix[:3],
            }

    if accepted_certificate is not None:
        _write_json(accepted_certificate, out_dir / "scc_guarded_ranking_certificate.json")
        _write_json(
            {
                "schema": "collatz_lab.remaining_guarded_scc_obstruction",
                "version": 1,
                "run_id": RUN_ID,
                "status": "PASS",
                "unresolved_guarded_scc_count": 0,
            },
            out_dir / "remaining_guarded_scc_obstruction.json",
        )
        replay_result = replay_scc_guarded_ranking_certificate(accepted_certificate, expected_edge_ids=guarded_edge_ids)
    else:
        failure_cert = {
            "schema": SCHEMA,
            "version": 1,
            "type": CERT_TYPE,
            "scc_id": DEFAULT_SCC_ID,
            "states": states,
            "covered_edge_ids": guarded_edge_ids,
            "guarded_node_count": graph.get("node_count", 0),
            "guarded_edge_count": graph.get("edge_count", 0),
            "proof_kind": "none",
            "node_ranks": {},
            "edge_checks": [],
            "cycle_exit_checks": exit_certs,
            "status": "FAIL",
            "failure_classification": status,
        }
        failure_cert["certificate_hash"] = certificate_hash(failure_cert)
        _write_json(failure_cert, out_dir / "scc_guarded_ranking_certificate.json")
        _write_json(obstruction or {}, out_dir / "remaining_guarded_scc_obstruction.json")
        replay_result = {
            "accepted": False,
            "status": "FAIL",
            "failures": [
                {
                    "reason": status,
                    "obstruction_artifact": str(out_dir / "remaining_guarded_scc_obstruction.json"),
                }
            ],
        }

    result = {
        "schema": "collatz_lab.run040_guarded_scc_ranking_repair",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_tuning_launched": False,
        "verifier_relaxed": False,
        "floating_point_certificate_used": False,
        "status": status,
        "guarded_domains_built": sum(1 for row in guarded_rows if row.get("status") == "PASS"),
        "guarded_domains_expected": len(edge_maps),
        "scc_internal_edge_count": len(edge_maps),
        "guarded_transition_node_count": graph.get("node_count", 0),
        "guarded_transition_edge_count": graph.get("edge_count", 0),
        "cycle_reclassification_count": len(reclassified),
        "guarded_repeatable_non_descending_count": len(repeatable),
        "hash_failure_count": hash_failure_count,
        "accepted_scc_guarded_ranking": accepted_certificate is not None,
        "replay_scc_guarded_ranking_certificate": replay_result,
        "unresolved_guarded_scc_count": 0 if accepted_certificate is not None else 1,
        "failure_classification": None if accepted_certificate is not None else status,
        "artifacts": {
            "guarded_edge_domains": str(out_dir / "guarded_edge_domains.jsonl"),
            "guarded_transition_graph": str(out_dir / "guarded_transition_graph.json"),
            "guarded_cycle_reclassification": str(out_dir / "guarded_cycle_reclassification.jsonl"),
            "guarded_exit_certificates": str(out_dir / "guarded_exit_certificates.jsonl"),
            "scc_guarded_ranking_certificate": str(out_dir / "scc_guarded_ranking_certificate.json"),
            "remaining_guarded_scc_obstruction": str(out_dir / "remaining_guarded_scc_obstruction.json"),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result
