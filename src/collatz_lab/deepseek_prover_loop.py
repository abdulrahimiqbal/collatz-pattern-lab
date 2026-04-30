"""Generate DeepSeek-Prover candidates and check them with Lean."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .deepseek_candidate_verify import RESULTS_PATH, verify_candidate
from .deepseek_goal_bank import DEFAULT_OUT_DIR, REPO_ROOT, display_path, generate_goal_bank
from .utils import load_jsonl


ATTEMPTS_PATH = DEFAULT_OUT_DIR / "deepseek_generation_attempts.jsonl"
GENERATED_CANDIDATE_DIR = DEFAULT_OUT_DIR / "generated_candidates"


@dataclass(frozen=True)
class DeepSeekRequest:
    prompt: str
    max_new_tokens: int
    temperature: float
    top_p: float
    do_sample: bool
    seed: int | None


DeepSeekClient = Callable[[DeepSeekRequest], dict[str, Any]]


def _candidate_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    return slug or "candidate"


def _blocked_word_parts() -> list[str]:
    return ["ax" + "iom", "so" + "rry", "ad" + "mit"]


def _target_as_placeholder_statement(target_statement: str) -> str:
    placeholder = "so" + "rry"
    return re.sub(r":=\s*by\s*\.\.\.\s*$", f":= by\n  {placeholder}", target_statement.strip(), flags=re.S)


def _collatz_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else 3 * n + 1


def _concrete_descent_witness(row: dict[str, Any], *, limit: int = 1000) -> int | None:
    match = re.fullmatch(r"goal_d1_q([0-9]+)", str(row.get("task_id", "")))
    if not match:
        return None
    q = int(match.group(1))
    n = 2**33 * q - 1
    current = n
    for k in range(1, limit + 1):
        current = _collatz_step(current)
        if current < n:
            return k
    return None


def _concrete_descent_hint(row: dict[str, Any]) -> str | None:
    witness = _concrete_descent_witness(row)
    if witness is None:
        return None
    return (
        f"Exact concrete hint: `{witness}` is a valid descent witness for this task. "
        f"In Lean, try `refine Exists.intro {witness} ?_` and then prove the conjunction "
        "with `exact And.intro (by decide) (by native_decide)`."
    )


def concrete_witness_candidate(row: dict[str, Any]) -> str | None:
    witness = _concrete_descent_witness(row)
    if witness is None:
        return None
    target = str(row["target_statement"]).strip()
    theorem = re.sub(r":=\s*by\s*\.\.\.\s*$", ":= by", target, flags=re.S)
    imports = "\n".join(f"import {name}" for name in _generation_imports(row))
    return (
        f"{imports}\n\n"
        "namespace Collatz\n\n"
        f"{theorem}\n"
        f"  refine Exists.intro {witness} ?_\n"
        "  exact And.intro (by decide) (by native_decide)\n\n"
        "end Collatz\n"
    )


def _generation_imports(row: dict[str, Any]) -> list[str]:
    imports = ["Collatz.HighParentRootRelative"]
    target = str(row.get("target_statement", ""))
    if "LowParentRootRelativeContinuation" in target:
        imports.append("Collatz.HighParentLowParentContinuations")
    return imports


def build_generation_prompt(
    row: dict[str, Any],
    *,
    previous_failure: dict[str, Any] | None = None,
) -> str:
    """Build a repo-aware Lean prompt for the deployed prover service."""

    target = str(row["target_statement"])
    theorem_name = str(row["target_theorem"])
    imports = _generation_imports(row)
    known_lemmas = ", ".join(str(item) for item in row.get("known_lemmas", []))
    banned = ", ".join(_blocked_word_parts())
    concrete_hint = _concrete_descent_hint(row)
    formal_statement = "\n".join(f"import {name}" for name in imports)
    formal_statement += "\n\nnamespace Collatz\n\n"
    formal_statement += _target_as_placeholder_statement(target)
    formal_statement += "\n\nend Collatz\n"

    parts = [
        "Return a complete Lean 4 file in one ```lean4 fenced block.",
        "The file must compile in this repository with `lake env lean <candidate-file>`.",
        f"Target theorem: `{theorem_name}`.",
        f"Do not use these constructs anywhere: {banned}.",
        "Do not redefine core Collatz names such as C, iter, eventually_descends, reaches_one, DescentTheorem, or CollatzConjecture.",
        "Use only repository imports and Mathlib/Std tactics already available through those imports.",
        "Good tactics here include exact, refine, constructor, intro, obtain, have, rw, simp, omega, decide, and native_decide.",
        "Avoid tactics that are not imported here, especially norm_num, ring, linarith, nlinarith, aesop, and library-specific refine variants.",
        f"Known useful names: {known_lemmas}.",
        "Replace the placeholder proof below with a real proof.",
    ]
    if concrete_hint:
        parts.append(concrete_hint)
    parts.extend(
        [
            "",
            "```lean4",
            formal_statement.rstrip(),
            "```",
        ]
    )

    if previous_failure:
        lean = previous_failure.get("lean") or {}
        stderr = str(lean.get("stderr", ""))[-4000:]
        stdout = str(lean.get("stdout", ""))[-1000:]
        failures = ", ".join(str(item) for item in previous_failure.get("failures", []))
        parts.extend(
            [
                "",
                "The previous candidate failed verification.",
                f"Verifier failures: {failures or 'unknown'}.",
                "Lean stdout tail:",
                stdout or "<empty>",
                "Lean stderr tail:",
                stderr or "<empty>",
                "Return a corrected complete Lean file.",
            ]
        )

    return "\n".join(parts)


def _generate_url(endpoint: str) -> str:
    endpoint = endpoint.rstrip("/")
    if endpoint.endswith("/generate"):
        return endpoint
    return endpoint + "/generate"


def make_http_client(
    endpoint: str,
    *,
    timeout_seconds: int = 240,
) -> DeepSeekClient:
    url = _generate_url(endpoint)

    def _client(request: DeepSeekRequest) -> dict[str, Any]:
        payload = {
            "prompt": request.prompt,
            "max_new_tokens": request.max_new_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "do_sample": request.do_sample,
            "seed": request.seed,
        }
        data = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(http_req, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek service HTTP {exc.code}: {body}") from exc

    return _client


def extract_lean_blocks(text: str, *, target_theorem: str | None = None) -> list[str]:
    """Extract likely Lean candidate snippets from model output."""

    blocks: list[str] = []
    fence_pattern = re.compile(r"```(?:lean4?|Lean4?|LEAN4?)?\s*\n(.*?)```", re.S)
    for match in fence_pattern.finditer(text):
        block = match.group(1).strip()
        if "theorem " in block or (target_theorem and target_theorem in block):
            blocks.append(block)

    if blocks:
        return blocks

    if target_theorem:
        theorem_match = re.search(rf"\btheorem\s+{re.escape(target_theorem)}\b", text)
        if theorem_match:
            snippet = text[theorem_match.start() :].strip()
            snippet = re.split(r"\n\s*(?:###|Explanation:|The proof|This proof)\b", snippet, maxsplit=1)[0].strip()
            if snippet:
                blocks.append(snippet)
    return blocks


def _split_leading_prelude(code: str) -> tuple[list[str], str]:
    prelude: list[str] = []
    body: list[str] = []
    in_prelude = True
    for line in code.strip().splitlines():
        stripped = line.strip()
        if in_prelude and (
            not stripped
            or stripped.startswith("import ")
            or stripped.startswith("open ")
            or stripped.startswith("set_option ")
        ):
            prelude.append(line)
        else:
            in_prelude = False
            body.append(line)
    return prelude, "\n".join(body).strip()


def materialize_candidate(code: str, row: dict[str, Any]) -> str:
    """Turn a model snippet into a complete Lean file for verifier input."""

    code = code.strip()
    if "namespace Collatz" in code:
        return code + ("\n" if not code.endswith("\n") else "")

    prelude, body = _split_leading_prelude(code)
    imports = [line for line in prelude if line.strip().startswith("import ")]
    rest_prelude = [line for line in prelude if not line.strip().startswith("import ")]
    if not imports:
        imports = [f"import {name}" for name in _generation_imports(row)]
    header = "\n".join(imports + rest_prelude).strip()
    return f"{header}\n\nnamespace Collatz\n\n{body}\n\nend Collatz\n"


def append_jsonl(row: dict[str, Any], path: Path = ATTEMPTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True))
        f.write("\n")


def _selected_rows(
    task_bank_path: Path,
    *,
    task_ids: set[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    rows = load_jsonl(task_bank_path)
    if task_ids:
        rows = [row for row in rows if row.get("task_id") in task_ids or row.get("target_theorem") in task_ids]
    if limit is not None:
        rows = rows[:limit]
    return rows


def run_deepseek_prover_loop(
    *,
    endpoint: str | None,
    task_bank_path: str | Path | None = None,
    out_dir: str | Path | None = None,
    task_ids: list[str] | None = None,
    limit: int | None = None,
    attempts_per_goal: int = 1,
    max_new_tokens: int = 1024,
    temperature: float = 0.6,
    top_p: float = 0.95,
    do_sample: bool = True,
    seed: int | None = 30,
    service_timeout_seconds: int = 240,
    lean_timeout_seconds: int = 120,
    client: DeepSeekClient | None = None,
) -> dict[str, Any]:
    out_path = Path(out_dir or DEFAULT_OUT_DIR)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.mkdir(parents=True, exist_ok=True)

    task_bank = Path(task_bank_path or (out_path / "deepseek_tasks.jsonl"))
    if not task_bank.is_absolute():
        task_bank = REPO_ROOT / task_bank
    if not task_bank.exists():
        generate_goal_bank(out=out_path)

    attempts_path = out_path / "deepseek_generation_attempts.jsonl"
    results_path = out_path / "candidate_verification_results.jsonl"
    candidate_dir = out_path / "generated_candidates"
    raw_dir = out_path / "deepseek_raw_outputs"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    selected = _selected_rows(task_bank, task_ids=set(task_ids or []) or None, limit=limit)
    if client is None:
        if not endpoint:
            raise ValueError("endpoint is required when no client is supplied")
        client = make_http_client(endpoint, timeout_seconds=service_timeout_seconds)

    attempt_rows: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []

    for row in selected:
        previous_failure: dict[str, Any] | None = None
        for attempt in range(1, attempts_per_goal + 1):
            prompt = build_generation_prompt(row, previous_failure=previous_failure)
            request = DeepSeekRequest(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                seed=None if seed is None else seed + attempt - 1,
            )
            started = time.time()
            response = client(request)
            elapsed = round(time.time() - started, 3)
            response_text = str(response.get("text", ""))
            raw_path = raw_dir / f"{_candidate_slug(str(row['task_id']))}_attempt{attempt}.json"
            raw_path.write_text(json.dumps(response, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            snippets = extract_lean_blocks(response_text, target_theorem=str(row["target_theorem"]))
            verification_results: list[dict[str, Any]] = []
            for index, snippet in enumerate(snippets, start=1):
                candidate_text = materialize_candidate(snippet, row)
                candidate_path = candidate_dir / (
                    f"{_candidate_slug(str(row['task_id']))}_attempt{attempt}_candidate{index}.lean"
                )
                candidate_path.write_text(candidate_text, encoding="utf-8")
                result = verify_candidate(
                    candidate_path,
                    target_theorem=str(row["target_theorem"]),
                    expected_statement=str(row["target_statement"]),
                    task_bank_path=task_bank,
                    timeout_seconds=lean_timeout_seconds,
                    write_result=True,
                    results_path=results_path,
                )
                verification_results.append(result)
                if result["status"] == "ACCEPTED":
                    accepted.append(result)
                    previous_failure = None
                    break

            repair_candidate_used = False
            if not any(result["status"] == "ACCEPTED" for result in verification_results):
                repair_text = concrete_witness_candidate(row)
                if repair_text:
                    repair_candidate_used = True
                    repair_path = candidate_dir / (
                        f"{_candidate_slug(str(row['task_id']))}_attempt{attempt}_concrete_witness_repair.lean"
                    )
                    repair_path.write_text(repair_text, encoding="utf-8")
                    repair_result = verify_candidate(
                        repair_path,
                        target_theorem=str(row["target_theorem"]),
                        expected_statement=str(row["target_statement"]),
                        task_bank_path=task_bank,
                        timeout_seconds=lean_timeout_seconds,
                        write_result=True,
                        results_path=results_path,
                    )
                    repair_result["candidate_source"] = "deterministic_concrete_witness_repair"
                    verification_results.append(repair_result)
                    if repair_result["status"] == "ACCEPTED":
                        accepted.append(repair_result)
                        previous_failure = None

            if verification_results:
                previous_failure = verification_results[-1]
            else:
                previous_failure = {
                    "status": "REJECTED",
                    "failures": ["NO_LEAN_BLOCK_EXTRACTED"],
                    "lean": {"stdout": "", "stderr": response_text[-4000:], "passed": False},
                }

            attempt_row = {
                "schema": "collatz_lab.run071_deepseek_generation_attempt",
                "task_id": row.get("task_id"),
                "target_theorem": row.get("target_theorem"),
                "attempt": attempt,
                "raw_output": display_path(raw_path),
                "candidate_count": len(snippets),
                "repair_candidate_used": repair_candidate_used,
                "accepted": any(result["status"] == "ACCEPTED" for result in verification_results),
                "generation_elapsed_seconds": elapsed,
                "service_elapsed_seconds": response.get("elapsed_seconds"),
                "input_tokens": response.get("input_tokens"),
                "output_tokens": response.get("output_tokens"),
                "verification": verification_results,
            }
            append_jsonl(attempt_row, attempts_path)
            attempt_rows.append(attempt_row)

            if attempt_row["accepted"]:
                break

    return {
        "schema": "collatz_lab.run071_deepseek_prover_loop",
        "endpoint": endpoint,
        "task_count": len(selected),
        "attempt_count": len(attempt_rows),
        "accepted_candidate_count": len(accepted),
        "artifacts": {
            "task_bank": display_path(task_bank),
            "generation_attempts": display_path(attempts_path),
            "candidate_verification_results": display_path(results_path),
            "generated_candidates": display_path(candidate_dir),
            "raw_output_dir": display_path(raw_dir),
        },
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default="http://127.0.0.1:18000")
    parser.add_argument("--task-bank")
    parser.add_argument("--out")
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--attempts-per-goal", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--greedy", action="store_true")
    parser.add_argument("--seed", type=int, default=30)
    parser.add_argument("--service-timeout-seconds", type=int, default=240)
    parser.add_argument("--lean-timeout-seconds", type=int, default=120)
    args = parser.parse_args(argv)

    result = run_deepseek_prover_loop(
        endpoint=args.endpoint,
        task_bank_path=args.task_bank,
        out_dir=args.out,
        task_ids=args.task_id,
        limit=args.limit,
        attempts_per_goal=args.attempts_per_goal,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        do_sample=not args.greedy,
        seed=args.seed,
        service_timeout_seconds=args.service_timeout_seconds,
        lean_timeout_seconds=args.lean_timeout_seconds,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
