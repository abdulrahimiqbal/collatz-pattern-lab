"""RUN-036 SCC ranking attempt using RUN-034 parent-coordinate maps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .proof_action_scc_ranking_cert import (
    RUN_ID as RUN033_ID,
    build_refined_scc_graph,
    check_affine_cycle_descent,
    derive_all_affine_edge_maps,
    extract_scc_internal_edges,
    load_jsonl,
    write_jsonl,
)
from .utils import load_yaml


RUN_ID = "RUN-036-exact-scc-ranking-with-parent-coordinate-maps"
DEFAULT_RUN030_DIR = Path("reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening")


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _cycle_key(edge_ids: list[str]) -> tuple[str, ...]:
    rotations = [tuple(edge_ids[index:] + edge_ids[:index]) for index in range(len(edge_ids))]
    return min(rotations)


def _enumerate_simple_cycles(edge_maps: list[dict[str, Any]], *, cap: int) -> tuple[list[list[dict[str, Any]]], bool]:
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edge_maps:
        adjacency.setdefault(str(edge["source"]), []).append(edge)
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

    for node in sorted(adjacency):
        dfs(node, node, [], {node})
        if capped:
            break
    return list(cycles.values()), capped


def _minimal_obstruction(
    *,
    states: list[str],
    edges: list[dict[str, Any]],
    cycle_obstructions: list[dict[str, Any]],
    cycle_cap_reached: bool,
) -> dict[str, Any]:
    return {
        "schema": "collatz_lab.run036_minimal_ranking_obstruction",
        "version": 1,
        "run_id": RUN_ID,
        "classification": "CYCLE_COMPOSITION_NOT_DESCENDING",
        "status": "CYCLE_COMPOSITION_NOT_DESCENDING",
        "unresolved_scc_states": states,
        "internal_edge_count": len(edges),
        "non_descending_cycle_count": len(cycle_obstructions),
        "cycle_enumeration_cap_reached": cycle_cap_reached,
        "representative_non_descending_cycles": cycle_obstructions[:20],
        "why_parent_level_ranking_fails": "RUN-032 already found no accepted parent-level/topological ranking; RUN-036 sees explicit cycles.",
        "why_affine_q_descent_fails": "At least one composed q-cycle has A >= D or fails A*q+B < D*q on the exact positive domain check used by this certificate language.",
        "why_lexicographic_ranking_fails": "No lexicographic affine certificate was synthesized; non-descending q-cycles require a stronger secondary invariant tied to exact cycle domains.",
        "refinement_status": "SOURCE_BRANCH_REFINEMENT_REQUIRED_FOR_CYCLE_DOMAIN_COMPATIBILITY",
        "exact_missing_invariant_type": "cycle-domain-compatible ranking over parent coordinate, valuation residue, or debt; simple q-affine cycle descent is insufficient",
    }


def run_scc_ranking_with_parent_maps(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("scc_ranking_with_maps_run036", {}) if isinstance(cfg.get("scc_ranking_with_maps_run036", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    run030_dir = Path(run_cfg.get("run030_dir") or DEFAULT_RUN030_DIR)
    unresolved_sccs = load_jsonl(run_cfg.get("unresolved_sccs") or run030_dir / "unresolved_sccs.jsonl")
    s4_rows = load_jsonl(run_cfg.get("parent_transition_certificates") or "certificate_store/run035_parent_transition_certificates.jsonl")
    extraction = extract_scc_internal_edges(unresolved_sccs, s4_rows)
    write_jsonl(out_dir / "scc_internal_edges.jsonl", extraction.edges)
    map_rows = derive_all_affine_edge_maps(extraction.edges)
    write_jsonl(out_dir / "scc_affine_edge_maps.jsonl", map_rows)
    passing_maps = [row for row in map_rows if row.get("status") == "PASS"]

    cycles_checked: list[dict[str, Any]] = []
    cycle_descent: list[dict[str, Any]] = []
    cycle_obstructions: list[dict[str, Any]] = []
    cycle_cap = int(run_cfg.get("cycle_cap", 20000))
    cycle_cap_reached = False
    classification = "MISSING_PARENT_COORDINATE_MAP"
    if extraction.failures:
        classification = "MISSING_PARENT_COORDINATE_MAP"
    elif len(passing_maps) == len(extraction.edges):
        cycles, cycle_cap_reached = _enumerate_simple_cycles(passing_maps, cap=cycle_cap)
        for cycle in cycles:
            replay = check_affine_cycle_descent(cycle, minimum_q=1)
            cycles_checked.append(replay)
            if replay.get("status") == "PASS":
                cycle_descent.append(replay)
            else:
                cycle_obstructions.append(replay)
        classification = "CYCLE_COMPOSITION_NOT_DESCENDING" if cycle_obstructions else "NEEDS_NEW_INVARIANT"

    write_jsonl(out_dir / "scc_cycles_checked.jsonl", cycles_checked)
    write_jsonl(out_dir / "scc_cycle_descent_certificates.jsonl", cycle_descent)
    write_jsonl(out_dir / "scc_cycle_obstructions.jsonl", cycle_obstructions)
    refined_graph = build_refined_scc_graph(extraction.edges)
    _write_json(refined_graph, out_dir / "refined_scc_graph.json")
    write_jsonl(out_dir / "refined_scc_edges.jsonl", list(refined_graph.get("edges") or []))
    _write_json(
        {
            "schema": "collatz_lab.run036_refinement_summary",
            "version": 1,
            "run_id": RUN_ID,
            "input_edge_count": len(extraction.edges),
            "refined_edge_count": len(refined_graph.get("edges") or []),
            "coverage_preserved": len(refined_graph.get("edges") or []) == len(extraction.edges),
            "status": "NOT_RANKED",
            "reason": "cycle-domain-compatible refinement/ranking invariant is still required",
        },
        out_dir / "refinement_summary.json",
    )

    states = list((unresolved_sccs[0] if unresolved_sccs else {}).get("nodes") or [])
    obstruction = _minimal_obstruction(
        states=states,
        edges=extraction.edges,
        cycle_obstructions=cycle_obstructions,
        cycle_cap_reached=cycle_cap_reached,
    )
    _write_json(obstruction, out_dir / "minimal_ranking_obstruction.json")
    _write_json(
        {
            "schema": "collatz_lab.scc_cycle_ranking_certificate",
            "version": 1,
            "run_id": RUN_ID,
            "certificate_id": "run036_scc_ranking_P12_P24_internal_s4",
            "type": "SCC_WELL_FOUNDED_RANKING_EXACT",
            "scc_id": (unresolved_sccs[0] if unresolved_sccs else {}).get("scc_id"),
            "states": states,
            "ranking_kind": "none",
            "status": "FAIL",
            "failure_classification": classification,
            "reason": obstruction["exact_missing_invariant_type"],
        },
        out_dir / "scc_ranking_certificate.json",
    )
    (out_dir / "refined_ranking_failure_report.md").write_text(
        "# RUN-036 Refined Ranking Failure\n\n"
        f"- classification: `{classification}`\n"
        f"- map replay: `{len(passing_maps)}/{len(extraction.edges)}`\n"
        f"- non-descending cycles recorded: `{len(cycle_obstructions)}`\n"
        f"- cycle cap reached: `{str(cycle_cap_reached).lower()}`\n\n"
        "A new exact invariant over cycle-compatible domains is required; the verifier was not relaxed.\n",
        encoding="utf-8",
    )
    result = {
        "schema": "collatz_lab.run036_exact_scc_ranking_with_parent_coordinate_maps",
        "version": 1,
        "run_id": RUN_ID,
        "source_run": RUN033_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "floating_point_certificate_used": False,
        "status": classification,
        "scc_internal_edge_count": len(extraction.edges),
        "affine_edge_map_pass": len(passing_maps),
        "affine_edge_map_fail": len(map_rows) - len(passing_maps),
        "cycles_checked": len(cycles_checked),
        "cycle_descent_pass": len(cycle_descent),
        "cycle_obstruction_count": len(cycle_obstructions),
        "cycle_enumeration_cap_reached": cycle_cap_reached,
        "unresolved_scc_count": 1 if classification != "PASS" else 0,
        "artifacts": {
            "scc_internal_edges": str(out_dir / "scc_internal_edges.jsonl"),
            "scc_affine_edge_maps": str(out_dir / "scc_affine_edge_maps.jsonl"),
            "scc_cycles_checked": str(out_dir / "scc_cycles_checked.jsonl"),
            "scc_cycle_descent_certificates": str(out_dir / "scc_cycle_descent_certificates.jsonl"),
            "scc_cycle_obstructions": str(out_dir / "scc_cycle_obstructions.jsonl"),
            "scc_ranking_certificate": str(out_dir / "scc_ranking_certificate.json"),
            "minimal_ranking_obstruction": str(out_dir / "minimal_ranking_obstruction.json"),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_scc_ranking_with_parent_maps(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
