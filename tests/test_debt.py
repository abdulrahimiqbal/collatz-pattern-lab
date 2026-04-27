from collatz_lab.debt import AffineBlock, ancestor_descent_status, classify_certificate_after_expansion, compose_blocks


def test_compose_blocks() -> None:
    first = AffineBlock(3, 1, 2, "first")
    second = AffineBlock(5, 7, 4, "second")
    composed = compose_blocks([first, second])
    assert composed.A == 15
    assert composed.B == 5 * 1 + 7 * 2
    assert composed.D == 8


def test_ancestor_descent_detects_direct_descent() -> None:
    result = ancestor_descent_status(AffineBlock(1, 0, 2), q_residue=1, q_depth=1)
    assert result["status"] == "PROVED_ANCESTOR_DESCENT"
    assert result["debt_paid"] is True


def test_ancestor_debt_unpaid_after_sharp_then_q9() -> None:
    sharp_return = AffineBlock(729, 665, 128, "sharp")
    q9_local = AffineBlock(729, 665, 1024, "q9")
    result = classify_certificate_after_expansion(sharp_return, q9_local, q_residue=791, q_depth=11)
    assert result["local_certificate_status"] == "PROVED_LOCAL_DESCENT"
    assert result["ancestor_certificate_status"] == "DEBT_UNPAID"
    assert result["debt_paid"] is False


def test_strong_local_certificate_pays_debt() -> None:
    sharp_return = AffineBlock(729, 665, 128, "sharp")
    strong = AffineBlock(1, 0, 1024, "strong")
    result = classify_certificate_after_expansion(sharp_return, strong, q_residue=23, q_depth=7)
    assert result["ancestor_certificate_status"] == "PROVED_ANCESTOR_DESCENT"
