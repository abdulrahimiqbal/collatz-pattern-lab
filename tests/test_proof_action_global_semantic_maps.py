import json
from pathlib import Path

from collatz_lab.proof_action_global_semantic_maps import (
    build_global_semantic_maps,
    replay_global_semantic_maps,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _jsonl(path: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _reasons(replay: dict) -> set[str]:
    return {str(failure.get("reason", "")) for failure in replay["failures"]}


def test_run056b_real_payloads_fail_with_exact_global_gaps() -> None:
    maps, build_failures = build_global_semantic_maps(
        coverage_domain_map=_json("certificate_store/run051_top_level_coverage_domain_map.json"),
        s4_semantic_witnesses=_jsonl("certificate_store/run048_semantic_witnesses.jsonl"),
        s6_proof_trees=_jsonl("certificate_store/run051_s6_proof_trees.jsonl"),
        s3_semantic_roles=_jsonl("certificate_store/run051_s3_semantic_roles.jsonl"),
        kernel_to_path_link=_json("certificate_store/run051_kernel_to_path_link.json"),
    )
    replay = replay_global_semantic_maps(maps)

    assert replay["well_formed"]
    assert not replay["accepted"]
    reasons = _reasons(replay)
    assert "MISSING_PARAMETRIC_ENTRY_COVERAGE" in reasons
    assert "MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM" in reasons
    assert "MISSING_APPLICABLE_EDGE_PARTITION" in reasons
    assert "MISSING_KERNEL_TO_PATH_LINK" in reasons
    assert "MISSING_WELL_FOUNDED_RANK_BRIDGE" in reasons
    assert {failure["reason"] for failure in build_failures} <= reasons


def test_run056b_detects_status_only_map_as_malformed() -> None:
    maps = {
        "entry_map": {
            "schema": "collatz_lab.run056b_global_semantic_map",
            "kind": "ENTRY_TO_CERTIFIED_NODE_MAP",
            "semantic_validation": {"status": "FAIL", "failures": [{"reason": "MISSING_PARAMETRIC_ENTRY_COVERAGE"}]},
            "global_semantic_map_hash": "bad",
        },
        "coverage_map": {},
        "no_escape_map": {},
        "well_founded_bridge": {},
    }

    replay = replay_global_semantic_maps(maps)

    assert not replay["well_formed"]
    assert "status_only_global_semantic_map" in _reasons(replay)
