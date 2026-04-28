"""RUN-018 exact residual coverage certificate generation.

This pass is symbolic/certifying only: it does not train, launch a big model, or
touch selector weights.  It tries to close the one residual coverage class left
by RUN-017 and, when successful, makes that certificate visible to the theorem
composer's S6 states.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_action_s6_analyzer import _candidate_actions as _s6_candidate_actions
from .proof_action_s6_analyzer import blocker_state
from .proof_action_theorem_composer import run_theorem_composer
from .utils import load_yaml
from .verifier import verify_fixed_residue_descent_exhaustive


DEFAULT_CERTIFICATE_ID = "coverage_cert_0000_residual_67108863_67108864"


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _canonical_hash(data: dict[str, Any]) -> str:
    payload = {key: value for key, value in data.items() if key != "certificate_hash"}
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _localize_path(path: str | Path) -> Path:
    text = str(path)
    if text.startswith("/mnt/collatz/"):
        return Path(text.removeprefix("/mnt/collatz/"))
    return Path(text)


def _try_leaf_certificate(
    *,
    modulus: int,
    residue: int,
    max_steps: int,
    t_limit_multiplier: int,
) -> dict[str, Any] | None:
    max_stable_k = modulus.bit_length() - 1
    for k in range(1, min(max_steps, max_stable_k) + 1):
        result = verify_fixed_residue_descent_exhaustive(
            modulus=modulus,
            residue=residue,
            k=k,
            t_limit=max(modulus * t_limit_multiplier, residue + modulus * t_limit_multiplier),
        )
        if result.status == "PASS":
            return {
                "modulus": modulus,
                "residue": residue % modulus,
                "status": "PASS",
                "k": k,
                "reason": result.reason,
            }
    return None


def _refine_residue(
    *,
    modulus: int,
    residue: int,
    depth: int,
    max_extra_depth: int,
    max_steps: int,
    t_limit_multiplier: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    leaf = _try_leaf_certificate(
        modulus=modulus,
        residue=residue,
        max_steps=max_steps,
        t_limit_multiplier=t_limit_multiplier,
    )
    if leaf is not None:
        return [leaf], []
    if depth >= max_extra_depth:
        return [], [
            {
                "modulus": modulus,
                "residue": residue % modulus,
                "status": "FAIL",
                "max_stable_k": modulus.bit_length() - 1,
                "max_steps": max_steps,
                "reason": "no stable affine descent proof found before max_extra_depth",
            }
        ]

    child_modulus = modulus * 2
    left_certificates, left_failures = _refine_residue(
        modulus=child_modulus,
        residue=residue,
        depth=depth + 1,
        max_extra_depth=max_extra_depth,
        max_steps=max_steps,
        t_limit_multiplier=t_limit_multiplier,
    )
    if left_failures:
        return left_certificates, left_failures
    right_certificates, right_failures = _refine_residue(
        modulus=child_modulus,
        residue=residue + modulus,
        depth=depth + 1,
        max_extra_depth=max_extra_depth,
        max_steps=max_steps,
        t_limit_multiplier=t_limit_multiplier,
    )
    return left_certificates + right_certificates, right_failures


def build_residual_coverage_certificate(
    *,
    obligation: dict[str, Any],
    certificate_id: str = DEFAULT_CERTIFICATE_ID,
    max_extra_depth: int = 16,
    max_steps: int = 220,
    t_limit_multiplier: int = 2,
) -> dict[str, Any]:
    residual = obligation["residual_domain"]
    modulus = int(residual["modulus"])
    residual_start = int(residual["residue_start"])
    residual_end = int(residual["residue_end_exclusive"])
    leaf_certificates: list[dict[str, Any]] = []
    failed_leaves: list[dict[str, Any]] = []
    for residue in range(residual_start, residual_end):
        leaves, failures = _refine_residue(
            modulus=modulus,
            residue=residue,
            depth=0,
            max_extra_depth=max_extra_depth,
            max_steps=max_steps,
            t_limit_multiplier=t_limit_multiplier,
        )
        leaf_certificates.extend(leaves)
        failed_leaves.extend(failures)
        if failed_leaves:
            break

    status = "PASS" if not failed_leaves and len(leaf_certificates) > 0 else "FAIL"
    certificate = {
        "schema": "collatz_lab.proof_action_residual_coverage_certificate",
        "version": 1,
        "certificate_id": certificate_id,
        "parent_certificate_id": str(obligation["coverage_certificate"]),
        "modulus": modulus,
        "residual_start": residual_start,
        "residual_end": residual_end,
        "covered_residue_count": residual_end - residual_start if status == "PASS" else 0,
        "status": status,
        "max_extra_depth": max_extra_depth,
        "max_steps": max_steps,
        "t_limit_multiplier": t_limit_multiplier,
        "leaf_certificate_count": len(leaf_certificates),
        "leaf_certificates": leaf_certificates,
        "failed_leaf_count": len(failed_leaves),
        "failed_leaves": failed_leaves,
    }
    certificate["certificate_hash"] = _canonical_hash(certificate)
    return certificate


def _residual_obligation(run017_dir: str | Path) -> dict[str, Any]:
    rows = _load_jsonl(Path(run017_dir) / "s6_residual_coverage_obligations.jsonl")
    if not rows:
        rows = _load_jsonl(Path(run017_dir) / "root_missing_certificates.jsonl")
    if not rows:
        raise ValueError(f"no residual coverage obligation found under {run017_dir}")
    return rows[0]


def _run017_repaired_s6_dir(run017_dir: str | Path) -> Path:
    result_path = Path(run017_dir) / "run_result.json"
    if result_path.exists():
        result = _load_json(result_path)
        repaired = result.get("repair_summary", {}).get("repaired_s6_dir")
        if repaired:
            localized = _localize_path(repaired)
            if localized.exists():
                return localized
    return Path(run017_dir) / "repaired_s6"


def _residual_action(certificate: dict[str, Any], *, target: str) -> dict[str, Any]:
    return {
        "type": "PROVE_RESIDUAL_COVERAGE",
        "target": target,
        "certificate_id": certificate["certificate_id"],
        "parent_certificate_id": certificate["parent_certificate_id"],
        "modulus": int(certificate["modulus"]),
        "residual_start": int(certificate["residual_start"]),
        "residual_end": int(certificate["residual_end"]),
        "covered_residue_count": int(certificate["covered_residue_count"]),
        "leaf_certificate_count": int(certificate["leaf_certificate_count"]),
        "certificate_hash": certificate["certificate_hash"],
    }


def build_residual_s6_dir(
    *,
    source_s6_dir: str | Path,
    certificate: dict[str, Any],
    out_dir: str | Path,
) -> str:
    source = Path(source_s6_dir)
    blockers = _load_jsonl(source / "s6_blockers.jsonl")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    repaired: list[dict[str, Any]] = []
    for blocker in blockers:
        row = dict(blocker)
        if (
            certificate.get("status") == "PASS"
            and str(blocker.get("coverage_certificate")) == str(certificate["parent_certificate_id"])
        ):
            residual_fact = {
                "kind": "residual_coverage_certificate",
                "certificate_id": certificate["certificate_id"],
                "parent_certificate_id": certificate["parent_certificate_id"],
                "modulus": int(certificate["modulus"]),
                "residual_start": int(certificate["residual_start"]),
                "residual_end": int(certificate["residual_end"]),
                "covered_residue_count": int(certificate["covered_residue_count"]),
                "leaf_certificate_count": int(certificate["leaf_certificate_count"]),
                "certificate_hash": certificate["certificate_hash"],
                "status": "PASS",
            }
            row["residual_coverage_certificate"] = residual_fact
            row["verifier_status"] = "ACCEPT"
            actions = _s6_candidate_actions(row)
            action_texts = {json.dumps(action, sort_keys=True) for action in actions}
            residual = _residual_action(certificate, target=str(row["target"]))
            if json.dumps(residual, sort_keys=True) not in action_texts:
                actions.append(residual)
            row["candidate_actions"] = actions
            row["state"] = blocker_state(row)
        repaired.append(row)
    _write_jsonl(out / "s6_blockers.jsonl", repaired)
    return str(out)


def run_residual_coverage_cert(config_path: str | Path, *, out: str | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path)
    residual_cfg = cfg.get("residual", {})
    run017_dir = Path(str(residual_cfg.get("run017_dir") or "reports/runs/RUN-017-proof-action-v2-s6-lemma-repair"))
    out_dir = Path(str(out or residual_cfg.get("out_dir") or "reports/runs/RUN-018-proof-action-v2-residual-coverage-cert"))
    out_dir.mkdir(parents=True, exist_ok=True)
    obligation = _residual_obligation(run017_dir)
    certificate = build_residual_coverage_certificate(
        obligation=obligation,
        certificate_id=str(residual_cfg.get("certificate_id") or DEFAULT_CERTIFICATE_ID),
        max_extra_depth=int(residual_cfg.get("max_extra_depth", 16)),
        max_steps=int(residual_cfg.get("max_steps", 220)),
        t_limit_multiplier=int(residual_cfg.get("t_limit_multiplier", 2)),
    )
    certificate_path = out_dir / "residual_coverage_certificate.json"
    certificate_path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    source_s6_dir = Path(str(residual_cfg.get("source_s6_dir") or _run017_repaired_s6_dir(run017_dir)))
    repaired_s6_dir = build_residual_s6_dir(
        source_s6_dir=source_s6_dir,
        certificate=certificate,
        out_dir=out_dir / "repaired_s6",
    )
    composer_summary = run_theorem_composer(
        str(residual_cfg.get("composer_config") or "configs/collatz_proof_action_v2_theorem_composer_run016.yaml"),
        checkpoint=str((cfg.get("model") or {}).get("checkpoint") or (cfg.get("evaluation") or {}).get("checkpoint")),
        frontier_dir=str((cfg.get("composer") or {}).get("frontier_eval_dir") or (cfg.get("evaluation") or {}).get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval"),
        s6_dir=repaired_s6_dir,
        out=str(out_dir / "theorem_composer"),
    )

    root_missing: list[dict[str, Any]] = []
    if certificate["status"] != "PASS":
        root_missing.append(
            {
                "kind": "RESIDUAL_COVERAGE_CERTIFICATE",
                "missing_certificate_id": certificate["certificate_id"],
                "parent_certificate_id": certificate["parent_certificate_id"],
                "residual_domain": {
                    "modulus": certificate["modulus"],
                    "residue_start": certificate["residual_start"],
                    "residue_end_exclusive": certificate["residual_end"],
                    "residue_count": certificate["residual_end"] - certificate["residual_start"],
                },
                "failed_leaves": certificate["failed_leaves"],
                "reason": "exact residual coverage generator did not find a stable affine descent certificate within configured bounds",
            }
        )
    elif composer_summary["strict_theorem_verifier_result"] != "PASS":
        for blocker in composer_summary.get("minimal_blocker_report", []):
            if blocker.get("missing_kind") == "blocked_dependency":
                continue
            root_missing.append(
                {
                    "kind": "STRICT_THEOREM_ADDITIONAL_DEPENDENCY",
                    "node_id": blocker.get("node_id"),
                    "node_type": blocker.get("node_type"),
                    "missing_kind": blocker.get("missing_kind"),
                    "last_rejection": blocker.get("last_rejection"),
                    "evidence": blocker.get("evidence", {}),
                }
            )

    _write_jsonl(out_dir / "root_missing_certificates.jsonl", root_missing)
    result = {
        "schema": "collatz_lab.run_result.residual_coverage_cert",
        "version": 1,
        "run_id": "RUN-018-proof-action-v2-residual-coverage-cert",
        "training_launched": False,
        "big_model_launched": False,
        "selector_work": False,
        "residual_certificate_status": certificate["status"],
        "residual_certificate_path": str(certificate_path),
        "repaired_s6_dir": repaired_s6_dir,
        "composer_summary": composer_summary,
        "strict_theorem_verifier_result": composer_summary["strict_theorem_verifier_result"],
        "proof_confidence_percent": composer_summary["proof_confidence_percent"],
        "status": "STRICT_VERIFIER_PASS" if composer_summary["strict_theorem_verifier_result"] == "PASS" else "MINIMAL_ROOT_MISSING_CERTIFICATES",
        "root_missing_certificate_count": len(root_missing),
        "root_missing_certificates": root_missing,
        "artifacts": {
            "residual_coverage_certificate": str(certificate_path),
            "root_missing_certificates": str(out_dir / "root_missing_certificates.jsonl"),
            "theorem_composition_report": str(out_dir / "theorem_composer" / "theorem_composition_report.json"),
        },
    }
    (out_dir / "run_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate RUN-018 residual coverage certificate and rerun theorem composer.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    result = run_residual_coverage_cert(args.config, out=args.out)
    Console().print(
        {
            "status": result["status"],
            "residual_certificate_status": result["residual_certificate_status"],
            "strict_theorem_verifier_result": result["strict_theorem_verifier_result"],
            "root_missing_certificate_count": result["root_missing_certificate_count"],
            "run_result": str(Path(result["residual_certificate_path"]).parent / "run_result.json"),
        }
    )


if __name__ == "__main__":
    main()
