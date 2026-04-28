import json

from collatz_lab.proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from collatz_lab.proof_action_s6_analyzer import analyze_s6_blockers
from collatz_lab.proof_action_s6_lemma_generator import generate_s6_candidate_lemmas


def test_s6_eval_holdout_actions_have_verifier_outcomes(tmp_path):
    analyze_s6_blockers(out=tmp_path, sources=[], min_blockers=10)
    generate_s6_candidate_lemmas(blockers_path=tmp_path / "s6_blockers.jsonl", out=tmp_path / "s6_candidate_lemmas.jsonl", min_lemmas=10)
    row = json.loads((tmp_path / "s6_candidate_lemmas.jsonl").read_text().splitlines()[1])

    actions = legal_action_candidates_from_state(row["state"], max_candidates=32)
    checks = [verify_action_for_state(action, row["state"]) for action in actions]

    assert not any(action["type"] == "VERIFY_S6_LEMMA" for action in actions)
    assert any(check.accepted for check in checks)
    assert row["verify_action"] is None
    assert row["verifier_reason"] == "missing replayable S6 lemma proof payload"
