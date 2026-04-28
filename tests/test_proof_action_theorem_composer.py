import html
import json

from collatz_lab.proof_action_dsl import serialize_action
from collatz_lab.proof_action_parent_transition_cert import build_parent_transition_certificate
from collatz_lab.proof_action_s3_debt_cert import build_s3_debt_certificate
from collatz_lab.proof_action_state import canonical_state, state_from_debt_transition
from collatz_lab.proof_action_theorem_composer import (
    build_theorem_dependency_graph,
    compose_theorem_graph,
    minimal_blocker_report,
)


def _transition_certificate() -> dict:
    action = {
        "type": "DERIVE_PARENT_TRANSITION",
        "target": "goal_0",
        "branch_id": "P7:r1:d2",
        "source_parent": 7,
        "target_parent": 9,
        "valuation": 1,
    }
    return build_parent_transition_certificate(action=action, state=_s4_state(include_certificate=False), node_id="s4:unit")


def _s6_lemma_payload() -> dict:
    return {
        "lemma_id": "s6_lemma",
        "statement": "unit S6 lemma",
        "depends_on": ["coverage_cert", "base_case_cert", "lifting_cert", "no_escape_cert"],
        "proof_payload": {
            "coverage": {"certificate_hash": "coverage_hash", "proof": "exact coverage replay"},
            "transition_chain": {"certificate_hash": "transition_hash", "proof": "exact transition replay"},
            "ranking_decrease": {"certificate_hash": "rank_hash", "proof": "strict ranking decrease"},
            "no_escape": {"certificate_hash": "escape_hash", "proof": "no escape replay"},
            "induction_link": {"certificate_hash": "induction_hash", "proof": "well-founded induction replay"},
        },
    }


def _s3_action() -> dict:
    return {
        "type": "CHECK_DEBT_DECREASE",
        "target": "goal_0",
        "branch_id": "P7:r1:d2",
        "gain_num": 1,
        "gain_den": 4,
        "valuation": 2,
    }


def _debt_state(*, include_certificate: bool = True) -> str:
    state = state_from_debt_transition(
        {
            "branch_id": "P7:r1:d2",
            "source_state": {"parent_level": 7, "odd_coordinate_residue": 1, "odd_coordinate_modulus": 8},
            "target_state": {"parent_level": 9, "valuation": 2},
            "gain_bound": {"numerator": 1, "denominator": 4},
            "local_descent_passed": True,
            "exact_congruence_passed": True,
        }
    )
    if not include_certificate:
        return state
    certificate = build_s3_debt_certificate(action=_s3_action(), state=state, node_id="s3:unit")
    payload = json.dumps(certificate, sort_keys=True, separators=(",", ":"))
    attrs = {
        "kind": "s3_debt_certificate",
        "branch_id": certificate["branch_id"],
        "certificate_id": certificate["certificate_id"],
        "certificate_hash": certificate["certificate_hash"],
        "status": certificate["status"],
        "certificate_payload": payload,
    }
    fact = "<FACT " + " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in sorted(attrs.items())) + "/>"
    return state.replace("</FACTS>", f"{fact}\n</FACTS>", 1)


def _s4_state(*, include_certificate: bool = True) -> str:
    fact = {
        "kind": "high_parent_successor",
        "target": "goal_0",
        "branch_id": "P7:r1:d2",
        "source_parent": 7,
        "target_parent": 9,
        "valuation": 1,
        "sample_checks_passed": True,
    }
    if include_certificate:
        fact["transition_certificate"] = json.dumps(_transition_certificate(), sort_keys=True, separators=(",", ":"))
    return canonical_state(
        gate="S4_HIGH_PARENT_SUCCESSOR_FACT",
        goal="derive parent transition",
        goal_attrs={"kind": "high_parent_successor", "branch_id": "P7:r1:d2", "valuation": 1},
        assumptions=["z_family=z(k) = 5 + 2187*k"],
        known_lemmas=["high_parent_successor_exactness"],
        facts=[fact],
    )


def _s6_state() -> str:
    return canonical_state(
        gate="S6_STRICT_THEOREM_BLOCKER",
        goal="close strict blocker",
        goal_id="s6_goal",
        goal_attrs={"kind": "s6_blocker", "blocker_id": "s6_blocker", "blocker_type": "no_escape"},
        known_lemmas=["s6_lemma"],
        facts=[
            {
                "kind": "s6_blocker",
                "target": "s6_goal",
                "blocker_id": "s6_blocker",
                "branch_id": "s6_branch",
                "lemma_id": "s6_lemma",
                "coverage_certificate": "coverage_cert",
                "certificate_id": "coverage_cert",
                "base_case_certificate": "base_case_cert",
                "lifting_certificate": "lifting_cert",
                "no_escape_certificate": "no_escape_cert",
                "coverage_modulus": 8,
                "covered_residue_count": 8,
                "verifier_status": "ACCEPT",
                "lemma_payload": json.dumps(_s6_lemma_payload(), sort_keys=True, separators=(",", ":")),
            }
        ],
        open_obligations=["s6_goal"],
    )


def test_dependency_graph_contains_theorem_node_types(tmp_path) -> None:
    frontier = tmp_path / "frontier"
    s6_dir = tmp_path / "s6"
    frontier.mkdir()
    s6_dir.mkdir()
    s3_action = _s3_action()
    s4_action = {
        "type": "DERIVE_PARENT_TRANSITION",
        "target": "goal_0",
        "branch_id": "P7:r1:d2",
        "source_parent": 7,
        "target_parent": 9,
        "valuation": 1,
        "transition_certificate": _transition_certificate(),
    }
    (frontier / "s3_frontier.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"example_id": "s3_unit", "state": _debt_state(), "candidates": [{"action": serialize_action(s3_action)}]}),
                json.dumps(
                    {
                        "example_id": "s3_rejected_unit",
                        "state": _debt_state(),
                        "candidates": [
                            {
                                "action": serialize_action(
                                    {
                                        "type": "CHECK_DEBT_DECREASE",
                                        "target": "goal_0",
                                        "branch_id": "P7:r1:d2",
                                        "gain_num": 8,
                                        "gain_den": 4,
                                        "valuation": 2,
                                    }
                                )
                            }
                        ],
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (frontier / "s4_lifting_frontier.jsonl").write_text(
        json.dumps({"example_id": "s4_unit", "state": _s4_state(), "candidates": [{"action": serialize_action(s4_action)}]}) + "\n",
        encoding="utf-8",
    )
    blocker = {
        "blocker_id": "s6_blocker",
        "blocker_type": "no_escape",
        "target": "s6_goal",
        "lemma_id": "s6_lemma",
        "coverage_certificate": "coverage_cert",
        "lifting_certificate": "lifting_cert",
        "base_case_certificate": "base_case_cert",
        "no_escape_certificate": "no_escape_cert",
        "state": _s6_state(),
        "candidate_actions": [
            {"type": "VERIFY_S6_LEMMA", "target": "s6_goal", "lemma_id": "s6_lemma", "verifier": "strict_theorem_verifier", "status": "ACCEPT", "lemma": _s6_lemma_payload()},
            {"type": "PROVE_RESIDUE_COVERAGE", "target": "s6_goal", "modulus": 8, "covered_residue_count": 8, "certificate_id": "coverage_cert"},
            {"type": "LIFT_LOCAL_TO_PARAMETRIC_FAMILY", "target": "s6_goal", "local_lemma": "s6_lemma", "family_id": "s6_parametric_family", "lifting_certificate": "lifting_cert"},
            {"type": "CLOSE_WELL_FOUNDED_INDUCTION", "target": "s6_goal", "measure": "n", "descent_lemma": "s6_lemma", "base_case_certificate": "base_case_cert"},
            {"type": "CERTIFY_NO_ESCAPE_BRANCH", "target": "s6_goal", "branch_id": "s6_branch", "certificate_id": "no_escape_cert"},
            {"type": "CLOSE_STRICT_THEOREM_BLOCKER", "target": "s6_goal", "blocker_id": "s6_blocker", "lemma_id": "s6_lemma"},
        ],
    }
    (s6_dir / "s6_blockers.jsonl").write_text(json.dumps(blocker) + "\n", encoding="utf-8")

    graph = build_theorem_dependency_graph(frontier_dir=frontier, s6_dir=s6_dir)

    node_types = {node["node_type"] for node in graph["nodes"].values()}
    assert {"S3_TRANSITION", "S4_LIFT", "S6_LEMMA", "COVERAGE_CERTIFICATE", "INDUCTION_CLOSURE", "NO_ESCAPE_CERTIFICATE", "STRICT_THEOREM_BLOCKER"} <= node_types
    assert "s3:s3_rejected_unit" not in graph["nodes"]


def test_composer_verifier_checks_selector_proposals_before_accepting(monkeypatch) -> None:
    state = _debt_state()
    reject = {"type": "CLOSE_BY_VERIFIER", "target": "goal_0", "verifier": "strict_collatz_descent", "status": "PASS"}
    accept = _s3_action()
    graph = {
        "schema": "collatz_lab.proof_action_theorem_dependency_graph",
        "version": 1,
        "nodes": {
            "s3:test": {
                "node_id": "s3:test",
                "node_type": "S3_TRANSITION",
                "status": "OPEN",
                "depends_on": [],
                "state": state,
                "candidate_actions": [reject, accept],
                "required_action_types": ["CHECK_DEBT_DECREASE"],
                "source": {},
                "evidence": {},
                "accepted_actions": [],
                "rejected_actions": [],
                "tried_action_texts": [],
            }
        },
        "edges": [],
    }

    def fake_scores(model, tokenizer, state, action_texts, *, max_candidate_pair_len):
        return [{"selector_score": 10.0 - index} for index, _ in enumerate(action_texts)]

    monkeypatch.setattr("collatz_lab.proof_action_theorem_composer.score_candidate_selector_components", fake_scores)

    result = compose_theorem_graph(
        graph=graph,
        model=None,
        tokenizer=None,
        max_actions_per_node=2,
        max_iterations=1,
    )

    assert [row["verifier_check"]["status"] for row in result["proposal_trace"][:2]] == ["REJECT_STRICT_VERIFIER", "ACCEPT"]
    assert result["graph"]["nodes"]["s3:test"]["status"] == "ACCEPTED"


def test_minimal_blocker_report_names_missing_dependency() -> None:
    graph = {
        "nodes": {
            "s6_lemma:missing": {"node_type": "S6_LEMMA", "status": "OPEN", "depends_on": [], "required_action_types": ["VERIFY_S6_LEMMA"]},
            "strict_blocker:x": {
                "node_type": "STRICT_THEOREM_BLOCKER",
                "status": "BLOCKED",
                "depends_on": ["s6_lemma:missing"],
                "required_action_types": ["CLOSE_STRICT_THEOREM_BLOCKER"],
            },
        }
    }

    report = minimal_blocker_report(graph, {"minimal_blocking_set": []})

    blocker = next(item for item in report if item["node_id"] == "strict_blocker:x")
    assert blocker["missing_kind"] == "blocked_dependency"
    assert blocker["missing_dependency_types"] == ["S6_LEMMA"]
