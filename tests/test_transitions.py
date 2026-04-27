from collatz_lab.transitions import (
    affine_image_residue,
    build_transition_graph,
    parse_affine_signature_id,
)


def test_parse_affine_signature_id() -> None:
    assert parse_affine_signature_id("standard:A=9:B=5:D=16") == (9, 5, 16)


def test_affine_image_residue_reduces_modulus_by_denominator_power() -> None:
    image_residue, image_power = affine_image_residue(
        n_residue=7524799,
        n_mod_power=24,
        affine_a=19683,
        affine_b=20387,
        affine_d=32768,
    )
    assert image_power == 9
    assert 0 <= image_residue < 2**9


def test_transition_graph_builds_pass_fragment_for_validated_cube() -> None:
    report = {
        "q_bit_cube_validation": [
            {
                "status": "PASS",
                "cube": {
                    "depth": 18,
                    "mask": (1 << 18) - 1,
                    "value": 117575,
                    "label": {
                        "k": 24,
                        "standard_affine_signature_id": "standard:A=19683:B=20387:D=32768",
                    },
                    "support": 1,
                    "known_matches": 1,
                    "fixed_bits": 18,
                    "free_bits": 0,
                    "completions": 1,
                    "density_within_q_depth": 2.0**-18,
                    "bit_pattern_lsb_first": "111010110101110001",
                    "fixed_bit_conditions": [],
                },
            }
        ]
    }

    candidate = build_transition_graph(report, burst_length=6)

    assert candidate["verifier_status"] == "PASS_FRAGMENT"
    assert candidate["state_count"] == 1
    assert candidate["expanded_certificate_count"] == 1
    assert candidate["potential"]["status"] == "PASS"
