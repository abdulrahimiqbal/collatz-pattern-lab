# Proof-Policy Run v1

- status: `PROOF_POLICY_BASELINE_NOT_A_COLLATZ_PROOF`
- policy: `heuristic_seed_policy`
- input open obligations: `27`
- attempted open obligations: `27`
- actions tried: `113`
- action counts: `{'SPLIT_BY_H': 26, 'LIFT_CUBE': 1, 'TRY_VALUATION_CLOSURE': 8, 'RUN_FALSIFIER': 7, 'SPLIT_BY_RESIDUE': 26, 'TRY_ANCESTOR_COMPOSITION': 6, 'PROMOTE_TO_PARENT_STATE': 7, 'TRY_ADIC_BASIN': 1, 'SPLIT_BY_PARENT_LEVEL': 20, 'PROPOSE_VALUATION_FORM': 11}`
- result counts: `{'NEEDS_SPLIT': 91, 'FAILED': 8, 'REDUCED': 14}`
- proof status counts: `{'NEEDS_SPLIT': 91, 'FAILED_VERIFIER_OR_UNIMPLEMENTED': 8, 'REDUCED_BY_DEBT_CHECK': 6, 'REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION': 7, 'REDUCED_BY_HEIGHT_RANKED_SUBBRANCH': 1}`
- useful action rate: `0.12389380530973451`
- model-guided obligation closure rate: `0.0`

This is not a proof of Collatz. It is the verifier-backed proof-game scaffold that records proof-action traces for future model training.

## Highest-Reward Attempts

- `unresolved_bucket:t=0:a=6:h=1` -> `TRY_ADIC_BASIN` => `REDUCED_BY_HEIGHT_RANKED_SUBBRANCH` reward `55`
- `unresolved_bucket:t=0:a=6:h=1` -> `PROMOTE_TO_PARENT_STATE` => `REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION` reward `40`
- `unresolved_bucket:t=1:a=7:h=1` -> `PROMOTE_TO_PARENT_STATE` => `REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION` reward `40`
- `unresolved_bucket:t=2:a=8:h=1` -> `PROMOTE_TO_PARENT_STATE` => `REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION` reward `40`
- `unresolved_bucket:t=3:a=9:h=1` -> `PROMOTE_TO_PARENT_STATE` => `REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION` reward `40`
- `unresolved_bucket:t=4:a=10:h=1` -> `PROMOTE_TO_PARENT_STATE` => `REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION` reward `40`
- `unresolved_bucket:t=5:a=11:h=1` -> `PROMOTE_TO_PARENT_STATE` => `REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION` reward `40`
- `unresolved_bucket:t=6:a=12:h=1` -> `PROMOTE_TO_PARENT_STATE` => `REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION` reward `40`
- `cube_lift:k19:NEEDS_SPLIT` -> `TRY_ANCESTOR_COMPOSITION` => `REDUCED_BY_DEBT_CHECK` reward `20`
- `cube_lift:k21:NEEDS_SPLIT` -> `TRY_ANCESTOR_COMPOSITION` => `REDUCED_BY_DEBT_CHECK` reward `20`
- `cube_lift:k24:NEEDS_SPLIT` -> `TRY_ANCESTOR_COMPOSITION` => `REDUCED_BY_DEBT_CHECK` reward `20`
- `cube_lift:k26:NEEDS_SPLIT` -> `TRY_ANCESTOR_COMPOSITION` => `REDUCED_BY_DEBT_CHECK` reward `20`
- `cube_lift:residual_certified:NEEDS_SPLIT` -> `TRY_ANCESTOR_COMPOSITION` => `REDUCED_BY_DEBT_CHECK` reward `20`
- `cube_lift:unknown:NEEDS_SPLIT` -> `TRY_ANCESTOR_COMPOSITION` => `REDUCED_BY_DEBT_CHECK` reward `20`
- `unresolved_bucket:t=0:a=6:h=1` -> `SPLIT_BY_PARENT_LEVEL` => `NEEDS_SPLIT` reward `18`
- `unresolved_bucket:t=1:a=7:h=1` -> `SPLIT_BY_PARENT_LEVEL` => `NEEDS_SPLIT` reward `18`
- `unresolved_bucket:t=0:a=6:h=2` -> `SPLIT_BY_PARENT_LEVEL` => `NEEDS_SPLIT` reward `18`
- `unresolved_bucket:t=2:a=8:h=1` -> `SPLIT_BY_PARENT_LEVEL` => `NEEDS_SPLIT` reward `18`
- `unresolved_bucket:t=1:a=7:h=2` -> `SPLIT_BY_PARENT_LEVEL` => `NEEDS_SPLIT` reward `18`
- `unresolved_bucket:t=3:a=9:h=1` -> `SPLIT_BY_PARENT_LEVEL` => `NEEDS_SPLIT` reward `18`