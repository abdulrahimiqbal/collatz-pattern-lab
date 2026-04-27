from collatz_lab.cycle_certificates import sharp_q23_return_map
from collatz_lab.valuation_closure import (
    build_valuation_closure,
    height_form_for_return_map,
    normalize_form,
    pullback_form_through_map,
)


def test_height_form_for_sharp_map() -> None:
    form = height_form_for_return_map(sharp_q23_return_map())
    assert (form.u, form.v, form.offset) == (601, 1, 0)


def test_normalize_form_tracks_power_of_two_offset() -> None:
    form = normalize_form(12, 20)
    assert (form.u, form.v, form.offset) == (3, 5, 2)


def test_pullback_form_through_sharp_map() -> None:
    sharp = sharp_q23_return_map()
    form = height_form_for_return_map(sharp)
    transfer = pullback_form_through_map(form, sharp)
    assert transfer["valuation_delta"] == -7
    assert transfer["source_form"]["u"] == 601
    assert transfer["source_form"]["v"] == 1


def test_build_valuation_closure() -> None:
    sharp = sharp_q23_return_map()
    report = build_valuation_closure([sharp], max_depth=2, max_forms=8)
    assert report["form_count"] >= 1
    assert report["transfer_count"] >= 1
