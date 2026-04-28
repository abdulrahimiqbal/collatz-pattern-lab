import json

from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_s3_debt_cert import (
    build_s3_debt_certificate,
    certificate_hash,
    replay_s3_debt_certificate,
)
from collatz_lab.proof_action_state import canonical_state


def _action() -> dict:
    return {
        "type": "CHECK_DEBT_DECREASE",
        "target": "goal_0",
        "branch_id": "P3:r7:d5",
        "gain_num": 1,
        "gain_den": 2,
        "valuation": 1,
    }


def _state(*, certificate: dict | None = None, status_only_cert: bool = False) -> str:
    facts = [
        {
            "kind": "debt_transition",
            "target": "goal_0",
            "branch_id": "P3:r7:d5",
            "source_parent": 3,
            "target_parent": 5,
            "valuation": 1,
            "gain_num": 1,
            "gain_den": 2,
            "exact_congruence_passed": True,
            "local_descent_passed": True,
        }
    ]
    if certificate is not None:
        fact = {
            "kind": "s3_debt_certificate",
            "target": "goal_0",
            "branch_id": certificate["branch_id"],
            "certificate_id": certificate["certificate_id"],
            "certificate_hash": certificate["certificate_hash"],
            "status": certificate["status"],
        }
        if not status_only_cert:
            fact["certificate_payload"] = json.dumps(certificate, sort_keys=True, separators=(",", ":"))
        facts.append(fact)
    return canonical_state(
        gate="S3_MIXED_MODULUS_DEBT_TRANSITION",
        goal="check debt decrease",
        goal_id="goal_0",
        goal_attrs={"kind": "debt_transition", "branch_id": "P3:r7:d5", "valuation": 1},
        known_lemmas=["mixed_modulus_debt_transition_exactness"],
        facts=facts,
    )


def _certificate() -> dict:
    return build_s3_debt_certificate(action=_action(), state=_state(), node_id="s3:unit")


def test_status_only_s3_debt_state_is_rejected() -> None:
    check = verify_action_for_state(_action(), _state())

    assert not check.accepted
    assert check.status == "REJECT_S3_DEBT_STATUS_ONLY"


def test_status_only_s3_debt_certificate_fact_is_rejected() -> None:
    cert = _certificate()
    check = verify_action_for_state(_action(), _state(certificate=cert, status_only_cert=True))

    assert not check.accepted
    assert check.status == "REJECT_S3_DEBT_STATUS_ONLY"


def test_s3_debt_certificate_rejects_embedded_status_booleans() -> None:
    cert = _certificate()
    cert["exact_congruence_passed"] = True
    cert["certificate_hash"] = certificate_hash(cert)

    replay = replay_s3_debt_certificate(cert, action=_action(), state=_state())

    assert not replay.accepted
    assert replay.status == "REJECT_S3_DEBT_STATUS_ONLY"


def test_missing_congruence_certificate_rejected() -> None:
    cert = _certificate()
    cert.pop("exact_congruence_certificate")

    replay = replay_s3_debt_certificate(cert, action=_action(), state=_state())

    assert not replay.accepted
    assert replay.status == "REJECT_S3_DEBT_REPLAY_FAIL"


def test_missing_local_descent_certificate_rejected() -> None:
    cert = _certificate()
    cert.pop("local_descent_certificate")

    replay = replay_s3_debt_certificate(cert, action=_action(), state=_state())

    assert not replay.accepted
    assert replay.status == "REJECT_S3_DEBT_REPLAY_FAIL"


def test_gain_not_strictly_decreasing_rejected() -> None:
    cert = _certificate()
    cert["gain_num"] = cert["gain_den"]
    cert["debt_measure_definition"]["gain_num"] = cert["gain_num"]
    cert["local_descent_certificate"]["gain_num"] = cert["gain_num"]
    cert["certificate_hash"] = certificate_hash(cert)

    replay = replay_s3_debt_certificate(cert, action=None, state=None)

    assert not replay.accepted
    assert replay.status == "REJECT_S3_DEBT_REPLAY_FAIL"
    assert "gain_num" in replay.reason


def test_valid_exact_s3_debt_certificate_is_accepted() -> None:
    cert = _certificate()

    replay = replay_s3_debt_certificate(cert, action=_action(), state=_state())
    check = verify_action_for_state(_action(), _state(certificate=cert))

    assert replay.accepted
    assert check.accepted
    assert check.reason == "exact S3 debt certificate replays"
