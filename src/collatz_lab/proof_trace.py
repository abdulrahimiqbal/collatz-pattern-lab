"""Verifier-backed proof-search trace records.

The proof-policy layer treats proof search as a game:

    open obligation -> candidate proof action -> exact verifier result -> reward

This module stores those attempts in a small JSONL format suitable for later
policy/value-model training.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .proof_actions import ProofAction, action_from_dict


RESULT_STATUSES = {
    "CLOSED",
    "REDUCED",
    "NEEDS_SPLIT",
    "FAILED",
    "INVALID",
}


@dataclass(frozen=True)
class ProofActionResult:
    """Outcome of executing one proof action against one obligation."""

    status: str
    reward: int
    proof_status: str
    message: str = ""
    new_obligations: list[dict[str, Any]] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in RESULT_STATUSES:
            raise ValueError(f"unknown proof action result status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProofTrace:
    """One verifier-backed proof-search transition."""

    obligation_id: str
    obligation_before: dict[str, Any]
    action: ProofAction
    result: ProofActionResult
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "obligation_id": self.obligation_id,
            "obligation_before": self.obligation_before,
            "action": self.action.to_dict(),
            "result": self.result.to_dict(),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


def trace_from_dict(row: dict[str, Any]) -> ProofTrace:
    """Load a trace from its JSON representation."""

    return ProofTrace(
        obligation_id=str(row["obligation_id"]),
        obligation_before=dict(row["obligation_before"]),
        action=action_from_dict(dict(row["action"])),
        result=ProofActionResult(**dict(row["result"])),
        created_at=str(row.get("created_at", "")),
    )


def append_trace(path: str | Path, trace: ProofTrace) -> None:
    """Append one trace as JSONL."""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as handle:
        handle.write(trace.to_json() + "\n")


def write_traces(path: str | Path, traces: list[ProofTrace]) -> None:
    """Write traces as JSONL, replacing the destination."""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(trace.to_json() for trace in traces) + ("\n" if traces else ""), encoding="utf-8")


def load_traces(path: str | Path) -> list[ProofTrace]:
    """Load JSONL proof-search traces."""

    source = Path(path)
    if not source.exists():
        return []
    traces: list[ProofTrace] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.strip():
            traces.append(trace_from_dict(json.loads(line)))
    return traces
