import json
from pathlib import Path

from collatz_lab.proof_action_run039 import run_run039_from_config


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def test_run039_counterexample_audit_reports_cycle_invariance_fail(tmp_path: Path) -> None:
    cycle_witnesses = tmp_path / "cycle_witnesses.jsonl"
    raw_replay = tmp_path / "raw_replay.jsonl"
    obstruction = tmp_path / "minimal_obstruction.json"
    out_dir = tmp_path / "out"
    edge = {
        "edge_id": "unit",
        "source": "P1",
        "target": "P1",
        "A": "1",
        "B": "0",
        "D": "1",
        "domain_residue": "1",
        "domain_modulus": "2",
        "branch_id": "P1:r1:d1",
        "valuation": "1",
    }
    witness_step = {
        "edge_id": "unit",
        "source": "P1",
        "target": "P1",
        "q": "1",
        "n": "1",
        "q_next": "1",
        "n_next": "1",
        "standard_steps": 3,
    }
    _write_jsonl(
        cycle_witnesses,
        [
            {
                "cycle_id": "unit",
                "edge_ids": ["unit"],
                "classification": "EXECUTABLE_REPEATABLE_NON_DESCENDING",
                "edge_sequence": [edge],
                "cycle_domain": {"residue": "1", "modulus": "2", "minimum_q": "1", "lower_bound": "1"},
                "composed_map": {"A": "1", "B": "0", "D": "1"},
                "self_return_domain": {"status": "PASS", "residue": "1", "modulus": "2", "minimum_q": "1"},
                "minimum_self_return_domain_witness": {
                    "q0": "1",
                    "n0": "1",
                    "q_final": "1",
                    "n_final": "1",
                    "steps": [witness_step],
                    "status": "PASS",
                },
            }
        ],
    )
    _write_jsonl(
        raw_replay,
        [
            {
                "cycle_id": "unit",
                "witness_kind": "minimum_self_return_domain",
                "edge_id": "unit",
                "status": "PASS",
                "parent_transition": {"standard_steps": "3"},
                "raw_collatz": {"status": "PASS"},
            }
        ],
    )
    obstruction.write_text(
        json.dumps(
            {
                "cycle_id": "unit",
                "exact_cycle_domain": {"residue": "1", "modulus": "2", "minimum_q": "1", "lower_bound": "1"},
                "composed_map": {"A": "1", "B": "0", "D": "1"},
                "exact_edge_sequence": [edge],
                "repeat_witness": {"q0": "1", "n0": "1"},
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    cfg = tmp_path / "run039.yaml"
    cfg.write_text(
        "\n".join(
            [
                "counterexample_audit_run039:",
                f"  out_dir: {out_dir}",
                "  cycle_id: unit",
                f"  cycle_witnesses: {cycle_witnesses}",
                f"  raw_collatz_replay: {raw_replay}",
                f"  minimal_invariant_obstruction: {obstruction}",
                "  cycle_counts: [1, 2]",
            ]
        ),
        encoding="utf-8",
    )

    result = run_run039_from_config(cfg)
    certificate = json.loads((out_dir / "counterexample_family_certificate.json").read_text(encoding="utf-8"))

    assert result["status"] == "CYCLE_INVARIANCE_FAIL"
    assert result["standalone_multicycle_all_pass"] is True
    assert certificate["status"] == "FAIL"
