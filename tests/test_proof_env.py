from collatz_lab.proof_actions import ProofAction
from collatz_lab.proof_env import execute_action, run_policy_on_report


def test_execute_adic_basin_reduces_aggregate_bucket() -> None:
    obligation = {
        "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
        "scc_status": "NEEDS_SPLIT",
        "coverage": {"a": 6, "h": 1, "t": 0},
    }
    result = execute_action(
        ProofAction("TRY_ADIC_BASIN", {"form": {"u": 601, "v": 1}}),
        obligation,
    )
    assert result.status == "REDUCED"
    assert result.proof_status == "REDUCED_BY_HEIGHT_RANKED_SUBBRANCH"
    assert result.details["basin_status"] == "PROVED_NO_INFINITE_REPEAT"


def test_execute_adic_basin_closes_specific_sharp_obligation() -> None:
    obligation = {
        "obligation_id": "adic_basin:sharp_q23_R23",
        "scc_status": "NEEDS_SPLIT",
        "coverage": {},
    }
    result = execute_action(ProofAction("TRY_ADIC_BASIN"), obligation)
    assert result.status == "CLOSED"
    assert result.proof_status == "CLOSED_BY_HEIGHT_RANKING"


def test_run_policy_on_synthetic_report() -> None:
    report = {
        "obligation_count": 2,
        "open_obligation_count": 1,
        "obligations": [
            {
                "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
                "scc_status": "NEEDS_SPLIT",
                "coverage": {"a": 6, "h": 1, "t": 0},
            }
        ],
    }
    policy_report, traces = run_policy_on_report(report, beam_size=3)
    assert policy_report["actions_tried"] == 3
    assert traces
    assert policy_report["result_counts"]["REDUCED"] >= 1


def test_execute_generalize_in_a_is_exact_scaffold() -> None:
    result = execute_action(
        ProofAction("GENERALIZE_IN_A", {"depth": 4, "a_min": 1, "a_max": 16}),
        {"obligation_id": "global", "scc_status": "NEEDS_SPLIT", "coverage": {}},
    )
    assert result.status == "REDUCED"
    assert result.proof_status == "REDUCED_BY_PARAMETRIC_A_PERIODICITY"
    assert result.details["parametric_a"]["sample_period_check_passed"]


def test_execute_parent_transition_template_reduces_bucket() -> None:
    result = execute_action(
        ProofAction("TRY_PARENT_TRANSITION_TEMPLATE", {"a": 6, "h": 1, "a_next": 5, "r_depth": 7}),
        {
            "obligation_id": "P6:h=1:to=P5:rdepth=7",
            "scc_status": "NEEDS_SPLIT",
            "coverage": {"residue_count": 1},
        },
    )
    assert result.status == "REDUCED"
    assert result.proof_status == "REDUCED_BY_PARENT_TRANSITION_TEMPLATE"
    assert result.details["verified_residue_count"] == 1
