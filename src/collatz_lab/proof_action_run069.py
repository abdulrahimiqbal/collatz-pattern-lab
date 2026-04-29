"""RUN-069 high-parent accelerated recursion."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .high_parent_symbolic_composer import (
    RUN_ID,
    build_high_parent_accelerated_recursion,
    load_default_inputs,
    write_json,
    write_jsonl,
)
from .proof_action_parametric_entry_coverage import REPO_ROOT
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run069_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_high_parent_accelerated_recursion(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("high_parent_accelerated_recursion_run069", {})
        if isinstance(cfg.get("high_parent_accelerated_recursion_run069"), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    schema, families, run068_obstruction, run068_uncovered = load_default_inputs(
        families_path=run_cfg.get(
            "p32_special_transition_families",
            "certificate_store/run067_p32_special_transition_families.jsonl",
        ),
        schema_path=run_cfg.get(
            "p32_special_transition_schema",
            "certificate_store/run067_p32_special_transition_schema.json",
        ),
        obstruction_path=run_cfg.get(
            "run068_obstruction",
            "certificate_store/run068_minimal_high_parent_invariant_obstruction.json",
        ),
        uncovered_path=run_cfg.get(
            "run068_remaining_uncovered",
            "certificate_store/run068_remaining_uncovered_high_parent_domains.jsonl",
        ),
    )
    result = build_high_parent_accelerated_recursion(
        schema=schema,
        families=families,
        run068_obstruction=run068_obstruction,
        run068_uncovered=run068_uncovered,
        max_depth=int(run_cfg.get("max_depth", 3)),
        max_representatives=int(run_cfg.get("max_representative_branches", 8)),
    )

    composed_out = out_dir / "composed_transition_families.jsonl"
    descent_out = out_dir / "root_relative_descent_certificates.jsonl"
    debt_out = out_dir / "debt_reduction_certificates.jsonl"
    uncovered_out = out_dir / "uncovered_high_parent_domains.jsonl"
    remaining_parent_out = out_dir / "remaining_uncovered_parent_families.jsonl"
    obstruction_out = out_dir / "minimal_high_parent_branch_obstruction.json"
    missing_out = out_dir / "missing_high_parent_accelerated_recursion.md"
    run_result_out = out_dir / "run_result.json"

    write_jsonl(result["composed_transition_families"], composed_out)
    write_jsonl(result["root_relative_descent_certificates"], descent_out)
    write_jsonl(result["debt_reduction_certificates"], debt_out)
    write_jsonl(result["uncovered_high_parent_domains"], uncovered_out)
    write_jsonl(result["remaining_uncovered_parent_families"], remaining_parent_out)
    write_json(result["minimal_high_parent_branch_obstruction"], obstruction_out)
    if result["run_result"]["status"] == "PASS":
        missing_out.write_text(
            "# RUN-069 High-Parent Accelerated Recursion\n\nNo accelerated-recursion gap remains.\n",
            encoding="utf-8",
        )
    else:
        missing_out.write_text(
            "# RUN-069 High-Parent Accelerated Recursion\n\n"
            "- `HIGH_PARENT_ACCELERATED_RECURSION_INCOMPLETE`\n"
            "- `FINITE_SUBSYSTEM_ROOT_RELATIVE_MARGIN_MISSING`\n"
            "- `TARGET_COORDINATE_SPECIAL_3_POWER_FORM_NOT_CERTIFIED`\n\n"
            "RUN-069 composed the exact available P32-special branches. The emitted RUN-067 branches land in "
            "`P1..P8`, so no second accelerated P32-special step is justified by the available schema, and no "
            "root-relative descent or lower-debt certificate was accepted.\n",
            encoding="utf-8",
        )

    store_composed = _copy_to_store("composed_transition_families", composed_out)
    store_descent = _copy_to_store("root_relative_descent_certificates", descent_out)
    store_debt = _copy_to_store("debt_reduction_certificates", debt_out)
    store_uncovered = _copy_to_store("uncovered_high_parent_domains", uncovered_out)
    store_remaining_parent = _copy_to_store("remaining_uncovered_parent_families", remaining_parent_out)
    store_obstruction = _copy_to_store("minimal_high_parent_branch_obstruction", obstruction_out)

    run_result = dict(result["run_result"])
    run_result["artifacts"] = {
        "composed_transition_families": str(composed_out),
        "root_relative_descent_certificates": str(descent_out),
        "debt_reduction_certificates": str(debt_out),
        "uncovered_high_parent_domains": str(uncovered_out),
        "remaining_uncovered_parent_families": str(remaining_parent_out),
        "minimal_high_parent_branch_obstruction": str(obstruction_out),
        "missing_high_parent_accelerated_recursion": str(missing_out),
        "run_result": str(run_result_out),
        "certificate_store_composed_transition_families": str(store_composed),
        "certificate_store_root_relative_descent_certificates": str(store_descent),
        "certificate_store_debt_reduction_certificates": str(store_debt),
        "certificate_store_uncovered_high_parent_domains": str(store_uncovered),
        "certificate_store_remaining_uncovered_parent_families": str(store_remaining_parent),
        "certificate_store_minimal_high_parent_branch_obstruction": str(store_obstruction),
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
    result = run_high_parent_accelerated_recursion(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

