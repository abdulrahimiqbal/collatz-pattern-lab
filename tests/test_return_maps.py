from collatz_lab.burst import burst_post_division_value
from collatz_lab.return_maps import (
    compare_return_map_images_to_residual_images,
    derive_parent_return_maps,
    parent_q_prime,
    parent_q_prime_projection_for_map,
    parent_return_residue,
    returns_to_parent,
)


def test_parent_return_residue_samples_return_to_parent() -> None:
    row = parent_return_residue(a=6, h=1)
    modulus = 1 << row["modulus_depth"]
    for i in range(8):
        r = row["r_residue"] + i * modulus
        assert burst_post_division_value(6, r) % 64 == 63
        assert returns_to_parent(6, r)


def test_parent_q_prime_is_integer_for_sampled_condition() -> None:
    row = parent_return_residue(a=7, h=2)
    modulus = 1 << row["modulus_depth"]
    r = row["r_residue"] + modulus
    q_prime = parent_q_prime(7, r)
    assert isinstance(q_prime, int)
    assert q_prime >= 1


def test_derive_parent_return_maps_smoke() -> None:
    maps = derive_parent_return_maps(a_min=6, a_max=7, h_min=1, h_max=3)
    assert len(maps) == 6
    assert all(row["sample_check_passed"] for row in maps)


def test_parent_q_prime_projection_covers_all_depth_four_residues() -> None:
    row = derive_parent_return_maps(a_min=6, a_max=6, h_min=10, h_max=10)[0]
    projection = parent_q_prime_projection_for_map(row, q_depth=20)
    assert projection["q_image_depth"] == 4
    assert projection["covers_all_residues_at_image_depth"] is True
    assert projection["projected_residues"] == list(range(16))


def test_projected_return_maps_match_observed_image_side_classes() -> None:
    row = derive_parent_return_maps(a_min=6, a_max=6, h_min=10, h_max=10)[0]
    residual = {
        "q_depth": 20,
        "inside_parent_images": {
            "all_classes": [
                {"q_image_depth": 4, "q_image_residue": residue}
                for residue in range(16)
            ]
        },
    }
    comparison = compare_return_map_images_to_residual_images([row], residual)
    assert comparison["matched_observed_image_class_count"] == 16
    assert comparison["unmatched_observed_image_class_count"] == 0
