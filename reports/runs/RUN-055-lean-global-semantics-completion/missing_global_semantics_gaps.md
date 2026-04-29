# RUN-055 Global Semantics Gaps

RUN-055 still does not add `run051_descent` or `collatz_conjecture`.

The earlier empty projection blocker has been repaired. Lean now proves:

- `Collatz.Reflection.checkEntry_sound`
- `Collatz.Reflection.checkCoverage_sound`
- `Collatz.run051Entry_sound`
- `Collatz.run051Coverage_sound`

The exact current blocking gap is:

- `MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS`

Reason:

S6 proof trees are now checked structurally: dependencies must exist in the typed bundle, dependency claim kinds must match, proof steps must have inputs, and each proof tree must contain a rule that closes its claim kind. That still does not construct the semantic theorem required by `NoEscapeSemantics`: every covered nonterminal state must have a modeled transition or certified exit.

Remaining gaps:

- `MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS`
- `MISSING_KERNEL_TO_PATH_LINK`
- `MISSING_WELL_FOUNDED_RANK_BRIDGE`

Next required enrichment/formalization:

1. Prove S6 no-escape proof trees construct `NoEscapeSemantics`.
2. Prove guarded natural-kernel elimination and ranking support construct `WellFoundedSystem`.
3. Combine entry, coverage, transition soundness, no-escape, and well-foundedness into `checkCertifiedSystemBundle_sound`.
