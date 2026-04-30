"""RUN-072 DeepSeek high-parent batch prover campaign."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from .deepseek_batch_campaign import (
    DEFAULT_OUT_DIR,
    DEFAULT_TASK_ORDER,
    RUN_ID,
    refresh_run072_task_bank,
    run_deepseek_batch_campaign,
)
from .deepseek_goal_bank import REPO_ROOT, display_path
from .high_parent_theorem_synthesizer import next_missing_theorem, strongest_level, synthesize_high_parent_patterns
from .utils import load_jsonl, load_yaml, save_json


SCHEMA = "collatz_lab.run072_deepseek_high_parent_batch"


def _run_command(command: list[str], *, timeout_seconds: int = 600) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return {
        "command": " ".join(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "passed": completed.returncode == 0,
    }


def _status_from_progress(
    *,
    accepted_rows: list[dict[str, Any]],
    general_proved: bool,
    synthesis: dict[str, Any],
) -> str:
    if general_proved:
        return "HIGH_PARENT_THEOREM_PROVED"
    levels = {str(row.get("proof_level")) for row in accepted_rows if row.get("status") == "ACCEPTED"}
    if synthesis.get("generated_task_count", 0):
        return "DEEPSEEK_GENERALIZATION_CANDIDATE_FOUND"
    if "LOW_PARENT_MARGIN_CASE" in levels:
        return "DEEPSEEK_LOW_PARENT_MARGIN_PROGRESS"
    if "FIXED_D_SYMBOLIC" in levels or "P32_SPECIAL_FIXED_D" in levels:
        return "DEEPSEEK_FIXED_D_PROGRESS"
    if accepted_rows:
        return "HIGH_PARENT_STILL_OPEN"
    return "DEEPSEEK_BATCH_NO_SYMBOLIC_PROGRESS"


def _write_remaining_gap_report(
    out_dir: Path,
    *,
    attempted: list[str],
    accepted_rows: list[dict[str, Any]],
    rejected_count: int,
    next_missing: str,
) -> Path:
    accepted_names = [str(row.get("target_theorem")) for row in accepted_rows if row.get("status") == "ACCEPTED"]
    lines = [
        "# RUN-072 Remaining High-Parent Gap",
        "",
        "Global Collatz is not claimed by this report.",
        "",
        f"- tasks attempted: {len(attempted)}",
        f"- accepted candidates: {len(accepted_rows)}",
        f"- rejected candidates: {rejected_count}",
        f"- strongest theorem harvested: {strongest_level(accepted_rows)}",
        f"- next smallest missing theorem: `{next_missing}`",
        f"- d=1 solved: {'high_parent_d1' in accepted_names}",
        f"- d=2 solved: {'high_parent_d2' in accepted_names}",
        f"- P32-special fixed-d solved: {any(name.startswith('p32_special_root_relative_d') for name in accepted_names)}",
        f"- low-parent margin cases solved: {sorted(name for name in accepted_names if name.startswith('low_parent_b')) or 'none'}",
        "",
        "## DeepSeek Failure Patterns",
        "- rejected candidates remained subject to Lean compiler errors, theorem-statement mismatch, missing imported tactics, or missing symbolic inequalities",
        "- concrete witness repairs are not counted as symbolic high-parent progress",
        "",
        f"Next recommended task: `{next_missing}`",
    ]
    path = out_dir / "remaining_high_parent_gap.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _load_rows(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(path) if path.exists() else []


def _maybe_run_global_gates(out_dir: Path, *, enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {"enabled": False, "commands": []}
    remaining = REPO_ROOT / "certificate_store/run072_remaining_uncovered_parent_families.jsonl"
    remaining.parent.mkdir(parents=True, exist_ok=True)
    remaining.write_text("", encoding="utf-8")
    commands = [
        _run_command([".venv/bin/python", "-m", "collatz_lab.replay_strict_proof", "--manifest", "proof_manifest.json"]),
        _run_command(["lake", "build", "Collatz.HighParentRootRelative"]),
        _run_command(["lake", "build", "Collatz.HighParentLowParentContinuations"]),
        _run_command(["lake", "env", "lean", "formal/lean/CollatzProofCandidate.lean"]),
    ]
    save_json({"schema": "collatz_lab.run072_global_gates", "commands": commands}, out_dir / "global_gate_results.json")
    return {"enabled": True, "commands": commands}


def run_deepseek_high_parent_batch(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("deepseek_high_parent_batch_run072", {})
    if not isinstance(run_cfg, dict):
        run_cfg = {}
    out_dir = Path(out or run_cfg.get("out_dir") or DEFAULT_OUT_DIR)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    task_ids = run_cfg.get("task_ids") or DEFAULT_TASK_ORDER
    if isinstance(task_ids, str):
        task_ids = [task_ids]
    task_ids = [str(item) for item in task_ids]

    endpoint = str(run_cfg.get("endpoint", "http://127.0.0.1:18000"))
    campaign_error: str | None = None
    try:
        campaign = run_deepseek_batch_campaign(
            endpoint=endpoint,
            out_dir=out_dir,
            task_ids=task_ids,
            attempts_per_goal=int(run_cfg.get("attempts_per_goal", 4)),
            feedback_retries_per_failed_task=int(run_cfg.get("feedback_retries_per_failed_task", 2)),
            max_new_tokens=int(run_cfg.get("max_new_tokens", 2048)),
            temperature=float(run_cfg.get("temperature", 0.6)),
            top_p=float(run_cfg.get("top_p", 0.95)),
            do_sample=not bool(run_cfg.get("greedy", True)),
            seed=int(run_cfg["seed"]) if run_cfg.get("seed") is not None else None,
            service_timeout_seconds=int(run_cfg.get("service_timeout_seconds", 360)),
            lean_timeout_seconds=int(run_cfg.get("timeout_seconds", 120)),
            stop_on_first_symbolic_success=bool(run_cfg.get("stop_on_first_symbolic_success", False)),
        )
    except Exception as exc:
        campaign_error = repr(exc)
        task_bank = refresh_run072_task_bank(out_dir)
        campaign = {
            "schema": "collatz_lab.run072_deepseek_batch_campaign",
            "endpoint": endpoint,
            "task_count": len(task_ids),
            "attempt_count": 0,
            "accepted_candidate_count": 0,
            "accepted_symbolic_count": 0,
            "campaign_error": campaign_error,
            "task_bank": task_bank,
            "artifacts": {
                "task_bank": task_bank["artifacts"]["deepseek_tasks"],
                "generation_attempts": display_path(out_dir / "deepseek_generation_attempts.jsonl"),
                "candidate_verification_results": display_path(out_dir / "candidate_verification_results.jsonl"),
                "generated_candidates": display_path(out_dir / "generated_candidates"),
                "raw_output_dir": display_path(out_dir / "deepseek_raw_outputs"),
                "retry_prompts": display_path(out_dir / "retry_prompts"),
                "accepted_candidates": "formal/lean/DeepSeekCandidates/accepted",
                "rejected_candidates": "formal/lean/DeepSeekCandidates/rejected",
            },
        }

    verification_path = out_dir / "candidate_verification_results.jsonl"
    rows = _load_rows(verification_path)
    accepted_rows = [row for row in rows if row.get("status") == "ACCEPTED"]
    rejected_count = len([row for row in rows if row.get("status") == "REJECTED"])
    harvest_path = out_dir / "harvested_theorems.jsonl"
    symbolic_harvest = [row for row in accepted_rows if row.get("proof_level") != "CONCRETE_EXAMPLE"]
    for row in symbolic_harvest:
        row["schema"] = "collatz_lab.run072_harvested_theorem"
    from .utils import write_jsonl

    write_jsonl(symbolic_harvest, harvest_path)
    synthesis = synthesize_high_parent_patterns(accepted_rows=symbolic_harvest, out_dir=out_dir)
    general_proved = any(
        row.get("status") == "ACCEPTED" and row.get("target_theorem") == "high_parent_root_relative_descent"
        for row in accepted_rows
    )
    next_missing = next_missing_theorem(accepted_rows)
    gap_report = _write_remaining_gap_report(
        out_dir,
        attempted=task_ids,
        accepted_rows=accepted_rows,
        rejected_count=rejected_count,
        next_missing=next_missing,
    )
    gates = _maybe_run_global_gates(out_dir, enabled=general_proved and bool(run_cfg.get("run_global_gates_if_proved", True)))

    cert_path = REPO_ROOT / "certificate_store/run072_high_parent_batch_summary.json"
    save_json(
        {
            "schema": "collatz_lab.run072_high_parent_batch_certificate",
            "global_proof_claimed": False,
            "general_high_parent_theorem_proved": general_proved,
            "accepted_symbolic_count": len(symbolic_harvest),
            "next_missing_theorem": next_missing,
        },
        cert_path,
    )

    status = _status_from_progress(accepted_rows=symbolic_harvest, general_proved=general_proved, synthesis=synthesis)
    if status != "HIGH_PARENT_THEOREM_PROVED" and symbolic_harvest:
        status = "HIGH_PARENT_STILL_OPEN"

    result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": status,
        "global_proof_claimed": False,
        "high_parent_theorem_proved": general_proved,
        "task_count": len(task_ids),
        "accepted_candidate_count": len(accepted_rows),
        "accepted_symbolic_count": len(symbolic_harvest),
        "rejected_candidate_count": rejected_count,
        "strongest_theorem_harvested": strongest_level(symbolic_harvest),
        "next_missing_theorem": next_missing,
        "campaign": campaign,
        "campaign_error": campaign_error,
        "synthesis": synthesis,
        "global_gates": gates,
        "artifacts": {
            **campaign["artifacts"],
            "harvested_theorems": display_path(harvest_path),
            "pattern_synthesis_report": synthesis["artifacts"]["pattern_synthesis_report"],
            "generated_generalization_tasks": synthesis["artifacts"]["generated_generalization_tasks"],
            "remaining_high_parent_gap": display_path(gap_report),
            "run072_certificate": display_path(cert_path),
            "run_result": display_path(out_dir / "run_result.json"),
        },
    }
    save_json(result, out_dir / "run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_deepseek_high_parent_batch(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
