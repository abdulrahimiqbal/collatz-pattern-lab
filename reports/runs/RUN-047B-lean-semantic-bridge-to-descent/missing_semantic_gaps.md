# RUN-047B Missing Semantic Gaps

Status: `PARTIAL_SEMANTIC_BRIDGE`.

Lean now defines the actual semantic objects needed for the bridge:

- `parentState`, `exactParentState`, and `semanticParentTransitionRel` over `Collatz.iter`.
- `SemanticParentTransition` for S4 parent-map certificates.
- `SemanticDescentOrExit` for S3 debt certificates.
- `S6LemmaSemanticClaim` and `TopLevelSemanticHypotheses`.
- `NoInfiniteInternalParentPathOverNat` over the RUN-046 natural-kernel affine map.

Lean also proves partial bridges:

- `even_semantic_descent`
- `S4ParentMapClaim.to_parent_map_payload`
- `S3DebtClaim.to_debt_arithmetic`
- `NaturalViabilityKernelEmpty.no_positive_fixed_point_coordinate`
- existing RUN-046 checker soundness theorems still build.

The full theorem still cannot be declared. Exact missing semantic theorems:

1. `S4ParentMapClaim.to_semantic_transition`

   Missing fields:
   - positive Collatz iterate step count for each S4 edge;
   - parity or iterate witness proving the affine parent-coordinate map equals `iter C t`;
   - proof that computed `q'` is positive for every `q` in the exact S4 domain.

2. `S3DebtExactClaim.to_semantic_descent_or_exit`

   Missing fields:
   - positive Collatz iterate step count for each S3 debt edge;
   - target iterate value or exact parent exit consumed by the graph;
   - theorem connecting `gain_num < gain_den` to eventual descent of the original natural number.

3. `S6LemmaClaim.to_semantic`

   Missing fields:
   - semantic theorem statement for each blocker id;
   - coverage interval theorem over parent-state domains;
   - no-escape theorem for certified branches;
   - induction and lifting theorem payloads over the actual Collatz map.

4. `natural_kernel_empty_implies_no_infinite_internal_path`

   Missing fields:
   - proof that every surviving internal natural path is represented by the RUN-045 affine kernel map;
   - guard/domain congruences for every repeated SCC step;
   - theorem connecting non-natural fixed-point exclusion to absence of infinite internal paths over `Nat`.

5. `top_level_semantics_imply_descent`

   Missing fields:
   - theorem that required coverage domains include every odd `n > 1`;
   - theorem that checked transition edges cover every nonterminal parent state;
   - theorem turning ranked graph metadata plus natural-kernel emptiness into actual Collatz descent.

Because these semantic bridges are missing, `run046_descent : DescentTheorem` and `collatz_conjecture : CollatzConjecture` are intentionally not declared.
