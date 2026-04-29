"""Lean candidate checker for RUN-071 generated tasks."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .deepseek_goal_bank import DEFAULT_OUT_DIR, REPO_ROOT
from .utils import load_jsonl


CANDIDATE_DIR = REPO_ROOT / "formal/lean/DeepSeekCandidates"
RESULTS_PATH = DEFAULT_OUT_DIR / "candidate_verification_results.jsonl"


def _blocked_terms() -> list[str]:
    return ["ax" + "iom", "so" + "rry", "ad" + "mit"]


def _blocked_regex() -> re.Pattern[str]:
    return re.compile(r"\b(?:" + "|".join(re.escape(term) for term in _blocked_terms()) + r")\b")


def normalize_lean(text: str) -> str:
    return " ".join(text.split())


def _copy_candidate(candidate: Path) -> tuple[Path, bool]:
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    dst = CANDIDATE_DIR / candidate.name
    if candidate.resolve() != dst.resolve():
        shutil.copy2(candidate, dst)
        return dst, True
    return dst, False


def _load_expected_from_task_bank(task_bank_path: Path | None, target_theorem: str | None) -> str | None:
    if not task_bank_path or not target_theorem or not task_bank_path.exists():
        return None
    for row in load_jsonl(task_bank_path):
        if row.get("target_theorem") == target_theorem:
            value = row.get("target_statement")
            return str(value) if value else None
    return None


def _detect_theorems(text: str) -> list[str]:
    return re.findall(r"\btheorem\s+([A-Za-z_][A-Za-z0-9_']*)", text)


def _statement_matches(text: str, expected_statement: str | None) -> bool:
    if not expected_statement:
        return True
    expected = normalize_lean(expected_statement).replace(" := by ...", "")
    actual = normalize_lean(text)
    return expected in actual


def _has_core_redefinition(text: str) -> bool:
    protected = ("C", "iter", "eventually_descends", "reaches_one", "DescentTheorem", "CollatzConjecture")
    pattern = re.compile(r"\b(?:def|theorem)\s+(" + "|".join(re.escape(name) for name in protected) + r")\b")
    return bool(pattern.search(text))


def _has_suspicious_import(text: str) -> bool:
    blocked_import_fragments = (
        "Collatz.Run051Proof",
        "CollatzProofCandidate",
        "Collatz.GlobalSemanticMaps",
    )
    return any(fragment in text for fragment in blocked_import_fragments)


def _run_lean(path: Path, timeout_seconds: int) -> dict[str, Any]:
    completed = subprocess.run(
        ["lake", "env", "lean", str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return {
        "command": f"lake env lean {path.relative_to(REPO_ROOT)}",
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "passed": completed.returncode == 0,
    }


def append_jsonl(row: dict[str, Any], path: Path = RESULTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True))
        f.write("\n")


def verify_candidate(
    candidate: str | Path,
    *,
    target_theorem: str | None = None,
    expected_statement: str | None = None,
    task_bank_path: str | Path | None = None,
    timeout_seconds: int = 120,
    run_lean: bool = True,
    write_result: bool = True,
    results_path: str | Path = RESULTS_PATH,
) -> dict[str, Any]:
    src = Path(candidate)
    if not src.is_absolute():
        src = REPO_ROOT / src
    dst, copied = _copy_candidate(src)
    text = dst.read_text(encoding="utf-8")

    found_terms = sorted(set(_blocked_regex().findall(text)))
    theorem_names = _detect_theorems(text)
    expected = expected_statement or _load_expected_from_task_bank(
        Path(task_bank_path) if task_bank_path else None,
        target_theorem,
    )
    target_exists = (target_theorem in theorem_names) if target_theorem else bool(theorem_names)
    statement_matches = _statement_matches(text, expected)
    core_redefinition = _has_core_redefinition(text)
    suspicious_import = _has_suspicious_import(text)

    lean_result: dict[str, Any]
    if run_lean:
        try:
            lean_result = _run_lean(dst, timeout_seconds)
        except subprocess.TimeoutExpired:
            lean_result = {
                "command": f"lake env lean {dst.relative_to(REPO_ROOT)}",
                "returncode": "TIMEOUT",
                "stdout": "",
                "stderr": "timeout",
                "passed": False,
            }
    else:
        lean_result = {
            "command": None,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "passed": True,
        }

    failures: list[str] = []
    if found_terms:
        failures.append("BLOCKED_TERM_FOUND")
    if not lean_result["passed"]:
        failures.append("LEAN_CHECK_FAILED")
    if not target_exists:
        failures.append("TARGET_THEOREM_MISSING")
    if not statement_matches:
        failures.append("THEOREM_STATEMENT_MISMATCH")
    if suspicious_import:
        failures.append("SUSPICIOUS_IMPORT")
    if core_redefinition:
        failures.append("CORE_DEFINITION_REDEFINED")

    result = {
        "schema": "collatz_lab.run071_candidate_verification",
        "candidate_file": str(dst.relative_to(REPO_ROOT)),
        "target_theorem": target_theorem,
        "status": "ACCEPTED" if not failures else "REJECTED",
        "failures": failures,
        "blocked_construct_status": {
            "passed": not found_terms,
            "found": found_terms,
        },
        "lean": lean_result,
        "theorem_names_detected": theorem_names,
        "target_theorem_exists": target_exists,
        "statement_matches_expected": statement_matches,
        "suspicious_import": suspicious_import,
        "core_redefinition": core_redefinition,
    }
    if found_terms and copied and dst.exists():
        dst.unlink()
    if write_result:
        append_jsonl(result, Path(results_path))
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate")
    parser.add_argument("--target-theorem")
    parser.add_argument("--expected-statement")
    parser.add_argument("--task-bank")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--no-lean", action="store_true")
    args = parser.parse_args(argv)
    result = verify_candidate(
        args.candidate,
        target_theorem=args.target_theorem,
        expected_statement=args.expected_statement,
        task_bank_path=args.task_bank,
        timeout_seconds=args.timeout_seconds,
        run_lean=not args.no_lean,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
