import hashlib
import json

from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_parent_transition_cert import build_parent_transition_certificate
from collatz_lab.proof_action_state import canonical_state
from collatz_lab.replay_strict_proof import replay_manifest


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _transition_certificate() -> dict:
    action = {
        "type": "DERIVE_PARENT_TRANSITION",
        "target": "goal_0",
        "branch_id": "P23:r1:d1",
        "source_parent": 23,
        "target_parent": 20,
        "valuation": 1,
    }
    return build_parent_transition_certificate(action=action, state=_s4_state(include_certificate=False), node_id="s4:unit")


def _s4_state(*, include_certificate: bool = False) -> str:
    fact = {
        "kind": "high_parent_successor",
        "target": "goal_0",
        "branch_id": "P23:r1:d1",
        "source_parent": 23,
        "target_parent": 20,
        "valuation": 1,
        "sample_checks_passed": True,
    }
    if include_certificate:
        fact["transition_certificate"] = json.dumps(_transition_certificate(), sort_keys=True, separators=(",", ":"))
    return canonical_state(
        gate="S4_HIGH_PARENT_SUCCESSOR_FACT",
        goal="derive parent transition",
        goal_attrs={"kind": "high_parent_successor"},
        assumptions=["z_family=z(k) = 5 + 94143178827*k"],
        facts=[fact],
    )


def _s6_payload() -> dict:
    return {
        "lemma_id": "s6_lemma",
        "statement": "S6 replayable lemma",
        "depends_on": ["coverage_cert", "base_case_cert", "lifting_cert", "no_escape_cert"],
        "proof_payload": {
            "coverage": {"certificate_hash": "coverage_hash", "proof": "exact coverage proof"},
            "transition_chain": {"certificate_hash": "transition_hash", "proof": "exact transition chain"},
            "ranking_decrease": {"certificate_hash": "rank_hash", "proof": "exact ranking proof"},
            "no_escape": {"certificate_hash": "escape_hash", "proof": "exact no escape proof"},
            "induction_link": {"certificate_hash": "induction_hash", "proof": "exact induction link"},
        },
    }


def _s6_state() -> str:
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="verify S6 lemma",
        goal_id="s6_goal",
        goal_attrs={"kind": "s6_blocker"},
        known_lemmas=["s6_lemma"],
        facts=[
            {
                "kind": "s6_blocker",
                "target": "s6_goal",
                "lemma_id": "s6_lemma",
                "coverage_certificate": "coverage_cert",
                "certificate_id": "coverage_cert",
                "base_case_certificate": "base_case_cert",
                "lifting_certificate": "lifting_cert",
                "no_escape_certificate": "no_escape_cert",
                "coverage_modulus": 8,
                "covered_residue_count": 8,
                "verifier_status": "ACCEPT",
            }
        ],
    )


def test_parent_transition_sample_checks_are_diagnostic_only() -> None:
    action = {
        "type": "DERIVE_PARENT_TRANSITION",
        "target": "goal_0",
        "branch_id": "P23:r1:d1",
        "source_parent": 23,
        "target_parent": 20,
        "valuation": 1,
    }

    check = verify_action_for_state(action, _s4_state())

    assert not check.accepted
    assert check.status == "REJECT_SYNTAX"
    assert "transition_certificate" in check.reason


def test_parent_transition_requires_replayable_exact_payload() -> None:
    action = {
        "type": "DERIVE_PARENT_TRANSITION",
        "target": "goal_0",
        "branch_id": "P23:r1:d1",
        "source_parent": 23,
        "target_parent": 20,
        "valuation": 1,
        "transition_certificate": _transition_certificate(),
    }

    check = verify_action_for_state(action, _s4_state(include_certificate=True))

    assert check.accepted
    assert check.reason == "exact symbolic parent-transition certificate replays"


def test_s6_lemma_status_id_is_not_proof() -> None:
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal",
        "lemma_id": "s6_lemma",
        "verifier": "strict_theorem_verifier",
        "status": "ACCEPT",
    }

    check = verify_action_for_state(action, _s6_state())

    assert not check.accepted
    assert check.status == "REJECT_SYNTAX"
    assert "lemma" in check.reason


def test_s6_lemma_payload_rejects_bare_dependency_names() -> None:
    payload = _s6_payload()
    payload["proof_payload"]["coverage"] = "coverage_cert"
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal",
        "lemma_id": "s6_lemma",
        "verifier": "strict_theorem_verifier",
        "status": "ACCEPT",
        "lemma": payload,
    }

    check = verify_action_for_state(action, _s6_state())

    assert not check.accepted
    assert check.status == "REJECT_S6_LEMMA_PAYLOAD"


def test_s6_lemma_accepts_replayable_payload() -> None:
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal",
        "lemma_id": "s6_lemma",
        "verifier": "strict_theorem_verifier",
        "status": "ACCEPT",
        "lemma": _s6_payload(),
    }

    check = verify_action_for_state(action, _s6_state())

    assert check.accepted
    assert check.reason == "S6 lemma proof payload and dependencies replay"


def test_manifest_replay_downgrades_unsound_pass(tmp_path) -> None:
    graph = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {"coverage:unit": {"node_id": "coverage:unit", "node_type": "COVERAGE_CERTIFICATE", "status": "ACCEPTED"}},
        "edges": [],
        "open": [],
    }
    trace_rows = [
        {
            "node_id": "s4:unit",
            "node_type": "S4_LIFT",
            "action": {
                "type": "DERIVE_PARENT_TRANSITION",
                "target": "goal_0",
                "branch_id": "P23:r1:d1",
                "source_parent": 23,
                "target_parent": 20,
                "valuation": 1,
            },
            "verifier_check": {"reason": "high-parent successor congruence samples are exact"},
        },
        {
            "node_id": "s6_lemma:unit",
            "node_type": "S6_LEMMA",
            "action": {"type": "VERIFY_S6_LEMMA", "target": "s6_goal", "lemma_id": "s6_lemma", "verifier": "strict_theorem_verifier", "status": "ACCEPT"},
        },
    ]
    graph_path = tmp_path / "graph.json"
    trace_path = tmp_path / "trace.jsonl"
    source_path = tmp_path / "source.py"
    graph_text = json.dumps(graph, sort_keys=True)
    trace_text = "\n".join(json.dumps(row, sort_keys=True) for row in trace_rows) + "\n"
    source_text = "print('replay')\n"
    graph_path.write_text(graph_text, encoding="utf-8")
    trace_path.write_text(trace_text, encoding="utf-8")
    source_path.write_text(source_text, encoding="utf-8")
    manifest = {
        "artifacts": [
            {"name": "proof_dependency_graph_frozen", "path": "graph.json", "sha256": _sha(graph_text)},
            {"name": "accepted_action_trace", "path": "trace.jsonl", "sha256": _sha(trace_text)},
        ],
        "source_files": [{"name": "source.py", "path": "source.py", "sha256": _sha(source_text)}],
        "source_run_accounting": {"strict_verifier": "PASS", "audit_status": "FAIL", "proof_confidence_percent": 100.0},
    }
    manifest_path = tmp_path / "proof_manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")

    result = replay_manifest(manifest_path)

    assert result["audit_status"] == "PASS_FOR_VERIFIER_SOUNDNESS"
    assert result["strict_verifier"] == "FAIL"
    assert result["proof_confidence_percent"] == 0.0
    assert result["source_run_accounting"]["verifier_status"] == "UNSOUND_PASS"
    assert {row["node_type"] for row in result["root_unsound_certificates"]} >= {"S4_LIFT", "S6_LEMMA", "STRICT_THEOREM_TOP_LEVEL"}
