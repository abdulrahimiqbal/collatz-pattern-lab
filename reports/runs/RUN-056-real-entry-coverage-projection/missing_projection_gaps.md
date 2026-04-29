# RUN-056 Projection Status

RUN-056 replaces the empty reflected-system projection:

- `entryState := CertifiedSystemBundle.entryPredicate`
- `covered := CertifiedSystemBundle.coveredPredicate`

Lean now proves:

- `Collatz.run051EntryProjection_built`
- `Collatz.run051CoveredProjection_built`

The projection is intentionally not a full global soundness proof. These remain for RUN-057 and later:

- `MISSING_ENTRY_TO_COVERAGE_LINK`: prove arbitrary odd `n > 1` enters a covered parent-coordinate domain.
- `MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM`: prove coverage-domain membership is closed under reflected S4 internal targets.
- `MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS`: prove S6 proof trees construct no-escape semantics.
- `MISSING_KERNEL_TO_PATH_LINK`: prove infinite internal paths map into the eliminated natural kernel.
- `MISSING_WELL_FOUNDED_RANK_BRIDGE`: prove ranked/guarded checks imply `WellFoundedSystem`.

No `run051_descent` or `collatz_conjecture` theorem is stated in this run.
