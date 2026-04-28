# RUN-052 Missing Semantic Gaps

Lean built `Collatz.Run051Data` and `Collatz.Run051Proof` and inspected the
RUN-051 payload fields. The final descent theorem was not declared.

## Exact Missing Lean Theorems

1. `S3 role semantics`

   The payloads classify all S3 debt certificates as `SUPPORTING_DEBT_EDGE`,
   which is conservative and correct. Lean still needs a formal constructor
   turning each `S3DebtClaim + S3SemanticRolePayload` into either an
   `EdgeSemantics` contribution or a `RankingSupport` object consumed by a
   concrete `WellFoundedSystem`.

2. `S6 proof-tree semantics`

   The RUN-051 S6 proof trees now name semantic claim types, dependencies, and
   proof rules, but the rules are still data strings. Lean needs formal
   theorem objects for `compose_transition`, `apply_coverage`,
   `apply_no_escape`, `apply_ranking`, `apply_induction`, and
   `apply_residual_parent`, plus a checker that verifies each proof-tree step
   against typed inputs and outputs.

3. `kernel-to-path theorem`

   Lean proves the elementary number-theory obstruction:
   no positive natural number is divisible by every power of two. It still
   needs the semantic theorem that any infinite internal guarded parent-state
   path over `Nat` induces the divisibility family recorded by
   `run051KernelToPathLink`.

4. `coverage domain theorem`

   The top-level coverage map now records explicit domains, residual reference,
   and the universal-entry schema. Lean still needs a formal map from an
   arbitrary odd `n > 1` to a concrete covered `InternalState` and certified
   `SystemNode`, rather than a string-valued domain predicate.

5. `top-level instantiation mismatch`

   A concrete `CertifiedTransitionSystem` must be generated or defined with
   typed edges, source domains, target domains, exit certificates, and ranks
   matching the RUN-046/RUN-051 payloads. Only then can RUN-050's
   `certified_transition_system_implies_descent` be instantiated.

## Status

`run051_descent : DescentTheorem` and
`collatz_conjecture : CollatzConjecture` are intentionally absent.
