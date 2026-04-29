"""RUN-057 parametric entry coverage theorem attempt."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_parametric_entry_coverage import (
    REPO_ROOT,
    RUN_ID,
    build_parent_level_coverage_taxonomy,
    read_json,
    read_jsonl,
    sha256_file,
    write_json,
    write_jsonl,
)
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run057_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def _hashes(paths: dict[str, Path]) -> dict[str, dict[str, str]]:
    return {
        name: {"path": str(path), "sha256": sha256_file(path)}
        for name, path in paths.items()
        if path.exists()
    }


def _gap_markdown(taxonomy: dict[str, Any], uncovered: list[dict[str, Any]]) -> str:
    lines = [
        "# RUN-057 Parametric Entry Coverage",
        "",
        "RUN-057 does not prove universal parametric entry coverage from the current artifacts.",
        "",
        "## Exact Failure",
        "",
        "- `MISSING_PARAMETRIC_ENTRY_COVERAGE`",
        "",
        "## Uncovered Families",
    ]
    for family in uncovered:
        lines.append(
            "- `{family_id}`: range `{level_range}`, q-domain `{q_domain}`; missing `{missing}`".format(
                family_id=family.get("family_id", ""),
                level_range=family.get("parent_level_range", {}),
                q_domain=family.get("q_domain", ""),
                missing=family.get("missing_transition_or_coverage_certificate", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Taxonomy Summary",
            f"- finite parent levels: `{taxonomy.get('finite_parent_levels', [])}`",
            f"- S4 source levels: `{taxonomy.get('s4_source_parent_levels', [])}`",
            f"- S4 target levels: `{taxonomy.get('s4_target_parent_levels', [])}`",
            f"- residual parent levels: `{taxonomy.get('residual_parent_levels', [])}`",
            "",
            "Current proof candidate lacks universal entry coverage and is not a Lean Collatz proof.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_parametric_entry_coverage(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("parametric_entry_coverage_run057", {})
        if isinstance(cfg.get("parametric_entry_coverage_run057"), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    coverage_path = Path(run_cfg.get("coverage_domain_map") or "certificate_store/run051_top_level_coverage_domain_map.json")
    s4_path = Path(run_cfg.get("s4_semantic_witnesses") or "certificate_store/run048_semantic_witnesses.jsonl")
    s3_path = Path(run_cfg.get("s3_semantic_roles") or "certificate_store/run051_s3_semantic_roles.jsonl")
    s6_path = Path(run_cfg.get("s6_proof_trees") or "certificate_store/run051_s6_proof_trees.jsonl")
    top_path = Path(run_cfg.get("top_level_certificates") or "certificate_store/run046_top_level_certificates.jsonl")

    taxonomy, uncovered = build_parent_level_coverage_taxonomy(
        coverage_map=read_json(coverage_path),
        s4_semantic_witnesses=read_jsonl(s4_path),
        s3_semantic_roles=read_jsonl(s3_path),
        s6_proof_trees=read_jsonl(s6_path),
        top_level_rows=read_jsonl(top_path),
    )

    taxonomy_out = out_dir / "parent_level_coverage_taxonomy.json"
    uncovered_out = out_dir / "uncovered_parent_families.jsonl"
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_parametric_entry_coverage.md"
    run_result_out = out_dir / "run_result.json"

    write_json(taxonomy, taxonomy_out)
    write_jsonl(uncovered, uncovered_out)
    gaps_out.write_text(_gap_markdown(taxonomy, uncovered), encoding="utf-8")

    status = "PARAMETRIC_ENTRY_COVERAGE_PROVED" if taxonomy["status"] == "PASS" else "MISSING_PARAMETRIC_ENTRY_COVERAGE"
    status_payload = {
        "schema": "collatz_lab.run057_formalization_status",
        "version": 1,
        "run_id": RUN_ID,
        "status": status,
        "run051_entry_gate_reopened": False,
        "run051_coverage_gate_reopened": False,
        "parametric_entry_coverage_certificate_emitted": taxonomy["status"] == "PASS",
        "run051_descent_declared": False,
        "collatz_conjecture_declared": False,
        "uncovered_family_count": len(uncovered),
    }
    write_json(status_payload, status_out)

    store_taxonomy = _copy_to_store("parent_level_coverage_taxonomy", taxonomy_out)
    store_uncovered = _copy_to_store("uncovered_parent_families", uncovered_out)
    if taxonomy["status"] == "PASS":
        certificate = {
            "schema": "collatz_lab.run057_parametric_entry_coverage_certificate",
            "version": 1,
            "run_id": RUN_ID,
            "taxonomy_hash": taxonomy["taxonomy_hash"],
            "statement": "forall a q, q odd positive -> P_a(q) either descends or enters a certified covered parent-state domain",
        }
        cert_out = out_dir / "parametric_entry_coverage_certificate.json"
        write_json(certificate, cert_out)
        _copy_to_store("parametric_entry_coverage_certificate", cert_out)

    result = {
        "schema": "collatz_lab.run057_parametric_entry_coverage",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if taxonomy["status"] == "PASS" else "FAIL",
        "formalization_status": status,
        "failure_reason": None if taxonomy["status"] == "PASS" else "MISSING_PARAMETRIC_ENTRY_COVERAGE",
        "training_launched": False,
        "search_launched": False,
        "uncovered_family_count": len(uncovered),
        "uncovered_parent_families": uncovered,
        "source_artifacts": _hashes(
            {
                "coverage_domain_map": coverage_path,
                "s4_semantic_witnesses": s4_path,
                "s3_semantic_roles": s3_path,
                "s6_proof_trees": s6_path,
                "top_level_certificates": top_path,
            }
        ),
        "artifacts": {
            "parent_level_coverage_taxonomy": str(taxonomy_out),
            "uncovered_parent_families": str(uncovered_out),
            "formalization_status": str(status_out),
            "missing_parametric_entry_coverage": str(gaps_out),
            "run_result": str(run_result_out),
            "certificate_store_parent_level_coverage_taxonomy": str(store_taxonomy),
            "certificate_store_uncovered_parent_families": str(store_uncovered),
        },
    }
    write_json(result, run_result_out)
    store_result = _copy_to_store("run_result", run_result_out)
    result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(result, run_result_out)
    shutil.copy2(run_result_out, store_result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_parametric_entry_coverage(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
