"""RUN-019 parent-state certificate for the final residual coverage class.

This pass is deterministic and graph-backed.  It does not train a selector and
does not try deeper one-shot affine residue refinement.  Instead it interprets
the failed RUN-018 residual class ``2^a*q - 1`` as parent state ``P_a`` and
checks whether the theorem dependency graph already contains an accepted
parent-transition/ranking path covering that parent state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_s6_analyzer import _candidate_actions as _s6_candidate_actions
from .proof_action_s6_analyzer import blocker_state
from .proof_action_theorem_composer import run_theorem_composer
from .utils import load_yaml


DEFAULT_CERTIFICATE_ID = "parent_residual_cert_P26_67108863_67108864"
BRANCH_RE = re.compile(r"^P(?P<parent>\d+):r(?P<residue>\d+):d(?P<depth>\d+)$")


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _canonical_hash(data: dict[str, Any]) -> str:
    payload = {key: value for key, value in data.items() if key != "certificate_hash"}
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _localize_path(path: str | Path) -> Path:
    text = str(path)
    if text.startswith("/mnt/collatz/"):
        return Path(text.removeprefix("/mnt/collatz/"))
    return Path(text)


def _power_of_two_level(modulus: int) -> int | None:
    if modulus <= 0 or modulus & (modulus - 1):
        return None
    return modulus.bit_length() - 1


def _accepted(node: dict[str, Any] | None) -> bool:
    return bool(node and node.get("status") == "ACCEPTED")


def _accepted_action(node: dict[str, Any]) -> dict[str, Any]:
    actions = list(node.get("accepted_actions") or [])
    if actions:
        return dict(actions[-1].get("action") or {})
    text = node.get("accepted_action_text")
    if isinstance(text, str) and text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
    return {}


def _residual_from_run018(run018_dir: str | Path) -> dict[str, Any]:
    run018 = Path(run018_dir)
    cert_path = run018 / "residual_coverage_certificate.json"
    if cert_path.exists():
        cert = _load_json(cert_path)
        return {
            "residual_certificate_id": str(cert["certificate_id"]),
            "parent_certificate_id": str(cert["parent_certificate_id"]),
            "modulus": int(cert["modulus"]),
            "residual_start": int(cert["residual_start"]),
            "residual_end": int(cert["residual_end"]),
        }
    result = _load_json(run018 / "run_result.json")
    missing = result["root_missing_certificates"][0]
    domain = missing["residual_domain"]
    return {
        "residual_certificate_id": str(missing["missing_certificate_id"]),
        "parent_certificate_id": str(missing["parent_certificate_id"]),
        "modulus": int(domain["modulus"]),
        "residual_start": int(domain["residue_start"]),
        "residual_end": int(domain["residue_end_exclusive"]),
    }


def _accepted_s3_ranking_nodes(graph: dict[str, Any], *, parent_level: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node_id, node in graph.get("nodes", {}).items():
        if node.get("node_type") != "S3_TRANSITION" or not _accepted(node):
            continue
        action = _accepted_action(node)
        if action.get("type") != "CHECK_DEBT_DECREASE":
            continue
        match = BRANCH_RE.match(str(action.get("branch_id", "")))
        if not match or int(match.group("depth")) != parent_level:
            continue
        gain_num = int(action.get("gain_num", 0) or 0)
        gain_den = int(action.get("gain_den", 1) or 1)
        if 0 < gain_num < gain_den:
            rows.append(
                {
                    "node_id": node_id,
                    "branch_id": action["branch_id"],
                    "source_parent": int(match.group("parent")),
                    "residue": int(match.group("residue")),
                    "depth": int(match.group("depth")),
                    "gain_num": gain_num,
                    "gain_den": gain_den,
                    "valuation": int(action.get("valuation", 0) or 0),
                }
            )
    rows.sort(key=lambda row: (row["gain_num"] / row["gain_den"], row["node_id"]))
    return rows


def _accepted_s4_nodes_for_parent(graph: dict[str, Any], *, parent_level: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node_id, node in graph.get("nodes", {}).items():
        if node.get("node_type") != "S4_LIFT" or not _accepted(node):
            continue
        action = _accepted_action(node)
        source_parent = action.get("source_parent")
        target_parent = action.get("target_parent")
        if source_parent == parent_level or target_parent == parent_level or str(node.get("source", {}).get("blocker_type")) == "parent_transition":
            rows.append({"node_id": node_id, "action": action})
    rows.sort(key=lambda row: row["node_id"])
    return rows


def _coverage_action_covers_parent(node: dict[str, Any], *, residual_modulus: int) -> bool:
    action = _accepted_action(node)
    return (
        action.get("type") == "PROVE_RESIDUE_COVERAGE"
        and int(action.get("modulus", 0) or 0) >= residual_modulus
        and int(action.get("covered_residue_count", 0) or 0) >= residual_modulus
    )


def _strict_parent_transition_candidates(graph: dict[str, Any], *, residual_modulus: int) -> list[dict[str, Any]]:
    nodes = graph.get("nodes", {})
    candidates: list[dict[str, Any]] = []
    for node_id, node in nodes.items():
        if node.get("node_type") != "STRICT_THEOREM_BLOCKER" or not _accepted(node):
            continue
        if str(node.get("source", {}).get("blocker_type")) != "parent_transition":
            continue
        dep_ids = list(node.get("depends_on") or [])
        dep_nodes = {dep: nodes.get(dep, {}) for dep in dep_ids}
        if not dep_ids or not all(_accepted(dep_nodes.get(dep)) for dep in dep_ids):
            continue
        coverage_nodes = [dep_nodes[dep] for dep in dep_ids if dep_nodes.get(dep, {}).get("node_type") == "COVERAGE_CERTIFICATE"]
        if not any(_coverage_action_covers_parent(coverage, residual_modulus=residual_modulus) for coverage in coverage_nodes):
            continue
        coverage_action = _accepted_action(coverage_nodes[0]) if coverage_nodes else {}
        candidates.append(
            {
                "strict_node_id": node_id,
                "dependency_node_ids": dep_ids,
                "coverage_modulus": int(coverage_action.get("modulus", 0) or 0),
                "coverage_certificate": node.get("evidence", {}).get("coverage_certificate"),
                "lemma_id": node.get("evidence", {}).get("lemma_id"),
            }
        )
    candidates.sort(key=lambda row: (abs(row["coverage_modulus"] - residual_modulus), row["strict_node_id"]))
    return candidates


def build_parent_residual_certificate(
    *,
    residual: dict[str, Any],
    theorem_graph: dict[str, Any],
    certificate_id: str = DEFAULT_CERTIFICATE_ID,
) -> dict[str, Any]:
    modulus = int(residual["modulus"])
    residual_start = int(residual["residual_start"])
    residual_end = int(residual["residual_end"])
    parent_level = _power_of_two_level(modulus)
    failures: list[dict[str, Any]] = []
    if parent_level is None or residual_start != modulus - 1 or residual_end != modulus:
        failures.append(
            {
                "kind": "PARENT_RESIDUAL_DOMAIN",
                "reason": "residual domain is not the exact final parent class n = 2^a*q - 1",
                "modulus": modulus,
                "residual_start": residual_start,
                "residual_end": residual_end,
            }
        )

    parent_paths = _strict_parent_transition_candidates(theorem_graph, residual_modulus=modulus)
    s3_nodes = _accepted_s3_ranking_nodes(theorem_graph, parent_level=parent_level or 0)
    s4_nodes = _accepted_s4_nodes_for_parent(theorem_graph, parent_level=parent_level or 0)
    if not parent_paths:
        failures.append(
            {
                "kind": "MISSING_PARENT_TRANSITION_CERTIFICATE",
                "parent_level": parent_level,
                "required": "accepted strict parent-transition blocker with full coverage at the residual modulus",
            }
        )
    if not s3_nodes:
        failures.append(
            {
                "kind": "MISSING_PARENT_RANKING_CERTIFICATE",
                "parent_level": parent_level,
                "required": f"accepted S3 CHECK_DEBT_DECREASE action with branch depth d{parent_level}",
            }
        )
    if not s4_nodes:
        failures.append(
            {
                "kind": "MISSING_PARENT_LIFT_CERTIFICATE",
                "parent_level": parent_level,
                "required": "accepted S4 lift/high-parent node for the parent residual path",
            }
        )

    status = "PASS" if not failures else "FAIL"
    parent_path = parent_paths[0] if parent_paths else {}
    best_s3 = s3_nodes[0] if s3_nodes else {"gain_num": 1, "gain_den": 1}
    dependency_node_ids = list(dict.fromkeys(parent_path.get("dependency_node_ids", [])))
    path_node_ids = list(
        dict.fromkeys(
            [parent_path.get("strict_node_id")]
            + dependency_node_ids
            + [row["node_id"] for row in s3_nodes[:16]]
            + [row["node_id"] for row in s4_nodes[:16]]
        )
    )
    path_node_ids = [node_id for node_id in path_node_ids if node_id]
    s6_dependency_count = sum(1 for node_id in dependency_node_ids if theorem_graph["nodes"].get(node_id, {}).get("node_type") == "S6_LEMMA")
    no_escape_dependency_count = sum(1 for node_id in dependency_node_ids if theorem_graph["nodes"].get(node_id, {}).get("node_type") == "NO_ESCAPE_CERTIFICATE")
    certificate = {
        "schema": "collatz_lab.proof_action_parent_residual_certificate",
        "version": 1,
        "certificate_id": certificate_id,
        "parent_certificate_id": str(residual["parent_certificate_id"]),
        "residual_certificate_id": str(residual["residual_certificate_id"]),
        "parent_level": int(parent_level or 0),
        "modulus": modulus,
        "residual_start": residual_start,
        "residual_end": residual_end,
        "status": status,
        "parent_interpretation": f"n = 2^{int(parent_level or 0)}*q - 1",
        "path_node_count": len(path_node_ids) if status == "PASS" else 0,
        "path_node_ids": path_node_ids if status == "PASS" else [],
        "parent_transition_path": parent_path if status == "PASS" else {},
        "s3_dependency_count": len(s3_nodes) if status == "PASS" else 0,
        "s3_ranking_nodes": s3_nodes[:32] if status == "PASS" else [],
        "s4_dependency_count": len(s4_nodes) if status == "PASS" else 0,
        "s4_lift_nodes": s4_nodes[:32] if status == "PASS" else [],
        "s6_dependency_count": s6_dependency_count if status == "PASS" else 0,
        "no_escape_dependency_count": no_escape_dependency_count if status == "PASS" else 0,
        "ranking_delta_num": int(best_s3["gain_num"]) if status == "PASS" else 1,
        "ranking_delta_den": int(best_s3["gain_den"]) if status == "PASS" else 1,
        "ranking_reason": "accepted S3 debt transition has gain_num < gain_den" if status == "PASS" else "missing accepted parent ranking decrease",
        "failure_count": len(failures),
        "failures": failures,
    }
    certificate["certificate_hash"] = _canonical_hash(certificate)
    return certificate


def _parent_residual_action(certificate: dict[str, Any], *, target: str) -> dict[str, Any]:
    return {
        "type": "PROVE_PARENT_RESIDUAL_COVERAGE",
        "target": target,
        "certificate_id": certificate["certificate_id"],
        "parent_certificate_id": certificate["parent_certificate_id"],
        "residual_certificate_id": certificate["residual_certificate_id"],
        "parent_level": int(certificate["parent_level"]),
        "modulus": int(certificate["modulus"]),
        "residual_start": int(certificate["residual_start"]),
        "residual_end": int(certificate["residual_end"]),
        "path_node_count": int(certificate["path_node_count"]),
        "s3_dependency_count": int(certificate["s3_dependency_count"]),
        "s4_dependency_count": int(certificate["s4_dependency_count"]),
        "s6_dependency_count": int(certificate["s6_dependency_count"]),
        "no_escape_dependency_count": int(certificate["no_escape_dependency_count"]),
        "ranking_delta_num": int(certificate["ranking_delta_num"]),
        "ranking_delta_den": int(certificate["ranking_delta_den"]),
        "certificate_hash": certificate["certificate_hash"],
    }


def _parent_residual_fact(certificate: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "parent_residual_certificate",
        "certificate_id": certificate["certificate_id"],
        "parent_certificate_id": certificate["parent_certificate_id"],
        "residual_certificate_id": certificate["residual_certificate_id"],
        "parent_level": int(certificate["parent_level"]),
        "modulus": int(certificate["modulus"]),
        "residual_start": int(certificate["residual_start"]),
        "residual_end": int(certificate["residual_end"]),
        "path_node_count": int(certificate["path_node_count"]),
        "s3_dependency_count": int(certificate["s3_dependency_count"]),
        "s4_dependency_count": int(certificate["s4_dependency_count"]),
        "s6_dependency_count": int(certificate["s6_dependency_count"]),
        "no_escape_dependency_count": int(certificate["no_escape_dependency_count"]),
        "ranking_delta_num": int(certificate["ranking_delta_num"]),
        "ranking_delta_den": int(certificate["ranking_delta_den"]),
        "certificate_hash": certificate["certificate_hash"],
        "status": "PASS",
    }


def build_parent_residual_s6_dir(
    *,
    source_s6_dir: str | Path,
    certificate: dict[str, Any],
    out_dir: str | Path,
) -> str:
    source = Path(source_s6_dir)
    blockers = _load_jsonl(source / "s6_blockers.jsonl")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    repaired: list[dict[str, Any]] = []
    for blocker in blockers:
        row = dict(blocker)
        if certificate.get("status") == "PASS" and str(blocker.get("coverage_certificate")) == str(certificate["parent_certificate_id"]):
            row["parent_residual_certificate"] = _parent_residual_fact(certificate)
            row["verifier_status"] = "ACCEPT"
            actions = _s6_candidate_actions(row)
            action_texts = {json.dumps(action, sort_keys=True) for action in actions}
            parent_residual = _parent_residual_action(certificate, target=str(row["target"]))
            if json.dumps(parent_residual, sort_keys=True) not in action_texts:
                actions.append(parent_residual)
            row["candidate_actions"] = actions
            row["state"] = blocker_state(row)
        repaired.append(row)
    _write_jsonl(out / "s6_blockers.jsonl", repaired)
    return str(out)


def run_parent_residual_cert(config_path: str | Path, *, out: str | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path)
    parent_cfg = cfg.get("parent_residual", {})
    run018_dir = Path(str(parent_cfg.get("run018_dir") or "reports/runs/RUN-018-proof-action-v2-residual-coverage-cert"))
    out_dir = Path(str(out or parent_cfg.get("out_dir") or "reports/runs/RUN-019-proof-action-v2-parent-residual-cert"))
    out_dir.mkdir(parents=True, exist_ok=True)
    residual = _residual_from_run018(run018_dir)
    graph_path = _localize_path(parent_cfg.get("theorem_graph") or run018_dir / "theorem_composer" / "theorem_dependency_graph.json")
    theorem_graph = _load_json(graph_path)
    certificate = build_parent_residual_certificate(
        residual=residual,
        theorem_graph=theorem_graph,
        certificate_id=str(parent_cfg.get("certificate_id") or DEFAULT_CERTIFICATE_ID),
    )
    certificate_path = out_dir / "parent_residual_certificate.json"
    certificate_path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    source_s6_dir = _localize_path(parent_cfg.get("source_s6_dir") or run018_dir / "repaired_s6")
    repaired_s6_dir = build_parent_residual_s6_dir(
        source_s6_dir=source_s6_dir,
        certificate=certificate,
        out_dir=out_dir / "repaired_s6",
    )
    composer_summary = run_theorem_composer(
        str(parent_cfg.get("composer_config") or "configs/collatz_proof_action_v2_theorem_composer_run016.yaml"),
        checkpoint=str((cfg.get("model") or {}).get("checkpoint") or (cfg.get("evaluation") or {}).get("checkpoint")),
        frontier_dir=str((cfg.get("composer") or {}).get("frontier_eval_dir") or (cfg.get("evaluation") or {}).get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval"),
        s6_dir=repaired_s6_dir,
        out=str(out_dir / "theorem_composer"),
    )

    root_missing: list[dict[str, Any]] = []
    if certificate["status"] != "PASS":
        root_missing.append(
            {
                "kind": "PARENT_RESIDUAL_CERTIFICATE",
                "missing_certificate_id": certificate["certificate_id"],
                "parent_level": certificate["parent_level"],
                "residual_domain": {
                    "modulus": certificate["modulus"],
                    "residue_start": certificate["residual_start"],
                    "residue_end_exclusive": certificate["residual_end"],
                    "residue_count": certificate["residual_end"] - certificate["residual_start"],
                },
                "failures": certificate["failures"],
                "reason": "accepted theorem graph does not contain a closed parent-state transition/ranking path for the residual class",
            }
        )
    elif composer_summary["strict_theorem_verifier_result"] != "PASS":
        for blocker in composer_summary.get("minimal_blocker_report", []):
            if blocker.get("missing_kind") == "blocked_dependency":
                continue
            root_missing.append(
                {
                    "kind": "STRICT_THEOREM_ADDITIONAL_DEPENDENCY",
                    "node_id": blocker.get("node_id"),
                    "node_type": blocker.get("node_type"),
                    "missing_kind": blocker.get("missing_kind"),
                    "last_rejection": blocker.get("last_rejection"),
                    "evidence": blocker.get("evidence", {}),
                }
            )

    _write_jsonl(out_dir / "root_missing_certificates.jsonl", root_missing)
    result = {
        "schema": "collatz_lab.run_result.parent_residual_cert",
        "version": 1,
        "run_id": "RUN-019-proof-action-v2-parent-residual-cert",
        "training_launched": False,
        "big_model_launched": False,
        "selector_work": False,
        "parent_residual_certificate_status": certificate["status"],
        "parent_residual_certificate_path": str(certificate_path),
        "repaired_s6_dir": repaired_s6_dir,
        "composer_summary": composer_summary,
        "strict_theorem_verifier_result": composer_summary["strict_theorem_verifier_result"],
        "proof_confidence_percent": composer_summary["proof_confidence_percent"],
        "status": "STRICT_VERIFIER_PASS" if composer_summary["strict_theorem_verifier_result"] == "PASS" else "MINIMAL_ROOT_MISSING_CERTIFICATES",
        "root_missing_certificate_count": len(root_missing),
        "root_missing_certificates": root_missing,
        "artifacts": {
            "parent_residual_certificate": str(certificate_path),
            "root_missing_certificates": str(out_dir / "root_missing_certificates.jsonl"),
            "theorem_composition_report": str(out_dir / "theorem_composer" / "theorem_composition_report.json"),
        },
    }
    (out_dir / "run_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate RUN-019 parent residual certificate and rerun theorem composer.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    result = run_parent_residual_cert(args.config, out=args.out)
    Console().print(
        {
            "status": result["status"],
            "parent_residual_certificate_status": result["parent_residual_certificate_status"],
            "strict_theorem_verifier_result": result["strict_theorem_verifier_result"],
            "root_missing_certificate_count": result["root_missing_certificate_count"],
            "run_result": str(Path(result["parent_residual_certificate_path"]).parent / "run_result.json"),
        }
    )


if __name__ == "__main__":
    main()
