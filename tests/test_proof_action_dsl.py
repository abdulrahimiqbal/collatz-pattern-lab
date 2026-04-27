import json

import pytest

from collatz_lab.proof_action_dsl import ProofActionError, parse_action, serialize_action


def test_canonical_action_serialization_order() -> None:
    action = {
        "affine_b": 211,
        "type": "PROVE_AFFINE_DESCENT",
        "steps": 11,
        "target": "goal_0",
        "modulus": 128,
        "residue": 37,
        "odd_count": 5,
    }

    assert serialize_action(action) == (
        '{"type":"PROVE_AFFINE_DESCENT","target":"goal_0","modulus":128,'
        '"residue":37,"steps":11,"odd_count":5,"affine_b":211}'
    )


def test_parser_rejects_unknown_type_and_fields() -> None:
    with pytest.raises(ProofActionError):
        parse_action('{"type":"PROOF_PARAGRAPH","target":"goal_0"}')
    with pytest.raises(ProofActionError):
        parse_action('{"type":"UNROLL_PARITY","target":"goal_0","steps":3,"parity_word":"101","extra":1}')


def test_parser_rejects_bad_parity_and_duplicate_keys() -> None:
    with pytest.raises(ProofActionError):
        parse_action('{"type":"UNROLL_PARITY","target":"goal_0","steps":3,"parity_word":"10x"}')
    with pytest.raises(ProofActionError):
        parse_action('{"type":"UNROLL_PARITY","target":"goal_0","steps":3,"steps":3,"parity_word":"101"}')


def test_finite_certificate_schema_is_strict() -> None:
    cert = {
        "n": 3,
        "first_descent_below_n": 2,
        "steps_to_descent": 6,
        "parity_word": "101000",
        "max_value": 16,
        "reaches_terminal_cycle": False,
        "trajectory_hash": "abc",
    }
    text = serialize_action({"type": "CHECK_FINITE_DESCENT", "target": "goal_0", "certificate": cert})
    assert json.loads(text)["certificate"]["n"] == 3
    cert["raw_trajectory"] = [3, 10, 5]
    with pytest.raises(ProofActionError):
        serialize_action({"type": "CHECK_FINITE_DESCENT", "target": "goal_0", "certificate": cert})
