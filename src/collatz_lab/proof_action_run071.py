"""RUN-071 DeepSeek-Prover preparation action."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .deepseek_candidate_verify import RESULTS_PATH, verify_candidate
from .deepseek_goal_bank import DEFAULT_OUT_DIR, REPO_ROOT, display_path, generate_goal_bank
from .deepseek_harvest import HARVEST_PATH, harvest_candidates
from .deepseek_prover_loop import run_deepseek_prover_loop
from .utils import load_jsonl, load_yaml, save_json


RUN_ID = "RUN-071-deepseek-prover-prep"
SCHEMA = "collatz_lab.run071_deepseek_prover_prep"


def _clean_run_files(out_dir: Path) -> None:
    for path in (
        out_dir / "candidate_verification_results.jsonl",
        out_dir / "harvested_theorems.jsonl",
    ):
        if path.exists():
            path.unlink()


def _configured_candidates(run_cfg: dict[str, Any]) -> list[Path]:
    values = run_cfg.get("candidate_files") or []
    if isinstance(values, (str, Path)):
        values = [values]
    candidates: list[Path] = []
    for value in values:
        path = Path(value)
        if not path.is_absolute():
            path = REPO_ROOT / path
        candidates.append(path)
    return candidates


def _highest_level(rows: list[dict[str, Any]]) -> str:
    ordering = [
        "NONE",
        "EXAMPLE_ONLY",
        "FIXED_D_PROVED",
        "P32_SPECIAL_FIXED_D_PROVED",
        "LOW_PARENT_MARGIN_CASE_PROVED",
        "GENERAL_HIGH_PARENT_THEOREM_PROVED",
    ]
    highest = "NONE"
    for row in rows:
        level = str(row.get("progress_level", "NONE"))
        if level in ordering and ordering.index(level) > ordering.index(highest):
            highest = level
    return highest


def run_deepseek_prover_prep(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("deepseek_prover_prep_run071", {})
        if isinstance(cfg.get("deepseek_prover_prep_run071"), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or DEFAULT_OUT_DIR)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    _clean_run_files(out_dir)

    goal_bank = generate_goal_bank(config_path, out=out_dir)
    task_bank = out_dir / "deepseek_tasks.jsonl"
    candidates = _configured_candidates(run_cfg)

    verification_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        target = run_cfg.get("target_theorem")
        expected = run_cfg.get("expected_statement")
        verification_rows.append(
            verify_candidate(
                candidate,
                target_theorem=str(target) if target else None,
                expected_statement=str(expected) if expected else None,
                task_bank_path=task_bank,
                timeout_seconds=int(run_cfg.get("timeout_seconds", 120)),
                write_result=True,
                results_path=out_dir / "candidate_verification_results.jsonl",
            )
        )

    prover_loop: dict[str, Any] | None = None
    endpoint = run_cfg.get("deepseek_endpoint")
    auto_prove = bool(run_cfg.get("auto_prove_enabled", False))
    if auto_prove and endpoint:
        task_id_values = run_cfg.get("task_ids") or []
        if isinstance(task_id_values, str):
            task_id_values = [task_id_values]
        prover_loop = run_deepseek_prover_loop(
            endpoint=str(endpoint),
            task_bank_path=task_bank,
            out_dir=out_dir,
            task_ids=[str(value) for value in task_id_values],
            limit=int(run_cfg["task_limit"]) if run_cfg.get("task_limit") is not None else None,
            attempts_per_goal=int(run_cfg.get("max_attempts_per_goal", 1)),
            max_new_tokens=int(run_cfg.get("max_new_tokens", 1024)),
            temperature=float(run_cfg.get("temperature", 0.6)),
            top_p=float(run_cfg.get("top_p", 0.95)),
            do_sample=bool(run_cfg.get("do_sample", True)),
            seed=int(run_cfg["seed"]) if run_cfg.get("seed") is not None else None,
            service_timeout_seconds=int(run_cfg.get("service_timeout_seconds", 240)),
            lean_timeout_seconds=int(run_cfg.get("timeout_seconds", 120)),
        )
        verification_rows = load_jsonl(out_dir / "candidate_verification_results.jsonl")

    harvest = harvest_candidates(
        [],
        apply=bool(run_cfg.get("harvest_apply", False)),
        timeout_seconds=int(run_cfg.get("timeout_seconds", 120)),
        results_path=out_dir / "candidate_verification_results.jsonl",
        harvest_path=out_dir / "harvested_theorems.jsonl",
    )

    local_results = out_dir / "candidate_verification_results.jsonl"
    local_harvest = out_dir / "harvested_theorems.jsonl"
    local_results.touch(exist_ok=True)
    local_harvest.touch(exist_ok=True)
    if local_results.exists() and not verification_rows:
        verification_rows = load_jsonl(local_results)
    harvested_rows = load_jsonl(local_harvest) if local_harvest.exists() else []
    accepted_count = len([row for row in verification_rows if row.get("status") == "ACCEPTED"])
    harvested_count = len(
        [row for row in harvested_rows if row.get("status") in {"READY_FOR_REVIEW", "HARVESTED"}]
    )
    highest = _highest_level(harvested_rows) if harvested_rows else harvest.get("highest_progress_level", "NONE")

    if highest == "GENERAL_HIGH_PARENT_THEOREM_PROVED":
        status = "HIGH_PARENT_THEOREM_PROVED"
        remaining_gap = None
        next_goal = "rerun strict replay and scope status before exposing global semantic maps"
    elif harvested_count:
        status = "PARTIAL_LEAN_PROOFS_HARVESTED"
        remaining_gap = "odd_entry_parent_levels_ge_33"
        next_goal = "p32_special_root_relative_general"
    elif goal_bank.get("deepseek_status") == "DEEPSEEK_ATTEMPTED_NO_PROOFS":
        status = "DEEPSEEK_ATTEMPTED_NO_PROOFS"
        remaining_gap = "odd_entry_parent_levels_ge_33"
        next_goal = "p32_special_root_relative_general"
    else:
        status = "MANUAL_DEEPSEEK_REQUIRED"
        remaining_gap = "odd_entry_parent_levels_ge_33"
        next_goal = "p32_special_root_relative_d1"

    result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": status,
        "task_count": goal_bank["task_count"],
        "generated_goal_files": goal_bank["generated_goal_files"],
        "deepseek_enabled": goal_bank["deepseek_enabled"],
        "candidate_count": len(candidates),
        "accepted_candidate_count": accepted_count,
        "harvested_theorem_count": harvested_count,
        "highest_progress_level": highest,
        "remaining_high_parent_gap": remaining_gap,
        "next_recommended_goal": next_goal,
        "global_proof_claimed": False,
        "artifacts": {
            **goal_bank["artifacts"],
            "generation_attempts": display_path(out_dir / "deepseek_generation_attempts.jsonl"),
            "generated_candidates": display_path(out_dir / "generated_candidates"),
            "candidate_verification_results": display_path(out_dir / "candidate_verification_results.jsonl"),
            "harvested_theorems": display_path(out_dir / "harvested_theorems.jsonl"),
            "run_result": display_path(out_dir / "run_result.json"),
        },
    }
    if prover_loop is not None:
        result["prover_loop"] = prover_loop
    save_json(result, out_dir / "run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_deepseek_prover_prep(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
