#!/usr/bin/env python3
"""Generate Lean data for RUN-056B global semantic maps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRY_PATH = REPO_ROOT / "certificate_store/run056b_entry_map.json"
COVERAGE_PATH = REPO_ROOT / "certificate_store/run056b_coverage_map.json"
NO_ESCAPE_PATH = REPO_ROOT / "certificate_store/run056b_no_escape_map.json"
WELL_FOUNDED_PATH = REPO_ROOT / "certificate_store/run056b_well_founded_bridge.json"
OUT_PATH = REPO_ROOT / "formal/lean/Collatz/Run056BData.lean"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def lean_string(value: Any) -> str:
    text = str(value)
    text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{text}"'


def lean_bool(value: Any) -> str:
    return "true" if bool(value) else "false"


def lean_string_list(values: list[str], *, indent: str = "    ") -> str:
    if not values:
        return "[]"
    return "[\n" + indent + (",\n" + indent).join(lean_string(value) for value in values) + "\n  ]"


def validation(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("semantic_validation")
    return value if isinstance(value, dict) else {}


def failure_reasons(payload: dict[str, Any]) -> list[str]:
    failures = validation(payload).get("failures")
    if not isinstance(failures, list):
        return []
    reasons: list[str] = []
    for failure in failures:
        reason = str(failure.get("reason", ""))
        if reason and reason not in reasons:
            reasons.append(reason)
    return reasons


def finite_node_count(payload: dict[str, Any]) -> int:
    model = payload.get("certified_node_model")
    if isinstance(model, dict):
        return int(model.get("finite_node_count", 0) or 0)
    summary = payload.get("domain_summary")
    if isinstance(summary, dict):
        return len(summary.get("node_levels", []) or [])
    edge_summary = payload.get("edge_applicability_summary")
    if isinstance(edge_summary, dict):
        return len(edge_summary.get("certified_node_levels", []) or [])
    return 0


def witness_count(payload: dict[str, Any]) -> int:
    model = payload.get("certified_node_model")
    if isinstance(model, dict):
        return len(model.get("node_levels", []) or [])
    summary = payload.get("domain_summary")
    if isinstance(summary, dict):
        return int(summary.get("domain_count", 0) or 0)
    edge_summary = payload.get("edge_applicability_summary")
    if isinstance(edge_summary, dict):
        return int(edge_summary.get("s4_transition_count", 0) or 0)
    roles = payload.get("s3_role_counts")
    if isinstance(roles, dict):
        return sum(int(value or 0) for value in roles.values())
    return 0


def map_def(name: str, payload: dict[str, Any]) -> str:
    status = validation(payload).get("status") == "PASS"
    reasons = failure_reasons(payload)
    theorem_witnesses_present = status and not reasons
    return "\n".join(
        [
            f"def {name} : GlobalSemanticMap := {{",
            f"  kind := {lean_string(payload.get('kind', ''))},",
            f"  status := {lean_bool(status)},",
            f"  failureReasons := {lean_string_list(reasons)},",
            f"  observedFiniteNodeCount := {finite_node_count(payload)},",
            f"  witnessCount := {witness_count(payload)},",
            f"  theoremWitnessesPresent := {lean_bool(theorem_witnesses_present)},",
            f"  semanticMapHash := {lean_string(payload.get('global_semantic_map_hash', ''))}",
            "}",
        ]
    )


def generate(
    *,
    entry_path: Path = ENTRY_PATH,
    coverage_path: Path = COVERAGE_PATH,
    no_escape_path: Path = NO_ESCAPE_PATH,
    well_founded_path: Path = WELL_FOUNDED_PATH,
    out_path: Path = OUT_PATH,
) -> None:
    maps = {
        "run056BEntryMap": read_json(entry_path),
        "run056BCoverageMap": read_json(coverage_path),
        "run056BNoEscapeMap": read_json(no_escape_path),
        "run056BWellFoundedBridge": read_json(well_founded_path),
    }
    all_reasons = sorted({reason for payload in maps.values() for reason in failure_reasons(payload)})
    text = "\n\n".join(
        [
            "import Collatz.GlobalSemanticMaps",
            "/-!\nGenerated RUN-056B global semantic map data.\n\nThe current maps intentionally fail closed because the source payloads do not\nyet provide theorem-grade global semantic witnesses.\n-/",
            "namespace Collatz",
            *(map_def(name, payload) for name, payload in maps.items()),
            "def Run056BGeneratedGapReasons : List String :=\n  " + lean_string_list(all_reasons),
            "end Collatz",
            "",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", type=Path, default=ENTRY_PATH)
    parser.add_argument("--coverage", type=Path, default=COVERAGE_PATH)
    parser.add_argument("--no-escape", type=Path, default=NO_ESCAPE_PATH)
    parser.add_argument("--well-founded", type=Path, default=WELL_FOUNDED_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args(argv)
    generate(
        entry_path=args.entry,
        coverage_path=args.coverage,
        no_escape_path=args.no_escape,
        well_founded_path=args.well_founded,
        out_path=args.out,
    )


if __name__ == "__main__":
    main()
