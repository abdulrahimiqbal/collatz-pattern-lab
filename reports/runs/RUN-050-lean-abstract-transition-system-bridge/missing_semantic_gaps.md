# RUN-050 Missing Semantic Gaps

## Proved

Lean now proves the abstract transition-system bridge:

```lean
theorem certified_transition_system_implies_descent
  (system : CertifiedTransitionSystem)
  (entry : UniversalEntrySemantics system)
  (coverage : CoverageSemantics system)
  (sound : TransitionSoundnessSemantics system)
  (noEscape : NoEscapeSemantics system)
  (wf : WellFoundedSystem system) :
  DescentTheorem
```

This theorem is RUN-independent.  It threads the original `root` through
internal states, so every certified descent is below the original input, not
merely below an intermediate iterate.

## Not Yet Instantiated

The RUN-048/RUN-046 bundle does not yet provide enough semantic payload to
prove the five assumptions of the abstract theorem.

- `MISSING_S3_SEMANTIC_ROLE_FIELD`: Lean data has S3 debt arithmetic, but not a
  certificate-level semantic role mapping each S3 fact to direct descent,
  ranking decrease, exit certificate, or supporting debt edge.
- `MISSING_S6_PROOF_TREE_SEMANTICS`: S6 payloads list dependency IDs and replay
  counts, but not theorem-level proof-tree conclusions for coverage,
  no-escape, induction, transition composition, ranking/well-foundedness, or
  residual parent coverage.
- `MISSING_KERNEL_TO_PATH_SEMANTIC_LINK`: the natural-kernel certificate proves
  no positive natural fixed-point coordinate, but does not yet prove that every
  infinite internal parent-state path maps into that kernel.
- `MISSING_TOP_LEVEL_COVERAGE_DOMAIN_MAP`: top-level certificates do not yet
  expose a Lean-usable map from arbitrary odd `n > 1` to covered
  `InternalState`s and outgoing certified edges.

No `run048_descent : DescentTheorem` or `collatz_conjecture :
CollatzConjecture` theorem is declared in this state.
