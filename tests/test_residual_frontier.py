from collatz_lab.residual_frontier import (
    build_residual_frontier,
    classify_q_residue,
    cube_residues_at_depth,
    mark_existing_cube_coverage,
    normalize_residue,
)


def test_normalize_residue_mod_power() -> None:
    assert normalize_residue(8, 3) == 0
    assert normalize_residue(16, 4) == 0
    assert normalize_residue(9, 4) == 9
    assert normalize_residue(17, 4) == 1


def test_classify_q_residue_for_small_63_mod_64_class() -> None:
    result = classify_q_residue(q_residue=1, q_depth=6, burst_length=6, max_steps=12)
    assert result["status"] in {"CERTIFIED_DESCENT", "UNKNOWN"}
    assert result["n_residue"] == 63


def test_cube_residues_lift_to_requested_depth() -> None:
    cube = {"depth": 2, "mask": 1, "value": 0}
    assert sorted(cube_residues_at_depth(cube, q_depth=3)) == [0, 2, 4, 6]


def test_mark_existing_cube_coverage_counts_union() -> None:
    candidate = {
        "states": [
            {"cube": {"depth": 2, "mask": 1, "value": 0}},
            {"cube": {"depth": 2, "mask": 3, "value": 0}},
        ]
    }
    _, covered = mark_existing_cube_coverage(candidate, q_depth=3)
    assert covered == 4


def test_build_residual_frontier_smoke() -> None:
    candidate = {"states": [{"cube": {"depth": 2, "mask": 3, "value": 0}}]}
    report = build_residual_frontier(
        candidate,
        q_depth=3,
        burst_length=6,
        max_steps=4,
        show_progress=False,
    )
    assert report["total_q_classes"] == 8
    assert report["existing_cube_covered_q_classes"] == 2
    assert report["residual_q_classes"] == 6
