from collatz_lab.parametric_a import (
    build_parametric_a_report,
    power_period_mod_power,
    verify_power_period,
)


def test_power_period_mod_power() -> None:
    assert power_period_mod_power(1) == 1
    assert power_period_mod_power(2) == 2
    assert power_period_mod_power(4) == 4
    assert verify_power_period(4, sample_count=16)


def test_parametric_a_report_groups_by_periodic_power() -> None:
    report = build_parametric_a_report(a_min=1, a_max=16, depth=5)
    assert report["period"] == 8
    assert report["sample_period_check_passed"]
    assert report["group_count"] <= report["period"]
