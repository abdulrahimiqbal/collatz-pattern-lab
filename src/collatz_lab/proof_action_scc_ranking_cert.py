"""RUN-033 exact SCC ranking-certificate attempt.

This module deliberately separates the exact S4 transition replay already
available in RUN-022 from the stronger parent-coordinate semantics needed to
rank the unresolved RUN-030 SCC.  A HIGH_PARENT_SUCCESSOR_EXACT certificate
proves a local ``z(k)`` successor statement; RUN-033 only composes or ranks it
after an explicit ``q -> q'`` parent-coordinate affine map is present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .proof_action_parent_transition_cert import _certificate_hash as parent_transition_hash
from .proof_action_parent_transition_cert import parse_branch_id
from .utils import load_yaml


RUN_ID = "RUN-033-exact-scc-cycle-ranking-certificate"
SCHEMA = "collatz_lab.scc_cycle_ranking_certificate"
DEFAULT_RUN030_DIR = Path("reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening")
DEFAULT_OUT_DIR = Path(f"reports/runs/{RUN_ID}")
DEFAULT_MISSING_FIELDS = (
    "source_parent_coordinate_parameterization",
    "q_to_k_affine_map",
    "target_parent_coordinate_formula",
    "integrality_domain_for_q",
)


@dataclass(frozen=True)
class ExtractionResult:
    edges: list[dict[str, Any]]
    failures: list[dict[str, Any]]

    @property
    def accepted(self) -> bool:
        return not self.failures


@dataclass(frozen=True)
class AffineMapReplay:
    accepted: bool
    row: dict[str, Any]


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def scc_ranking_certificate_hash(certificate: dict[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_hash"}
    return _hash(payload)


def _artifact_hashes(manifest_path: str | Path | None) -> dict[str, str]:
    if not manifest_path:
        return {}
    manifest = _load_json(manifest_path)
    return {str(entry.get("name")): str(entry.get("sha256")) for entry in manifest.get("artifacts", []) if entry.get("name")}


def _artifact_path(manifest_path: str | Path | None, name: str) -> Path | None:
    if not manifest_path:
        return None
    manifest_file = Path(manifest_path)
    manifest = _load_json(manifest_file)
    for entry in manifest.get("artifacts", []):
        if entry.get("name") != name:
            continue
        raw = Path(str(entry.get("path")))
        return raw if raw.is_absolute() else manifest_file.parent / raw
    return None


def _row_certificate(row: dict[str, Any]) -> dict[str, Any]:
    certificate = row.get("transition_certificate")
    if isinstance(certificate, dict):
        return certificate
    action = row.get("action")
    if isinstance(action, dict) and isinstance(action.get("transition_certificate"), dict):
        return action["transition_certificate"]
    return {}


def _index_s4_rows(s4_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in s4_rows:
        cert = _row_certificate(row)
        for key in (
            str(cert.get("transition_id", "")),
            str(cert.get("certificate_id", "")),
            str(cert.get("certificate_hash", "")),
            str(row.get("node_id", "")),
        ):
            if key:
                indexed[key] = row
    return indexed


def _parent_label(value: Any) -> str:
    text = str(value)
    if text.startswith("P"):
        return text
    return f"P{text}"


def _parent_number(label: Any) -> int:
    text = str(label)
    if text.startswith("P"):
        text = text[1:]
    return int(text)


def _status_only_failure(edge: dict[str, Any], row: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "edge_id": edge.get("edge_id"),
        "node_id": edge.get("node_id"),
        "transition_certificate_id": edge.get("transition_certificate_id"),
        "reason": "REJECT_STATUS_ONLY_EDGE",
        "detail": "SCC edge has verifier/status metadata but no replayable HIGH_PARENT_SUCCESSOR_EXACT payload",
        "available_keys": sorted(row.keys()) if isinstance(row, dict) else [],
    }


def _domain_constraints(certificate: dict[str, Any]) -> list[dict[str, Any]]:
    branch = parse_branch_id(str(certificate.get("branch_id")))
    divisibility = certificate.get("divisibility_certificate")
    symbolic = certificate.get("symbolic_map")
    if not isinstance(divisibility, dict):
        divisibility = {}
    if not isinstance(symbolic, dict):
        symbolic = {}
    constraints = [
        {
            "kind": "source_branch_residue",
            "branch_id": certificate.get("branch_id"),
            "source_parent": branch["a"],
            "source_residue": branch["residue"],
            "source_depth": branch["depth"],
            "modulus": 1 << branch["depth"],
            "residue": branch["residue"],
            "note": "This is the S4 branch residue from the existing payload; it is not by itself a parent-coordinate q map.",
        },
        {
            "kind": "k_divisibility",
            "modulus": int(divisibility.get("k_divisibility_modulus", 0) or 0),
            "residue": int(divisibility.get("k_divisibility_residue", 0) or 0),
            "valuation": int(certificate.get("valuation", 0) or 0),
        },
        {
            "kind": "excluded_next_power",
            "modulus": int(divisibility.get("excluded_next_power_modulus", 0) or 0),
            "residue": int(divisibility.get("excluded_next_power_residue", 0) or 0),
        },
    ]
    z_family = symbolic.get("z_family")
    if z_family:
        constraints.append({"kind": "z_family", "expression": z_family})
    return constraints


def _edge_from_s4_row(scc_edge: dict[str, Any], row: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    cert = _row_certificate(row)
    if not cert:
        return None, _status_only_failure(scc_edge, row)
    if cert.get("type") not in {"HIGH_PARENT_SUCCESSOR_EXACT", "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP"}:
        return None, {
            "edge_id": scc_edge.get("edge_id"),
            "transition_certificate_id": scc_edge.get("transition_certificate_id"),
            "reason": "UNSUPPORTED_TRANSITION_CERTIFICATE_TYPE",
            "type": cert.get("type"),
        }
    if cert.get("status") != "PASS":
        return None, {
            "edge_id": scc_edge.get("edge_id"),
            "transition_certificate_id": scc_edge.get("transition_certificate_id"),
            "reason": "TRANSITION_CERTIFICATE_NOT_PASS",
            "status": cert.get("status"),
        }
    computed_hash = parent_transition_hash(cert)
    cert_hash = str(cert.get("certificate_hash", ""))
    if cert_hash != computed_hash:
        return None, {
            "edge_id": scc_edge.get("edge_id"),
            "transition_certificate_id": scc_edge.get("transition_certificate_id"),
            "reason": "TRANSITION_CERTIFICATE_HASH_MISMATCH",
            "certificate_hash": cert_hash,
            "computed_hash": computed_hash,
        }
    if (
        scc_edge.get("transition_certificate_hash")
        and scc_edge["transition_certificate_hash"] != cert_hash
        and cert.get("type") != "HIGH_PARENT_SUCCESSOR_EXACT_WITH_PARENT_MAP"
    ):
        return None, {
            "edge_id": scc_edge.get("edge_id"),
            "transition_certificate_id": scc_edge.get("transition_certificate_id"),
            "reason": "SCC_EDGE_CERTIFICATE_HASH_MISMATCH",
            "edge_hash": scc_edge.get("transition_certificate_hash"),
            "certificate_hash": cert_hash,
        }
    source_parent = _parent_number(scc_edge.get("source"))
    target_parent = _parent_number(scc_edge.get("target"))
    if int(cert.get("source_parent", -1)) != source_parent or int(cert.get("target_parent", -1)) != target_parent:
        return None, {
            "edge_id": scc_edge.get("edge_id"),
            "transition_certificate_id": scc_edge.get("transition_certificate_id"),
            "reason": "SCC_EDGE_PARENT_MISMATCH",
            "edge_source": scc_edge.get("source"),
            "edge_target": scc_edge.get("target"),
            "certificate_source_parent": cert.get("source_parent"),
            "certificate_target_parent": cert.get("target_parent"),
        }
    action = row.get("action") if isinstance(row.get("action"), dict) else {}
    edge = {
        "edge_id": str(scc_edge.get("edge_id")),
        "source": _parent_label(source_parent),
        "target": _parent_label(target_parent),
        "source_parent": source_parent,
        "target_parent": target_parent,
        "branch_id": str(cert.get("branch_id")),
        "valuation": int(cert.get("valuation", 0) or 0),
        "transition_certificate_id": str(cert.get("transition_id")),
        "transition_certificate_hash": cert_hash,
        "node_id": str(row.get("node_id") or scc_edge.get("node_id") or ""),
        "branch_action": {
            "type": action.get("type"),
            "target": action.get("target"),
            "source_parent": action.get("source_parent"),
            "target_parent": action.get("target_parent"),
            "valuation": action.get("valuation"),
        },
        "exact_symbolic_transition_payload": cert,
        "domain_constraints": _domain_constraints(cert),
        "parent_coordinate_map": None,
    }
    explicit_map = _explicit_parent_coordinate_map(cert)
    if explicit_map is not None:
        edge["parent_coordinate_map"] = explicit_map
    return edge, None


def extract_scc_internal_edges(
    scc_rows: list[dict[str, Any]],
    s4_rows: list[dict[str, Any]],
) -> ExtractionResult:
    """Build the exact directed multigraph for the unresolved RUN-030 SCC."""

    indexed = _index_s4_rows(s4_rows)
    edges: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for scc in scc_rows:
        for scc_edge in scc.get("edges", []) or []:
            if scc_edge.get("kind") != "HIGH_PARENT_SUCCESSOR_EXACT":
                failures.append(
                    {
                        "edge_id": scc_edge.get("edge_id"),
                        "reason": "UNSUPPORTED_SCC_EDGE_KIND",
                        "kind": scc_edge.get("kind"),
                    }
                )
                continue
            row = (
                indexed.get(str(scc_edge.get("transition_certificate_id", "")))
                or indexed.get(str(scc_edge.get("transition_certificate_hash", "")))
                or indexed.get(str(scc_edge.get("node_id", "")))
            )
            if row is None:
                failures.append(
                    {
                        "edge_id": scc_edge.get("edge_id"),
                        "node_id": scc_edge.get("node_id"),
                        "transition_certificate_id": scc_edge.get("transition_certificate_id"),
                        "reason": "MISSING_TRANSITION_CERTIFICATE",
                    }
                )
                continue
            edge, failure = _edge_from_s4_row(scc_edge, row)
            if failure:
                failures.append(failure)
            elif edge:
                edges.append(edge)
    edges.sort(key=lambda row: (row["source"], row["target"], row["edge_id"]))
    return ExtractionResult(edges=edges, failures=failures)


def _explicit_parent_coordinate_map(certificate: dict[str, Any]) -> dict[str, Any] | None:
    symbolic = certificate.get("symbolic_map")
    candidates = [
        certificate.get("parent_coordinate_map"),
        symbolic.get("parent_coordinate_map") if isinstance(symbolic, dict) else None,
        certificate.get("affine_parent_coordinate_map"),
    ]
    for candidate in candidates:
        if isinstance(candidate, dict):
            return candidate
    return None


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _normalise_affine_map(raw_map: dict[str, Any], *, edge: dict[str, Any]) -> dict[str, Any]:
    A = _as_int(raw_map.get("A"), "A")
    B = _as_int(raw_map.get("B"), "B")
    D = _as_int(raw_map.get("D"), "D")
    if D <= 0:
        raise ValueError("D must be a positive integer")
    modulus = _as_int(raw_map.get("domain_modulus", raw_map.get("M", 1)), "domain_modulus")
    residue = _as_int(raw_map.get("domain_residue", raw_map.get("r", 0)), "domain_residue")
    minimum_q = _as_int(raw_map.get("minimum_q", 1), "minimum_q")
    if modulus <= 0:
        raise ValueError("domain_modulus must be positive")
    if minimum_q <= 0:
        raise ValueError("minimum_q must be positive")
    residue %= modulus
    gcd = math.gcd(math.gcd(abs(A), abs(B)), D)
    if gcd > 1:
        A //= gcd
        B //= gcd
        D //= gcd
    return {
        "edge_id": edge["edge_id"],
        "source": edge["source"],
        "target": edge["target"],
        "source_parent": edge["source_parent"],
        "target_parent": edge["target_parent"],
        "transition_certificate_id": edge["transition_certificate_id"],
        "transition_certificate_hash": edge["transition_certificate_hash"],
        "A": A,
        "B": B,
        "D": D,
        "domain_modulus": modulus,
        "domain_residue": residue,
        "minimum_q": minimum_q,
        "integrality_conditions": list(raw_map.get("integrality_conditions") or []),
        "statement": f"q' = ({A}*q + {B}) / {D}",
    }


def derive_parent_coordinate_affine_map(edge: dict[str, Any]) -> AffineMapReplay:
    """Replay an explicit parent-coordinate affine map, if the payload has one."""

    certificate = edge.get("exact_symbolic_transition_payload")
    if not isinstance(certificate, dict):
        return AffineMapReplay(
            False,
            {
                "edge_id": edge.get("edge_id"),
                "transition_certificate_id": edge.get("transition_certificate_id"),
                "status": "FAIL",
                "failure_classification": "MISSING_AFFINE_EDGE_MAP",
                "missing_fields": ["exact_symbolic_transition_payload"],
            },
        )
    raw_map = _explicit_parent_coordinate_map(certificate)
    if raw_map is None:
        return AffineMapReplay(
            False,
            {
                "edge_id": edge.get("edge_id"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "branch_id": edge.get("branch_id"),
                "transition_certificate_id": edge.get("transition_certificate_id"),
                "transition_certificate_hash": edge.get("transition_certificate_hash"),
                "status": "FAIL",
                "failure_classification": "MISSING_PARENT_COORDINATE_MAP",
                "missing_fields": list(DEFAULT_MISSING_FIELDS),
                "available_symbolic_fields": sorted((certificate.get("symbolic_map") or {}).keys()),
                "available_certificate_fields": sorted(certificate.keys()),
                "detail": "HIGH_PARENT_SUCCESSOR_EXACT supplies z(k) successor algebra, but no exact q -> k -> q' parent-coordinate map.",
            },
        )
    try:
        affine = _normalise_affine_map(raw_map, edge=edge)
    except ValueError as exc:
        return AffineMapReplay(
            False,
            {
                "edge_id": edge.get("edge_id"),
                "transition_certificate_id": edge.get("transition_certificate_id"),
                "status": "FAIL",
                "failure_classification": "MISSING_AFFINE_EDGE_MAP",
                "reason": str(exc),
            },
        )
    return AffineMapReplay(
        True,
        {
            **affine,
            "status": "PASS",
            "replay_checks": {
                "source_parent_identity": f"n = 2^{edge['source_parent']}*q - 1",
                "target_parent_identity": f"n' = 2^{edge['target_parent']}*q' - 1",
                "positive_integer_domain": True,
                "explicit_payload_required": True,
            },
        },
    )


def derive_all_affine_edge_maps(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [derive_parent_coordinate_affine_map(edge).row for edge in edges]


def _normalise_fraction_triple(A: int, B: int, D: int) -> dict[str, int]:
    if D < 0:
        A, B, D = -A, -B, -D
    gcd = math.gcd(math.gcd(abs(A), abs(B)), abs(D))
    if gcd > 1:
        A //= gcd
        B //= gcd
        D //= gcd
    return {"A": A, "B": B, "D": D}


def compose_affine_maps(edge_maps: list[dict[str, Any]]) -> dict[str, Any]:
    """Compose q'=(Aq+B)/D maps exactly."""

    A_acc = 1
    B_acc = 0
    D_acc = 1
    edge_ids: list[str] = []
    for edge_map in edge_maps:
        A = _as_int(edge_map.get("A"), "A")
        B = _as_int(edge_map.get("B"), "B")
        D = _as_int(edge_map.get("D"), "D")
        if D <= 0:
            raise ValueError("D must be positive")
        edge_ids.append(str(edge_map.get("edge_id", "")))
        A_acc, B_acc, D_acc = A * A_acc, A * B_acc + B * D_acc, D * D_acc
        normal = _normalise_fraction_triple(A_acc, B_acc, D_acc)
        A_acc, B_acc, D_acc = normal["A"], normal["B"], normal["D"]
    return {
        "A": A_acc,
        "B": B_acc,
        "D": D_acc,
        "edge_ids": edge_ids,
        "statement": f"q_final = ({A_acc}*q + {B_acc}) / {D_acc}",
    }


def check_affine_cycle_descent(edge_maps: list[dict[str, Any]], *, minimum_q: int = 1) -> dict[str, Any]:
    composed = compose_affine_maps(edge_maps)
    A = int(composed["A"])
    B = int(composed["B"])
    D = int(composed["D"])
    if minimum_q <= 0:
        raise ValueError("minimum_q must be positive")
    slope_decreases = A < D
    equal_slope_negative_shift = A == D and B < 0
    minimum_passes = (D - A) * minimum_q > B if (slope_decreases or equal_slope_negative_shift) else False
    accepted = minimum_passes
    return {
        "cycle_id": _hash({"edge_ids": composed["edge_ids"], "kind": "affine_cycle"})[:16],
        "edge_ids": composed["edge_ids"],
        "composed_map": {"A": str(A), "B": str(B), "D": str(D)},
        "descent_check": {
            "kind": "affine_q_descent",
            "inequality": "A*q + B < D*q",
            "minimum_q_checked": str(minimum_q),
            "slope_decreases": slope_decreases,
            "equal_slope_negative_shift": equal_slope_negative_shift,
            "minimum_domain_passes": minimum_passes,
            "status": "PASS" if accepted else "FAIL",
        },
        "status": "PASS" if accepted else "FAIL",
    }


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(str(value))


def _coefficients(certificate: dict[str, Any], state: str) -> tuple[Fraction, Fraction]:
    coeffs = certificate.get("coefficients")
    if not isinstance(coeffs, dict) or state not in coeffs:
        raise ValueError(f"missing coefficients for {state}")
    row = coeffs[state]
    if not isinstance(row, dict):
        raise ValueError(f"coefficient row for {state} must be an object")
    return _fraction(row.get("alpha", 0)), _fraction(row.get("beta", 0))


def _edge_map_by_id(edges: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for edge in edges:
        edge_map = edge.get("parent_coordinate_map")
        if isinstance(edge_map, dict):
            merged = {**edge_map}
            for key in ("edge_id", "source", "target", "source_parent", "target_parent"):
                merged.setdefault(key, edge.get(key))
            out[str(edge["edge_id"])] = merged
        elif all(key in edge for key in ("A", "B", "D")):
            out[str(edge["edge_id"])] = edge
    return out


def _ranking_edge_check(edge_map: dict[str, Any], certificate: dict[str, Any]) -> dict[str, Any]:
    source = str(edge_map["source"])
    target = str(edge_map["target"])
    alpha_source, beta_source = _coefficients(certificate, source)
    alpha_target, beta_target = _coefficients(certificate, target)
    A = Fraction(_as_int(edge_map.get("A"), "A"), 1)
    B = Fraction(_as_int(edge_map.get("B"), "B"), 1)
    D = Fraction(_as_int(edge_map.get("D"), "D"), 1)
    minimum_q = _as_int(edge_map.get("minimum_q", 1), "minimum_q")
    slope = alpha_source - alpha_target * A / D
    intercept = beta_source - beta_target - alpha_target * B / D
    if slope < 0:
        accepted = False
        reason = "negative_delta_slope"
        min_delta = None
    else:
        min_delta = slope * minimum_q + intercept
        accepted = min_delta > 0
        reason = "strict_decrease" if accepted else "non_decreasing_at_minimum_q"
    return {
        "edge_id": edge_map["edge_id"],
        "source": source,
        "target": target,
        "source_rank_expr": f"{alpha_source}*q + {beta_source}",
        "target_rank_expr": f"{alpha_target}*(({edge_map['A']})*q + ({edge_map['B']}))/({edge_map['D']}) + {beta_target}",
        "delta_slope": str(slope),
        "delta_intercept": str(intercept),
        "minimum_q": minimum_q,
        "minimum_delta": str(min_delta) if min_delta is not None else None,
        "decrease_certificate": reason,
        "status": "PASS" if accepted else "FAIL",
    }


def check_affine_ranking_certificate(certificate: dict[str, Any], edges: list[dict[str, Any]]) -> dict[str, Any]:
    edge_maps = _edge_map_by_id(edges)
    expected_edge_ids = set(edge_maps)
    checked_edge_ids = {str(row.get("edge_id")) for row in certificate.get("edge_checks", []) or []}
    failures: list[dict[str, Any]] = []
    if certificate.get("type") not in {"SCC_WELL_FOUNDED_RANKING_EXACT", "SCC_INTERNAL_RANKING_EXACT"}:
        failures.append({"reason": "unsupported_scc_ranking_certificate_type", "type": certificate.get("type")})
    if certificate.get("ranking_kind") not in {"affine", "lexicographic_affine", "cycle_potential", "mixed_debt"}:
        failures.append({"reason": "unsupported_ranking_kind", "ranking_kind": certificate.get("ranking_kind")})
    missing_edges = sorted(expected_edge_ids - checked_edge_ids)
    extra_edges = sorted(checked_edge_ids - expected_edge_ids)
    if missing_edges:
        failures.append({"reason": "ranking_certificate_missing_internal_edges", "missing_edge_ids": missing_edges})
    if extra_edges:
        failures.append({"reason": "ranking_certificate_has_unknown_edges", "extra_edge_ids": extra_edges})
    replayed_checks: list[dict[str, Any]] = []
    for edge_id in sorted(expected_edge_ids):
        try:
            check = _ranking_edge_check(edge_maps[edge_id], certificate)
        except (ValueError, KeyError) as exc:
            check = {"edge_id": edge_id, "status": "FAIL", "reason": str(exc)}
        replayed_checks.append(check)
        if check.get("status") != "PASS":
            failures.append({"reason": "non_decreasing_edge", "edge_check": check})
    if str(certificate.get("certificate_hash", "")) != scc_ranking_certificate_hash(certificate):
        failures.append(
            {
                "reason": "scc_ranking_certificate_hash_mismatch",
                "certificate_hash": certificate.get("certificate_hash"),
                "computed_hash": scc_ranking_certificate_hash(certificate),
            }
        )
    accepted = not failures
    return {
        "accepted": accepted,
        "status": "PASS" if accepted else "FAIL",
        "edge_count": len(expected_edge_ids),
        "replayed_edge_checks": replayed_checks,
        "failures": failures,
    }


def replay_scc_ranking_certificate(certificate: dict[str, Any], edges: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(certificate, dict):
        return {"accepted": False, "status": "FAIL", "failures": [{"reason": "missing_certificate"}]}
    if certificate.get("ranking_kind") == "affine":
        return check_affine_ranking_certificate(certificate, edges)
    return {
        "accepted": False,
        "status": "FAIL",
        "failures": [{"reason": "ranking_kind_not_implemented_for_replay", "ranking_kind": certificate.get("ranking_kind")}],
    }


def build_affine_ranking_certificate(
    *,
    scc_id: str,
    states: list[str],
    edges: list[dict[str, Any]],
    coefficients: dict[str, dict[str, str | int]],
) -> dict[str, Any]:
    edge_checks = [
        {"edge_id": edge["edge_id"], "source": edge["source"], "target": edge["target"], "status": "PENDING_REPLAY"}
        for edge in edges
    ]
    cert = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "certificate_id": f"run033_scc_ranking_{scc_id}",
        "type": "SCC_WELL_FOUNDED_RANKING_EXACT",
        "scc_id": scc_id,
        "states": states,
        "edges": [{"edge_id": edge["edge_id"], "transition_certificate_id": edge.get("transition_certificate_id")} for edge in edges],
        "ranking_kind": "affine",
        "well_founded_order": "nonnegative_rational_with_common_denominator_over_nat_domain",
        "coefficients": coefficients,
        "edge_checks": edge_checks,
        "status": "PASS",
    }
    cert["certificate_hash"] = scc_ranking_certificate_hash(cert)
    return cert


def build_refined_scc_graph(edges: list[dict[str, Any]]) -> dict[str, Any]:
    refined_edges: list[dict[str, Any]] = []
    nodes: dict[str, dict[str, Any]] = {}
    for edge in edges:
        branch = str(edge.get("branch_id", "unknown"))
        source_node = f"{edge.get('source')}[{branch}]"
        target_node = f"{edge.get('target')}[unresolved_target_domain]"
        nodes.setdefault(source_node, {"parent_state": edge.get("source"), "predicate": {"branch_id": branch}})
        nodes.setdefault(target_node, {"parent_state": edge.get("target"), "predicate": {"target_domain": "unresolved_without_parent_coordinate_map"}})
        refined_edges.append(
            {
                "edge_id": edge["edge_id"],
                "source": source_node,
                "target": target_node,
                "transition_certificate_id": edge.get("transition_certificate_id"),
                "coverage_preserved": True,
            }
        )
    return {
        "schema": "collatz_lab.refined_scc_graph",
        "version": 1,
        "run_id": RUN_ID,
        "node_count": len(nodes),
        "edge_count": len(refined_edges),
        "nodes": nodes,
        "edges": refined_edges,
        "coverage_preserved": len(refined_edges) == len(edges),
        "status": "NOT_RANKED",
        "reason": "refinement by source branch preserves edge coverage but target q-domains are missing without parent-coordinate maps",
    }


def _source_scc_summary(sccs: list[dict[str, Any]]) -> dict[str, Any]:
    if not sccs:
        return {"scc_id": "unknown", "nodes": [], "edge_count": 0}
    first = sccs[0]
    return {
        "scc_id": first.get("scc_id", "unknown"),
        "nodes": list(first.get("nodes") or []),
        "edge_count": int(first.get("edge_count", len(first.get("edges") or [])) or 0),
    }


def _minimal_obstruction(
    *,
    classification: str,
    sccs: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    map_rows: list[dict[str, Any]],
    extraction_failures: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    summary = _source_scc_summary(sccs)
    missing = [row for row in map_rows if row.get("failure_classification") == "MISSING_PARENT_COORDINATE_MAP"]
    return {
        "schema": "collatz_lab.run033_minimal_ranking_obstruction",
        "version": 1,
        "run_id": RUN_ID,
        "classification": classification,
        "status": classification,
        "unresolved_scc_states": summary["nodes"],
        "scc_id": summary["scc_id"],
        "expected_internal_edge_count": summary["edge_count"],
        "extracted_internal_edge_count": len(edges),
        "internal_edges": [
            {
                "edge_id": edge["edge_id"],
                "source": edge["source"],
                "target": edge["target"],
                "branch_id": edge["branch_id"],
                "valuation": edge["valuation"],
                "transition_certificate_id": edge["transition_certificate_id"],
                "transition_certificate_hash": edge["transition_certificate_hash"],
            }
            for edge in edges
        ],
        "extraction_failures": list(extraction_failures or []),
        "missing_parent_coordinate_map_certificate_ids": sorted({str(row.get("transition_certificate_id")) for row in missing}),
        "missing_parent_coordinate_map_count": len(missing),
        "missing_fields_required": list(DEFAULT_MISSING_FIELDS),
        "cycle_composition_status": "NOT_ATTEMPTED_WITHOUT_PARENT_COORDINATE_MAP",
        "parent_level_ranking_status": "RUN032_FOUND_NO_ACCEPTED_CANDIDATE",
        "affine_ranking_status": "NOT_ATTEMPTED_WITHOUT_PARENT_COORDINATE_MAP",
        "lexicographic_ranking_status": "NOT_ATTEMPTED_WITHOUT_PARENT_COORDINATE_MAP",
        "refinement_status": "SOURCE_BRANCH_REFINEMENT_PRESERVES_COVERAGE_BUT_TARGET_DOMAINS_REMAIN_UNINTERPRETED",
        "exact_missing_invariant_type": "parent-coordinate transition invariant or an alternative exact well-founded measure over the existing z(k) transition language",
    }


def _new_math_required(obstruction: dict[str, Any]) -> str:
    states = ", ".join(obstruction.get("unresolved_scc_states") or [])
    missing_count = obstruction.get("missing_parent_coordinate_map_count", 0)
    lines = [
        "# RUN-033 New Math Required",
        "",
        f"- classification: `{obstruction.get('classification')}`",
        f"- unresolved SCC: `{obstruction.get('scc_id')}`",
        f"- states: `{states}`",
        f"- extracted internal exact S4 edges: `{obstruction.get('extracted_internal_edge_count')}`",
        f"- S4 certs missing parent-coordinate maps: `{missing_count}`",
        "",
        "RUN-033 replayed the internal SCC edge certificates as exact HIGH_PARENT_SUCCESSOR_EXACT payloads.",
        "Those payloads prove the existing `z(k)` successor congruence and valuation statement, but they do not expose the algebra needed to rewrite each edge as",
        "",
        "`q' = (A*q + B) / D` for `P_a(q): n = 2^a*q - 1`.",
        "",
        "## Required Semantic Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in DEFAULT_MISSING_FIELDS)
    lines.extend(
        [
            "",
            "Without those fields, cycle composition would be composing an untrusted interpretation rather than replaying the certificate language.",
            "The next replayable certificate must either add exact parent-coordinate maps for all internal SCC edges, or introduce a different exact measure defined directly on the current `z(k)`/valuation domains.",
            "",
        ]
    )
    return "\n".join(lines)


def _empty_failure_certificate(classification: str, obstruction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "certificate_id": "run033_scc_ranking_P12_P24_internal_s4",
        "type": "SCC_WELL_FOUNDED_RANKING_EXACT",
        "scc_id": obstruction.get("scc_id"),
        "states": obstruction.get("unresolved_scc_states", []),
        "ranking_kind": "none",
        "status": "FAIL",
        "failure_classification": classification,
        "reason": obstruction.get("exact_missing_invariant_type"),
    }


def _validate_manifest_artifact_hash(manifest_path: str | Path | None, artifact_name: str, artifact_path: Path) -> dict[str, Any]:
    hashes = _artifact_hashes(manifest_path)
    expected = hashes.get(artifact_name)
    actual = _sha256(artifact_path) if artifact_path.exists() else None
    return {
        "artifact_name": artifact_name,
        "path": str(artifact_path),
        "expected_sha256": expected,
        "actual_sha256": actual,
        "matches": expected is None or expected == actual,
    }


def run_exact_scc_cycle_ranking_certificate(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("scc_ranking_run033", {}) if isinstance(cfg.get("scc_ranking_run033", {}), dict) else {}
    run030_dir = Path(run_cfg.get("run030_dir") or DEFAULT_RUN030_DIR)
    out_dir = Path(out or run_cfg.get("out_dir") or DEFAULT_OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    unresolved_sccs_path = Path(run_cfg.get("unresolved_sccs") or run030_dir / "unresolved_sccs.jsonl")
    s4_path = Path(
        run_cfg.get("parent_transition_certificates")
        or _artifact_path(manifest_path, "parent_transition_certificates")
        or "certificate_store/run030_parent_transition_certificates.jsonl"
    )
    sccs = load_jsonl(unresolved_sccs_path)
    s4_rows = load_jsonl(s4_path)
    manifest_checks = [_validate_manifest_artifact_hash(manifest_path, "parent_transition_certificates", s4_path)]

    extraction = extract_scc_internal_edges(sccs, s4_rows)
    write_jsonl(out_dir / "scc_internal_edges.jsonl", extraction.edges)
    map_rows = derive_all_affine_edge_maps(extraction.edges)
    write_jsonl(out_dir / "scc_affine_edge_maps.jsonl", map_rows)

    pass_maps = [row for row in map_rows if row.get("status") == "PASS"]
    missing_maps = [row for row in map_rows if row.get("failure_classification") == "MISSING_PARENT_COORDINATE_MAP"]
    classification = "PASS"
    if extraction.failures:
        classification = "MISSING_AFFINE_EDGE_MAP"
    if missing_maps:
        classification = "MISSING_PARENT_COORDINATE_MAP"
    elif len(pass_maps) != len(extraction.edges):
        classification = "MISSING_AFFINE_EDGE_MAP"

    cycles_checked: list[dict[str, Any]] = []
    cycle_descent: list[dict[str, Any]] = []
    cycle_obstructions: list[dict[str, Any]] = []
    ranking_certificate: dict[str, Any]
    refined_graph = build_refined_scc_graph(extraction.edges)
    refined_edges = list(refined_graph.get("edges") or [])
    refinement_summary = {
        "schema": "collatz_lab.run033_refinement_summary",
        "version": 1,
        "run_id": RUN_ID,
        "input_edge_count": len(extraction.edges),
        "refined_edge_count": len(refined_edges),
        "coverage_preserved": len(refined_edges) == len(extraction.edges),
        "status": "NOT_RANKED" if classification != "PASS" else "READY_FOR_RANKING",
        "reason": "target parent-coordinate domains are absent" if classification != "PASS" else None,
    }

    if classification != "PASS":
        obstruction = _minimal_obstruction(
            classification=classification,
            sccs=sccs,
            edges=extraction.edges,
            map_rows=map_rows,
            extraction_failures=extraction.failures,
        )
        ranking_certificate = _empty_failure_certificate(classification, obstruction)
        cycle_obstructions.append(
            {
                "status": "FAIL",
                "failure_classification": classification,
                "reason": "cycle composition requires replayed parent-coordinate affine edge maps",
            }
        )
        _write_json(obstruction, out_dir / "minimal_ranking_obstruction.json")
        (out_dir / "new_math_required.md").write_text(_new_math_required(obstruction), encoding="utf-8")
        (out_dir / "refined_ranking_failure_report.md").write_text(
            "# RUN-033 Refined Ranking Failure\n\n"
            f"- classification: `{classification}`\n"
            "- source-branch refinement preserves edge coverage, but target-domain predicates cannot be replayed without parent-coordinate maps.\n",
            encoding="utf-8",
        )
    else:
        # This branch is reserved for future certificates that contain explicit maps.
        # It still refuses to invent coefficients; a ranking payload must replay.
        obstruction = _minimal_obstruction(
            classification="NEEDS_NEW_INVARIANT",
            sccs=sccs,
            edges=extraction.edges,
            map_rows=map_rows,
            extraction_failures=[],
        )
        ranking_certificate = _empty_failure_certificate("NEEDS_NEW_INVARIANT", obstruction)
        classification = "NEEDS_NEW_INVARIANT"
        _write_json(obstruction, out_dir / "minimal_ranking_obstruction.json")
        (out_dir / "new_math_required.md").write_text(_new_math_required(obstruction), encoding="utf-8")
        (out_dir / "refined_ranking_failure_report.md").write_text(
            "# RUN-033 Refined Ranking Failure\n\n- explicit maps replayed, but no replayable ranking coefficients were supplied or synthesized.\n",
            encoding="utf-8",
        )

    write_jsonl(out_dir / "scc_cycles_checked.jsonl", cycles_checked)
    write_jsonl(out_dir / "scc_cycle_descent_certificates.jsonl", cycle_descent)
    write_jsonl(out_dir / "scc_cycle_obstructions.jsonl", cycle_obstructions)
    _write_json(ranking_certificate, out_dir / "scc_ranking_certificate.json")
    _write_json(refined_graph, out_dir / "refined_scc_graph.json")
    write_jsonl(out_dir / "refined_scc_edges.jsonl", refined_edges)
    _write_json(refinement_summary, out_dir / "refinement_summary.json")

    result = {
        "schema": "collatz_lab.run033_exact_scc_cycle_ranking_certificate",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "floating_point_certificate_used": False,
        "status": classification,
        "scc_internal_edge_count": len(extraction.edges),
        "scc_internal_edge_failures": extraction.failures,
        "affine_edge_map_pass": len(pass_maps),
        "affine_edge_map_fail": len(map_rows) - len(pass_maps),
        "missing_parent_coordinate_map_count": len(missing_maps),
        "manifest_artifact_checks": manifest_checks,
        "strict_verifier_updated": False,
        "lean_continuation_allowed": False,
        "artifacts": {
            "scc_internal_edges": str(out_dir / "scc_internal_edges.jsonl"),
            "scc_affine_edge_maps": str(out_dir / "scc_affine_edge_maps.jsonl"),
            "scc_cycles_checked": str(out_dir / "scc_cycles_checked.jsonl"),
            "scc_cycle_descent_certificates": str(out_dir / "scc_cycle_descent_certificates.jsonl"),
            "scc_cycle_obstructions": str(out_dir / "scc_cycle_obstructions.jsonl"),
            "scc_ranking_certificate": str(out_dir / "scc_ranking_certificate.json"),
            "refined_scc_graph": str(out_dir / "refined_scc_graph.json"),
            "refined_scc_edges": str(out_dir / "refined_scc_edges.jsonl"),
            "refinement_summary": str(out_dir / "refinement_summary.json"),
            "minimal_ranking_obstruction": str(out_dir / "minimal_ranking_obstruction.json"),
            "new_math_required": str(out_dir / "new_math_required.md"),
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_exact_scc_cycle_ranking_certificate(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
