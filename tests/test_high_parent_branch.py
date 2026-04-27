from collatz_lab.high_parent_branch import build_high_parent_branch_report, derive_high_parent_branch
from collatz_lab.parent_states import parent_transition
from collatz_lab.burst import v2_int


def test_derive_high_parent_branch_matches_exact_parent_transition() -> None:
    branch = derive_high_parent_branch(a=1, r_residue=5, r_depth=3)

    assert branch["status"] == "CLOSED_BY_SOURCE_CLASS_AFFINE_DESCENT"
    assert branch["known_target_parent_floor"] == 2
    assert branch["source_class_affine_descent"]["status"] == "PASS"
    assert branch["finite_refinement_conclusion"]["status"] == "FINITE_SOURCE_DEPTH_REFINEMENT_CANNOT_CLOSE_BRANCH_GLOBALLY"

    for k in range(8):
        r = 5 + (1 << 3) * k
        exact = parent_transition(1, r)
        z = 2 + 3 * k
        assert exact["a_next"] == branch["known_target_parent_floor"] + v2_int(z)
        assert exact["r_next"] == z >> v2_int(z)


def test_high_parent_report_marks_open_symbolic_branches() -> None:
    report = build_high_parent_branch_report(
        {
            "status": "VARIABLE_DEPTH_CERTIFICATE_NOT_READY",
            "bad_state_count": 1,
            "bad_states": [
                {
                    "status": "NEEDS_DEEPER_SOURCE_SPLIT",
                    "a": 7,
                    "r_residue": 9512459,
                    "r_depth": 24,
                    "h": 3,
                    "a_next": 24,
                    "required_source_depth": 28,
                }
            ],
        }
    )

    assert report["status"] == "HIGH_PARENT_BRANCHES_OPEN"
    assert report["ready_for_run7"] is False
    assert report["branch_count"] == 1
    assert report["open_branch_count"] == 1
    assert report["closed_branch_count"] == 0
