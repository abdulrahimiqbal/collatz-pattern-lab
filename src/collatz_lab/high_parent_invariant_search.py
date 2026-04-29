"""RUN-068 high-parent root-relative invariant search.

The search in this module is proof-oriented bookkeeping, not a proof by
experiment.  It builds candidate invariants from the exact RUN-067 transition
families and accepts only candidates that the exact verifier can replay.
"""

from __future__ import annotations

from typing import Any

from .high_parent_invariant_verifier import (
    accepted_invariant_certificate,
    stable_hash,
    verify_high_parent_invariant,
)


RUN_ID = "RUN-068-high-parent-root-relative-invariant-search"
SCHEMA = "collatz_lab.run068_high_parent_invariant_search"


INVARIANT_TYPES = [
    "DIRECT_ROOT_DESCENT",
    "ROOT_DEBT_DECREASE",
    "ROOT_MARGIN_DECREASE",
    "LOWER_DEBT_ENTRY",
    "FINITE_SUBSYSTEM_ENTRY_WITH_ROOT_MARGIN",
    "BOUNDED_COMPOSITION_DESCENT",
    "V3_DEBT",
    "LEXICOGRAPHIC",
    "PIECEWISE_RESIDUE",
]


def _with_hash(row: dict[str, Any]) -> dict[str, Any]:
    row["candidate_hash"] = stable_hash({key: value for key, value in row.items() if key != "candidate_hash"})
    return row


def _classifications(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row.get("classification", {})
        for row in graph.get("transitions", [])
        if isinstance(row.get("classification", {}), dict)
    ]


def _full_domain_covered(graph: dict[str, Any]) -> bool:
    return bool(graph.get("transitions")) and not graph.get("uncovered_domains_from_run067")


def generate_candidate_invariants(graph: dict[str, Any], *, max_composition_depth: int = 4) -> list[dict[str, Any]]:
    """Generate exact invariant candidates from the reflected transition graph.

    Candidates are intentionally conservative.  Most current candidates are
    expected to fail; the value is in preserving the exact failed obligation for
    the next proof attempt.
    """

    classifications = _classifications(graph)
    full_domain_covered = _full_domain_covered(graph)
    all_direct = bool(classifications) and all(bool(row.get("descends_below_root")) for row in classifications)
    all_debt_decrease = bool(classifications) and all(bool(row.get("decreases_debt")) for row in classifications)
    any_finite_exit = any(bool(row.get("exits_to_finite_subsystem")) for row in classifications)
    all_finite_exits_have_margin = bool(classifications) and all(
        (not bool(row.get("exits_to_finite_subsystem"))) or bool(row.get("finite_subsystem_margin_available"))
        for row in classifications
    )
    residue_case_count = int(graph.get("transition_count", 0) or 0)
    shared = {
        "kind": "HIGH_PARENT_INVARIANT_CANDIDATE",
        "run_id": RUN_ID,
        "schema": SCHEMA,
        "version": 1,
        "claimed_domain": "d >= 1 and q > 0 and q % 2 = 1",
        "domain_coverage_proved": full_domain_covered,
        "integer_or_rational_arithmetic_only": True,
        "sample_only": False,
        "uses_float_or_log": False,
        "source_graph_hash": graph.get("graph_hash"),
        "transition_count": graph.get("transition_count", 0),
        "run067_uncovered_domain_count": len(graph.get("uncovered_domains_from_run067", [])),
    }
    candidates = [
        {
            **shared,
            "invariant_type": "DIRECT_ROOT_DESCENT",
            "candidate_id": "direct_root_descent_from_p32_special_families",
            "claim": "Every P32(3^d*q) special transition descends below root = 2^(32+d)*q - 1.",
            "exact_root_inequality_proved": all_direct,
            "required_inequality": "current_final < 2^(32+d)*q - 1",
        },
        {
            **shared,
            "invariant_type": "ROOT_DEBT_DECREASE",
            "candidate_id": "p32_special_transitions_decrease_debt",
            "claim": "Every exact P32 special transition maps debt d to d' < d.",
            "well_founded_measure": "Nat.debt",
            "all_transitions_decrease_debt": all_debt_decrease,
        },
        {
            **shared,
            "invariant_type": "ROOT_MARGIN_DECREASE",
            "candidate_id": "root_relative_rational_margin_decreases",
            "claim": "The rational current/root gain decreases under all P32 special transitions.",
            "well_founded_measure": "Nat.marginDeficit",
            "margin_representation": "integer pair comparisons, no logs",
            "all_transitions_decrease_margin": False,
            "missing_field": "exact composed gain comparison for every transition family",
        },
        {
            **shared,
            "invariant_type": "LOWER_DEBT_ENTRY",
            "candidate_id": "p32_special_enters_lower_debt_family",
            "claim": "Each transition enters an already certified high-parent family with lower debt.",
            "lower_debt_entry_proved": False,
            "known_lower_debt_certificate_count": 0,
        },
        {
            **shared,
            "invariant_type": "FINITE_SUBSYSTEM_ENTRY_WITH_ROOT_MARGIN",
            "candidate_id": "finite_subsystem_entry_has_root_margin",
            "claim": "Finite-subsystem exits have enough margin to descend below the original high-parent root.",
            "finite_subsystem_exit_present": any_finite_exit,
            "finite_margin_certificate_proved": any_finite_exit and all_finite_exits_have_margin,
        },
        {
            **shared,
            "invariant_type": "BOUNDED_COMPOSITION_DESCENT",
            "candidate_id": "bounded_composition_root_descent",
            "claim": "A bounded composition of P32 special families descends below the original root.",
            "composition_depth": max_composition_depth,
            "composition_descends_below_root": False,
            "composition_depths_attempted": list(range(2, max_composition_depth + 1)),
            "missing_field": "exact composition certificate over the full symbolic domain",
        },
        {
            **shared,
            "invariant_type": "V3_DEBT",
            "candidate_id": "v3_coordinate_debt_decreases",
            "claim": "v3(3^d*q) debt decreases or converts into exact root-relative shrink.",
            "all_transitions_decrease_v3_debt": False,
            "missing_field": "exact v3 target-coordinate theorem for all residue families",
        },
        {
            **shared,
            "invariant_type": "LEXICOGRAPHIC",
            "candidate_id": "lexicographic_debt_margin_parent_rank",
            "claim": "The tuple (d, margin_deficit, parent_rank, residue_rank) decreases lexicographically.",
            "lexicographic_components": ["debt", "margin_deficit", "parent_rank", "residue_rank"],
            "all_transitions_lexicographically_decrease": False,
            "missing_field": "case split proving lexicographic decrease under every family",
        },
        {
            **shared,
            "invariant_type": "PIECEWISE_RESIDUE",
            "candidate_id": "piecewise_residue_family_partition",
            "claim": "A residue split by q mod 2^k, d mod m, valuation h, and target parent b covers U.",
            "all_residue_cases_covered": full_domain_covered,
            "case_certificate_count": residue_case_count if full_domain_covered else 0,
            "missing_field": "unbounded h/b tail coverage and root-relative progress theorem",
        },
    ]
    return [_with_hash(candidate) for candidate in candidates]


def remaining_high_parent_domain(verifications: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "REMAINING_HIGH_PARENT_INVARIANT_DOMAIN",
        "domain_id": "high_parent_all_d_ge_1_q_odd_positive",
        "family_id": "odd_entry_parent_levels_ge_33",
        "d_range": {"type": "tail", "lower_bound": 1},
        "parent_level_range": {"type": "tail", "lower_bound": 33},
        "q_domain": "q > 0 and q % 2 = 1",
        "example": {"d": 1, "a": 33, "q": 1, "n_expr": "2^33 - 1"},
        "failure_reason": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING",
        "failed_invariant_classes": [
            {
                "invariant_type": row.get("invariant_type"),
                "candidate_id": row.get("candidate_id"),
                "reason": row.get("reason"),
                "detail": row.get("detail"),
            }
            for row in verifications
            if row.get("accepted") is not True
        ],
    }


def remaining_parent_family() -> dict[str, Any]:
    return {
        "kind": "UNCOVERED_PARENT_FAMILY",
        "family_id": "odd_entry_parent_levels_ge_33",
        "parent_level_range": {"type": "tail", "lower_bound": 33},
        "q_domain": "q > 0 and q % 2 = 1",
        "example": {"a": 33, "q": 1, "n_expr": "2^33 - 1"},
        "missing_transition_or_coverage_certificate": "no exact high-parent root-relative invariant certificate",
        "failure_reason": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING",
    }


def minimal_obstruction(
    *,
    graph: dict[str, Any],
    remaining_domains: list[dict[str, Any]],
    verifications: list[dict[str, Any]],
    max_representatives: int = 8,
) -> dict[str, Any]:
    failed_reasons = sorted({str(row.get("reason")) for row in verifications if row.get("accepted") is not True})
    representative = [
        {
            "transition_id": row.get("transition_id"),
            "domain_predicate": row.get("domain_predicate"),
            "classification": row.get("classification"),
            "root_relative_margin_at_min_debt": row.get("root_relative_margin_at_min_debt"),
        }
        for row in graph.get("transitions", [])[:max_representatives]
    ]
    obstruction = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING",
        "obstruction_id": "high_parent_d_ge_1_q_odd_root_relative_invariant",
        "exact_uncovered_domain": remaining_domains[0] if remaining_domains else None,
        "minimal_example": {"d": 1, "a": 33, "q": 1, "n": 2**33 - 1},
        "candidate_invariant_types_attempted": sorted(
            {str(row.get("invariant_type")) for row in verifications}
        ),
        "failed_reasons": failed_reasons,
        "new_invariant_needed": True,
        "representative_transition_families": representative,
        "why_no_progress_relation_was_certified": [
            "RUN-067 families derive exact P32 special transitions but include no root-relative progress family.",
            "Finite-subsystem exits still lack a certificate with margin below the original root 2^(32+d)*q - 1.",
            "No exact debt, margin, v3, lexicographic, residue, or bounded-composition measure was verified over the full domain.",
        ],
        "suggested_missing_invariant_fields": [
            "exact composed root-relative gain numerator/denominator for transition paths",
            "proof that unbounded h/b tails are covered by the same invariant",
            "target-coordinate v3 theorem for Q = 3^d*q",
            "well-founded measure whose decrease is proved by integer inequalities for every residue family",
        ],
    }
    obstruction["obstruction_hash"] = stable_hash(
        {key: value for key, value in obstruction.items() if key != "obstruction_hash"}
    )
    return obstruction


def run_high_parent_invariant_search(
    *,
    graph: dict[str, Any],
    max_composition_depth: int = 4,
    max_representatives: int = 8,
) -> dict[str, Any]:
    candidates = generate_candidate_invariants(graph, max_composition_depth=max_composition_depth)
    verifications = [verify_high_parent_invariant(candidate) for candidate in candidates]
    accepted = [
        cert
        for candidate, verification in zip(candidates, verifications, strict=True)
        if (cert := accepted_invariant_certificate(candidate, verification)) is not None
    ]
    success = bool(accepted)
    remaining_domains = [] if success else [remaining_high_parent_domain(verifications)]
    remaining_parent_families = [] if success else [remaining_parent_family()]
    obstruction = (
        {
            "schema": SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "status": "HIGH_PARENT_INVARIANT_CLOSED",
            "exact_uncovered_domain": None,
            "new_invariant_needed": False,
        }
        if success
        else minimal_obstruction(
            graph=graph,
            remaining_domains=remaining_domains,
            verifications=verifications,
            max_representatives=max_representatives,
        )
    )
    run_result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if success else "FAIL",
        "formalization_status": "HIGH_PARENT_INVARIANT_CLOSED"
        if success
        else "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING",
        "training_launched": False,
        "ml_hypothesis_generation_launched": False,
        "symbolic_search_launched": True,
        "root_relative_graph_status": graph.get("graph_status"),
        "transition_count": graph.get("transition_count", 0),
        "progress_transition_count": graph.get("progress_transition_count", 0),
        "candidate_invariant_count": len(candidates),
        "accepted_certificate_count": len(accepted),
        "remaining_uncovered_domain_count": len(remaining_domains),
        "remaining_uncovered_families": remaining_parent_families,
        "candidate_invariant_types_attempted": sorted({row["invariant_type"] for row in candidates}),
        "failed_reasons": sorted({str(row.get("reason")) for row in verifications if row.get("accepted") is not True}),
    }
    run_result["run_result_hash"] = stable_hash(
        {key: value for key, value in run_result.items() if key != "run_result_hash"}
    )
    return {
        "candidate_invariants": candidates,
        "verifications": verifications,
        "accepted_certificates": accepted,
        "remaining_uncovered_domains": remaining_domains,
        "remaining_uncovered_parent_families": remaining_parent_families,
        "minimal_obstruction": obstruction,
        "run_result": run_result,
    }
