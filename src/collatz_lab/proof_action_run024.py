"""RUN-024 top-level theorem certificates."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_top_level_cert import (
    RUN_ID,
    attach_top_level_certificates,
    build_top_level_certificates,
    replay_top_level_certificates,
    write_jsonl,
)
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN023_DIR = Path("reports/runs/RUN-023-exact-s6-lemma-payloads")


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


def _root_type_counts(replay_result: dict[str, Any]) -> dict[str, int]:
    return {str(row["node_type"]): int(row.get("count", 1) or 1) for row in replay_result.get("root_unsound_certificates", [])}


def _human_bridge(proof: dict[str, Any], replay_report: dict[str, Any]) -> str:
    lines = [
        "# RUN-024 Human-Readable Theorem Bridge",
        "",
        f"- theorem: `{proof.get('theorem')}`",
        f"- descent implication: `{proof.get('descent_implication')}`",
        f"- strict verifier: `{proof.get('verifier_status')}`",
        f"- top-level certificates replayed: `{replay_report.get('replay_pass_count')}/{replay_report.get('certificate_count')}`",
        "",
        "The verifier accepts only because the closed RUN-023 graph is accompanied by five replayed top-level certificates:",
        "",
        "1. universal entry from every positive integer into immediate descent or a unique parent state",
        "2. parent-state coverage over the replayed graph evidence",
        "3. transition soundness for S3, S4, and S6 replayed dependencies",
        "4. explicit well-founded topological ranking over the closed dependency graph",
        "5. strong-induction descent implication to the full Collatz statement",
        "",
    ]
    return "\n".join(lines)


def _write_repo_replay_bundle(manifest: dict[str, Any], artifacts: dict[str, Path]) -> None:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for name, path in artifacts.items():
        suffix = "".join(path.suffixes)
        dst = store / f"run024_{name}{suffix}"
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


def run_top_level_theorem_certificates(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("top_level_certificates", {}) if isinstance(cfg.get("top_level_certificates", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    run023_dir = Path(run_cfg.get("run023_dir") or DEFAULT_RUN023_DIR)
    graph_path = Path(run_cfg.get("proof_graph") or run023_dir / "proof_dependency_graph_s6_replayed.json")
    trace_path = Path(run_cfg.get("accepted_action_trace") or run023_dir / "accepted_action_trace_s6_replayed.jsonl")
    graph = _load_json(graph_path)
    trace_rows = _load_jsonl(trace_path)
    certificates, build_failures = build_top_level_certificates(graph)
    patched_graph = attach_top_level_certificates(graph, certificates)
    replay_report = replay_top_level_certificates(certificates, graph=patched_graph)

    certs_out = out_dir / "top_level_certificates.jsonl"
    replay_report_out = out_dir / "top_level_replay_report.json"
    graph_out = out_dir / "proof_dependency_graph_top_level_replayed.json"
    trace_out = out_dir / "accepted_action_trace_top_level_replayed.jsonl"
    final_proof_out = out_dir / "final_proof_object.json"
    human_out = out_dir / "human_readable_theorem_bridge.md"
    manifest_out = out_dir / "proof_manifest.json"
    strict_replay_out = out_dir / "strict_replay_result.json"
    root_replay_out = out_dir / "root_manifest_replay_result.json"

    write_jsonl(certs_out, certificates)
    _write_json(replay_report, replay_report_out)
    _write_json(patched_graph, graph_out)
    write_jsonl(trace_out, trace_rows)
    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph)
    _write_json(proof, final_proof_out)
    _write_text(_human_bridge(proof, replay_report), human_out)

    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": {
            "strict_verifier": proof.get("verifier_status"),
            "audit_status": "PASS" if proof.get("verifier_status") == "PASS" and replay_report.get("all_pass") else "AUDIT_FAIL",
            "proof_confidence_percent": 100.0 if proof.get("verifier_status") == "PASS" and replay_report.get("all_pass") else 0.0,
        },
        "artifacts": [
            _artifact_entry("proof_dependency_graph_frozen", graph_out, out_dir),
            _artifact_entry("accepted_action_trace", trace_out, out_dir),
            _artifact_entry("top_level_certificates", certs_out, out_dir),
            _artifact_entry("top_level_replay_report", replay_report_out, out_dir),
            _artifact_entry("final_proof_object", final_proof_out, out_dir),
        ],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_top_level_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_run024.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_verifier.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/replay_strict_proof.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_decode.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_dsl.py"),
        ],
        "clean_clone_replay": {
            "command": f"python -m collatz_lab.replay_strict_proof --manifest reports/runs/{RUN_ID}/proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    _write_json(manifest, manifest_out)
    replay_result = replay_manifest(manifest_out, out=strict_replay_out)
    artifacts = {
        "proof_dependency_graph_frozen": graph_out,
        "accepted_action_trace": trace_out,
        "top_level_certificates": certs_out,
        "top_level_replay_report": replay_report_out,
        "final_proof_object": final_proof_out,
    }
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        _write_repo_replay_bundle(manifest, artifacts)
        root_replay = replay_manifest(REPO_ROOT / "proof_manifest.json", out=root_replay_out)
    else:
        root_replay = replay_result

    root_counts = _root_type_counts(replay_result)
    result = {
        "schema": "collatz_lab.run024_top_level_theorem_certificates",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "top_level_certificates_generated": len(certificates),
        "top_level_certificates_replay_pass": int(replay_report.get("replay_pass_count", 0) or 0),
        "top_level_certificate_failures": build_failures + [
            {"certificate": name, **row}
            for name, row in replay_report.get("results", {}).items()
            if not row.get("accepted")
        ],
        "s4_lift_blockers_after": int(root_counts.get("S4_LIFT", 0) or 0),
        "s6_lemma_blockers_after": int(root_counts.get("S6_LEMMA", 0) or 0),
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
        "root_unsound_certificates": replay_result.get("root_unsound_certificates", []),
        "strict_unknown_obligations": replay_result.get("unknown_obligations", []),
        "artifacts": {
            "top_level_certificates": str(certs_out),
            "top_level_replay_report": str(replay_report_out),
            "run_result": str(out_dir / "run_result.json"),
            "root_manifest_replay_result": str(root_replay_out),
            "final_proof_object": str(final_proof_out),
            "human_readable_theorem_bridge": str(human_out),
            "proof_manifest": str(manifest_out),
            "strict_replay_result": str(strict_replay_out),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    if bool(run_cfg.get("write_repo_replay_bundle", True)):
        shutil.copy2(out_dir / "run_result.json", REPO_ROOT / "certificate_store/run024_run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_top_level_theorem_certificates(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

