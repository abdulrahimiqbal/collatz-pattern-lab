import copy

from collatz_lab.proof_action_guarded_scc_ranking import (
    build_bounded_guard_exit_certificate,
    replay_scc_guarded_ranking_certificate,
)


def _graph() -> dict:
    return {"node_count": 1, "edge_count": 1}


def test_bounded_repeat_exit_produces_valid_rank() -> None:
    cert = build_bounded_guard_exit_certificate(
        states=["P1"],
        edge_ids=["e1"],
        graph=_graph(),
        cycle_exit_checks=[
            {
                "cycle_id": "c1",
                "classification": "GUARDED_BOUNDED_REPEAT_EXIT",
                "bounded": True,
                "status": "PASS",
            }
        ],
    )

    replay = replay_scc_guarded_ranking_certificate(cert, expected_edge_ids=["e1"])

    assert replay["accepted"]


def test_ranking_certificate_missing_one_guarded_edge_fails() -> None:
    cert = build_bounded_guard_exit_certificate(
        states=["P1"],
        edge_ids=["e1"],
        graph=_graph(),
        cycle_exit_checks=[{"cycle_id": "c1", "classification": "GUARDED_BOUNDED_REPEAT_EXIT", "bounded": True, "status": "PASS"}],
    )

    replay = replay_scc_guarded_ranking_certificate(cert, expected_edge_ids=["e1", "e2"])

    assert not replay["accepted"]
    assert any(failure["reason"] == "guarded_ranking_missing_internal_edges" for failure in replay["failures"])


def test_mutation_of_ranking_cert_hash_fails_replay() -> None:
    cert = build_bounded_guard_exit_certificate(
        states=["P1"],
        edge_ids=["e1"],
        graph=_graph(),
        cycle_exit_checks=[{"cycle_id": "c1", "classification": "GUARDED_BOUNDED_REPEAT_EXIT", "bounded": True, "status": "PASS"}],
    )
    mutated = copy.deepcopy(cert)
    mutated["states"] = ["P2"]

    replay = replay_scc_guarded_ranking_certificate(mutated, expected_edge_ids=["e1"])

    assert not replay["accepted"]
    assert any(failure["reason"] == "guarded_ranking_certificate_hash_mismatch" for failure in replay["failures"])


def test_float_in_ranking_cert_fails_replay() -> None:
    cert = build_bounded_guard_exit_certificate(
        states=["P1"],
        edge_ids=["e1"],
        graph=_graph(),
        cycle_exit_checks=[{"cycle_id": "c1", "classification": "GUARDED_BOUNDED_REPEAT_EXIT", "bounded": True, "status": "PASS"}],
    )
    cert["node_ranks"] = {"n": 1.5}

    replay = replay_scc_guarded_ranking_certificate(cert, expected_edge_ids=["e1"])

    assert not replay["accepted"]
    assert any(failure["reason"] == "floating_point_certificate_rejected" for failure in replay["failures"])

