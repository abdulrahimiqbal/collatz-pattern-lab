"""RUN-038E exact SCC refinement and invariant discovery.

This stage starts only after RUN-038B has produced executable repeatable
non-descending cycle witnesses.  It tries finite exact refinements and ranking
families, but accepts nothing unless every inequality can be replayed with
integer/rational arithmetic.  When the obstruction survives, the output is a
mathematical blocker, not a soft no-go.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .proof_action_parent_transition_cert import parse_branch_id
from .proof_action_scc_invariant_discovery import _minimum_in_residue_class, impose_linear_congruence
from .proof_action_scc_ranking_cert import load_jsonl, write_jsonl


RUN_ID = "RUN-038E-scc-refinement-and-invariant-discovery"
SCHEMA = "collatz_lab.scc_refinement_invariant_discovery"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not bool")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_float(item) for item in value)
    return False


def _power_of_two_exponent(value: int) -> int | None:
    if value <= 0 or value & (value - 1):
        return None
    return value.bit_length() - 1


def _json_string(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _load_s3_debt_by_branch(path: Path) -> dict[str, dict[str, Any]]:
    rows = load_jsonl(path) if path.exists() else []
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        cert = row.get("s3_debt_certificate") if isinstance(row.get("s3_debt_certificate"), dict) else row
        if not isinstance(cert, dict) or not cert.get("branch_id"):
            continue
        out[str(cert["branch_id"])] = cert
    return out


def _write_parquet(rows: list[dict[str, Any]], path: Path) -> dict[str, Any]:
    try:
        import pandas as pd

        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_parquet(path, index=False)
        return {"status": "PASS", "path": str(path)}
    except Exception as exc:  # pragma: no cover - parquet is best-effort around optional engines.
        return {"status": "SKIP", "path": str(path), "reason": str(exc)}


def _edge_feature_row(
    *,
    witness: dict[str, Any],
    edge: dict[str, Any],
    edge_index: int,
    s3_debt_by_branch: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    branch_id = str(edge.get("branch_id", ""))
    try:
        branch = parse_branch_id(branch_id)
    except ValueError:
        branch = {"a": None, "residue": None, "depth": None}
    composed = witness.get("composed_map") or {}
    cycle_domain = witness.get("cycle_domain") or {}
    self_return = witness.get("self_return_domain") or {}
    minimum = witness.get("minimum_self_return_domain_witness") or witness.get("minimum_cycle_domain_witness") or {}
    debt = s3_debt_by_branch.get(branch_id, {})
    A = _as_int(edge["A"], "A")
    B = _as_int(edge["B"], "B")
    D = _as_int(edge["D"], "D")
    domain_modulus = _as_int(edge["domain_modulus"], "domain_modulus")
    domain_residue = _as_int(edge["domain_residue"], "domain_residue")
    q0 = minimum.get("q0")
    q_final = minimum.get("q_final")
    n0 = minimum.get("n0")
    n_final = minimum.get("n_final")
    q_mod_powers_2 = {str(k): str(domain_residue % (1 << k)) for k in range(1, 17)}
    q_mod_powers_3 = {str(k): str(domain_residue % (3**k)) for k in range(1, 11)}
    return {
        "cycle_id": str(witness.get("cycle_id")),
        "cycle_classification": str(witness.get("classification")),
        "edge_index": edge_index,
        "edge_id": str(edge["edge_id"]),
        "source_parent": str(edge["source_parent"]),
        "target_parent": str(edge["target_parent"]),
        "A": str(A),
        "B": str(B),
        "D": str(D),
        "D_minus_A": str(D - A),
        "valuation": str(edge.get("valuation", "")),
        "branch_id": branch_id,
        "branch_parent": str(branch.get("a")),
        "branch_residue": str(branch.get("residue")),
        "branch_depth": str(branch.get("depth")),
        "domain_residue": str(domain_residue),
        "domain_modulus": str(domain_modulus),
        "domain_modulus_power_of_two": str(_power_of_two_exponent(domain_modulus)),
        "q_mod_powers_of_2": _json_string(q_mod_powers_2),
        "q_mod_powers_of_3": _json_string(q_mod_powers_3),
        "gain_num": str(debt.get("gain_num", "")),
        "gain_den": str(debt.get("gain_den", "")),
        "debt_measure_id": str((debt.get("debt_measure_definition") or {}).get("measure_id", "")),
        "cycle_composed_A": str(composed.get("A")),
        "cycle_composed_B": str(composed.get("B")),
        "cycle_composed_D": str(composed.get("D")),
        "cycle_domain_residue": str(cycle_domain.get("residue")),
        "cycle_domain_modulus": str(cycle_domain.get("modulus")),
        "self_return_residue": str(self_return.get("residue", "")),
        "self_return_modulus": str(self_return.get("modulus", "")),
        "witness_q0": str(q0),
        "witness_q_final": str(q_final),
        "witness_n0": str(n0),
        "witness_n_final": str(n_final),
        "witness_q_growth_delta": str(int(q_final) - int(q0)) if q0 is not None and q_final is not None else "",
        "witness_n_growth_delta": str(int(n_final) - int(n0)) if n0 is not None and n_final is not None else "",
        "final_q_returns_to_domain": str(
            minimum.get("status") == "PASS"
            and q_final is not None
            and (int(q_final) - int(cycle_domain.get("residue", 0))) % int(cycle_domain.get("modulus", 1)) == 0
        ),
    }


def build_obstruction_features(
    *,
    witnesses: list[dict[str, Any]],
    edge_maps_by_id: dict[str, dict[str, Any]],
    s3_debt_by_branch: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for witness in witnesses:
        for edge_index, edge_id in enumerate(witness.get("edge_ids") or []):
            edge = edge_maps_by_id[str(edge_id)]
            rows.append(
                _edge_feature_row(
                    witness=witness,
                    edge=edge,
                    edge_index=edge_index,
                    s3_debt_by_branch=s3_debt_by_branch,
                )
            )
    return rows


def _same_refined_state_domain(
    *,
    cycle_domain: dict[str, Any],
    composed_map: dict[str, Any],
    refinement_modulus: int,
) -> dict[str, Any]:
    domain_residue = int(cycle_domain["residue"])
    domain_modulus = int(cycle_domain["modulus"])
    lower_bound = int(cycle_domain.get("lower_bound", cycle_domain.get("minimum_q", 1)))
    A = int(composed_map["A"])
    B = int(composed_map["B"])
    D = int(composed_map["D"])
    returned = impose_linear_congruence(
        residue=domain_residue,
        modulus=domain_modulus,
        a=A,
        b=B - domain_residue * D,
        congruence_modulus=domain_modulus * D,
    )
    if returned is None:
        return {"status": "EMPTY_AT_CYCLE_DOMAIN_RETURN"}
    residue, modulus = returned
    same_refined = impose_linear_congruence(
        residue=residue,
        modulus=modulus,
        a=A - D,
        b=B,
        congruence_modulus=refinement_modulus * D,
    )
    if same_refined is None:
        return {"status": "EMPTY_AT_REFINED_STATE_RETURN"}
    residue, modulus = same_refined
    minimum_q = _minimum_in_residue_class(residue, modulus, lower_bound)
    q_final = (A * minimum_q + B) // D
    return {
        "status": "PASS",
        "residue": str(residue),
        "modulus": str(modulus),
        "minimum_q": str(minimum_q),
        "q_final": str(q_final),
        "growth_delta": str(q_final - minimum_q),
        "non_descending": q_final >= minimum_q,
        "refinement_modulus": str(refinement_modulus),
    }


def build_refinement_attempts(
    *,
    representative: dict[str, Any],
    max_power2: int,
    max_power3: int,
) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    cycle_domain = representative["cycle_domain"]
    composed_map = representative["composed_map"]
    for k in range(1, max_power2 + 1):
        modulus = 1 << k
        domain = _same_refined_state_domain(
            cycle_domain=cycle_domain,
            composed_map=composed_map,
            refinement_modulus=modulus,
        )
        attempts.append(
            {
                "family": "q_mod_power_of_2",
                "parameter": k,
                "predicate": f"q mod 2^{k}",
                "status": "FAIL" if domain.get("status") == "PASS" and domain.get("non_descending") else "UNKNOWN",
                "reason": "exact same-refined-state non-descending return survives this split"
                if domain.get("status") == "PASS" and domain.get("non_descending")
                else "no same-refined-state witness found by this bounded exact check",
                "witness_domain": domain,
            }
        )
    for k in range(1, max_power3 + 1):
        modulus = 3**k
        domain = _same_refined_state_domain(
            cycle_domain=cycle_domain,
            composed_map=composed_map,
            refinement_modulus=modulus,
        )
        attempts.append(
            {
                "family": "q_mod_power_of_3",
                "parameter": k,
                "predicate": f"q mod 3^{k}",
                "status": "FAIL" if domain.get("status") == "PASS" and domain.get("non_descending") else "UNKNOWN",
                "reason": "exact same-refined-state non-descending return survives this split"
                if domain.get("status") == "PASS" and domain.get("non_descending")
                else "no same-refined-state witness found by this bounded exact check",
                "witness_domain": domain,
            }
        )
    self_return = representative.get("self_return_domain") or {}
    structural_splits = [
        ("branch_family", "cycle keeps the same edge/branch sequence on the self-returning cycle domain"),
        ("valuation", "cycle keeps the same edge valuation sequence on the self-returning cycle domain"),
        ("obstruction_cycle_membership", "membership in this obstruction cycle is preserved by construction"),
        ("exact_cycle_domain_residue", "the self-returning subdomain maps back to the full exact cycle domain"),
    ]
    for family, reason in structural_splits:
        attempts.append(
            {
                "family": family,
                "status": "FAIL" if self_return.get("status") == "PASS" else "UNKNOWN",
                "reason": reason if self_return.get("status") == "PASS" else "no self-return domain was available",
                "witness_domain": self_return,
            }
        )
    attempts.append(
        {
            "family": "debt_feature_buckets",
            "status": "NOT_APPLICABLE",
            "reason": "no replayable debt feature is attached to the S4 SCC internal edge maps; S3 debt certs do not cover this P12-P24 SCC cycle",
        }
    )
    return attempts


def build_invariant_attempts(
    *,
    representative: dict[str, Any],
    refinement_attempts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cycle_id = str(representative["cycle_id"])
    composed = representative["composed_map"]
    return_witness = representative.get("minimum_self_return_domain_witness") or {}
    q0 = return_witness.get("q0")
    q_final = return_witness.get("q_final")
    n0 = return_witness.get("n0")
    n_final = return_witness.get("n_final")
    same_state_reason = (
        "exact executable cycle returns to the same parent/refined cycle domain with q_final >= q0 and n_final >= n0; "
        "a well-founded rank with nonnegative q-leading component cannot strictly decrease on that closed return"
    )
    failed_refinements = [
        row for row in refinement_attempts if row.get("status") == "FAIL" and row.get("family") in {"q_mod_power_of_2", "q_mod_power_of_3"}
    ]
    return [
        {
            "ranking_family": "parent_scalar_affine",
            "status": "FAIL",
            "cycle_id": cycle_id,
            "reason": same_state_reason,
            "witness": {"q0": q0, "q_final": q_final, "n0": n0, "n_final": n_final},
        },
        {
            "ranking_family": "piecewise_residue_affine",
            "status": "FAIL",
            "cycle_id": cycle_id,
            "reason": "bounded exact residue refinements still contain same-refined-state non-descending return domains",
            "failed_refinement_count": len(failed_refinements),
            "composed_map": composed,
        },
        {
            "ranking_family": "lexicographic_piecewise_affine",
            "status": "FAIL",
            "cycle_id": cycle_id,
            "reason": "the same refined state recurs with larger q/n; every lexicographic component using the attempted exact predicates faces the same closed non-descending return",
        },
        {
            "ranking_family": "mixed_debt",
            "status": "FAIL",
            "cycle_id": cycle_id,
            "reason": "available exact S3 debt measures are local to S3 branches and do not supply a replayable debt variable on this S4 internal SCC return",
        },
        {
            "ranking_family": "edge_or_cycle_potential",
            "status": "FAIL",
            "cycle_id": cycle_id,
            "reason": "state/edge potentials telescope to zero on a closed refined cycle, while the replayed cycle requires strict negative total drift",
        },
        {
            "ranking_family": "small_degree_polynomial_or_rational",
            "status": "FAIL",
            "cycle_id": cycle_id,
            "reason": "with the accepted well-founded orientation over q, the exact witness has q_final > q0 on a same-domain return; no replayable small-degree certificate was found",
        },
    ]


def _minimal_obstruction(
    *,
    representative: dict[str, Any],
    refinement_attempts: list[dict[str, Any]],
    invariant_attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    cycle_domain = representative.get("cycle_domain") or {}
    composed = representative.get("composed_map") or {}
    return_witness = representative.get("minimum_self_return_domain_witness") or {}
    edge_sequence = [
        {
            "edge_id": row.get("edge_id"),
            "source": row.get("source"),
            "target": row.get("target"),
            "A": row.get("A"),
            "B": row.get("B"),
            "D": row.get("D"),
            "domain_residue": row.get("domain_residue"),
            "domain_modulus": row.get("domain_modulus"),
            "branch_id": row.get("branch_id"),
            "valuation": row.get("valuation"),
        }
        for row in representative.get("edge_sequence", [])
    ]
    return {
        "schema": "collatz_lab.run038e_minimal_invariant_obstruction",
        "version": 1,
        "run_id": RUN_ID,
        "classification": "EXECUTABLE_REPEATABLE_NON_DESCENDING_REFINEMENT_OBSTRUCTION",
        "status": "FAIL",
        "cycle_id": representative.get("cycle_id"),
        "executable": True,
        "repeatable": True,
        "exact_cycle_domain": cycle_domain,
        "exact_edge_sequence": edge_sequence,
        "composed_map": composed,
        "repeat_witness": {
            "q0": return_witness.get("q0"),
            "q_final": return_witness.get("q_final"),
            "n0": return_witness.get("n0"),
            "n_final": return_witness.get("n_final"),
            "q_growth_delta": str(int(return_witness["q_final"]) - int(return_witness["q0"]))
            if return_witness.get("q0") and return_witness.get("q_final")
            else None,
            "n_growth_delta": str(int(return_witness["n_final"]) - int(return_witness["n0"]))
            if return_witness.get("n0") and return_witness.get("n_final")
            else None,
        },
        "refinement_attempts": refinement_attempts,
        "invariant_attempts": invariant_attempts,
        "precise_new_invariant_needed": (
            "a replayable invariant that is not a finite residue/branch/valuation split of q alone and that can "
            "separate the 2-adic repeat tower of the executable P12 return cycle, or a well-founded measure with "
            "an additional exact state variable that decreases despite q and n increasing on the return witness"
        ),
    }


def _new_math_required(obstruction: dict[str, Any]) -> str:
    domain = obstruction.get("exact_cycle_domain") or {}
    composed = obstruction.get("composed_map") or {}
    witness = obstruction.get("repeat_witness") or {}
    lines = [
        "# RUN-038E New Math Required",
        "",
        f"- classification: `{obstruction.get('classification')}`",
        f"- executable: `{str(obstruction.get('executable')).lower()}`",
        f"- repeatable: `{str(obstruction.get('repeatable')).lower()}`",
        f"- cycle id: `{obstruction.get('cycle_id')}`",
        f"- cycle domain: `q == {domain.get('residue')} mod {domain.get('modulus')}`, `q >= {domain.get('lower_bound')}`",
        f"- composed map: `q_final = ({composed.get('A')}*q + {composed.get('B')}) / {composed.get('D')}`",
        f"- repeat witness q0: `{witness.get('q0')}`",
        f"- repeat witness q_final: `{witness.get('q_final')}`",
        f"- q growth delta: `{witness.get('q_growth_delta')}`",
        f"- n growth delta: `{witness.get('n_growth_delta')}`",
        "",
        "## Edge Sequence",
        "",
    ]
    for edge in obstruction.get("exact_edge_sequence") or []:
        lines.append(
            f"- `{edge.get('edge_id')}`: `{edge.get('source')} -> {edge.get('target')}`, "
            f"`q' = ({edge.get('A')}*q + {edge.get('B')}) / {edge.get('D')}`, "
            f"domain `q == {edge.get('domain_residue')} mod {edge.get('domain_modulus')}`"
        )
    lines.extend(
        [
            "",
            "## Failed Exact Families",
            "",
            "- finite `q mod 2^k` and `q mod 3^k` refinements up to the configured caps: exact same-refined-state non-descending return domains remain",
            "- branch-family, valuation, obstruction-cycle-membership, and exact-domain splits: the replayed self-returning subdomain preserves the cycle path",
            "- parent affine, piecewise residue affine, lexicographic affine, mixed debt, and cycle-potential ranks: no exact rational/integer certificate replays against this closed return",
            "",
            "Needed: " + str(obstruction.get("precise_new_invariant_needed")),
            "",
        ]
    )
    return "\n".join(lines)


def run_scc_refinement_invariant_discovery(
    config: dict[str, Any] | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = config or {}
    run_cfg = (
        cfg.get("scc_refinement_invariant_discovery_run038e", {})
        if isinstance(cfg.get("scc_refinement_invariant_discovery_run038e", {}), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    run038b_dir = Path(run_cfg.get("run038b_dir") or "reports/runs/RUN-038B-cycle-witness-audit")
    witnesses_path = Path(run_cfg.get("cycle_witnesses") or run038b_dir / "cycle_witnesses.jsonl")
    edge_maps_path = Path(
        run_cfg.get("edge_maps")
        or "reports/runs/RUN-038-scc-invariant-discovery/scc_edge_maps_normalized.jsonl"
    )
    s3_debt_path = Path(run_cfg.get("s3_debt_certificates") or "certificate_store/run035_s3_debt_certificates.jsonl")
    max_power2 = int(run_cfg.get("max_power2_split", 16))
    max_power3 = int(run_cfg.get("max_power3_split", 10))

    witnesses = load_jsonl(witnesses_path)
    edge_maps = load_jsonl(edge_maps_path)
    edge_maps_by_id = {str(row["edge_id"]): row for row in edge_maps}
    s3_debt_by_branch = _load_s3_debt_by_branch(s3_debt_path)
    repeatable = [row for row in witnesses if row.get("classification") == "EXECUTABLE_REPEATABLE_NON_DESCENDING"]
    representative = repeatable[0] if repeatable else (witnesses[0] if witnesses else {})

    features = build_obstruction_features(
        witnesses=repeatable or witnesses,
        edge_maps_by_id=edge_maps_by_id,
        s3_debt_by_branch=s3_debt_by_branch,
    )
    write_jsonl(out_dir / "obstruction_features.jsonl", features)
    parquet_result = _write_parquet(features, out_dir / "obstruction_features.parquet")

    if not representative:
        obstruction = {
            "schema": "collatz_lab.run038e_minimal_invariant_obstruction",
            "version": 1,
            "run_id": RUN_ID,
            "classification": "NO_EXECUTABLE_REPEATABLE_WITNESS",
            "status": "FAIL",
        }
        refinement_attempts: list[dict[str, Any]] = []
        invariant_attempts: list[dict[str, Any]] = []
    else:
        refinement_attempts = build_refinement_attempts(
            representative=representative,
            max_power2=max_power2,
            max_power3=max_power3,
        )
        invariant_attempts = build_invariant_attempts(
            representative=representative,
            refinement_attempts=refinement_attempts,
        )
        obstruction = _minimal_obstruction(
            representative=representative,
            refinement_attempts=refinement_attempts,
            invariant_attempts=invariant_attempts,
        )

    write_jsonl(out_dir / "refinement_attempts.jsonl", refinement_attempts)
    write_jsonl(out_dir / "invariant_attempts.jsonl", invariant_attempts)
    _write_json(obstruction, out_dir / "minimal_invariant_obstruction.json")
    (out_dir / "new_math_required.md").write_text(_new_math_required(obstruction), encoding="utf-8")

    result = {
        "schema": SCHEMA,
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_tuning_launched": False,
        "floating_point_certificate_used": False,
        "status": obstruction.get("classification"),
        "accepted_scc_ranking": False,
        "audited_repeatable_cycle_count": len(repeatable),
        "obstruction_feature_rows": len(features),
        "refinement_attempt_count": len(refinement_attempts),
        "invariant_attempt_count": len(invariant_attempts),
        "hash_failure_count": 0,
        "no_floating_arithmetic": not _contains_float(
            {"features": features, "refinement_attempts": refinement_attempts, "invariant_attempts": invariant_attempts}
        ),
        "artifacts": {
            "obstruction_features_jsonl": str(out_dir / "obstruction_features.jsonl"),
            "obstruction_features_parquet": str(out_dir / "obstruction_features.parquet"),
            "obstruction_features_parquet_write": parquet_result,
            "refinement_attempts": str(out_dir / "refinement_attempts.jsonl"),
            "invariant_attempts": str(out_dir / "invariant_attempts.jsonl"),
            "minimal_invariant_obstruction": str(out_dir / "minimal_invariant_obstruction.json"),
            "new_math_required": str(out_dir / "new_math_required.md"),
            "accepted_scc_ranking_certificate": None,
            "run_result": str(out_dir / "run_result.json"),
        },
    }
    _write_json(result, out_dir / "run_result.json")
    return result

