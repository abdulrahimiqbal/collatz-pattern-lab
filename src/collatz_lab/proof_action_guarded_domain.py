"""Exact guarded domains for parent-coordinate SCC replay.

RUN-038 treated an SCC cycle as repeatable once the composed parent coordinate
returned to a coarse residue class.  The S4 parent-coordinate maps carry more
guards than that: source branch, k-divisibility, excluded-next-power, exact
valuation, and affine integrality.  This module keeps those guards as exact
integer predicates and provides the pullback operations needed by RUN-040.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .proof_action_parent_coordinate_map import replay_parent_coordinate_map_certificate
from .proof_action_parent_transition_cert import parse_branch_id


@dataclass(frozen=True)
class ResidueClass:
    residue: int
    modulus: int
    kind: str = "congruence"
    source: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.residue, bool) or isinstance(self.modulus, bool):
            raise TypeError("residue classes require integer values")
        if self.modulus <= 0:
            raise ValueError("residue-class modulus must be positive")
        object.__setattr__(self, "residue", self.residue % self.modulus)

    def to_json(self) -> dict[str, Any]:
        return {
            "residue": str(self.residue),
            "modulus": str(self.modulus),
            "kind": self.kind,
            "source": self.source,
        }


@dataclass(frozen=True)
class AffineMap:
    A: int
    B: int
    D: int = 1

    def __post_init__(self) -> None:
        if self.D <= 0:
            raise ValueError("affine denominator must be positive")
        A, B, D = _normalise_fraction_triple(self.A, self.B, self.D)
        object.__setattr__(self, "A", A)
        object.__setattr__(self, "B", B)
        object.__setattr__(self, "D", D)

    def compose_after(self, other: "AffineMap") -> "AffineMap":
        """Return ``self(other(q))``."""

        return AffineMap(
            self.A * other.A,
            self.A * other.B + self.B * other.D,
            self.D * other.D,
        )

    def to_json(self) -> dict[str, str]:
        return {"A": str(self.A), "B": str(self.B), "D": str(self.D)}


@dataclass(frozen=True)
class GuardedDomain:
    congruence: ResidueClass
    non_congruences: tuple[ResidueClass, ...] = ()
    lower_bound: int = 1
    guards: tuple[dict[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if self.lower_bound <= 0:
            raise ValueError("guarded-domain lower bound must be positive")

    @staticmethod
    def top() -> "GuardedDomain":
        return GuardedDomain(ResidueClass(0, 1, source="top"), lower_bound=1)

    def minimum_q(self) -> int:
        return minimum_in_residue_class(self.congruence.residue, self.congruence.modulus, self.lower_bound)

    def to_json(self) -> dict[str, Any]:
        return {
            "congruences": [self.congruence.to_json()],
            "canonical_congruence": self.congruence.to_json(),
            "non_congruences": [row.to_json() for row in self.non_congruences],
            "lower_bound": str(self.lower_bound),
            "minimum_q": str(self.minimum_q()),
            "guards": list(self.guards),
        }


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


def ceil_div(num: int, den: int) -> int:
    if den <= 0:
        raise ValueError("denominator must be positive")
    return -((-num) // den)


def minimum_in_residue_class(residue: int, modulus: int, lower_bound: int) -> int:
    residue %= modulus
    if residue >= lower_bound:
        return residue
    return residue + ceil_div(lower_bound - residue, modulus) * modulus


def _normalise_fraction_triple(A: int, B: int, D: int) -> tuple[int, int, int]:
    if D < 0:
        A, B, D = -A, -B, -D
    gcd = math.gcd(math.gcd(abs(A), abs(B)), abs(D))
    if gcd > 1:
        A //= gcd
        B //= gcd
        D //= gcd
    return A, B, D


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


def intersect_congruence(domain: GuardedDomain, constraint: ResidueClass) -> GuardedDomain | None:
    imposed = impose_linear_congruence(
        residue=domain.congruence.residue,
        modulus=domain.congruence.modulus,
        a=1,
        b=-constraint.residue,
        congruence_modulus=constraint.modulus,
    )
    if imposed is None:
        return None
    updated = GuardedDomain(
        ResidueClass(imposed[0], imposed[1], source=f"{domain.congruence.source}&{constraint.source}".strip("&")),
        non_congruences=domain.non_congruences,
        lower_bound=domain.lower_bound,
        guards=domain.guards + (constraint.to_json(),),
    )
    for excluded in updated.non_congruences:
        if congruence_implies(updated.congruence, excluded):
            return None
    return updated


def congruence_implies(base: ResidueClass, required: ResidueClass) -> bool:
    return base.modulus % required.modulus == 0 and base.residue % required.modulus == required.residue


def congruence_intersection_empty(left: ResidueClass, right: ResidueClass) -> bool:
    return (left.residue - right.residue) % math.gcd(left.modulus, right.modulus) != 0


def add_non_congruence(domain: GuardedDomain, excluded: ResidueClass) -> GuardedDomain | None:
    if congruence_implies(domain.congruence, excluded):
        return None
    if congruence_intersection_empty(domain.congruence, excluded):
        guards = domain.guards + ({**excluded.to_json(), "vacuous_on_current_congruence": True},)
        return GuardedDomain(domain.congruence, domain.non_congruences, domain.lower_bound, guards)
    if any(row.modulus == excluded.modulus and row.residue == excluded.residue for row in domain.non_congruences):
        return domain
    return GuardedDomain(
        domain.congruence,
        domain.non_congruences + (excluded,),
        domain.lower_bound,
        domain.guards + (excluded.to_json(),),
    )


def impose_image_congruence(
    domain: GuardedDomain,
    image_map: AffineMap,
    constraint: ResidueClass,
) -> GuardedDomain | None:
    imposed = impose_linear_congruence(
        residue=domain.congruence.residue,
        modulus=domain.congruence.modulus,
        a=image_map.A,
        b=image_map.B - image_map.D * constraint.residue,
        congruence_modulus=image_map.D * constraint.modulus,
    )
    if imposed is None:
        return None
    return GuardedDomain(
        ResidueClass(imposed[0], imposed[1], source=f"pullback:{constraint.source}"),
        non_congruences=domain.non_congruences,
        lower_bound=domain.lower_bound,
        guards=domain.guards + ({**constraint.to_json(), "pullback_via": image_map.to_json()},),
    )


def impose_image_non_congruence(
    domain: GuardedDomain,
    image_map: AffineMap,
    excluded: ResidueClass,
) -> GuardedDomain | None:
    violation = impose_linear_congruence(
        residue=domain.congruence.residue,
        modulus=domain.congruence.modulus,
        a=image_map.A,
        b=image_map.B - image_map.D * excluded.residue,
        congruence_modulus=image_map.D * excluded.modulus,
    )
    if violation is None:
        return GuardedDomain(
            domain.congruence,
            domain.non_congruences,
            domain.lower_bound,
            domain.guards + ({**excluded.to_json(), "pullback_vacuous": True, "pullback_via": image_map.to_json()},),
        )
    return add_non_congruence(
        GuardedDomain(domain.congruence, domain.non_congruences, domain.lower_bound, domain.guards),
        ResidueClass(violation[0], violation[1], kind="non_congruence", source=f"pullback:{excluded.source}"),
    )


def impose_image_lower_bound(domain: GuardedDomain, image_map: AffineMap, lower_bound: int) -> GuardedDomain:
    if image_map.A <= 0:
        raise ValueError("lower-bound transfer currently requires positive affine slope")
    transferred = ceil_div(image_map.D * lower_bound - image_map.B, image_map.A)
    return GuardedDomain(
        domain.congruence,
        domain.non_congruences,
        max(domain.lower_bound, transferred),
        domain.guards + ({"kind": "lower_bound_pullback", "image_lower_bound": str(lower_bound), "pullback_via": image_map.to_json()},),
    )


def pullback_domain(domain: GuardedDomain, image_map: AffineMap, required: GuardedDomain) -> GuardedDomain | None:
    updated: GuardedDomain | None = impose_image_congruence(domain, image_map, required.congruence)
    if updated is None:
        return None
    for excluded in required.non_congruences:
        updated = impose_image_non_congruence(updated, image_map, excluded)
        if updated is None:
            return None
    updated = impose_image_lower_bound(updated, image_map, required.lower_bound)
    return updated


def image_domain(domain: GuardedDomain, image_map: AffineMap) -> tuple[GuardedDomain | None, dict[str, Any]]:
    """Push a single residue-class domain through an affine map exactly.

    Non-congruence images are not silently discarded; they are reported as a
    limitation because a non-congruence can map to a union of residue exclusions.
    RUN-040 uses pullbacks for proof checks whenever this limitation matters.
    """

    r = domain.congruence.residue
    M = domain.congruence.modulus
    base_num = image_map.A * r + image_map.B
    step_num = image_map.A * M
    failures: list[dict[str, Any]] = []
    if base_num % image_map.D != 0:
        failures.append({"reason": "image_base_not_integral", "numerator_mod_D": str(base_num % image_map.D)})
    if step_num % image_map.D != 0:
        failures.append({"reason": "image_step_not_integral", "step_mod_D": str(step_num % image_map.D)})
    if failures:
        return None, {"status": "FAIL", "failures": failures}
    image_residue = base_num // image_map.D
    image_modulus = abs(step_num // image_map.D)
    pushed = GuardedDomain(
        ResidueClass(image_residue, image_modulus, source="affine_image"),
        lower_bound=max(1, (image_map.A * domain.minimum_q() + image_map.B) // image_map.D),
        guards=({"kind": "affine_image", "source_domain_hash": stable_hash(domain.to_json()), "map": image_map.to_json()},),
    )
    report = {
        "status": "PASS",
        "non_congruence_image_supported": False,
        "non_congruence_count_not_pushed": len(domain.non_congruences),
    }
    return pushed, report


def domain_implies_linear_non_congruence(
    domain: GuardedDomain,
    *,
    a: int,
    b: int,
    modulus: int,
) -> tuple[bool, dict[str, Any]]:
    """Check whether ``domain`` proves ``a*q+b != 0 mod modulus``.

    The check is exact for the residue-class-minus-exclusions shape used here:
    it first computes the violation subprogression and then verifies that it is
    either CRT-empty or wholly covered by one recorded non-congruence.
    """

    violation = impose_linear_congruence(
        residue=domain.congruence.residue,
        modulus=domain.congruence.modulus,
        a=a,
        b=b,
        congruence_modulus=modulus,
    )
    if violation is None:
        return True, {"status": "PASS", "reason": "violation_subdomain_empty"}
    violation_class = ResidueClass(violation[0], violation[1], source="linear_violation")
    for excluded in domain.non_congruences:
        if congruence_implies(violation_class, excluded):
            return True, {
                "status": "PASS",
                "reason": "violation_subdomain_covered_by_existing_non_congruence",
                "violation": violation_class.to_json(),
                "covering_non_congruence": excluded.to_json(),
            }
    return False, {
        "status": "FAIL",
        "reason": "violation_subdomain_not_excluded",
        "violation": violation_class.to_json(),
    }


def domain_self_invariance(domain: GuardedDomain, cycle_map: AffineMap) -> dict[str, Any]:
    """Replay whether ``cycle_map`` sends the full guarded domain into itself."""

    failures: list[dict[str, Any]] = []
    r = domain.congruence.residue
    M = domain.congruence.modulus
    A = cycle_map.A
    B = cycle_map.B
    D = cycle_map.D
    if (A * r + B) % D != 0:
        failures.append(
            {
                "guard": "map_integrality",
                "reason": "base_residue_not_integral",
                "numerator_mod_D": str((A * r + B) % D),
            }
        )
    if (A * M) % D != 0:
        failures.append(
            {
                "guard": "map_integrality",
                "reason": "domain_step_not_integral",
                "numerator_mod_D": str((A * M) % D),
            }
        )
    if not failures:
        image_min = (A * domain.minimum_q() + B) // D
        if image_min < domain.lower_bound:
            failures.append(
                {
                    "guard": "lower_bound",
                    "reason": "image_below_lower_bound",
                    "image_minimum_q": str(image_min),
                    "required_lower_bound": str(domain.lower_bound),
                }
            )
    return_modulus = D * M
    if (A * r + B - D * r) % return_modulus != 0:
        failures.append(
            {
                "guard": "congruence",
                "reason": "base_residue_does_not_return",
                "numerator_mod_D": str((A * r + B - D * r) % return_modulus),
            }
        )
    if (A * M) % return_modulus != 0:
        failures.append(
            {
                "guard": "congruence",
                "reason": "domain_step_does_not_return",
                "numerator_mod_D": str((A * M) % return_modulus),
            }
        )
    for excluded in domain.non_congruences:
        ok, report = domain_implies_linear_non_congruence(
            domain,
            a=A,
            b=B - D * excluded.residue,
            modulus=D * excluded.modulus,
        )
        if not ok:
            failures.append(
                {
                    "guard": "non_congruence",
                    "reason": "image_can_hit_excluded_residue",
                    "excluded": excluded.to_json(),
                    "detail": report,
                }
            )
    return {
        "status": "PASS" if not failures else "FAIL",
        "domain_hash": stable_hash(domain.to_json()),
        "cycle_map": cycle_map.to_json(),
        "failures": failures,
    }


def descent_check(domain: GuardedDomain, cycle_map: AffineMap) -> dict[str, Any]:
    q_min = domain.minimum_q()
    delta = (cycle_map.D - cycle_map.A) * q_min - cycle_map.B
    status = "PASS" if delta > 0 and (cycle_map.A < cycle_map.D or (cycle_map.A == cycle_map.D and cycle_map.B < 0)) else "FAIL"
    return {
        "status": status,
        "minimum_q": str(q_min),
        "delta_at_minimum_q": str(delta),
        "slope_relation": "A<D" if cycle_map.A < cycle_map.D else "A=D" if cycle_map.A == cycle_map.D else "A>D",
    }


def _required_field(container: dict[str, Any], field: str, failures: list[dict[str, Any]]) -> Any:
    value = container.get(field)
    if value is None:
        failures.append({"reason": "missing_guard_field", "field": field})
    return value


def build_guarded_domain_from_map_certificate(
    *,
    edge_map: dict[str, Any],
    map_certificate: dict[str, Any],
) -> dict[str, Any]:
    """Build a replayable full guarded-domain row for one SCC edge."""

    failures: list[dict[str, Any]] = []
    if contains_float({"edge_map": edge_map, "map_certificate": map_certificate}):
        failures.append({"reason": "floating_point_guard_payload_rejected"})
    replay = replay_parent_coordinate_map_certificate(map_certificate)
    if not replay.accepted:
        failures.append({"reason": "parent_coordinate_map_certificate_replay_failed", "replay": replay.to_dict()})

    source_transition = map_certificate.get("source_transition_certificate")
    parent_map = map_certificate.get("parent_coordinate_map")
    if not isinstance(source_transition, dict):
        failures.append({"reason": "missing_source_transition_certificate"})
        source_transition = {}
    if not isinstance(parent_map, dict):
        failures.append({"reason": "missing_parent_coordinate_map"})
        parent_map = {}

    try:
        branch = parse_branch_id(str(_required_field(map_certificate, "branch_id", failures) or ""))
    except ValueError as exc:
        failures.append({"reason": "invalid_branch_id", "detail": str(exc)})
        branch = {"a": -1, "residue": 0, "depth": 0}

    divisibility = source_transition.get("divisibility_certificate")
    if not isinstance(divisibility, dict):
        failures.append({"reason": "missing_divisibility_certificate"})
        divisibility = {}

    try:
        A = _as_int(parent_map.get("A"), "A")
        B = _as_int(parent_map.get("B"), "B")
        D = _as_int(parent_map.get("D"), "D")
        source_depth = _as_int(parent_map.get("source_depth"), "source_depth")
        source_residue = _as_int(parent_map.get("source_residue"), "source_residue")
        domain_modulus = _as_int(parent_map.get("domain_modulus"), "domain_modulus")
        domain_residue = _as_int(parent_map.get("domain_residue"), "domain_residue")
        minimum_q = _as_int(parent_map.get("minimum_q", 1), "minimum_q")
        valuation = _as_int(map_certificate.get("valuation"), "valuation")
        k_modulus = _as_int(divisibility.get("k_divisibility_modulus"), "k_divisibility_modulus")
        k_residue = _as_int(divisibility.get("k_divisibility_residue"), "k_divisibility_residue")
        excluded_modulus = _as_int(divisibility.get("excluded_next_power_modulus"), "excluded_next_power_modulus")
        excluded_residue = _as_int(divisibility.get("excluded_next_power_residue"), "excluded_next_power_residue")
    except ValueError as exc:
        failures.append({"reason": "guard_integer_field_invalid", "detail": str(exc)})
        A = B = 0
        D = 1
        source_depth = branch["depth"]
        source_residue = branch["residue"]
        domain_modulus = 1
        domain_residue = 0
        minimum_q = 1
        valuation = -1
        k_modulus = 0
        k_residue = 0
        excluded_modulus = 0
        excluded_residue = 0

    source_modulus = 1 << source_depth if source_depth >= 0 else 0
    if source_depth != branch["depth"] or source_residue != branch["residue"]:
        failures.append({"reason": "branch_guard_mismatch"})
    if int(map_certificate.get("source_parent", -1)) != branch["a"]:
        failures.append({"reason": "source_parent_branch_mismatch"})
    if valuation != _as_int(divisibility.get("valuation", valuation), "divisibility_valuation"):
        failures.append({"reason": "valuation_field_mismatch"})
    expected_k_modulus = 1 << valuation if valuation > 0 else 1
    if k_modulus != expected_k_modulus:
        failures.append({"reason": "k_divisibility_modulus_mismatch", "expected": expected_k_modulus, "actual": k_modulus})
    expected_excluded_modulus = 1 << (valuation + 1) if valuation >= 0 else None
    if expected_excluded_modulus is not None and excluded_modulus != expected_excluded_modulus:
        failures.append(
            {
                "reason": "excluded_next_power_modulus_mismatch",
                "expected": expected_excluded_modulus,
                "actual": excluded_modulus,
            }
        )

    domain: GuardedDomain | None = GuardedDomain.top()
    guard_rows: list[dict[str, Any]] = []
    if source_modulus <= 0 or D <= 0 or k_modulus <= 0 or excluded_modulus <= 0:
        failures.append({"reason": "nonpositive_guard_modulus"})
    else:
        branch_cong = ResidueClass(source_residue, source_modulus, source="branch_guard")
        parity_cong = ResidueClass(1, 2, source="parity_q_odd")
        k_cong = ResidueClass(source_residue + source_modulus * k_residue, source_modulus * k_modulus, source="k_divisibility")
        integrality_cong = impose_linear_congruence(residue=0, modulus=1, a=A, b=B, congruence_modulus=D)
        if integrality_cong is None:
            failures.append({"reason": "map_integrality_has_empty_solution"})
            integrality = ResidueClass(0, 1, source="map_integrality_empty")
        else:
            integrality = ResidueClass(integrality_cong[0], integrality_cong[1], source="map_integrality")
        for constraint in (branch_cong, parity_cong, k_cong, integrality):
            guard_rows.append(constraint.to_json())
            domain = intersect_congruence(domain, constraint) if domain is not None else None
        excluded = ResidueClass(
            source_residue + source_modulus * excluded_residue,
            source_modulus * excluded_modulus,
            kind="non_congruence",
            source="excluded_next_power",
        )
        domain = add_non_congruence(domain, excluded) if domain is not None else None
        if domain is not None:
            domain = GuardedDomain(domain.congruence, domain.non_congruences, max(domain.lower_bound, minimum_q), domain.guards)
        if domain is None:
            failures.append({"reason": "guarded_domain_empty"})
        elif domain.congruence.modulus != domain_modulus or domain.congruence.residue != domain_residue % domain_modulus:
            failures.append(
                {
                    "reason": "parent_map_domain_residue_mismatch",
                    "expected": {"residue": str(domain_residue % domain_modulus), "modulus": str(domain_modulus)},
                    "actual": domain.congruence.to_json(),
                }
            )
        elif (A * domain.congruence.residue + B) % D != 0 or (A * domain.congruence.modulus) % D != 0:
            failures.append({"reason": "map_integrality_not_proven_on_canonical_domain"})

    edge_id = str(edge_map.get("edge_id") or f"s4:{map_certificate.get('transition_certificate_id')}")
    affine = AffineMap(A, B, D)
    row = {
        "schema": "collatz_lab.guarded_edge_domain",
        "version": 1,
        "edge_id": edge_id,
        "source": str(edge_map.get("source") or f"P{map_certificate.get('source_parent')}"),
        "target": str(edge_map.get("target") or f"P{map_certificate.get('target_parent')}"),
        "transition_certificate_id": str(map_certificate.get("transition_certificate_id") or source_transition.get("transition_id", "")),
        "transition_certificate_hash": str(map_certificate.get("transition_certificate_hash") or source_transition.get("certificate_hash", "")),
        "parent_coordinate_map_certificate_hash": str(map_certificate.get("certificate_hash", "")),
        "affine_map": affine.to_json(),
        "guarded_domain": domain.to_json() if domain is not None else {},
        "guard_components": {
            "congruences": guard_rows,
            "non_congruences": [row.to_json() for row in (domain.non_congruences if domain else ())],
            "lower_bound": str(minimum_q),
            "parity": "q odd",
            "branch_guard": {
                "source_residue": str(source_residue),
                "source_modulus": str(source_modulus),
                "source_parent": str(branch["a"]),
            },
            "k_divisibility": {
                "k_residue": str(k_residue),
                "k_modulus": str(k_modulus),
            },
            "excluded_next_power": {
                "excluded_residue": str(excluded_residue),
                "excluded_modulus": str(excluded_modulus),
            },
            "map_integrality": {"A": str(A), "B": str(B), "D": str(D)},
            "valuation_exactness": {
                "valuation": str(valuation),
                "divisibility_modulus": str(k_modulus),
                "excluded_next_power_modulus": str(excluded_modulus),
            },
        },
        "replay_checks": {
            "parent_coordinate_map_certificate_replays": replay.accepted,
            "branch_guard_present": source_modulus > 0,
            "k_divisibility_present": k_modulus > 0,
            "excluded_next_power_present": excluded_modulus > 0,
            "map_integrality_present": D > 0,
            "valuation_exactness_present": valuation >= 0,
            "not_status_or_id_only": bool(source_transition and parent_map),
            "no_floats": not contains_float({"edge_map": edge_map, "map_certificate": map_certificate}),
        },
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
    row["guarded_domain_hash"] = stable_hash({key: value for key, value in row.items() if key != "guarded_domain_hash"})
    return row


def domain_from_json(payload: dict[str, Any]) -> GuardedDomain:
    canonical = payload.get("canonical_congruence") or (payload.get("congruences") or [{}])[0]
    non = payload.get("non_congruences") or []
    return GuardedDomain(
        ResidueClass(_as_int(canonical.get("residue"), "residue"), _as_int(canonical.get("modulus"), "modulus"), source=str(canonical.get("source", ""))),
        tuple(
            ResidueClass(
                _as_int(row.get("residue"), "non_congruence.residue"),
                _as_int(row.get("modulus"), "non_congruence.modulus"),
                kind="non_congruence",
                source=str(row.get("source", "")),
            )
            for row in non
        ),
        lower_bound=_as_int(payload.get("lower_bound", 1), "lower_bound"),
        guards=tuple(payload.get("guards") or ()),
    )


def affine_from_json(payload: dict[str, Any]) -> AffineMap:
    return AffineMap(_as_int(payload.get("A"), "A"), _as_int(payload.get("B"), "B"), _as_int(payload.get("D", 1), "D"))


def replay_guarded_edge_domain_row(row: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if contains_float(row):
        failures.append({"reason": "floating_point_guard_payload_rejected"})
    if row.get("schema") != "collatz_lab.guarded_edge_domain" or int(row.get("version", 0) or 0) != 1:
        failures.append({"reason": "unsupported_guarded_edge_domain_schema"})
    if str(row.get("guarded_domain_hash")) != stable_hash({key: value for key, value in row.items() if key != "guarded_domain_hash"}):
        failures.append({"reason": "guarded_edge_domain_hash_mismatch"})
    checks = row.get("replay_checks")
    required_checks = (
        "parent_coordinate_map_certificate_replays",
        "branch_guard_present",
        "k_divisibility_present",
        "excluded_next_power_present",
        "map_integrality_present",
        "valuation_exactness_present",
        "not_status_or_id_only",
        "no_floats",
    )
    if not isinstance(checks, dict) or not all(checks.get(key) is True for key in required_checks):
        failures.append({"reason": "guarded_edge_replay_checks_incomplete"})
    components = row.get("guard_components")
    if not isinstance(components, dict):
        failures.append({"reason": "missing_guard_components"})
    else:
        if not components.get("non_congruences") and not (row.get("guarded_domain") or {}).get("non_congruences"):
            failures.append({"reason": "missing_non_congruence_guard"})
        if not components.get("valuation_exactness"):
            failures.append({"reason": "missing_valuation_exactness_guard"})
    if row.get("status") != "PASS":
        failures.append({"reason": "guarded_edge_domain_status_not_pass", "status": row.get("status")})
    return {
        "accepted": not failures,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")

