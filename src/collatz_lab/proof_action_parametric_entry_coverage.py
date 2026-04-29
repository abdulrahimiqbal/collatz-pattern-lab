"""RUN-057 parametric entry coverage taxonomy.

This pass checks whether the final coverage artifacts prove universal entry for
odd inputs.  It classifies the reflected parent levels and reports the exact
uncovered parent families when no parametric coverage theorem is present.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


RUN_ID = "RUN-057-parametric-entry-coverage-theorem"
SCHEMA = "collatz_lab.run057_parametric_entry_coverage"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(data: Any, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parent_level(value: Any) -> int | None:
    match = re.search(r"P_?(\d+)$", str(value or ""))
    return int(match.group(1)) if match else None


def _s4_witnesses(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("kind") == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"]


def _node_levels(*, s3_roles: list[dict[str, Any]], s4_witnesses: list[dict[str, Any]]) -> list[int]:
    levels: set[int] = set()
    for role in s3_roles:
        for key in ("source_node", "target_node"):
            level = _parent_level(role.get(key))
            if level is not None and level > 0:
                levels.add(level)
    for row in s4_witnesses:
        for key in ("source_parent", "target_parent"):
            try:
                level = int(row.get(key, 0) or 0)
            except (TypeError, ValueError):
                level = 0
            if level > 0:
                levels.add(level)
    return sorted(levels)


def _domains(coverage_map: dict[str, Any]) -> list[dict[str, Any]]:
    domains = coverage_map.get("parent_state_domains")
    return domains if isinstance(domains, list) else []


def _has_parametric_family(coverage_map: dict[str, Any], top_rows: list[dict[str, Any]], s6_trees: list[dict[str, Any]]) -> bool:
    blobs = [json.dumps(coverage_map, sort_keys=True), json.dumps(top_rows, sort_keys=True), json.dumps(s6_trees, sort_keys=True)]
    text = "\n".join(blobs).lower()
    markers = [
        "parametric_entry_coverage",
        "entry_to_certified_node_map",
        "parent levels above",
        "all parent levels",
        "a >= 33",
    ]
    return any(marker in text for marker in markers)


def _has_immediate_descent_odd_family(top_rows: list[dict[str, Any]]) -> bool:
    text = json.dumps(top_rows, sort_keys=True).lower()
    return "odd" in text and "immediate descent" in text and "parent" in text


def _coverage_domains_by_parent(coverage_map: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for domain in _domains(coverage_map):
        parent = str(domain.get("parent_state", ""))
        counts[parent] = counts.get(parent, 0) + 1
    return dict(sorted(counts.items()))


def _uncovered_families(
    *,
    finite_levels: list[int],
    has_parametric_family: bool,
    has_immediate_descent_odd_family: bool,
) -> list[dict[str, Any]]:
    uncovered: list[dict[str, Any]] = []
    if 1 not in finite_levels and not has_immediate_descent_odd_family:
        uncovered.append(
            {
                "kind": "UNCOVERED_PARENT_FAMILY",
                "family_id": "odd_entry_parent_level_1",
                "parent_level_range": {"type": "singleton", "level": 1},
                "q_domain": "q > 0 and q % 2 = 1",
                "example": {"a": 1, "q": 3, "n": 5},
                "missing_transition_or_coverage_certificate": "no generated P1 node/domain and no odd immediate-descent certificate",
                "failure_reason": "MISSING_PARAMETRIC_ENTRY_COVERAGE",
            }
        )
    if finite_levels and not has_parametric_family:
        upper = max(finite_levels)
        uncovered.append(
            {
                "kind": "UNCOVERED_PARENT_FAMILY",
                "family_id": f"odd_entry_parent_levels_ge_{upper + 1}",
                "parent_level_range": {"type": "tail", "lower_bound": upper + 1},
                "q_domain": "q > 0 and q % 2 = 1",
                "example": {"a": upper + 1, "q": 1, "n_expr": f"2^{upper + 1} - 1"},
                "missing_transition_or_coverage_certificate": "no parametric lift/high-parent coverage family into the finite certified node range",
                "failure_reason": "MISSING_PARAMETRIC_ENTRY_COVERAGE",
            }
        )
    return uncovered


def build_parent_level_coverage_taxonomy(
    *,
    coverage_map: dict[str, Any],
    s4_semantic_witnesses: list[dict[str, Any]],
    s3_semantic_roles: list[dict[str, Any]],
    s6_proof_trees: list[dict[str, Any]],
    top_level_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    s4_rows = _s4_witnesses(s4_semantic_witnesses)
    finite_levels = _node_levels(s3_roles=s3_semantic_roles, s4_witnesses=s4_rows)
    s4_source_levels = sorted({int(row.get("source_parent", 0) or 0) for row in s4_rows if row.get("source_parent")})
    s4_target_levels = sorted({int(row.get("target_parent", 0) or 0) for row in s4_rows if row.get("target_parent")})
    residual_levels = sorted(
        {
            int(domain.get("parent_state", "P_0").split("_")[-1])
            for domain in _domains(coverage_map)
            if str(domain.get("parent_state", "")).startswith("P_") and str(domain.get("parent_state", "")).split("_")[-1].isdigit()
        }
    )
    has_parametric = _has_parametric_family(coverage_map, top_level_rows, s6_proof_trees)
    has_odd_immediate = _has_immediate_descent_odd_family(top_level_rows)
    uncovered = _uncovered_families(
        finite_levels=finite_levels,
        has_parametric_family=has_parametric,
        has_immediate_descent_odd_family=has_odd_immediate,
    )
    status = "PASS" if not uncovered else "FAIL"
    taxonomy = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": status,
        "failure_reason": None if status == "PASS" else "MISSING_PARAMETRIC_ENTRY_COVERAGE",
        "entry_parent_decomposition": {
            "odd_n_gt_one": "a = v2(n + 1), q = (n + 1) / 2^a, n = 2^a*q - 1",
            "parent_level_range": "a >= 1 and unbounded",
            "q_domain": "q > 0 and q % 2 = 1",
        },
        "coverage_taxonomy": [
            {
                "category": "COVERED_FINITE_PARENT_LEVEL",
                "parent_levels": finite_levels,
                "coverage_domains_by_parent": _coverage_domains_by_parent(coverage_map),
                "supported": bool(finite_levels),
            },
            {
                "category": "COVERED_PARAMETRIC_PARENT_FAMILY",
                "families": [] if not has_parametric else ["artifact-declared-parametric-family"],
                "supported": has_parametric,
            },
            {
                "category": "IMMEDIATE_DESCENT_PARENT_FAMILY",
                "families": [] if not has_odd_immediate else ["artifact-declared-odd-immediate-descent-family"],
                "supported": has_odd_immediate,
            },
            {
                "category": "TRANSITIONS_INTO_CERTIFIED_RANGE",
                "source_parent_levels": s4_source_levels,
                "target_parent_levels": s4_target_levels,
                "transition_count": len(s4_rows),
                "supported": bool(s4_rows),
            },
            {
                "category": "UNCOVERED_PARENT_FAMILY",
                "families": uncovered,
                "supported": not uncovered,
            },
        ],
        "finite_parent_levels": finite_levels,
        "s4_source_parent_levels": s4_source_levels,
        "s4_target_parent_levels": s4_target_levels,
        "residual_parent_levels": residual_levels,
        "coverage_domain_count": len(_domains(coverage_map)),
        "universal_entry_coverage_supported": not uncovered,
        "uncovered_family_count": len(uncovered),
        "taxonomy_hash": "",
    }
    taxonomy["taxonomy_hash"] = stable_hash({key: value for key, value in taxonomy.items() if key != "taxonomy_hash"})
    return taxonomy, uncovered


__all__ = [
    "REPO_ROOT",
    "RUN_ID",
    "SCHEMA",
    "build_parent_level_coverage_taxonomy",
    "read_json",
    "read_jsonl",
    "sha256_file",
    "write_json",
    "write_jsonl",
]
