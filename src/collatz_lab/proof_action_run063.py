"""RUN-063 final external audit package gate."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .proof_action_parametric_entry_coverage import REPO_ROOT, read_json, write_json
from .utils import load_yaml


RUN_ID = "RUN-063-final-external-audit-package"


def run_final_audit_gate(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("final_external_audit_run063", {}) if isinstance(cfg.get("final_external_audit_run063"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    run062_path = Path(run_cfg.get("run062_result") or "certificate_store/run062_run_result.json")
    run062 = read_json(run062_path) if run062_path.exists() else {}
    ready = run062.get("formalization_status") == "RUN051_DESCENT_FORMALIZED"
    status = "AUDIT_PACKAGE_READY" if ready else "AUDIT_PACKAGE_BLOCKED"
    status_out = out_dir / "formalization_status.json"
    checklist_out = out_dir / "external_reviewer_checklist.md"
    run_result_out = out_dir / "run_result.json"
    write_json({"schema": "collatz_lab.run063_formalization_status", "version": 1, "run_id": RUN_ID, "status": status}, status_out)
    checklist_out.write_text(
        "# RUN-063 External Audit Package\n\n"
        + ("Audit package may be assembled.\n" if ready else "Blocked until RUN-062 proves the final Lean theorem.\n"),
        encoding="utf-8",
    )
    result = {
        "schema": "collatz_lab.run063_final_external_audit_package",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if ready else "FAIL",
        "formalization_status": status,
        "training_launched": False,
        "search_launched": False,
        "artifacts": {
            "formalization_status": str(status_out),
            "external_reviewer_checklist": str(checklist_out),
            "run_result": str(run_result_out),
        },
    }
    write_json(result, run_result_out)
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    store_result = store / "run063_run_result.json"
    shutil.copy2(run_result_out, store_result)
    result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(result, run_result_out)
    shutil.copy2(run_result_out, store_result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_final_audit_gate(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
