"""RUN-059 high-parent parametric entry."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .proof_action_high_parent_parametric import (
    REPO_ROOT,
    RUN_ID,
    build_high_parent_entry_taxonomy,
    build_high_parent_transition_certificate,
    write_json,
)
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run059_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_high_parent_parametric(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("high_parent_parametric_run059", {}) if isinstance(cfg.get("high_parent_parametric_run059"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    taxonomy = build_high_parent_entry_taxonomy()
    transition_cert = build_high_parent_transition_certificate()
    taxonomy_out = out_dir / "high_parent_entry_taxonomy.json"
    transition_out = out_dir / "high_parent_transition_certificate.json"
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_high_parent_parametric_entry.md"
    run_result_out = out_dir / "run_result.json"
    write_json(taxonomy, taxonomy_out)
    write_json(transition_cert, transition_out)
    write_json(
        {
            "schema": "collatz_lab.run059_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": "FINITE_SYSTEM_ROOT_RELATIVE_DESCENT_GAP",
            "transition_to_p32_proved": True,
            "root_relative_descent_proved": False,
        },
        status_out,
    )
    gaps_out.write_text(
        "# RUN-059 High-Parent Parametric Entry\n\n"
        "- `HIGH_PARENT_DESCENT_BELOW_ROOT_GAP`\n"
        "- `FINITE_SYSTEM_ROOT_RELATIVE_DESCENT_GAP`\n"
        "- `HIGH_PARENT_RANKING_GAP`\n\n"
        "The parametric transition into `P32` is certified, but it is not a descent theorem below the original root.\n",
        encoding="utf-8",
    )
    store_taxonomy = _copy_to_store("high_parent_entry_taxonomy", taxonomy_out)
    store_transition = _copy_to_store("high_parent_transition_certificate", transition_out)
    result = {
        "schema": "collatz_lab.run059_high_parent_parametric_entry",
        "version": 1,
        "run_id": RUN_ID,
        "status": "FAIL",
        "formalization_status": "FINITE_SYSTEM_ROOT_RELATIVE_DESCENT_GAP",
        "training_launched": False,
        "search_launched": False,
        "transition_to_p32_proved": True,
        "root_relative_descent_proved": False,
        "artifacts": {
            "high_parent_entry_taxonomy": str(taxonomy_out),
            "high_parent_transition_certificate": str(transition_out),
            "formalization_status": str(status_out),
            "missing_high_parent_parametric_entry": str(gaps_out),
            "run_result": str(run_result_out),
            "certificate_store_high_parent_entry_taxonomy": str(store_taxonomy),
            "certificate_store_high_parent_transition_certificate": str(store_transition),
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
    result = run_high_parent_parametric(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
