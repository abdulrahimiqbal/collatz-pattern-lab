"""RUN-044 exact guarded viability-kernel elimination.

RUN-044 treats the P12--P24 internal SCC as a symbolic transition system over
parent coordinates.  The state predicates are exact residue cylinders with
integer lower bounds; transitions are exact affine q-maps

    q' = (A*q + B) / D.

The pass computes the greatest fixed point of the guarded internal transition
relation by partition refinement and elimination.  When a nonempty symbolic
kernel is found, the artifact includes a replayed lasso witness.  A 2-adic
witness is recorded separately from a raw natural-number Collatz witness.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .proof_action_guarded_domain import (
    AffineMap,
    GuardedDomain,
    ResidueClass,
    add_non_congruence,
    affine_from_json,
    ceil_div,
    congruence_implies,
    contains_float,
    domain_from_json,
    intersect_congruence,
    load_jsonl,
    pullback_domain,
    stable_hash,
    write_jsonl,
)
from .proof_action_guarded_scc_ranking import (
    CERT_TYPE as RANKING_CERT_TYPE,
    DEFAULT_SCC_ID,
    SCHEMA as RANKING_SCHEMA,
    certificate_hash as ranking_certificate_hash,
    compose_guarded_sequence,
)


RUN_ID = "RUN-044-guarded-viability-kernel-elimination"
SCHEMA = "collatz_lab.guarded_viability_kernel"
EMPTY_KERNEL_CERT_TYPE = "SCC_GUARDED_EMPTY_VIABILITY_KERNEL_CERTIFICATE"
NONEMPTY_KERNEL_TYPE = "NONEMPTY_GUARDED_VIABILITY_KERNEL"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _short_hash(data: Any, size: int = 16) -> str:
    return _hash(data)[:size]


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


def _edge_sort_key(edge_id: str) -> tuple[str, str]:
    return (edge_id.split(":", 1)[0], edge_id)


def _fraction_to_json(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _fraction_mod_power_two(value: Fraction, modulus: int) -> int | None:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    denominator = value.denominator % modulus
    if denominator % 2 == 0:
        return None
    return (value.numerator * pow(denominator, -1, modulus)) % modulus


def _fraction_is_natural(value: Fraction, *, lower_bound: int) -> bool:
    return value.denominator == 1 and value.numerator >= lower_bound


def _is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def _compatible(left: ResidueClass, right: ResidueClass) -> bool:
    return (left.residue - right.residue) % math.gcd(left.modulus, right.modulus) == 0


def _lcm(left: int, right: int) -> int:
    return left // math.gcd(left, right) * right


def fixed_point_for_cycle_map(cycle_map: AffineMap) -> Fraction | None:
    if cycle_map.D == cycle_map.A:
        return None
    return Fraction(cycle_map.B, cycle_map.D - cycle_map.A)


def exact_domain_intersection(left: GuardedDomain, right: GuardedDomain) -> GuardedDomain | None:
    """Intersect two guarded domains exactly.

    The representation is a single congruence cylinder minus finitely many
    congruence cylinders.  This is closed under intersection with another
    domain of the same shape.
    """

    updated = intersect_congruence(left, right.congruence)
    if updated is None:
        return None
    for excluded in right.non_congruences:
        updated = add_non_congruence(updated, excluded)
        if updated is None:
            return None
    return GuardedDomain(
        updated.congruence,
        updated.non_congruences,
        max(left.lower_bound, right.lower_bound),
        updated.guards
        + (
            {
                "kind": "domain_intersection",
                "left_hash": stable_hash(left.to_json()),
                "right_hash": stable_hash(right.to_json()),
            },
        ),
    )


def exact_domain_preimage(source_domain: GuardedDomain, image_map: AffineMap, target_domain: GuardedDomain) -> GuardedDomain | None:
    """Return q in ``source_domain`` whose affine image lies in ``target_domain``."""

    return pullback_domain(source_domain, image_map, target_domain)


def _subtract_cylinder(base: ResidueClass, removed: ResidueClass) -> list[ResidueClass]:
    """Return ``base \\ removed`` as disjoint power-of-two cylinders."""

    if not (_is_power_of_two(base.modulus) and _is_power_of_two(removed.modulus)):
        raise ValueError("exact cylinder difference requires power-of-two moduli")
    if not _compatible(base, removed):
        return [base]
    if removed.modulus <= base.modulus:
        if congruence_implies(base, removed):
            return []
        return [base]

    pieces: list[ResidueClass] = []
    base_bits = base.modulus.bit_length() - 1
    removed_bits = removed.modulus.bit_length() - 1
    for bit in range(base_bits, removed_bits):
        modulus = 1 << (bit + 1)
        residue = (removed.residue % (1 << bit)) | (((removed.residue >> bit) ^ 1) << bit)
        pieces.append(ResidueClass(residue, modulus, source=f"difference:{base.source}:{removed.source}"))
    return pieces


def _domain_to_cylinders(domain: GuardedDomain) -> list[ResidueClass]:
    cylinders = [domain.congruence]
    for excluded in domain.non_congruences:
        next_cylinders: list[ResidueClass] = []
        for cylinder in cylinders:
            next_cylinders.extend(_subtract_cylinder(cylinder, excluded))
        cylinders = next_cylinders
    return cylinders


def exact_domain_difference_partition(
    domain: GuardedDomain,
    removed_domains: list[GuardedDomain],
) -> list[GuardedDomain]:
    """Return an exact disjoint partition of ``domain`` minus removed domains."""

    normalised_removed: list[GuardedDomain] = []
    for removed in removed_domains:
        if removed.lower_bound == domain.lower_bound:
            normalised_removed.append(removed)
            continue
        first_at_domain_lower = removed.congruence.residue
        if first_at_domain_lower < domain.lower_bound:
            first_at_domain_lower += ceil_div(domain.lower_bound - first_at_domain_lower, removed.congruence.modulus) * removed.congruence.modulus
        if first_at_domain_lower < removed.lower_bound:
            raise ValueError("domain difference with finite lower-bound prefix is not represented in this RUN-044 certificate")
        normalised_removed.append(
            GuardedDomain(removed.congruence, removed.non_congruences, domain.lower_bound, removed.guards)
        )
    cylinders = _domain_to_cylinders(domain)
    for removed_domain in normalised_removed:
        for removed in _domain_to_cylinders(removed_domain):
            next_cylinders: list[ResidueClass] = []
            for cylinder in cylinders:
                next_cylinders.extend(_subtract_cylinder(cylinder, removed))
            cylinders = next_cylinders
    return [
        GuardedDomain(
            cylinder,
            lower_bound=domain.lower_bound,
            guards=domain.guards
            + (
                {
                    "kind": "domain_difference_piece",
                    "source_domain_hash": stable_hash(domain.to_json()),
                    "removed_domain_count": len(removed_domains),
                },
            ),
        )
        for cylinder in cylinders
    ]


def _domain_measure(domain: GuardedDomain) -> Fraction:
    """Exact 2-adic cylinder measure, used only for audit metadata."""

    cylinders = _domain_to_cylinders(domain)
    return sum((Fraction(1, cylinder.modulus) for cylinder in cylinders), Fraction(0, 1))


def _fraction_json(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _piece_id(payload: dict[str, Any]) -> str:
    return f"piece:{_short_hash(payload)}"


@dataclass(frozen=True)
class RefinedPiece:
    piece_id: str
    edge_id: str
    source: str
    target: str
    domain: GuardedDomain
    edge_map: AffineMap
    successor_edge_id: str | None = None
    piece_class: str = "INTERNAL"
    parent_piece_id: str | None = None
    elimination_round: int | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "piece_id": self.piece_id,
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "successor_edge_id": self.successor_edge_id,
            "piece_class": self.piece_class,
            "parent_piece_id": self.parent_piece_id,
            "elimination_round": self.elimination_round,
            "affine_map": self.edge_map.to_json(),
            "domain": self.domain.to_json(),
            "domain_hash": stable_hash(self.domain.to_json()),
        }


def _edge_domain_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["edge_id"]): row for row in rows if row.get("status") == "PASS"}


def _initial_edge_pieces(guarded_edges: dict[str, dict[str, Any]]) -> list[RefinedPiece]:
    pieces: list[RefinedPiece] = []
    for edge_id, row in sorted(guarded_edges.items(), key=lambda item: _edge_sort_key(item[0])):
        domain = domain_from_json(row["guarded_domain"])
        for index, cylinder in enumerate(_domain_to_cylinders(domain)):
            piece_domain = GuardedDomain(cylinder, lower_bound=domain.lower_bound, guards=domain.guards)
            payload = {
                "edge_id": edge_id,
                "index": index,
                "domain": piece_domain.to_json(),
                "kind": "initial",
            }
            pieces.append(
                RefinedPiece(
                    piece_id=_piece_id(payload),
                    edge_id=edge_id,
                    source=str(row["source"]),
                    target=str(row["target"]),
                    domain=piece_domain,
                    edge_map=affine_from_json(row["affine_map"]),
                )
            )
    return pieces


def _piece_from_domain(
    *,
    edge_row: dict[str, Any],
    domain: GuardedDomain,
    successor_edge_id: str | None,
    piece_class: str,
    parent_piece_id: str | None = None,
    salt: Any = None,
) -> RefinedPiece:
    payload = {
        "edge_id": edge_row["edge_id"],
        "successor_edge_id": successor_edge_id,
        "piece_class": piece_class,
        "parent_piece_id": parent_piece_id,
        "domain": domain.to_json(),
        "salt": salt,
    }
    return RefinedPiece(
        piece_id=_piece_id(payload),
        edge_id=str(edge_row["edge_id"]),
        source=str(edge_row["source"]),
        target=str(edge_row["target"]),
        successor_edge_id=successor_edge_id,
        piece_class=piece_class,
        parent_piece_id=parent_piece_id,
        domain=domain,
        edge_map=affine_from_json(edge_row["affine_map"]),
    )


def build_one_step_partition(guarded_edges: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Partition each guarded edge domain by exact one-step successor behavior."""

    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in guarded_edges.values():
        by_source[str(row["source"])].append(row)

    pieces: list[RefinedPiece] = []
    coverage_rows: list[dict[str, Any]] = []
    for edge_id, row in sorted(guarded_edges.items(), key=lambda item: _edge_sort_key(item[0])):
        edge_domain = domain_from_json(row["guarded_domain"])
        edge_map = affine_from_json(row["affine_map"])
        successor_domains: list[GuardedDomain] = []
        successor_piece_count = 0
        for successor in sorted(by_source.get(str(row["target"]), []), key=lambda item: _edge_sort_key(str(item["edge_id"]))):
            pulled = exact_domain_preimage(edge_domain, edge_map, domain_from_json(successor["guarded_domain"]))
            if pulled is None:
                continue
            successor_domains.append(pulled)
            for index, cylinder in enumerate(_domain_to_cylinders(pulled)):
                piece_domain = GuardedDomain(cylinder, lower_bound=pulled.lower_bound, guards=pulled.guards)
                pieces.append(
                    _piece_from_domain(
                        edge_row=row,
                        domain=piece_domain,
                        successor_edge_id=str(successor["edge_id"]),
                        piece_class="STAYS_IN_SCC",
                        salt={"successor": successor["edge_id"], "index": index},
                    )
                )
                successor_piece_count += 1
        exit_domains = exact_domain_difference_partition(edge_domain, successor_domains)
        for index, exit_domain in enumerate(exit_domains):
            pieces.append(
                _piece_from_domain(
                    edge_row=row,
                    domain=exit_domain,
                    successor_edge_id=None,
                    piece_class="GUARD_EXIT",
                    salt={"exit": index},
                )
            )
        edge_measure = _domain_measure(edge_domain)
        successor_measure = sum((_domain_measure(domain) for domain in successor_domains), Fraction(0, 1))
        coverage_rows.append(
            {
                "edge_id": edge_id,
                "source": row["source"],
                "target": row["target"],
                "successor_edge_count": len(successor_domains),
                "successor_piece_count": successor_piece_count,
                "exit_piece_count": len(exit_domains),
                "domain_measure": _fraction_json(edge_measure),
                "internal_successor_measure": _fraction_json(successor_measure),
                "guard_exit_measure": _fraction_json(edge_measure - successor_measure),
                "status": "PASS",
            }
        )
    return {
        "pieces": pieces,
        "coverage_rows": coverage_rows,
    }


def build_piece_successor_graph(pieces: list[RefinedPiece]) -> dict[str, Any]:
    """Compute exact successor intersections between refined pieces."""

    internal = [piece for piece in pieces if piece.piece_class == "STAYS_IN_SCC"]
    by_edge: dict[str, list[RefinedPiece]] = defaultdict(list)
    for piece in internal:
        by_edge[piece.edge_id].append(piece)

    graph_edges: list[dict[str, Any]] = []
    for piece in internal:
        for target_piece in by_edge.get(str(piece.successor_edge_id), []):
            pulled = exact_domain_preimage(piece.domain, piece.edge_map, target_piece.domain)
            if pulled is None:
                continue
            intersection = exact_domain_intersection(piece.domain, pulled)
            if intersection is None:
                continue
            graph_edges.append(
                {
                    "edge_id": f"{piece.piece_id}->{target_piece.piece_id}",
                    "source_piece_id": piece.piece_id,
                    "target_piece_id": target_piece.piece_id,
                    "source_edge_id": piece.edge_id,
                    "target_edge_id": target_piece.edge_id,
                    "transition_domain": intersection.to_json(),
                    "transition_domain_hash": stable_hash(intersection.to_json()),
                    "status": "PASS",
                }
            )
    return {
        "schema": "collatz_lab.guarded_piece_successor_graph",
        "version": 1,
        "run_id": RUN_ID,
        "node_count": len(internal),
        "edge_count": len(graph_edges),
        "nodes": {piece.piece_id: piece.to_json() for piece in internal},
        "edges": graph_edges,
        "status": "PASS",
    }


def eliminate_nonviable_graph_pieces(
    *,
    piece_ids: set[str],
    graph_edges: list[dict[str, Any]],
) -> dict[str, Any]:
    """Greatest fixed point on the finite refined-piece successor graph."""

    successors: dict[str, set[str]] = {piece_id: set() for piece_id in piece_ids}
    for edge in graph_edges:
        source = str(edge["source_piece_id"])
        target = str(edge["target_piece_id"])
        if source in piece_ids and target in piece_ids:
            successors[source].add(target)

    alive = set(piece_ids)
    ranks: dict[str, int] = {}
    iteration_rows: list[dict[str, Any]] = []
    round_index = 0
    while True:
        removed = sorted(
            piece_id for piece_id in alive if not (successors.get(piece_id, set()) & alive)
        )
        iteration_rows.append(
            {
                "iteration": round_index,
                "live_piece_count_before": len(alive),
                "removed_piece_count": len(removed),
                "live_piece_count_after": len(alive) - len(removed),
                "status": "FIXPOINT" if not removed else "ELIMINATION_ROUND",
            }
        )
        if not removed:
            break
        for piece_id in removed:
            ranks[piece_id] = round_index
        alive.difference_update(removed)
        round_index += 1
    return {
        "alive_piece_ids": alive,
        "node_ranks": ranks,
        "iterations": iteration_rows,
    }


def _find_graph_cycle(alive: set[str], graph_edges: list[dict[str, Any]]) -> list[str] | None:
    adjacency: dict[str, list[str]] = {piece_id: [] for piece_id in alive}
    for edge in graph_edges:
        source = str(edge["source_piece_id"])
        target = str(edge["target_piece_id"])
        if source in alive and target in alive:
            adjacency[source].append(target)
    visited: set[str] = set()
    in_stack: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        visited.add(node)
        in_stack[node] = len(stack)
        stack.append(node)
        for target in sorted(adjacency.get(node, [])):
            if target not in visited:
                cycle = visit(target)
                if cycle:
                    return cycle
            elif target in in_stack:
                return stack[in_stack[target] :]
        stack.pop()
        in_stack.pop(node, None)
        return None

    for node in sorted(alive):
        if node not in visited:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def _edge_cycle_from_piece_cycle(piece_cycle: list[str], pieces_by_id: dict[str, RefinedPiece]) -> list[str]:
    pieces = [pieces_by_id[piece_id] for piece_id in piece_cycle]
    if not pieces:
        return []
    edge_ids = [pieces[0].edge_id]
    edge_ids.extend(str(piece.successor_edge_id) for piece in pieces[:-1] if piece.successor_edge_id)
    return edge_ids


def _edge_graph_from_pieces(pieces: list[RefinedPiece]) -> dict[str, list[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for piece in pieces:
        if piece.piece_class == "STAYS_IN_SCC" and piece.successor_edge_id:
            adjacency[piece.edge_id].add(piece.successor_edge_id)
    return {edge_id: sorted(targets, key=_edge_sort_key) for edge_id, targets in adjacency.items()}


def _candidate_edge_cycle(edge_graph: dict[str, list[str]]) -> list[str] | None:
    visited: set[str] = set()
    in_stack: dict[str, int] = {}
    stack: list[str] = []

    def visit(edge_id: str) -> list[str] | None:
        visited.add(edge_id)
        in_stack[edge_id] = len(stack)
        stack.append(edge_id)
        for target in edge_graph.get(edge_id, []):
            if target not in visited:
                cycle = visit(target)
                if cycle:
                    return cycle
            elif target in in_stack:
                return stack[in_stack[target] :]
        stack.pop()
        in_stack.pop(edge_id, None)
        return None

    for edge_id in sorted(edge_graph, key=_edge_sort_key):
        if edge_id not in visited:
            cycle = visit(edge_id)
            if cycle:
                return cycle
    return None


def check_fraction_in_guarded_domain(value: Fraction, domain: GuardedDomain) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    residue = _fraction_mod_power_two(value, domain.congruence.modulus)
    if residue is None:
        failures.append({"reason": "fixed_point_denominator_not_invertible_mod_congruence"})
    elif residue != domain.congruence.residue:
        failures.append(
            {
                "reason": "fixed_point_congruence_mismatch",
                "expected_residue": str(domain.congruence.residue),
                "modulus": str(domain.congruence.modulus),
                "actual_residue": str(residue),
            }
        )
    non_congruence_checks: list[dict[str, Any]] = []
    for excluded in domain.non_congruences:
        excluded_residue = _fraction_mod_power_two(value, excluded.modulus)
        if excluded_residue is None:
            failures.append({"reason": "fixed_point_denominator_not_invertible_mod_non_congruence"})
            continue
        hit = excluded_residue == excluded.residue
        non_congruence_checks.append(
            {
                "excluded_residue": str(excluded.residue),
                "modulus": str(excluded.modulus),
                "actual_residue": str(excluded_residue),
                "satisfied": not hit,
                "source": excluded.source,
            }
        )
        if hit:
            failures.append(
                {
                    "reason": "fixed_point_hits_excluded_residue",
                    "excluded_residue": str(excluded.residue),
                    "modulus": str(excluded.modulus),
                    "source": excluded.source,
                }
            )
    natural = _fraction_is_natural(value, lower_bound=domain.lower_bound)
    return {
        "status": "PASS" if not failures else "FAIL",
        "fixed_point": _fraction_to_json(value),
        "canonical_congruence_check": {
            "residue": str(residue) if residue is not None else None,
            "expected_residue": str(domain.congruence.residue),
            "modulus": str(domain.congruence.modulus),
        },
        "non_congruence_checks": non_congruence_checks,
        "natural_number_status": "POSITIVE_NATURAL" if natural else "NON_NATURAL_2ADIC",
        "lower_bound": str(domain.lower_bound),
        "failures": failures,
    }


def build_cycle_viability_witness(
    *,
    cycle_record: dict[str, Any],
    guarded_edges: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    edge_ids = [str(edge_id) for edge_id in cycle_record.get("edge_ids", [])]
    composed = compose_guarded_sequence(edge_ids=edge_ids, guarded_edges=guarded_edges)
    base = {
        "cycle_id": str(cycle_record.get("cycle_id") or _hash(edge_ids)[:16]),
        "edge_ids": edge_ids,
        "source_states": list(cycle_record.get("source_states") or []),
    }
    if composed.get("status") != "PASS":
        return {**base, "status": "FAIL", "failure": composed, "classification": "DOMAIN_COMPOSITION_BUG"}
    cycle_map = affine_from_json(composed["composed_map"])
    fixed = fixed_point_for_cycle_map(cycle_map)
    if fixed is None:
        return {
            **base,
            "status": "FAIL",
            "classification": "NO_UNIQUE_2ADIC_FIXED_POINT",
            "composed_map": cycle_map.to_json(),
        }
    domain = domain_from_json(composed["guarded_domain"])
    fixed_check = check_fraction_in_guarded_domain(fixed, domain)
    fixed_equation_ok = cycle_map.A * fixed + cycle_map.B == cycle_map.D * fixed
    status = "PASS" if fixed_check["status"] == "PASS" and fixed_equation_ok else "FAIL"
    natural_status = fixed_check["natural_number_status"]
    classification = (
        "RAW_NATURAL_SURVIVING_CYCLE"
        if status == "PASS" and natural_status == "POSITIVE_NATURAL"
        else "NON_NATURAL_2ADIC_SURVIVING_KERNEL"
        if status == "PASS"
        else "FIXED_POINT_OUTSIDE_GUARDED_DOMAIN"
    )
    witness = {
        **base,
        "status": status,
        "classification": classification,
        "composed_map": cycle_map.to_json(),
        "guarded_cycle_domain": composed["guarded_domain"],
        "guarded_cycle_domain_hash": stable_hash(composed["guarded_domain"]),
        "fixed_point": _fraction_to_json(fixed),
        "fixed_point_equation": {
            "equation": "A*q+B = D*q",
            "status": "PASS" if fixed_equation_ok else "FAIL",
        },
        "fixed_point_guard_check": fixed_check,
        "raw_executable_natural_counterexample": status == "PASS" and natural_status == "POSITIVE_NATURAL",
    }
    witness["witness_hash"] = stable_hash({key: value for key, value in witness.items() if key != "witness_hash"})
    return witness


def replay_viability_kernel_witness(witness: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not isinstance(witness, dict):
        return {"accepted": False, "status": "FAIL", "failures": [{"reason": "missing_witness"}]}
    if contains_float(witness):
        failures.append({"reason": "floating_point_witness_rejected"})
    if str(witness.get("witness_hash")) != stable_hash({key: value for key, value in witness.items() if key != "witness_hash"}):
        failures.append({"reason": "viability_witness_hash_mismatch"})
    fixed = witness.get("fixed_point") if isinstance(witness.get("fixed_point"), dict) else {}
    try:
        q = Fraction(
            _as_int(fixed.get("numerator"), "fixed_point.numerator"),
            _as_int(fixed.get("denominator"), "fixed_point.denominator"),
        )
        cycle_map = affine_from_json(witness.get("composed_map") or {})
        domain = domain_from_json(witness.get("guarded_cycle_domain") or {})
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        failures.append({"reason": "viability_witness_payload_invalid", "detail": str(exc)})
    else:
        if cycle_map.A * q + cycle_map.B != cycle_map.D * q:
            failures.append({"reason": "fixed_point_equation_failed"})
        check = check_fraction_in_guarded_domain(q, domain)
        if check.get("status") != "PASS":
            failures.append({"reason": "fixed_point_guard_replay_failed", "check": check})
        if witness.get("fixed_point_guard_check") != check:
            failures.append(
                {
                    "reason": "fixed_point_guard_check_mismatch",
                    "expected": check,
                    "actual": witness.get("fixed_point_guard_check"),
                }
            )
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failures": failures}


def _raw_replay_status_for_witness(witness: dict[str, Any]) -> dict[str, Any]:
    fixed = witness.get("fixed_point") if isinstance(witness.get("fixed_point"), dict) else {}
    try:
        q = Fraction(_as_int(fixed.get("numerator"), "fixed_point.numerator"), _as_int(fixed.get("denominator"), "fixed_point.denominator"))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        return {"status": "FAIL", "raw_executable": False, "reason": "invalid_fixed_point", "detail": str(exc)}
    if q.denominator != 1 or q.numerator <= 0:
        return {
            "status": "NOT_RAW_NATURAL",
            "raw_executable": False,
            "reason": "surviving symbolic point is not a positive natural q",
        }
    return {
        "status": "RAW_Q_MAP_NATURAL_REPLAY_REQUIRED",
        "raw_executable": None,
        "reason": "positive natural symbolic witness requires standard Collatz boundary replay",
        "q0": str(q.numerator),
    }


def _certificate_hash(certificate: dict[str, Any]) -> str:
    return _hash({key: value for key, value in certificate.items() if key != "certificate_hash"})


def build_empty_viability_certificate(
    *,
    states: list[str],
    edge_ids: list[str],
    pieces: list[RefinedPiece],
    graph_edges: list[dict[str, Any]],
    elimination: dict[str, Any],
) -> dict[str, Any]:
    ranks = {piece_id: int(rank) for piece_id, rank in (elimination.get("node_ranks") or {}).items()}
    edge_checks: list[dict[str, Any]] = []
    for edge in graph_edges:
        source = str(edge["source_piece_id"])
        target = str(edge["target_piece_id"])
        if source not in ranks:
            continue
        if target in ranks:
            decreases = ranks[target] < ranks[source]
            edge_checks.append(
                {
                    "edge_id": edge["edge_id"],
                    "source_guarded_node": source,
                    "target_guarded_node": target,
                    "edge_class": "STAYS_IN_SCC",
                    "rank_decreases": decreases,
                    "or_exits": False,
                    "status": "PASS" if decreases else "FAIL",
                }
            )
        else:
            edge_checks.append(
                {
                    "edge_id": edge["edge_id"],
                    "source_guarded_node": source,
                    "target_guarded_node": target,
                    "edge_class": "GUARD_EXIT",
                    "rank_decreases": True,
                    "or_exits": True,
                    "status": "PASS",
                }
            )
    certificate = {
        "schema": "collatz_lab.scc_guarded_empty_viability_kernel_certificate",
        "version": 1,
        "type": EMPTY_KERNEL_CERT_TYPE,
        "scc_id": DEFAULT_SCC_ID,
        "states": states,
        "covered_edge_ids": sorted(edge_ids, key=_edge_sort_key),
        "refined_piece_count": len(pieces),
        "ranked_piece_count": len(ranks),
        "final_kernel_piece_count": 0,
        "node_ranks": ranks,
        "edge_checks": edge_checks,
        "viability_kernel_iterations": elimination.get("iterations") or [],
        "status": "PASS",
    }
    certificate["certificate_hash"] = _certificate_hash(certificate)
    return certificate


def replay_empty_viability_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not isinstance(certificate, dict):
        return {"accepted": False, "status": "FAIL", "failures": [{"reason": "missing_certificate"}]}
    if contains_float(certificate):
        failures.append({"reason": "floating_point_certificate_rejected"})
    if certificate.get("schema") != "collatz_lab.scc_guarded_empty_viability_kernel_certificate":
        failures.append({"reason": "unsupported_empty_viability_schema"})
    if certificate.get("type") != EMPTY_KERNEL_CERT_TYPE:
        failures.append({"reason": "unsupported_empty_viability_type", "type": certificate.get("type")})
    if str(certificate.get("certificate_hash")) != _certificate_hash(certificate):
        failures.append({"reason": "empty_viability_certificate_hash_mismatch"})
    if certificate.get("status") != "PASS":
        failures.append({"reason": "empty_viability_certificate_status_not_pass", "status": certificate.get("status")})
    if int(certificate.get("final_kernel_piece_count", -1)) != 0:
        failures.append({"reason": "final_viability_kernel_not_empty"})
    ranks = certificate.get("node_ranks") or {}
    if int(certificate.get("ranked_piece_count", -1)) != len(ranks):
        failures.append({"reason": "ranked_piece_count_mismatch"})
    for check in certificate.get("edge_checks", []) or []:
        if check.get("status") != "PASS":
            failures.append({"reason": "edge_check_not_pass", "edge_check": check})
        source = check.get("source_guarded_node")
        target = check.get("target_guarded_node")
        if source in ranks and target in ranks and int(ranks[target]) >= int(ranks[source]) and not check.get("or_exits"):
            failures.append({"reason": "rank_not_decreasing_under_replay", "edge_check": check})
    return {"accepted": not failures, "status": "PASS" if not failures else "FAIL", "failures": failures}


def _ranking_certificate_from_empty_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    ranking = {
        "schema": RANKING_SCHEMA,
        "version": 1,
        "type": RANKING_CERT_TYPE,
        "scc_id": DEFAULT_SCC_ID,
        "states": certificate.get("states") or [],
        "covered_edge_ids": certificate.get("covered_edge_ids") or [],
        "guarded_node_count": certificate.get("refined_piece_count", 0),
        "guarded_edge_count": len(certificate.get("edge_checks") or []),
        "proof_kind": "viability_kernel_elimination",
        "node_ranks": certificate.get("node_ranks") or {},
        "edge_checks": certificate.get("edge_checks") or [],
        "cycle_exit_checks": [],
        "empty_viability_kernel_certificate_hash": certificate.get("certificate_hash"),
        "status": "PASS",
    }
    ranking["certificate_hash"] = ranking_certificate_hash(ranking)
    return ranking


def _write_empty_certificate_to_store(certificate: dict[str, Any], ranking: dict[str, Any]) -> dict[str, str]:
    out_cert = Path("certificate_store/run044_scc_guarded_empty_viability_kernel_certificate.json")
    out_rank = Path("certificate_store/run044_scc_guarded_ranking_certificate.json")
    _write_json(certificate, out_cert)
    _write_json(ranking, out_rank)
    return {
        "empty_viability_kernel_certificate": str(out_cert),
        "well_founded_ranking_certificate": str(out_rank),
    }


def run_guarded_viability_kernel(config: dict[str, Any] | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = cfg.get("guarded_viability_kernel_run044", {}) if isinstance(cfg.get("guarded_viability_kernel_run044"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    guarded_edges_path = Path(run_cfg.get("guarded_edge_domains") or "reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_edge_domains.jsonl")
    guarded_rows = load_jsonl(guarded_edges_path)
    guarded_edges = _edge_domain_by_id(guarded_rows)
    states = [f"P{index}" for index in range(12, 25)]
    edge_ids = sorted(guarded_edges, key=_edge_sort_key)
    edge_failures = [row for row in guarded_rows if row.get("status") != "PASS"]

    if edge_failures:
        result = {
            "schema": "collatz_lab.run044_guarded_viability_kernel_elimination",
            "version": 1,
            "run_id": RUN_ID,
            "training_launched": False,
            "big_model_launched": False,
            "selector_work_launched": False,
            "search_tuning_launched": False,
            "verifier_relaxed": False,
            "floating_point_certificate_used": False,
            "status": "GUARD_SEMANTICS_MISSING",
            "failure_classification": "GUARD_SEMANTICS_MISSING",
            "accepted_scc_elimination_ranking": False,
            "guarded_edge_count": len(edge_ids),
            "failures": edge_failures[:20],
        }
        _write_json(result, out_dir / "run_result.json")
        return result

    initial_pieces = _initial_edge_pieces(guarded_edges)
    partition = build_one_step_partition(guarded_edges)
    one_step_pieces: list[RefinedPiece] = partition["pieces"]
    internal_pieces = [piece for piece in one_step_pieces if piece.piece_class == "STAYS_IN_SCC"]
    graph = build_piece_successor_graph(one_step_pieces)
    pieces_by_id = {piece.piece_id: piece for piece in internal_pieces}
    elimination = eliminate_nonviable_graph_pieces(piece_ids=set(pieces_by_id), graph_edges=list(graph["edges"]))
    alive = set(elimination["alive_piece_ids"])

    write_jsonl(out_dir / "guarded_refined_pieces.jsonl", [piece.to_json() for piece in one_step_pieces])
    write_jsonl(out_dir / "guarded_partition_coverage.jsonl", partition["coverage_rows"])
    _write_json(graph, out_dir / "guarded_piece_successor_graph.json")
    write_jsonl(out_dir / "viability_kernel_iterations.jsonl", list(elimination["iterations"]))

    witness: dict[str, Any] | None = None
    piece_cycle = _find_graph_cycle(alive, list(graph["edges"])) if alive else None
    if piece_cycle:
        edge_cycle = _edge_cycle_from_piece_cycle(piece_cycle, pieces_by_id)
        witness = build_cycle_viability_witness(cycle_record={"edge_ids": edge_cycle}, guarded_edges=guarded_edges)
        if witness.get("status") != "PASS":
            edge_graph = _edge_graph_from_pieces(internal_pieces)
            fallback_cycle = _candidate_edge_cycle(edge_graph)
            if fallback_cycle:
                fallback = build_cycle_viability_witness(cycle_record={"edge_ids": fallback_cycle}, guarded_edges=guarded_edges)
                if fallback.get("status") == "PASS":
                    witness = fallback

    artifacts: dict[str, str] = {
        "guarded_refined_pieces": str(out_dir / "guarded_refined_pieces.jsonl"),
        "guarded_partition_coverage": str(out_dir / "guarded_partition_coverage.jsonl"),
        "guarded_piece_successor_graph": str(out_dir / "guarded_piece_successor_graph.json"),
        "viability_kernel_iterations": str(out_dir / "viability_kernel_iterations.jsonl"),
        "guarded_viability_kernel": str(out_dir / "guarded_viability_kernel.json"),
        "surviving_viability_kernel_obstruction": str(out_dir / "surviving_viability_kernel_obstruction.json"),
        "scc_guarded_empty_viability_kernel_certificate": str(out_dir / "scc_guarded_empty_viability_kernel_certificate.json"),
        "scc_guarded_elimination_certificate": str(out_dir / "scc_guarded_elimination_certificate.json"),
        "run_result": str(out_dir / "run_result.json"),
    }

    if alive and witness and witness.get("status") == "PASS":
        witness_replay = replay_viability_kernel_witness(witness)
        raw_replay = _raw_replay_status_for_witness(witness)
        surviving_piece_rows = [pieces_by_id[piece_id].to_json() for piece_id in sorted(alive)[:128]]
        kernel = {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "type": NONEMPTY_KERNEL_TYPE,
            "scc_id": DEFAULT_SCC_ID,
            "status": "NONEMPTY",
            "kernel_kind": "exact_refined_piece_gfp_with_lasso_witness",
            "refined_piece_count": len(internal_pieces),
            "surviving_piece_count": len(alive),
            "surviving_pieces_recorded": len(surviving_piece_rows),
            "surviving_pieces": surviving_piece_rows,
            "piece_cycle": piece_cycle,
            "surviving_witness": witness,
            "witness_replay": witness_replay,
            "raw_collatz_replay": raw_replay,
        }
        obstruction = {
            "schema": "collatz_lab.guarded_viability_kernel_obstruction",
            "version": 1,
            "run_id": RUN_ID,
            "failure_classification": "NONEMPTY_GUARDED_VIABILITY_KERNEL",
            "guarded_kernel_nonempty": True,
            "raw_executable": raw_replay.get("raw_executable"),
            "raw_collatz_replay": raw_replay,
            "natural_number_status": (witness.get("fixed_point_guard_check") or {}).get("natural_number_status"),
            "surviving_cycle_id": witness.get("cycle_id"),
            "surviving_edge_ids": witness.get("edge_ids"),
            "fixed_point": witness.get("fixed_point"),
            "exact_reason": (
                "the exact refined guarded transition graph has a nonempty greatest fixed point; "
                "the recorded lasso fixed point replays against the full guarded cycle domain"
            ),
            "new_invariant_or_stronger_state_variable_needed": True,
        }
        failure_cert = {
            "schema": RANKING_SCHEMA,
            "version": 1,
            "type": RANKING_CERT_TYPE,
            "scc_id": DEFAULT_SCC_ID,
            "states": states,
            "covered_edge_ids": edge_ids,
            "guarded_node_count": len(internal_pieces),
            "guarded_edge_count": int(graph["edge_count"]),
            "proof_kind": "none",
            "node_ranks": {},
            "edge_checks": [],
            "cycle_exit_checks": [],
            "status": "FAIL",
            "failure_classification": "NONEMPTY_GUARDED_VIABILITY_KERNEL",
        }
        failure_cert["certificate_hash"] = ranking_certificate_hash(failure_cert)
        _write_json(kernel, out_dir / "guarded_viability_kernel.json")
        _write_json(obstruction, out_dir / "surviving_viability_kernel_obstruction.json")
        _write_json({"schema": "collatz_lab.scc_guarded_empty_viability_kernel_certificate", "version": 1, "status": "FAIL", "reason": "NONEMPTY_GUARDED_VIABILITY_KERNEL"}, out_dir / "scc_guarded_empty_viability_kernel_certificate.json")
        _write_json(failure_cert, out_dir / "scc_guarded_elimination_certificate.json")
        status = "NONEMPTY_GUARDED_VIABILITY_KERNEL"
        accepted = False
        certificate_replay = {"accepted": False, "status": "FAIL", "failures": [{"reason": status}]}
    elif alive:
        kernel = {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "type": NONEMPTY_KERNEL_TYPE,
            "scc_id": DEFAULT_SCC_ID,
            "status": "EXACT_MISSING_DOMAIN_OPERATION",
            "kernel_kind": "refined_piece_gfp_without_replayed_lasso",
            "surviving_piece_count": len(alive),
            "exact_missing_domain_operation": "no replayed lasso witness was found for the nonempty refined-piece kernel",
        }
        _write_json(kernel, out_dir / "guarded_viability_kernel.json")
        _write_json(kernel, out_dir / "surviving_viability_kernel_obstruction.json")
        _write_json({"schema": "collatz_lab.scc_guarded_empty_viability_kernel_certificate", "version": 1, "status": "FAIL", "reason": "EXACT_MISSING_DOMAIN_OPERATION"}, out_dir / "scc_guarded_empty_viability_kernel_certificate.json")
        _write_json({"schema": RANKING_SCHEMA, "version": 1, "type": RANKING_CERT_TYPE, "status": "FAIL", "proof_kind": "none", "certificate_hash": ""}, out_dir / "scc_guarded_elimination_certificate.json")
        status = "EXACT_MISSING_DOMAIN_OPERATION"
        accepted = False
        certificate_replay = {"accepted": False, "status": "FAIL", "failures": [{"reason": status}]}
    else:
        empty_certificate = build_empty_viability_certificate(
            states=states,
            edge_ids=edge_ids,
            pieces=internal_pieces,
            graph_edges=list(graph["edges"]),
            elimination=elimination,
        )
        certificate_replay = replay_empty_viability_certificate(empty_certificate)
        ranking_certificate = _ranking_certificate_from_empty_certificate(empty_certificate)
        store_paths = _write_empty_certificate_to_store(empty_certificate, ranking_certificate) if certificate_replay["accepted"] else {}
        artifacts.update(store_paths)
        kernel = {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "scc_id": DEFAULT_SCC_ID,
            "status": "EMPTY",
            "kernel_kind": "exact_refined_piece_gfp",
            "final_kernel_piece_count": 0,
            "certificate_hash": empty_certificate.get("certificate_hash"),
        }
        _write_json(kernel, out_dir / "guarded_viability_kernel.json")
        _write_json({"schema": "collatz_lab.guarded_viability_kernel_obstruction", "version": 1, "run_id": RUN_ID, "status": "EMPTY"}, out_dir / "surviving_viability_kernel_obstruction.json")
        _write_json(empty_certificate, out_dir / "scc_guarded_empty_viability_kernel_certificate.json")
        _write_json(ranking_certificate, out_dir / "scc_guarded_elimination_certificate.json")
        status = "PASS" if certificate_replay["accepted"] else "ELIMINATION_CERTIFICATE_REPLAY_FAIL"
        accepted = certificate_replay["accepted"]

    result = {
        "schema": "collatz_lab.run044_guarded_viability_kernel_elimination",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_tuning_launched": False,
        "verifier_relaxed": False,
        "floating_point_certificate_used": False,
        "status": status,
        "accepted_scc_elimination_ranking": accepted,
        "guarded_edge_count": len(edge_ids),
        "initial_piece_count": len(initial_pieces),
        "refined_piece_count": len(one_step_pieces),
        "internal_refined_piece_count": len(internal_pieces),
        "guard_exit_piece_count": len(one_step_pieces) - len(internal_pieces),
        "piece_successor_edge_count": int(graph["edge_count"]),
        "viability_kernel_empty": status == "PASS",
        "viability_kernel_nonempty": status == "NONEMPTY_GUARDED_VIABILITY_KERNEL",
        "surviving_piece_count": len(alive),
        "raw_executable_survivor": bool(witness and witness.get("raw_executable_natural_counterexample")),
        "surviving_cycle_id": witness.get("cycle_id") if witness else None,
        "certificate_replay": certificate_replay,
        "top_level_replay_launched": False,
        "top_level_replay_reason": "guarded viability kernel is nonempty" if status == "NONEMPTY_GUARDED_VIABILITY_KERNEL" else "not launched by RUN-044 implementation",
        "artifacts": artifacts,
    }
    _write_json(result, out_dir / "run_result.json")
    return result
