"""Proof-scope audit helpers after the RUN-057 global entry check."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN057_UNCOVERED = REPO_ROOT / "certificate_store/run057_uncovered_parent_families.jsonl"
DEFAULT_UNCOVERED_CANDIDATES = [
    REPO_ROOT / "certificate_store/run069_remaining_uncovered_parent_families.jsonl",
    REPO_ROOT / "certificate_store/run068_remaining_uncovered_parent_families.jsonl",
    REPO_ROOT / "certificate_store/run066_remaining_uncovered_parent_families.jsonl",
    REPO_ROOT / "certificate_store/run065_remaining_uncovered_parent_families.jsonl",
    REPO_ROOT / "certificate_store/run060_remaining_uncovered_parent_families.jsonl",
    REPO_ROOT / "certificate_store/run058_remaining_uncovered_parent_families.jsonl",
    RUN057_UNCOVERED,
]


def latest_uncovered_families_path() -> Path:
    for path in DEFAULT_UNCOVERED_CANDIDATES:
        if path.exists():
            return path
    return RUN057_UNCOVERED


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(data: Any, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_proof_scope_status(
    *,
    strict_replay: dict[str, Any],
    uncovered_families_path: str | Path | None = None,
) -> dict[str, Any]:
    subsystem_confidence = strict_replay.get(
        "subsystem_proof_confidence_percent",
        strict_replay.get("proof_confidence_percent", 0.0),
    )
    subsystem_status = strict_replay.get("subsystem_strict_verifier", strict_replay.get("strict_verifier", "UNKNOWN"))
    uncovered_path = Path(uncovered_families_path) if uncovered_families_path is not None else latest_uncovered_families_path()
    if not uncovered_path.exists():
        return {
            "schema": "collatz_lab.proof_scope_status",
            "version": 1,
            "scope_status": "GLOBAL_ENTRY_AUDIT_MISSING",
            "subsystem_status": subsystem_status,
            "global_verifier_status": "GLOBAL_ENTRY_AUDIT_MISSING",
            "public_proof_confidence_percent": 0.0,
            "subsystem_proof_confidence_percent": subsystem_confidence,
            "uncovered_family_count": None,
            "uncovered_families": [],
        }
    uncovered = read_jsonl(uncovered_path)
    if uncovered:
        return {
            "schema": "collatz_lab.proof_scope_status",
            "version": 1,
            "scope_status": "UNIVERSAL_COLLATZ_ENTRY_FAIL",
            "subsystem_status": "CERTIFIED_SUBSYSTEM_PASS"
            if subsystem_status == "PASS"
            else subsystem_status,
            "global_verifier_status": "UNIVERSAL_COLLATZ_ENTRY_FAIL",
            "public_proof_confidence_percent": 0.0,
            "subsystem_proof_confidence_percent": subsystem_confidence,
            "uncovered_family_count": len(uncovered),
            "uncovered_families": uncovered,
        }
    return {
        "schema": "collatz_lab.proof_scope_status",
        "version": 1,
        "scope_status": "UNIVERSAL_ENTRY_COVERAGE_CLOSED",
        "subsystem_status": subsystem_status,
        "global_verifier_status": strict_replay.get("verifier_status", "UNKNOWN"),
        "public_proof_confidence_percent": strict_replay.get("proof_confidence_percent", 0.0),
        "subsystem_proof_confidence_percent": subsystem_confidence,
        "uncovered_family_count": 0,
        "uncovered_families": [],
    }
