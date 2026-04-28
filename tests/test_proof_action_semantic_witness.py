import json
from pathlib import Path

from collatz_lab.proof_action_semantic_witness import (
    build_natural_kernel_semantic_witness,
    build_s3_semantic_witness,
    build_s4_semantic_witness,
    replay_semantic_witnesses,
)


ROOT = Path(__file__).resolve().parents[1]


def _first_jsonl(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").splitlines()[0])


def test_s3_semantic_witness_is_ranking_decrease() -> None:
    row = _first_jsonl(ROOT / "certificate_store/run046_s3_debt_certificates.jsonl")
    witness, failures = build_s3_semantic_witness(row)

    assert not failures
    assert witness["kind"] == "S3_DEBT_SEMANTIC_WITNESS"
    assert witness["semantic_role"] == "RANKING_DECREASE"
    assert witness["decrease_inequality"] == "gain_num < gain_den"
    assert replay_semantic_witnesses([witness])["accepted"]


def test_natural_kernel_semantic_witness_records_positive_distance() -> None:
    cert = json.loads((ROOT / "certificate_store/run045_natural_viability_kernel_certificate.json").read_text(encoding="utf-8"))
    witness, failures = build_natural_kernel_semantic_witness(cert)

    assert not failures
    assert witness["kind"] == "NATURAL_KERNEL_SEMANTIC_WITNESS"
    assert witness["fixed_point_num"] == -580126354671
    assert witness["fixed_point_den"] == 141087436042258129
    assert witness["denominator_positive"]
    assert witness["denominator_odd"]
    assert witness["fixed_point_negative"]


def test_s4_semantic_witness_accepts_stored_parent_coordinate_map() -> None:
    row = _first_jsonl(ROOT / "certificate_store/run046_parent_transition_certificates.jsonl")
    witness, failures = build_s4_semantic_witness(row)

    assert witness["kind"] == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"
    assert not failures
    assert witness["source_parent"] == 23
    assert witness["target_parent"] == 22
    assert witness["valuation"] == 1
    assert witness["base_burst_division_exponent"] == 5
    assert witness["standard_step_count"] == 51
    assert witness["parent_coordinate_map"]["A"] == 94143178827
    assert witness["parent_coordinate_map"]["B"] == 31
    assert witness["parent_coordinate_map"]["D"] == 134217728
    assert witness["replay_checks"]["branch_coordinate_identity"]
    assert replay_semantic_witnesses([witness])["accepted"]


def test_s4_semantic_witness_rejects_simplified_valuation_only_formula() -> None:
    row = _first_jsonl(ROOT / "certificate_store/run046_parent_transition_certificates.jsonl")
    cert = row["transition_certificate"]
    pmap = cert["parent_coordinate_map"]
    pmap["B"] = str((2 ** int(cert["valuation"])) - 1)
    pmap["D"] = str(2 ** (int(cert["valuation"]) + int(cert["target_parent"])))
    pmap["formula"] = f"q_prime = ({pmap['A']}*q + {pmap['B']}) / {pmap['D']}"

    witness, failures = build_s4_semantic_witness(row)

    assert witness["kind"] == "S4_PARENT_TRANSITION_SEMANTIC_WITNESS"
    assert failures
    assert "S4_SIMPLIFIED_VALUATION_ONLY_FORMULA_REJECTED" in {failure["reason"] for failure in failures}
    assert not replay_semantic_witnesses([witness])["accepted"]
