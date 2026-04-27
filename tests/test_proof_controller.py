from collatz_lab.proof_controller import run_controller, run_fixed_point_controller


def test_run_controller_generates_traces() -> None:
    report, traces = run_controller(
        {
            "open_obligation_count": 1,
            "obligations": [
                {
                    "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
                    "scc_status": "NEEDS_SPLIT",
                    "coverage": {"a": 6, "h": 1, "t": 0},
                }
            ],
        },
        beam_size=3,
        rounds=1,
    )
    assert report["actions_tried"] == 3
    assert traces
    assert report["generated_child_obligations"] >= 1


def test_run_fixed_point_controller_persists_graph() -> None:
    report, traces, graph = run_fixed_point_controller(
        {
            "open_obligation_count": 1,
            "obligations": [
                {
                    "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
                    "scc_status": "NEEDS_SPLIT",
                    "coverage": {"a": 6, "h": 1, "t": 0},
                }
            ],
        },
        beam_size=2,
        max_rounds=1,
    )
    assert report["status"] == "PROOF_CONTROLLER_FIXED_POINT"
    assert traces
    assert graph["summary"]["node_count"] >= 1
    assert graph["nodes"]["unresolved_bucket:t=0:a=6:h=1"]["status"] == "NEEDS_SPLIT"
