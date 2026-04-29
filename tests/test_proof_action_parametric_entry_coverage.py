import json
from pathlib import Path

from collatz_lab.proof_action_parametric_entry_coverage import build_parent_level_coverage_taxonomy
from collatz_lab.proof_action_run057 import run_parametric_entry_coverage


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _jsonl(path: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_run057_taxonomy_finds_uncovered_entry_families() -> None:
    taxonomy, uncovered = build_parent_level_coverage_taxonomy(
        coverage_map=_json("certificate_store/run051_top_level_coverage_domain_map.json"),
        s4_semantic_witnesses=_jsonl("certificate_store/run048_semantic_witnesses.jsonl"),
        s3_semantic_roles=_jsonl("certificate_store/run051_s3_semantic_roles.jsonl"),
        s6_proof_trees=_jsonl("certificate_store/run051_s6_proof_trees.jsonl"),
        top_level_rows=_jsonl("certificate_store/run046_top_level_certificates.jsonl"),
    )

    assert taxonomy["status"] == "FAIL"
    assert taxonomy["failure_reason"] == "MISSING_PARAMETRIC_ENTRY_COVERAGE"
    assert taxonomy["finite_parent_levels"][0] == 2
    assert taxonomy["finite_parent_levels"][-1] == 32
    assert {row["family_id"] for row in uncovered} == {
        "odd_entry_parent_level_1",
        "odd_entry_parent_levels_ge_33",
    }


def test_run057_runner_writes_failure_reports(tmp_path: Path) -> None:
    cfg = tmp_path / "run057.yaml"
    out_dir = tmp_path / "run057"
    cfg.write_text(
        "\n".join(
            [
                "parametric_entry_coverage_run057:",
                f"  out_dir: {out_dir}",
                "  coverage_domain_map: certificate_store/run051_top_level_coverage_domain_map.json",
                "  s4_semantic_witnesses: certificate_store/run048_semantic_witnesses.jsonl",
                "  s3_semantic_roles: certificate_store/run051_s3_semantic_roles.jsonl",
                "  s6_proof_trees: certificate_store/run051_s6_proof_trees.jsonl",
                "  top_level_certificates: certificate_store/run046_top_level_certificates.jsonl",
            ]
        ),
        encoding="utf-8",
    )

    result = run_parametric_entry_coverage(cfg)

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "MISSING_PARAMETRIC_ENTRY_COVERAGE"
    assert result["uncovered_family_count"] == 2
    assert (out_dir / "parent_level_coverage_taxonomy.json").exists()
    assert (out_dir / "uncovered_parent_families.jsonl").exists()
    assert not (out_dir / "parametric_entry_coverage_certificate.json").exists()
