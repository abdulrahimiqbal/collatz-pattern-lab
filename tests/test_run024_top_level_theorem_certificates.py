import hashlib
import json

from collatz_lab.proof_action_state import canonical_state
from collatz_lab.proof_action_run024 import run_top_level_theorem_certificates
from collatz_lab.replay_strict_proof import replay_manifest


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _graph() -> dict:
    state = canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="coverage",
        goal_id="s6_goal",
        goal_attrs={"kind": "s6_blocker"},
        known_lemmas=["lemma"],
        facts=[
            {
                "kind": "s6_blocker",
                "target": "s6_goal",
                "blocker_id": "blocker",
                "branch_id": "branch",
                "lemma_id": "lemma",
                "certificate_id": "coverage_cert",
                "coverage_certificate": "coverage_cert",
                "base_case_certificate": "base_cert",
                "lifting_certificate": "lift_cert",
                "no_escape_certificate": "escape_cert",
                "coverage_modulus": 2,
                "covered_residue_count": 2,
                "status": "PASS",
            }
        ],
    )
    coverage_action = {
        "type": "PROVE_RESIDUE_COVERAGE",
        "target": "s6_goal",
        "modulus": 2,
        "covered_residue_count": 2,
        "certificate_id": "coverage_cert",
    }
    return {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "coverage:coverage_cert": {
                "node_id": "coverage:coverage_cert",
                "node_type": "COVERAGE_CERTIFICATE",
                "status": "ACCEPTED",
                "state": state,
                "accepted_actions": [{"action": coverage_action, "verifier_check": {"accepted": True, "status": "ACCEPT"}}],
            }
        },
        "edges": [],
        "open": [],
    }


def test_run024_generates_top_level_certificates_and_clean_replay(tmp_path) -> None:
    graph_path = tmp_path / "graph.json"
    trace_path = tmp_path / "trace.jsonl"
    graph_path.write_text(json.dumps(_graph(), sort_keys=True), encoding="utf-8")
    trace_path.write_text("", encoding="utf-8")
    cfg = tmp_path / "run024.yaml"
    cfg.write_text(
        "\n".join(
            [
                "top_level_certificates:",
                f"  out_dir: {tmp_path / 'out'}",
                f"  proof_graph: {graph_path}",
                f"  accepted_action_trace: {trace_path}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_top_level_theorem_certificates(cfg)
    replay = replay_manifest(tmp_path / "out" / "proof_manifest.json")

    assert result["top_level_certificates_generated"] == 5
    assert result["top_level_certificates_replay_pass"] == 5
    assert result["strict_verifier"] == "PASS"
    assert result["proof_confidence_percent"] == 100.0
    assert replay["audit_status"] == "PASS"
    assert replay["hash_failure_count"] == 0


def test_manifest_hash_mismatch_fails(tmp_path) -> None:
    graph_text = json.dumps(_graph(), sort_keys=True)
    trace_text = ""
    graph_path = tmp_path / "graph.json"
    trace_path = tmp_path / "trace.jsonl"
    graph_path.write_text(graph_text, encoding="utf-8")
    trace_path.write_text(trace_text, encoding="utf-8")
    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": "hash-mismatch",
        "artifacts": [
            {"name": "proof_dependency_graph_frozen", "path": "graph.json", "sha256": "bad"},
            {"name": "accepted_action_trace", "path": "trace.jsonl", "sha256": _sha(trace_text)},
        ],
        "source_files": [],
        "source_run_accounting": {},
    }
    manifest_path = tmp_path / "proof_manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")

    result = replay_manifest(manifest_path)

    assert result["audit_status"] == "FAIL_REPRODUCTION"
    assert result["hash_failure_count"] == 1

