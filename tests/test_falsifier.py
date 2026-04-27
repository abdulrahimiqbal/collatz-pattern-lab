from collatz_lab.cycle_certificates import sharp_q23_return_map
from collatz_lab.debt import AffineBlock
from collatz_lab.falsifier import falsify_ancestor_descent_claim, falsify_return_map_integrality


def test_falsifier_sharp_return_integrality() -> None:
    report = falsify_return_map_integrality(sharp_q23_return_map(), limit=4)
    assert report["status"] == "NO_COUNTEREXAMPLE_FOUND"


def test_falsifier_finds_unpaid_ancestor_debt() -> None:
    block = AffineBlock(729 * 729, 729 * 665 + 665 * 128, 128 * 1024)
    report = falsify_ancestor_descent_claim(block, q_residue=791, q_depth=11, sample_count=4)
    assert report["status"] == "COUNTEREXAMPLE_FOUND"
