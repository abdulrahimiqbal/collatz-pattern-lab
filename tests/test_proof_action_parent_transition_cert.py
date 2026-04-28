import json

from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_parent_transition_cert import (
    build_parent_transition_certificate,
    replay_parent_transition_certificate,
    run_parent_transition_certificates,
)
from collatz_lab.proof_action_state import canonical_state


def _action() -> dict:
    return {
        "type": "DERIVE_PARENT_TRANSITION",
        "target": "goal_0",
        "branch_id": "P3:r7:d5",
        "source_parent": 3,
        "target_parent": 5,
        "valuation": 1,
    }


def _state() -> str:
    return canonical_state(
        gate="S4_HIGH_PARENT_SUCCESSOR_FACT",
        goal="derive parent transition",
        goal_attrs={"kind": "high_parent_successor", "branch_id": "P3:r7:d5", "valuation": 1},
        assumptions=["z_family=z(k) = 5 + 27*k"],
        known_lemmas=["high_parent_successor_exactness"],
        facts=[
            {
                "kind": "high_parent_successor",
                "target": "goal_0",
                "branch_id": "P3:r7:d5",
                "source_parent": 3,
                "target_parent": 5,
                "valuation": 1,
                "sample_checks_passed": True,
            }
        ],
    )


def test_parent_transition_certificate_replays_exact_symbolic_payload() -> None:
    certificate = build_parent_transition_certificate(action=_action(), state=_state(), node_id="s4:unit")
    action = {**_action(), "transition_certificate": certificate}

    replay = replay_parent_transition_certificate(action=action, state=_state(), certificate=certificate)
    check = verify_action_for_state(action, _state())

    assert replay.accepted
    assert check.accepted
    assert certificate["congruence_certificate"]["target_odd_residue_mod_3a"] == 16


def test_parent_transition_certificate_rejects_tampered_congruence() -> None:
    certificate = build_parent_transition_certificate(action=_action(), state=_state(), node_id="s4:unit")
    certificate["congruence_certificate"]["target_odd_residue_mod_3a"] += 1
    action = {**_action(), "transition_certificate": certificate}

    replay = replay_parent_transition_certificate(action=action, state=_state(), certificate=certificate)

    assert not replay.accepted
    assert replay.status == "REJECT_TRANSITION_CERTIFICATE"


def test_run022_patches_s4_trace_and_leaves_s6_blocker(tmp_path) -> None:
    graph = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "s4:unit": {
                "node_id": "s4:unit",
                "node_type": "S4_LIFT",
                "status": "ACCEPTED",
                "state": _state(),
                "candidate_actions": [_action()],
                "accepted_actions": [
                    {
                        "action": _action(),
                        "action_text": json.dumps(_action(), sort_keys=True),
                        "verifier_check": {"accepted": True, "reason": "high-parent successor congruence samples are exact", "status": "ACCEPT"},
                    }
                ],
            },
            "s6_lemma:unit": {
                "node_id": "s6_lemma:unit",
                "node_type": "S6_LEMMA",
                "status": "ACCEPTED",
                "accepted_actions": [
                    {
                        "action": {"type": "VERIFY_S6_LEMMA", "target": "s6_goal", "lemma_id": "s6_lemma", "verifier": "strict_theorem_verifier", "status": "ACCEPT"}
                    }
                ],
            },
        },
        "edges": [],
        "open": [],
    }
    trace_rows = [
        {
            "node_id": "s4:unit",
            "node_type": "S4_LIFT",
            "action": _action(),
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
    audit_path = tmp_path / "audit.json"
    graph_path.write_text(json.dumps(graph, sort_keys=True), encoding="utf-8")
    trace_path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in trace_rows) + "\n", encoding="utf-8")
    audit_path.write_text(json.dumps({"verdict": "AUDIT_FAIL"}), encoding="utf-8")
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "\n".join(
            [
                "parent_transition_certificates:",
                f"  out_dir: {tmp_path / 'out'}",
                f"  proof_graph: {graph_path}",
                f"  accepted_action_trace: {trace_path}",
                f"  run020_audit_summary: {audit_path}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_parent_transition_certificates(cfg)

    assert result["s4_lift_blockers_after"] == 0
    assert result["strict_verifier"] == "FAIL"
    assert {row["node_type"] for row in result["root_unsound_certificates"]} >= {"S6_LEMMA", "STRICT_THEOREM_TOP_LEVEL"}
