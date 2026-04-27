# 2-adic Basin Acceleration

- status: `PROOF_COMPILER_COMPONENT`

## sharp_q23_R23

- status: `PROVED_NO_INFINITE_REPEAT`
- map: `q -> (729q + 1)/128`
- fixed point in Z_2: `-1/601`
- height: `v2(601*q + 1)`
- height drop per repeat: `7`
- positive fixed point: `{'status': 'NO_INTEGER_FIXED_POINT', 'positive_integer_fixed_point': False, 'q': None}`

### Repeat Cylinders

- repeat `1`+: `q == 23 mod 2^7`
- repeat `2`+: `q == 6679 mod 2^14`
- repeat `3`+: `q == 55831 mod 2^21`
- repeat `4`+: `q == 234936855 mod 2^28`

### Finite-depth Counts

- repeat `1`+: count `65536`, exit after this repeat `65024`
- repeat `2`+: count `512`, exit after this repeat `508`
- repeat `3`+: count `4`, exit after this repeat `4`
- repeat `4`+: count `0`, exit after this repeat `0`
