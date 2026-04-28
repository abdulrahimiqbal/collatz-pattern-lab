import copy
import json
from pathlib import Path

from collatz_lab.proof_action_state import canonical_state
from collatz_lab.proof_action_top_level_cert import (
    attach_top_level_certificates,
    build_replay_context,
    build_top_level_certificates,
    certificate_hash,
    replay_top_level_certificate,
)


ROOT = Path(__file__).resolve().parents[1]


def _run030_graph() -> dict:
    return json.loads((ROOT / "certificate_store/run030_proof_dependency_graph_frozen.json").read_text(encoding="utf-8"))


def _run030_context(graph: dict | None = None) -> dict:
    graph = graph or _run030_graph()
    loadl = lambda path: [json.loads(line) for line in (ROOT / path).read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = json.loads((ROOT / "reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening/proof_manifest.json").read_text(encoding="utf-8"))
    return build_replay_context(
        graph=graph,
        s3_rows=loadl("certificate_store/run030_s3_debt_certificates.jsonl"),
        s4_rows=loadl("certificate_store/run030_parent_transition_certificates.jsonl"),
        s6_rows=loadl("certificate_store/run030_s6_lemma_certificates.jsonl"),
        parent_residual_certificate=json.loads((ROOT / "certificate_store/run030_parent_residual_certificate.json").read_text(encoding="utf-8")),
        manifest_hashes={str(entry["name"]): str(entry["sha256"]) for entry in manifest["artifacts"]},
    )


def _run030_cert(name: str) -> dict:
    rows = [json.loads(line) for line in (ROOT / "certificate_store/run030_top_level_certificates.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return copy.deepcopy(next(row for row in rows if row["certificate_type"] == name))


def _rehash(cert: dict) -> dict:
    cert["certificate_hash"] = certificate_hash(cert)
    return cert


def test_run030_coverage_and_transition_replay_from_manifest_context() -> None:
    graph = _run030_graph()
    context = _run030_context(graph)

    coverage = replay_top_level_certificate(_run030_cert("parent_state_coverage_certificate"), graph=graph, context=context)
    transition = replay_top_level_certificate(_run030_cert("transition_soundness_certificate"), graph=graph, context=context)

    assert coverage.accepted
    assert transition.accepted


def test_run030_ranking_replay_fails_with_exact_scc() -> None:
    graph = _run030_graph()
    replay = replay_top_level_certificate(_run030_cert("well_founded_ranking_certificate"), graph=graph, context=_run030_context(graph))

    assert not replay.accepted
    assert replay.failures
    assert any(failure.get("reason") == "unresolved_scc" for failure in replay.failures)


def test_top_level_status_only_dependency_is_rejected() -> None:
    cert = _run030_cert("transition_soundness_certificate")
    cert["proof_payload"] = {"status": "PASS", "certificate_id": cert["certificate_id"]}
    _rehash(cert)

    replay = replay_top_level_certificate(cert, graph=_run030_graph(), context=_run030_context())

    assert not replay.accepted
    assert replay.status == "REJECT_TOP_LEVEL_CERTIFICATE"
    assert "status-only" in replay.reason


def test_parent_coverage_uncovered_residual_is_rejected() -> None:
    graph = _run030_graph()
    context = _run030_context(graph)
    context["parent_residual_certificate"] = {}

    replay = replay_top_level_certificate(_run030_cert("parent_state_coverage_certificate"), graph=graph, context=context)

    assert not replay.accepted
    assert replay.failures
    assert any("P26" in json.dumps(failure) or failure.get("reason") == "final_P26_residual_parent_class_not_covered" for failure in replay.failures)


def test_transition_soundness_stale_s3_hash_is_rejected() -> None:
    graph = _run030_graph()
    context = _run030_context(graph)
    context["s3_rows"] = copy.deepcopy(context["s3_rows"])
    context["s3_rows"][0]["s3_debt_certificate"]["certificate_hash"] = "stale"

    replay = replay_top_level_certificate(_run030_cert("transition_soundness_certificate"), graph=graph, context=context)

    assert not replay.accepted
    assert any(failure.get("reason") == "lower_layer_replay_failed" for failure in replay.failures or [])


def test_descent_implication_without_induction_payload_is_rejected() -> None:
    cert = _run030_cert("descent_implication_certificate")
    cert["status"] = "PASS"
    cert["replay_status"] = "PASS"
    cert["proof_payload"]["blocked_by"] = []
    cert["proof_payload"]["strong_induction"] = {"base_case": {"n": 1, "reaches_one": True}}
    _rehash(cert)

    replay = replay_top_level_certificate(cert, graph=_run030_graph(), context=_run030_context())

    assert not replay.accepted
    assert any(failure.get("reason") == "strong_induction_payload_incomplete" for failure in replay.failures or [])


def test_ranking_certificate_with_nondecreasing_edge_is_rejected() -> None:
    def node(name: str) -> dict:
        state = canonical_state(
            gate="S6_STRICT_THEOREM_BLOCKER",
            goal="coverage",
            goal_id=f"goal_{name}",
            goal_attrs={"kind": "s6_blocker"},
            facts=[{"kind": "s6_blocker", "target": f"goal_{name}", "certificate_id": f"coverage_{name}", "coverage_certificate": f"coverage_{name}"}],
        )
        action = {"type": "PROVE_RESIDUE_COVERAGE", "target": f"goal_{name}", "modulus": 2, "covered_residue_count": 2, "certificate_id": f"coverage_{name}"}
        return {"node_id": f"coverage:{name}", "node_type": "COVERAGE_CERTIFICATE", "status": "ACCEPTED", "state": state, "accepted_actions": [{"action": action}]}

    graph = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {"coverage:a": node("a"), "coverage:b": node("b")},
        "edges": [{"from": "coverage:a", "to": "coverage:b", "kind": "requires"}],
        "open": [],
    }
    certs, failures = build_top_level_certificates(graph)
    patched = attach_top_level_certificates(graph, certs)
    ranking = copy.deepcopy(next(cert for cert in certs if cert["certificate_type"] == "well_founded_ranking_certificate"))
    ranking["proof_payload"]["ranking"]["edge_checks"][0]["decreases"] = False
    _rehash(ranking)

    replay = replay_top_level_certificate(ranking, graph=patched)

    assert failures == []
    assert not replay.accepted
    assert any(failure.get("reason") == "non_decreasing_edge" for failure in replay.failures or [])


def test_legacy_synthetic_top_level_proof_object_still_replays_locally() -> None:
    state = canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="coverage",
        goal_id="s6_goal",
        goal_attrs={"kind": "s6_blocker"},
        facts=[
            {
                "kind": "s6_blocker",
                "target": "s6_goal",
                "certificate_id": "coverage_cert",
                "coverage_certificate": "coverage_cert",
                "coverage_modulus": 2,
                "covered_residue_count": 2,
            }
        ],
    )
    action = {"type": "PROVE_RESIDUE_COVERAGE", "target": "s6_goal", "modulus": 2, "covered_residue_count": 2, "certificate_id": "coverage_cert"}
    graph = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "coverage:unit": {
                "node_id": "coverage:unit",
                "node_type": "COVERAGE_CERTIFICATE",
                "status": "ACCEPTED",
                "state": state,
                "accepted_actions": [{"action": action}],
            }
        },
        "edges": [],
        "open": [],
    }
    certs, failures = build_top_level_certificates(graph)
    patched = attach_top_level_certificates(graph, certs)

    assert failures == []
    assert all(replay_top_level_certificate(cert, graph=patched).accepted for cert in certs)
