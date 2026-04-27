from collatz_lab.cycle_miner import (
    affine_return_from_parent_return_row,
    build_cycle_mining_report,
    compose_return_sequence,
)


def _sharp_row() -> dict:
    return {
        "a": 6,
        "t": 0,
        "h": 1,
        "q_condition_depth": 7,
        "q_condition_residue": 23,
    }


def test_affine_return_from_parent_return_row_sharp() -> None:
    row = affine_return_from_parent_return_row(_sharp_row())
    assert row.A == 729
    assert row.B == 1
    assert row.D == 128
    assert row.domain_residue == 23
    assert row.domain_depth == 7
    assert row.step_count == 13


def test_compose_sharp_sequence_twice_domain() -> None:
    row = affine_return_from_parent_return_row(_sharp_row())
    composed = compose_return_sequence([row, row], name="twice")
    assert composed.A == 729 * 729
    assert composed.B == 729 + 128
    assert composed.D == 128 * 128
    assert composed.domain_residue == 6679
    assert composed.domain_depth == 14


def test_cycle_mining_report_smoke() -> None:
    report = build_cycle_mining_report({"maps": [_sharp_row()]}, q_depth=23, max_cycle_length=2)
    assert report["return_map_count"] == 1
    assert report["overall_status_counts"]["PROVED_HEIGHT_DECREASE_ON_REPEAT"] == 2
    length2 = report["sequence_reports"]["length_2"]["top_certified_by_coverage"][0]
    assert length2["source_q_residue"] == 6679
    assert length2["source_q_depth"] == 14
