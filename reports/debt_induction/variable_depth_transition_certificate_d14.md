# Variable-Depth Transition Certificate

- status: `VARIABLE_DEPTH_CERTIFICATE_NOT_READY`
- ready for RUN-007: `False`
- source depth: `14`
- start states: `28672`
- reachable states: `36850`
- exact projection passed: `False`
- potential status: `PASS`
- bad states: `145`
- transition status counts: `{'PROVED_EXACT_VARIABLE_DEPTH_TRANSITION': 32915, 'NEEDS_DEEPER_SOURCE_SPLIT': 145, 'CLOSED_BY_DIRECT_BURST_DESCENT': 3790}`

## Formal Blockers

- variable-depth exact projection still has blocked states
- log-potential/ranking passed
- bounded certificate still needs audit before theorem promotion

## Bad State Sample

- `NEEDS_DEEPER_SOURCE_SPLIT`: P6:r8855:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r8413:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P6:r10181:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P8:r13727:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r8855:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P9:r10037:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P8:r8413:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P6:r12833:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P10:r8807:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r9739:d14 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P12:r1:d1 - source depth does not prove both h and the next parent level for the whole class
- `NEEDS_DEEPER_SOURCE_SPLIT`: P7:r29:d6 - source depth does not prove both h and the next parent level for the whole class

## Next Step

Refine blocked variable-depth states by increasing source depth or adding a richer rank/debt state; RUN-007 remains blocked until ready_for_run7 is true.
