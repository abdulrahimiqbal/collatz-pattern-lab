# RUN-033 New Math Required

- classification: `MISSING_PARENT_COORDINATE_MAP`
- unresolved SCC: `run030_parent_state_scc_0001`
- states: `P12, P13, P14, P15, P16, P17, P18, P19, P20, P21, P22, P23, P24`
- extracted internal exact S4 edges: `106`
- S4 certs missing parent-coordinate maps: `106`

RUN-033 replayed the internal SCC edge certificates as exact HIGH_PARENT_SUCCESSOR_EXACT payloads.
Those payloads prove the existing `z(k)` successor congruence and valuation statement, but they do not expose the algebra needed to rewrite each edge as

`q' = (A*q + B) / D` for `P_a(q): n = 2^a*q - 1`.

## Required Semantic Fields

- `source_parent_coordinate_parameterization`
- `q_to_k_affine_map`
- `target_parent_coordinate_formula`
- `integrality_domain_for_q`

Without those fields, cycle composition would be composing an untrusted interpretation rather than replaying the certificate language.
The next replayable certificate must either add exact parent-coordinate maps for all internal SCC edges, or introduce a different exact measure defined directly on the current `z(k)`/valuation domains.
