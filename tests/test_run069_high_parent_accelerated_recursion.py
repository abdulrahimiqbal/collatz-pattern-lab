from collatz_lab.high_parent_domain_partition import merge_congruence
from collatz_lab.high_parent_root_inequality import prove_one_step_root_descent
from collatz_lab.proof_action_run069 import run_high_parent_accelerated_recursion
from collatz_lab.proof_scope_status import build_proof_scope_status, read_jsonl


def test_root_inequality_uses_exact_integer_arithmetic() -> None:
    domain = {
        "d_congruence": {"residue": 1, "modulus": 2, "minimum_d": 1},
        "q_congruence": {"residue": 1, "modulus": 8},
    }

    fail = prove_one_step_root_descent(domain=domain, h=1)
    passed = prove_one_step_root_descent(domain=domain, h=64)

    assert fail["status"] == "FAIL"
    assert fail["uses_float_or_log"] is False
    assert passed["status"] == "PASS"
    assert passed["exact_arithmetic"] is True


def test_domain_partition_rejects_incompatible_residues() -> None:
    merged = merge_congruence({"residue": 1, "modulus": 4}, {"residue": 2, "modulus": 4})

    assert merged["status"] == "INCOMPATIBLE"
    assert merged["reason"] == "RESIDUES_DISAGREE_MOD_GCD"


def test_run069_current_repo_fails_with_branch_obstruction(tmp_path) -> None:
    result = run_high_parent_accelerated_recursion(out=tmp_path / "run069")

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "HIGH_PARENT_ACCELERATED_RECURSION_INCOMPLETE"
    assert result["composed_family_count"] == result["input_family_count"]
    assert result["composed_family_count"] > 0
    assert result["root_relative_descent_certificate_count"] == 0
    assert result["debt_reduction_certificate_count"] == 0
    assert "FINITE_SUBSYSTEM_ROOT_RELATIVE_MARGIN_MISSING" in result["blocked_branch_reasons"]

    remaining = read_jsonl(tmp_path / "run069" / "remaining_uncovered_parent_families.jsonl")
    assert remaining[0]["failure_reason"] == "HIGH_PARENT_ACCELERATED_RECURSION_INCOMPLETE"


def test_scope_guard_can_consume_run069_remaining_family(tmp_path) -> None:
    result = run_high_parent_accelerated_recursion(out=tmp_path / "run069")
    scope = build_proof_scope_status(
        strict_replay={"strict_verifier": "PASS", "proof_confidence_percent": 100.0},
        uncovered_families_path=tmp_path / "run069" / "remaining_uncovered_parent_families.jsonl",
    )

    assert result["remaining_uncovered_families"]
    assert scope["scope_status"] == "UNIVERSAL_COLLATZ_ENTRY_FAIL"
    assert scope["public_proof_confidence_percent"] == 0.0
