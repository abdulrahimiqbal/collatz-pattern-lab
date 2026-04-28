import json
from pathlib import Path

from collatz_lab.proof_action_natural_viability_kernel import (
    build_natural_kernel_ranking_certificate,
    build_natural_viability_kernel_certificate,
    replay_natural_kernel_ranking_certificate,
    replay_natural_viability_kernel_certificate,
)
from collatz_lab.proof_action_guarded_domain import load_jsonl


ROOT = Path(__file__).resolve().parents[1]


def _run044_kernel() -> dict:
    return json.loads(
        (ROOT / "reports/runs/RUN-044-guarded-viability-kernel-elimination/guarded_viability_kernel.json").read_text(
            encoding="utf-8"
        )
    )


def _guarded_edge_ids() -> list[str]:
    rows = load_jsonl(ROOT / "reports/runs/RUN-040-guarded-scc-ranking-repair/guarded_edge_domains.jsonl")
    return sorted(str(row["edge_id"]) for row in rows if row.get("status") == "PASS")


def test_natural_viability_certificate_eliminates_non_natural_2adic_kernel() -> None:
    cert = build_natural_viability_kernel_certificate(
        run044_kernel=_run044_kernel(),
        guarded_edge_ids=_guarded_edge_ids(),
    )

    replay = replay_natural_viability_kernel_certificate(cert)

    assert replay["accepted"]
    assert cert["type"] == "SCC_NATURAL_VIABILITY_KERNEL_EMPTY_EXACT"
    assert cert["surviving_kernel_type"] == "NON_NATURAL_2ADIC"
    assert cert["fixed_point"] == {"numerator": -580126354671, "denominator": 141087436042258129}
    assert cert["proof"]["denominator_is_odd"]
    assert cert["proof"]["fixed_point_not_natural"]
    assert cert["proof"]["kernel_congruence_depth_unbounded"]
    assert cert["proof"]["any_natural_q_has_finite_2adic_distance_from_fixed_point"]
    assert cert["proof"]["therefore_no_positive_integer_q_in_kernel"]


def test_natural_viability_certificate_hash_mutation_fails_replay() -> None:
    cert = build_natural_viability_kernel_certificate(
        run044_kernel=_run044_kernel(),
        guarded_edge_ids=_guarded_edge_ids(),
    )
    cert["fixed_point"]["numerator"] = -1

    replay = replay_natural_viability_kernel_certificate(cert)

    assert not replay["accepted"]
    assert any(failure["reason"] == "natural_viability_certificate_hash_mismatch" for failure in replay["failures"])


def test_natural_kernel_ranking_certificate_replays() -> None:
    edge_ids = _guarded_edge_ids()
    cert = build_natural_viability_kernel_certificate(run044_kernel=_run044_kernel(), guarded_edge_ids=edge_ids)
    ranking = build_natural_kernel_ranking_certificate(cert, guarded_edge_ids=edge_ids)

    replay = replay_natural_kernel_ranking_certificate(ranking, expected_edge_ids=edge_ids)

    assert replay["accepted"]
