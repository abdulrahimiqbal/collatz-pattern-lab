# Model Proof Verification

- status: `FAIL`
- proof confidence: `0.0`
- accepted claims: `1 / 4`
- claim status counts: `{'PASS': 1, 'REDUCED': 1, 'FAIL_REQUIRES_REPAIR': 1, 'FAIL': 1}`
- proof action result counts: `{'REDUCED': 4}`

## Accepted

- `L-MM1-high-parent-successor` via `high_parent_bypass_exact_successor_checker`

## Failed Or Open

- `L-MM2-state-space`: `REDUCED` via `typed_proof_dsl_contract`
- `L-MM3-debt-rank`: `FAIL_REQUIRES_REPAIR` via `scalar_parent_level_rank_checker`
- `L-MM4-theorem-assembly`: `FAIL` via `strict_theorem_verifier`

## Next Step

Implement the mixed-modulus debt verifier and train the proof model on its PASS/FAIL/repair traces.
