from collatz_lab.proof_action_run068 import run_high_parent_root_relative_invariant_search
from collatz_lab.proof_scope_status import build_proof_scope_status, read_jsonl


def test_run068_current_repo_fails_with_exact_invariant_gap(tmp_path) -> None:
    result = run_high_parent_root_relative_invariant_search(out=tmp_path / "run068")

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING"
    assert result["accepted_certificate_count"] == 0
    assert result["remaining_uncovered_domain_count"] == 1
    assert result["training_launched"] is False
    assert result["ml_hypothesis_generation_launched"] is False

    remaining = read_jsonl(tmp_path / "run068" / "remaining_uncovered_parent_families.jsonl")
    assert remaining[0]["failure_reason"] == "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING"


def test_scope_guard_can_consume_run068_remaining_family(tmp_path) -> None:
    result = run_high_parent_root_relative_invariant_search(out=tmp_path / "run068")
    scope = build_proof_scope_status(
        strict_replay={"strict_verifier": "PASS", "proof_confidence_percent": 100.0},
        uncovered_families_path=tmp_path / "run068" / "remaining_uncovered_parent_families.jsonl",
    )

    assert result["remaining_uncovered_families"]
    assert scope["scope_status"] == "UNIVERSAL_COLLATZ_ENTRY_FAIL"
    assert scope["public_proof_confidence_percent"] == 0.0
