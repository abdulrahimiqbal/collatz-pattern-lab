"""RUN-068 high-parent root-relative invariant search."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .high_parent_invariant_search import RUN_ID, run_high_parent_invariant_search
from .high_parent_root_relative_graph import (
    build_root_relative_transition_graph,
    load_run067_inputs,
    write_json,
    write_jsonl,
)
from .proof_action_parametric_entry_coverage import REPO_ROOT
from .utils import load_yaml


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run068_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def _accepted_certificate_payload(accepted: list[dict]) -> dict:
    if accepted:
        return {
            "kind": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_CERTIFICATE_BUNDLE",
            "run_id": RUN_ID,
            "status": "PASS",
            "accepted_certificate_count": len(accepted),
            "root_relative_descent_proved": True,
            "certificates": accepted,
            "semantic_validation": {"status": "PASS", "failures": []},
        }
    return {
        "kind": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_CERTIFICATE_BUNDLE",
        "run_id": RUN_ID,
        "status": "FAIL",
        "accepted_certificate_count": 0,
        "root_relative_descent_proved": False,
        "certificates": [],
        "semantic_validation": {
            "status": "FAIL",
            "failures": [
                {
                    "reason": "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING",
                    "detail": "no exact invariant certificate replayed over d >= 1 and q odd positive",
                }
            ],
        },
    }


def run_high_parent_root_relative_invariant_search(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = (
        cfg.get("high_parent_invariant_run068", {})
        if isinstance(cfg.get("high_parent_invariant_run068"), dict)
        else {}
    )
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    schema, families, uncovered = load_run067_inputs(
        schema_path=run_cfg.get(
            "p32_special_transition_schema",
            "certificate_store/run067_p32_special_transition_schema.json",
        ),
        families_path=run_cfg.get(
            "p32_special_transition_families",
            "certificate_store/run067_p32_special_transition_families.jsonl",
        ),
        uncovered_path=run_cfg.get(
            "p32_special_uncovered_domains",
            "certificate_store/run067_p32_special_uncovered_domains.jsonl",
        ),
    )
    graph = build_root_relative_transition_graph(schema=schema, families=families, uncovered_domains=uncovered)
    result = run_high_parent_invariant_search(
        graph=graph,
        max_composition_depth=int(run_cfg.get("max_composition_depth", 4)),
        max_representatives=int(run_cfg.get("max_representative_transitions", 8)),
    )

    graph_out = out_dir / "root_relative_transition_graph.json"
    candidates_out = out_dir / "candidate_invariants.jsonl"
    verifications_out = out_dir / "candidate_invariant_verifications.jsonl"
    accepted_out = out_dir / "accepted_high_parent_invariant_certificate.json"
    remaining_out = out_dir / "remaining_uncovered_high_parent_domains.jsonl"
    remaining_parent_out = out_dir / "remaining_uncovered_parent_families.jsonl"
    obstruction_out = out_dir / "minimal_high_parent_invariant_obstruction.json"
    missing_out = out_dir / "high_parent_missing_invariant.md"
    run_result_out = out_dir / "run_result.json"

    write_json(graph, graph_out)
    write_jsonl(result["candidate_invariants"], candidates_out)
    write_jsonl(result["verifications"], verifications_out)
    accepted_payload = _accepted_certificate_payload(result["accepted_certificates"])
    write_json(accepted_payload, accepted_out)
    write_jsonl(result["remaining_uncovered_domains"], remaining_out)
    write_jsonl(result["remaining_uncovered_parent_families"], remaining_parent_out)
    write_json(result["minimal_obstruction"], obstruction_out)
    if result["run_result"]["status"] == "PASS":
        missing_out.write_text(
            "# RUN-068 High-Parent Root-Relative Invariant\n\nNo high-parent invariant gap remains.\n",
            encoding="utf-8",
        )
    else:
        missing_out.write_text(
            "# RUN-068 High-Parent Root-Relative Invariant\n\n"
            "- `HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING`\n"
            "- `FINITE_SUBSYSTEM_ROOT_MARGIN_MISSING`\n"
            "- `ROOT_DEBT_DECREASE_NOT_PROVED`\n"
            "- `BOUNDED_COMPOSITION_DESCENT_MISSING`\n\n"
            "RUN-068 built an exact graph from the 512 RUN-067 P32 special families and tested debt, "
            "margin, v3, lexicographic, residue, and bounded-composition invariants. No candidate replayed "
            "as a universal certificate over `d >= 1` and odd positive `q`.\n",
            encoding="utf-8",
        )

    store_graph = _copy_to_store("root_relative_transition_graph", graph_out)
    store_candidates = _copy_to_store("candidate_invariants", candidates_out)
    store_verifications = _copy_to_store("candidate_invariant_verifications", verifications_out)
    store_accepted = _copy_to_store("accepted_high_parent_invariant_certificate", accepted_out)
    store_remaining = _copy_to_store("remaining_uncovered_high_parent_domains", remaining_out)
    store_remaining_parent = _copy_to_store("remaining_uncovered_parent_families", remaining_parent_out)
    store_obstruction = _copy_to_store("minimal_high_parent_invariant_obstruction", obstruction_out)

    run_result = dict(result["run_result"])
    run_result["artifacts"] = {
        "root_relative_transition_graph": str(graph_out),
        "candidate_invariants": str(candidates_out),
        "candidate_invariant_verifications": str(verifications_out),
        "accepted_high_parent_invariant_certificate": str(accepted_out),
        "remaining_uncovered_high_parent_domains": str(remaining_out),
        "remaining_uncovered_parent_families": str(remaining_parent_out),
        "minimal_high_parent_invariant_obstruction": str(obstruction_out),
        "high_parent_missing_invariant": str(missing_out),
        "run_result": str(run_result_out),
        "certificate_store_root_relative_transition_graph": str(store_graph),
        "certificate_store_candidate_invariants": str(store_candidates),
        "certificate_store_candidate_invariant_verifications": str(store_verifications),
        "certificate_store_accepted_high_parent_invariant_certificate": str(store_accepted),
        "certificate_store_remaining_uncovered_high_parent_domains": str(store_remaining),
        "certificate_store_remaining_uncovered_parent_families": str(store_remaining_parent),
        "certificate_store_minimal_high_parent_invariant_obstruction": str(store_obstruction),
    }
    write_json(run_result, run_result_out)
    store_result = _copy_to_store("run_result", run_result_out)
    run_result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(run_result, run_result_out)
    shutil.copy2(run_result_out, store_result)
    return run_result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_high_parent_root_relative_invariant_search(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

