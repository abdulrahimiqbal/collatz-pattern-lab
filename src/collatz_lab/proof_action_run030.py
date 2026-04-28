"""RUN-030 top-level theorem certificates after S3/S6 hardening."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_top_level_cert import (
    RUN030_ID,
    attach_top_level_certificates,
    build_replay_context,
    build_top_level_certificates_after_hardening,
    replay_top_level_certificates,
    write_jsonl,
)
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = RUN030_ID
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = Path("proof_manifest.json")
DEFAULT_PARENT_RESIDUAL = Path("certificate_store/run019_parent_residual_certificate.json")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


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


def _artifact_entry(name: str, path: Path, manifest_dir: Path) -> dict[str, Any]:
    return {"name": name, "path": str(path.relative_to(manifest_dir)), "sha256": _sha256(path)}


def _source_entry(path: Path) -> dict[str, Any]:
    return {"name": str(path.relative_to(REPO_ROOT)), "path": str(path.relative_to(REPO_ROOT)), "sha256": _sha256(path)}


def _resolve_manifest_artifact(manifest: dict[str, Any], name: str, *, manifest_path: Path) -> Path:
    manifest_dir = manifest_path.parent
    for entry in manifest.get("artifacts", []):
        if entry.get("name") == name:
            raw = Path(str(entry["path"]))
            if raw.is_absolute():
                return raw
            candidate = manifest_dir / raw
            if candidate.exists():
                return candidate
            return REPO_ROOT / raw
    raise KeyError(f"manifest artifact not found: {name}")


def _manifest_hashes(manifest: dict[str, Any]) -> dict[str, str]:
    return {str(entry.get("name")): str(entry.get("sha256")) for entry in manifest.get("artifacts", []) if entry.get("name")}


def _root_type_counts(replay_result: dict[str, Any]) -> dict[str, int]:
    return {str(row["node_type"]): int(row.get("count", 1) or 1) for row in replay_result.get("root_unsound_certificates", [])}


def _human_bridge(proof: dict[str, Any], replay_report: dict[str, Any]) -> str:
    lines = [
        "# RUN-030 Human-Readable Theorem Bridge",
        "",
        f"- theorem: `{proof.get('theorem')}`",
        f"- descent implication: `{proof.get('descent_implication')}`",
        f"- strict verifier: `{proof.get('verifier_status')}`",
        f"- top-level certificates replayed: `{replay_report.get('replay_pass_count')}/{replay_report.get('certificate_count')}`",
        "",
        "RUN-030 accepts only manifest-backed replay of:",
        "",
        "1. universal arithmetic entry into even descent or odd parent states",
        "2. parent-state coverage including the final P26 residual parent certificate",
        "3. exact S3/S4/S6 transition soundness from certificate_store payloads",
        "4. a well-founded ranking over non-terminal parent-state transitions",
        "5. the explicit strong-induction bridge from descent to convergence",
        "",
    ]
    if proof.get("verifier_status") != "PASS":
        lines.extend(
            [
                "## Current Blocker",
                "",
                "The top-level replay is intentionally failing until the reported mathematical blocker is supplied as a replayable certificate.",
                "",
            ]
        )
        for row in proof.get("minimal_blocking_set", proof.get("unknown_obligations", [])):
            lines.append(f"- `{row.get('obligation_id')}`: {row.get('reason')}")
    return "\n".join(lines) + "\n"


def _ranking_payload(certs: list[dict[str, Any]]) -> dict[str, Any]:
    for cert in certs:
        if cert.get("certificate_type") == "well_founded_ranking_certificate":
            payload = cert.get("proof_payload") if isinstance(cert.get("proof_payload"), dict) else {}
            ranking = payload.get("ranking")
            return ranking if isinstance(ranking, dict) else {}
    return {}


def _write_ranking_failure_artifacts(ranking: dict[str, Any], out_dir: Path) -> None:
    unresolved = list(ranking.get("unresolved_sccs") or [])
    nondecreasing = list(ranking.get("nondecreasing_edges") or [])
    write_jsonl(out_dir / "unresolved_sccs.jsonl", unresolved)
    write_jsonl(out_dir / "nondecreasing_edges.jsonl", nondecreasing)
    lines = [
        "# RUN-030 Ranking Failure Report",
        "",
        f"- status: `{ranking.get('status', 'UNKNOWN')}`",
        f"- well-founded order attempted: `{ranking.get('well_founded_order')}`",
        f"- terminal/descent edges: `{ranking.get('terminal_edge_count', 0)}`",
        f"- non-terminal edges: `{ranking.get('nonterminal_edge_count', 0)}`",
        f"- unresolved SCCs: `{len(unresolved)}`",
        f"- nondecreasing edges: `{len(nondecreasing)}`",
        "",
    ]
    if unresolved:
        lines.extend(["## GLOBAL_RANKING_INVARIANT_REQUIRED", ""])
        first = unresolved[0]
        lines.append(f"- first SCC id: `{first.get('scc_id')}`")
        lines.append(f"- nodes: `{', '.join(first.get('nodes', []))}`")
        lines.append(f"- internal edge count: `{first.get('edge_count')}`")
        lines.append("")
        lines.append("A replayable `SCC_INTERNAL_RANKING_EXACT` certificate is required for this SCC before the top-level descent implication can be accepted.")
    _write_text("\n".join(lines) + "\n", out_dir / "ranking_failure_report.md")


def _write_missing_top_level(replay_report: dict[str, Any], out_dir: Path) -> None:
    rows = [
        {
            "obligation_id": f"top_level:{name}",
            "status": "UNKNOWN",
            "reason": row.get("reason"),
            "failures": row.get("failures", []),
        }
        for name, row in replay_report.get("results", {}).items()
        if not row.get("accepted")
    ]
    write_jsonl(out_dir / "root_missing_top_level_certificates.jsonl", rows)


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run030_{name}{suffix}"
        shutil.copy2(path, dst)
        entries.append({"name": name, "path": str(dst.relative_to(REPO_ROOT)), "sha256": _sha256(dst)})
    root_manifest = {
        **manifest,
        "artifacts": entries,
        "clean_clone_replay": {
            "command": "python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    _write_json(root_manifest, REPO_ROOT / "proof_manifest.json")


def run_top_level_after_hardening(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("top_level_after_hardening_run030", {}) if isinstance(cfg.get("top_level_after_hardening_run030", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    source_manifest_path = Path(run_cfg.get("manifest") or DEFAULT_MANIFEST)
    source_manifest = _load_json(source_manifest_path)
    graph_path = Path(run_cfg.get("proof_graph") or _resolve_manifest_artifact(source_manifest, "proof_dependency_graph_frozen", manifest_path=source_manifest_path))
    trace_path = Path(run_cfg.get("accepted_action_trace") or _resolve_manifest_artifact(source_manifest, "accepted_action_trace", manifest_path=source_manifest_path))
    s3_path = Path(run_cfg.get("s3_debt_certificates") or _resolve_manifest_artifact(source_manifest, "s3_debt_certificates", manifest_path=source_manifest_path))
    s4_path = Path(run_cfg.get("parent_transition_certificates") or _resolve_manifest_artifact(source_manifest, "parent_transition_certificates", manifest_path=source_manifest_path))
    s6_path = Path(run_cfg.get("s6_lemma_certificates") or _resolve_manifest_artifact(source_manifest, "s6_lemma_certificates", manifest_path=source_manifest_path))
    parent_residual_path = Path(run_cfg.get("parent_residual_certificate") or DEFAULT_PARENT_RESIDUAL)

    graph = _load_json(graph_path)
    trace_rows = _load_jsonl(trace_path)
    s3_rows = _load_jsonl(s3_path)
    s4_rows = _load_jsonl(s4_path)
    s6_rows = _load_jsonl(s6_path)
    parent_residual = _load_json(parent_residual_path)
    manifest_hashes = _manifest_hashes(source_manifest)
    manifest_hashes["parent_residual_certificate"] = _sha256(parent_residual_path)

    context = build_replay_context(
        graph=graph,
        s3_rows=s3_rows,
        s4_rows=s4_rows,
        s6_rows=s6_rows,
        parent_residual_certificate=parent_residual,
        manifest_hashes=manifest_hashes,
    )
    certificates, build_failures = build_top_level_certificates_after_hardening(graph, context=context)
    patched_graph = attach_top_level_certificates(graph, certificates)
    patched_context = {**context, "graph": patched_graph, "graph_hash": None}
    replay_report = replay_top_level_certificates(certificates, graph=patched_graph, context=patched_context, run_id=RUN_ID)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph, replay_context=patched_context)

    certs_out = out_dir / "top_level_certificates.jsonl"
    replay_report_out = out_dir / "top_level_replay_report.json"
    graph_out = out_dir / "proof_dependency_graph_top_level_run030.json"
    trace_out = out_dir / "accepted_action_trace_top_level_run030.jsonl"
    s3_out = out_dir / "s3_debt_certificates.jsonl"
    s4_out = out_dir / "parent_transition_certificates.jsonl"
    s6_out = out_dir / "s6_lemma_certificates.jsonl"
    parent_residual_out = out_dir / "parent_residual_certificate.json"
    final_proof_out = out_dir / "final_proof_object.json"
    human_out = out_dir / "human_readable_theorem_bridge.md"
    manifest_out = out_dir / "proof_manifest.json"
    strict_replay_out = out_dir / "strict_replay_result.json"
    root_replay_out = out_dir / "root_manifest_replay_result.json"

    write_jsonl(certs_out, certificates)
    _write_json(replay_report, replay_report_out)
    _write_json(patched_graph, graph_out)
    write_jsonl(trace_out, trace_rows)
    write_jsonl(s3_out, s3_rows)
    write_jsonl(s4_out, s4_rows)
    write_jsonl(s6_out, s6_rows)
    _write_json(parent_residual, parent_residual_out)
    _write_json(proof, final_proof_out)
    _write_text(_human_bridge(proof, replay_report), human_out)
    _write_missing_top_level(replay_report, out_dir)
    _write_ranking_failure_artifacts(_ranking_payload(certificates), out_dir)

    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "s3_debt_certificates": s3_out,
        "parent_transition_certificates": s4_out,
        "s6_lemma_certificates": s6_out,
        "parent_residual_certificate": parent_residual_out,
        "top_level_certificates": certs_out,
        "top_level_replay_report": replay_report_out,
        "final_proof_object": final_proof_out,
    }
    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {
            "strict_verifier": proof.get("verifier_status"),
            "audit_status": "PASS" if proof.get("verifier_status") == "PASS" and replay_report.get("all_pass") else "AUDIT_FAIL",
            "proof_confidence_percent": 100.0 if proof.get("verifier_status") == "PASS" and replay_report.get("all_pass") else 0.0,
        },
        "artifacts": [_artifact_entry(name, path, out_dir) for name, path in artifacts.items()],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_top_level_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run030.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_verifier.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/replay_strict_proof.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_decode.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s3_debt_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_parent_transition_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_s6_lemma_cert.py"),
        ],
        "clean_clone_replay": {
            "command": f"python -m collatz_lab.replay_strict_proof --manifest reports/runs/{RUN_ID}/proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    _write_json(manifest, manifest_out)
    replay_result = replay_manifest(manifest_out, out=strict_replay_out)

    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        _write_repo_replay_bundle(manifest, artifacts)
        root_replay = replay_manifest(REPO_ROOT / "proof_manifest.json", out=root_replay_out)
    else:
        root_replay = replay_result

    root_counts = _root_type_counts(replay_result)
    ranking = _ranking_payload(certificates)
    result = {
        "schema": "collatz_lab.run030_top_level_theorem_certificates_after_s3_s6_hardening",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "top_level_certificates_generated": len(certificates),
        "top_level_replay_pass": int(replay_report.get("replay_pass_count", 0) or 0),
        "top_level_certificate_failures": build_failures + [
            {"certificate": name, **row}
            for name, row in replay_report.get("results", {}).items()
            if not row.get("accepted")
        ],
        "s3_exact_replay_pass": 182 - int(root_counts.get("S3_CERTIFICATE", 0) or 0),
        "s3_exact_certificate_count": len(s3_rows),
        "s4_exact_certificate_count": len(s4_rows),
        "s6_exact_replay_pass": 28 - int(root_counts.get("S6_CERTIFICATE", 0) or 0),
        "s6_exact_certificate_count": len(s6_rows),
        "hash_failure_count": int(replay_result.get("hash_failure_count", 0) or 0),
        "strict_verifier": replay_result.get("strict_verifier"),
        "verifier_status": replay_result.get("verifier_status"),
        "proof_confidence_percent": replay_result.get("proof_confidence_percent"),
        "clean_manifest_replay": {
            "audit_status": root_replay.get("audit_status"),
            "strict_verifier": root_replay.get("strict_verifier"),
            "verifier_status": root_replay.get("verifier_status"),
            "proof_confidence_percent": root_replay.get("proof_confidence_percent"),
            "hash_failure_count": root_replay.get("hash_failure_count"),
        },
        "ranking_status": ranking.get("status", "UNKNOWN"),
        "ranking_blocker": "GLOBAL_RANKING_INVARIANT_REQUIRED" if ranking.get("unresolved_sccs") else None,
        "unresolved_scc_count": len(ranking.get("unresolved_sccs") or []),
        "root_unsound_certificates": replay_result.get("root_unsound_certificates", []),
        "strict_unknown_obligations": replay_result.get("unknown_obligations", []),
        "artifacts": {
            "top_level_certificates": str(certs_out),
            "top_level_replay_report": str(replay_report_out),
            "final_proof_object": str(final_proof_out),
            "root_manifest_replay_result": str(root_replay_out),
            "human_readable_theorem_bridge": str(human_out),
            "run_result": str(out_dir / "run_result.json"),
            "unresolved_sccs": str(out_dir / "unresolved_sccs.jsonl"),
            "nondecreasing_edges": str(out_dir / "nondecreasing_edges.jsonl"),
            "ranking_failure_report": str(out_dir / "ranking_failure_report.md"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run030_run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_top_level_after_hardening(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
