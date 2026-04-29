"""RUN-056B global semantic maps entrypoint."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .proof_action_global_semantic_maps import (
    REPO_ROOT,
    RUN_ID,
    build_global_semantic_maps,
    first_status_for_failures,
    read_json,
    read_jsonl,
    replay_global_semantic_maps,
    sha256_file,
    write_json,
)
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run056b_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def _artifact_hashes(paths: dict[str, Path]) -> dict[str, dict[str, str]]:
    return {
        name: {"path": str(path), "sha256": sha256_file(path)}
        for name, path in paths.items()
        if path.exists()
    }


def _missing_gaps_markdown(*, failures: list[dict[str, Any]], maps: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# RUN-056B Missing Global Semantic Map Gaps",
        "",
        "RUN-056B generated the four requested map artifacts, but they do not yet open the Lean reflection gates.",
        "The gaps below are data/theorem gaps, not Python replay failures.",
        "",
        "## Exact Gaps",
    ]
    if not failures:
        lines.append("- none")
    else:
        seen: set[tuple[str, str]] = set()
        for failure in failures:
            item = (str(failure.get("map", "")), str(failure.get("reason", "")))
            if item in seen:
                continue
            seen.add(item)
            detail = str(failure.get("detail", "")).strip()
            suffix = f": {detail}" if detail else ""
            lines.append(f"- `{item[1]}` in `{item[0]}`{suffix}")
    lines.extend(["", "## Gate Status"])
    for name, payload in maps.items():
        validation = payload.get("semantic_validation") if isinstance(payload.get("semantic_validation"), dict) else {}
        reasons = sorted({str(row.get("reason", "")) for row in validation.get("failures", []) if row.get("reason")})
        reason_text = ", ".join(reasons) if reasons else "none"
        lines.append(f"- `{name}`: `{validation.get('status', 'UNKNOWN')}` ({reason_text})")
    lines.extend(
        [
            "",
            "## Required Next Payloads",
            "- `ENTRY_TO_CERTIFIED_NODE_MAP` with a finite reduction or parametric lift for arbitrary `a = v2(n+1)`.",
            "- `COVERAGE_DOMAIN_MEMBERSHIP_MAP` proving arbitrary entry and transition targets are in listed domains.",
            "- `APPLICABLE_EDGE_PARTITION` proving a selected edge and full `SourceDomain` for every covered state.",
            "- `KERNEL_TO_PATH_FORMAL_BRIDGE` connecting infinite internal paths to the eliminated natural kernel.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_global_semantic_maps(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("global_semantic_maps_run056b", {}) if isinstance(cfg.get("global_semantic_maps_run056b"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(run_cfg.get("manifest") or "proof_manifest.json")
    coverage_path = Path(run_cfg.get("coverage_domain_map") or "certificate_store/run051_top_level_coverage_domain_map.json")
    s4_path = Path(run_cfg.get("s4_semantic_witnesses") or "certificate_store/run048_semantic_witnesses.jsonl")
    s6_path = Path(run_cfg.get("s6_proof_trees") or "certificate_store/run051_s6_proof_trees.jsonl")
    s3_path = Path(run_cfg.get("s3_semantic_roles") or "certificate_store/run051_s3_semantic_roles.jsonl")
    kernel_path = Path(run_cfg.get("kernel_to_path_link") or "certificate_store/run051_kernel_to_path_link.json")

    maps, build_failures = build_global_semantic_maps(
        coverage_domain_map=read_json(coverage_path),
        s4_semantic_witnesses=read_jsonl(s4_path),
        s6_proof_trees=read_jsonl(s6_path),
        s3_semantic_roles=read_jsonl(s3_path),
        kernel_to_path_link=read_json(kernel_path),
    )
    replay = replay_global_semantic_maps(maps)
    all_failures = build_failures + replay.get("structural_failures", [])
    formalization_status = first_status_for_failures(all_failures)

    entry_out = out_dir / "entry_map.json"
    coverage_out = out_dir / "coverage_map.json"
    no_escape_out = out_dir / "no_escape_map.json"
    well_founded_out = out_dir / "well_founded_bridge.json"
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_global_semantic_map_gaps.md"
    run_result_out = out_dir / "run_result.json"

    write_json(maps["entry_map"], entry_out)
    write_json(maps["coverage_map"], coverage_out)
    write_json(maps["no_escape_map"], no_escape_out)
    write_json(maps["well_founded_bridge"], well_founded_out)

    store_entry = _copy_to_store("entry_map", entry_out)
    store_coverage = _copy_to_store("coverage_map", coverage_out)
    store_no_escape = _copy_to_store("no_escape_map", no_escape_out)
    store_well_founded = _copy_to_store("well_founded_bridge", well_founded_out)

    status_payload = {
        "schema": "collatz_lab.run056b_formalization_status",
        "version": 1,
        "run_id": RUN_ID,
        "status": formalization_status,
        "training_launched": False,
        "search_launched": False,
        "reflection_gates_reopened": False,
        "run051_descent_declared": False,
        "collatz_conjecture_declared": False,
        "map_statuses": {
            name: (payload.get("semantic_validation") or {}).get("status")
            for name, payload in maps.items()
        },
        "exact_failure_reasons": sorted(
            {str(failure.get("reason", "")) for failure in all_failures if failure.get("reason")}
        ),
    }
    write_json(status_payload, status_out)
    gaps_out.write_text(_missing_gaps_markdown(failures=all_failures, maps=maps), encoding="utf-8")

    source_artifacts = {
        "manifest": manifest_path,
        "run048_semantic_witnesses": s4_path,
        "run051_s3_semantic_roles": s3_path,
        "run051_s6_proof_trees": s6_path,
        "run051_kernel_to_path_link": kernel_path,
        "run051_top_level_coverage_domain_map": coverage_path,
    }
    result = {
        "schema": "collatz_lab.run056b_global_semantic_maps",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if replay.get("accepted") else "FAIL",
        "formalization_status": formalization_status,
        "failure_reason": None if replay.get("accepted") else formalization_status,
        "training_launched": False,
        "search_launched": False,
        "semantic_replay": replay,
        "build_failure_count": len(build_failures),
        "build_failures": build_failures,
        "source_artifacts": _artifact_hashes(source_artifacts),
        "artifacts": {
            "entry_map": str(entry_out),
            "coverage_map": str(coverage_out),
            "no_escape_map": str(no_escape_out),
            "well_founded_bridge": str(well_founded_out),
            "formalization_status": str(status_out),
            "missing_global_semantic_map_gaps": str(gaps_out),
            "run_result": str(run_result_out),
            "certificate_store_entry_map": str(store_entry),
            "certificate_store_coverage_map": str(store_coverage),
            "certificate_store_no_escape_map": str(store_no_escape),
            "certificate_store_well_founded_bridge": str(store_well_founded),
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
    result = run_global_semantic_maps(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
