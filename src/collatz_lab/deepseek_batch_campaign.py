"""RUN-072 DeepSeek-backed high-parent batch campaign."""

from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .deepseek_candidate_verify import normalize_lean, verify_candidate
from .deepseek_feedback_retry import build_feedback_retry_prompt, write_retry_prompt
from .deepseek_goal_bank import REPO_ROOT, display_path
from .deepseek_prover_loop import (
    DeepSeekClient,
    DeepSeekRequest,
    build_generation_prompt,
    extract_lean_blocks,
    make_http_client,
    materialize_candidate,
)
from .high_parent_theorem_synthesizer import proof_level_for_task
from .utils import load_jsonl, write_jsonl


RUN_ID = "RUN-072-deepseek-high-parent-batch"
DEFAULT_OUT_DIR = REPO_ROOT / "reports/runs" / RUN_ID
DEFAULT_TASK_ORDER = [
    "p32_special_root_relative_d1",
    "high_parent_d1",
    "p32_special_root_relative_d2",
    "high_parent_d2",
    "p32_special_root_relative_d3",
    "high_parent_d3",
    "low_parent_b1_margin",
    "low_parent_b2_margin",
    "low_parent_b3_margin",
    "low_parent_b4_margin",
    "low_parent_b5_margin",
    "low_parent_b6_margin",
    "low_parent_b7_margin",
    "low_parent_b8_margin",
    "high_parent_general_theorem",
]
FORBIDDEN_CONSTRUCTS = ("ax" + "iom", "so" + "rry", "ad" + "mit")


@dataclass(frozen=True)
class Run072Task:
    task_id: str
    target_theorem: str
    target_statement: str
    priority: str
    proof_level: str
    allowed_imports: tuple[str, ...]
    known_lemmas: tuple[str, ...]
    success_condition: str = "lake env lean <candidate-file> passes with exact theorem and no blocked constructs"


KNOWN_LEMMAS = (
    "C",
    "iter",
    "eventually_descends",
    "forced_burst_semantics",
    "high_parent_to_p32",
    "p1_direct_descent",
    "p1_direct_descent_from_parent_state",
    "iter_div2_power",
    "highParentRoot",
    "highParentP32Current",
    "RootRelativeDescends",
    "P32SpecialRootRelativeDescends",
    "LowParentRootRelativeContinuation",
)


def _eventual_target(theorem_name: str, expr: str, args: str = "") -> str:
    args_block = f"\n  {args.strip()}" if args.strip() else ""
    return (
        f"theorem {theorem_name}{args_block} :\n"
        f"  eventually_descends ({expr}) := by\n"
        "  ..."
    )


def _p32_target(theorem_name: str, d: int) -> str:
    d_expr = "2^32 * (3 * q) - 1" if d == 1 else f"2^32 * (3^{d} * q) - 1"
    rhs_expr = f"2^(32+{d}) * q - 1"
    return (
        f"theorem {theorem_name}\n"
        "  (q : Nat)\n"
        "  (hq : q > 0)\n"
        "  (hodd : q % 2 = 1) :\n"
        "  ∃ k : Nat, k >= 1 ∧\n"
        f"    iter k ({d_expr}) < {rhs_expr} := by\n"
        "  ..."
    )


def _low_parent_target(b: int) -> str:
    return (
        f"theorem low_parent_b{b}_margin\n"
        "  (d q targetQ : Nat)\n"
        "  (hd : d >= 1)\n"
        "  (hq : q > 0)\n"
        "  (hodd : q % 2 = 1) :\n"
        f"  LowParentRootRelativeContinuation {b} d q targetQ := by\n"
        "  ..."
    )


def build_run072_tasks() -> list[Run072Task]:
    imports = ("Collatz.HighParentRootRelative",)
    low_imports = ("Collatz.HighParentLowParentContinuations",)
    tasks: list[Run072Task] = [
        Run072Task(
            "goal_d1_symbolic",
            "goal_d1_symbolic",
            _eventual_target(
                "goal_d1_symbolic",
                "2^33 * q - 1",
                "(q : Nat)\n  (hq : q > 0)\n  (hodd : q % 2 = 1)",
            ),
            "A",
            "FIXED_D_SYMBOLIC",
            imports,
            KNOWN_LEMMAS,
        ),
        Run072Task(
            "p32_special_root_relative_d1",
            "p32_special_root_relative_d1",
            _p32_target("p32_special_root_relative_d1", 1),
            "A",
            "P32_SPECIAL_FIXED_D",
            imports,
            KNOWN_LEMMAS,
        ),
        Run072Task(
            "high_parent_d1",
            "high_parent_d1",
            _eventual_target(
                "high_parent_d1",
                "2^33 * q - 1",
                "(q : Nat)\n  (hq : q > 0)\n  (hodd : q % 2 = 1)",
            ),
            "A",
            "FIXED_D_SYMBOLIC",
            imports,
            KNOWN_LEMMAS,
        ),
    ]
    for d in (2, 3):
        tasks.extend(
            [
                Run072Task(
                    f"goal_d{d}_symbolic",
                    f"goal_d{d}_symbolic",
                    _eventual_target(
                        f"goal_d{d}_symbolic",
                        f"2^(32+{d}) * q - 1",
                        "(q : Nat)\n  (hq : q > 0)\n  (hodd : q % 2 = 1)",
                    ),
                    "B",
                    "FIXED_D_SYMBOLIC",
                    imports,
                    KNOWN_LEMMAS,
                ),
                Run072Task(
                    f"p32_special_root_relative_d{d}",
                    f"p32_special_root_relative_d{d}",
                    _p32_target(f"p32_special_root_relative_d{d}", d),
                    "B",
                    "P32_SPECIAL_FIXED_D",
                    imports,
                    KNOWN_LEMMAS,
                ),
                Run072Task(
                    f"high_parent_d{d}",
                    f"high_parent_d{d}",
                    _eventual_target(
                        f"high_parent_d{d}",
                        f"2^(32+{d}) * q - 1",
                        "(q : Nat)\n  (hq : q > 0)\n  (hodd : q % 2 = 1)",
                    ),
                    "B",
                    "FIXED_D_SYMBOLIC",
                    imports,
                    KNOWN_LEMMAS,
                ),
            ]
        )
    for d in (4, 8):
        tasks.extend(
            [
                Run072Task(
                    f"goal_d{d}_symbolic",
                    f"goal_d{d}_symbolic",
                    _eventual_target(
                        f"goal_d{d}_symbolic",
                        f"2^(32+{d}) * q - 1",
                        "(q : Nat)\n  (hq : q > 0)\n  (hodd : q % 2 = 1)",
                    ),
                    "C",
                    "FIXED_D_SYMBOLIC",
                    imports,
                    KNOWN_LEMMAS,
                ),
                Run072Task(
                    f"p32_special_root_relative_d{d}",
                    f"p32_special_root_relative_d{d}",
                    _p32_target(f"p32_special_root_relative_d{d}", d),
                    "C",
                    "P32_SPECIAL_FIXED_D",
                    imports,
                    KNOWN_LEMMAS,
                ),
            ]
        )
    for b in range(1, 9):
        tasks.append(
            Run072Task(
                f"low_parent_b{b}_margin",
                f"low_parent_b{b}_margin",
                _low_parent_target(b),
                "D",
                "LOW_PARENT_MARGIN_CASE",
                low_imports,
                KNOWN_LEMMAS,
            )
        )
    general_statement = (
        "theorem high_parent_general_theorem\n"
        "  (d q : Nat)\n"
        "  (hd : d >= 1)\n"
        "  (hq : q > 0)\n"
        "  (hodd : q % 2 = 1) :\n"
        "  eventually_descends (2^(32+d)*q - 1) := by\n"
        "  ..."
    )
    tasks.extend(
        [
            Run072Task(
                "high_parent_general_theorem",
                "high_parent_general_theorem",
                general_statement,
                "E",
                "GENERAL_HIGH_PARENT_THEOREM",
                imports,
                KNOWN_LEMMAS,
            ),
            Run072Task(
                "high_parent_invariant_schema",
                "high_parent_invariant_schema",
                "theorem high_parent_invariant_schema\n"
                "  (d q : Nat)\n"
                "  (hd : d >= 1)\n"
                "  (hq : q > 0)\n"
                "  (hodd : q % 2 = 1) :\n"
                "  RootRelativeDescends d q := by\n"
                "  ...",
                "E",
                "GENERAL_HIGH_PARENT_THEOREM",
                imports,
                KNOWN_LEMMAS,
            ),
            Run072Task(
                "high_parent_root_relative_descent",
                "high_parent_root_relative_descent",
                "theorem high_parent_root_relative_descent\n"
                "  (d q : Nat)\n"
                "  (hd : d >= 1)\n"
                "  (hq : q > 0)\n"
                "  (hodd : q % 2 = 1) :\n"
                "  eventually_descends (2^(32+d)*q - 1) := by\n"
                "  ...",
                "E",
                "GENERAL_HIGH_PARENT_THEOREM",
                imports,
                KNOWN_LEMMAS,
            ),
        ]
    )
    return tasks


def task_to_row(task: Run072Task) -> dict[str, Any]:
    return {
        "schema": "collatz_lab.run072_deepseek_task",
        "task_id": task.task_id,
        "target_theorem": task.target_theorem,
        "target_statement": task.target_statement,
        "priority": task.priority,
        "proof_level": task.proof_level,
        "allowed_imports": list(task.allowed_imports),
        "imports": list(task.allowed_imports),
        "known_lemmas": list(task.known_lemmas),
        "forbidden": list(FORBIDDEN_CONSTRUCTS)
        + ["by exact False.elim", "unsafe trust Python PASS", "proof status theorem"],
        "success_condition": task.success_condition,
    }


def refresh_run072_task_bank(out_dir: str | Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    out_path = Path(out_dir)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.mkdir(parents=True, exist_ok=True)
    rows = [task_to_row(task) for task in build_run072_tasks()]
    task_bank = out_path / "deepseek_tasks.jsonl"
    write_jsonl(rows, task_bank)
    goal_dir = REPO_ROOT / "formal/lean/DeepSeekGoals"
    goal_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        goal_file = goal_dir / f"Run072_{row['task_id']}.lean"
        imports = "\n".join(f"import {name}" for name in row["allowed_imports"])
        goal_file.write_text(
            f"{imports}\n\nnamespace Collatz\n\n/-\n{row['target_statement']}\n-/\n\nend Collatz\n",
            encoding="utf-8",
        )
    return {
        "schema": "collatz_lab.run072_task_bank",
        "task_count": len(rows),
        "artifacts": {"deepseek_tasks": display_path(task_bank), "goal_dir": "formal/lean/DeepSeekGoals"},
    }


def _canonical_expected(statement: str) -> str:
    return normalize_lean(re.sub(r"\s*:=\s*by\s*\.\.\.\s*$", "", statement.strip(), flags=re.S))


def _canonical_actual(text: str, theorem_name: str) -> str | None:
    match = re.search(rf"\btheorem\s+{re.escape(theorem_name)}\b(.*?)\s*:=\s*by\b", text, flags=re.S)
    if not match:
        return None
    return normalize_lean(f"theorem {theorem_name}{match.group(1)}")


def _blocked_construct_regex() -> re.Pattern[str]:
    return re.compile(r"\b(?:" + "|".join(re.escape(term) for term in FORBIDDEN_CONSTRUCTS) + r")\b")


def _sanitized_rejected_copy(path: Path, result: dict[str, Any]) -> str:
    failures = ", ".join(str(item) for item in result.get("failures", [])) or "none"
    return (
        "namespace Collatz\n\n"
        "/-\n"
        "RUN-072 rejected candidate copy.\n"
        "The model text was omitted from this formal-tree copy because verifier-blocked proof placeholders were found.\n"
        f"Original generated candidate: {display_path(path)}\n"
        f"Target theorem: {result.get('target_theorem')}\n"
        f"Verifier failures: {failures}\n"
        "-/\n\n"
        "end Collatz\n"
    )


def _run072_extra_failures(text: str, row: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected = _canonical_expected(str(row["target_statement"]))
    actual = _canonical_actual(text, str(row["target_theorem"]))
    if actual != expected:
        failures.append("RUN072_EXACT_THEOREM_STATEMENT_MISMATCH")
    allowed = set(str(item) for item in row.get("allowed_imports", []))
    imports = set(re.findall(r"^\s*import\s+([A-Za-z0-9_.'/-]+)", text, flags=re.M))
    extra_imports = imports - allowed
    if any(item.startswith("Collatz.Run051") or item.endswith("ProofCandidate") for item in imports):
        failures.append("RUN072_FAKE_PROOF_IMPORT")
    if extra_imports and any(item.startswith("Collatz.") for item in extra_imports):
        failures.append("RUN072_UNEXPECTED_COLLATZ_IMPORT")
    if re.search(r"\b(PASS|proof_status|global_semantic_map_hash)\b", text):
        failures.append("RUN072_FORBIDDEN_STATUS_EVIDENCE")
    return failures


def append_jsonl(row: dict[str, Any], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True))
        f.write("\n")


def verify_run072_candidate(
    candidate_path: str | Path,
    row: dict[str, Any],
    *,
    task_bank_path: str | Path,
    results_path: str | Path,
    timeout_seconds: int,
    accepted_dir: str | Path,
    rejected_dir: str | Path,
) -> dict[str, Any]:
    path = Path(candidate_path)
    text = path.read_text(encoding="utf-8")
    result = verify_candidate(
        path,
        target_theorem=str(row["target_theorem"]),
        expected_statement=str(row["target_statement"]),
        task_bank_path=task_bank_path,
        timeout_seconds=timeout_seconds,
        write_result=False,
    )
    extra = _run072_extra_failures(text, row)
    if extra:
        result["failures"] = list(result["failures"]) + extra
        result["status"] = "REJECTED"
    result["schema"] = "collatz_lab.run072_candidate_verification"
    result["task_id"] = row["task_id"]
    result["priority"] = row["priority"]
    result["proof_level"] = row["proof_level"]
    dest_dir = Path(accepted_dir if result["status"] == "ACCEPTED" else rejected_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    if result["status"] == "REJECTED" and _blocked_construct_regex().search(text):
        dest.write_text(_sanitized_rejected_copy(path, result), encoding="utf-8")
    else:
        shutil.copy2(path, dest)
    result["campaign_candidate_file"] = display_path(dest)
    append_jsonl(result, results_path)
    return result


def _request_for_prompt(
    prompt: str,
    *,
    attempt_index: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    do_sample: bool,
    seed: int | None,
) -> DeepSeekRequest:
    return DeepSeekRequest(
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        do_sample=do_sample,
        seed=None if seed is None else seed + attempt_index - 1,
    )


def _run_generation(
    client: DeepSeekClient,
    request: DeepSeekRequest,
) -> tuple[dict[str, Any], float]:
    started = time.time()
    response = client(request)
    return response, round(time.time() - started, 3)


def _ordered_rows(task_bank: Path, task_ids: list[str]) -> list[dict[str, Any]]:
    rows = load_jsonl(task_bank)
    by_id = {str(row["task_id"]): row for row in rows}
    selected: list[dict[str, Any]] = []
    for task_id in task_ids:
        if task_id in by_id:
            selected.append(by_id[task_id])
    return selected


def run_deepseek_batch_campaign(
    *,
    endpoint: str | None,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    task_ids: list[str] | None = None,
    attempts_per_goal: int = 4,
    feedback_retries_per_failed_task: int = 2,
    max_new_tokens: int = 2048,
    temperature: float = 0.6,
    top_p: float = 0.95,
    do_sample: bool = False,
    seed: int | None = 30,
    service_timeout_seconds: int = 360,
    lean_timeout_seconds: int = 120,
    stop_on_first_symbolic_success: bool = False,
    client: DeepSeekClient | None = None,
) -> dict[str, Any]:
    out_path = Path(out_dir)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.mkdir(parents=True, exist_ok=True)
    task_bank_result = refresh_run072_task_bank(out_path)
    task_bank = out_path / "deepseek_tasks.jsonl"
    selected_ids = task_ids or DEFAULT_TASK_ORDER
    rows = _ordered_rows(task_bank, selected_ids)
    if client is None:
        if not endpoint:
            raise ValueError("endpoint is required when no client is supplied")
        client = make_http_client(endpoint, timeout_seconds=service_timeout_seconds)

    raw_dir = out_path / "deepseek_raw_outputs"
    candidate_dir = out_path / "generated_candidates"
    prompt_dir = out_path / "retry_prompts"
    accepted_dir = REPO_ROOT / "formal/lean/DeepSeekCandidates/accepted"
    rejected_dir = REPO_ROOT / "formal/lean/DeepSeekCandidates/rejected"
    for directory in (raw_dir, candidate_dir, prompt_dir, accepted_dir, rejected_dir):
        directory.mkdir(parents=True, exist_ok=True)
    attempts_path = out_path / "deepseek_generation_attempts.jsonl"
    results_path = out_path / "candidate_verification_results.jsonl"
    for path in (attempts_path, results_path):
        if path.exists():
            path.unlink()

    accepted: list[dict[str, Any]] = []
    attempt_rows: list[dict[str, Any]] = []
    for row in rows:
        previous_rejection: dict[str, Any] | None = None
        previous_candidate_text = ""
        task_accepted = False
        total_attempts = attempts_per_goal + feedback_retries_per_failed_task
        for attempt in range(1, total_attempts + 1):
            is_retry = attempt > attempts_per_goal
            if is_retry and not previous_rejection:
                break
            if is_retry:
                prompt_path = prompt_dir / f"{row['task_id']}_retry{attempt - attempts_per_goal}.txt"
                prompt = write_retry_prompt(
                    prompt_path,
                    task=row,
                    previous_candidate=previous_candidate_text,
                    verification_result=previous_rejection or {},
                    retry_index=attempt - attempts_per_goal,
                )
            else:
                prompt = build_generation_prompt(row, previous_failure=previous_rejection)
                prompt_path = prompt_dir / f"{row['task_id']}_attempt{attempt}.txt"
                prompt_path.write_text(prompt, encoding="utf-8")

            request = _request_for_prompt(
                prompt,
                attempt_index=attempt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                seed=seed,
            )
            response, elapsed = _run_generation(client, request)
            raw_path = raw_dir / f"{row['task_id']}_attempt{attempt}.json"
            raw_path.write_text(json.dumps(response, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            text = str(response.get("text", ""))
            snippets = extract_lean_blocks(text, target_theorem=str(row["target_theorem"]))
            verifications: list[dict[str, Any]] = []
            if not snippets:
                previous_rejection = {
                    "status": "REJECTED",
                    "failures": ["NO_LEAN_BLOCK_EXTRACTED"],
                    "lean": {"stdout": text[-5000:], "stderr": "", "passed": False},
                }
            for index, snippet in enumerate(snippets, start=1):
                candidate_text = materialize_candidate(snippet, row)
                previous_candidate_text = candidate_text
                candidate_path = candidate_dir / f"{row['task_id']}_attempt{attempt}_candidate{index}.lean"
                candidate_path.write_text(candidate_text, encoding="utf-8")
                verification = verify_run072_candidate(
                    candidate_path,
                    row,
                    task_bank_path=task_bank,
                    results_path=results_path,
                    timeout_seconds=lean_timeout_seconds,
                    accepted_dir=accepted_dir,
                    rejected_dir=rejected_dir,
                )
                verifications.append(verification)
                previous_rejection = verification
                if verification["status"] == "ACCEPTED":
                    accepted.append(verification)
                    task_accepted = True
                    break

            attempt_row = {
                "schema": "collatz_lab.run072_generation_attempt",
                "task_id": row["task_id"],
                "target_theorem": row["target_theorem"],
                "priority": row["priority"],
                "proof_level": row["proof_level"],
                "attempt": attempt,
                "is_feedback_retry": is_retry,
                "retry_prompt": display_path(prompt_path),
                "raw_output": display_path(raw_path),
                "candidate_count": len(snippets),
                "accepted": any(item["status"] == "ACCEPTED" for item in verifications),
                "generation_elapsed_seconds": elapsed,
                "service_elapsed_seconds": response.get("elapsed_seconds"),
                "input_tokens": response.get("input_tokens"),
                "output_tokens": response.get("output_tokens"),
                "verification": verifications,
            }
            append_jsonl(attempt_row, attempts_path)
            attempt_rows.append(attempt_row)
            if task_accepted:
                break
        if stop_on_first_symbolic_success and task_accepted and row["proof_level"] != "CONCRETE_EXAMPLE":
            break

    accepted_symbolic = [row for row in accepted if row.get("proof_level") != "CONCRETE_EXAMPLE"]
    return {
        "schema": "collatz_lab.run072_deepseek_batch_campaign",
        "endpoint": endpoint,
        "task_count": len(rows),
        "attempt_count": len(attempt_rows),
        "accepted_candidate_count": len(accepted),
        "accepted_symbolic_count": len(accepted_symbolic),
        "task_bank": task_bank_result,
        "artifacts": {
            "task_bank": display_path(task_bank),
            "generation_attempts": display_path(attempts_path),
            "candidate_verification_results": display_path(results_path),
            "generated_candidates": display_path(candidate_dir),
            "raw_output_dir": display_path(raw_dir),
            "retry_prompts": display_path(prompt_dir),
            "accepted_candidates": "formal/lean/DeepSeekCandidates/accepted",
            "rejected_candidates": "formal/lean/DeepSeekCandidates/rejected",
        },
    }
