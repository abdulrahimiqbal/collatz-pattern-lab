"""Compiler-feedback prompts for DeepSeek Lean candidate repair."""

from __future__ import annotations

from pathlib import Path
from typing import Any


FORBIDDEN_CONSTRUCTS = ("ax" + "iom", "so" + "rry", "ad" + "mit")


def _tail(value: str, limit: int) -> str:
    return value[-limit:] if len(value) > limit else value


def lean_error_text(result: dict[str, Any]) -> str:
    lean = result.get("lean") if isinstance(result.get("lean"), dict) else {}
    stdout = str(lean.get("stdout", ""))
    stderr = str(lean.get("stderr", ""))
    failures = ", ".join(str(item) for item in result.get("failures", []))
    parts = []
    if failures:
        parts.append(f"Verifier failures: {failures}")
    if stdout:
        parts.append("Lean stdout:\n" + _tail(stdout, 5000))
    if stderr:
        parts.append("Lean stderr:\n" + _tail(stderr, 5000))
    return "\n\n".join(parts) or "Lean rejected the previous candidate."


def build_feedback_retry_prompt(
    *,
    task: dict[str, Any],
    previous_candidate: str,
    verification_result: dict[str, Any],
    retry_index: int,
) -> str:
    forbidden = "/".join(FORBIDDEN_CONSTRUCTS)
    return "\n".join(
        [
            "Return a complete Lean 4 file in one ```lean4 fenced block.",
            "Fix only the proof body. Do not change the theorem name, assumptions, or conclusion.",
            f"Do not use {forbidden}.",
            "Do not import proof-status files, global semantic-map proof modules, or any theorem that merely records a Python PASS.",
            "Do not redefine core Collatz definitions.",
            f"Retry index: {retry_index}.",
            "",
            "Exact theorem statement:",
            str(task["target_statement"]).strip(),
            "",
            "Previous candidate:",
            "```lean4",
            previous_candidate.strip(),
            "```",
            "",
            "Compiler/verifier feedback:",
            lean_error_text(verification_result),
        ]
    )


def write_retry_prompt(
    path: str | Path,
    *,
    task: dict[str, Any],
    previous_candidate: str,
    verification_result: dict[str, Any],
    retry_index: int,
) -> str:
    prompt = build_feedback_retry_prompt(
        task=task,
        previous_candidate=previous_candidate,
        verification_result=verification_result,
        retry_index=retry_index,
    )
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    return prompt
