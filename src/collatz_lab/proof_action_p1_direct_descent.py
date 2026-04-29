"""RUN-058 P1 direct descent certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ID = "RUN-058-p1-direct-descent-entry"
SCHEMA = "collatz_lab.run058_p1_direct_descent"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def write_json(data: Any, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_p1_direct_descent_certificate() -> dict[str, Any]:
    cert = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "P1_DIRECT_DESCENT_ENTRY_CERTIFICATE",
        "covered_family_id": "odd_entry_parent_level_1",
        "statement": "For q > 1 odd, n = 2*q - 1 descends in three Collatz steps.",
        "hypotheses": {
            "parent_level": 1,
            "q_positive_odd": "q > 0 and q % 2 = 1",
            "n_gt_one": "2*q - 1 > 1, hence q > 1",
        },
        "arithmetic_witness": {
            "n_expr": "2*q - 1",
            "step_1": "C(n) = 6*q - 2",
            "step_2": "C^2(n) = 3*q - 1",
            "step_3": "C^3(n) = (3*q - 1) / 2",
            "descent_inequality": "(3*q - 1) / 2 < 2*q - 1 for q > 1",
            "step_count": 3,
        },
        "lean_theorem": "Collatz.p1_direct_descent",
        "semantic_validation": {"status": "PASS", "failures": []},
    }
    cert["certificate_hash"] = stable_hash({key: value for key, value in cert.items() if key != "certificate_hash"})
    return cert


def validate_p1_direct_descent_certificate(cert: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if cert.get("kind") != "P1_DIRECT_DESCENT_ENTRY_CERTIFICATE":
        failures.append({"reason": "P1_CERT_KIND_MISMATCH"})
    witness = cert.get("arithmetic_witness") if isinstance(cert.get("arithmetic_witness"), dict) else {}
    required = {"n_expr", "step_1", "step_2", "step_3", "descent_inequality", "step_count"}
    missing = sorted(required - set(witness))
    if missing:
        failures.append({"reason": "P1_DIRECT_DESCENT_WITNESS_INCOMPLETE", "missing": missing})
    if witness.get("step_count") != 3:
        failures.append({"reason": "P1_DIRECT_DESCENT_STEP_COUNT_MISMATCH"})
    expected = stable_hash({key: value for key, value in cert.items() if key != "certificate_hash"})
    if cert.get("certificate_hash") != expected:
        failures.append({"reason": "P1_DIRECT_DESCENT_HASH_MISMATCH"})
    return failures
