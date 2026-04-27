from collatz_lab.proof_actions import ProofAction
from collatz_lab.split_executor import execute_split_action, split_cube_by_first_star


def test_split_cube_by_first_star() -> None:
    children = split_cube_by_first_star({"bits": "1*0", "depth": 3, "bit_order": "lsb"})
    assert [child["bits"] for child in children] == ["100", "110"]


def test_execute_parent_level_split() -> None:
    obligation = {
        "obligation_id": "unresolved_bucket:t=0:a=6:h=1",
        "coverage": {"a": 6, "h": 1},
    }
    report = execute_split_action(ProofAction("SPLIT_BY_PARENT_LEVEL", {"a": 6, "h": 1, "r_depth": 7}), obligation)
    assert report["status"] == "REDUCED_BY_PARENT_LEVEL_SPLIT"
    assert report["child_count"] >= 1
    assert any(child["transition_rule"] == "P_6->P_5" for child in report["children"])
