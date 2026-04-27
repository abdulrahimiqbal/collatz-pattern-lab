from collatz_lab.cube_compress import Cube, cube_contains, cube_count, residues_to_cubes


def test_full_set_compresses_to_one_all_star_cube() -> None:
    cubes = residues_to_cubes(set(range(8)), depth=3)
    assert cubes == [Cube("***", depth=3, bit_order="lsb")]
    assert cube_count(cubes[0]) == 8


def test_empty_set_returns_empty() -> None:
    assert residues_to_cubes(set(), depth=4) == []


def test_q_9_mod_16_compresses_to_one_cube_at_depth_20() -> None:
    residues = {q for q in range(1 << 20) if q % 16 == 9}
    cubes = residues_to_cubes(residues, depth=20)
    assert len(cubes) == 1
    assert cubes[0].bits == "1001" + "*" * 16


def test_reexpanded_cubes_equal_original_set() -> None:
    residues = {0, 1, 4, 5, 7}
    cubes = residues_to_cubes(residues, depth=3)
    expanded = {x for x in range(8) if any(cube_contains(cube, x) for cube in cubes)}
    assert expanded == residues
