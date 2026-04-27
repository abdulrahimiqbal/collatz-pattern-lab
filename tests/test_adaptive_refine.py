from collatz_lab.adaptive_refine import build_refinement_report


def test_small_refinement_counts_sum_to_total() -> None:
    report = build_refinement_report(focus_depth=1, focus_residue=0, extra_depth=3, candidate=None, max_steps=4)
    assert report["total_refinements"] == 8
    assert report["counts_sum"] == 8


def test_refinement_filter_excludes_nonmatching_features() -> None:
    report = build_refinement_report(
        focus_depth=6,
        focus_residue=23,
        extra_depth=2,
        candidate=None,
        max_steps=4,
        feature_filter={"a": 6, "h": 1, "post_burst_mod_64": 63, "returns_to_parent": True},
    )
    assert report["total_refinements"] == 4
    assert report["matching_refinements"] <= 4
    assert report["counts_sum"] == 4
