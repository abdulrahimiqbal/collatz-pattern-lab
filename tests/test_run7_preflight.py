import json

from collatz_lab.run7_preflight import build_run7_preflight


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_jsonl(path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_preflight_blocks_without_exact_gates(tmp_path) -> None:
    run_dir = tmp_path / "run"
    rows = [{"run_id": "RUN-X", "attempt_id": f"a{i}"} for i in range(5)]
    _write_jsonl(run_dir / "proof_attempts.jsonl", rows)
    _write_jsonl(tmp_path / "proof_attempts.jsonl", rows)
    _write_json(
        run_dir / "proof_attempt_search.json",
        {
            "attempt_count": 5,
            "selected_attempt_id": "a0",
            "ranked_attempts": [{"variant_id": "v", "focus_step": "S3-global-parent-transitions"}],
        },
    )
    _write_json(
        tmp_path / "replay.json",
        {
            "example_count": 3,
            "repair_action_counts": {
                "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE": 1,
                "PROVE_PARAMETRIC_LIFTING_LEMMA": 1,
                "PROVE_DEBT_CARRYING_INDUCTION": 1,
            },
        },
    )
    _write_json(tmp_path / "debt.json", {"status": "DEBT_INDUCTION_NOT_FIXED", "ready_for_run7": False})
    _write_json(tmp_path / "vd.json", {"status": "VARIABLE_DEPTH_CERTIFICATE_NOT_READY", "ready_for_run7": False})

    report = build_run7_preflight(
        run_id="RUN-X",
        run_dir=run_dir,
        central_attempts_log=tmp_path / "proof_attempts.jsonl",
        replay_report_path=tmp_path / "replay.json",
        debt_gate_path=tmp_path / "debt.json",
        variable_depth_path=tmp_path / "vd.json",
    )

    assert report["ready_for_run7"] is False
    assert "debt_induction_gate_ready" in report["blocking_checks"]
    assert "variable_depth_certificate_ready" in report["blocking_checks"]


def test_preflight_passes_when_required_gates_pass(tmp_path) -> None:
    run_dir = tmp_path / "run"
    rows = [{"run_id": "RUN-X", "attempt_id": f"a{i}"} for i in range(5)]
    _write_jsonl(run_dir / "proof_attempts.jsonl", rows)
    _write_jsonl(tmp_path / "proof_attempts.jsonl", rows)
    _write_json(
        run_dir / "proof_attempt_search.json",
        {
            "attempt_count": 5,
            "selected_attempt_id": "a0",
            "ranked_attempts": [{"variant_id": "v", "focus_step": "S3-global-parent-transitions"}],
        },
    )
    _write_json(
        tmp_path / "replay.json",
        {
            "example_count": 3,
            "repair_action_counts": {
                "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE": 1,
                "PROVE_PARAMETRIC_LIFTING_LEMMA": 1,
                "PROVE_DEBT_CARRYING_INDUCTION": 1,
            },
        },
    )
    _write_json(tmp_path / "debt.json", {"status": "PROVED_DEBT_CARRYING_PARENT_INDUCTION", "ready_for_run7": True})
    _write_json(tmp_path / "vd.json", {"status": "EXACT_VARIABLE_DEPTH_POTENTIAL_PASS", "ready_for_run7": True})

    report = build_run7_preflight(
        run_id="RUN-X",
        run_dir=run_dir,
        central_attempts_log=tmp_path / "proof_attempts.jsonl",
        replay_report_path=tmp_path / "replay.json",
        debt_gate_path=tmp_path / "debt.json",
        variable_depth_path=tmp_path / "vd.json",
    )

    assert report["ready_for_run7"] is True
    assert report["diagnostic_run_allowed"] is True


def test_preflight_force_allows_diagnostic_without_ready(tmp_path) -> None:
    run_dir = tmp_path / "run"
    rows = [{"run_id": "RUN-X", "attempt_id": f"a{i}"} for i in range(5)]
    _write_jsonl(run_dir / "proof_attempts.jsonl", rows)
    _write_jsonl(tmp_path / "proof_attempts.jsonl", rows)
    _write_json(
        run_dir / "proof_attempt_search.json",
        {
            "attempt_count": 5,
            "selected_attempt_id": "a0",
            "ranked_attempts": [{"variant_id": "v", "focus_step": "S3-global-parent-transitions"}],
        },
    )
    _write_json(
        tmp_path / "replay.json",
        {
            "example_count": 3,
            "repair_action_counts": {
                "PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE": 1,
                "PROVE_PARAMETRIC_LIFTING_LEMMA": 1,
                "PROVE_DEBT_CARRYING_INDUCTION": 1,
            },
        },
    )
    _write_json(tmp_path / "debt.json", {"status": "DEBT_INDUCTION_NOT_FIXED", "ready_for_run7": False})
    _write_json(tmp_path / "vd.json", {"status": "VARIABLE_DEPTH_CERTIFICATE_NOT_READY", "ready_for_run7": False})
    _write_json(
        tmp_path / "hp.json",
        {
            "schema": "collatz_lab.high_parent_branch",
            "status": "HIGH_PARENT_BRANCHES_OPEN",
            "ready_for_run7": False,
            "branch_count": 1,
        },
    )

    report = build_run7_preflight(
        run_id="RUN-X",
        run_dir=run_dir,
        central_attempts_log=tmp_path / "proof_attempts.jsonl",
        replay_report_path=tmp_path / "replay.json",
        debt_gate_path=tmp_path / "debt.json",
        variable_depth_path=tmp_path / "vd.json",
        high_parent_branch_path=tmp_path / "hp.json",
        force_diagnostic_run=True,
    )

    assert report["status"] == "FORCED_DIAGNOSTIC_RUN_ALLOWED_WITH_BLOCKERS"
    assert report["ready_for_run7"] is False
    assert report["diagnostic_run_allowed"] is True
    assert "debt_induction_gate_ready" in report["blocking_checks"]
