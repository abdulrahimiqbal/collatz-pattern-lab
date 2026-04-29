# RUN-056 Projection Status

RUN-056 now hardens the reflected projection instead of preserving the
level-0 entry shortcut.

Lean now proves:

- `Collatz.run051EntryProjection_built`
- `Collatz.run051CoveredProjection_built`
- `Collatz.run051Coverage_sound`
- `Collatz.run051Entry_check_fails`
- `Collatz.run051Coverage_check_fails`
- `Collatz.run051Bundle_check_fails`

Important changes:

- `entryPredicate` no longer hardcodes `state.node = { id := 0 }`.
- `coveredPredicate` now requires the state node to correspond to a generated `NodeId`.
- `checkCoverage` now checks that every transition target is a generated node and that the generated node level matches the semantic target parent level.
- `checkEntry run051Bundle` is now deliberately false because the RUN-051 payload does not yet provide a real map from arbitrary odd `n` via `v2(n+1)` into the finite certified node set.
- `checkCoverage run051Bundle` is now deliberately false because the RUN-051 payload does not yet provide a real coverage-domain membership theorem beyond structural domain metadata.

Exact remaining projection gap:

- `MISSING_ENTRY_TO_CERTIFIED_NODE_MAP`: generate or prove a theorem that arbitrary odd `n > 1` enters a certified node/domain consumed by the reflected transition graph.
- `MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM`: generate or prove the actual coverage-domain map rather than accepting a universal-domain shortcut.

Remaining global semantic gaps:

- `MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS`
- `MISSING_KERNEL_TO_PATH_LINK`
- `MISSING_WELL_FOUNDED_RANK_BRIDGE`

No `run051_descent` or `collatz_conjecture` theorem is stated in this run.
