from collatz_lab.proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from collatz_lab.proof_action_dsl import serialize_action
from collatz_lab.proof_action_s6_analyzer import analyze_s6_blockers


def test_s6_analyzer_builds_verifier_checkable_obligations(tmp_path):
    report = analyze_s6_blockers(out=tmp_path, sources=[], min_blockers=10)
    assert report["blocker_count"] >= 10
    blockers = (tmp_path / "s6_blockers.jsonl").read_text().splitlines()
    assert blockers

    import json

    blocker = json.loads(blockers[0])
    candidates = legal_action_candidates_from_state(blocker["state"], max_candidates=32)
    assert any(action["type"] == "PROPOSE_S6_LEMMA" for action in candidates)
    assert any(serialize_action(action) for action in candidates)
    accepted = [verify_action_for_state(action, blocker["state"]) for action in candidates]
    assert any(check.accepted for check in accepted)
