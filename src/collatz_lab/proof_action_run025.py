"""RUN-025 independent audit package for the RUN-024 proof candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .proof_action_top_level_cert import (
    COLLATZ_CONJECTURE_STATEMENT,
    THEOREM_STATEMENT,
    certificate_hash,
)
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "RUN-025-proof-candidate-external-audit-package"
DEFAULT_RUN024_DIR = Path("reports/runs/RUN-024-top-level-theorem-certificates")
PROOF_TAG = "proof-candidate-run024"
VERIFY_SOURCE_FILES = (
    "src/collatz_lab/proof_verifier.py",
    "src/collatz_lab/replay_strict_proof.py",
    "src/collatz_lab/proof_action_top_level_cert.py",
    "src/collatz_lab/proof_action_s6_lemma_cert.py",
    "src/collatz_lab/proof_action_parent_transition_cert.py",
    "src/collatz_lab/proof_action_decode.py",
    "src/collatz_lab/proof_action_dsl.py",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(command),
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-12000:],
    }


def _git_text(args: list[str], *, cwd: Path = REPO_ROOT) -> str:
    completed = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True)
    return completed.stdout.strip()


def _clone_at_tag(tag: str, parent: Path, *, name: str) -> Path:
    clone = parent / name
    result = _run(["git", "clone", "--no-hardlinks", str(REPO_ROOT), str(clone)], cwd=REPO_ROOT)
    if result["returncode"] != 0:
        raise RuntimeError(f"git clone failed: {result['stderr']}")
    result = _run(["git", "checkout", tag], cwd=clone)
    if result["returncode"] != 0:
        raise RuntimeError(f"git checkout {tag} failed: {result['stderr']}")
    return clone


def _replay_in_clone(clone: Path, *, out_name: str = "replay_result.json") -> dict[str, Any]:
    out_path = clone / out_name
    env = os.environ.copy()
    env["PYTHONPATH"] = str(clone / "src")
    result = _run(
        [
            sys.executable,
            "-m",
            "collatz_lab.replay_strict_proof",
            "--manifest",
            "proof_manifest.json",
            "--out",
            out_name,
        ],
        cwd=clone,
        env=env,
    )
    payload = _read_json(out_path) if out_path.exists() else {}
    return {"process": result, "result": payload, "passed": _is_strict_pass(payload)}


def _replay_with_network_disabled(clone: Path) -> dict[str, Any]:
    script = (
        "import json, socket\n"
        "_OriginalSocket = socket.socket\n"
        "class BlockedSocket(_OriginalSocket):\n"
        "    def connect(self, *args, **kwargs):\n"
        "        raise RuntimeError('network disabled by RUN-025 audit')\n"
        "    def connect_ex(self, *args, **kwargs):\n"
        "        raise RuntimeError('network disabled by RUN-025 audit')\n"
        "socket.socket = BlockedSocket\n"
        "from collatz_lab.replay_strict_proof import replay_manifest\n"
        "result = replay_manifest('proof_manifest.json', out='network_disabled_replay_result.json')\n"
        "print(json.dumps(result, sort_keys=True))\n"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(clone / "src")
    env["NO_NETWORK"] = "1"
    env["http_proxy"] = "http://127.0.0.1:9"
    env["https_proxy"] = "http://127.0.0.1:9"
    result = _run([sys.executable, "-c", script], cwd=clone, env=env)
    payload = _read_json(clone / "network_disabled_replay_result.json") if (clone / "network_disabled_replay_result.json").exists() else {}
    return {"process": result, "result": payload, "passed": _is_strict_pass(payload)}


def _is_strict_pass(result: dict[str, Any]) -> bool:
    return (
        result.get("audit_status") == "PASS"
        and result.get("strict_verifier") == "PASS"
        and result.get("verifier_status") == "PASS"
        and int(result.get("hash_failure_count", 0) or 0) == 0
        and not result.get("root_unsound_certificates")
        and not result.get("unknown_obligations")
    )


def _mutation_replay_failed(result: dict[str, Any]) -> bool:
    return not _is_strict_pass(result)


def _load_graph(clone: Path) -> dict[str, Any]:
    return _read_json(clone / "certificate_store/run024_proof_dependency_graph_frozen.json")


def _save_graph_and_update_manifest(clone: Path, graph: dict[str, Any]) -> None:
    graph_path = clone / "certificate_store/run024_proof_dependency_graph_frozen.json"
    _write_json(graph_path, graph)
    _update_manifest_artifact_hash(clone, "proof_dependency_graph_frozen")


def _update_manifest_artifact_hash(clone: Path, artifact_name: str) -> None:
    manifest_path = clone / "proof_manifest.json"
    manifest = _read_json(manifest_path)
    for entry in manifest.get("artifacts", []):
        if entry.get("name") == artifact_name:
            entry["sha256"] = _sha256(clone / str(entry["path"]))
            break
    else:
        raise KeyError(f"manifest artifact not found: {artifact_name}")
    _write_json(manifest_path, manifest)


def _top_level_certificates(graph: dict[str, Any]) -> list[dict[str, Any]]:
    certs = graph.get("top_level_certificates", [])
    if isinstance(certs, list):
        return certs
    if isinstance(certs, dict):
        return [row for row in certs.values() if isinstance(row, dict)]
    return []


def _set_top_level_certificates(graph: dict[str, Any], certificates: list[dict[str, Any]]) -> None:
    existing = graph.get("top_level_certificates")
    if isinstance(existing, dict):
        graph["top_level_certificates"] = {
            str(cert.get("certificate_type") or cert.get("type") or cert.get("certificate_id")): cert
            for cert in certificates
        }
    else:
        graph["top_level_certificates"] = certificates


def _mutate_certificate_hash(clone: Path) -> str:
    graph = _load_graph(clone)
    cert = _top_level_certificates(graph)[0]
    cert["certificate_hash"] = "0" * 64
    _save_graph_and_update_manifest(clone, graph)
    return "mutated first top-level certificate_hash without changing payload"


def _mutate_top_level_theorem(clone: Path) -> str:
    graph = _load_graph(clone)
    cert = next(
        row
        for row in _top_level_certificates(graph)
        if row.get("certificate_type") == "universal_entry_certificate"
    )
    payload = cert.setdefault("proof_payload", {})
    payload["theorem"] = "forall n > 1 sample checks eventually decrease n"
    cert["certificate_hash"] = certificate_hash(cert)
    _save_graph_and_update_manifest(clone, graph)
    return "changed universal_entry_certificate theorem payload and recomputed certificate hash"


def _remove_s4_transition_certificate(clone: Path) -> str:
    graph = _load_graph(clone)
    for node in graph.get("nodes", {}).values():
        if node.get("node_type") != "S4_LIFT":
            continue
        for accepted in node.get("accepted_actions", []) or []:
            action = accepted.get("action") or {}
            if action.get("type") == "DERIVE_PARENT_TRANSITION":
                action.pop("transition_certificate", None)
                _save_graph_and_update_manifest(clone, graph)
                return f"removed transition_certificate from S4 node {node.get('node_id')}"
    raise RuntimeError("no S4 DERIVE_PARENT_TRANSITION action found")


def _remove_s6_lemma_certificate(clone: Path) -> str:
    graph = _load_graph(clone)
    for node in graph.get("nodes", {}).values():
        if node.get("node_type") != "S6_LEMMA":
            continue
        for accepted in node.get("accepted_actions", []) or []:
            action = accepted.get("action") or {}
            if action.get("type") == "VERIFY_S6_LEMMA":
                action.pop("certificate_id", None)
                action.pop("certificate_hash", None)
                _save_graph_and_update_manifest(clone, graph)
                return f"removed certificate_id/hash from S6 node {node.get('node_id')}"
    raise RuntimeError("no S6 VERIFY_S6_LEMMA action found")


def _remove_ranking_certificate(clone: Path) -> str:
    graph = _load_graph(clone)
    remaining = [
        cert for cert in _top_level_certificates(graph) if cert.get("certificate_type") != "well_founded_ranking_certificate"
    ]
    _set_top_level_certificates(graph, remaining)
    _save_graph_and_update_manifest(clone, graph)
    return "removed well_founded_ranking_certificate from graph"


def _mutate_artifact_file_hash(clone: Path) -> str:
    certs_path = clone / "certificate_store/run024_top_level_certificates.jsonl"
    lines = certs_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["certificate_hash"] = "f" * 64
    lines[0] = json.dumps(first, sort_keys=True)
    certs_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "mutated top_level_certificates.jsonl certificate hash without updating manifest"


def _run_mutation_check(
    *,
    tag: str,
    temp_root: Path,
    name: str,
    mutate,
) -> dict[str, Any]:
    clone = _clone_at_tag(tag, temp_root, name=name)
    mutation = mutate(clone)
    replay = _replay_in_clone(clone, out_name=f"{name}_replay_result.json")
    return {
        "name": name,
        "mutation": mutation,
        "expected_failure": True,
        "passed": _mutation_replay_failed(replay["result"]),
        "replay": replay["result"],
        "process": replay["process"],
    }


def _certificate_hash_manifest(package_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((package_dir / "certificate_store").glob("*")):
        if path.is_file():
            rows.append({"path": str(path.relative_to(package_dir)), "sha256": _sha256(path)})
    manifest = _read_json(package_dir / "proof_manifest.json")
    for section in ("artifacts", "source_files"):
        for entry in manifest.get(section, []):
            rows.append({"manifest_section": section, **entry})
    return rows


def _copy_required_artifacts(package_dir: Path, run024_dir: Path) -> None:
    shutil.copy2(REPO_ROOT / "proof_manifest.json", package_dir / "proof_manifest.json")
    shutil.copytree(REPO_ROOT / "certificate_store", package_dir / "certificate_store", dirs_exist_ok=True)
    artifact_map = {
        "final_proof_object.json": run024_dir / "final_proof_object.json",
        "top_level_certificates.jsonl": run024_dir / "top_level_certificates.jsonl",
        "root_manifest_replay_result.json": run024_dir / "root_manifest_replay_result.json",
        "human_readable_theorem_bridge.md": run024_dir / "human_readable_theorem_bridge.md",
    }
    for name, source in artifact_map.items():
        if source.exists():
            shutil.copy2(source, package_dir / name)
    verifier_dir = package_dir / "verifier_source_files"
    for source_name in VERIFY_SOURCE_FILES:
        source = REPO_ROOT / source_name
        if source.exists():
            target = verifier_dir / source_name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _reproduction_script(commit_hash: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

git clone <repo-url> collatz-pattern-lab-proof-candidate
cd collatz-pattern-lab-proof-candidate
git checkout {PROOF_TAG}
test "$(git rev-parse HEAD)" = "{commit_hash}"
python -m pip install -e ".[dev]"
python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json
"""


def _audit_summary(result: dict[str, Any]) -> str:
    status = "AUDIT_PASS: proof candidate ready for external review" if result["audit_status"] == "AUDIT_PASS" else "AUDIT_FAIL: exact unsound assumption / verifier gap found"
    return "\n".join(
        [
            f"# {RUN_ID}",
            "",
            status,
            "",
            "Language to use externally:",
            "",
            "> We have a clean-replay, verifier-passing Collatz proof candidate in our repository.",
            "",
            "Do not say: `We proved Collatz.` External review is still required.",
            "",
            f"- frozen commit: `{result['commit_hash']}`",
            f"- frozen tag: `{PROOF_TAG}`",
            f"- clean clone replay: `{result['checks']['clean_clone_replay']['passed']}`",
            f"- manifest-only replay after deleting generated ignored files: `{result['checks']['manifest_only_replay_after_delete']['passed']}`",
            f"- network-disabled replay: `{result['checks']['network_disabled_replay']['passed']}`",
            f"- mutation checks passed: `{result['mutation_checks_passed']}/{result['mutation_check_count']}`",
            f"- theorem statement exact: `{result['checks']['theorem_statement_exact']['passed']}`",
            f"- descent implication exact: `{result['checks']['descent_implication_exact']['passed']}`",
            "",
            "Audit question: does the verifier actually prove the theorem it says it proves?",
            "",
        ]
    )


def run_external_audit_package(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("external_audit", {}) if isinstance(cfg.get("external_audit", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    run024_dir = Path(run_cfg.get("run024_dir") or DEFAULT_RUN024_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    commit_hash = _git_text(["rev-parse", "HEAD"])
    tag_hash = _git_text(["rev-list", "-n", "1", PROOF_TAG])
    if tag_hash != commit_hash:
        raise RuntimeError(f"{PROOF_TAG} points to {tag_hash}, but HEAD is {commit_hash}")

    _copy_required_artifacts(out_dir, run024_dir)
    _write_text(out_dir / "reproduction_script.sh", _reproduction_script(commit_hash))
    os.chmod(out_dir / "reproduction_script.sh", 0o755)
    _write_json(out_dir / "certificate_hash_manifest.json", _certificate_hash_manifest(out_dir))

    with tempfile.TemporaryDirectory(prefix="run025-audit-") as tmp:
        temp_root = Path(tmp)
        clean_clone = _clone_at_tag(PROOF_TAG, temp_root, name="clean-clone")
        clean_replay = _replay_in_clone(clean_clone)

        manifest_only_clone = _clone_at_tag(PROOF_TAG, temp_root, name="manifest-only-clone")
        for generated_name in ("reports", "data", "remote_reports", "runs", ".pytest_cache"):
            shutil.rmtree(manifest_only_clone / generated_name, ignore_errors=True)
        manifest_only_replay = _replay_in_clone(manifest_only_clone, out_name="manifest_only_replay_result.json")

        network_clone = _clone_at_tag(PROOF_TAG, temp_root, name="network-disabled-clone")
        network_replay = _replay_with_network_disabled(network_clone)

        mutation_checks = [
            _run_mutation_check(tag=PROOF_TAG, temp_root=temp_root, name="mutate_artifact_certificate_hash", mutate=_mutate_artifact_file_hash),
            _run_mutation_check(tag=PROOF_TAG, temp_root=temp_root, name="mutate_graph_certificate_hash", mutate=_mutate_certificate_hash),
            _run_mutation_check(tag=PROOF_TAG, temp_root=temp_root, name="mutate_top_level_theorem", mutate=_mutate_top_level_theorem),
            _run_mutation_check(tag=PROOF_TAG, temp_root=temp_root, name="remove_s4_transition_certificate", mutate=_remove_s4_transition_certificate),
            _run_mutation_check(tag=PROOF_TAG, temp_root=temp_root, name="remove_s6_lemma_certificate", mutate=_remove_s6_lemma_certificate),
            _run_mutation_check(tag=PROOF_TAG, temp_root=temp_root, name="remove_ranking_certificate", mutate=_remove_ranking_certificate),
        ]

    local_replay = replay_manifest(REPO_ROOT / "proof_manifest.json", out=out_dir / "root_manifest_replay_result.json")
    proof = _read_json(REPO_ROOT / "certificate_store/run024_final_proof_object.json")
    theorem_exact = proof.get("theorem") == THEOREM_STATEMENT
    descent_exact = proof.get("descent_implication") == COLLATZ_CONJECTURE_STATEMENT
    checks = {
        "root_manifest_replay": {"passed": _is_strict_pass(local_replay), "result": local_replay},
        "clean_clone_replay": clean_replay,
        "manifest_only_replay_after_delete": manifest_only_replay,
        "network_disabled_replay": network_replay,
        "theorem_statement_exact": {
            "passed": theorem_exact,
            "expected": THEOREM_STATEMENT,
            "actual": proof.get("theorem"),
        },
        "descent_implication_exact": {
            "passed": descent_exact,
            "expected": COLLATZ_CONJECTURE_STATEMENT,
            "actual": proof.get("descent_implication"),
        },
    }
    passed_mutations = sum(1 for row in mutation_checks if row.get("passed"))
    all_required_pass = (
        all(bool(row.get("passed")) for row in checks.values())
        and passed_mutations == len(mutation_checks)
    )
    result = {
        "schema": "collatz_lab.run025_external_audit_package",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "audit_status": "AUDIT_PASS" if all_required_pass else "AUDIT_FAIL",
        "audit_conclusion": "proof candidate ready for external review" if all_required_pass else "exact unsound assumption / verifier gap found",
        "commit_hash": commit_hash,
        "tag": PROOF_TAG,
        "tag_hash": tag_hash,
        "checks": checks,
        "mutation_checks": mutation_checks,
        "mutation_check_count": len(mutation_checks),
        "mutation_checks_passed": passed_mutations,
        "artifacts": {
            "audit_summary": str(out_dir / "audit_summary.md"),
            "audit_checks": str(out_dir / "audit_checks.json"),
            "certificate_hash_manifest": str(out_dir / "certificate_hash_manifest.json"),
            "reproduction_script": str(out_dir / "reproduction_script.sh"),
            "proof_manifest": str(out_dir / "proof_manifest.json"),
            "certificate_store": str(out_dir / "certificate_store"),
        },
    }
    _write_json(out_dir / "audit_checks.json", {"checks": checks, "mutation_checks": mutation_checks})
    _write_json(out_dir / "run_result.json", result)
    _write_text(out_dir / "audit_summary.md", _audit_summary(result))
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_external_audit_package(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
