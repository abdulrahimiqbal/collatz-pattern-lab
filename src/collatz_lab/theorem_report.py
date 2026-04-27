"""Assemble theorem-shaped reports for the parent ``63 mod 64`` frontier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .residual_frontier import normalize_residue


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _default_paths(q_depth: int) -> dict[str, Path]:
    return {
        "residual_frontier": Path(f"reports/residual_frontier_63mod64_q{q_depth}.json"),
        "burst_families": Path("reports/burst_families_a6_a20.json"),
        "frontier_strata": Path(f"reports/frontier_strata_63mod64_q{q_depth}.json"),
        "return_maps": Path("reports/parent_return_maps_a6_a20_h1_h20.json"),
        "parent_graph": Path(f"reports/parent_transition_graph_q{q_depth}.json"),
        "cube_compression": Path(f"reports/cube_compression_q{q_depth}.json"),
        "signature_summary": Path(f"reports/signature_summary_residual_certified_q{q_depth}.json"),
        "potential": Path(f"reports/potential_parent_q{q_depth}.json"),
        "sharp_return": Path("reports/sharp_return_tower_q23.json"),
        "cycle_certificates": Path("reports/cycle_certificates_sharp_q23.json"),
        "cycle_mining": Path("reports/cycle_mining_parent_returns_q23.json"),
        "adic_basin": Path("reports/adic_basin_q23.json"),
        "cube_lift": Path("reports/P6_cube_lift_report.json"),
        "proof_obligations": Path("reports/proof_obligations_parent_P6.json"),
        "proof_policy": Path("reports/proof_policy_run_v2.json"),
        "parent_states": Path("reports/parent_states_a1_a20_samples.json"),
    }


def _known_infinite_families(burst: dict[str, Any] | None) -> list[dict[str, Any]]:
    if burst is None:
        return []
    families = []
    for row in burst.get("families", []):
        families.append(
            {
                "claim": row["symbolic_statement"],
                "status": row["status"],
                "a": row["a"],
                "q_residue": row["q_residue"],
                "q_depth": row["q_depth"],
                "descent_steps_standard": row["descent_steps_standard"],
            }
        )
    return families


def _remaining_hard_families(
    residual: dict[str, Any] | None,
    strata: dict[str, Any] | None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if strata is not None:
        for row in strata.get("top_unresolved_buckets", [])[:limit]:
            rows.append(
                {
                    "condition": f"v2(q)={row['t']} (a={row['a']}), h={row['h']}",
                    "count_unknown": row["count_unknown"],
                    "unknown_percent": row["unknown_percent"],
                    "status": "UNKNOWN",
                }
            )
    if rows:
        return rows
    if residual is None:
        return []
    for row in residual.get("unknown_q_mod_64", [])[:limit]:
        residue = normalize_residue(int(row["value"]), 6)
        rows.append(
            {
                "condition": f"q == {residue} mod 64",
                "count_unknown": row["count"],
                "status": "UNKNOWN",
            }
        )
    return rows


def build_theorem_candidate_report(q_depth: int, paths: dict[str, Path] | None = None) -> dict[str, Any]:
    paths = paths or _default_paths(q_depth)
    loaded = {name: _load_optional(path) for name, path in paths.items()}
    residual = loaded["residual_frontier"]
    burst = loaded["burst_families"]
    strata = loaded["frontier_strata"]
    returns = loaded["return_maps"]
    cubes = loaded["cube_compression"]
    signatures = loaded["signature_summary"]
    graph = loaded["parent_graph"]
    potential = loaded["potential"]
    sharp_return = loaded.get("sharp_return")
    cycle_certificates = loaded.get("cycle_certificates")
    cycle_mining = loaded.get("cycle_mining")
    adic_basin = loaded.get("adic_basin")
    cube_lift = loaded.get("cube_lift")
    proof_obligations = loaded.get("proof_obligations")
    proof_policy = loaded.get("proof_policy")
    parent_states = loaded.get("parent_states")

    return {
        "scope": "parent frontier n = 64*q - 1",
        "q_depth": q_depth,
        "claim_legend": {
            "PROVED_INFINITE_FAMILY": "symbolic integer proof for an infinite family",
            "VERIFIED_FINITE_DEPTH": "exhaustive verification at a fixed q-depth",
            "SAMPLED_SANITY_CHECK": "sampled check only",
            "NUMERIC_HEURISTIC": "numeric search or ranking scaffold",
            "UNKNOWN": "not certified by current artifacts",
        },
        "source_paths": {name: str(path) for name, path in paths.items()},
        "loaded_sources": {name: payload is not None for name, payload in loaded.items()},
        "residual_frontier_summary": None
        if residual is None
        else {
            key: residual.get(key)
            for key in [
                "total_q_classes",
                "existing_cube_covered_q_classes",
                "residual_certified_q_classes",
                "residual_unknown_q_classes",
                "total_certified_within_parent_percent",
                "unknown_within_parent_percent",
            ]
        }
        | {"status": "VERIFIED_FINITE_DEPTH"},
        "known_exact_infinite_families_discovered": _known_infinite_families(burst),
        "parent_return_maps": None
        if returns is None
        else {
            "map_count": returns.get("map_count"),
            "status": "PROVED_SYMBOLIC_CONGRUENCE",
            "source_condition_comparison": returns.get("source_condition_comparison"),
            "residual_image_projection_comparison": returns.get("residual_image_projection_comparison"),
        },
        "cube_compression": None
        if cubes is None
        else {
            name: {
                "raw_residue_count": row["raw_residue_count"],
                "cube_count": row["cube_count"],
                "compression_ratio_raw_to_cubes": row["compression_ratio_raw_to_cubes"],
                "top_conditions": row["top_conditions"][:10],
                "status": "VERIFIED_FINITE_DEPTH",
            }
            for name, row in cubes.get("sets", {}).items()
        },
        "signature_summary": None if signatures is None else {**signatures, "status": "VERIFIED_FINITE_DEPTH"},
        "parent_transition_graph": None
        if graph is None
        else {
            "node_count": graph.get("node_count"),
            "edge_count": graph.get("edge_count"),
            "largest_unresolved_scc_size": graph.get("largest_unresolved_scc_size"),
            "status": graph.get("claim_status", "VERIFIED_FINITE_DEPTH"),
        },
        "potential": None
        if potential is None
        else {
            "status": "NUMERIC_HEURISTIC",
            "found_potential": potential.get("found_potential"),
            "raw_status": potential.get("status"),
            "suggested_state_splits": potential.get("suggested_state_splits"),
        },
        "sharp_return_subsystem": None
        if sharp_return is None
        else {
            "status": sharp_return.get("status"),
            "R23": sharp_return.get("R23"),
            "height_identity": sharp_return.get("height_identity"),
            "tower": sharp_return.get("tower"),
            "potential": sharp_return.get("potential"),
            "q9_pullback_debt_example": sharp_return.get("q9_pullback_debt_example"),
        },
        "parent_state_sample": None
        if parent_states is None
        else {
            "status": parent_states.get("status"),
            "top_transition_counts": parent_states.get("transition_counts", [])[:20],
        },
        "cycle_certificates": None
        if cycle_certificates is None
        else {
            "claim_status": cycle_certificates.get("claim_status"),
            "certificates": cycle_certificates.get("certificates", []),
        },
        "cycle_mining": None
        if cycle_mining is None
        else {
            "claim_status": cycle_mining.get("claim_status"),
            "q_depth": cycle_mining.get("q_depth"),
            "overall_status_counts": cycle_mining.get("overall_status_counts"),
            "return_map_count_with_domain_at_depth": cycle_mining.get("return_map_count_with_domain_at_depth"),
            "sequence_reports": {
                key: {
                    "sequence_count": value.get("sequence_count"),
                    "status_counts": value.get("status_counts"),
                    "top_certified_by_coverage": value.get("top_certified_by_coverage", [])[:10],
                }
                for key, value in cycle_mining.get("sequence_reports", {}).items()
            },
        },
        "adic_basin": None
        if adic_basin is None
        else {
            "claim_status": adic_basin.get("claim_status"),
            "basins": adic_basin.get("basins", []),
        },
        "cube_lift": None
        if cube_lift is None
        else {
            "claim_status": cube_lift.get("claim_status"),
            "overall_infinite_lift_rate": cube_lift.get("overall_infinite_lift_rate"),
            "overall_status_counts": cube_lift.get("overall_status_counts"),
        },
        "proof_obligations": None
        if proof_obligations is None
        else {
            "proof_status": proof_obligations.get("proof_status"),
            "status_counts": proof_obligations.get("status_counts"),
            "open_obligation_count": proof_obligations.get("open_obligation_count"),
            "closed_obligation_count": proof_obligations.get("closed_obligation_count"),
        },
        "proof_policy": None
        if proof_policy is None
        else {
            "status": proof_policy.get("status"),
            "policy": proof_policy.get("policy"),
            "actions_tried": proof_policy.get("actions_tried"),
            "action_counts": proof_policy.get("action_counts"),
            "result_counts": proof_policy.get("result_counts"),
            "proof_status_counts": proof_policy.get("proof_status_counts"),
            "useful_action_rate": proof_policy.get("useful_action_rate"),
            "model_guided_obligation_closure_rate": proof_policy.get("model_guided_obligation_closure_rate"),
        },
        "remaining_hard_families": _remaining_hard_families(residual, strata),
        "remaining_sharp_recursive_states": []
        if strata is None
        else [
            {**row, "status": "UNKNOWN"}
            for row in strata.get("top_unresolved_recursive_states", [])[:40]
        ],
        "verifier_status": "THEOREM_CANDIDATE_NOT_COLLATZ_PROOF",
    }


def write_theorem_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Theorem Candidate: Parent `63 mod 64` Frontier",
        "",
        f"- q-depth: `{report['q_depth']}`",
        f"- verifier status: `{report['verifier_status']}`",
        "",
        "This is not a proof of Collatz. Infinite families are exact only where labeled `PROVED_INFINITE_FAMILY`; finite-depth verification is not universal proof; numeric potential search is not formal proof.",
        "",
        "## Residual Frontier",
        "",
        f"`{report['residual_frontier_summary']}`",
        "",
        "## Known Exact Infinite Families Discovered",
        "",
    ]
    for row in report["known_exact_infinite_families_discovered"][:30]:
        lines.append(f"- `{row['status']}`: {row['claim']}")
    return_maps = report["parent_return_maps"]
    if return_maps is not None:
        projection = return_maps.get("residual_image_projection_comparison") or {}
        lines.extend(
            [
                "",
                "## Parent Return Map Image Comparison",
                "",
                f"- return maps: `{return_maps.get('map_count')}`",
                f"- observed image classes: `{projection.get('observed_image_class_count')}`",
                f"- matched observed image classes: `{projection.get('matched_observed_image_class_count')}`",
                f"- unmatched observed image classes: `{projection.get('unmatched_observed_image_class_count')}`",
                f"- projected depth counts: `{projection.get('projected_depth_counts')}`",
                "",
            ]
        )
    sharp = report["sharp_return_subsystem"]
    if sharp is not None:
        tower = sharp["tower"]
        lines.extend(
            [
                "",
                "## Sharp Return Subsystem",
                "",
                f"- status: `{sharp['status']}`",
                f"- transition: `{sharp['R23']}`",
                f"- identity: `{sharp['height_identity']}`",
                f"- sharp branch count at q-depth `{tower['q_depth']}`: `{tower['sharp_branch_count']}`",
            ]
        )
        for row in tower["guaranteed_exit_counts"]:
            lines.append(f"- guaranteed exit after `{row['exit_after_returns']}` return(s): `{row['count']}`")
        lines.extend(
            [
                f"- needs deeper bits: `{tower['needs_deeper_bits']}`",
                f"- potential status: `{sharp['potential']['status']}`",
                f"- q9 pullback ancestor status: `{sharp['q9_pullback_debt_example']['status']}`",
                "",
            ]
        )
    parent_state = report["parent_state_sample"]
    if parent_state is not None:
        lines.extend(["", "## Parent-State Sample", "", f"`{parent_state['top_transition_counts'][:12]}`", ""])
    cycle_certificates = report["cycle_certificates"]
    if cycle_certificates is not None:
        lines.extend(["", "## Cycle Certificates", ""])
        for cert in cycle_certificates["certificates"][:10]:
            lines.append(
                f"- `{cert['status']}` for `{cert['map']['name']}` with height "
                f"`v2({cert['height']['linear_form']})`"
            )
    cycle_mining = report["cycle_mining"]
    if cycle_mining is not None:
        lines.extend(
            [
                "",
                "## Cycle Mining",
                "",
                f"- q-depth: `{cycle_mining['q_depth']}`",
                f"- return maps in depth: `{cycle_mining['return_map_count_with_domain_at_depth']}`",
                f"- status counts: `{cycle_mining['overall_status_counts']}`",
                "",
            ]
        )
        for name, section in cycle_mining["sequence_reports"].items():
            lines.append(f"- `{name}`: `{section['status_counts']}`")
    adic = report["adic_basin"]
    if adic is not None:
        lines.extend(["", "## 2-adic Basin Acceleration", ""])
        for basin in adic["basins"][:10]:
            lines.append(
                f"- `{basin['status']}` for `{basin['cycle_map']['name']}` "
                f"with height `v2({basin['height']['linear_form']})`"
            )
    cube_lift = report["cube_lift"]
    if cube_lift is not None:
        lines.extend(
            [
                "",
                "## Cube Infinite Lift",
                "",
                f"- infinite lift rate: `{cube_lift['overall_infinite_lift_rate']}`",
                f"- status counts: `{cube_lift['overall_status_counts']}`",
            ]
        )
    proof_obligations = report["proof_obligations"]
    if proof_obligations is not None:
        lines.extend(
            [
                "",
                "## Proof Obligations",
                "",
                f"- proof status: `{proof_obligations['proof_status']}`",
                f"- closed: `{proof_obligations['closed_obligation_count']}`",
                f"- open: `{proof_obligations['open_obligation_count']}`",
                f"- status counts: `{proof_obligations['status_counts']}`",
            ]
        )
    proof_policy = report["proof_policy"]
    if proof_policy is not None:
        lines.extend(
            [
                "",
                "## Proof Policy",
                "",
                f"- status: `{proof_policy['status']}`",
                f"- policy: `{proof_policy['policy']}`",
                f"- actions tried: `{proof_policy['actions_tried']}`",
                f"- action counts: `{proof_policy['action_counts']}`",
                f"- result counts: `{proof_policy['result_counts']}`",
                f"- proof status counts: `{proof_policy['proof_status_counts']}`",
                f"- useful action rate: `{proof_policy['useful_action_rate']}`",
                f"- model-guided obligation closure rate: `{proof_policy['model_guided_obligation_closure_rate']}`",
            ]
        )
    lines.extend(["", "## Remaining Hard Families", ""])
    for row in report["remaining_hard_families"][:30]:
        lines.append(f"- `{row['status']}`: {row['condition']} ({row.get('count_unknown')} unknown)")
    lines.extend(["", "## Sharp Recursive Unknown States", ""])
    for row in report["remaining_sharp_recursive_states"][:30]:
        lines.append(f"- `{row['status']}`: `{row['state_id']}` ({row['count_unknown']} unknown)")
    lines.extend(
        [
            "",
            "## Compression",
            "",
            f"`{report['cube_compression']}`",
            "",
            "## Potential",
            "",
            f"`{report['potential']}`",
            "",
        ]
    )
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assemble theorem-shaped parent frontier report.")
    parser.add_argument("--q-depth", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = build_theorem_candidate_report(args.q_depth)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_theorem_markdown(report, md_out)
    Console().print({"out": str(out), "known_families": len(report["known_exact_infinite_families_discovered"])})


if __name__ == "__main__":
    main()
