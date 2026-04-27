from pathlib import Path

import pandas as pd

from collatz_lab.discover import mine_lifted_descent_candidates
from collatz_lab.generate import row_for_n
from collatz_lab.verifier import verify_fixed_residue_descent_exhaustive


def test_lifted_miner_emits_verifiable_parity_stable_rule(tmp_path: Path) -> None:
    row = row_for_n(
        3,
        task="multitask",
        base=2,
        bits=2,
        lsb_first=True,
        split="test",
        parity_k=8,
        max_steps=100,
        signed=True,
    )
    row["hard_case"] = 1
    data_path = tmp_path / "tiny.parquet"
    pd.DataFrame([row]).to_parquet(data_path)

    candidates = mine_lifted_descent_candidates(
        data_path,
        max_k=20,
        max_candidates=10,
        hard_only=True,
    )

    assert candidates
    candidate = candidates[0]
    assert candidate["modulus"] == 64
    assert candidate["residue"] == 3
    assert candidate["suggested_k"] == 6

    result = verify_fixed_residue_descent_exhaustive(
        modulus=candidate["modulus"],
        residue=candidate["residue"],
        k=candidate["suggested_k"],
        t_limit=100,
    )
    assert result.status == "PASS"
