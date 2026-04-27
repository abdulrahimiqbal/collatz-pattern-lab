"""Search finite-state logarithmic potentials for verified transitions."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from rich.console import Console

from .signature import min_in_residue_class
from .utils import load_jsonl


@dataclass(frozen=True)
class PotentialTransition:
    from_state: str
    to_state: str
    affine_A: int
    affine_B: int
    affine_D: int
    min_n: int
    label: str = ""

    @property
    def log_gain_upper(self) -> float:
        numerator = self.affine_A * self.min_n + self.affine_B
        denominator = self.affine_D * self.min_n
        if numerator <= 0 or denominator <= 0:
            raise ValueError("transition gain must be positive")
        return math.log(numerator / denominator)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "affine_A": self.affine_A,
            "affine_B": self.affine_B,
            "affine_D": self.affine_D,
            "min_n": self.min_n,
            "label": self.label,
            "log_gain_upper": self.log_gain_upper,
        }


@dataclass(frozen=True)
class Transition:
    source_state: str
    target_state: str
    A: int
    B: int
    D: int
    n_min: int | None = None
    n_max: int | None = None
    description: str = ""

    def to_potential_transition(self) -> PotentialTransition:
        if self.n_min is None:
            raise ValueError("n_min is required for numeric potential bounds")
        return PotentialTransition(
            from_state=self.source_state,
            to_state=self.target_state,
            affine_A=self.A,
            affine_B=self.B,
            affine_D=self.D,
            min_n=self.n_min,
            label=self.description,
        )


def bound_log_ratio(transition: Transition) -> float | None:
    """Return a conservative numeric upper bound for ``log(n'/n)``.

    This is a scaffold, not a formal proof. For
    ``n' / n = (A*n+B)/(D*n) = A/D + B/(D*n)``, the ratio is decreasing in
    ``n`` when ``B >= 0`` and increasing when ``B < 0``.
    """

    if transition.n_min is None:
        return None
    if transition.B < 0 and transition.n_max is None:
        return None
    n = transition.n_min if transition.B >= 0 else transition.n_max
    if n is None or n <= 0:
        return None
    numerator = transition.A * n + transition.B
    denominator = transition.D * n
    if numerator <= 0 or denominator <= 0:
        return None
    return math.log(numerator / denominator)


def build_difference_constraints(
    transitions: list[Transition],
    margin: float = 1e-9,
) -> list[dict[str, Any]]:
    constraints = []
    for transition in transitions:
        bound = bound_log_ratio(transition)
        if bound is None:
            constraints.append(
                {
                    "source_state": transition.source_state,
                    "target_state": transition.target_state,
                    "status": "UNKNOWN_BOUND",
                    "description": transition.description,
                }
            )
            continue
        constraints.append(
            {
                "source_state": transition.source_state,
                "target_state": transition.target_state,
                "upper_bound": -bound - margin,
                "log_ratio_bound": bound,
                "status": "BOUND",
                "description": transition.description,
            }
        )
    return constraints


def solve_potential_bellman_ford(
    transitions: list[Transition],
    margin: float = 1e-9,
) -> dict[str, Any]:
    """Solve the numeric potential scaffold with Bellman-Ford constraints."""

    unknown = [transition for transition in transitions if bound_log_ratio(transition) is None]
    known = [transition for transition in transitions if bound_log_ratio(transition) is not None]
    if not known:
        return {
            "found_potential": False,
            "status": "UNKNOWN",
            "reason": "no transitions had finite numeric bounds",
            "unknown_transition_count": len(unknown),
            "claim_status": "NUMERIC_SCAFFOLD_NOT_FORMAL_PROOF",
        }
    result = find_log_potential(
        [transition.to_potential_transition() for transition in known],
        epsilon=margin,
    )
    return {
        "found_potential": result["status"] == "PASS",
        "status": result["status"],
        "claim_status": "NUMERIC_SCAFFOLD_NOT_FORMAL_PROOF",
        "phi_by_state": result.get("phi"),
        "tight_transitions": result.get("tight_transitions"),
        "infeasible_cycle": result.get("negative_cycle_witness"),
        "unknown_transition_count": len(unknown),
        "suggested_state_splits": (
            []
            if result["status"] == "PASS"
            else ["split states participating in infeasible cycles by a/h/parity-run bucket"]
        ),
    }


def _first_present(row: dict[str, Any], names: Iterable[str], default: Any = None) -> Any:
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    return default


def transition_from_row(row: dict[str, Any]) -> PotentialTransition:
    from_state = str(_first_present(row, ["from_state", "state", "source_state"], "all"))
    to_state = str(_first_present(row, ["to_state", "next_state", "target_state"], from_state))
    a = int(_first_present(row, ["affine_A", "standard_affine_A", "A"]))
    b = int(_first_present(row, ["affine_B", "standard_affine_B", "B"]))
    d = int(_first_present(row, ["affine_D", "standard_affine_D", "D"]))
    min_n = _first_present(row, ["min_n", "n_min", "threshold_min_n"])
    if min_n is None:
        modulus = _first_present(row, ["n_modulus", "modulus"])
        residue = _first_present(row, ["n_residue", "residue"])
        if modulus is None or residue is None:
            raise ValueError("transition rows need min_n or residue/modulus")
        min_n = min_in_residue_class(int(modulus), int(residue), min_value=2)
    label = str(_first_present(row, ["label", "signature_id", "standard_affine_signature_id"], ""))
    return PotentialTransition(
        from_state=from_state,
        to_state=to_state,
        affine_A=a,
        affine_B=b,
        affine_D=d,
        min_n=int(min_n),
        label=label,
    )


def load_transition_rows(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if path.suffix == ".jsonl":
        return load_jsonl(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "transitions" in payload:
        transitions = payload["transitions"]
    else:
        transitions = payload
    if not isinstance(transitions, list):
        raise ValueError("Expected a list of transition rows")
    return transitions


def transition_from_scaffold_row(row: dict[str, Any]) -> Transition:
    return Transition(
        source_state=str(_first_present(row, ["source_state", "from_state"], "all")),
        target_state=str(_first_present(row, ["target_state", "to_state"], "all")),
        A=int(_first_present(row, ["A", "affine_A"], 1)),
        B=int(_first_present(row, ["B", "affine_B"], 0)),
        D=int(_first_present(row, ["D", "affine_D"], 1)),
        n_min=(
            None
            if _first_present(row, ["n_min", "min_n"]) is None
            else int(_first_present(row, ["n_min", "min_n"]))
        ),
        n_max=(
            None
            if _first_present(row, ["n_max", "max_n"]) is None
            else int(_first_present(row, ["n_max", "max_n"]))
        ),
        description=str(_first_present(row, ["description", "label"], "")),
    )


def load_scaffold_transitions(path: str | Path) -> list[Transition]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        rows = payload.get("potential_transitions") or payload.get("transitions") or []
    else:
        rows = payload
    transitions: list[Transition] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if {"A", "B", "D"}.issubset(row) or {"affine_A", "affine_B", "affine_D"}.issubset(row):
            transitions.append(transition_from_scaffold_row(row))
    return transitions


def find_log_potential(
    transitions: list[PotentialTransition],
    epsilon: float = 0.0,
) -> dict[str, Any]:
    """Solve difference constraints for ``V(n,s) = log(n) + phi[s]``.

    Each transition contributes
    ``phi[to] - phi[from] <= -epsilon - log_gain_upper``. Bellman-Ford either
    finds feasible correction terms or returns a negative cycle witness.
    """

    states = sorted({transition.from_state for transition in transitions} | {transition.to_state for transition in transitions})
    dist = {state: 0.0 for state in states}
    predecessor: dict[str, tuple[str, PotentialTransition, float]] = {}
    edges: list[tuple[str, str, float, PotentialTransition]] = []
    for transition in transitions:
        c = -epsilon - transition.log_gain_upper
        edges.append((transition.from_state, transition.to_state, c, transition))

    updated_edge: tuple[str, str, float, PotentialTransition] | None = None
    for _ in range(len(states)):
        updated_edge = None
        for source, target, bound, transition in edges:
            candidate = dist[source] + bound
            if dist[target] > candidate + 1e-15:
                dist[target] = candidate
                predecessor[target] = (source, transition, bound)
                updated_edge = (source, target, bound, transition)
        if updated_edge is None:
            break

    if updated_edge is not None:
        cycle_state = updated_edge[1]
        for _ in range(len(states)):
            if cycle_state not in predecessor:
                break
            cycle_state = predecessor[cycle_state][0]
        witness: list[dict[str, Any]] = []
        seen: set[str] = set()
        current = cycle_state
        while current not in seen and current in predecessor:
            seen.add(current)
            source, transition, bound = predecessor[current]
            witness.append(
                {
                    "from_state": source,
                    "to_state": current,
                    "bound": bound,
                    "transition": transition.to_dict(),
                }
            )
            current = source
        return {
            "status": "FAIL",
            "reason": "no log-state potential exists for this state space and epsilon",
            "epsilon": epsilon,
            "states": states,
            "negative_cycle_witness": witness,
        }

    margins = []
    for source, target, bound, transition in edges:
        lhs = dist[target] - dist[source]
        margin = bound - lhs
        margins.append(
            {
                "from_state": source,
                "to_state": target,
                "margin": margin,
                "bound": bound,
                "log_gain_upper": transition.log_gain_upper,
                "label": transition.label,
            }
        )
    margins.sort(key=lambda row: row["margin"])
    return {
        "status": "PASS",
        "reason": "found correction terms for V(n,state)=log(n)+phi[state]",
        "epsilon": epsilon,
        "states": states,
        "phi": dist,
        "tight_transitions": margins[:20],
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search finite-state Collatz log potentials.")
    parser.add_argument("--transitions", default=None, help="JSON/JSONL transition or signature rows.")
    parser.add_argument("--graph", default=None, help="Parent transition graph JSON with potential_transitions.")
    parser.add_argument("--epsilon", type=float, default=0.0)
    parser.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.graph:
        scaffold_transitions = load_scaffold_transitions(args.graph)
        result = solve_potential_bellman_ford(scaffold_transitions, margin=args.epsilon)
    elif args.transitions:
        transitions = [transition_from_row(row) for row in load_transition_rows(args.transitions)]
        raw = find_log_potential(transitions, epsilon=args.epsilon)
        result = {
            **raw,
            "found_potential": raw["status"] == "PASS",
            "claim_status": "NUMERIC_SCAFFOLD_NOT_FORMAL_PROOF",
        }
    else:
        raise ValueError("Provide --transitions or --graph")
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Console().print(result)


if __name__ == "__main__":
    main()
