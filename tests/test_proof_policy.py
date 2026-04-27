from collatz_lab.proof_policy import featurize_obligation, open_obligations, propose_actions


def test_featurize_unresolved_bucket() -> None:
    obligation = {
        "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
        "scc_status": "NEEDS_SPLIT",
        "coverage": {"count_unknown": 10, "unknown_percent": 50.0},
    }
    features = featurize_obligation(obligation)
    assert features["kind"] == "unresolved_bucket"
    assert features["is_sharp_return_candidate"] is True
    actions = propose_actions(obligation, beam_size=4)
    assert actions[0].action == "PROMOTE_TO_PARENT_STATE"
    assert any(row.action == "TRY_ADIC_BASIN" for row in actions)


def test_open_obligations_filters_closed() -> None:
    report = {
        "obligations": [
            {"obligation_id": "closed", "scc_status": "CLOSED_BY_ANCESTOR_DESCENT"},
            {"obligation_id": "open", "scc_status": "NEEDS_SPLIT"},
            {"obligation_id": "status-open", "status": "UNKNOWN"},
        ]
    }
    rows = open_obligations(report)
    assert [row["obligation_id"] for row in rows] == ["open", "status-open"]


def test_cube_lift_policy_prefers_split() -> None:
    obligation = {
        "obligation_id": "cube_lift:unknown:NEEDS_SPLIT",
        "scc_status": "NEEDS_SPLIT",
        "coverage": {"cube_count": 228},
    }
    actions = propose_actions(obligation, beam_size=2)
    assert actions[0].action == "SPLIT_BY_RESIDUE"
    assert actions[1].action == "SPLIT_BY_H"


def test_parent_template_policy_targets_generalization() -> None:
    obligation = {
        "obligation_id": "parent_state_transition_templates",
        "status": "UNKNOWN",
        "coverage": {"a_min": 1, "a_max": 20, "r_depth": 7},
    }
    features = featurize_obligation(obligation)
    assert features["kind"] == "parent_state_templates"
    actions = propose_actions(obligation, beam_size=2)
    assert actions[0].action == "GENERALIZE_IN_A"


def test_parent_transition_bucket_policy_targets_exact_template() -> None:
    obligation = {
        "obligation_id": "P6:h=1:to=P5:rdepth=7",
        "scc_status": "NEEDS_SPLIT",
        "coverage": {"residue_count": 1},
    }
    features = featurize_obligation(obligation)
    assert features["kind"] == "parent_transition_bucket"
    actions = propose_actions(obligation, beam_size=2)
    assert actions[0].action == "TRY_PARENT_TRANSITION_TEMPLATE"
