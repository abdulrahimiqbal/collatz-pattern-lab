from pathlib import Path

from collatz_lab.proof_action_high_parent_parametric import build_high_parent_entry_taxonomy
from collatz_lab.proof_action_p1_direct_descent import (
    build_p1_direct_descent_certificate,
    validate_p1_direct_descent_certificate,
)
from collatz_lab.proof_action_run058 import run_p1_direct_descent
from collatz_lab.proof_action_run059 import run_high_parent_parametric
from collatz_lab.proof_action_run060 import run_entry_closure_maps
from collatz_lab.proof_scope_status import build_proof_scope_status, write_jsonl


def test_scope_guard_downgrades_public_confidence_when_run057_has_gaps(tmp_path: Path) -> None:
    uncovered = tmp_path / "uncovered.jsonl"
    write_jsonl([{"family_id": "odd_entry_parent_level_1"}], uncovered)

    scope = build_proof_scope_status(
        strict_replay={"strict_verifier": "PASS", "verifier_status": "PASS", "proof_confidence_percent": 100.0},
        uncovered_families_path=uncovered,
    )

    assert scope["subsystem_status"] == "CERTIFIED_SUBSYSTEM_PASS"
    assert scope["global_verifier_status"] == "UNIVERSAL_COLLATZ_ENTRY_FAIL"
    assert scope["public_proof_confidence_percent"] == 0.0
    assert scope["subsystem_proof_confidence_percent"] == 100.0


def test_p1_direct_descent_certificate_is_replayable() -> None:
    cert = build_p1_direct_descent_certificate()

    assert not validate_p1_direct_descent_certificate(cert)
    assert cert["arithmetic_witness"]["step_count"] == 3
    assert cert["covered_family_id"] == "odd_entry_parent_level_1"


def test_run058_closes_only_p1_family(tmp_path: Path) -> None:
    uncovered = tmp_path / "uncovered.jsonl"
    write_jsonl(
        [
            {"family_id": "odd_entry_parent_level_1"},
            {"family_id": "odd_entry_parent_levels_ge_33"},
        ],
        uncovered,
    )
    cfg = tmp_path / "run058.yaml"
    out_dir = tmp_path / "run058"
    cfg.write_text(
        "\n".join(
            [
                "p1_direct_descent_run058:",
                f"  out_dir: {out_dir}",
                f"  run057_uncovered_parent_families: {uncovered}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_p1_direct_descent(cfg)

    assert result["status"] == "PASS"
    assert result["closed_family"] == "odd_entry_parent_level_1"
    assert [row["family_id"] for row in result["remaining_uncovered_families"]] == ["odd_entry_parent_levels_ge_33"]


def test_run059_records_transition_but_not_root_descent(tmp_path: Path) -> None:
    result = run_high_parent_parametric(out=tmp_path / "run059")
    taxonomy = build_high_parent_entry_taxonomy()

    assert result["status"] == "FAIL"
    assert result["transition_to_p32_proved"] is True
    assert result["root_relative_descent_proved"] is False
    assert taxonomy["failure_reason"] == "FINITE_SYSTEM_ROOT_RELATIVE_DESCENT_GAP"


def test_run060_stays_closed_when_high_parent_is_open(tmp_path: Path) -> None:
    p1 = tmp_path / "p1.json"
    p1.write_text(
        '{"semantic_validation":{"status":"PASS"}}\n',
        encoding="utf-8",
    )
    high = tmp_path / "high.json"
    high.write_text('{"status":"FAIL","root_relative_descent_proved":false}\n', encoding="utf-8")
    remaining = tmp_path / "remaining.jsonl"
    write_jsonl([{"family_id": "odd_entry_parent_levels_ge_33"}], remaining)
    cfg = tmp_path / "run060.yaml"
    out_dir = tmp_path / "run060"
    cfg.write_text(
        "\n".join(
            [
                "entry_closure_maps_run060:",
                f"  out_dir: {out_dir}",
                f"  p1_certificate: {p1}",
                f"  high_parent_taxonomy: {high}",
                f"  run058_remaining: {remaining}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_entry_closure_maps(cfg)

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "ENTRY_MAP_GAP_HIGH_PARENT"
    assert result["p1_closed"] is True
    assert result["high_parent_closed"] is False
