from collatz_lab.cycle_certificates import (
    AffineReturnMap,
    apply_affine_return,
    certify_affine_return_map,
    compose_affine_return_maps,
    cycle_height_value,
    fixed_point_info,
    sharp_q23_return_map,
    verify_height_drop,
)


def test_sharp_q23_cycle_certificate() -> None:
    row = sharp_q23_return_map()
    cert = certify_affine_return_map(row, sample_qs=[23, 151, 279])
    assert cert["status"] == "PROVED_HEIGHT_DECREASE_ON_REPEAT"
    assert cert["height"]["linear_form_alpha"] == 601
    assert cert["height"]["linear_form_beta"] == 1
    assert cert["height"]["drop_per_repeat"] == 7
    assert cert["sample_height_drop_passed"] is True


def test_apply_and_height_drop_for_sharp_map() -> None:
    row = sharp_q23_return_map()
    assert apply_affine_return(row, 23) == 131
    assert verify_height_drop(row, 23)
    assert cycle_height_value(row, 131) == cycle_height_value(row, 23) - 7


def test_compose_two_sharp_returns() -> None:
    row = sharp_q23_return_map()
    composed = compose_affine_return_maps([row, row], name="twice")
    assert composed.A == 729 * 729
    assert composed.B == 729 + 128
    assert composed.D == 128 * 128
    cert = certify_affine_return_map(composed, sample_qs=[6679])
    assert cert["status"] == "PROVED_HEIGHT_DECREASE_ON_REPEAT"
    assert cert["height"]["drop_per_repeat"] == 14


def test_positive_fixed_point_is_reported() -> None:
    row = AffineReturnMap(name="fixed", A=3, B=-1, D=2)
    info = fixed_point_info(row)
    assert info["positive_integer_fixed_point"] is True
    assert info["q"] == 1
    assert certify_affine_return_map(row)["status"] == "POSITIVE_FIXED_POINT_REQUIRES_EXCEPTION_CHECK"


def test_invalid_even_A_is_rejected() -> None:
    row = AffineReturnMap(name="bad", A=2, B=1, D=2)
    cert = certify_affine_return_map(row)
    assert cert["status"] == "INVALID_AFFINE_RETURN_MAP"
