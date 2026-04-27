# Variable-Depth Transition Certificate

- status: `VARIABLE_DEPTH_CERTIFICATE_NOT_READY`
- ready for RUN-007: `False`
- source depth: `12`
- max refinement depth: `26`
- start states: `7168`
- reachable states: `31648`
- exact projection passed: `False`
- potential status: `PASS`
- bad states: `165`
- transition status counts: `{'PROVED_EXACT_VARIABLE_DEPTH_TRANSITION': 28370, 'NEEDS_DEEPER_SOURCE_SPLIT': 2001, 'CLOSED_BY_DIRECT_BURST_DESCENT': 1277}`
- refinement count: `1836`

## Formal Blockers

- variable-depth exact projection still has blocked states
- log-potential/ranking passed
- bounded certificate still needs audit before theorem promotion

## Bad State Sample

- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r9512459:d24 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P9:r26781493:d25 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P6:r52011671:d26 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P6:r21817285:d25 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r52011671:d26 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P11:r35743131:d26 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P8:r13235615:d24 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P10:r53666407:d26 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P12:r40120529:d26 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P12:r44704769:d26 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P1:r22369621:d25 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P2:r52195783:d26 - source depth does not prove both h and the next parent level for the whole class

## Next Step

Refine blocked variable-depth states by increasing source depth or adding a richer rank/debt state; RUN-007 remains blocked until ready_for_run7 is true.
