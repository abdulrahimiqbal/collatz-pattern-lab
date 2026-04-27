"""Canonical proof-compiler schemas.

These dataclasses intentionally describe proof objects rather than model
outputs.  A neural policy may propose actions, but only exact certificates using
these statuses are allowed to close proof obligations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CLOSED_STATUSES = {
    "CLOSED_BY_ANCESTOR_DESCENT",
    "CLOSED_BY_TRANSITION_TO_CLOSED_STATE",
    "CLOSED_BY_HEIGHT_RANKING",
    "CLOSED_BY_EXACT_POTENTIAL",
}

OPEN_STATUSES = {"NEEDS_SPLIT", "UNKNOWN"}
FINAL_STATUSES = CLOSED_STATUSES | OPEN_STATUSES


@dataclass(frozen=True)
class ProofState:
    state_id: str
    kind: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Transition:
    transition_id: str
    source_state: str
    target_state: str
    A: int
    B: int
    D: int
    status: str = "UNKNOWN"
    domain: dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if self.D <= 0:
            raise ValueError("transition denominator D must be positive")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Certificate:
    certificate_id: str
    status: str
    claim: str
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in FINAL_STATUSES and not self.status.startswith("PROVED_"):
            raise ValueError(f"unsupported certificate status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RankingCertificate:
    certificate_id: str
    status: str
    scc_id: str
    ranking_kind: str
    ranking_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in CLOSED_STATUSES and self.status not in OPEN_STATUSES:
            raise ValueError(f"unsupported ranking status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProofObligation:
    obligation_id: str
    status: str
    scope: str
    claim: str
    coverage: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in FINAL_STATUSES:
            raise ValueError(f"unsupported obligation status: {self.status}")

    @property
    def is_closed(self) -> bool:
        return self.status in CLOSED_STATUSES

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["is_closed"] = self.is_closed
        return row


def status_is_closed(status: str) -> bool:
    return status in CLOSED_STATUSES


def status_is_open(status: str) -> bool:
    return status in OPEN_STATUSES
