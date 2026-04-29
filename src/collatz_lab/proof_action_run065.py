"""RUN-065 high-parent root-debt system."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .proof_action_high_parent_root_debt import (
    REPO_ROOT,
    RUN_ID,
    build_high_parent_root_debt_system,
    load_default_inputs,
    write_json,
    write_jsonl,
)
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run065_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_high_parent_root_debt_system(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("high_parent_root_debt_run065", {}) if isinstance(cfg.get("high_parent_root_debt_run065"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    semantic_witnesses, s3_roles, margin_report, candidate_margins = load_default_inputs(
        semantic_witnesses_path=run_cfg.get("semantic_witnesses", "certificate_store/run048_semantic_witnesses.jsonl"),
        s3_roles_path=run_cfg.get("s3_roles", "certificate_store/run051_s3_semantic_roles.jsonl"),
        margin_report_path=run_cfg.get("margin_report", "certificate_store/run064_high_parent_margin_report.json"),
        candidate_margin_certificates_path=run_cfg.get(
            "candidate_margin_certificates", "certificate_store/run064_candidate_margin_certificates.jsonl"
        ),
    )
    built = build_high_parent_root_debt_system(
        s4_semantic_witnesses=semantic_witnesses,
        s3_semantic_roles=s3_roles,
        margin_report=margin_report,
        candidate_margin_certificates=candidate_margins,
    )
    report = built["report"]

    states_out = out_dir / "high_parent_root_debt_states.jsonl"
    transitions_out = out_dir / "root_relative_transition_certificates.jsonl"
    ranking_out = out_dir / "high_parent_root_debt_ranking_certificate.json"
    entry_out = out_dir / "high_parent_entry_coverage_certificate.json"
    remaining_out = out_dir / "remaining_uncovered_parent_families.jsonl"
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_high_parent_root_debt_gaps.md"
    run_result_out = out_dir / "run_result.json"

    write_jsonl(built["root_debt_states"], states_out)
    write_jsonl(built["transition_certificates"], transitions_out)
    write_json(built["ranking_certificate"], ranking_out)
    write_json(built["entry_coverage_certificate"], entry_out)
    write_jsonl(built["remaining_uncovered_families"], remaining_out)
    write_json(
        {
            "schema": "collatz_lab.run065_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": report["formalization_status"],
            "root_relative_descent_proved": report["root_relative_descent_proved"],
            "p32_outgoing_s4_transition_count": report["p32_outgoing_s4_transition_count"],
            "root_relative_transition_certificate_count": report["root_relative_transition_certificate_count"],
            "missing_reasons": report["missing_reasons"],
        },
        status_out,
    )
    if report["status"] == "PASS":
        gaps_text = "# RUN-065 High-Parent Root-Debt System\n\nNo root-debt gap remains.\n"
    else:
        gaps_text = (
            "# RUN-065 High-Parent Root-Debt System\n\n"
            "- `HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING`\n"
            "- `P32_OUTGOING_ITERATE_FAMILY_MISSING`\n"
            "- `ROOT_RELATIVE_DEBT_DECREASE_MISSING`\n\n"
            "The current certificates prove the transition into `P32`, but the certified subsystem does not provide "
            "a root-relative path, debt decrease, or lower-debt entry certificate from `P32(3^d*q)`.\n"
        )
    gaps_out.write_text(gaps_text, encoding="utf-8")

    store_states = _copy_to_store("high_parent_root_debt_states", states_out)
    store_transitions = _copy_to_store("root_relative_transition_certificates", transitions_out)
    store_ranking = _copy_to_store("high_parent_root_debt_ranking_certificate", ranking_out)
    store_entry = _copy_to_store("high_parent_entry_coverage_certificate", entry_out)
    store_remaining = _copy_to_store("remaining_uncovered_parent_families", remaining_out)

    result = {
        "schema": "collatz_lab.run065_high_parent_root_debt_system",
        "version": 1,
        "run_id": RUN_ID,
        "status": report["status"],
        "formalization_status": report["formalization_status"],
        "failure_reason": None if report["status"] == "PASS" else "HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING",
        "training_launched": False,
        "ml_launched": False,
        "symbolic_search_launched": True,
        "root_relative_descent_proved": report["root_relative_descent_proved"],
        "remaining_uncovered_families": report["remaining_uncovered_families"],
        "p32_outgoing_s4_transition_count": report["p32_outgoing_s4_transition_count"],
        "root_relative_transition_certificate_count": report["root_relative_transition_certificate_count"],
        "missing_reasons": report["missing_reasons"],
        "artifacts": {
            "high_parent_root_debt_states": str(states_out),
            "root_relative_transition_certificates": str(transitions_out),
            "high_parent_root_debt_ranking_certificate": str(ranking_out),
            "high_parent_entry_coverage_certificate": str(entry_out),
            "remaining_uncovered_parent_families": str(remaining_out),
            "formalization_status": str(status_out),
            "missing_high_parent_root_debt_gaps": str(gaps_out),
            "run_result": str(run_result_out),
            "certificate_store_high_parent_root_debt_states": str(store_states),
            "certificate_store_root_relative_transition_certificates": str(store_transitions),
            "certificate_store_high_parent_root_debt_ranking_certificate": str(store_ranking),
            "certificate_store_high_parent_entry_coverage_certificate": str(store_entry),
            "certificate_store_remaining_uncovered_parent_families": str(store_remaining),
        },
    }
    write_json(result, run_result_out)
    store_result = _copy_to_store("run_result", run_result_out)
    result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(result, run_result_out)
    shutil.copy2(run_result_out, store_result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_high_parent_root_debt_system(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
