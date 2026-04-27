from collatz_lab.variable_depth_transition import build_variable_depth_certificate, exact_variable_depth_transition


def test_exact_variable_depth_transition_lowers_target_depth() -> None:
    row = exact_variable_depth_transition(a=6, r_residue=1, r_depth=12)

    if row["status"] == "PROVED_EXACT_VARIABLE_DEPTH_TRANSITION":
        assert row["target_depth"] == row["r_depth"] - row["h"] - row["a_next"]
        assert row["target_depth"] >= 1
        assert row["exactness"]["required_source_depth"] <= row["r_depth"]
    else:
        assert row["status"] in {"CLOSED_BY_DIRECT_BURST_DESCENT", "NEEDS_DEEPER_SOURCE_SPLIT", "TARGET_DEPTH_EXHAUSTED"}


def test_variable_depth_certificate_reports_blockers_for_tiny_depth() -> None:
    report = build_variable_depth_certificate(
        {
            "target_buckets": [
                {"obligation_id": "unresolved_bucket:t=0:a=6:h=1", "a": 6, "h": 1},
            ]
        },
        top_n=1,
        source_depth=3,
        max_states=1000,
    )

    assert report["status"] == "VARIABLE_DEPTH_CERTIFICATE_NOT_READY"
    assert report["ready_for_run7"] is False
    assert report["bad_state_count"] > 0
