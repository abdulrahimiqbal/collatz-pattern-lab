# Mixed-Modulus Debt Verifier

- status: `MIXED_MODULUS_DEBT_VERIFIER_READY_WITH_OPEN_BLOCKERS`
- verifier available: `True`
- ready for RUN-009 evaluation: `True`
- proof closed: `False`
- verifier status: `FAIL`
- transitions: `1312`
- exact transition checks passed: `True`
- local descent pass count: `698`
- local descent fail count: `614`
- local descent pass rate: `0.5320121951219512`

## Blocking Obligations

- prove the debt/rank update for every local transition whose odd-coordinate gain bound is >= 1
- prove unbounded valuation closure for all T, not only the sampled valuation families
- map mixed-modulus target states back into the global theorem obligation graph
- assemble the strict theorem candidate and require strict verifier PASS before proof confidence changes

## Failure Sample

- `P16:r6332577:d23` T=`0` P16 -> P18: gain <= `75542777/14721185`
- `P16:r6332577:d23` T=`1` P16 -> P19: gain <= `59294749/23109793`
- `P16:r6332577:d23` T=`2` P16 -> P20: gain <= `51170735/39887009`
- `P17:r2110859:d22` T=`0` P17 -> P17: gain <= `194132275/6305163`
- `P17:r2110859:d22` T=`1` P17 -> P18: gain <= `161636219/10499467`
- `P17:r2110859:d22` T=`2` P17 -> P19: gain <= `145388191/18888075`
- `P17:r2110859:d22` T=`3` P17 -> P20: gain <= `137264177/35665291`
- `P17:r2110859:d22` T=`4` P17 -> P21: gain <= `4062007/2110859`

## Next Step

Use this verifier's PASS/FAIL transition traces to train the RUN-009 proof model, then search for a mixed-modulus debt/rank law that closes the failing transitions.
