# RUN-055 Global Semantics Gaps

RUN-055 did not add `run051_descent` or `collatz_conjecture`.

Lean proves the current reflected system cannot satisfy entry semantics:

- `Collatz.GlobalSemantics.reflected_system_not_universal_entry`
- `Collatz.run051_entry_soundness_obstructed`

The exact blocking gap is:

- `MISSING_ENTRY_TO_COVERAGE_LINK`

Reason:

`CertifiedSystemBundle.system` currently projects:

- `entryState := fun _ _ => False`
- `covered := fun _ => False`

Therefore `checkEntry run051Bundle = true` cannot imply `UniversalEntrySemantics run051Bundle.system`. The RUN-051 coverage-domain payload validates descriptive domain metadata, but it does not yet construct a typed `InternalState` for arbitrary odd `n > 1`, nor prove that this state is covered by the reflected system.

Remaining gaps after entry:

- `MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM`
- `MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS`
- `MISSING_KERNEL_TO_PATH_LINK`
- `MISSING_WELL_FOUNDED_RANK_BRIDGE`

Next required enrichment/formalization:

1. Replace the empty `entryState` and `covered` projection with typed predicates derived from the RUN-051 coverage domain map.
2. Prove arbitrary odd `n > 1` maps to a typed covered parent-state domain.
3. Prove S6 no-escape proof trees construct `NoEscapeSemantics`.
4. Prove guarded natural-kernel elimination and ranking support construct `WellFoundedSystem`.
