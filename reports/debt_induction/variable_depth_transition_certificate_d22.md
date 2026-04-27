# Variable-Depth Transition Certificate

- status: `VARIABLE_DEPTH_CERTIFICATE_NOT_READY`
- ready for RUN-007: `False`
- source depth: `12`
- max refinement depth: `22`
- start states: `7168`
- reachable states: `22140`
- exact projection passed: `False`
- potential status: `PASS`
- bad states: `114`
- transition status counts: `{'PROVED_EXACT_VARIABLE_DEPTH_TRANSITION': 19713, 'NEEDS_DEEPER_SOURCE_SPLIT': 1193, 'CLOSED_BY_DIRECT_BURST_DESCENT': 1234}`
- refinement count: `1079`

## Formal Blockers

- variable-depth exact projection still has blocked states
- log-potential/ranking passed
- bounded certificate still needs audit before theorem promotion

## Bad State Sample

- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r1123851:d21 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P9:r1615669:d21 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P6:r1680023:d21 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P6:r845765:d20 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r1680023:d21 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P8:r652703:d20 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P10:r3334759:d22 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P12:r2371793:d22 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P12:r2761729:d22 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P11:r2188699:d22 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P3:r3417581:d22 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P1:r1398101:d21 - source depth does not prove both h and the next parent level for the whole class

## Next Step

Refine blocked variable-depth states by increasing source depth or adding a richer rank/debt state; RUN-007 remains blocked until ready_for_run7 is true.
