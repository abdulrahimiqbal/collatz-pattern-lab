"""RUN-060 rerun global semantic maps after entry-family attempts."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .proof_action_parametric_entry_coverage import REPO_ROOT, read_json, read_jsonl, write_json, write_jsonl
from .utils import load_yaml


RUN_ID = "RUN-060-rerun-global-semantic-maps-after-entry-closure"


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run060_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_entry_closure_maps(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("entry_closure_maps_run060", {}) if isinstance(cfg.get("entry_closure_maps_run060"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    p1_cert_path = Path(run_cfg.get("p1_certificate") or "certificate_store/run058_p1_direct_descent_certificate.json")
    high_parent_taxonomy_path = Path(run_cfg.get("high_parent_taxonomy") or "certificate_store/run059_high_parent_entry_taxonomy.json")
    run058_remaining_path = Path(run_cfg.get("run058_remaining") or "certificate_store/run058_remaining_uncovered_parent_families.jsonl")

    p1_closed = p1_cert_path.exists() and read_json(p1_cert_path).get("semantic_validation", {}).get("status") == "PASS"
    high_parent_taxonomy = read_json(high_parent_taxonomy_path) if high_parent_taxonomy_path.exists() else {}
    high_parent_closed = high_parent_taxonomy.get("status") == "PASS" and high_parent_taxonomy.get("root_relative_descent_proved") is True
    remaining = read_jsonl(run058_remaining_path)
    if p1_closed:
        remaining = [row for row in remaining if row.get("family_id") != "odd_entry_parent_level_1"]
    if high_parent_closed:
        remaining = [row for row in remaining if row.get("family_id") != "odd_entry_parent_levels_ge_33"]

    status = "ENTRY_COVERAGE_CLOSED" if not remaining else "ENTRY_MAP_GAP_HIGH_PARENT"
    entry_map = {
        "schema": "collatz_lab.run060_entry_closure_map",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if not remaining else "FAIL",
        "formalization_status": status,
        "p1_closed": p1_closed,
        "high_parent_closed": high_parent_closed,
        "remaining_uncovered_families": remaining,
        "reflection_gates_reopened": False,
    }
    entry_out = out_dir / "entry_closure_map.json"
    remaining_out = out_dir / "remaining_uncovered_parent_families.jsonl"
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_entry_closure_gaps.md"
    run_result_out = out_dir / "run_result.json"
    write_json(entry_map, entry_out)
    write_jsonl(remaining, remaining_out)
    write_json(
        {
            "schema": "collatz_lab.run060_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": status,
            "run051Entry_check": False,
            "run051Coverage_check": False,
            "reflection_gates_reopened": False,
        },
        status_out,
    )
    gaps_out.write_text(
        "# RUN-060 Entry Closure Maps\n\n"
        + ("Entry coverage is closed.\n" if not remaining else "- `ENTRY_MAP_GAP_HIGH_PARENT`: high-parent root-relative descent remains open.\n"),
        encoding="utf-8",
    )
    store_entry = _copy_to_store("entry_closure_map", entry_out)
    store_remaining = _copy_to_store("remaining_uncovered_parent_families", remaining_out)
    result = {
        "schema": "collatz_lab.run060_entry_closure_maps",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if not remaining else "FAIL",
        "formalization_status": status,
        "training_launched": False,
        "search_launched": False,
        "p1_closed": p1_closed,
        "high_parent_closed": high_parent_closed,
        "remaining_uncovered_families": remaining,
        "artifacts": {
            "entry_closure_map": str(entry_out),
            "remaining_uncovered_parent_families": str(remaining_out),
            "formalization_status": str(status_out),
            "missing_entry_closure_gaps": str(gaps_out),
            "run_result": str(run_result_out),
            "certificate_store_entry_closure_map": str(store_entry),
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
    result = run_entry_closure_maps(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
