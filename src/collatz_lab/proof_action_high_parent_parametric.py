"""RUN-059 high-parent parametric entry audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ID = "RUN-059-high-parent-parametric-entry"
SCHEMA = "collatz_lab.run059_high_parent_parametric_entry"
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


def build_high_parent_entry_taxonomy() -> dict[str, Any]:
    taxonomy = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "status": "FAIL",
        "failure_reason": "FINITE_SYSTEM_ROOT_RELATIVE_DESCENT_GAP",
        "family_id": "odd_entry_parent_levels_ge_33",
        "parent_level_range": {"type": "tail", "lower_bound": 33},
        "q_domain": "q > 0 and q % 2 = 1",
        "proved_transition": {
            "statement": "For a >= 32, P_a(q) reaches P_32(3^(a-32)*q) after 2*(a-32) Collatz steps.",
            "root_expr": "2^a*q - 1",
            "entry_current_expr": "2^32 * 3^(a-32) * q - 1",
            "lean_theorem": "Collatz.high_parent_to_p32",
        },
        "route_attempts": [
            {
                "route": "DIRECT_DESCENT_BEFORE_FINITE_ENTRY",
                "status": "FAIL",
                "failure_reason": "HIGH_PARENT_DESCENT_BELOW_ROOT_GAP",
                "detail": "forced transition to P32 grows the odd coordinate by 3^(a-32); no descent-before-entry certificate is present",
            },
            {
                "route": "FINITE_SYSTEM_DESCENT_BELOW_ORIGINAL_ROOT",
                "status": "FAIL",
                "failure_reason": "FINITE_SYSTEM_ROOT_RELATIVE_DESCENT_GAP",
                "detail": "finite system descent is not root-relative to 2^a*q - 1 after the high-parent growth step",
            },
            {
                "route": "SEPARATE_HIGH_PARENT_RANKING",
                "status": "FAIL",
                "failure_reason": "HIGH_PARENT_RANKING_GAP",
                "detail": "no high-parent ranking/descent theorem is present in the current payloads",
            },
        ],
    }
    taxonomy["taxonomy_hash"] = stable_hash({key: value for key, value in taxonomy.items() if key != "taxonomy_hash"})
    return taxonomy


def build_high_parent_transition_certificate() -> dict[str, Any]:
    cert = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "kind": "HIGH_PARENT_TO_P32_TRANSITION_CERTIFICATE",
        "statement": "For a >= 32 and q > 0, Collatz.iter (2*(a-32)) (2^a*q - 1) = 2^32*(3^(a-32)*q) - 1.",
        "semantic_role": "TRANSITION_ONLY_NOT_DESCENT",
        "lean_theorem": "Collatz.high_parent_to_p32",
        "root_relative_descent_proved": False,
    }
    cert["certificate_hash"] = stable_hash({key: value for key, value in cert.items() if key != "certificate_hash"})
    return cert
