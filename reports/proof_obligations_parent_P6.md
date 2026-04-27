# P6 Proof Obligations

- proof status: `INCOMPLETE_OPEN_OBLIGATIONS`
- obligations: `37`
- closed obligations: `10`
- open obligations: `27`
- status counts: `{'NEEDS_SPLIT': 27, 'CLOSED_BY_ANCESTOR_DESCENT': 6, 'CLOSED_BY_HEIGHT_RANKING': 3, 'CLOSED_BY_EXACT_POTENTIAL': 1}`

| obligation | coverage | transition rule | ancestor descent? | SCC status |
|---|---:|---|---:|---|
| `P6_q20_finite_frontier_coverage` | `627712` | `finite-depth residual classifier` | `False` | `NEEDS_SPLIT` |
| `cube_lift:k16:PROVED_INFINITE_ANCESTOR_DESCENT` | `1` | `PROVED_INFINITE_ANCESTOR_DESCENT` | `True` | `CLOSED_BY_ANCESTOR_DESCENT` |
| `cube_lift:k19:NEEDS_SPLIT` | `3` | `NEEDS_SPLIT` | `False` | `NEEDS_SPLIT` |
| `cube_lift:k19:PROVED_INFINITE_ANCESTOR_DESCENT` | `1` | `PROVED_INFINITE_ANCESTOR_DESCENT` | `True` | `CLOSED_BY_ANCESTOR_DESCENT` |
| `cube_lift:k21:NEEDS_SPLIT` | `13` | `NEEDS_SPLIT` | `False` | `NEEDS_SPLIT` |
| `cube_lift:k21:PROVED_INFINITE_ANCESTOR_DESCENT` | `1` | `PROVED_INFINITE_ANCESTOR_DESCENT` | `True` | `CLOSED_BY_ANCESTOR_DESCENT` |
| `cube_lift:k24:NEEDS_SPLIT` | `33` | `NEEDS_SPLIT` | `False` | `NEEDS_SPLIT` |
| `cube_lift:k24:PROVED_INFINITE_ANCESTOR_DESCENT` | `2` | `PROVED_INFINITE_ANCESTOR_DESCENT` | `True` | `CLOSED_BY_ANCESTOR_DESCENT` |
| `cube_lift:k26:NEEDS_SPLIT` | `124` | `NEEDS_SPLIT` | `False` | `NEEDS_SPLIT` |
| `cube_lift:k26:PROVED_INFINITE_ANCESTOR_DESCENT` | `1` | `PROVED_INFINITE_ANCESTOR_DESCENT` | `True` | `CLOSED_BY_ANCESTOR_DESCENT` |
| `cube_lift:residual_certified:NEEDS_SPLIT` | `173` | `NEEDS_SPLIT` | `False` | `NEEDS_SPLIT` |
| `cube_lift:residual_certified:PROVED_INFINITE_ANCESTOR_DESCENT` | `6` | `PROVED_INFINITE_ANCESTOR_DESCENT` | `True` | `CLOSED_BY_ANCESTOR_DESCENT` |
| `cube_lift:unknown:NEEDS_SPLIT` | `228` | `NEEDS_SPLIT` | `False` | `NEEDS_SPLIT` |
| `adic_basin:sharp_q23_R23` | `` | `{'A': 729, 'B': 1, 'D': 128, 'd_power': 7, 'description': 'q == 23 mod 128 return inside n = 64*q - 1', 'domain_depth': 7, 'domain_residue': 23, 'height_linear_form': '601*q + 1', 'name': 'sharp_q23_R23', 'step_count': 13}` | `False` | `CLOSED_BY_HEIGHT_RANKING` |
| `sharp_q23_potential` | `` | `R(q) = (729*q + 1) / 128` | `False` | `CLOSED_BY_EXACT_POTENTIAL` |
| `cycle_mining:length_1:PROVED_HEIGHT_DECREASE_ON_REPEAT` | `150` | `PROVED_HEIGHT_DECREASE_ON_REPEAT` | `False` | `CLOSED_BY_HEIGHT_RANKING` |
| `cycle_mining:length_2:PROVED_HEIGHT_DECREASE_ON_REPEAT` | `715` | `PROVED_HEIGHT_DECREASE_ON_REPEAT` | `False` | `CLOSED_BY_HEIGHT_RANKING` |
| `unresolved_bucket:t=0:a=6:h=1` | `161792` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=1:a=7:h=1` | `100352` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=0:a=6:h=2` | `61440` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=2:a=8:h=1` | `58368` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=1:a=7:h=2` | `41984` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=3:a=9:h=1` | `31744` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=2:a=8:h=2` | `26624` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=0:a=6:h=3` | `19456` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=4:a=10:h=1` | `16384` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=1:a=7:h=3` | `15360` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=3:a=9:h=2` | `15360` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=2:a=8:h=3` | `11264` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=5:a=11:h=1` | `8192` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=4:a=10:h=2` | `8192` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=3:a=9:h=3` | `7168` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=4:a=10:h=3` | `4096` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=2:a=8:h=4` | `4096` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=1:a=7:h=4` | `4096` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=6:a=12:h=1` | `4096` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
| `unresolved_bucket:t=5:a=11:h=2` | `4096` | `not yet lifted to infinite theorem` | `False` | `NEEDS_SPLIT` |
