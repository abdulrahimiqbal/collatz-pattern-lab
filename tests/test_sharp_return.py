from collatz_lab.collatz import collatz_step
from collatz_lab.sharp_return import (
    R23,
    compose_return_with_certificate,
    pullback_q23_image_class,
    pushforward_q23_class,
    q9_pullback_debt_example,
    sharp_cylinder_residue,
    sharp_height,
    sharp_phi,
    sharp_return_count_lower_bound,
    verify_sharp_height_drop,
    verify_sharp_phi_decreases,
)


def _iterate(n: int, steps: int) -> int:
    current = n
    for _ in range(steps):
        current = collatz_step(current)
    return current


def test_R23_matches_collatz_13_step_return() -> None:
    q = 23
    q1 = R23(q)
    assert q1 == 131
    assert _iterate(64 * q - 1, 13) == 64 * q1 - 1


def test_sharp_height_drops_by_7() -> None:
    for i in range(20):
        q = 23 + 128 * i
        assert verify_sharp_height_drop(q)
        assert sharp_height(R23(q)) == sharp_height(q) - 7


def test_sharp_tower_cylinders() -> None:
    assert sharp_cylinder_residue(1) == (23, 7)
    assert sharp_cylinder_residue(2) == (6679, 14)
    assert sharp_cylinder_residue(3) == (55831, 21)


def test_sharp_return_count_lower_bound_q23() -> None:
    report = sharp_return_count_lower_bound(23)
    assert report["sharp_branch_count"] == 65536
    assert report["guaranteed_exit_counts"] == [
        {"exit_after_returns": 1, "count": 65024},
        {"exit_after_returns": 2, "count": 508},
    ]
    assert report["needs_deeper_bits"] == 4


def test_push_pull_roundtrip() -> None:
    for depth in range(0, 8):
        modulus = 1 << depth
        for residue in range(modulus):
            q_residue, q_depth = pullback_q23_image_class(residue, depth)
            assert pushforward_q23_class(q_residue, q_depth) == (residue, depth)


def test_sharp_phi_decreases() -> None:
    q = 23
    q1 = R23(q)
    assert sharp_phi(64 * q1 - 1, q1) < sharp_phi(64 * q - 1, q)
    assert verify_sharp_phi_decreases(q)


def test_q9_pullback_debt_is_unpaid() -> None:
    result = q9_pullback_debt_example()
    assert result["preimage_condition"] == "q == 791 mod 2^11"
    assert result["status"] == "ANCESTOR_DEBT_UNPAID"
    assert result["debt_paid"] is False


def test_compose_return_with_contracting_certificate_can_pay_debt() -> None:
    result = compose_return_with_certificate(
        None,
        {
            "affine_A": 1,
            "affine_B": 0,
            "affine_D": 1024,
            "preimage_q_residue": 23,
            "preimage_q_depth": 7,
        },
    )
    assert result["status"] == "PROVED_ANCESTOR_DESCENT"
