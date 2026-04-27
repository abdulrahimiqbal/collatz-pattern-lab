import json

from collatz_lab.family_search import search_mask_families, verify_mask_family


def test_verify_mask_family_can_prove_wider_exact_family() -> None:
    result = verify_mask_family(prefix=0, mask_depth=2, proof_depth=4, max_expansions=16)
    assert result["status"] == "PASS"
    assert result["completion_count"] == 4
    assert result["claim"] == "for all n == 0 mod 2^2, C^4(n) < n"


def test_search_mask_families_merges_verified_leaves(tmp_path) -> None:
    rows = []
    for residue in [0, 4, 8, 12]:
        rows.append(
            {
                "rule": {
                    "modulus": 16,
                    "residue": residue,
                    "suggested_k": 4,
                    "source": "synthetic",
                },
                "exact": {"status": "PASS", "modulus": 16, "residue": residue, "k": 4},
            }
        )
    path = tmp_path / "verification.json"
    path.write_text(json.dumps(rows), encoding="utf-8")

    report = search_mask_families(path, max_free_bits=2, max_expansions=16)

    assert report["input_verified_leaf_count"] == 4
    assert report["candidate_pass_count"] >= 1
    assert report["selected_family_count"] == 1
    assert report["merged_leaf_count"] == 3
    assert report["top_selected_families"][0]["mask_depth"] == 2


def test_density_selection_keeps_broad_exact_families(tmp_path) -> None:
    rows = [
        {
            "rule": {"modulus": 16, "residue": 0, "suggested_k": 4, "source": "synthetic"},
            "exact": {"status": "PASS", "modulus": 16, "residue": 0, "k": 4},
        }
    ]
    path = tmp_path / "verification.json"
    path.write_text(json.dumps(rows), encoding="utf-8")

    report = search_mask_families(path, max_free_bits=2, max_expansions=16, selection_mode="density")

    assert report["selection_mode"] == "density"
    assert report["selected_family_count"] == 1
    assert report["top_selected_families"][0]["claim"] == "for all n == 0 mod 2^2, C^4(n) < n"
    assert report["selected_union_density_percent"] == 25.0
