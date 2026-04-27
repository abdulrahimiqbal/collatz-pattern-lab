from collatz_lab.collatz import syracuse_step_odd, v2
from collatz_lab.encode import decode_tokens
from collatz_lab.generate import generate_rows
from collatz_lab.verifier import affine_for_parity_prefix, verify_fixed_residue_descent_exhaustive


def test_affine_for_simple_prefix() -> None:
    # Odd then even: C(C(n)) = (3n + 1) / 2 for values following prefix [1, 0].
    assert affine_for_parity_prefix([1, 0]) == (3, 1, 2)


def test_even_residue_descent_passes() -> None:
    result = verify_fixed_residue_descent_exhaustive(modulus=2, residue=0, k=1, t_limit=100)
    assert result.status == "PASS"


def test_lifted_residue_descent_passes_for_three() -> None:
    result = verify_fixed_residue_descent_exhaustive(modulus=64, residue=3, k=6, t_limit=100)
    assert result.status == "PASS"


def test_generated_syracuse_targets_match_math() -> None:
    rows = generate_rows(
        task="syracuse",
        base=24,
        bits=12,
        n_rows=25,
        lsb_first=True,
        seed=123,
        show_progress=False,
    )
    for row in rows:
        n = int(row["n"])
        assert row["v2_3n_plus_1"] == v2(3 * n + 1)
        assert int(row["syracuse_next"]) == syracuse_step_odd(n)
        assert decode_tokens(row["target_digits"], base=24, lsb_first=True) == syracuse_step_odd(n)
