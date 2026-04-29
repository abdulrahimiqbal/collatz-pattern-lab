from collatz_lab.high_parent_candidate_rules import generate_candidate_rules
from collatz_lab.high_parent_certificate_verifier import verify_high_parent_candidate


def test_candidate_rules_include_all_expected_rule_types() -> None:
    rules = generate_candidate_rules(
        feature_rows=[{"d": 1, "q": 1, "descent_found_within_max_steps": False}],
        margin_report={"available_certificate_inventory": {"candidate_root_relative_margin_count": 0}},
        p32_outgoing_count=0,
    )

    assert {rule["rule_type"] for rule in rules} == {
        "DIRECT_ROOT_DESCENT",
        "ROOT_DEBT_DECREASE",
        "LOWER_DEBT_ENTRY",
        "CERTIFIED_MARGIN_DESCENT",
        "RESIDUE_SPLIT_FAMILY",
    }
    assert all(rule["candidate_rule_hash"] for rule in rules)


def test_verifier_rejects_false_or_descriptive_candidates() -> None:
    rules = generate_candidate_rules(
        feature_rows=[{"d": 1, "q": 1, "descent_found_within_max_steps": True, "first_descent_below_root": 42}],
        margin_report={"available_certificate_inventory": {"passing_root_relative_margin_count": 0}},
        p32_outgoing_count=0,
    )
    reasons = {verify_high_parent_candidate(rule)["reason"] for rule in rules}

    assert "DIRECT_ROOT_DESCENT_INEQUALITY_FALSE" in reasons
    assert "P32_OUTGOING_ITERATE_FAMILY_MISSING" in reasons
    assert "LOWER_DEBT_ENTRY_CERTIFICATE_MISSING" in reasons
    assert "P32_ROOT_RELATIVE_MARGIN_CERTIFICATE_MISSING" in reasons
    assert "SAMPLE_ONLY_RULE_REJECTED" in reasons


def test_verifier_accepts_explicit_margin_certificate_candidate() -> None:
    rules = generate_candidate_rules(
        feature_rows=[],
        margin_report={"available_certificate_inventory": {"candidate_root_relative_margin_count": 1, "passing_root_relative_margin_count": 1}},
        p32_outgoing_count=0,
    )
    margin = next(rule for rule in rules if rule["rule_type"] == "CERTIFIED_MARGIN_DESCENT")
    verification = verify_high_parent_candidate(margin)

    assert verification["status"] == "ACCEPT"
    assert verification["reason"] == "CERTIFIED_MARGIN_DESCENT_VERIFIED"
