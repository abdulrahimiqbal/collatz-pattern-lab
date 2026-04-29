"""RUN-066 high-parent self-improving proof search."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .high_parent_cegar import (
    RUN_ID,
    load_default_inputs,
    run_high_parent_cegar,
    write_json,
    write_jsonl,
)
from .proof_action_parametric_entry_coverage import REPO_ROOT
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run066_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_high_parent_self_improving_search(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("high_parent_self_improving_run066", {})
        if isinstance(cfg.get("high_parent_self_improving_run066"), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    semantic_witnesses, margin_report = load_default_inputs(
        semantic_witnesses_path=run_cfg.get("semantic_witnesses", "certificate_store/run048_semantic_witnesses.jsonl"),
        margin_report_path=run_cfg.get("margin_report", "certificate_store/run064_high_parent_margin_report.json"),
    )
    q_samples = [int(value) for value in run_cfg.get("q_samples", [1, 3, 5, 7, 9, 15, 31])]
    powers_two = [int(value) for value in run_cfg.get("residue_powers_two", [1, 2, 3, 4, 5, 6, 8])]
    powers_three = [int(value) for value in run_cfg.get("residue_powers_three", [1, 2, 3, 4])]
    result = run_high_parent_cegar(
        d_min=int(run_cfg.get("d_min", 1)),
        d_max=int(run_cfg.get("d_max", 4)),
        q_samples=q_samples,
        max_steps=int(run_cfg.get("max_steps", 500)),
        semantic_witnesses=semantic_witnesses,
        margin_report=margin_report,
        powers_two=powers_two,
        powers_three=powers_three,
    )

    feature_out = out_dir / "high_parent_feature_table.jsonl"
    candidates_out = out_dir / "candidate_rules.jsonl"
    accepted_out = out_dir / "accepted_high_parent_certificates.jsonl"
    uncovered_out = out_dir / "uncovered_high_parent_domains.jsonl"
    remaining_out = out_dir / "remaining_uncovered_parent_families.jsonl"
    obstruction_out = out_dir / "minimal_high_parent_obstruction.json"
    missing_out = out_dir / "high_parent_missing_invariant.md"
    run_result_out = out_dir / "run_result.json"

    write_jsonl(result["feature_rows"], feature_out)
    write_jsonl(result["candidate_rules"], candidates_out)
    write_jsonl(result["accepted_certificates"], accepted_out)
    write_jsonl(result["uncovered_domains"], uncovered_out)
    write_jsonl(result["remaining_uncovered_parent_families"], remaining_out)
    write_json(result["minimal_obstruction"], obstruction_out)
    if result["run_result"]["status"] == "PASS":
        missing_out.write_text("# RUN-066 High-Parent Missing Invariant\n\nNo missing invariant remains.\n", encoding="utf-8")
    else:
        missing_out.write_text(
            "# RUN-066 High-Parent Missing Invariant\n\n"
            "- `HIGH_PARENT_ROOT_DEBT_INVARIANT_MISSING`\n"
            "- `P32_OUTGOING_ITERATE_FAMILY_MISSING`\n"
            "- `P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING`\n\n"
            "The self-improving loop generated exact diagnostic features and candidate rules, but no candidate "
            "replayed as a universal high-parent certificate. A new root-relative invariant is still required.\n",
            encoding="utf-8",
        )
    write_json(result["run_result"], run_result_out)

    store_feature = _copy_to_store("high_parent_feature_table", feature_out)
    store_candidates = _copy_to_store("candidate_rules", candidates_out)
    store_accepted = _copy_to_store("accepted_high_parent_certificates", accepted_out)
    store_uncovered = _copy_to_store("uncovered_high_parent_domains", uncovered_out)
    store_remaining = _copy_to_store("remaining_uncovered_parent_families", remaining_out)
    store_obstruction = _copy_to_store("minimal_high_parent_obstruction", obstruction_out)
    if result["run_result"]["status"] == "PASS":
        coverage_cert = {
            "kind": "HIGH_PARENT_ENTRY_COVERAGE_CERTIFICATE",
            "run_id": RUN_ID,
            "status": "PASS",
            "accepted_certificate_count": len(result["accepted_certificates"]),
            "root_relative_descent_proved": True,
            "semantic_validation": {"status": "PASS", "failures": []},
        }
        coverage_out = out_dir / "high_parent_entry_coverage_certificate.json"
        write_json(coverage_cert, coverage_out)
        _copy_to_store("high_parent_entry_coverage_certificate", coverage_out)

    run_result = dict(result["run_result"])
    run_result["artifacts"] = {
        "high_parent_feature_table": str(feature_out),
        "candidate_rules": str(candidates_out),
        "accepted_high_parent_certificates": str(accepted_out),
        "uncovered_high_parent_domains": str(uncovered_out),
        "remaining_uncovered_parent_families": str(remaining_out),
        "minimal_high_parent_obstruction": str(obstruction_out),
        "high_parent_missing_invariant": str(missing_out),
        "run_result": str(run_result_out),
        "certificate_store_high_parent_feature_table": str(store_feature),
        "certificate_store_candidate_rules": str(store_candidates),
        "certificate_store_accepted_high_parent_certificates": str(store_accepted),
        "certificate_store_uncovered_high_parent_domains": str(store_uncovered),
        "certificate_store_remaining_uncovered_parent_families": str(store_remaining),
        "certificate_store_minimal_high_parent_obstruction": str(store_obstruction),
    }
    write_json(run_result, run_result_out)
    store_result = _copy_to_store("run_result", run_result_out)
    run_result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(run_result, run_result_out)
    shutil.copy2(run_result_out, store_result)
    return run_result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_high_parent_self_improving_search(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
