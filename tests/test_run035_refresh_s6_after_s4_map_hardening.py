import copy
import json
from pathlib import Path

from collatz_lab.proof_action_run035 import run_refresh_s6_after_s4_map_hardening
from collatz_lab.proof_action_parent_transition_cert import _certificate_hash as transition_certificate_hash
from collatz_lab.proof_action_s6_lemma_cert import certificate_hash, dependency_hash, replay_s6_lemma_certificate


ROOT = Path(__file__).resolve().parents[1]


def _s4_dependency(certificate: dict) -> tuple[str, dict]:
    return next(
        (dep_id, payload)
        for dep_id, payload in certificate["proof_payload"]["dependency_replay_payloads"].items()
        if payload.get("kind") == "s4_parent_transition_certificate"
    )


def _rehash_s6_after_dependency_mutation(certificate: dict, dep_id: str, dep_payload: dict) -> None:
    certificate["proof_payload"]["dependency_hashes"][dep_id] = dependency_hash(dep_payload)
    certificate["dependency_hashes"] = certificate["proof_payload"]["dependency_hashes"]
    certificate["certificate_hash"] = certificate_hash(certificate)


def test_run035_refreshes_s6_against_map_enriched_s4(tmp_path: Path) -> None:
    cfg = tmp_path / "run035.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "s6_after_s4_map_hardening_run035:",
                f"  out_dir: {out_dir}",
                f"  proof_graph: {ROOT / 'certificate_store/run034_proof_dependency_graph_frozen.json'}",
                f"  accepted_action_trace: {ROOT / 'certificate_store/run034_accepted_action_trace.jsonl'}",
                f"  s3_debt_certificates: {ROOT / 'certificate_store/run034_s3_debt_certificates.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run034_parent_transition_certificates.jsonl'}",
                f"  parent_coordinate_map_certificates: {ROOT / 'certificate_store/run034_parent_coordinate_map_certificates.jsonl'}",
                f"  parent_residual_certificate: {ROOT / 'certificate_store/run034_parent_residual_certificate.json'}",
                f"  top_level_certificates: {ROOT / 'certificate_store/run034_top_level_certificates.jsonl'}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_refresh_s6_after_s4_map_hardening(cfg)
    report = json.loads((out_dir / "s6_lemma_replay_report.json").read_text(encoding="utf-8"))

    assert result["regenerated_s6_lemma_certificates"] == 28
    assert result["s6_replay_pass"] == 28
    assert result["s3_exact_replay_pass"] == 182
    assert result["s4_map_enriched_replay_pass"] == 135
    assert result["hash_failure_count"] == 0
    assert report["all_pass"]


def test_s6_cert_rejects_stale_s4_hash_when_parent_map_required(tmp_path: Path) -> None:
    cfg = tmp_path / "run035.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "s6_after_s4_map_hardening_run035:",
                f"  out_dir: {out_dir}",
                f"  proof_graph: {ROOT / 'certificate_store/run034_proof_dependency_graph_frozen.json'}",
                f"  accepted_action_trace: {ROOT / 'certificate_store/run034_accepted_action_trace.jsonl'}",
                f"  s3_debt_certificates: {ROOT / 'certificate_store/run034_s3_debt_certificates.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run034_parent_transition_certificates.jsonl'}",
                f"  parent_coordinate_map_certificates: {ROOT / 'certificate_store/run034_parent_coordinate_map_certificates.jsonl'}",
                f"  parent_residual_certificate: {ROOT / 'certificate_store/run034_parent_residual_certificate.json'}",
                f"  top_level_certificates: {ROOT / 'certificate_store/run034_top_level_certificates.jsonl'}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )
    run_refresh_s6_after_s4_map_hardening(cfg)
    cert = next(
        json.loads(line)["s6_lemma_certificate"]
        for line in (out_dir / "s6_lemma_certificates.jsonl").read_text(encoding="utf-8").splitlines()
        if "s4_parent_transition_certificate" in line
    )
    mutated = copy.deepcopy(cert)
    dep_id, dep = _s4_dependency(mutated)
    dep["certificate_hash"] = "stale"
    _rehash_s6_after_dependency_mutation(mutated, dep_id, dep)

    replay = replay_s6_lemma_certificate(mutated)

    assert not replay.accepted
    assert replay.status == "REJECT_S6_LEMMA_HASH_MISMATCH"


def test_s6_cert_rejects_missing_parent_coordinate_map_dependency(tmp_path: Path) -> None:
    cfg = tmp_path / "run035.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "s6_after_s4_map_hardening_run035:",
                f"  out_dir: {out_dir}",
                f"  proof_graph: {ROOT / 'certificate_store/run034_proof_dependency_graph_frozen.json'}",
                f"  accepted_action_trace: {ROOT / 'certificate_store/run034_accepted_action_trace.jsonl'}",
                f"  s3_debt_certificates: {ROOT / 'certificate_store/run034_s3_debt_certificates.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run034_parent_transition_certificates.jsonl'}",
                f"  parent_coordinate_map_certificates: {ROOT / 'certificate_store/run034_parent_coordinate_map_certificates.jsonl'}",
                f"  parent_residual_certificate: {ROOT / 'certificate_store/run034_parent_residual_certificate.json'}",
                f"  top_level_certificates: {ROOT / 'certificate_store/run034_top_level_certificates.jsonl'}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )
    run_refresh_s6_after_s4_map_hardening(cfg)
    cert = next(
        json.loads(line)["s6_lemma_certificate"]
        for line in (out_dir / "s6_lemma_certificates.jsonl").read_text(encoding="utf-8").splitlines()
        if "s4_parent_transition_certificate" in line
    )
    mutated = copy.deepcopy(cert)
    dep_id, dep = _s4_dependency(mutated)
    dep["transition_certificate"].pop("parent_coordinate_map", None)
    dep["transition_certificate"].pop("parent_coordinate_map_certificate_id", None)
    dep["transition_certificate"].pop("parent_coordinate_map_certificate_hash", None)
    dep["transition_certificate"].pop("replay_checks", None)
    dep["transition_certificate"]["type"] = "HIGH_PARENT_SUCCESSOR_EXACT"
    dep["transition_certificate"]["certificate_hash"] = transition_certificate_hash(dep["transition_certificate"])
    dep["certificate_hash"] = dep["transition_certificate"]["certificate_hash"]
    _rehash_s6_after_dependency_mutation(mutated, dep_id, dep)

    replay = replay_s6_lemma_certificate(mutated)

    assert not replay.accepted
    assert any("parent-coordinate map" in failure.get("reason", "") for failure in replay.failures or [])


def test_valid_run035_s6_cert_replays(tmp_path: Path) -> None:
    cfg = tmp_path / "run035.yaml"
    out_dir = tmp_path / "out"
    cfg.write_text(
        "\n".join(
            [
                "s6_after_s4_map_hardening_run035:",
                f"  out_dir: {out_dir}",
                f"  proof_graph: {ROOT / 'certificate_store/run034_proof_dependency_graph_frozen.json'}",
                f"  accepted_action_trace: {ROOT / 'certificate_store/run034_accepted_action_trace.jsonl'}",
                f"  s3_debt_certificates: {ROOT / 'certificate_store/run034_s3_debt_certificates.jsonl'}",
                f"  parent_transition_certificates: {ROOT / 'certificate_store/run034_parent_transition_certificates.jsonl'}",
                f"  parent_coordinate_map_certificates: {ROOT / 'certificate_store/run034_parent_coordinate_map_certificates.jsonl'}",
                f"  parent_residual_certificate: {ROOT / 'certificate_store/run034_parent_residual_certificate.json'}",
                f"  top_level_certificates: {ROOT / 'certificate_store/run034_top_level_certificates.jsonl'}",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )
    run_refresh_s6_after_s4_map_hardening(cfg)
    cert = json.loads((out_dir / "s6_lemma_certificates.jsonl").read_text(encoding="utf-8").splitlines()[0])["s6_lemma_certificate"]

    replay = replay_s6_lemma_certificate(cert)

    assert replay.accepted
