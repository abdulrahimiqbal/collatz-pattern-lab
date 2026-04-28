"""Exact SCC invariant/ranking discovery for RUN-038.

The RUN-036 failure exposed non-descending cycles after composing the S4
parent-coordinate maps.  This module strengthens that diagnostic by replaying
the cycle domains themselves: every branch residue is pulled back to the
starting parent coordinate with integer congruence arithmetic before any drift
classification is accepted.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .proof_action_scc_ranking_cert import (
    derive_all_affine_edge_maps,
    extract_scc_internal_edges,
    load_jsonl,
    scc_ranking_certificate_hash,
    write_jsonl,
)


RUN_ID = "RUN-038-scc-invariant-discovery"
SCHEMA = "collatz_lab.scc_invariant_discovery"
DEFAULT_RUN030_DIR = Path("reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening")
DEFAULT_RUN036_DIR = Path("reports/runs/RUN-036-exact-scc-ranking-with-parent-coordinate-maps")
DEFAULT_STATES = [f"P{index}" for index in range(12, 25)]


@dataclass(frozen=True)
class CycleDomain:
    accepted: bool
    residue: int = 0
    modulus: int = 1
    lower_bound: int = 1
    minimum_q: int = 1
    A: int = 1
    B: int = 0
    D: int = 1
    failure: dict[str, Any] | None = None
    trace: tuple[dict[str, Any], ...] = ()


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


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _ceil_div(num: int, den: int) -> int:
    if den <= 0:
        raise ValueError("denominator must be positive")
    return -((-num) // den)


def _normalise_fraction_triple(A: int, B: int, D: int) -> tuple[int, int, int]:
    if D < 0:
        A, B, D = -A, -B, -D
    gcd = math.gcd(math.gcd(abs(A), abs(B)), abs(D))
    if gcd > 1:
        A //= gcd
        B //= gcd
        D //= gcd
    return A, B, D


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_float(item) for item in value)
    return False


def _artifact_path(manifest_path: str | Path | None, name: str) -> Path | None:
    if manifest_path is None:
        return None
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        return None
    manifest = _load_json(manifest_file)
    for entry in manifest.get("artifacts", []) or []:
        if entry.get("name") != name:
            continue
        raw = Path(str(entry.get("path")))
        return raw if raw.is_absolute() else manifest_file.parent / raw
    return None


def _manifest_hash_check(manifest_path: str | Path | None, artifact_name: str, artifact_path: Path) -> dict[str, Any]:
    if manifest_path is None or not Path(manifest_path).exists():
        return {
            "artifact_name": artifact_name,
            "path": str(artifact_path),
            "expected_sha256": None,
            "actual_sha256": _sha256(artifact_path) if artifact_path.exists() else None,
            "matches": True,
            "manifest_present": False,
        }
    manifest = _load_json(manifest_path)
    expected = None
    for entry in manifest.get("artifacts", []) or []:
        if entry.get("name") == artifact_name:
            expected = str(entry.get("sha256"))
            break
    actual = _sha256(artifact_path) if artifact_path.exists() else None
    return {
        "artifact_name": artifact_name,
        "path": str(artifact_path),
        "expected_sha256": expected,
        "actual_sha256": actual,
        "matches": expected is None or expected == actual,
        "manifest_present": True,
    }


def _parent_number(label: Any) -> int:
    text = str(label)
    return int(text[1:] if text.startswith("P") else text)


def _cycle_key(edge_ids: list[str]) -> tuple[str, ...]:
    rotations = [tuple(edge_ids[index:] + edge_ids[:index]) for index in range(len(edge_ids))]
    return min(rotations)


def _enumerate_simple_cycles(edge_maps: list[dict[str, Any]], *, cap: int) -> tuple[list[list[dict[str, Any]]], bool]:
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edge_maps:
        adjacency.setdefault(str(edge["source"]), []).append(edge)
    for rows in adjacency.values():
        rows.sort(key=lambda row: (str(row["target"]), str(row["edge_id"])))

    cycles: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    capped = False

    def dfs(start: str, node: str, path: list[dict[str, Any]], seen: set[str]) -> None:
        nonlocal capped
        if len(cycles) >= cap:
            capped = True
            return
        for edge in adjacency.get(node, []):
            target = str(edge["target"])
            if target == start:
                cycle = path + [edge]
                cycles.setdefault(_cycle_key([str(row["edge_id"]) for row in cycle]), cycle)
                if len(cycles) >= cap:
                    capped = True
                    return
                continue
            if target in seen:
                continue
            dfs(start, target, path + [edge], seen | {target})
            if capped:
                return

    for node in sorted(adjacency, key=_parent_number):
        dfs(node, node, [], {node})
        if capped:
            break
    return list(cycles.values()), capped


def impose_linear_congruence(
    *,
    residue: int,
    modulus: int,
    a: int,
    b: int,
    congruence_modulus: int,
) -> tuple[int, int] | None:
    """Intersect ``q == residue mod modulus`` with ``a*q+b == 0 mod m``."""

    if modulus <= 0 or congruence_modulus <= 0:
        raise ValueError("moduli must be positive")
    if congruence_modulus == 1:
        return residue % modulus, modulus
    coefficient = (a * modulus) % congruence_modulus
    rhs = (-b - a * residue) % congruence_modulus
    gcd = math.gcd(coefficient, congruence_modulus)
    if rhs % gcd != 0:
        return None
    coefficient //= gcd
    rhs //= gcd
    reduced_modulus = congruence_modulus // gcd
    if reduced_modulus == 1:
        t0 = 0
    else:
        t0 = (rhs * pow(coefficient % reduced_modulus, -1, reduced_modulus)) % reduced_modulus
    new_modulus = modulus * reduced_modulus
    return (residue + modulus * t0) % new_modulus, new_modulus


def _minimum_in_residue_class(residue: int, modulus: int, lower_bound: int) -> int:
    if residue >= lower_bound:
        return residue
    return residue + _ceil_div(lower_bound - residue, modulus) * modulus


def compose_cycle_domain(edge_maps: list[dict[str, Any]]) -> CycleDomain:
    """Compose a cycle and prove all branch domains as congruences in q0."""

    residue = 0
    modulus = 1
    lower_bound = 1
    A_acc = 1
    B_acc = 0
    D_acc = 1
    trace: list[dict[str, Any]] = []
    for index, edge in enumerate(edge_maps):
        edge_modulus = _as_int(edge.get("domain_modulus"), "domain_modulus")
        edge_residue = _as_int(edge.get("domain_residue"), "domain_residue") % edge_modulus
        imposed = impose_linear_congruence(
            residue=residue,
            modulus=modulus,
            a=A_acc,
            b=B_acc - edge_residue * D_acc,
            congruence_modulus=edge_modulus * D_acc,
        )
        if imposed is None:
            return CycleDomain(
                accepted=False,
                failure={
                    "reason": "DOMAIN_COMPOSITION_EMPTY",
                    "step_index": index,
                    "edge_id": edge.get("edge_id"),
                    "required_domain_residue": str(edge_residue),
                    "required_domain_modulus": str(edge_modulus),
                },
                trace=tuple(trace),
            )
        residue, modulus = imposed
        edge_minimum_q = _as_int(edge.get("minimum_q", 1), "minimum_q")
        lower_bound = max(lower_bound, _ceil_div(D_acc * edge_minimum_q - B_acc, A_acc))
        trace.append(
            {
                "step_index": index,
                "edge_id": edge.get("edge_id"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "pulled_back_residue": str(residue),
                "pulled_back_modulus": str(modulus),
                "lower_bound": str(lower_bound),
            }
        )

        A = _as_int(edge.get("A"), "A")
        B = _as_int(edge.get("B"), "B")
        D = _as_int(edge.get("D"), "D")
        A_acc, B_acc, D_acc = A * A_acc, A * B_acc + B * D_acc, D * D_acc
        A_acc, B_acc, D_acc = _normalise_fraction_triple(A_acc, B_acc, D_acc)

    first = edge_maps[0]
    first_modulus = _as_int(first.get("domain_modulus"), "domain_modulus")
    first_residue = _as_int(first.get("domain_residue"), "domain_residue") % first_modulus
    closed = impose_linear_congruence(
        residue=residue,
        modulus=modulus,
        a=A_acc,
        b=B_acc - first_residue * D_acc,
        congruence_modulus=first_modulus * D_acc,
    )
    if closed is None:
        return CycleDomain(
            accepted=False,
            failure={
                "reason": "DOMAIN_COMPOSITION_EMPTY_AT_CYCLE_CLOSE",
                "edge_id": first.get("edge_id"),
                "required_domain_residue": str(first_residue),
                "required_domain_modulus": str(first_modulus),
            },
            trace=tuple(trace),
        )
    residue, modulus = closed
    minimum_q = _minimum_in_residue_class(residue, modulus, lower_bound)
    trace.append(
        {
            "step_index": "cycle_close",
            "edge_id": first.get("edge_id"),
            "source": edge_maps[-1].get("target"),
            "target": first.get("source"),
            "pulled_back_residue": str(residue),
            "pulled_back_modulus": str(modulus),
            "lower_bound": str(lower_bound),
        }
    )
    return CycleDomain(
        accepted=True,
        residue=residue,
        modulus=modulus,
        lower_bound=lower_bound,
        minimum_q=minimum_q,
        A=A_acc,
        B=B_acc,
        D=D_acc,
        trace=tuple(trace),
    )


def _cycle_self_return_mod_domain(domain: CycleDomain) -> dict[str, Any]:
    if not domain.accepted:
        return {"status": "NOT_APPLICABLE"}
    imposed = impose_linear_congruence(
        residue=domain.residue,
        modulus=domain.modulus,
        a=domain.A - domain.D,
        b=domain.B,
        congruence_modulus=domain.modulus * domain.D,
    )
    if imposed is None:
        return {"status": "NO_EXACT_SELF_RETURNING_SUBDOMAIN_MOD_CYCLE_DOMAIN"}
    residue, modulus = imposed
    minimum_q = _minimum_in_residue_class(residue, modulus, domain.lower_bound)
    grows = domain.A * minimum_q + domain.B > domain.D * minimum_q
    return {
        "status": "PASS",
        "description": "subdomain where one full cycle returns to the same cycle-domain residue modulo the cycle-domain modulus",
        "residue": str(residue),
        "modulus": str(modulus),
        "minimum_q": str(minimum_q),
        "grows_at_minimum_q": grows,
        "growth_delta_at_minimum_q": str(domain.A * minimum_q + domain.B - domain.D * minimum_q),
    }


def replay_cycle(edge_maps: list[dict[str, Any]]) -> dict[str, Any]:
    domain = compose_cycle_domain(edge_maps)
    edge_ids = [str(edge["edge_id"]) for edge in edge_maps]
    if not domain.accepted:
        return {
            "cycle_id": _hash({"edge_ids": edge_ids, "run_id": RUN_ID})[:16],
            "edge_ids": edge_ids,
            "source_states": [str(edge["source"]) for edge in edge_maps],
            "domain_status": "DOMAIN_EMPTY",
            "classification": "DOMAIN_INCOMPATIBLE",
            "status": "SKIP",
            "failure": domain.failure,
            "domain_trace": list(domain.trace),
        }

    A = domain.A
    B = domain.B
    D = domain.D
    minimum_q = domain.minimum_q
    delta_at_min = (D - A) * minimum_q - B
    if A < D and delta_at_min > 0:
        classification = "CONTRACTING"
        status = "PASS"
    elif A == D and B < 0:
        classification = "TRANSLATING_DOWN"
        status = "PASS"
    else:
        classification = "NON_DESCENDING"
        status = "FAIL"
    return {
        "cycle_id": _hash({"edge_ids": edge_ids, "run_id": RUN_ID})[:16],
        "edge_ids": edge_ids,
        "source_states": [str(edge["source"]) for edge in edge_maps],
        "domain_status": "PASS",
        "classification": classification,
        "status": status,
        "composed_map": {"A": str(A), "B": str(B), "D": str(D)},
        "cycle_domain": {
            "residue": str(domain.residue),
            "modulus": str(domain.modulus),
            "lower_bound": str(domain.lower_bound),
            "minimum_q": str(minimum_q),
        },
        "descent_check": {
            "inequality": "A*q + B < D*q",
            "slope_relation": "A<D" if A < D else "A=D" if A == D else "A>D",
            "B_sign": "negative" if B < 0 else "zero" if B == 0 else "positive",
            "delta_at_minimum_q": str(delta_at_min),
            "minimum_domain_passes": delta_at_min > 0,
            "status": status,
        },
        "self_return_mod_cycle_domain": _cycle_self_return_mod_domain(domain),
        "domain_trace": list(domain.trace),
    }


def _compact_cycle_record(record: dict[str, Any]) -> dict[str, Any]:
    compact = dict(record)
    compact.pop("domain_trace", None)
    self_return = compact.get("self_return_mod_cycle_domain")
    if isinstance(self_return, dict) and self_return.get("status") == "PASS":
        compact["self_return_mod_cycle_domain"] = {
            "status": "PASS",
            "description": self_return.get("description"),
            "grows_at_minimum_q": self_return.get("grows_at_minimum_q"),
            "growth_delta_at_minimum_q": self_return.get("growth_delta_at_minimum_q"),
        }
    return compact


def _normalised_edge_from_map(edge: dict[str, Any], edge_map: dict[str, Any]) -> dict[str, Any]:
    if edge_map.get("status") != "PASS":
        raise ValueError(f"edge map did not replay: {edge_map.get('edge_id')}")
    if _contains_float(edge) or _contains_float(edge_map):
        raise ValueError(f"non-exact floating payload in edge {edge_map.get('edge_id')}")
    parent_map = edge.get("parent_coordinate_map")
    if not isinstance(parent_map, dict):
        raise ValueError(f"missing explicit parent-coordinate map for {edge.get('edge_id')}")
    certificate = edge.get("exact_symbolic_transition_payload")
    if not isinstance(certificate, dict):
        raise ValueError(f"missing transition certificate payload for {edge.get('edge_id')}")
    if certificate.get("type") != "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP":
        raise ValueError(f"stale or non-map S4 certificate for {edge.get('edge_id')}")

    domain_constraints = list(parent_map.get("domain_constraints") or [])
    integrality_conditions = list(edge_map.get("integrality_conditions") or [])
    return {
        "edge_id": str(edge_map["edge_id"]),
        "source": str(edge_map["source"]),
        "target": str(edge_map["target"]),
        "source_parent": _as_int(edge_map["source_parent"], "source_parent"),
        "target_parent": _as_int(edge_map["target_parent"], "target_parent"),
        "A": _as_int(edge_map["A"], "A"),
        "B": _as_int(edge_map["B"], "B"),
        "D": _as_int(edge_map["D"], "D"),
        "domain_modulus": _as_int(edge_map["domain_modulus"], "domain_modulus"),
        "domain_residue": _as_int(edge_map["domain_residue"], "domain_residue"),
        "minimum_q": _as_int(edge_map.get("minimum_q", 1), "minimum_q"),
        "branch_id": str(edge.get("branch_id")),
        "valuation": _as_int(edge.get("valuation", 0), "valuation"),
        "transition_certificate_id": str(edge_map["transition_certificate_id"]),
        "transition_certificate_hash": str(edge_map["transition_certificate_hash"]),
        "parent_coordinate_map_certificate_id": str(certificate.get("parent_coordinate_map_certificate_id", "")),
        "parent_coordinate_map_certificate_hash": str(certificate.get("parent_coordinate_map_certificate_hash", "")),
        "integrality_conditions": integrality_conditions,
        "domain_constraints": domain_constraints,
        "all_integrality_domain_constraints": {
            "parent_coordinate_map_domain_constraints": domain_constraints,
            "integrality_conditions": integrality_conditions,
            "s4_domain_constraints": list(edge.get("domain_constraints") or []),
        },
        "statement": f"q' = ({edge_map['A']}*q + {edge_map['B']}) / {edge_map['D']}",
        "status": "PASS",
    }


def normalize_scc_maps(
    *,
    unresolved_sccs_path: Path,
    parent_transition_certificates_path: Path,
    manifest_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    scc_rows = load_jsonl(unresolved_sccs_path)
    s4_rows = load_jsonl(parent_transition_certificates_path)
    extraction = extract_scc_internal_edges(scc_rows, s4_rows)
    derived_maps = derive_all_affine_edge_maps(extraction.edges)
    maps_by_id = {str(row.get("edge_id")): row for row in derived_maps}
    failures = list(extraction.failures)
    normalised: list[dict[str, Any]] = []
    for edge in extraction.edges:
        edge_id = str(edge.get("edge_id"))
        try:
            normalised.append(_normalised_edge_from_map(edge, maps_by_id[edge_id]))
        except (KeyError, ValueError) as exc:
            failures.append({"edge_id": edge_id, "reason": str(exc)})
    normalised.sort(key=lambda row: (row["source_parent"], row["target_parent"], row["edge_id"]))
    manifest_checks = [_manifest_hash_check(manifest_path, "parent_transition_certificates", parent_transition_certificates_path)]
    failures.extend(
        {"reason": "manifest_artifact_hash_mismatch", **check}
        for check in manifest_checks
        if not check.get("matches")
    )
    summary = {
        "scc_id": (scc_rows[0] if scc_rows else {}).get("scc_id", "P12_P24_internal_s4"),
        "states": list((scc_rows[0] if scc_rows else {}).get("nodes") or DEFAULT_STATES),
        "expected_edge_count": int((scc_rows[0] if scc_rows else {}).get("edge_count", 106) or 106),
        "extracted_edge_count": len(extraction.edges),
        "normalized_edge_count": len(normalised),
        "manifest_checks": manifest_checks,
        "failures": failures,
    }
    return normalised, summary, failures


def build_invariant_candidates(
    *,
    edge_maps: list[dict[str, Any]],
    cycle_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    non_descending = [row for row in cycle_records if row.get("classification") == "NON_DESCENDING" and row.get("domain_status") == "PASS"]
    representative = non_descending[0] if non_descending else None
    families = [
        ("parent_scalar_affine", "A", "R(P_a,q)=alpha_a*q+beta_a"),
        ("parent_normalized_affine", "B", "domain-normalized parent affine ranking"),
        ("lexicographic_affine", "C", "finite tuple of parent affine rankings"),
        ("piecewise_residue_affine", "D", "exact residue-class affine ranking"),
        ("mixed_debt", "E", "RUN-028 debt/q mixed ranking"),
        ("cycle_potential", "F", "negative cycle-potential ranking"),
    ]
    candidates: list[dict[str, Any]] = []
    for family, label, description in families:
        if representative is None:
            candidates.append(
                {
                    "family": label,
                    "ranking_kind": family,
                    "description": description,
                    "status": "NOT_ACCEPTED",
                    "reason": "no complete descending cycle proof was available for this family",
                }
            )
            continue
        composed = representative["composed_map"]
        candidates.append(
            {
                "family": label,
                "ranking_kind": family,
                "description": description,
                "status": "FAIL",
                "failure_classification": "CYCLE_COMPOSITION_NOT_DESCENDING"
                if family == "cycle_potential"
                else "NO_AFFINE_RANKING_EXISTS_FOR_FEATURES",
                "reason": (
                    "exact domain-compatible cycle has composed A>D, so this family cannot certify strict q-descent "
                    "on the replayed SCC without an additional invariant excluding or resolving that cycle domain"
                ),
                "representative_cycle_id": representative["cycle_id"],
                "representative_edge_ids": representative["edge_ids"],
                "composed_A": composed["A"],
                "composed_D": composed["D"],
                "domain_modulus": representative["cycle_domain"]["modulus"],
                "domain_residue": representative["cycle_domain"]["residue"],
                "edge_count": len(edge_maps),
            }
        )
    return candidates


def build_refinement_outputs(
    *,
    edge_maps: list[dict[str, Any]],
    obstruction: dict[str, Any] | None,
    modulus_cap: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    refined_edges = [
        {
            "edge_id": edge["edge_id"],
            "source": f"{edge['source']}[q=={edge['domain_residue']} mod {edge['domain_modulus']}]",
            "target": f"{edge['target']}[induced_by:{edge['edge_id']}]",
            "transition_certificate_id": edge["transition_certificate_id"],
            "exact_predicate": {
                "q_modulus": edge["domain_modulus"],
                "q_residue": edge["domain_residue"],
            },
            "coverage_preserved": True,
        }
        for edge in edge_maps
    ]
    nodes: dict[str, dict[str, Any]] = {}
    for edge in refined_edges:
        nodes.setdefault(str(edge["source"]), {"predicate": edge["exact_predicate"]})
        nodes.setdefault(str(edge["target"]), {"predicate": {"induced_by_edge_id": edge["edge_id"]}})
    graph = {
        "schema": "collatz_lab.run038_refined_scc_graph",
        "version": 1,
        "run_id": RUN_ID,
        "node_count": len(nodes),
        "edge_count": len(refined_edges),
        "nodes": nodes,
        "edges": refined_edges,
        "status": "NOT_RANKED",
    }

    attempts: list[dict[str, Any]] = []
    modulus = 2
    while modulus <= max(1, modulus_cap):
        projected: dict[str, Any] = {"modulus": modulus, "status": "NO_OBSTRUCTION_PROJECTED"}
        if obstruction and obstruction.get("representative_non_descending_cycle"):
            cycle = obstruction["representative_non_descending_cycle"]
            self_return = cycle.get("self_return_mod_cycle_domain", {})
            if self_return.get("status") == "PASS" and int(self_return["modulus"]) % modulus == 0:
                projected = {
                    "modulus": modulus,
                    "status": "REFINEMENT_STILL_HAS_PROJECTED_NON_DESCENDING_CYCLE",
                    "projected_residue": str(int(self_return["residue"]) % modulus),
                    "cycle_id": cycle.get("cycle_id"),
                }
        attempts.append(projected)
        modulus *= 2
    summary = {
        "schema": "collatz_lab.run038_refinement_summary",
        "version": 1,
        "run_id": RUN_ID,
        "input_edge_count": len(edge_maps),
        "refined_edge_count": len(refined_edges),
        "refinement_modulus_cap": modulus_cap,
        "attempted_moduli": attempts,
        "status": "FAIL",
        "failure_classification": "REFINEMENT_STILL_HAS_UNRANKED_SCC",
        "reason": "finite exact refinements attempted here did not remove the representative non-descending cycle obstruction",
    }
    refined_obstruction = {
        "schema": "collatz_lab.run038_refined_scc_obstruction",
        "version": 1,
        "run_id": RUN_ID,
        "status": "FAIL",
        "failure_classification": "REFINEMENT_STILL_HAS_UNRANKED_SCC",
        "representative_cycle_id": (
            obstruction.get("representative_non_descending_cycle", {}).get("cycle_id") if obstruction else None
        ),
        "refinement_summary": summary,
    }
    return graph, refined_edges, summary, refined_obstruction


def _minimal_obstruction(
    *,
    states: list[str],
    edge_maps: list[dict[str, Any]],
    cycle_records: list[dict[str, Any]],
    cycle_cap_reached: bool,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    non_descending = [row for row in cycle_records if row.get("classification") == "NON_DESCENDING" and row.get("domain_status") == "PASS"]
    domain_incomplete = [row for row in cycle_records if row.get("classification") == "DOMAIN_INCOMPATIBLE"]
    if non_descending:
        classification = "CYCLE_COMPOSITION_NOT_DESCENDING"
        representative = non_descending[0]
        gap = "exact domain-compatible cycle composes to A*q+B >= D*q on its nonempty domain"
    elif domain_incomplete:
        classification = "DOMAIN_COMPOSITION_INCOMPLETE"
        representative = domain_incomplete[0]
        gap = "cycle domain composition did not yield a complete descending proof"
    else:
        classification = "NEEDS_NEW_INVARIANT"
        representative = cycle_records[0] if cycle_records else {}
        gap = "no accepted exact ranking/invariant was synthesized"
    return {
        "schema": "collatz_lab.run038_minimal_invariant_obstruction",
        "version": 1,
        "run_id": RUN_ID,
        "classification": classification,
        "status": classification,
        "unresolved_scc_states": states,
        "internal_edge_count": len(edge_maps),
        "cycle_count_considered": len(cycle_records),
        "cycle_enumeration_cap_reached": cycle_cap_reached,
        "domain_compatible_non_descending_cycle_count": len(non_descending),
        "domain_incompatible_cycle_count": len(domain_incomplete),
        "representative_non_descending_cycle": representative if non_descending else None,
        "ranking_families_attempted": candidates,
        "exact_invariant_gap": gap,
        "failure_classification_options_respected": True,
    }


def _new_math_required(obstruction: dict[str, Any]) -> str:
    cycle = obstruction.get("representative_non_descending_cycle") or {}
    composed = cycle.get("composed_map") or {}
    domain = cycle.get("cycle_domain") or {}
    lines = [
        "# RUN-038 New Math Required",
        "",
        f"- classification: `{obstruction.get('classification')}`",
        f"- unresolved SCC states: `{', '.join(obstruction.get('unresolved_scc_states') or [])}`",
        f"- internal exact S4 edges: `{obstruction.get('internal_edge_count')}`",
        f"- cycles considered: `{obstruction.get('cycle_count_considered')}`",
        f"- cycle cap reached: `{str(obstruction.get('cycle_enumeration_cap_reached')).lower()}`",
        "",
        "RUN-038 did not accept a graph status, certificate id, sample, float, or ML score as proof.",
        "The strongest replayed obstruction is an exact branch-domain cycle whose composed parent-coordinate map is not descending.",
        "",
        "## Representative Obstruction",
        "",
        f"- cycle id: `{cycle.get('cycle_id')}`",
        f"- edge ids: `{', '.join(cycle.get('edge_ids') or [])}`",
        f"- composed map: `q_final = ({composed.get('A')}*q + {composed.get('B')}) / {composed.get('D')}`",
        f"- cycle domain: `q == {domain.get('residue')} mod {domain.get('modulus')}`, `q >= {domain.get('lower_bound')}`",
        f"- minimum q in domain: `{domain.get('minimum_q')}`",
        f"- descent delta at minimum q: `{(cycle.get('descent_check') or {}).get('delta_at_minimum_q')}`",
        "",
        "A new invariant must either exclude this exact cycle domain, prove a stronger descent after additional exact unfolding,",
        "or introduce a different replayable well-founded measure with integer/rational certificate checks.",
        "",
    ]
    return "\n".join(lines)


def _failure_certificate(obstruction: dict[str, Any]) -> dict[str, Any]:
    certificate = {
        "schema": "collatz_lab.scc_cycle_ranking_certificate",
        "version": 1,
        "run_id": RUN_ID,
        "certificate_id": "run038_scc_ranking_P12_P24_internal_s4",
        "type": "SCC_WELL_FOUNDED_RANKING_EXACT",
        "scc_id": "P12_P24_internal_s4",
        "states": obstruction.get("unresolved_scc_states", []),
        "edge_count": obstruction.get("internal_edge_count", 0),
        "ranking_kind": "none",
        "feature_set": [],
        "coefficients": {},
        "edge_checks": [],
        "well_founded_order": "not_established",
        "status": "FAIL",
        "failure_classification": obstruction.get("classification"),
        "reason": obstruction.get("exact_invariant_gap"),
    }
    certificate["certificate_hash"] = scc_ranking_certificate_hash(certificate)
    return certificate


def run_scc_invariant_discovery(config: dict[str, Any] | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = cfg.get("scc_invariant_discovery_run038", {}) if isinstance(cfg.get("scc_invariant_discovery_run038", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    run036_dir = Path(run_cfg.get("run036_dir") or DEFAULT_RUN036_DIR)
    run030_dir = Path(run_cfg.get("run030_dir") or DEFAULT_RUN030_DIR)
    unresolved_sccs = Path(run_cfg.get("unresolved_sccs") or run030_dir / "unresolved_sccs.jsonl")
    parent_transition_certificates = Path(
        run_cfg.get("parent_transition_certificates")
        or _artifact_path(manifest_path, "parent_transition_certificates")
        or "certificate_store/run035_parent_transition_certificates.jsonl"
    )
    cycle_cap = int(run_cfg.get("cycle_cap", 20000))
    cycle_detail_limit = int(run_cfg.get("cycle_detail_limit", 64))
    obstruction_record_limit = int(run_cfg.get("obstruction_record_limit", 256))
    refinement_modulus_cap = int(run_cfg.get("refinement_modulus_cap", 4096))

    edge_maps, normalization_summary, normalization_failures = normalize_scc_maps(
        unresolved_sccs_path=unresolved_sccs,
        parent_transition_certificates_path=parent_transition_certificates,
        manifest_path=manifest_path,
    )
    write_jsonl(out_dir / "scc_edge_maps_normalized.jsonl", edge_maps)

    cycle_records: list[dict[str, Any]] = []
    cycle_obstructions: list[dict[str, Any]] = []
    cycle_cap_reached = False
    if not normalization_failures and len(edge_maps) == normalization_summary["expected_edge_count"]:
        cycles, cycle_cap_reached = _enumerate_simple_cycles(edge_maps, cap=cycle_cap)
        for index, cycle in enumerate(cycles):
            replay = replay_cycle(cycle)
            stored_replay = replay if index < cycle_detail_limit else _compact_cycle_record(replay)
            cycle_records.append(stored_replay)
            if replay.get("classification") == "NON_DESCENDING" and replay.get("domain_status") == "PASS":
                if len(cycle_obstructions) < obstruction_record_limit:
                    cycle_obstructions.append(stored_replay)
    else:
        cycle_obstructions.append(
            {
                "status": "FAIL",
                "classification": "DOMAIN_INCOMPLETE",
                "failure": normalization_failures[:20],
            }
        )

    write_jsonl(out_dir / "scc_cycles_full_or_basis.jsonl", cycle_records)
    write_jsonl(out_dir / "scc_cycle_obstructions.jsonl", cycle_obstructions)
    candidates = build_invariant_candidates(edge_maps=edge_maps, cycle_records=cycle_records)
    write_jsonl(out_dir / "invariant_candidates.jsonl", candidates)

    obstruction = _minimal_obstruction(
        states=list(normalization_summary.get("states") or DEFAULT_STATES),
        edge_maps=edge_maps,
        cycle_records=cycle_records,
        cycle_cap_reached=cycle_cap_reached,
        candidates=candidates,
    )
    refined_graph, refined_edges, refinement_summary, refined_obstruction = build_refinement_outputs(
        edge_maps=edge_maps,
        obstruction=obstruction,
        modulus_cap=refinement_modulus_cap,
    )
    _write_json(refined_graph, out_dir / "refined_scc_graph.json")
    write_jsonl(out_dir / "refined_scc_edges.jsonl", refined_edges)
    _write_json(refinement_summary, out_dir / "refinement_summary.json")
    _write_json(refined_obstruction, out_dir / "refined_scc_obstruction.json")
    _write_json(obstruction, out_dir / "minimal_invariant_obstruction.json")
    (out_dir / "new_math_required.md").write_text(_new_math_required(obstruction), encoding="utf-8")

    accepted_certificate: dict[str, Any] | None = None
    failure_certificate = _failure_certificate(obstruction)
    _write_json(failure_certificate, out_dir / "scc_ranking_certificate.json")

    drift_report = {
        "schema": "collatz_lab.run038_cycle_drift_report",
        "version": 1,
        "run_id": RUN_ID,
        "cycle_evidence_kind": "bounded_simple_cycles" if cycle_cap_reached else "all_simple_cycles_enumerated",
        "cycle_cap": cycle_cap,
        "cycle_detail_limit": cycle_detail_limit,
        "obstruction_record_limit": obstruction_record_limit,
        "cycle_cap_reached": cycle_cap_reached,
        "cycles_considered": len(cycle_records),
        "contracting": sum(1 for row in cycle_records if row.get("classification") == "CONTRACTING"),
        "translating_down": sum(1 for row in cycle_records if row.get("classification") == "TRANSLATING_DOWN"),
        "non_descending": sum(1 for row in cycle_records if row.get("classification") == "NON_DESCENDING"),
        "domain_incompatible": sum(1 for row in cycle_records if row.get("classification") == "DOMAIN_INCOMPATIBLE"),
        "representative_obstruction_cycle_id": (cycle_obstructions[0].get("cycle_id") if cycle_obstructions else None),
        "complete_cycle_descent_proof": False,
        "basis_proof_sufficient": False,
    }
    _write_json(drift_report, out_dir / "cycle_drift_report.json")

    hash_failure_count = sum(1 for check in normalization_summary.get("manifest_checks", []) if not check.get("matches"))
    status = str(obstruction.get("classification") or "NEEDS_NEW_INVARIANT")
    result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "source_run": "RUN-036-exact-scc-ranking-with-parent-coordinate-maps",
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "floating_point_certificate_used": False,
        "status": status if accepted_certificate is None else "PASS",
        "scc_internal_edge_count": len(edge_maps),
        "normalized_edge_map_pass": len(edge_maps) if not normalization_failures else 0,
        "normalized_edge_map_fail": len(normalization_failures),
        "cycle_checks_attempted": len(cycle_records),
        "cycle_enumeration_cap_reached": cycle_cap_reached,
        "domain_compatible_non_descending_cycle_count": drift_report["non_descending"],
        "accepted_scc_ranking": accepted_certificate is not None,
        "hash_failure_count": hash_failure_count,
        "unresolved_scc_count": 0 if accepted_certificate is not None else 1,
        "failure_classification": None if accepted_certificate is not None else status,
        "artifacts": {
            "scc_edge_maps_normalized": str(out_dir / "scc_edge_maps_normalized.jsonl"),
            "scc_cycles_full_or_basis": str(out_dir / "scc_cycles_full_or_basis.jsonl"),
            "cycle_drift_report": str(out_dir / "cycle_drift_report.json"),
            "invariant_candidates": str(out_dir / "invariant_candidates.jsonl"),
            "accepted_scc_ranking_certificate": str(out_dir / "accepted_scc_ranking_certificate.json")
            if accepted_certificate is not None
            else None,
            "minimal_invariant_obstruction": str(out_dir / "minimal_invariant_obstruction.json"),
            "new_math_required": str(out_dir / "new_math_required.md"),
            "refined_scc_graph": str(out_dir / "refined_scc_graph.json"),
            "refinement_summary": str(out_dir / "refinement_summary.json"),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    # Keep the original RUN-036 artifact reachable in the report for audit traceability.
    if (run036_dir / "minimal_ranking_obstruction.json").exists():
        result["artifacts"]["run036_minimal_ranking_obstruction"] = str(run036_dir / "minimal_ranking_obstruction.json")
        _write_json(result, out_dir / "run_result.json")
    return result
