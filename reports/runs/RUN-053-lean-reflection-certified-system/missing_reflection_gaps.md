# RUN-053 Missing Reflection Gaps

Lean now has a typed finite `CertifiedSystemBundle` with generated `NodeId`,
`EdgeId`, and `CertId` constructors. The generated bundle passes the component
reflection checks by computation.

The final theorem is intentionally absent. The missing piece is not another
string payload; it is checker soundness from typed reflected data to the
semantic assumptions of RUN-050.

## Exact Missing Theorems

1. `checkTransitionSoundness_sound`

   Missing typed theorem:

   ```lean
   checkTransitionSoundness b = true →
   TransitionSoundnessSemantics b.system
   ```

   The reflected S4 edges contain typed IDs, source/target parents, ranks, and
   iterate-witness flags, but Lean still needs a generated `SystemEdge` for
   each `EdgeId` plus a proof that the edge certificate yields
   `EdgeSemantics edge`, i.e. an actual `Collatz.iter` transition or descent.

2. `checkCoverage_sound`

   Missing typed theorem:

   ```lean
   checkCoverage b = true → CoverageSemantics b.system
   ```

   The coverage domains are now numeric and typed by certificate ID, but Lean
   still needs the source-domain and target-domain predicates for each reflected
   edge and a proof that arbitrary covered states stay covered after internal
   transitions.

3. `checkNoEscape_sound`

   Missing typed theorem:

   ```lean
   checkNoEscape b = true → NoEscapeSemantics b.system
   ```

   The S6 no-escape proof trees are typed by dependency kind and proof rule.
   Lean still needs typed rule soundness for `apply_no_escape`,
   `compose_transition`, `apply_coverage`, `apply_ranking`,
   `apply_induction`, and `apply_residual_parent`.

4. `checkWellFounded_sound`

   Missing typed theorem:

   ```lean
   checkWellFounded b = true → WellFoundedSystem b.system
   ```

   The reflection checker verifies rank decrease or guarded-kernel marking for
   reflected finite edges. Lean still needs a theorem that every guarded
   non-decreasing internal edge is semantically ruled out by the RUN-045 natural
   kernel link over actual parent-state paths.

5. `checkEntry_sound`

   Missing typed theorem:

   ```lean
   checkEntry b = true → UniversalEntrySemantics b.system
   ```

   The entry certificate booleans are inspected, but the reflected system still
   needs a concrete `entryState` predicate mapping arbitrary odd `n > 1` into a
   generated covered node.

## Status

`run051Bundle_check` builds. `run051_descent : DescentTheorem` and
`collatz_conjecture : CollatzConjecture` are intentionally not declared.
