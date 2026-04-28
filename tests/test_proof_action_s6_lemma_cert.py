import json

from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_s6_lemma_cert import certificate_hash, dependency_hash, replay_s6_lemma_certificate
from collatz_lab.proof_action_state import canonical_state


def _dependency_state() -> str:
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="certify no escape dependency",
        goal_id="dep_goal",
        goal_attrs={"kind": "s6_blocker"},
        known_lemmas=["s6_unit_lemma"],
        facts=[
            {
                "kind": "s6_blocker",
                "target": "dep_goal",
                "blocker_id": "blocker_unit",
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


def _dependency_payload() -> dict:
    return {
        "dependency_id": "no_escape:no_escape_cert_unit",
        "kind": "graph_node",
        "node_id": "no_escape:no_escape_cert_unit",
        "node_type": "NO_ESCAPE_CERTIFICATE",
        "state": _dependency_state(),
        "action": {
            "type": "CERTIFY_NO_ESCAPE_BRANCH",
            "target": "dep_goal",
            "branch_id": "branch_unit",
            "certificate_id": "no_escape_cert_unit",
        },
        "verifier_check": {"accepted": True, "status": "ACCEPT"},
    }


def _certificate(*, dependency_payload: dict | None = None) -> dict:
    payload = dependency_payload or _dependency_payload()
    dep_id = str(payload["dependency_id"])
    cert = {
        "schema": "collatz_lab.s6_lemma_certificate",
        "version": 1,
        "type": "S6_LEMMA_EXACT",
        "certificate_id": "s6_lemma_cert_unit",
        "lemma_id": "s6_unit_lemma",
        "blocker_id": "blocker_unit",
        "blocker_type": "no_escape",
        "statement": "Replayable S6 lemma s6_unit_lemma closes no_escape blocker blocker_unit.",
        "proof_payload": {
            "coverage_certificate_ids": ["coverage_cert_unit"],
            "parent_transition_certificate_ids": [],
            "debt_transition_certificate_ids": [],
            "no_escape_certificate_ids": ["no_escape_cert_unit"],
            "residual_parent_certificate_ids": [],
            "induction_or_ranking_certificate_ids": [],
            "depends_on": [dep_id],
            "dependency_hashes": {dep_id: dependency_hash(payload)},
            "dependency_replay_payloads": {dep_id: payload},
        },
        "replay_checks": {
            "all_dependencies_present": True,
            "all_dependencies_hash_match": True,
            "all_dependencies_replay_pass": True,
            "statement_matches_blocker": True,
            "closes_target_blocker": True,
        },
        "status": "PASS",
    }
    cert["certificate_hash"] = certificate_hash(cert)
    return cert


def _s6_state(cert: dict | None = None, *, status_only: bool = False) -> str:
    facts = [
        {
            "kind": "s6_blocker",
            "target": "s6_goal",
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
    ]
    if cert is not None:
        fact = {
            "kind": "s6_lemma_certificate",
            "target": "s6_goal",
            "lemma_id": cert["lemma_id"],
            "blocker_id": cert["blocker_id"],
            "certificate_id": cert["certificate_id"],
            "certificate_hash": cert["certificate_hash"],
            "status": "PASS",
        }
        if not status_only:
            fact["certificate_payload"] = json.dumps(cert, sort_keys=True, separators=(",", ":"))
        facts.append(fact)
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="verify S6 lemma",
        goal_id="s6_goal",
        goal_attrs={"kind": "s6_blocker"},
        known_lemmas=["s6_unit_lemma"],
        facts=facts,
    )


def _verify_action(cert: dict | None = None) -> dict:
    action = {
        "type": "VERIFY_S6_LEMMA",
        "target": "s6_goal",
        "lemma_id": "s6_unit_lemma",
        "verifier": "s6_lemma_certificate_replay",
        "status": "PASS",
    }
    if cert is not None:
        action["certificate_id"] = cert["certificate_id"]
        action["certificate_hash"] = cert["certificate_hash"]
    return action


def test_status_only_s6_lemma_is_rejected() -> None:
    check = verify_action_for_state(
        {"type": "VERIFY_S6_LEMMA", "target": "s6_goal", "lemma_id": "s6_unit_lemma", "verifier": "strict", "status": "ACCEPT"},
        _s6_state(),
    )

    assert not check.accepted
    assert check.status == "REJECT_MISSING_S6_LEMMA_CERTIFICATE"


def test_missing_proof_payload_is_rejected() -> None:
    cert = _certificate()
    broken = dict(cert)
    broken.pop("proof_payload")
    broken["certificate_hash"] = certificate_hash(broken)

    check = verify_action_for_state(_verify_action(broken), _s6_state(broken))

    assert not check.accepted
    assert check.status == "REJECT_S6_LEMMA_DEPENDENCY_FAIL"


def test_missing_dependency_hash_is_rejected() -> None:
    cert = _certificate()
    dep_id = cert["proof_payload"]["depends_on"][0]
    cert["proof_payload"]["dependency_hashes"].pop(dep_id)
    cert["certificate_hash"] = certificate_hash(cert)

    replay = replay_s6_lemma_certificate(cert)

    assert not replay.accepted
    assert replay.status == "REJECT_S6_LEMMA_HASH_MISMATCH"
    assert replay.failures and replay.failures[0]["reason"] == "missing_dependency_hash"


def test_sample_only_dependency_is_rejected() -> None:
    sample_dep = {
        "dependency_id": "s4_transition:sample_only",
        "kind": "parent_transition_certificate",
        "node_id": "s4:sample",
        "node_type": "S4_LIFT",
        "state": _dependency_state(),
        "action": {
            "type": "DERIVE_PARENT_TRANSITION",
            "target": "dep_goal",
            "branch_id": "P3:r7:d5",
            "source_parent": 3,
            "target_parent": 5,
            "valuation": 1,
        },
        "verifier_check": {"accepted": True, "reason": "sample_checks_passed"},
    }
    cert = _certificate(dependency_payload=sample_dep)

    replay = replay_s6_lemma_certificate(cert)

    assert not replay.accepted
    assert replay.status == "REJECT_S6_LEMMA_DEPENDENCY_FAIL"


def test_valid_replayable_s6_lemma_payload_is_accepted() -> None:
    cert = _certificate()

    replay = replay_s6_lemma_certificate(cert)
    check = verify_action_for_state(_verify_action(cert), _s6_state(cert))

    assert replay.accepted
    assert check.accepted
    assert check.reason == "S6 lemma certificate and dependencies replay"
