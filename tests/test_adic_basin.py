from collatz_lab.adic_basin import build_adic_basin_certificate, fixed_point_residue_mod_power, repeat_m_condition
from collatz_lab.cycle_certificates import sharp_q23_return_map


def test_fixed_point_residue_for_sharp_map() -> None:
    row = sharp_q23_return_map()
    assert fixed_point_residue_mod_power(row, 7) == 23
    assert fixed_point_residue_mod_power(row, 14) == 6679
    assert fixed_point_residue_mod_power(row, 21) == 55831


def test_repeat_m_condition() -> None:
    row = repeat_m_condition(sharp_q23_return_map(), 2)
    assert row["q_residue"] == 6679
    assert row["q_depth"] == 14


def test_adic_basin_certificate_for_sharp_map() -> None:
    cert = build_adic_basin_certificate(sharp_q23_return_map(), max_repeats=3, q_depth=23)
    assert cert["status"] == "PROVED_NO_INFINITE_REPEAT"
    assert cert["height_drop_per_repeat"] == 7
    rows = cert["q_depth_summary"]["rows"]
    assert rows[0]["exit_after_this_repeat_count"] == 65024
    assert rows[1]["exit_after_this_repeat_count"] == 508
    assert rows[2]["count_at_q_depth"] == 4
