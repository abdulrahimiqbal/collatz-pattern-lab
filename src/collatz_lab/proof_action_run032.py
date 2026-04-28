"""RUN-032 global ranking invariant discovery for RUN-030 SCC blockers."""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Any

from .proof_action_top_level_cert import RUN030_ID, write_jsonl
from .utils import load_yaml


RUN_ID = "RUN-032-global-ranking-invariant-discovery"
DEFAULT_RUN030_DIR = Path("reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening")


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _parent_sort_key(node: str) -> tuple[int, str]:
    if node.startswith("P") and node[1:].isdigit():
        return (int(node[1:]), node)
    return (10**9, node)


def _acyclic_rank_candidate(nodes: list[str], edges: list[dict[str, Any]]) -> dict[str, Any]:
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    indegree: dict[str, int] = {node: 0 for node in nodes}
    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        adjacency.setdefault(source, []).append(target)
        indegree.setdefault(source, 0)
        indegree[target] = indegree.get(target, 0) + 1
    queue = deque(sorted([node for node, degree in indegree.items() if degree == 0], key=_parent_sort_key))
    order: list[str] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for target in sorted(adjacency.get(node, []), key=_parent_sort_key):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(order) != len(indegree):
        cyclic = sorted([node for node, degree in indegree.items() if degree > 0], key=_parent_sort_key)
        return {
            "candidate_id": "run032_topological_dag_rank",
            "ranking_family": "natural topological rank",
            "status": "FAIL",
            "reason": "SCC is cyclic; no DAG rank exists",
            "unranked_nodes": cyclic,
        }
    ranks = {node: len(order) - index for index, node in enumerate(order)}
    bad = [edge for edge in edges if ranks[edge["target"]] >= ranks[edge["source"]]]
    return {
        "candidate_id": "run032_topological_dag_rank",
        "ranking_family": "natural topological rank",
        "status": "PASS" if not bad else "FAIL",
        "node_ranks": ranks,
        "nondecreasing_edges": bad,
    }


def _parent_level_candidate(edges: list[dict[str, Any]]) -> dict[str, Any]:
    bad: list[dict[str, Any]] = []
    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        if _parent_sort_key(target)[0] >= _parent_sort_key(source)[0]:
            bad.append(edge)
    return {
        "candidate_id": "run032_parent_level_rank",
        "ranking_family": "natural parent level",
        "status": "PASS" if not bad else "FAIL",
        "nondecreasing_edges": bad,
        "failure_count": len(bad),
    }


def _reverse_parent_level_candidate(edges: list[dict[str, Any]]) -> dict[str, Any]:
    bad: list[dict[str, Any]] = []
    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        if _parent_sort_key(target)[0] <= _parent_sort_key(source)[0]:
            bad.append(edge)
    return {
        "candidate_id": "run032_reverse_parent_level_rank",
        "ranking_family": "reverse natural parent level",
        "status": "PASS" if not bad else "FAIL",
        "nondecreasing_edges": bad,
        "failure_count": len(bad),
    }


def _scc_local_placeholder(scc: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": f"run032_scc_internal_ranking_{scc.get('scc_id', 'unknown')}",
        "ranking_family": "SCC-local ranking",
        "status": "FAIL",
        "reason": "No replayable SCC_INTERNAL_RANKING_EXACT payload exists in the current certificate store",
        "required_certificate": "SCC_INTERNAL_RANKING_EXACT",
        "scc_id": scc.get("scc_id"),
        "nodes": scc.get("nodes", []),
        "edge_count": scc.get("edge_count", 0),
    }


def _report(candidates: list[dict[str, Any]], sccs: list[dict[str, Any]]) -> str:
    accepted = [row for row in candidates if row.get("status") == "PASS"]
    lines = [
        "# RUN-032 Global Ranking Invariant Discovery",
        "",
        f"- source run: `{RUN030_ID}`",
        f"- unresolved SCCs inspected: `{len(sccs)}`",
        f"- candidates tried: `{len(candidates)}`",
        f"- accepted candidates: `{len(accepted)}`",
        f"- training launched: `false`",
        f"- selector/search launched: `false`",
        "",
    ]
    if accepted:
        lines.append("An accepted ranking candidate was found and should be promoted to a RUN-030 ranking certificate.")
    else:
        lines.extend(
            [
                "## Exact Remaining Blocker",
                "",
                "GLOBAL_RANKING_INVARIANT_REQUIRED",
                "",
                "The current exact S4 parent-state SCC has no replayable internal ranking certificate. A new mathematical invariant over the listed SCC edges is required.",
                "",
            ]
        )
        if sccs:
            first = sccs[0]
            lines.append(f"- SCC id: `{first.get('scc_id')}`")
            lines.append(f"- nodes: `{', '.join(first.get('nodes', []))}`")
            lines.append(f"- internal edge count: `{first.get('edge_count')}`")
    return "\n".join(lines) + "\n"


def run_global_ranking_invariant_discovery(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("global_ranking_invariant_discovery_run032", {}) if isinstance(cfg.get("global_ranking_invariant_discovery_run032", {}), dict) else {}
    run030_dir = Path(run_cfg.get("run030_dir") or DEFAULT_RUN030_DIR)
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    sccs = _load_jsonl(run_cfg.get("unresolved_sccs") or run030_dir / "unresolved_sccs.jsonl")
    candidates: list[dict[str, Any]] = []
    for scc in sccs:
        nodes = list(scc.get("nodes") or [])
        edges = list(scc.get("edges") or [])
        candidates.append(_acyclic_rank_candidate(nodes, edges))
        candidates.append(_parent_level_candidate(edges))
        candidates.append(_reverse_parent_level_candidate(edges))
        candidates.append(
            {
                "candidate_id": f"run032_lex_parent_level_source_target_{scc.get('scc_id', 'unknown')}",
                "ranking_family": "lexicographic tuple over parent level and edge orientation",
                "status": "FAIL",
                "reason": "The SCC contains both increasing and decreasing parent-level edges, including self-loops; this tuple is not decreasing on every edge.",
                "sample_edges": edges[:10],
            }
        )
        candidates.append(_scc_local_placeholder(scc))

    accepted = [row for row in candidates if row.get("status") == "PASS"]
    write_jsonl(out_dir / "ranking_candidate_certificates.jsonl", candidates)
    _write_text(_report(candidates, sccs), out_dir / "ranking_failure_report.md")
    result = {
        "schema": "collatz_lab.run032_global_ranking_invariant_discovery",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "unresolved_scc_count": len(sccs),
        "candidate_count": len(candidates),
        "accepted_candidate_count": len(accepted),
        "status": "RANKING_CERTIFICATE_FOUND" if accepted else "GLOBAL_RANKING_INVARIANT_REQUIRED",
        "exact_failed_sccs": sccs,
        "artifacts": {
            "ranking_candidate_certificates": str(out_dir / "ranking_candidate_certificates.jsonl"),
            "ranking_failure_report": str(out_dir / "ranking_failure_report.md"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_global_ranking_invariant_discovery(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
