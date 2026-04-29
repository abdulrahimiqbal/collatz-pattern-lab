"""RUN-067 P32 special-family transition derivation."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .p32_special_transition import (
    RUN_ID,
    build_p32_special_transition_families,
    build_p32_special_transition_schema,
    build_p32_special_uncovered_domains,
    write_json,
    write_jsonl,
)
from .proof_action_parametric_entry_coverage import REPO_ROOT
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run067_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_p32_special_transition_derivation(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("p32_special_transition_run067", {})
        if isinstance(cfg.get("p32_special_transition_run067"), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    h_max = int(run_cfg.get("h_max", 8))
    b_max = int(run_cfg.get("b_max", 8))
    max_families_raw = run_cfg.get("max_families")
    max_families = int(max_families_raw) if max_families_raw is not None else None

    schema = build_p32_special_transition_schema()
    families = build_p32_special_transition_families(h_max=h_max, b_max=b_max, max_families=max_families)
    uncovered = build_p32_special_uncovered_domains(h_max=h_max, b_max=b_max, families=families)
    accepted_progress = [
        row
        for row in families
        if row.get("root_relative_outcome", {}).get("kind") in {"DIRECT_ROOT_DESCENT", "ROOT_DEBT_DECREASE"}
    ]

    schema_out = out_dir / "p32_special_transition_schema.json"
    families_out = out_dir / "p32_special_transition_families.jsonl"
    uncovered_out = out_dir / "p32_special_uncovered_domains.jsonl"
    status_out = out_dir / "formalization_status.json"
    missing_out = out_dir / "missing_p32_special_transition_gaps.md"
    run_result_out = out_dir / "run_result.json"

    write_json(schema, schema_out)
    write_jsonl(families, families_out)
    write_jsonl(uncovered, uncovered_out)
    status = "P32_SPECIAL_TRANSITIONS_DERIVED" if families else "P32_SPECIAL_TRANSITION_DERIVATION_EMPTY"
    root_status = "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING" if uncovered else "P32_SPECIAL_TRANSITION_COVERAGE_PASS"
    write_json(
        {
            "schema": "collatz_lab.run067_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": root_status,
            "transition_derivation_status": status,
            "family_count": len(families),
            "uncovered_domain_count": len(uncovered),
            "root_relative_progress_family_count": len(accepted_progress),
        },
        status_out,
    )
    missing_out.write_text(
        "# RUN-067 P32 Special-Family Transition Derivation\n\n"
        + (
            "No P32 special transition gap remains.\n"
            if not uncovered
            else "- `HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING`\n"
            "- `P32_SPECIAL_VALUATION_BOUND_INCOMPLETE`\n"
            "- `P32_SPECIAL_TARGET_PARENT_BOUND_INCOMPLETE`\n\n"
            "The P32 special transition schema is exact, but the bounded emitted family list does not close "
            "the full high-parent root-relative theorem. RUN-068 must search for a debt/margin invariant over "
            "these symbolic transition families.\n"
        ),
        encoding="utf-8",
    )

    store_schema = _copy_to_store("p32_special_transition_schema", schema_out)
    store_families = _copy_to_store("p32_special_transition_families", families_out)
    store_uncovered = _copy_to_store("p32_special_uncovered_domains", uncovered_out)
    result = {
        "schema": "collatz_lab.run067_p32_special_transition_derivation",
        "version": 1,
        "run_id": RUN_ID,
        "status": "FAIL" if uncovered else "PASS",
        "formalization_status": root_status,
        "transition_derivation_status": status,
        "training_launched": False,
        "ml_launched": False,
        "symbolic_derivation_launched": True,
        "h_max": h_max,
        "b_max": b_max,
        "family_count": len(families),
        "uncovered_domain_count": len(uncovered),
        "root_relative_progress_family_count": len(accepted_progress),
        "artifacts": {
            "p32_special_transition_schema": str(schema_out),
            "p32_special_transition_families": str(families_out),
            "p32_special_uncovered_domains": str(uncovered_out),
            "formalization_status": str(status_out),
            "missing_p32_special_transition_gaps": str(missing_out),
            "run_result": str(run_result_out),
            "certificate_store_p32_special_transition_schema": str(store_schema),
            "certificate_store_p32_special_transition_families": str(store_families),
            "certificate_store_p32_special_uncovered_domains": str(store_uncovered),
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
    result = run_p32_special_transition_derivation(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
