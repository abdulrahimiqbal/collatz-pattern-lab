from collatz_lab.potential import PotentialTransition, Transition, find_log_potential, solve_potential_bellman_ford


def test_potential_passes_for_contracting_self_loop() -> None:
    transition = PotentialTransition(
        from_state="s",
        to_state="s",
        affine_A=1,
        affine_B=0,
        affine_D=2,
        min_n=2,
    )
    result = find_log_potential([transition], epsilon=0.0)
    assert result["status"] == "PASS"


def test_potential_fails_for_expanding_self_loop() -> None:
    transition = PotentialTransition(
        from_state="s",
        to_state="s",
        affine_A=2,
        affine_B=0,
        affine_D=1,
        min_n=2,
    )
    result = find_log_potential([transition], epsilon=0.0)
    assert result["status"] == "FAIL"


def test_scaffold_potential_passes_for_acyclic_decreasing_graph() -> None:
    transitions = [
        Transition("a", "b", A=1, B=0, D=2, n_min=2, description="halve"),
        Transition("b", "c", A=1, B=0, D=2, n_min=2, description="halve"),
    ]
    result = solve_potential_bellman_ford(transitions)
    assert result["found_potential"] is True


def test_scaffold_potential_fails_for_contradictory_cycle() -> None:
    transitions = [
        Transition("a", "a", A=2, B=0, D=1, n_min=2, description="double"),
    ]
    result = solve_potential_bellman_ford(transitions)
    assert result["found_potential"] is False
