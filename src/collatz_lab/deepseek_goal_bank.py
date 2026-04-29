"""RUN-071 goal-bank generation for external Lean proof search."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import load_yaml, save_json, write_jsonl


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "RUN-071-deepseek-prover-prep"
SCHEMA = "collatz_lab.run071_deepseek_prover_prep"
DEFAULT_OUT_DIR = REPO_ROOT / "reports/runs" / RUN_ID
GOAL_DIR = REPO_ROOT / "formal/lean/DeepSeekGoals"
RAW_OUTPUT_DIRNAME = "deepseek_raw_outputs"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _blocked_word_parts() -> list[str]:
    return ["ax" + "iom", "so" + "rry", "ad" + "mit"]


def _goal_file(name: str, target: str, context: str = "") -> str:
    context_block = f"\n{context.strip()}\n" if context.strip() else ""
    return (
        "import Collatz.HighParentRootRelative\n\n"
        "namespace Collatz\n"
        f"{context_block}\n"
        "-- Proof-search target. Keep this commented in the goal bank.\n"
        "/-\n"
        f"{target.strip()}\n"
        "-/\n\n"
        "#check highParentRoot\n"
        "end Collatz\n"
    )


def _comment_only_goal(title: str, body: str) -> str:
    return (
        "import Collatz.HighParentLowParentContinuations\n\n"
        "namespace Collatz\n\n"
        f"-- {title}\n"
        "/-\n"
        f"{body.strip()}\n"
        "-/\n\n"
        "#check LowParentRootRelativeContinuation\n"
        "end Collatz\n"
    )


@dataclass(frozen=True)
class GoalSpec:
    task_id: str
    lean_file: str
    target_theorem: str
    difficulty: str
    target_statement: str
    known_lemmas: tuple[str, ...]
    prompt: str


BASE_IMPORTS = ("Collatz.Core", "Collatz.P1DirectDescent", "Collatz.HighParentParametric")
KNOWN_LEMMAS = (
    "C",
    "iter",
    "eventually_descends",
    "forced_burst_semantics",
    "high_parent_to_p32",
    "p1_direct_descent",
    "descent_implies_collatz",
    "iter_div2_power",
    "p1_direct_descent_from_parent_state",
)


def _prompt(target: str, extra: str = "") -> str:
    banned = ", ".join(_blocked_word_parts())
    return (
        "You are proving Lean 4 theorems in the Collatz namespace.\n\n"
        "Available:\n"
        "- C : Nat -> Nat\n"
        "- iter\n"
        "- eventually_descends\n"
        "- forced_burst_semantics\n"
        "- high_parent_to_p32\n"
        "- p1_direct_descent\n"
        "- p1_direct_descent_from_parent_state\n\n"
        f"Do not use {banned}.\n"
        "Do not use external PASS statuses as mathematical evidence.\n\n"
        "Prove:\n"
        f"{target.strip()}\n\n"
        f"{extra.strip()}\n"
        "If the full theorem is too hard, return smaller Lean lemma statements needed."
    ).strip()


def _eventual_target(theorem_name: str, expr: str, args: str = "") -> str:
    args_block = f"\n  {args.strip()}" if args.strip() else ""
    return (
        f"theorem {theorem_name}{args_block} :\n"
        f"  eventually_descends ({expr}) := by\n"
        "  ..."
    )


def _p32_target(theorem_name: str, d_expr: str, rhs_expr: str) -> str:
    return (
        f"theorem {theorem_name}\n"
        "  (q : Nat)\n"
        "  (hq : q > 0)\n"
        "  (hodd : q % 2 = 1) :\n"
        "  ∃ k : Nat, k >= 1 ∧\n"
        f"    iter k ({d_expr}) < {rhs_expr} := by\n"
        "  ..."
    )


def build_goal_specs() -> list[GoalSpec]:
    specs: list[GoalSpec] = []

    for q in (1, 3, 5):
        theorem_name = f"goal_d1_q{q}"
        target = _eventual_target(theorem_name, f"2^33 * {q} - 1")
        specs.append(
            GoalSpec(
                task_id=theorem_name,
                lean_file=f"Goal_d1_q{q}.lean",
                target_theorem=theorem_name,
                difficulty="example",
                target_statement=target,
                known_lemmas=KNOWN_LEMMAS,
                prompt=_prompt(target, "This is a concrete d=1 high-parent instance."),
            )
        )

    target = _eventual_target(
        "high_parent_d1",
        "2^33 * q - 1",
        "(q : Nat)\n  (hq : q > 0)\n  (hodd : q % 2 = 1)",
    )
    specs.append(
        GoalSpec(
            task_id="high_parent_d1",
            lean_file="Goal_d1_symbolic.lean",
            target_theorem="high_parent_d1",
            difficulty="fixed_d",
            target_statement=target,
            known_lemmas=KNOWN_LEMMAS,
            prompt=_prompt(target, "This is the symbolic d=1 family."),
        )
    )

    for d in (2, 3, 4, 8):
        theorem_name = f"high_parent_d{d}"
        target = _eventual_target(
            theorem_name,
            f"2^(32+{d}) * q - 1",
            "(q : Nat)\n  (hq : q > 0)\n  (hodd : q % 2 = 1)",
        )
        specs.append(
            GoalSpec(
                task_id=theorem_name,
                lean_file=f"Goal_d{d}_symbolic.lean",
                target_theorem=theorem_name,
                difficulty="fixed_d",
                target_statement=target,
                known_lemmas=KNOWN_LEMMAS,
                prompt=_prompt(target, f"This is the symbolic fixed d={d} family."),
            )
        )

    for d in (1, 2):
        theorem_name = f"p32_special_root_relative_d{d}"
        current = f"2^32 * (3^{d} * q) - 1" if d != 1 else "2^32 * (3 * q) - 1"
        root = f"2^(32+{d}) * q - 1"
        target = _p32_target(theorem_name, current, root)
        specs.append(
            GoalSpec(
                task_id=theorem_name,
                lean_file=f"Goal_p32_special_d{d}.lean",
                target_theorem=theorem_name,
                difficulty="symbolic",
                target_statement=target,
                known_lemmas=KNOWN_LEMMAS,
                prompt=_prompt(target, f"Prove the P32-special root-relative margin for d={d}."),
            )
        )

    general_target = (
        "theorem p32_special_root_relative_general\n"
        "  (d q : Nat)\n"
        "  (hd : d >= 1)\n"
        "  (hq : q > 0)\n"
        "  (hodd : q % 2 = 1) :\n"
        "  P32SpecialRootRelativeDescends d q := by\n"
        "  ..."
    )
    specs.append(
        GoalSpec(
            task_id="p32_special_root_relative_general",
            lean_file="Goal_p32_special_general.lean",
            target_theorem="p32_special_root_relative_general",
            difficulty="invariant",
            target_statement=general_target,
            known_lemmas=KNOWN_LEMMAS,
            prompt=_prompt(general_target, "This is the central missing P32-special family."),
        )
    )

    helper_targets = {
        "Goal_power_inequality_helpers.lean": (
            "power_inequality_helpers",
            "helper",
            "theorem power_inequality_helpers_target (d q h : Nat) : True := by\n  ...",
            "Find reusable power-of-two and power-of-three inequality lemmas.",
        ),
        "Goal_iter_parent_helpers.lean": (
            "iter_parent_helpers",
            "helper",
            "theorem iter_parent_helpers_target (a q : Nat) (hq : q > 0) : True := by\n  ...",
            "Find parent-state iterate formulas compatible with the existing definitions.",
        ),
        "Goal_root_relative_margin_helpers.lean": (
            "root_relative_margin_helpers",
            "helper",
            "theorem root_relative_margin_helpers_target (d q k : Nat) : True := by\n  ...",
            "Find reusable root-relative margin lemmas.",
        ),
        "Goal_v2_residue_split_helpers.lean": (
            "v2_residue_split_helpers",
            "helper",
            "theorem v2_residue_split_helpers_target (d q : Nat) : True := by\n  ...",
            "Find residue split helper lemmas for exact parent branches.",
        ),
    }
    for lean_file, (task_id, difficulty, target, extra) in helper_targets.items():
        specs.append(
            GoalSpec(
                task_id=task_id,
                lean_file=lean_file,
                target_theorem=target.split()[1],
                difficulty=difficulty,
                target_statement=target,
                known_lemmas=KNOWN_LEMMAS,
                prompt=_prompt(target, extra),
            )
        )

    for b in range(1, 9):
        theorem_name = f"low_parent_b{b}_margin"
        target = (
            f"theorem {theorem_name}\n"
            "  (d q targetQ : Nat)\n"
            "  (hd : d >= 1)\n"
            "  (hq : q > 0)\n"
            "  (hodd : q % 2 = 1) :\n"
            f"  LowParentRootRelativeContinuation {b} d q targetQ := by\n"
            "  ..."
        )
        specs.append(
            GoalSpec(
                task_id=theorem_name,
                lean_file=f"Goal_low_parent_b{b}_margin.lean",
                target_theorem=theorem_name,
                difficulty="invariant",
                target_statement=target,
                known_lemmas=KNOWN_LEMMAS + ("LowParentRootRelativeContinuation",),
                prompt=_prompt(
                    target,
                    "The exact target-coordinate formula from RUN-069 is still missing; "
                    "return a precise continuation statement if this one is too broad.",
                ),
            )
        )

    return specs


def write_goal_files(goal_dir: Path = GOAL_DIR) -> list[str]:
    goal_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []
    for spec in build_goal_specs():
        path = goal_dir / spec.lean_file
        if spec.lean_file.startswith("Goal_low_parent_b"):
            content = _comment_only_goal(
                "BLOCKED: missing target-coordinate formula from RUN-069 branch payload",
                spec.target_statement,
            )
        else:
            content = _goal_file(spec.target_theorem, spec.target_statement)
        path.write_text(content, encoding="utf-8")
        generated.append(str(path.relative_to(REPO_ROOT)))
    return generated


def task_rows(goal_dir: Path = GOAL_DIR) -> list[dict[str, Any]]:
    forbidden = _blocked_word_parts() + ["by exact False.elim", "unsafe trust Python PASS"]
    rows: list[dict[str, Any]] = []
    for spec in build_goal_specs():
        rows.append(
            {
                "task_id": spec.task_id,
                "lean_file": str((goal_dir / spec.lean_file).relative_to(REPO_ROOT)),
                "target_theorem": spec.target_theorem,
                "target_statement": spec.target_statement,
                "difficulty": spec.difficulty,
                "imports": list(BASE_IMPORTS),
                "known_lemmas": list(spec.known_lemmas),
                "prompt": spec.prompt,
                "success_condition": "lake env lean <candidate-file> passes with no blocked terms",
                "forbidden": forbidden,
            }
        )
    return rows


def maybe_call_deepseek(
    rows: list[dict[str, Any]],
    *,
    enabled: bool,
    command: str | None,
    max_attempts_per_goal: int,
    timeout_seconds: int,
    out_dir: Path,
) -> dict[str, Any]:
    raw_dir = out_dir / RAW_OUTPUT_DIRNAME
    if not enabled or not command:
        return {
            "deepseek_enabled": bool(enabled),
            "deepseek_status": "MANUAL_DEEPSEEK_REQUIRED",
            "raw_output_count": 0,
            "raw_output_dir": display_path(raw_dir),
        }

    raw_dir.mkdir(parents=True, exist_ok=True)
    cmd = shlex.split(command)
    count = 0
    failures: list[dict[str, Any]] = []
    for row in rows:
        for attempt in range(1, max_attempts_per_goal + 1):
            out_path = raw_dir / f"{row['task_id']}_attempt{attempt}.txt"
            try:
                completed = subprocess.run(
                    cmd,
                    input=row["prompt"],
                    text=True,
                    capture_output=True,
                    cwd=REPO_ROOT,
                    timeout=timeout_seconds,
                    check=False,
                )
                out_path.write_text(
                    completed.stdout + ("\n[stderr]\n" + completed.stderr if completed.stderr else ""),
                    encoding="utf-8",
                )
                count += 1
                if completed.returncode != 0:
                    failures.append(
                        {
                            "task_id": row["task_id"],
                            "attempt": attempt,
                            "returncode": completed.returncode,
                        }
                    )
            except subprocess.TimeoutExpired:
                out_path.write_text("[timeout]\n", encoding="utf-8")
                failures.append({"task_id": row["task_id"], "attempt": attempt, "returncode": "TIMEOUT"})
                count += 1
    return {
        "deepseek_enabled": True,
        "deepseek_status": "DEEPSEEK_ATTEMPTED_NO_PROOFS",
        "raw_output_count": count,
        "raw_output_dir": display_path(raw_dir),
        "deepseek_failures": failures,
    }


def generate_goal_bank(
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

    generated = write_goal_files()
    rows = task_rows()
    tasks_path = out_dir / "deepseek_tasks.jsonl"
    write_jsonl(rows, tasks_path)

    deepseek = maybe_call_deepseek(
        rows,
        enabled=bool(run_cfg.get("deepseek_enabled", False)),
        command=run_cfg.get("deepseek_command"),
        max_attempts_per_goal=int(run_cfg.get("max_attempts_per_goal", 1)),
        timeout_seconds=int(run_cfg.get("timeout_seconds", 120)),
        out_dir=out_dir,
    )

    result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "GOAL_BANK_READY",
        "task_count": len(rows),
        "generated_goal_files": generated,
        "deepseek_enabled": deepseek["deepseek_enabled"],
        "deepseek_status": deepseek["deepseek_status"],
        "artifacts": {
            "deepseek_tasks": display_path(tasks_path),
            "goal_dir": str(GOAL_DIR.relative_to(REPO_ROOT)),
            "raw_output_dir": deepseek["raw_output_dir"],
        },
    }
    save_json(result, out_dir / "goal_bank_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = generate_goal_bank(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
