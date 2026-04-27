from collatz_lab.signature import (
    affine_for_parity_word,
    apply_affine,
    affine_for_shortcut_prefix,
    apply_shortcut_steps,
    initial_odd_burst_length,
    parity_word,
    post_burst_coordinates,
    rows_for_tabular_output,
    signature_for_rule,
    signature_for_q,
    shortcut_prefix_for_standard_steps,
)
from collatz_lab.collatz import collatz_step


def test_forced_six_step_shortcut_burst() -> None:
    q = 17
    n = 64 * q - 1
    assert initial_odd_burst_length(n) == 6
    assert apply_shortcut_steps(n, 6) == 729 * q - 1


def test_post_burst_q_coordinates_for_63_mod_64() -> None:
    coords = post_burst_coordinates(residue=7524799, modulus=2**24, burst_length=6)
    assert coords == ((7524799 + 1) // 64, 2**18)


def test_shortcut_affine_denominator_counts_every_step() -> None:
    assert affine_for_shortcut_prefix([1, 1, 1, 1, 1, 1]) == (729, 665, 64)


def test_standard_descent_signature_includes_shortcut_view() -> None:
    rule = {"modulus": 64, "residue": 3, "suggested_k": 6}
    row = signature_for_rule(rule)
    assert row["standard_affine_A"] == 9
    assert row["standard_affine_B"] == 5
    assert row["standard_affine_D"] == 16
    assert row["shortcut_parity_word"] == "1100"
    assert row["shortcut_aligned_with_standard_k"] is True


def test_shortcut_prefix_detects_unaligned_standard_prefix() -> None:
    prefix, aligned, consumed = shortcut_prefix_for_standard_steps(3, 1)
    assert prefix == []
    assert aligned is False
    assert consumed == 0


def test_standard_affine_for_single_step_words() -> None:
    assert affine_for_parity_word("0") == (1, 0, 2)
    assert affine_for_parity_word("1") == (3, 1, 1)


def test_affine_for_parity_word_matches_collatz_iteration() -> None:
    for n in range(2, 40):
        for k in range(6):
            word = parity_word(n, k)
            a, b, d = affine_for_parity_word(word)
            current = n
            for _ in range(k):
                current = collatz_step(current)
            assert apply_affine(a, b, d, n) == current


def test_signature_for_q_uses_parent_coordinate() -> None:
    row = signature_for_q(9, 16)
    assert row["q"] == 9
    assert row["n"] == 64 * 9 - 1
    assert row["burst_escape"] is True
    assert row["image"] < row["n"]


def test_rows_for_tabular_output_serializes_nested_values() -> None:
    rows = rows_for_tabular_output([{"a": 1, "nested": {"x": [1, 2]}}])
    assert rows == [{"a": 1, "nested": '{"x": [1, 2]}'}]
