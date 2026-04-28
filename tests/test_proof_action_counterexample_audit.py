from pathlib import Path

from collatz_lab.parent_states import parent_transition
from collatz_lab.proof_action_counterexample_audit import (
    build_counterexample_family_certificate,
    check_affine_self_map_invariance,
    replay_standard_multicycle,
    write_and_run_standalone_replay,
)


def _unit_edge(**overrides):
    edge = {
        "edge_id": "unit",
        "source_parent": 1,
        "target_parent": 1,
        "A": 1,
        "B": 0,
        "D": 1,
        "standard_steps": 3,
    }
    edge.update(overrides)
    return edge


def test_integrality_invariant_accepts_valid_affine_self_map() -> None:
    result = check_affine_self_map_invariance(residue=1, modulus=2, minimum_q=1, A=1, B=2, D=1)

    assert result["integrality"]["status"] == "PASS"
    assert result["status"] == "PASS"


def test_integrality_invariant_rejects_nonintegral_map() -> None:
    result = check_affine_self_map_invariance(residue=1, modulus=2, minimum_q=1, A=1, B=0, D=2)

    assert result["integrality"]["status"] == "FAIL"
    assert result["status"] == "FAIL"


def test_domain_invariance_accepts_return_to_residue_class() -> None:
    result = check_affine_self_map_invariance(residue=1, modulus=2, minimum_q=1, A=1, B=2, D=1)

    assert result["domain_invariance"]["status"] == "PASS"


def test_domain_invariance_rejects_false_return() -> None:
    result = check_affine_self_map_invariance(residue=1, modulus=2, minimum_q=1, A=1, B=1, D=1)

    assert result["domain_invariance"]["status"] == "FAIL"


def test_growth_proof_rejects_non_growing_map() -> None:
    result = check_affine_self_map_invariance(residue=1, modulus=2, minimum_q=1, A=1, B=0, D=1)

    assert result["growth"]["status"] == "FAIL"


def test_standalone_raw_collatz_replay_catches_bad_expected_boundary(tmp_path: Path) -> None:
    rows = write_and_run_standalone_replay(
        script_path=tmp_path / "standalone.py",
        out_jsonl=tmp_path / "rows.jsonl",
        q0=1,
        edge_sequence=[_unit_edge(B=2)],
        cycle_counts=[1],
    )

    assert rows[0]["status"] == "FAIL"
    assert rows[0]["failure"]["reason"] == "bad_expected_boundary"


def test_project_parent_transition_and_standalone_raw_replay_agree_on_synthetic_cycle() -> None:
    q0 = 1
    parent = parent_transition(1, q0)
    rows = replay_standard_multicycle(q0=q0, edge_sequence=[_unit_edge(standard_steps=parent["standard_steps"])], cycle_counts=[1, 2])

    assert parent["a_next"] == 1
    assert parent["r_next"] == 1
    assert all(row["status"] == "PASS" for row in rows)


def test_counterexample_family_certificate_requires_all_exact_checks() -> None:
    cycle_family = {
        "cycle_id": "unit",
        "start_parent": "P1",
        "q0": "1",
        "composed_map": {"A": "1", "B": "0", "D": "1"},
    }
    invariant = check_affine_self_map_invariance(residue=1, modulus=2, minimum_q=1, A=1, B=0, D=1)
    certificate = build_counterexample_family_certificate(
        cycle_family=cycle_family,
        invariant_check=invariant,
        multicycle_rows=[{"status": "PASS"}],
        project_compare={"status": "PASS"},
    )

    assert certificate is None
