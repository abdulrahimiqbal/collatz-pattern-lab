"""Structured proof-action DSL for verifier-backed proof search."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


ACTION_TYPES = [
    "SPLIT_BY_RESIDUE",
    "SPLIT_BY_H",
    "SPLIT_BY_PARENT_LEVEL",
    "LIFT_CUBE",
    "TRY_ADIC_BASIN",
    "TRY_VALUATION_CLOSURE",
    "TRY_ANCESTOR_COMPOSITION",
    "TRY_SCC_POTENTIAL",
    "TRY_SCC_RANKING",
    "PROMOTE_TO_PARENT_STATE",
    "TRY_PARENT_TRANSITION_TEMPLATE",
    "GENERALIZE_IN_A",
    "PROPOSE_VALUATION_FORM",
    "PROPOSE_POTENTIAL",
    "PROPOSE_PROOF_DSL",
    "PROPOSE_MIXED_MODULUS_STATE",
    "PROPOSE_DEBT_RANK",
    "TRY_MIXED_MODULUS_DEBT_VERIFIER",
    "SELF_CORRECT_PROOF_DSL",
    "RUN_FALSIFIER",
]


@dataclass(frozen=True)
class ProofAction:
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    rationale: str = ""

    def __post_init__(self) -> None:
        if self.action not in ACTION_TYPES:
            raise ValueError(f"unknown proof action: {self.action}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


def action_from_dict(row: dict[str, Any]) -> ProofAction:
    return ProofAction(
        action=str(row["action"]),
        params=dict(row.get("params", {})),
        score=float(row.get("score", 0.0)),
        rationale=str(row.get("rationale", "")),
    )
