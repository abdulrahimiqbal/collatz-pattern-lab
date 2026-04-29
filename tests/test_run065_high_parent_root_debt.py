from collatz_lab.proof_action_high_parent_root_debt import (
    build_high_parent_root_debt_system,
    build_root_debt_states,
)
from collatz_lab.proof_action_run065 import run_high_parent_root_debt_system
from collatz_lab.proof_scope_status import build_proof_scope_status, read_jsonl


def test_root_debt_states_record_exact_growth_obligation() -> None:
    states = build_root_debt_states([1, 2])

    assert states[0]["debt"] == 1
    assert states[0]["root_expr"] == "2^33*q - 1"
    assert states[0]["current_expr"] == "2^32*3^1*q - 1"
    assert states[0]["direct_current_below_root"] is False
    assert states[0]["direct_current_below_root_check"]["required_inequality"] == "3^1 < 2^1"
    assert states[1]["needed_subsystem_margin"] == "certified P32 continuation must recover factor < (2/3)^2"


def test_root_debt_system_fails_without_p32_or_margin_certificate() -> None:
    built = build_high_parent_root_debt_system(
        s4_semantic_witnesses=[
            {
                "kind": "S4_PARENT_TRANSITION_SEMANTIC_WITNESS",
                "certificate_id": "p23_to_p22",
                "source_parent": 23,
                "target_parent": 22,
            }
        ],
        s3_semantic_roles=[],
        margin_report={"status": "HIGH_PARENT_CERTIFICATE_INSUFFICIENT", "failure_reason": "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING"},
        candidate_margin_certificates=[],
    )
    report = built["report"]

    assert report["status"] == "FAIL"
    assert report["formalization_status"] == "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING"
    assert "P32_OUTGOING_ITERATE_FAMILY_MISSING" in report["missing_reasons"]
    assert built["remaining_uncovered_families"][0]["failure_reason"] == "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING"


def test_root_debt_system_accepts_explicit_passing_margin_candidate() -> None:
    candidate = {
        "kind": "HIGH_PARENT_ROOT_DEBT_RANKING_CERTIFICATE",
        "root_relative_descent_proved": True,
        "semantic_validation": {"status": "PASS", "failures": []},
    }
    built = build_high_parent_root_debt_system(
        s4_semantic_witnesses=[],
        s3_semantic_roles=[],
        margin_report={"status": "HIGH_PARENT_MARGIN_PASS"},
        candidate_margin_certificates=[candidate],
    )
    report = built["report"]

    assert report["status"] == "PASS"
    assert report["root_relative_descent_proved"] is True
    assert report["remaining_uncovered_families"] == []
    assert built["entry_coverage_certificate"]["status"] == "PASS"


def test_run065_current_repo_fails_closed_and_scope_uses_run065_gap(tmp_path) -> None:
    result = run_high_parent_root_debt_system(out=tmp_path / "run065")

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING"
    assert result["root_relative_descent_proved"] is False
    assert result["p32_outgoing_s4_transition_count"] == 0

    remaining = read_jsonl(tmp_path / "run065" / "remaining_uncovered_parent_families.jsonl")
    scope = build_proof_scope_status(
        strict_replay={"strict_verifier": "PASS", "proof_confidence_percent": 100.0},
        uncovered_families_path=tmp_path / "run065" / "remaining_uncovered_parent_families.jsonl",
    )
    assert remaining[0]["failure_reason"] == "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING"
    assert scope["global_verifier_status"] == "UNIVERSAL_COLLATZ_ENTRY_FAIL"
    assert scope["public_proof_confidence_percent"] == 0.0
