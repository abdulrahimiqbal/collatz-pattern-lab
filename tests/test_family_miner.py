from collatz_lab.family_miner import mine_families_from_signatures, mine_q_bit_cubes, validate_q_bit_cube
from collatz_lab.signature import signature_for_rule


def test_family_miner_sees_q_space_for_63_mod_64_rule() -> None:
    row = signature_for_rule({"modulus": 2**12, "residue": 63, "suggested_k": 12})
    report = mine_families_from_signatures([row], focus_burst=6)
    assert report["q_coordinate_rows"] == 1
    assert report["q_space_trie_compression"]["raw_leaf_count"] == 1
    assert report["parent_residue_mod_64"][0]["value"] == 63


def test_q_bit_cube_miner_generalizes_known_pure_even_q_class() -> None:
    rows = []
    for q in range(8):
        rows.append(
            {
                "q_residue": q,
                "q_mod_power": 3,
                "q_modulus": 8,
                "label": "even" if q % 2 == 0 else "odd",
            }
        )

    cubes = mine_q_bit_cubes(
        rows,
        label_keys=["label"],
        depths=[3],
        min_support=4,
        max_free_bits=2,
    )

    assert cubes
    assert cubes[0]["support"] == 4
    assert cubes[0]["free_bits"] == 2
    assert cubes[0]["bit_pattern_lsb_first"] in {"0??", "1??"}


def test_q_bit_cube_validation_expands_to_exact_residue_certificate() -> None:
    cube = {
        "depth": 18,
        "mask": (1 << 18) - 1,
        "value": 117575,
        "label": {"k": 24},
        "free_bits": 0,
    }

    result = validate_q_bit_cube(cube, burst_length=6, search_limit=100000)

    assert result["status"] == "PASS"
    assert result["verified_children"] == 1
