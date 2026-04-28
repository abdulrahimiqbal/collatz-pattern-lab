import json
from pathlib import Path

from collatz_lab.proof_action_scc_invariant_discovery import (
    compose_cycle_domain,
    impose_linear_congruence,
    replay_cycle,
)


ROOT = Path(__file__).resolve().parents[1]
RUN036 = ROOT / "reports/runs/RUN-036-exact-scc-ranking-with-parent-coordinate-maps"


def _run036_maps_by_id() -> dict[str, dict]:
    return {
        row["edge_id"]: row
        for row in (
            json.loads(line)
            for line in (RUN036 / "scc_affine_edge_maps.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def test_linear_congruence_intersection_is_exact() -> None:
    # q == 1 mod 4 and 3*q + 1 == 0 mod 8 has solution q == 5 mod 8.
    assert impose_linear_congruence(residue=1, modulus=4, a=3, b=1, congruence_modulus=8) == (5, 8)
    assert impose_linear_congruence(residue=0, modulus=2, a=2, b=1, congruence_modulus=4) is None


def test_run036_representative_cycle_has_exact_non_descending_domain() -> None:
    maps = _run036_maps_by_id()
    obstruction = json.loads((RUN036 / "scc_cycle_obstructions.jsonl").read_text(encoding="utf-8").splitlines()[0])
    cycle = [maps[edge_id] for edge_id in obstruction["edge_ids"]]

    domain = compose_cycle_domain(cycle)
    replay = replay_cycle(cycle)

    assert domain.accepted
    assert domain.A > domain.D
    assert replay["domain_status"] == "PASS"
    assert replay["classification"] == "NON_DESCENDING"
    assert replay["descent_check"]["status"] == "FAIL"
    assert replay["self_return_mod_cycle_domain"]["status"] == "PASS"
