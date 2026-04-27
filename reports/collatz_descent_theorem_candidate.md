# Collatz Descent Theorem Candidate

- verifier status: `FAIL`
- theorem: `forall n > 1 exists k >= 1 such that C^k(n) < n`
- states: `20`
- transitions: `128`
- ancestor descent certificates: `1`
- unknown obligations: `422`

This is not a proof unless `verifier_status` is `PASS`.

## Verification Errors

- unknown obligations remain: 422
- coverage is not universal over all parent states P_a

## Known Exact Ancestor Descent Certificates

- `PROVED_INFINITE_ANCESTOR_DESCENT`: n=64*q-1 and q == 9 mod 16 implies C^16(n)<n

## First Unknown Obligations

- `P6_q20_finite_frontier_coverage`: `NEEDS_SPLIT`
- `unresolved_bucket:t=0:a=6:h=1`: `NEEDS_SPLIT`
- `unresolved_bucket:t=1:a=7:h=1`: `NEEDS_SPLIT`
- `unresolved_bucket:t=0:a=6:h=2`: `NEEDS_SPLIT`
- `unresolved_bucket:t=2:a=8:h=1`: `NEEDS_SPLIT`
- `unresolved_bucket:t=1:a=7:h=2`: `NEEDS_SPLIT`
- `unresolved_bucket:t=3:a=9:h=1`: `NEEDS_SPLIT`
- `unresolved_bucket:t=2:a=8:h=2`: `NEEDS_SPLIT`
- `unresolved_bucket:t=0:a=6:h=3`: `NEEDS_SPLIT`
- `unresolved_bucket:t=4:a=10:h=1`: `NEEDS_SPLIT`
- `unresolved_bucket:t=1:a=7:h=3`: `NEEDS_SPLIT`
- `unresolved_bucket:t=3:a=9:h=2`: `NEEDS_SPLIT`
- `unresolved_bucket:t=2:a=8:h=3`: `NEEDS_SPLIT`
- `unresolved_bucket:t=4:a=10:h=2`: `NEEDS_SPLIT`
- `unresolved_bucket:t=5:a=11:h=1`: `NEEDS_SPLIT`
- `unresolved_bucket:t=3:a=9:h=3`: `NEEDS_SPLIT`
- `unresolved_bucket:t=1:a=7:h=4`: `NEEDS_SPLIT`
- `unresolved_bucket:t=2:a=8:h=4`: `NEEDS_SPLIT`
- `unresolved_bucket:t=4:a=10:h=3`: `NEEDS_SPLIT`
- `unresolved_bucket:t=5:a=11:h=2`: `NEEDS_SPLIT`
- `unresolved_bucket:t=6:a=12:h=1`: `NEEDS_SPLIT`
- `parent_state_transition_templates`: `UNKNOWN`
- `cube_lift:unknown:NEEDS_SPLIT`: `NEEDS_SPLIT`
- `cube_lift:residual_certified:NEEDS_SPLIT`: `NEEDS_SPLIT`
- `cube_lift:k26:NEEDS_SPLIT`: `NEEDS_SPLIT`
- `cube_lift:k24:NEEDS_SPLIT`: `NEEDS_SPLIT`
- `P10:h=1:to=P1:rdepth=7`: `NEEDS_SPLIT`
- `P10:h=1:to=P1:rdepth=7#2`: `NEEDS_SPLIT`
- `P10:h=1:to=P1:rdepth=7#3`: `NEEDS_SPLIT`
- `P11:h=1:to=P1:rdepth=7`: `NEEDS_SPLIT`