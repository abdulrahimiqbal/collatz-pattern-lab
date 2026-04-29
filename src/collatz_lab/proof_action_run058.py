"""RUN-058 P1 direct descent entry."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_p1_direct_descent import (
    REPO_ROOT,
    RUN_ID,
    build_p1_direct_descent_certificate,
    sha256_file,
    validate_p1_direct_descent_certificate,
    write_json,
)
from .proof_action_parametric_entry_coverage import read_jsonl, write_jsonl
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run058_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def _filter_uncovered_after_p1(uncovered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in uncovered if row.get("family_id") != "odd_entry_parent_level_1"]


def run_p1_direct_descent(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("p1_direct_descent_run058", {}) if isinstance(cfg.get("p1_direct_descent_run058"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    run057_uncovered_path = Path(run_cfg.get("run057_uncovered_parent_families") or "certificate_store/run057_uncovered_parent_families.jsonl")

    cert = build_p1_direct_descent_certificate()
    failures = validate_p1_direct_descent_certificate(cert)
    status = "PASS" if not failures else "FAIL"
    remaining = _filter_uncovered_after_p1(read_jsonl(run057_uncovered_path))

    cert_out = out_dir / "p1_direct_descent_certificate.json"
    remaining_out = out_dir / "remaining_uncovered_parent_families.jsonl"
    status_out = out_dir / "formalization_status.json"
    run_result_out = out_dir / "run_result.json"
    gaps_out = out_dir / "missing_p1_direct_descent_gaps.md"
    write_json(cert, cert_out)
    write_jsonl(remaining, remaining_out)
    gaps_out.write_text(
        "# RUN-058 P1 Direct Descent\n\n"
        + ("P1 direct descent certificate generated successfully.\n" if status == "PASS" else f"Gap: `{failures[0]['reason']}`\n"),
        encoding="utf-8",
    )
    write_json(
        {
            "schema": "collatz_lab.run058_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": "P1_DIRECT_DESCENT_PROVED" if status == "PASS" else "P1_DIRECT_DESCENT_ARITHMETIC_GAP",
            "closed_family": "odd_entry_parent_level_1" if status == "PASS" else None,
            "remaining_uncovered_family_count": len(remaining),
        },
        status_out,
    )
    store_cert = _copy_to_store("p1_direct_descent_certificate", cert_out)
    store_remaining = _copy_to_store("remaining_uncovered_parent_families", remaining_out)
    result = {
        "schema": "collatz_lab.run058_p1_direct_descent_entry",
        "version": 1,
        "run_id": RUN_ID,
        "status": status,
        "formalization_status": "P1_DIRECT_DESCENT_PROVED" if status == "PASS" else "P1_DIRECT_DESCENT_ARITHMETIC_GAP",
        "training_launched": False,
        "search_launched": False,
        "failures": failures,
        "closed_family": "odd_entry_parent_level_1" if status == "PASS" else None,
        "remaining_uncovered_families": remaining,
        "source_artifacts": {
            "run057_uncovered_parent_families": {
                "path": str(run057_uncovered_path),
                "sha256": sha256_file(run057_uncovered_path) if run057_uncovered_path.exists() else "",
            }
        },
        "artifacts": {
            "p1_direct_descent_certificate": str(cert_out),
            "remaining_uncovered_parent_families": str(remaining_out),
            "formalization_status": str(status_out),
            "missing_p1_direct_descent_gaps": str(gaps_out),
            "run_result": str(run_result_out),
            "certificate_store_p1_direct_descent_certificate": str(store_cert),
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
    result = run_p1_direct_descent(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
