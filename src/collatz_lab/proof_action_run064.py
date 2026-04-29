"""RUN-064 high-parent root-relative margin audit."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .proof_action_high_parent_margin import (
    REPO_ROOT,
    RUN_ID,
    build_high_parent_margin_audit,
    load_default_inputs,
    write_json,
    write_jsonl,
)
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run064_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_high_parent_margin_audit(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("high_parent_margin_run064", {}) if isinstance(cfg.get("high_parent_margin_run064"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    semantic_witnesses, s3_roles, enriched_payloads = load_default_inputs(
        semantic_witnesses_path=run_cfg.get("semantic_witnesses", "certificate_store/run048_semantic_witnesses.jsonl"),
        s3_roles_path=run_cfg.get("s3_roles", "certificate_store/run051_s3_semantic_roles.jsonl"),
        enriched_payloads_path=run_cfg.get("enriched_payloads", "certificate_store/run051_enriched_semantic_payloads.jsonl"),
    )
    report, p32_paths, failing_d_values, candidate_margins = build_high_parent_margin_audit(
        s4_semantic_witnesses=semantic_witnesses,
        s3_semantic_roles=s3_roles,
        enriched_semantic_payloads=enriched_payloads,
    )

    report_out = out_dir / "high_parent_margin_report.json"
    p32_paths_out = out_dir / "p32_paths_for_3_power_inputs.jsonl"
    failing_out = out_dir / "failing_d_values.jsonl"
    candidates_out = out_dir / "candidate_margin_certificates.jsonl"
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_high_parent_margin_gaps.md"
    run_result_out = out_dir / "run_result.json"

    write_json(report, report_out)
    write_jsonl(p32_paths, p32_paths_out)
    write_jsonl(failing_d_values, failing_out)
    write_jsonl(candidate_margins, candidates_out)
    write_json(
        {
            "schema": "collatz_lab.run064_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": report["formalization_status"],
            "root_relative_descent_proved": report["status"] == "HIGH_PARENT_MARGIN_PASS",
            "p32_outgoing_s4_path_count": report["available_certificate_inventory"]["p32_outgoing_s4_path_count"],
            "candidate_root_relative_margin_count": report["available_certificate_inventory"]["candidate_root_relative_margin_count"],
        },
        status_out,
    )
    if report["status"] == "HIGH_PARENT_MARGIN_PASS":
        gaps_text = "# RUN-064 High-Parent Root-Relative Margin\n\nNo margin gap remains.\n"
    else:
        gaps_text = (
            "# RUN-064 High-Parent Root-Relative Margin\n\n"
            "- `P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING`\n"
            "- `HIGH_PARENT_CERTIFICATE_INSUFFICIENT`\n\n"
            "The current certificates prove the high-parent transition into `P32`, but they do not expose a certified "
            "P32 proof path or margin bound showing descent below the original high-parent root.\n"
        )
    gaps_out.write_text(gaps_text, encoding="utf-8")

    store_report = _copy_to_store("high_parent_margin_report", report_out)
    store_paths = _copy_to_store("p32_paths_for_3_power_inputs", p32_paths_out)
    store_failing = _copy_to_store("failing_d_values", failing_out)
    store_candidates = _copy_to_store("candidate_margin_certificates", candidates_out)
    result = {
        "schema": "collatz_lab.run064_high_parent_root_relative_margin",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if report["status"] == "HIGH_PARENT_MARGIN_PASS" else "FAIL",
        "formalization_status": report["formalization_status"],
        "failure_reason": report.get("failure_reason"),
        "training_launched": False,
        "search_launched": False,
        "root_relative_descent_proved": report["status"] == "HIGH_PARENT_MARGIN_PASS",
        "p32_outgoing_s4_path_count": report["available_certificate_inventory"]["p32_outgoing_s4_path_count"],
        "candidate_root_relative_margin_count": report["available_certificate_inventory"]["candidate_root_relative_margin_count"],
        "artifacts": {
            "high_parent_margin_report": str(report_out),
            "p32_paths_for_3_power_inputs": str(p32_paths_out),
            "failing_d_values": str(failing_out),
            "candidate_margin_certificates": str(candidates_out),
            "formalization_status": str(status_out),
            "missing_high_parent_margin_gaps": str(gaps_out),
            "run_result": str(run_result_out),
            "certificate_store_high_parent_margin_report": str(store_report),
            "certificate_store_p32_paths_for_3_power_inputs": str(store_paths),
            "certificate_store_failing_d_values": str(store_failing),
            "certificate_store_candidate_margin_certificates": str(store_candidates),
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
    result = run_high_parent_margin_audit(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
