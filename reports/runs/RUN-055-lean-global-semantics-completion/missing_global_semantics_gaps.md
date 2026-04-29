# RUN-055 Global Semantics Gaps

RUN-055 still does not add `run051_descent` or `collatz_conjecture`.

The reflected projection has been hardened:

- `entryState` is no longer the empty predicate.
- `covered` is no longer the empty predicate.
- `entryPredicate` no longer enters through parent level `P0`.
- `coveredPredicate` now requires generated-node membership.
- `checkCoverage` now verifies transition target node membership and target parent-level agreement.
- `checkCoverage` no longer accepts the universal-domain shortcut as sufficient coverage semantics.

Lean currently proves:

- `Collatz.run051EntryProjection_built`
- `Collatz.run051CoveredProjection_built`
- `Collatz.run051TransitionSoundness_sound`
- `Collatz.run051S3Roles_support_sound`
- `Collatz.run051S6ProofTrees_structural_sound`

Lean also proves the hardened bundle does not fully check:

- `Collatz.run051Entry_check_fails`
- `Collatz.run051Coverage_check_fails`
- `Collatz.run051Bundle_check_fails`

Exact current blocking gaps:

- `MISSING_ENTRY_TO_CERTIFIED_NODE_MAP`: the payload does not provide a Lean-checkable map from arbitrary odd `n > 1`, via `v2(n+1)`, into a generated certified `NodeId` and covered domain.
- `MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM`: the payload does not provide a Lean-checkable coverage-domain map; a universal-looking domain is not accepted as a complete semantic proof.
- `MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS`: S6 proof trees validate typed dependency shapes, but do not prove every covered state has an applicable transition whose full source domain holds or a certified exit.
- `MISSING_KERNEL_TO_PATH_LINK`: the natural-kernel payload does not prove every infinite internal path maps into the eliminated kernel.
- `MISSING_WELL_FOUNDED_RANK_BRIDGE`: S3 ranking support and guarded-kernel metadata do not yet construct `WellFoundedSystem`.

This is now an honest failure mode: the old level-0 entry shortcut and universal coverage shortcut no longer let the generated bundle pass.
