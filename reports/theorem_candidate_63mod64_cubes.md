# Cube Transition Theorem Candidate

- verifier status: `PASS_FRAGMENT`
- scope: validated q-bit cube families only; not a universal Collatz proof
- states: `14`
- transitions: `14`
- expanded certificates: `3584`
- density over all positive integers: `7.104873657226562e-05`
- coverage within `63 mod 64`: `0.4547119140625`%
- target type counts: `{'INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH': 64, 'OUTSIDE_FORCED_BURST_PARENT': 3520}`
- potential status: `PASS`

## States

- `cube_000` k=`26` pattern=`00011010101???0?????` support=`5` completions=`256` log_gain<=`-0.10421770840086218`
- `cube_001` k=`26` pattern=`0001101010??1?0?????` support=`5` completions=`256` log_gain<=`-0.10422759823160316`
- `cube_002` k=`26` pattern=`0001101010?1?1??????` support=`4` completions=`256` log_gain<=`-0.10423015477697206`
- `cube_003` k=`24` pattern=`0101011000????????` support=`3` completions=`256` log_gain<=`-0.5095487352711165`
- `cube_004` k=`24` pattern=`0001101001????????` support=`3` completions=`256` log_gain<=`-0.5096717457841774`
- `cube_005` k=`24` pattern=`000110100??0??????` support=`3` completions=`256` log_gain<=`-0.50952415647391`
- `cube_006` k=`26` pattern=`001010100010????????` support=`3` completions=`256` log_gain<=`-0.10421576038278502`
- `cube_007` k=`26` pattern=`00110000001?0???????` support=`3` completions=`256` log_gain<=`-0.10421659318581714`
- `cube_008` k=`26` pattern=`01010010110?1???????` support=`3` completions=`256` log_gain<=`-0.10422870771382883`
- `cube_009` k=`26` pattern=`00011000001?1???????` support=`3` completions=`256` log_gain<=`-0.1042288330658977`
- `cube_010` k=`26` pattern=`01001000111?1???????` support=`3` completions=`256` log_gain<=`-0.1042285365730168`
- `cube_011` k=`26` pattern=`0001100000?01???????` support=`3` completions=`256` log_gain<=`-0.10422804537679373`
- `cube_012` k=`26` pattern=`0010101000?01???????` support=`3` completions=`256` log_gain<=`-0.10422769702902707`
- `cube_013` k=`26` pattern=`0101001011?01???????` support=`3` completions=`256` log_gain<=`-0.10422870771382883`

## Transition Summary

- `cube_000` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'0': 16, '10': 16, '14': 16, '18': 16, '24': 16, '28': 16, '32': 16, '36': 16, '38': 16, '4': 16, '42': 16, '46': 16, '50': 16, '56': 16, '6': 16, '60': 16}`
- `cube_001` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'1': 16, '10': 16, '18': 16, '19': 16, '27': 16, '28': 16, '33': 16, '36': 16, '4': 16, '41': 16, '42': 16, '50': 16, '51': 16, '59': 16, '60': 16, '9': 16}`
- `cube_002` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'0': 16, '11': 16, '16': 16, '20': 16, '23': 16, '27': 16, '32': 16, '36': 16, '39': 16, '4': 16, '43': 16, '48': 16, '52': 16, '55': 16, '59': 16, '7': 16}`
- `cube_003` target types `{'INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH': 8, 'OUTSIDE_FORCED_BURST_PARENT': 248}`, image mod 64 `{'1': 8, '11': 8, '13': 8, '15': 8, '17': 8, '19': 8, '21': 8, '23': 8, '25': 8, '27': 8, '29': 8, '3': 8, '31': 8, '33': 8, '35': 8, '37': 8, '39': 8, '41': 8, '43': 8, '45': 8, '47': 8, '49': 8, '5': 8, '51': 8, '53': 8, '55': 8, '57': 8, '59': 8, '61': 8, '63': 8, '7': 8, '9': 8}`
- `cube_004` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'0': 8, '10': 8, '12': 8, '14': 8, '16': 8, '18': 8, '2': 8, '20': 8, '22': 8, '24': 8, '26': 8, '28': 8, '30': 8, '32': 8, '34': 8, '36': 8, '38': 8, '4': 8, '40': 8, '42': 8, '44': 8, '46': 8, '48': 8, '50': 8, '52': 8, '54': 8, '56': 8, '58': 8, '6': 8, '60': 8, '62': 8, '8': 8}`
- `cube_005` target types `{'INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH': 8, 'OUTSIDE_FORCED_BURST_PARENT': 248}`, image mod 64 `{'0': 8, '10': 8, '13': 8, '15': 8, '16': 8, '18': 8, '2': 8, '21': 8, '23': 8, '24': 8, '26': 8, '29': 8, '31': 8, '32': 8, '34': 8, '37': 8, '39': 8, '40': 8, '42': 8, '45': 8, '47': 8, '48': 8, '5': 8, '50': 8, '53': 8, '55': 8, '56': 8, '58': 8, '61': 8, '63': 8, '7': 8, '8': 8}`
- `cube_006` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'1': 16, '13': 16, '17': 16, '21': 16, '25': 16, '29': 16, '33': 16, '37': 16, '41': 16, '45': 16, '49': 16, '5': 16, '53': 16, '57': 16, '61': 16, '9': 16}`
- `cube_007` target types `{'INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH': 16, 'OUTSIDE_FORCED_BURST_PARENT': 240}`, image mod 64 `{'13': 16, '15': 16, '21': 16, '23': 16, '29': 16, '31': 16, '37': 16, '39': 16, '45': 16, '47': 16, '5': 16, '53': 16, '55': 16, '61': 16, '63': 16, '7': 16}`
- `cube_008` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'0': 16, '14': 16, '16': 16, '22': 16, '24': 16, '30': 16, '32': 16, '38': 16, '40': 16, '46': 16, '48': 16, '54': 16, '56': 16, '6': 16, '62': 16, '8': 16}`
- `cube_009` target types `{'INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH': 16, 'OUTSIDE_FORCED_BURST_PARENT': 240}`, image mod 64 `{'13': 16, '15': 16, '21': 16, '23': 16, '29': 16, '31': 16, '37': 16, '39': 16, '45': 16, '47': 16, '5': 16, '53': 16, '55': 16, '61': 16, '63': 16, '7': 16}`
- `cube_010` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'10': 16, '12': 16, '18': 16, '2': 16, '20': 16, '26': 16, '28': 16, '34': 16, '36': 16, '4': 16, '42': 16, '44': 16, '50': 16, '52': 16, '58': 16, '60': 16}`
- `cube_011` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'12': 16, '13': 16, '20': 16, '21': 16, '28': 16, '29': 16, '36': 16, '37': 16, '4': 16, '44': 16, '45': 16, '5': 16, '52': 16, '53': 16, '60': 16, '61': 16}`
- `cube_012` target types `{'OUTSIDE_FORCED_BURST_PARENT': 256}`, image mod 64 `{'0': 16, '1': 16, '16': 16, '17': 16, '24': 16, '25': 16, '32': 16, '33': 16, '40': 16, '41': 16, '48': 16, '49': 16, '56': 16, '57': 16, '8': 16, '9': 16}`
- `cube_013` target types `{'INSIDE_FORCED_BURST_PARENT_BUT_TOO_SHALLOW_FOR_CUBE_MATCH': 16, 'OUTSIDE_FORCED_BURST_PARENT': 240}`, image mod 64 `{'14': 16, '15': 16, '22': 16, '23': 16, '30': 16, '31': 16, '38': 16, '39': 16, '46': 16, '47': 16, '54': 16, '55': 16, '6': 16, '62': 16, '63': 16, '7': 16}`

## Interpretation

This is an exact proof fragment for the listed q-bit cube states. It is not a universal proof because the state set covers only a small 2-adic subset and the image transitions mostly leave the current validated cube state space after descending.
