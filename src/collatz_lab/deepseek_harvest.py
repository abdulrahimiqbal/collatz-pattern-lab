"""Harvest Lean-checked RUN-071 candidate theorems."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .deepseek_candidate_verify import RESULTS_PATH, verify_candidate
from .deepseek_goal_bank import DEFAULT_OUT_DIR, REPO_ROOT
from .utils import load_jsonl


HARVEST_PATH = DEFAULT_OUT_DIR / "harvested_theorems.jsonl"
SCRATCH_MODULE = REPO_ROOT / "formal/lean/Collatz/DeepSeekScratch.lean"


def _progress_level(theorem_name: str | None) -> str:
    name = theorem_name or ""
    if name == "high_parent_root_relative_descent":
        return "GENERAL_HIGH_PARENT_THEOREM_PROVED"
    if name.startswith("p32_special_root_relative_d"):
        return "P32_SPECIAL_FIXED_D_PROVED"
    if name.startswith("high_parent_d"):
        return "FIXED_D_PROVED"
    if name.startswith("goal_d"):
        return "EXAMPLE_ONLY"
    if name.startswith("low_parent_b"):
        return "LOW_PARENT_MARGIN_CASE_PROVED"
    return "EXAMPLE_ONLY"


def _run_lake_build(timeout_seconds: int) -> dict[str, Any]:
    completed = subprocess.run(
        ["lake", "build"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return {
        "command": "lake build",
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "passed": completed.returncode == 0,
    }


def append_jsonl(row: dict[str, Any], path: Path = HARVEST_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True))
        f.write("\n")


def harvest_candidates(
    candidates: list[str | Path] | None = None,
    *,
    target_theorem: str | None = None,
    expected_statement: str | None = None,
    apply: bool = False,
    timeout_seconds: int = 120,
    results_path: str | Path = RESULTS_PATH,
    harvest_path: str | Path = HARVEST_PATH,
) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    if candidates:
        for candidate in candidates:
            result = verify_candidate(
                candidate,
                target_theorem=target_theorem,
                expected_statement=expected_statement,
                timeout_seconds=timeout_seconds,
            )
            if result["status"] == "ACCEPTED":
                accepted.append(result)
    elif Path(results_path).exists():
        accepted = [row for row in load_jsonl(results_path) if row.get("status") == "ACCEPTED"]

    harvested: list[dict[str, Any]] = []
    for result in accepted:
        theorem_name = result.get("target_theorem") or (
            result.get("theorem_names_detected", [None])[0] if result.get("theorem_names_detected") else None
        )
        row = {
            "schema": "collatz_lab.run071_harvested_theorem",
            "candidate_file": result.get("candidate_file"),
            "target_theorem": theorem_name,
            "progress_level": _progress_level(theorem_name),
            "applied_to_module": None,
            "lake_build": None,
            "status": "READY_FOR_REVIEW",
        }
        if apply:
            src = REPO_ROOT / str(result["candidate_file"])
            dst = SCRATCH_MODULE.parent / f"Harvested_{src.stem}.lean"
            shutil.copy2(src, dst)
            build = _run_lake_build(timeout_seconds)
            row["applied_to_module"] = str(dst.relative_to(REPO_ROOT))
            row["lake_build"] = build
            row["status"] = "HARVESTED" if build["passed"] else "REJECTED_AFTER_BUILD"
        append_jsonl(row, Path(harvest_path))
        harvested.append(row)

    highest = "NONE"
    ordering = [
        "NONE",
        "EXAMPLE_ONLY",
        "FIXED_D_PROVED",
        "P32_SPECIAL_FIXED_D_PROVED",
        "LOW_PARENT_MARGIN_CASE_PROVED",
        "GENERAL_HIGH_PARENT_THEOREM_PROVED",
    ]
    for row in harvested:
        level = row["progress_level"]
        if ordering.index(level) > ordering.index(highest):
            highest = level

    return {
        "schema": "collatz_lab.run071_harvest",
        "accepted_candidate_count": len(accepted),
        "harvested_theorem_count": len([row for row in harvested if row["status"] in {"READY_FOR_REVIEW", "HARVESTED"}]),
        "highest_progress_level": highest,
        "harvested": harvested,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", nargs="*")
    parser.add_argument("--target-theorem")
    parser.add_argument("--expected-statement")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args(argv)
    result = harvest_candidates(
        args.candidates,
        target_theorem=args.target_theorem,
        expected_statement=args.expected_statement,
        apply=args.apply,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
