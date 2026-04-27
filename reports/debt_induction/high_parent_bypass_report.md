# High-Parent Mixed-Modulus Bypass

- status: `MIXED_MODULUS_BYPASS_BUILT`
- ready for RUN-007: `False`
- source status: `HIGH_PARENT_BRANCHES_OPEN`
- source branches: `165`
- source open branches: `164`
- mixed successor families: `164`
- sample checks passed: `True`
- odd-coordinate descent candidates: `65`
- scalar level-rank status: `FAIL`

## What This Bypasses

The blocked branches cannot be closed by more finite 2-adic source splitting. This report carries the lost information as an exact odd-modulus successor family.

## Formal Blockers

- mixed-modulus successor families are derived but no verifier consumes odd-modulus/debt states
- finite 2-adic source-depth refinement is known insufficient for these branches
- proof confidence remains 0 until a mixed-modulus debt verifier closes the families
- scalar parent-level rank is obstructed by a positive mixed-branch cycle

## Scalar Rank Obstruction

- cycle log-gain sum: `11.19667502361156`
- `P20:r46520809:d26`: P20 -> P23, odd gain <= `51.957136407494545`
- `P23:r60246179:d26`: P23 -> P20, odd gain <= `1402.8426830023527`

## Mixed Successor Sample

- `P7:r9512459:d24`: `z(k) = 1240 + 2187*k`; T=0 target `P21: r' odd, r' == 1240 mod 2187`
- `P9:r26781493:d25`: `z(k) = 15710 + 19683*k`; T=0 target `P24: r' odd, r' == 15710 mod 19683`
- `P6:r52011671:d26`: `z(k) = 565 + 729*k`; T=0 target `P25: r' odd, r' == 565 mod 729`
- `P6:r21817285:d25`: `z(k) = 474 + 729*k`; T=0 target `P23: r' odd, r' == 474 mod 729`
- `P7:r52011671:d26`: `z(k) = 1695 + 2187*k`; T=0 target `P24: r' odd, r' == 1695 mod 2187`
- `P11:r35743131:d26`: `z(k) = 94351 + 177147*k`; T=0 target `P23: r' odd, r' == 94351 mod 177147`
- `P8:r13235615:d24`: `z(k) = 5176 + 6561*k`; T=0 target `P23: r' odd, r' == 5176 mod 6561`
- `P10:r53666407:d26`: `z(k) = 47221 + 59049*k`; T=0 target `P25: r' odd, r' == 47221 mod 59049`

## Next Step

Build a mixed-modulus debt verifier whose state is (parent level, odd-coordinate congruence modulo 3^a, remaining growth debt). Use the exact successor families in this report as its transition source.
