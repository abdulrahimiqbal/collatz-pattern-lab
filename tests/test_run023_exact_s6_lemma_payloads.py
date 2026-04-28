import html
import json

from collatz_lab.proof_action_run023 import run_exact_s6_lemma_payloads
from collatz_lab.proof_action_s3_debt_cert import build_s3_debt_certificate
from collatz_lab.proof_action_state import canonical_state, state_from_debt_transition
from collatz_lab.replay_strict_proof import replay_manifest


def _s6_state(target: str = "s6_goal_no_escape") -> str:
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="close no escape blocker",
        goal_id=target,
        goal_attrs={"kind": "s6_blocker", "blocker_id": "blocker_unit", "blocker_type": "no_escape"},
        known_lemmas=["s6_unit_lemma"],
        facts=[
            {
                "kind": "s6_blocker",
                "target": target,
                "blocker_id": "blocker_unit",
                "blocker_type": "no_escape",
                "branch_id": "branch_unit",
                "lemma_id": "s6_unit_lemma",
                "certificate_id": "coverage_cert_unit",
                "coverage_certificate": "coverage_cert_unit",
                "base_case_certificate": "base_case_cert_unit",
                "lifting_certificate": "lifting_cert_unit",
                "no_escape_certificate": "no_escape_cert_unit",
                "coverage_modulus": 8,
                "covered_residue_count": 8,
                "status": "PASS",
            }
        ],
    )


def _accepted(action: dict, reason: str = "accepted") -> list[dict]:
    return [{"action": action, "action_text": json.dumps(action, sort_keys=True), "verifier_check": {"accepted": True, "status": "ACCEPT", "reason": reason}}]


def _tiny_graph() -> dict:
    s6_state = _s6_state()
    s3_row = {
        "branch_id": "P3:r7:d5",
        "source_state": {"parent_level": 3, "odd_coordinate_residue": 7, "odd_coordinate_modulus": 27},
        "target_state": {"parent_level": 2, "valuation": 1},
        "gain_bound": {"numerator": 1, "denominator": 2},
        "local_descent_passed": True,
        "exact_congruence_passed": True,
    }
    s3_state = state_from_debt_transition(s3_row)
    s3_action = {"type": "CHECK_DEBT_DECREASE", "target": "goal_0", "branch_id": "P3:r7:d5", "gain_num": 1, "gain_den": 2, "valuation": 1}
    s3_certificate = build_s3_debt_certificate(action=s3_action, state=s3_state, node_id="s3:unit")
    s3_payload = json.dumps(s3_certificate, sort_keys=True, separators=(",", ":"))
    s3_fact = {
        "kind": "s3_debt_certificate",
        "branch_id": s3_certificate["branch_id"],
        "certificate_id": s3_certificate["certificate_id"],
        "certificate_hash": s3_certificate["certificate_hash"],
        "status": s3_certificate["status"],
        "certificate_payload": s3_payload,
    }
    s3_fact_text = "<FACT " + " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in sorted(s3_fact.items())) + "/>"
    s3_state = s3_state.replace("</FACTS>", f"{s3_fact_text}\n</FACTS>", 1)
    coverage_action = {"type": "PROVE_RESIDUE_COVERAGE", "target": "s6_goal_no_escape", "modulus": 8, "covered_residue_count": 8, "certificate_id": "coverage_cert_unit"}
    lift_action = {
        "type": "LIFT_LOCAL_TO_PARAMETRIC_FAMILY",
        "target": "s6_goal_no_escape",
        "local_lemma": "s6_unit_lemma",
        "family_id": "s6_parametric_family",
        "lifting_certificate": "lifting_cert_unit",
    }
    induction_action = {
        "type": "CLOSE_WELL_FOUNDED_INDUCTION",
        "target": "s6_goal_no_escape",
        "measure": "n",
        "descent_lemma": "s6_unit_lemma",
        "base_case_certificate": "base_case_cert_unit",
    }
    no_escape_action = {
        "type": "CERTIFY_NO_ESCAPE_BRANCH",
        "target": "s6_goal_no_escape",
        "branch_id": "branch_unit",
        "certificate_id": "no_escape_cert_unit",
    }
    status_only_verify = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal_no_escape",
        "lemma_id": "s6_unit_lemma",
        "verifier": "strict_theorem_verifier",
        "status": "ACCEPT",
    }
    nodes = {
        "s3:unit": {"node_id": "s3:unit", "node_type": "S3_TRANSITION", "status": "ACCEPTED", "state": s3_state, "accepted_actions": _accepted(s3_action)},
        "coverage:coverage_cert_unit": {
            "node_id": "coverage:coverage_cert_unit",
            "node_type": "COVERAGE_CERTIFICATE",
            "status": "ACCEPTED",
            "state": s6_state,
            "accepted_actions": _accepted(coverage_action),
        },
        "s6_lift:lifting_cert_unit": {
            "node_id": "s6_lift:lifting_cert_unit",
            "node_type": "S4_LIFT",
            "status": "ACCEPTED",
            "state": s6_state,
            "accepted_actions": _accepted(lift_action),
        },
        "induction:base_case_cert_unit": {
            "node_id": "induction:base_case_cert_unit",
            "node_type": "INDUCTION_CLOSURE",
            "status": "ACCEPTED",
            "state": s6_state,
            "accepted_actions": _accepted(induction_action),
        },
        "no_escape:no_escape_cert_unit": {
            "node_id": "no_escape:no_escape_cert_unit",
            "node_type": "NO_ESCAPE_CERTIFICATE",
            "status": "ACCEPTED",
            "state": s6_state,
            "accepted_actions": _accepted(no_escape_action),
        },
        "s6_lemma:s6_unit_lemma": {
            "node_id": "s6_lemma:s6_unit_lemma",
            "node_type": "S6_LEMMA",
            "status": "ACCEPTED",
            "state": s6_state,
            "source": {"kind": "s6_blocker", "blocker_id": "blocker_unit", "blocker_type": "no_escape", "target": "s6_goal_no_escape"},
            "evidence": {
                "lemma_id": "s6_unit_lemma",
                "coverage_certificate": "coverage_cert_unit",
                "lifting_certificate": "lifting_cert_unit",
                "base_case_certificate": "base_case_cert_unit",
                "no_escape_certificate": "no_escape_cert_unit",
            },
            "candidate_actions": [status_only_verify],
            "accepted_actions": _accepted(status_only_verify, reason="status-id lemma acceptance"),
        },
    }
    return {"schema": "collatz_lab.proof_action_theorem_dependency_graph", "version": 1, "nodes": nodes, "edges": [], "open": []}


def test_run023_patches_s6_status_only_acceptance_and_replays_manifest(tmp_path) -> None:
    graph_path = tmp_path / "graph.json"
    trace_path = tmp_path / "trace.jsonl"
    transition_path = tmp_path / "parent_transition_certificates.jsonl"
    graph = _tiny_graph()
    trace_rows = [
        {
            "node_id": "s6_lemma:s6_unit_lemma",
            "node_type": "S6_LEMMA",
            "action": graph["nodes"]["s6_lemma:s6_unit_lemma"]["accepted_actions"][0]["action"],
            "verifier_check": {"accepted": True, "reason": "status-id lemma acceptance", "status": "ACCEPT"},
        }
    ]
    graph_path.write_text(json.dumps(graph, sort_keys=True), encoding="utf-8")
    trace_path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in trace_rows) + "\n", encoding="utf-8")
    transition_path.write_text("", encoding="utf-8")
    cfg = tmp_path / "run023.yaml"
    cfg.write_text(
        "\n".join(
            [
                "s6_lemma_payloads:",
                f"  out_dir: {tmp_path / 'out'}",
                f"  proof_graph: {graph_path}",
                f"  accepted_action_trace: {trace_path}",
                f"  parent_transition_certificates: {transition_path}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_exact_s6_lemma_payloads(cfg)
    replay = replay_manifest(tmp_path / "out" / "proof_manifest.json")

    assert result["generated_s6_lemma_certificate_count"] == 1
    assert result["s6_lemma_blockers_before"] == 1
    assert result["s6_lemma_blockers_after"] == 0
    assert result["hash_failure_count"] == 0
    assert {row["node_type"] for row in replay["root_unsound_certificates"]} == {
        "S3_CERTIFICATE",
        "S4_CERTIFICATE",
        "S6_CERTIFICATE",
        "STRICT_THEOREM_TOP_LEVEL",
    }
