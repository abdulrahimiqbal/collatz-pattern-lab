from collatz_lab.proof_action_eval import _closes_or_reduces, _percentile
from collatz_lab.proof_action_outcome import VERIFIER_ACCEPTED_REDUCED


def test_topk_helpers_use_unique_candidate_distribution() -> None:
    assert _percentile([1, 5, 9], 0.5) == 5.0
    assert _percentile([1, 5, 9], 0.9) == 9.0


def test_topk_close_counts_reduced_or_closed_outcomes() -> None:
    assert _closes_or_reduces({"accepted": True, "outcome_class": VERIFIER_ACCEPTED_REDUCED})
    assert _closes_or_reduces({"closed_obligation": True, "outcome_class": "VERIFIER_ACCEPTED_CLOSED_LOCAL"})
    assert not _closes_or_reduces({"accepted": True, "outcome_class": "VERIFIER_ACCEPTED_NO_PROGRESS"})
