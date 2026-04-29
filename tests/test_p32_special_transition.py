from collatz_lab.burst import v2_int
from collatz_lab.p32_special_transition import (
    build_p32_special_transition_family,
    build_p32_special_transition_families,
    build_p32_special_uncovered_domains,
    multiplicative_order_mod_power_two,
    p32_special_residue,
)


def test_p32_special_residue_determines_exact_h_and_b() -> None:
    h = 2
    b = 3
    period = multiplicative_order_mod_power_two(3, h + b + 1)
    data = p32_special_residue(d_mod=1, d_period=period, h=h, b=b)
    q = data["residue"]
    a_mod = data["a_mod"]

    assert q % 2 == 1
    assert v2_int(a_mod * q - 1) == h
    y = (a_mod * q - 1) >> h
    assert v2_int(y + 1) == b


def test_p32_special_family_records_transition_and_root_outcome() -> None:
    h = 4
    b = 2
    period = multiplicative_order_mod_power_two(3, h + b + 1)
    family = build_p32_special_transition_family(d_mod=1, d_period=period, h=h, b=b)

    assert family["kind"] == "P32_SPECIAL_TRANSITION_FAMILY"
    assert family["transition"]["h"] == h
    assert family["transition"]["target_parent"] == b
    assert family["transition"]["target_q_expr"] == "(3^(32+d)*q + 2^h - 1) / 2^(h+b)"
    assert family["exactness_checks"]["residue_modulus_uses_exactness_bit"] is True
    assert family["root_relative_outcome"]["kind"] in {
        "DIRECT_ROOT_DESCENT",
        "ROOT_DEBT_DECREASE",
        "FINITE_SUBSYSTEM_ENTRY_NEEDS_ROOT_MARGIN",
        "NO_ROOT_RELATIVE_PROGRESS_PROVED",
    }


def test_p32_special_family_generation_and_uncovered_bounds() -> None:
    families = build_p32_special_transition_families(h_max=2, b_max=2)
    uncovered = build_p32_special_uncovered_domains(h_max=2, b_max=2, families=families)

    assert families
    assert any(row["domain_id"] == "p32_special_h_beyond_enumeration_bound" for row in uncovered)
    assert any(row["domain_id"] == "p32_special_b_beyond_enumeration_bound" for row in uncovered)
