from pathlib import Path

from collatz_lab.theorem_report import build_theorem_candidate_report


def test_theorem_candidate_report_handles_missing_sources(tmp_path: Path) -> None:
    paths = {
        "residual_frontier": tmp_path / "missing_residual.json",
        "burst_families": tmp_path / "missing_burst.json",
        "frontier_strata": tmp_path / "missing_strata.json",
        "return_maps": tmp_path / "missing_returns.json",
        "parent_graph": tmp_path / "missing_graph.json",
        "cube_compression": tmp_path / "missing_cubes.json",
        "signature_summary": tmp_path / "missing_signatures.json",
        "potential": tmp_path / "missing_potential.json",
    }
    report = build_theorem_candidate_report(4, paths=paths)
    assert report["verifier_status"] == "THEOREM_CANDIDATE_NOT_COLLATZ_PROOF"
    assert report["known_exact_infinite_families_discovered"] == []
