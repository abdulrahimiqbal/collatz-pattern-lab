from collatz_lab.proof_action_run067 import run_p32_special_transition_derivation
from collatz_lab.proof_scope_status import read_jsonl


def test_run067_derives_families_and_fails_closed(tmp_path) -> None:
    cfg = tmp_path / "run067.yaml"
    out = tmp_path / "run067"
    cfg.write_text(
        "\n".join(
            [
                "p32_special_transition_run067:",
                f"  out_dir: {out}",
                "  h_max: 3",
                "  b_max: 3",
                "  max_families: 20",
            ]
        ),
        encoding="utf-8",
    )
    result = run_p32_special_transition_derivation(cfg)
    families = read_jsonl(out / "p32_special_transition_families.jsonl")
    uncovered = read_jsonl(out / "p32_special_uncovered_domains.jsonl")

    assert result["status"] == "FAIL"
    assert result["formalization_status"] == "HIGH_PARENT_ROOT_RELATIVE_INVARIANT_MISSING"
    assert result["family_count"] == len(families)
    assert families
    assert uncovered
    assert result["training_launched"] is False
    assert result["ml_launched"] is False
