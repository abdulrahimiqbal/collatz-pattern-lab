from collatz_lab.compress import TrieNode, compressed_terminals, insert_rule, union_density


def test_trie_merges_sibling_residue_classes() -> None:
    root = TrieNode()
    insert_rule(root, residue=0, depth=1)
    insert_rule(root, residue=1, depth=1)
    assert compressed_terminals(root) == [0]


def test_union_density_removes_redundant_children() -> None:
    rules = [
        {"modulus": 2, "residue": 1},
        {"modulus": 4, "residue": 1},
    ]
    assert union_density(rules) == 0.5
