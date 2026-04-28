#!/usr/bin/env python3
"""Generate Lean data for RUN-048 semantic witnesses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
WITNESSES_PATH = REPO_ROOT / "certificate_store/run048_semantic_witnesses.jsonl"
OUT_PATH = REPO_ROOT / "formal/lean/Collatz/Run048Data.lean"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _lean_string(value: Any) -> str:
    return json.dumps(str(value or ""), ensure_ascii=True)


def _nat(value: Any) -> str:
    return str(int(value or 0))


def _extract_s4_witnesses(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    witnesses = [row for row in rows if row.get("kind") == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"]
    witnesses.sort(key=lambda row: str(row.get("certificate_id", "")))
    return witnesses


def _lean_s4_witness(witness: dict[str, Any]) -> str:
    pmap = witness.get("parent_coordinate_map") if isinstance(witness.get("parent_coordinate_map"), dict) else {}
    branch = witness.get("branch_coordinate_identity") if isinstance(witness.get("branch_coordinate_identity"), dict) else {}
    return "\n".join(
        [
            "{",
            f"  certificateId := {_lean_string(witness.get('certificate_id'))},",
            f"  sourceParent := {_nat(witness.get('source_parent'))},",
            f"  targetParent := {_nat(witness.get('target_parent'))},",
            f"  valuation := {_nat(witness.get('valuation'))},",
            f"  sourceDepth := {_nat(witness.get('source_depth'))},",
            f"  sourceResidue := {_nat(witness.get('source_residue'))},",
            f"  baseBurstDivisionExponent := {_nat(witness.get('base_burst_division_exponent'))},",
            f"  standardStepCount := {_nat(witness.get('standard_step_count'))},",
            f"  mapA := {_nat(pmap.get('A'))},",
            f"  mapB := {_nat(pmap.get('B'))},",
            f"  mapD := {_nat(pmap.get('D'))},",
            f"  c := {_nat(branch.get('c'))},",
            f"  semanticWitnessHash := {_lean_string(witness.get('semantic_witness_hash'))}",
            "}",
        ]
    )


def _lean_list(items: list[str], *, indent: str = "  ") -> str:
    if not items:
        return "[]"
    return "[\n" + indent + (",\n" + indent).join(items) + "\n]"


def generate(witnesses_path: Path = WITNESSES_PATH, out_path: Path = OUT_PATH) -> None:
    rows = _read_jsonl(witnesses_path)
    s4_witnesses = _extract_s4_witnesses(rows)
    body = "\n".join(
        [
            "import Collatz.SemanticBridge",
            "",
            "/-!",
            "Generated RUN-048 semantic witness data.",
            "",
            "This file contains literal data only.  The theorems below are",
            "decidable count/validity checks over that data, not imported Python",
            "PASS statuses.",
            "-/",
            "",
            "namespace Collatz",
            "",
            "def run048S4SemanticWitnesses : List S4ParentTransitionSemanticWitness :=",
            _lean_list([_lean_s4_witness(witness) for witness in s4_witnesses]),
            "",
            f"theorem run048_s4_semantic_witness_count : run048S4SemanticWitnesses.length = {len(s4_witnesses)} := by",
            "  native_decide",
            "",
            "def checkRun048S4SemanticWitness (w : S4ParentTransitionSemanticWitness) : Bool :=",
            "  decide w.Valid",
            "",
            "def checkAllRun048S4SemanticWitnesses : Bool :=",
            "  run048S4SemanticWitnesses.all checkRun048S4SemanticWitness",
            "",
            "theorem run048_s4_semantic_witnesses_valid_check :",
            "    checkAllRun048S4SemanticWitnesses = true := by",
            "  native_decide",
            "",
            "theorem run048_s4_semantic_witnesses_valid :",
            "    (∀ w ∈ run048S4SemanticWitnesses, w.Valid) := by",
            "  native_decide",
            "",
            "end Collatz",
            "",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witnesses", type=Path, default=WITNESSES_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args(argv)
    generate(args.witnesses, args.out)


if __name__ == "__main__":
    main()
