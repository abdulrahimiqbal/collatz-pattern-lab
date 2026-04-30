"""RUN-072 pattern synthesis and high-parent progress classification."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .deepseek_goal_bank import REPO_ROOT, display_path
from .utils import load_jsonl, write_jsonl


PROGRESS_ORDER = [
    "NONE",
    "CONCRETE_EXAMPLE",
    "FIXED_D_SYMBOLIC",
    "P32_SPECIAL_FIXED_D",
    "LOW_PARENT_MARGIN_CASE",
    "GENERAL_HIGH_PARENT_THEOREM",
]


def proof_level_for_task(task_id: str, target_theorem: str | None = None) -> str:
    name = target_theorem or task_id
    if name in {"high_parent_root_relative_descent", "high_parent_general_theorem", "high_parent_invariant_schema"}:
        return "GENERAL_HIGH_PARENT_THEOREM"
    if name.startswith("low_parent_b"):
        return "LOW_PARENT_MARGIN_CASE"
    if name.startswith("p32_special_root_relative_d"):
        return "P32_SPECIAL_FIXED_D"
    if name.startswith("high_parent_d") or name.startswith("goal_d") and "symbolic" in task_id:
        return "FIXED_D_SYMBOLIC"
    if name.startswith("goal_d"):
        return "CONCRETE_EXAMPLE"
    return "NONE"


def theorem_d_index(name: str | None) -> int | None:
    if not name:
        return None
    match = re.search(r"_d([0-9]+)(?:_|$)", name)
    return int(match.group(1)) if match else None


def accepted_symbolic_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if row.get("status") != "ACCEPTED":
            continue
        level = str(row.get("proof_level") or proof_level_for_task(str(row.get("task_id", "")), row.get("target_theorem")))
        if level != "CONCRETE_EXAMPLE":
            out.append({**row, "proof_level": level})
    return out


def strongest_level(rows: list[dict[str, Any]]) -> str:
    strongest = "NONE"
    for row in rows:
        level = str(row.get("proof_level") or "NONE")
        if level in PROGRESS_ORDER and PROGRESS_ORDER.index(level) > PROGRESS_ORDER.index(strongest):
            strongest = level
    return strongest


def _candidate_text(row: dict[str, Any]) -> str:
    file_value = row.get("candidate_file")
    if not file_value:
        return ""
    path = Path(str(file_value))
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _extract_witnesses(text: str) -> list[str]:
    patterns = [
        r"Exists\.intro\s+([A-Za-z0-9_+\-*/^ ()]+)",
        r"refine\s+[\u27e8<]([0-9A-Za-z_+\-*/^ ()]+)",
        r"\u27e8\s*([0-9]+)\s*,",
    ]
    values: list[str] = []
    for pattern in patterns:
        values.extend(match.strip() for match in re.findall(pattern, text))
    return sorted(set(values))


def synthesize_high_parent_patterns(
    *,
    accepted_rows: list[dict[str, Any]],
    out_dir: str | Path,
) -> dict[str, Any]:
    out_path = Path(out_dir)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.mkdir(parents=True, exist_ok=True)

    symbolic = accepted_symbolic_rows(accepted_rows)
    fixed_d = [
        row
        for row in symbolic
        if row.get("proof_level") == "FIXED_D_SYMBOLIC" and theorem_d_index(str(row.get("target_theorem"))) is not None
    ]
    p32_fixed = [
        row
        for row in symbolic
        if row.get("proof_level") == "P32_SPECIAL_FIXED_D" and theorem_d_index(str(row.get("target_theorem"))) is not None
    ]
    low_parent = [row for row in symbolic if row.get("proof_level") == "LOW_PARENT_MARGIN_CASE"]
    general = [row for row in symbolic if row.get("proof_level") == "GENERAL_HIGH_PARENT_THEOREM"]

    fixed_ds = sorted({theorem_d_index(str(row.get("target_theorem"))) for row in fixed_d if theorem_d_index(str(row.get("target_theorem"))) is not None})
    p32_ds = sorted({theorem_d_index(str(row.get("target_theorem"))) for row in p32_fixed if theorem_d_index(str(row.get("target_theorem"))) is not None})
    low_bs = sorted(
        {
            int(match.group(1))
            for row in low_parent
            for match in [re.search(r"low_parent_b([0-9]+)_margin", str(row.get("target_theorem")))]
            if match
        }
    )

    witness_map = {
        str(row.get("target_theorem")): _extract_witnesses(_candidate_text(row))
        for row in symbolic
    }
    common_witnesses = sorted(set.intersection(*(set(v) for v in witness_map.values() if v))) if any(witness_map.values()) else []

    generated_tasks: list[dict[str, Any]] = []
    if {1, 2}.issubset(set(fixed_ds)):
        generated_tasks.append(
            {
                "task_id": "high_parent_general_from_d12_pattern",
                "target_theorem": "high_parent_root_relative_descent",
                "proof_level": "GENERAL_HIGH_PARENT_THEOREM",
                "reason": "fixed d=1 and d=2 symbolic proofs were harvested",
            }
        )
    if {1, 2, 3}.issubset(set(fixed_ds)):
        generated_tasks.extend(
            [
                {
                    "task_id": "high_parent_general_from_d123_pattern",
                    "target_theorem": "high_parent_root_relative_descent",
                    "proof_level": "GENERAL_HIGH_PARENT_THEOREM",
                    "reason": "fixed d=1, d=2, and d=3 symbolic proofs were harvested",
                },
                {
                    "task_id": "p32_special_general_from_fixed_d_pattern",
                    "target_theorem": "p32_special_root_relative_general",
                    "proof_level": "GENERAL_HIGH_PARENT_THEOREM",
                    "reason": "fixed-d structure may expose the missing P32-special schema",
                },
                {
                    "task_id": "low_parent_margin_general_schema",
                    "target_theorem": "low_parent_margin_general_schema",
                    "proof_level": "LOW_PARENT_MARGIN_CASE",
                    "reason": "general high-parent synthesis needs a low-parent continuation schema",
                },
            ]
        )

    write_jsonl(generated_tasks, out_path / "generated_generalization_tasks.jsonl")

    report_lines = [
        "# RUN-072 Pattern Synthesis",
        "",
        f"- accepted symbolic rows: {len(symbolic)}",
        f"- fixed-d symbolic d values: {fixed_ds or 'none'}",
        f"- P32-special fixed d values: {p32_ds or 'none'}",
        f"- low-parent margin b values: {low_bs or 'none'}",
        f"- general high-parent rows: {len(general)}",
        f"- common extracted witnesses: {common_witnesses or 'none'}",
        "",
        "## Candidate Generalization Tasks",
    ]
    if generated_tasks:
        report_lines.extend(f"- `{task['task_id']}`: {task['reason']}" for task in generated_tasks)
    else:
        report_lines.append("- none; not enough symbolic fixed-d structure was harvested")
    report_path = out_path / "pattern_synthesis_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "schema": "collatz_lab.run072_pattern_synthesis",
        "accepted_symbolic_count": len(symbolic),
        "fixed_d_values": fixed_ds,
        "p32_special_d_values": p32_ds,
        "low_parent_b_values": low_bs,
        "general_high_parent_count": len(general),
        "common_witnesses": common_witnesses,
        "generated_task_count": len(generated_tasks),
        "artifacts": {
            "pattern_synthesis_report": display_path(report_path),
            "generated_generalization_tasks": display_path(out_path / "generated_generalization_tasks.jsonl"),
        },
    }


def next_missing_theorem(accepted_rows: list[dict[str, Any]]) -> str:
    accepted_names = {str(row.get("target_theorem")) for row in accepted_rows if row.get("status") == "ACCEPTED"}
    for name in (
        "p32_special_root_relative_d1",
        "high_parent_d1",
        "p32_special_root_relative_d2",
        "high_parent_d2",
        "p32_special_root_relative_d3",
        "high_parent_d3",
        "low_parent_b1_margin",
        "high_parent_root_relative_descent",
    ):
        if name not in accepted_names:
            return name
    return "high_parent_root_relative_descent"
