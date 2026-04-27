from collatz_lab.cube_lifter import build_cube_lift_report, congruence_subsets, lift_cube, low_congruence_from_cube
from collatz_lab.cube_compress import Cube


def test_low_congruence_from_cube() -> None:
    assert low_congruence_from_cube(Cube("1001" + "*" * 4, depth=8)) == (9, 4)
    assert low_congruence_from_cube(Cube("1*01" + "*" * 4, depth=8)) is None


def test_congruence_subsets() -> None:
    assert congruence_subsets(9, 5, 9, 4)
    assert not congruence_subsets(1, 3, 9, 4)


def test_lift_q9_cube_to_burst_family() -> None:
    cube = Cube("1001" + "*" * 4, depth=8).to_dict()
    burst = {"families": [{"q_residue": 9, "q_depth": 4, "status": "PROVED_INFINITE_FAMILY"}]}
    result = lift_cube(cube, "k16", burst, {"maps": []})
    assert result["status"] == "PROVED_INFINITE_ANCESTOR_DESCENT"
    assert result["mechanism"] == "forced_burst_family"


def test_build_cube_lift_report_smoke() -> None:
    cube_report = {"sets": {"k16": {"cubes": [Cube("1001" + "*" * 4, depth=8).to_dict()]}}}
    burst = {"families": [{"q_residue": 9, "q_depth": 4, "status": "PROVED_INFINITE_FAMILY"}]}
    report = build_cube_lift_report(cube_report, burst, {"maps": []})
    assert report["overall_infinite_lift_count"] == 1
