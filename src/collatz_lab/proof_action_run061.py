"""RUN-061 global Lean semantics gate."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .proof_action_parametric_entry_coverage import REPO_ROOT, read_json, write_json
from .utils import load_yaml


RUN_ID = "RUN-061-global-lean-semantics"


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run061_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_global_lean_semantics(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("global_lean_semantics_run061", {}) if isinstance(cfg.get("global_lean_semantics_run061"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    run060_path = Path(run_cfg.get("run060_result") or "certificate_store/run060_run_result.json")
    run060 = read_json(run060_path) if run060_path.exists() else {}
    if run060.get("formalization_status") != "ENTRY_COVERAGE_CLOSED":
        status = "ENTRY_COVERAGE_SOUNDNESS_BLOCKED"
        gaps = ["ENTRY_MAP_GAP_HIGH_PARENT"]
    else:
        status = "MISSING_APPLICABLE_EDGE_PARTITION"
        gaps = ["MISSING_APPLICABLE_EDGE_PARTITION", "MISSING_KERNEL_TO_PATH_LINK", "MISSING_WELL_FOUNDED_RANK_BRIDGE"]
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_global_lean_semantics_gaps.md"
    run_result_out = out_dir / "run_result.json"
    write_json(
        {
            "schema": "collatz_lab.run061_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": status,
            "checkEntry_sound": False,
            "checkCoverage_sound": False,
            "checkNoEscape_sound": False,
            "checkWellFounded_sound": False,
        },
        status_out,
    )
    gaps_out.write_text("# RUN-061 Global Lean Semantics\n\n" + "\n".join(f"- `{gap}`" for gap in gaps) + "\n", encoding="utf-8")
    result = {
        "schema": "collatz_lab.run061_global_lean_semantics",
        "version": 1,
        "run_id": RUN_ID,
        "status": "FAIL",
        "formalization_status": status,
        "training_launched": False,
        "search_launched": False,
        "gaps": gaps,
        "artifacts": {
            "formalization_status": str(status_out),
            "missing_global_lean_semantics_gaps": str(gaps_out),
            "run_result": str(run_result_out),
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
    result = run_global_lean_semantics(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
