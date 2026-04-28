import json

from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_s6_analyzer import _candidate_actions, blocker_state
from collatz_lab.proof_action_s6_lemma_repair import (
    atomic_sublemma_checks,
    classify_s6_lemma_rejection,
    repair_s6_blockers,
    residual_coverage_obligation,
)


def _lemma_payload(row: dict) -> dict:
    return {
        "lemma_id": row["lemma_id"],
        "statement": row["statement"],
        "depends_on": [
            row["coverage_certificate"],
            row["base_case_certificate"],
            row["lifting_certificate"],
            row["no_escape_certificate"],
        ],
        "proof_payload": {
            "coverage": {"certificate_hash": "coverage_hash", "proof": "exact coverage replay"},
            "transition_chain": {"certificate_hash": "transition_hash", "proof": "exact transition replay"},
            "ranking_decrease": {"certificate_hash": "rank_hash", "proof": "ranking replay"},
            "no_escape": {"certificate_hash": "escape_hash", "proof": "no escape replay"},
            "induction_link": {"certificate_hash": "induction_hash", "proof": "induction replay"},
        },
    }


def _blocker(*, blocker_type: str = "induction", covered: int = 8, status: str = "REJECT") -> dict:
    row = {
        "blocker_id": f"s6_{blocker_type}_unit_0000",
        "blocker_type": blocker_type,
        "gate": "S6",
        "target": f"s6_goal_{blocker_type}",
        "statement": f"repair {blocker_type}",
        "required_prior_gates": ["S3", "S4"],
        "branch_id": "s6_branch_unit",
        "lemma_id": f"s6_{blocker_type}_lemma_unit",
        "coverage_modulus": 8,
        "covered_residue_count": covered,
        "coverage_certificate": f"coverage_cert_{blocker_type}",
        "base_case_certificate": f"base_case_cert_{blocker_type}",
        "lifting_certificate": f"lifting_cert_{blocker_type}",
        "no_escape_certificate": f"no_escape_cert_{blocker_type}",
        "verifier": "strict_theorem_verifier",
        "verifier_status": status,
        "status": "OPEN",
    }
    if status == "ACCEPT":
        row["lemma_payload"] = _lemma_payload(row)
    row["candidate_actions"] = _candidate_actions(row)
    row["state"] = blocker_state(row)
    return row


def test_verify_s6_lemma_rejects_repaired_status_payload_without_run023_cert() -> None:
    blocker = _blocker(status="ACCEPT")
    verify_action = next(action for action in blocker["candidate_actions"] if action["type"] == "VERIFY_S6_LEMMA")

    check = verify_action_for_state(verify_action, blocker["state"])

    assert not check.accepted
    assert check.status == "REJECT_MISSING_S6_LEMMA_CERTIFICATE"


def test_partial_coverage_classification_and_residual() -> None:
    blocker = _blocker(blocker_type="coverage", covered=7)
    report = {"last_rejection": {"status": "REJECT_INCOMPLETE_COVERAGE", "reason": "coverage certificate is partial"}}

    assert classify_s6_lemma_rejection(report, blocker) == "partial_coverage"
    residual = residual_coverage_obligation(blocker)
    assert residual is not None
    assert residual["residual_domain"]["residue_start"] == 7
    assert residual["residual_domain"]["residue_end_exclusive"] == 8
    assert residual["missing_certificate_id"] == "coverage_cert_coverage:residual:7:8"


def test_atomic_sublemma_repair_accepts_explicit_rejection_atoms(tmp_path) -> None:
    blocker = _blocker(blocker_type="parametric_lift", status="REJECT")
    run016_report = {
        "minimal_blocker_report": [
            {
                "node_id": f"s6_lemma:{blocker['lemma_id']}",
                "node_type": "S6_LEMMA",
                "status": "OPEN",
                "evidence": {"lemma_id": blocker["lemma_id"]},
                "last_rejection": {"status": "REJECT_S6_LEMMA", "reason": "S6 lemma verifier did not accept this lemma"},
            }
        ]
    }
    s6_dir = tmp_path / "s6"
    s6_dir.mkdir()
    (s6_dir / "s6_blockers.jsonl").write_text(json.dumps(blocker) + "\n", encoding="utf-8")
    report_path = tmp_path / "run016.json"
    report_path.write_text(json.dumps(run016_report), encoding="utf-8")

    atoms = atomic_sublemma_checks(blocker)
    assert atoms
    assert all(atom["accepted"] for atom in atoms)

    summary = repair_s6_blockers(run016_report_path=report_path, s6_dir=s6_dir, out_dir=tmp_path / "out")
    repaired = json.loads((tmp_path / "out" / "repaired_s6" / "s6_blockers.jsonl").read_text(encoding="utf-8"))

    assert summary["classification_counts"] == {"explicit_lemma_rejection": 1}
    assert summary["repaired_lemma_count"] == 1
    assert repaired["verifier_status"] == "ACCEPT"
