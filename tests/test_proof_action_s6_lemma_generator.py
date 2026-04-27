from collatz_lab.proof_action_s6_analyzer import analyze_s6_blockers
from collatz_lab.proof_action_s6_lemma_generator import generate_s6_candidate_lemmas


def test_s6_lemma_generator_emits_accept_and_reject_rows(tmp_path):
    analyze_s6_blockers(out=tmp_path, sources=[], min_blockers=12)
    summary = generate_s6_candidate_lemmas(blockers_path=tmp_path / "s6_blockers.jsonl", out=tmp_path / "s6_candidate_lemmas.jsonl", min_lemmas=10)
    assert summary["candidate_lemma_count"] >= 10
    rows = (tmp_path / "s6_candidate_lemmas.jsonl").read_text().splitlines()
    assert rows
    assert "ACCEPT" in summary["verifier_status_counts"]
    assert "REJECT" in summary["verifier_status_counts"]
