# Frontier Strata for `n = 64q - 1`

- q-depth: `20`
- q=0 handling: q residue 0 is represented by q = 2**q_depth for burst variables
- status counts: `{'already_cube_covered': 4768, 'residual_certified': 416096, 'unknown': 627712}`

## By t

- `t=0`, `a=6`: count `524288`, unknown `242688` (46.2891%), burst escapes `65536`, returns `16383`
- `t=1`, `a=7`: count `262144`, unknown `161792` (61.7188%), burst escapes `16384`, returns `8191`
- `t=2`, `a=8`: count `131072`, unknown `100352` (76.5625%), burst escapes `8192`, returns `4096`
- `t=3`, `a=9`: count `65536`, unknown `58368` (89.0625%), burst escapes `2048`, returns `2048`
- `t=4`, `a=10`: count `32768`, unknown `31744` (96.8750%), burst escapes `1024`, returns `1025`
- `t=5`, `a=11`: count `16384`, unknown `16384` (100.0000%), burst escapes `256`, returns `511`
- `t=6`, `a=12`: count `8192`, unknown `8192` (100.0000%), burst escapes `64`, returns `256`
- `t=7`, `a=13`: count `4096`, unknown `4096` (100.0000%), burst escapes `32`, returns `128`
- `t=8`, `a=14`: count `2048`, unknown `2048` (100.0000%), burst escapes `8`, returns `63`
- `t=9`, `a=15`: count `1024`, unknown `1024` (100.0000%), burst escapes `4`, returns `31`
- `t=10`, `a=16`: count `512`, unknown `512` (100.0000%), burst escapes `1`, returns `16`
- `t=11`, `a=17`: count `256`, unknown `256` (100.0000%), burst escapes `0`, returns `8`
- `t=12`, `a=18`: count `128`, unknown `128` (100.0000%), burst escapes `1`, returns `3`
- `t=13`, `a=19`: count `64`, unknown `64` (100.0000%), burst escapes `1`, returns `2`
- `t=14`, `a=20`: count `32`, unknown `32` (100.0000%), burst escapes `0`, returns `1`
- `t=15`, `a=21`: count `16`, unknown `16` (100.0000%), burst escapes `0`, returns `1`
- `t=16`, `a=22`: count `8`, unknown `8` (100.0000%), burst escapes `0`, returns `0`
- `t=17`, `a=23`: count `4`, unknown `4` (100.0000%), burst escapes `0`, returns `0`
- `t=18`, `a=24`: count `2`, unknown `2` (100.0000%), burst escapes `0`, returns `0`
- `t=19`, `a=25`: count `1`, unknown `1` (100.0000%), burst escapes `0`, returns `0`
- `t=20`, `a=26`: count `1`, unknown `1` (100.0000%), burst escapes `0`, returns `0`

## Top Unresolved Buckets

- `t=0`, `a=6`, `h=1`: unknown `161792` (61.7188%)
- `t=1`, `a=7`, `h=1`: unknown `100352` (76.5625%)
- `t=0`, `a=6`, `h=2`: unknown `61440` (46.8750%)
- `t=2`, `a=8`, `h=1`: unknown `58368` (89.0625%)
- `t=1`, `a=7`, `h=2`: unknown `41984` (64.0625%)
- `t=3`, `a=9`, `h=1`: unknown `31744` (96.8750%)
- `t=2`, `a=8`, `h=2`: unknown `26624` (81.2500%)
- `t=0`, `a=6`, `h=3`: unknown `19456` (29.6875%)
- `t=4`, `a=10`, `h=1`: unknown `16384` (100.0000%)
- `t=1`, `a=7`, `h=3`: unknown `15360` (46.8750%)
- `t=3`, `a=9`, `h=2`: unknown `15360` (93.7500%)
- `t=2`, `a=8`, `h=3`: unknown `11264` (68.7500%)
- `t=5`, `a=11`, `h=1`: unknown `8192` (100.0000%)
- `t=4`, `a=10`, `h=2`: unknown `8192` (100.0000%)
- `t=3`, `a=9`, `h=3`: unknown `7168` (87.5000%)
- `t=4`, `a=10`, `h=3`: unknown `4096` (100.0000%)
- `t=2`, `a=8`, `h=4`: unknown `4096` (50.0000%)
- `t=1`, `a=7`, `h=4`: unknown `4096` (25.0000%)
- `t=6`, `a=12`, `h=1`: unknown `4096` (100.0000%)
- `t=5`, `a=11`, `h=2`: unknown `4096` (100.0000%)
- `t=3`, `a=9`, `h=4`: unknown `3072` (75.0000%)
- `t=7`, `a=13`, `h=1`: unknown `2048` (100.0000%)
- `t=4`, `a=10`, `h=4`: unknown `2048` (100.0000%)
- `t=6`, `a=12`, `h=2`: unknown `2048` (100.0000%)
- `t=5`, `a=11`, `h=3`: unknown `2048` (100.0000%)
- `t=5`, `a=11`, `h=4`: unknown `1024` (100.0000%)
- `t=6`, `a=12`, `h=3`: unknown `1024` (100.0000%)
- `t=8`, `a=14`, `h=1`: unknown `1024` (100.0000%)
- `t=3`, `a=9`, `h=5`: unknown `1024` (50.0000%)
- `t=7`, `a=13`, `h=2`: unknown `1024` (100.0000%)

## Top Recursive Unknown States

- `unknown:t=0:a=6:h=1:post64=41:q64=11:return=0`: `8192` (1.3051% of unknown)
- `unknown:t=0:a=6:h=1:post64=27:q64=15:return=0`: `8192` (1.3051% of unknown)
- `unknown:t=0:a=6:h=1:post64=63:q64=23:return=1`: `8192` (1.3051% of unknown)
- `unknown:t=0:a=6:h=1:post64=31:q64=23:return=0`: `8192` (1.3051% of unknown)
- `unknown:t=0:a=6:h=1:post64=39:q64=39:return=0`: `8192` (1.3051% of unknown)
- `unknown:t=0:a=6:h=1:post64=47:q64=55:return=0`: `8192` (1.3051% of unknown)
- `unknown:t=0:a=6:h=1:post64=55:q64=7:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=57:q64=43:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=43:q64=47:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=15:q64=55:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=59:q64=15:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=61:q64=51:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=19:q64=63:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=7:q64=39:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=9:q64=11:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=0:a=6:h=1:post64=33:q64=59:return=0`: `7168` (1.1419% of unknown)
- `unknown:t=1:a=7:h=1:post64=27:q64=10:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=1:a=7:h=1:post64=7:q64=26:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=1:a=7:h=1:post64=9:q64=50:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=0:a=6:h=1:post64=29:q64=51:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=1:a=7:h=1:post64=31:q64=58:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=0:a=6:h=1:post64=1:q64=59:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=0:a=6:h=2:post64=31:q64=5:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=0:a=6:h=1:post64=23:q64=7:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=1:a=7:h=1:post64=33:q64=18:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=1:a=7:h=1:post64=55:q64=26:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=0:a=6:h=1:post64=3:q64=31:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=0:a=6:h=2:post64=39:q64=37:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=0:a=6:h=1:post64=25:q64=43:return=0`: `4096` (0.6525% of unknown)
- `unknown:t=1:a=7:h=1:post64=57:q64=50:return=0`: `4096` (0.6525% of unknown)
