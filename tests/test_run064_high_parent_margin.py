from collatz_lab.proof_action_high_parent_margin import build_high_parent_margin_audit
from collatz_lab.proof_action_run064 import run_high_parent_margin_audit


def test_run064_reports_certificate_insufficient_without_p32_margin() -> None:
    s4 = [
        {
            "kind": "S4_PARENT_TRANSITION_SEMANTIC_WITNESS",
            "certificate_id": "edge_p23_p22",
            "source_parent": 23,
            "target_parent": 22,
            "parent_coordinate_map": {"A": 3**23, "D": 2**27},
        }
    ]
    report, p32_paths, failing_d_values, candidates = build_high_parent_margin_audit(
        s4_semantic_witnesses=s4,
        s3_semantic_roles=[],
        enriched_semantic_payloads=[],
    )

    assert report["status"] == "HIGH_PARENT_CERTIFICATE_INSUFFICIENT"
    assert report["failure_reason"] == "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING"
    assert p32_paths == []
    assert [row["d"] for row in failing_d_values] == [1, 2, 8]
    assert candidates == []


def test_run064_detects_passing_root_relative_margin_candidate() -> None:
    candidate = {
        "kind": "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE",
        "root_relative_descent_proved": True,
        "semantic_validation": {"status": "PASS", "failures": []},
    }
    report, _p32_paths, failing_d_values, candidates = build_high_parent_margin_audit(
        s4_semantic_witnesses=[],
        s3_semantic_roles=[],
        enriched_semantic_payloads=[candidate],
    )

    assert report["status"] == "HIGH_PARENT_MARGIN_PASS"
    assert report["failure_reason"] is None
    assert failing_d_values == []
    assert candidates == [candidate]


def test_run064_current_repo_stays_failed_closed(tmp_path) -> None:
    result = run_high_parent_margin_audit(out=tmp_path / "run064")

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "HIGH_PARENT_CERTIFICATE_INSUFFICIENT"
    assert result["failure_reason"] == "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING"
    assert result["root_relative_descent_proved"] is False
    assert result["candidate_root_relative_margin_count"] == 0
