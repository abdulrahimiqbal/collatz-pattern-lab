import copy
import json
from pathlib import Path

from collatz_lab.proof_action_decode import verify_action_for_state
from collatz_lab.proof_action_s6_lemma_cert import certificate_hash, dependency_hash, replay_s6_lemma_certificate
from collatz_lab.proof_action_state import state_from_debt_transition
from collatz_lab.replay_strict_proof import replay_manifest


ROOT = Path(__file__).resolve().parents[1]


def _run029_graph() -> dict:
    return json.loads((ROOT / "certificate_store/run029_proof_dependency_graph_frozen.json").read_text(encoding="utf-8"))


def _run029_cert() -> dict:
    rows = [
        json.loads(line)
        for line in (ROOT / "certificate_store/run029_s6_lemma_certificates.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return copy.deepcopy(rows[0]["s6_lemma_certificate"])


def _first_s3_dep_id(cert: dict) -> str:
    for dep_id in cert["proof_payload"]["depends_on"]:
        if dep_id.startswith("s3_debt_exact:"):
            return dep_id
    raise AssertionError("RUN-029 fixture has no S3 exact dependency")


def _rehash(cert: dict) -> dict:
    cert["dependency_hashes"] = dict(cert["proof_payload"]["dependency_hashes"])
    cert["certificate_hash"] = certificate_hash(cert)
    return cert


def test_s6_cert_referencing_old_s3_booleans_is_rejected() -> None:
    cert = _run029_cert()
    dep_id = _first_s3_dep_id(cert)
    old_state = state_from_debt_transition(
        {
            "branch_id": "P3:r7:d5",
            "source_state": {"parent_level": 3, "odd_coordinate_residue": 7, "odd_coordinate_modulus": 27},
            "target_state": {"parent_level": 5, "valuation": 1},
            "gain_bound": {"numerator": 1, "denominator": 2},
            "exact_congruence_passed": True,
            "local_descent_passed": True,
        }
    )
    old_payload = {
        "dependency_id": dep_id,
        "kind": "graph_node",
        "node_id": "s3:legacy",
        "node_type": "S3_TRANSITION",
        "state": old_state,
        "action": {
            "type": "CHECK_DEBT_DECREASE",
            "target": "goal_0",
            "branch_id": "P3:r7:d5",
            "gain_num": 1,
            "gain_den": 2,
            "valuation": 1,
        },
    }
    cert["proof_payload"]["dependency_replay_payloads"][dep_id] = old_payload
    cert["proof_payload"]["dependency_hashes"][dep_id] = dependency_hash(old_payload)
    _rehash(cert)

    replay = replay_s6_lemma_certificate(cert)

    assert not replay.accepted
    assert replay.status == "REJECT_S6_LEMMA_DEPENDENCY_FAIL"
    assert replay.failures and replay.failures[0]["reason"] == "graph_node_dependency_not_allowed"


def test_s6_cert_missing_s3_exact_hash_is_rejected() -> None:
    cert = _run029_cert()
    dep_id = _first_s3_dep_id(cert)
    cert["proof_payload"]["dependency_hashes"].pop(dep_id)
    _rehash(cert)

    replay = replay_s6_lemma_certificate(cert)

    assert not replay.accepted
    assert replay.failures and replay.failures[0]["reason"] == "missing_dependency_hash"


def test_s6_cert_with_stale_s3_hash_is_rejected() -> None:
    cert = _run029_cert()
    dep_id = _first_s3_dep_id(cert)
    cert["proof_payload"]["dependency_hashes"][dep_id] = "stale"
    _rehash(cert)

    replay = replay_s6_lemma_certificate(cert)

    assert not replay.accepted
    assert replay.status == "REJECT_S6_LEMMA_HASH_MISMATCH"
    assert replay.failures and replay.failures[0]["reason"] == "dependency_hash_mismatch"


def test_valid_run029_s6_cert_replays_and_verifier_accepts_action() -> None:
    graph = _run029_graph()
    cert = _run029_cert()
    replay = replay_s6_lemma_certificate(cert, graph=graph)
    assert replay.accepted

    node_id = next(
        node_id
        for node_id, node in graph["nodes"].items()
        if node.get("node_type") == "S6_LEMMA" and node.get("evidence", {}).get("s6_lemma_certificate_id") == cert["certificate_id"]
    )
    node = graph["nodes"][node_id]
    action = next(row["action"] for row in node["accepted_actions"] if row["action"]["type"] == "VERIFY_S6_LEMMA")
    check = verify_action_for_state(action, node["state"])

    assert check.accepted
    assert check.reason == "S6 lemma certificate and dependencies replay"


def test_clean_replay_after_run029_has_only_top_level_blockers() -> None:
    replay = replay_manifest(ROOT / "proof_manifest.json")

    assert replay["hash_failure_count"] == 0
    assert replay["strict_verifier"] == "FAIL"
    assert {row["node_type"] for row in replay["root_unsound_certificates"]} == {"STRICT_THEOREM_TOP_LEVEL"}
