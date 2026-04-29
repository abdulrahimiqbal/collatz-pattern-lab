"""RUN-056B global semantic map generation.

This pass audits the enriched semantic payloads against the global Lean
assumptions required by the reflected certified transition system.  It does not
weaken the verifier and it does not turn Python replay status into a theorem.
When a map is not theorem-grade, the generated artifact records the exact
missing payload instead of opening the corresponding Lean reflection gate.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Any

from .proof_action_semantic_payload_enrichment import (
    REPO_ROOT,
    read_json,
    read_jsonl,
    sha256_file,
    stable_hash,
    write_json,
)


RUN_ID = "RUN-056B-global-semantic-maps"
SCHEMA = "collatz_lab.run056b_global_semantic_maps"
MAP_SCHEMA = "collatz_lab.run056b_global_semantic_map"

ENTRY_KIND = "ENTRY_TO_CERTIFIED_NODE_MAP"
COVERAGE_KIND = "COVERAGE_DOMAIN_MEMBERSHIP_MAP"
NO_ESCAPE_KIND = "NO_ESCAPE_APPLICABLE_EDGE_MAP"
WELL_FOUNDED_KIND = "WELL_FOUNDED_KERNEL_TO_PATH_MAP"


def map_hash(payload: dict[str, Any]) -> str:
    return stable_hash({key: value for key, value in payload.items() if key != "global_semantic_map_hash"})


def attach_map_hash(payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    enriched["global_semantic_map_hash"] = map_hash(enriched)
    return enriched


def _parse_parent_level(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"P_?(\d+)$", str(value))
    if not match:
        return None
    return int(match.group(1))


def _node_levels_from_payloads(
    *,
    s3_roles: list[dict[str, Any]],
    s4_witnesses: list[dict[str, Any]],
) -> list[int]:
    levels: set[int] = set()
    for role in s3_roles:
        for key in ("source_node", "target_node"):
            level = _parse_parent_level(role.get(key))
            if level is not None and level > 0:
                levels.add(level)
    for witness in s4_witnesses:
        if witness.get("kind") != "S4_PARENT_TRANSITION_SEMANTIC_WITNESS":
            continue
        for key in ("source_parent", "target_parent"):
            try:
                level = int(witness.get(key, 0) or 0)
            except (TypeError, ValueError):
                level = 0
            if level > 0:
                levels.add(level)
    return sorted(levels)


def _s4_transition_witnesses(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("kind") == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"]


def _coverage_domains(coverage_map: dict[str, Any]) -> list[dict[str, Any]]:
    domains = coverage_map.get("parent_state_domains")
    return domains if isinstance(domains, list) else []


def _coverage_parent_states(coverage_map: dict[str, Any]) -> list[str]:
    return sorted({str(domain.get("parent_state", "")) for domain in _coverage_domains(coverage_map) if domain.get("parent_state")})


def _has_parametric_entry_payload(coverage_map: dict[str, Any]) -> bool:
    if isinstance(coverage_map.get("entry_to_certified_node_map"), dict):
        return True
    for domain in _coverage_domains(coverage_map):
        text = " ".join(str(domain.get(key, "")) for key in ("kind", "domain_id", "parent_state", "covered_predicate"))
        if "parametric" in text.lower() or "entry" in text.lower() and "map" in text.lower():
            return True
    return False


def _has_coverage_membership_theorem(coverage_map: dict[str, Any]) -> bool:
    theorem = coverage_map.get("coverage_domain_membership_theorem")
    if isinstance(theorem, dict):
        return bool(theorem.get("lean_statement") and theorem.get("cases"))
    return False


def _has_branch_partition_data(s6_trees: list[dict[str, Any]], no_escape_map: dict[str, Any] | None = None) -> bool:
    if isinstance(no_escape_map, dict) and no_escape_map.get("branch_partition"):
        return True
    for tree in s6_trees:
        blob = str(tree).lower()
        if "branch_partition" in blob or "source_domain" in blob or "applicable_edge" in blob:
            return True
    return False


def _semantic_validation(status: str, failures: list[dict[str, Any]]) -> dict[str, Any]:
    return {"status": status, "failures": failures}


def _failure(reason: str, **extra: Any) -> dict[str, Any]:
    return {"reason": reason, **{key: value for key, value in extra.items() if value is not None}}


def build_entry_map(
    *,
    coverage_map: dict[str, Any],
    node_levels: list[int],
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not node_levels:
        failures.append(_failure("ENTRY_CERTIFIED_NODE_SET_EMPTY"))
    if not _has_parametric_entry_payload(coverage_map):
        failures.append(
            _failure(
                "MISSING_PARAMETRIC_ENTRY_COVERAGE",
                detail=(
                    "odd entry uses a = v2(n+1), which is unbounded, but the payload "
                    "does not give a finite reduction or parametric certified-node map"
                ),
            )
        )
    status = "PASS" if not failures else "FAIL"
    return attach_map_hash(
        {
            "schema": MAP_SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": ENTRY_KIND,
            "statement": "Every n > 1 either descends immediately or enters a certified parent-state domain.",
            "even_case": "n even and n > 1 gives Collatz.C n = n / 2 < n",
            "odd_case": {
                "parent_level": "a = v2(n + 1)",
                "parent_coordinate": "q = (n + 1) / 2^a",
                "reconstruction": "n = 2^a * q - 1",
                "unbounded_parent_level": True,
            },
            "certified_node_model": {
                "node_levels": node_levels,
                "finite_node_count": len(node_levels),
                "minimum_node_level": min(node_levels) if node_levels else None,
                "maximum_node_level": max(node_levels) if node_levels else None,
                "coverage_parent_states": _coverage_parent_states(coverage_map),
            },
            "required_missing_payload": {
                "kind": "ENTRY_TO_CERTIFIED_NODE_MAP",
                "cases": [
                    "finite parent levels",
                    "parametric lift for parent levels above bound",
                    "residual or exception domains",
                ],
            },
            "theorem_target": "checkCertifiedEntryMap_sound",
            "semantic_validation": _semantic_validation(status, failures),
        }
    )


def build_coverage_membership_map(
    *,
    coverage_map: dict[str, Any],
    s4_witnesses: list[dict[str, Any]],
    node_levels: list[int],
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    domains = _coverage_domains(coverage_map)
    if not domains:
        failures.append(_failure("MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM", detail="coverage domain list is empty"))
    if not _has_coverage_membership_theorem(coverage_map):
        failures.append(
            _failure(
                "MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM",
                detail="payload lists domains but does not prove arbitrary entry/transition target membership in them",
            )
        )
    target_levels = sorted({int(row.get("target_parent", 0) or 0) for row in s4_witnesses if row.get("target_parent")})
    residual_domains = [domain for domain in domains if domain.get("residual_certificate_id")]
    universal_like = [
        domain
        for domain in domains
        if int(domain.get("modulus", 0) or 0) > 0
        and int(domain.get("residue_start", -1) or -1) == 0
        and int(domain.get("residue_end_exclusive", -1) or -1) == int(domain.get("modulus", 0) or 0)
    ]
    status = "PASS" if not failures else "FAIL"
    return attach_map_hash(
        {
            "schema": MAP_SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": COVERAGE_KIND,
            "statement": "Every entry domain and internal transition target is covered by a certified coverage domain.",
            "domain_summary": {
                "domain_count": len(domains),
                "parent_states": _coverage_parent_states(coverage_map),
                "universal_like_domain_count": len(universal_like),
                "residual_domain_count": len(residual_domains),
                "node_levels": node_levels,
                "transition_target_levels": target_levels,
            },
            "observed_limitation": (
                "RUN-051 coverage domains include structural residue intervals, but no Lean-checkable "
                "membership theorem mapping arbitrary entry levels and all transition targets into those domains."
            ),
            "theorem_target": "checkCertifiedCoverageMap_sound",
            "semantic_validation": _semantic_validation(status, failures),
        }
    )


def build_no_escape_map(
    *,
    s4_witnesses: list[dict[str, Any]],
    s6_trees: list[dict[str, Any]],
    node_levels: list[int],
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    source_levels = sorted({int(row.get("source_parent", 0) or 0) for row in s4_witnesses if row.get("source_parent")})
    target_levels = sorted({int(row.get("target_parent", 0) or 0) for row in s4_witnesses if row.get("target_parent")})
    missing_source_levels = sorted(set(node_levels) - set(source_levels))
    claim_counts = Counter(str(tree.get("semantic_claim_type", "")) for tree in s6_trees)
    if missing_source_levels:
        failures.append(
            _failure(
                "MISSING_APPLICABLE_EDGE_PARTITION",
                detail="some certified node levels have no reflected S4 outgoing transition source",
                missing_source_levels=missing_source_levels,
            )
        )
    if not _has_branch_partition_data(s6_trees):
        failures.append(
            _failure(
                "MISSING_APPLICABLE_EDGE_PARTITION",
                detail="S6 proof trees do not contain branch partition/sourceDomain witnesses for every covered state",
            )
        )
    status = "PASS" if not failures else "FAIL"
    return attach_map_hash(
        {
            "schema": MAP_SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": NO_ESCAPE_KIND,
            "statement": "Every covered nonterminal state has an applicable certified outgoing edge whose SourceDomain holds.",
            "edge_applicability_summary": {
                "certified_node_levels": node_levels,
                "s4_source_levels": source_levels,
                "s4_target_levels": target_levels,
                "node_levels_without_s4_source_edge": missing_source_levels,
                "s4_transition_count": len(s4_witnesses),
                "s6_claim_counts": dict(sorted(claim_counts.items())),
            },
            "required_missing_payload": {
                "kind": "APPLICABLE_EDGE_PARTITION",
                "fields": [
                    "covered-state case split",
                    "selected edge for each case",
                    "branch/domain congruence proof",
                    "map integrality proof",
                    "valuation exactness proof",
                    "SourceDomain proof",
                ],
            },
            "theorem_target": "checkCertifiedNoEscapeMap_sound",
            "semantic_validation": _semantic_validation(status, failures),
        }
    )


def build_well_founded_bridge(
    *,
    kernel_to_path_link: dict[str, Any],
    s3_roles: list[dict[str, Any]],
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    has_path_theorem = isinstance(kernel_to_path_link.get("infinite_path_to_kernel_theorem"), dict)
    has_rank_bridge = isinstance(kernel_to_path_link.get("well_founded_rank_bridge"), dict)
    if not has_path_theorem:
        failures.append(
            _failure(
                "MISSING_KERNEL_TO_PATH_LINK",
                detail="payload states the guarded-kernel link but does not give a formal infinite-path-to-kernel theorem",
            )
        )
    if not has_rank_bridge:
        failures.append(
            _failure(
                "MISSING_WELL_FOUNDED_RANK_BRIDGE",
                detail="current Lean WellFoundedSystem is rank-based, while the payload supplies a guarded-kernel story",
            )
        )
    role_counts = Counter(str(role.get("semantic_role", "")) for role in s3_roles)
    status = "PASS" if not failures else "FAIL"
    return attach_map_hash(
        {
            "schema": MAP_SCHEMA,
            "version": 1,
            "run_id": RUN_ID,
            "kind": WELL_FOUNDED_KIND,
            "statement": "No infinite internal natural path remains after guarded natural-kernel elimination.",
            "kernel_link_summary": {
                "kernel_certificate_id": kernel_to_path_link.get("kernel_certificate_id", ""),
                "scc_id": kernel_to_path_link.get("scc_id", ""),
                "fixed_point": kernel_to_path_link.get("kernel_fixed_point", {}),
                "divisibility_family": kernel_to_path_link.get("divisibility_family", {}),
                "conclusion": kernel_to_path_link.get("conclusion", ""),
            },
            "s3_role_counts": dict(sorted(role_counts.items())),
            "required_missing_payload": {
                "kind": "KERNEL_TO_PATH_FORMAL_BRIDGE",
                "fields": [
                    "infinite internal path predicate",
                    "map from every infinite path to surviving kernel membership",
                    "divisibility-by-all-powers conclusion",
                    "connection to WellFoundedSystem",
                ],
            },
            "theorem_target": "checkCertifiedWellFoundedBridge_sound",
            "semantic_validation": _semantic_validation(status, failures),
        }
    )


def build_global_semantic_maps(
    *,
    coverage_domain_map: dict[str, Any],
    s4_semantic_witnesses: list[dict[str, Any]],
    s6_proof_trees: list[dict[str, Any]],
    s3_semantic_roles: list[dict[str, Any]],
    kernel_to_path_link: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    s4_witnesses = _s4_transition_witnesses(s4_semantic_witnesses)
    node_levels = _node_levels_from_payloads(s3_roles=s3_semantic_roles, s4_witnesses=s4_witnesses)
    maps = {
        "entry_map": build_entry_map(coverage_map=coverage_domain_map, node_levels=node_levels),
        "coverage_map": build_coverage_membership_map(
            coverage_map=coverage_domain_map,
            s4_witnesses=s4_witnesses,
            node_levels=node_levels,
        ),
        "no_escape_map": build_no_escape_map(
            s4_witnesses=s4_witnesses,
            s6_trees=s6_proof_trees,
            node_levels=node_levels,
        ),
        "well_founded_bridge": build_well_founded_bridge(
            kernel_to_path_link=kernel_to_path_link,
            s3_roles=s3_semantic_roles,
        ),
    }
    failures: list[dict[str, Any]] = []
    for name, payload in maps.items():
        validation = payload.get("semantic_validation") if isinstance(payload.get("semantic_validation"), dict) else {}
        for failure in validation.get("failures") or []:
            failures.append({"map": name, **failure})
    return maps, failures


def validate_global_semantic_map_hash(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("global_semantic_map_hash") != map_hash(payload):
        return [{"reason": "global_semantic_map_hash_mismatch", "kind": payload.get("kind")}]
    return []


def replay_global_semantic_maps(maps: dict[str, dict[str, Any]]) -> dict[str, Any]:
    structural_failures: list[dict[str, Any]] = []
    semantic_failures: list[dict[str, Any]] = []
    expected = {
        "entry_map": ENTRY_KIND,
        "coverage_map": COVERAGE_KIND,
        "no_escape_map": NO_ESCAPE_KIND,
        "well_founded_bridge": WELL_FOUNDED_KIND,
    }
    for name, expected_kind in expected.items():
        payload = maps.get(name)
        if not isinstance(payload, dict):
            structural_failures.append({"reason": "missing_global_semantic_map", "map": name})
            continue
        if payload.get("schema") != MAP_SCHEMA or payload.get("kind") != expected_kind:
            structural_failures.append({"reason": "global_semantic_map_kind_mismatch", "map": name, "kind": payload.get("kind")})
        structural_failures.extend({"map": name, **failure} for failure in validate_global_semantic_map_hash(payload))
        validation = payload.get("semantic_validation") if isinstance(payload.get("semantic_validation"), dict) else {}
        failures = validation.get("failures") if isinstance(validation.get("failures"), list) else []
        if validation.get("status") != "PASS":
            semantic_failures.extend({"map": name, **failure} for failure in failures or [{"reason": "global_semantic_map_validation_failed"}])
        if validation.get("status") == "PASS" and failures:
            structural_failures.append({"reason": "passing_map_has_failures", "map": name})
        if not payload.get("statement") or not payload.get("theorem_target"):
            structural_failures.append({"reason": "status_only_global_semantic_map", "map": name})
    return {
        "status": "PASS" if not structural_failures and not semantic_failures else "FAIL",
        "accepted": not structural_failures and not semantic_failures,
        "well_formed": not structural_failures,
        "structural_failure_count": len(structural_failures),
        "semantic_failure_count": len(semantic_failures),
        "structural_failures": structural_failures,
        "semantic_failures": semantic_failures,
        "failures": structural_failures + semantic_failures,
    }


def first_status_for_failures(failures: list[dict[str, Any]]) -> str:
    reasons = [str(failure.get("reason", "")) for failure in failures]
    if "MISSING_PARAMETRIC_ENTRY_COVERAGE" in reasons:
        return "ENTRY_MAP_GAP"
    if "MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM" in reasons:
        return "COVERAGE_MAP_GAP"
    if "MISSING_APPLICABLE_EDGE_PARTITION" in reasons:
        return "NO_ESCAPE_MAP_GAP"
    if "MISSING_KERNEL_TO_PATH_LINK" in reasons or "MISSING_WELL_FOUNDED_RANK_BRIDGE" in reasons:
        return "WELL_FOUNDED_BRIDGE_GAP"
    return "FORMALIZATION_GAP"


__all__ = [
    "COVERAGE_KIND",
    "ENTRY_KIND",
    "MAP_SCHEMA",
    "NO_ESCAPE_KIND",
    "REPO_ROOT",
    "RUN_ID",
    "SCHEMA",
    "WELL_FOUNDED_KIND",
    "attach_map_hash",
    "build_global_semantic_maps",
    "first_status_for_failures",
    "map_hash",
    "read_json",
    "read_jsonl",
    "replay_global_semantic_maps",
    "sha256_file",
    "write_json",
]
