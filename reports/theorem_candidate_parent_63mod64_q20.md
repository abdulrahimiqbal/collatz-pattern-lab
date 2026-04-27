# Theorem Candidate: Parent `63 mod 64` Frontier

- q-depth: `20`
- verifier status: `THEOREM_CANDIDATE_NOT_COLLATZ_PROOF`

This is not a proof of Collatz. Infinite families are exact only where labeled `PROVED_INFINITE_FAMILY`; finite-depth verification is not universal proof; numeric potential search is not formal proof.

## Residual Frontier

`{'total_q_classes': 1048576, 'existing_cube_covered_q_classes': 4768, 'residual_certified_q_classes': 416096, 'residual_unknown_q_classes': 627712, 'total_certified_within_parent_percent': 40.13671875, 'unknown_within_parent_percent': 59.86328125, 'status': 'VERIFIED_FINITE_DEPTH'}`

## Known Exact Infinite Families Discovered

- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 0 and q == 9 mod 2^4, C^16(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 1 and q == 6 mod 2^6, C^19(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 2 and q == 4 mod 2^7, C^21(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 3 and q == 88 mod 2^9, C^24(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 4 and q == 400 mod 2^10, C^26(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 5 and q == 1632 mod 2^12, C^29(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 6 and q == 1088 mod 2^14, C^32(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 7 and q == 11648 mod 2^15, C^34(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 8 and q == 51456 mod 2^17, C^37(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 9 and q == 34304 mod 2^18, C^39(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 10 and q == 197632 mod 2^20, C^42(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 11 and q == 1529856 mod 2^21, C^44(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 12 and q == 1019904 mod 2^23, C^47(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 13 and q == 679936 mod 2^25, C^50(n) < n.
- `PROVED_INFINITE_FAMILY`: For n = 64*q - 1 with v2(q) = 14 and q == 22822912 mod 2^26, C^52(n) < n.

## Parent Return Map Image Comparison

- return maps: `300`
- observed image classes: `24`
- matched observed image classes: `24`
- unmatched observed image classes: `0`
- projected depth counts: `[{'map_count': 14, 'q_image_depth': 0}, {'map_count': 13, 'q_image_depth': 1}, {'map_count': 12, 'q_image_depth': 2}, {'map_count': 11, 'q_image_depth': 3}, {'map_count': 10, 'q_image_depth': 4}, {'map_count': 9, 'q_image_depth': 5}, {'map_count': 8, 'q_image_depth': 6}, {'map_count': 7, 'q_image_depth': 7}, {'map_count': 6, 'q_image_depth': 8}, {'map_count': 5, 'q_image_depth': 9}, {'map_count': 4, 'q_image_depth': 10}, {'map_count': 3, 'q_image_depth': 11}, {'map_count': 2, 'q_image_depth': 12}, {'map_count': 1, 'q_image_depth': 13}]`


## Sharp Return Subsystem

- status: `PROVED_TRANSITION_ONLY_AND_PROVED_POTENTIAL_DECREASE`
- transition: `R(q) = (729*q + 1) / 128`
- identity: `J(R(q))=J(q)-7`
- sharp branch count at q-depth `23`: `65536`
- guaranteed exit after `1` return(s): `65024`
- guaranteed exit after `2` return(s): `508`
- needs deeper bits: `4`
- potential status: `PROVED_POTENTIAL_DECREASE`
- q9 pullback ancestor status: `ANCESTOR_DEBT_UNPAID`


## Parent-State Sample

`[{'count': 65, 'transition': 'P_1->P_1'}, {'count': 65, 'transition': 'P_2->P_1'}, {'count': 65, 'transition': 'P_17->P_1'}, {'count': 64, 'transition': 'P_3->P_1'}, {'count': 64, 'transition': 'P_7->P_1'}, {'count': 64, 'transition': 'P_8->P_1'}, {'count': 64, 'transition': 'P_9->P_1'}, {'count': 64, 'transition': 'P_10->P_1'}, {'count': 64, 'transition': 'P_11->P_1'}, {'count': 64, 'transition': 'P_14->P_1'}, {'count': 64, 'transition': 'P_15->P_1'}, {'count': 64, 'transition': 'P_16->P_1'}]`


## Cycle Certificates

- `PROVED_HEIGHT_DECREASE_ON_REPEAT` for `sharp_q23_R23` with height `v2(601*q + 1)`
- `PROVED_HEIGHT_DECREASE_ON_REPEAT` for `sharp_q23_R23_twice` with height `v2(515057*q + 857)`

## Cycle Mining

- q-depth: `23`
- return maps in depth: `150`
- status counts: `{'PROVED_HEIGHT_DECREASE_ON_REPEAT': 865}`

- `length_1`: `{'PROVED_HEIGHT_DECREASE_ON_REPEAT': 150}`
- `length_2`: `{'PROVED_HEIGHT_DECREASE_ON_REPEAT': 715}`

## 2-adic Basin Acceleration

- `PROVED_NO_INFINITE_REPEAT` for `sharp_q23_R23` with height `v2(601*q + 1)`

## Cube Infinite Lift

- infinite lift rate: `0.020477815699658702`
- status counts: `{'NEEDS_SPLIT': 574, 'PROVED_INFINITE_ANCESTOR_DESCENT': 12}`

## Proof Obligations

- proof status: `INCOMPLETE_OPEN_OBLIGATIONS`
- closed: `10`
- open: `27`
- status counts: `{'CLOSED_BY_ANCESTOR_DESCENT': 6, 'CLOSED_BY_EXACT_POTENTIAL': 1, 'CLOSED_BY_HEIGHT_RANKING': 3, 'NEEDS_SPLIT': 27}`

## Proof Policy

- status: `PROOF_POLICY_BASELINE_NOT_A_COLLATZ_PROOF`
- policy: `heuristic_seed_policy`
- actions tried: `114`
- action counts: `{'LIFT_CUBE': 1, 'PROMOTE_TO_PARENT_STATE': 7, 'PROPOSE_VALUATION_FORM': 11, 'RUN_FALSIFIER': 7, 'SPLIT_BY_H': 20, 'SPLIT_BY_PARENT_LEVEL': 20, 'SPLIT_BY_RESIDUE': 26, 'TRY_ADIC_BASIN': 1, 'TRY_ANCESTOR_COMPOSITION': 6, 'TRY_SCC_RANKING': 7, 'TRY_VALUATION_CLOSURE': 8}`
- result counts: `{'NEEDS_SPLIT': 12, 'REDUCED': 102}`
- proof status counts: `{'CLOSED_BY_HEIGHT_RANKING': 7, 'NEEDS_SPLIT': 38, 'REDUCED_BY_DEBT_CHECK': 6, 'REDUCED_BY_FALSIFIER_CHECK': 7, 'REDUCED_BY_HEIGHT_RANKED_SUBBRANCH': 1, 'REDUCED_BY_PARENT_LEVEL_SPLIT': 40, 'REDUCED_BY_VALUATION_CLOSURE': 8, 'REDUCED_TO_PARENT_STATE_TRANSITION_OBLIGATION': 7}`
- useful action rate: `0.8947368421052632`
- model-guided obligation closure rate: `0.0`

## Remaining Hard Families

- `UNKNOWN`: v2(q)=0 (a=6), h=1 (161792 unknown)
- `UNKNOWN`: v2(q)=1 (a=7), h=1 (100352 unknown)
- `UNKNOWN`: v2(q)=0 (a=6), h=2 (61440 unknown)
- `UNKNOWN`: v2(q)=2 (a=8), h=1 (58368 unknown)
- `UNKNOWN`: v2(q)=1 (a=7), h=2 (41984 unknown)
- `UNKNOWN`: v2(q)=3 (a=9), h=1 (31744 unknown)
- `UNKNOWN`: v2(q)=2 (a=8), h=2 (26624 unknown)
- `UNKNOWN`: v2(q)=0 (a=6), h=3 (19456 unknown)
- `UNKNOWN`: v2(q)=4 (a=10), h=1 (16384 unknown)
- `UNKNOWN`: v2(q)=1 (a=7), h=3 (15360 unknown)
- `UNKNOWN`: v2(q)=3 (a=9), h=2 (15360 unknown)
- `UNKNOWN`: v2(q)=2 (a=8), h=3 (11264 unknown)
- `UNKNOWN`: v2(q)=5 (a=11), h=1 (8192 unknown)
- `UNKNOWN`: v2(q)=4 (a=10), h=2 (8192 unknown)
- `UNKNOWN`: v2(q)=3 (a=9), h=3 (7168 unknown)
- `UNKNOWN`: v2(q)=4 (a=10), h=3 (4096 unknown)
- `UNKNOWN`: v2(q)=2 (a=8), h=4 (4096 unknown)
- `UNKNOWN`: v2(q)=1 (a=7), h=4 (4096 unknown)
- `UNKNOWN`: v2(q)=6 (a=12), h=1 (4096 unknown)
- `UNKNOWN`: v2(q)=5 (a=11), h=2 (4096 unknown)

## Sharp Recursive Unknown States

- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=41:q64=11:return=0` (8192 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=27:q64=15:return=0` (8192 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=63:q64=23:return=1` (8192 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=31:q64=23:return=0` (8192 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=39:q64=39:return=0` (8192 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=47:q64=55:return=0` (8192 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=55:q64=7:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=57:q64=43:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=43:q64=47:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=15:q64=55:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=59:q64=15:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=61:q64=51:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=19:q64=63:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=7:q64=39:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=9:q64=11:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=33:q64=59:return=0` (7168 unknown)
- `UNKNOWN`: `unknown:t=1:a=7:h=1:post64=27:q64=10:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=1:a=7:h=1:post64=7:q64=26:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=1:a=7:h=1:post64=9:q64=50:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=29:q64=51:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=1:a=7:h=1:post64=31:q64=58:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=1:q64=59:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=2:post64=31:q64=5:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=23:q64=7:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=1:a=7:h=1:post64=33:q64=18:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=1:a=7:h=1:post64=55:q64=26:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=3:q64=31:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=2:post64=39:q64=37:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=0:a=6:h=1:post64=25:q64=43:return=0` (4096 unknown)
- `UNKNOWN`: `unknown:t=1:a=7:h=1:post64=57:q64=50:return=0` (4096 unknown)

## Compression

`{'k16': {'raw_residue_count': 65536, 'cube_count': 1, 'compression_ratio_raw_to_cubes': 65536.0, 'top_conditions': ['q == 9 mod 2^4'], 'status': 'VERIFIED_FINITE_DEPTH'}, 'k19': {'raw_residue_count': 65536, 'cube_count': 4, 'compression_ratio_raw_to_cubes': 16384.0, 'top_conditions': ['q == 6 mod 2^6', 'q == 17 mod 2^6', 'q == 29 mod 2^6', 'q == 35 mod 2^6'], 'status': 'VERIFIED_FINITE_DEPTH'}, 'k21': {'raw_residue_count': 114688, 'cube_count': 14, 'compression_ratio_raw_to_cubes': 8192.0, 'top_conditions': ['q == 4 mod 2^7', 'q == 66 mod 2^7', 'q == 38 mod 2^7', 'q == 54 mod 2^7', 'q == 62 mod 2^7', 'q == 65 mod 2^7', 'q == 49 mod 2^7', 'q == 85 mod 2^7', 'q == 77 mod 2^7', 'q == 61 mod 2^7'], 'status': 'VERIFIED_FINITE_DEPTH'}, 'k24': {'raw_residue_count': 67072, 'cube_count': 35, 'compression_ratio_raw_to_cubes': 1916.3428571428572, 'top_conditions': ['q == 196 mod 2^9', 'q == 36 mod 2^9', 'q == 212 mod 2^9', 'q == 300 mod 2^9', 'q == 2 mod 2^9', 'q == 354 mod 2^9', 'q == 18 mod 2^9', 'q == 358 mod 2^9', 'q == 214 mod 2^9', 'q == 374 mod 2^9'], 'status': 'VERIFIED_FINITE_DEPTH'}, 'k26': {'raw_residue_count': 103264, 'cube_count': 125, 'compression_ratio_raw_to_cubes': 826.112, 'top_conditions': ['q == 400 mod 2^10', 'q == 200 mod 2^10', 'q == 472 mod 2^10', 'q == 824 mod 2^10', 'q == 580 mod 2^10', 'q == 452 mod 2^10', 'q == 804 mod 2^10', 'q == 932 mod 2^10', 'q == 484 mod 2^10', 'q == 660 mod 2^10'], 'status': 'VERIFIED_FINITE_DEPTH'}, 'residual_certified': {'raw_residue_count': 416096, 'cube_count': 179, 'compression_ratio_raw_to_cubes': 2324.558659217877, 'top_conditions': ['q == 9 mod 2^4', 'q == 6 mod 2^6', 'q == 17 mod 2^6', 'q == 29 mod 2^6', 'q == 35 mod 2^6', 'q == 4 mod 2^7', 'q == 66 mod 2^7', 'q == 38 mod 2^7', 'q == 54 mod 2^7', 'q == 62 mod 2^7'], 'status': 'VERIFIED_FINITE_DEPTH'}, 'unknown': {'raw_residue_count': 627712, 'cube_count': 228, 'compression_ratio_raw_to_cubes': 2753.122807017544, 'top_conditions': ['q == 0 mod 2^5', 'q == 48 mod 2^6', 'q == 40 mod 2^6', 'q == 60 mod 2^6', 'q == 58 mod 2^6', 'q == 23 mod 2^6', 'q == 80 mod 2^7', 'q == 8 mod 2^7', 'q == 120 mod 2^7', 'q == 116 mod 2^7'], 'status': 'VERIFIED_FINITE_DEPTH'}}`

## Potential

`{'status': 'NUMERIC_HEURISTIC', 'found_potential': True, 'raw_status': 'PASS', 'suggested_state_splits': []}`
