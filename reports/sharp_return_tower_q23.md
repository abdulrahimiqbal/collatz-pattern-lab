# Sharp Return Subsystem

- status: `PROVED_TRANSITION_ONLY_AND_PROVED_POTENTIAL_DECREASE`
- domain: `q == 23 mod 128`
- transition: `R(q) = (729*q + 1) / 128`
- Collatz statement: `C^13(64*q-1) = 64*R(q)-1`
- height: `J(q)=v2(601*q+1)`
- identity: `J(R(q))=J(q)-7`

## Tower Counts

- q-depth: `23`
- sharp branch count: `65536`
- guaranteed exit after `1` return(s): `65024`
- guaranteed exit after `2` return(s): `508`
- needs deeper bits after at least `3` return(s): `4`
- forever status: `IMPOSSIBLE_FOR_POSITIVE_INTEGER`

## Cylinders

- at least `1` return(s): `q == 23 mod 2^7` count `65536`
- at least `2` return(s): `q == 6679 mod 2^14` count `512`
- at least `3` return(s): `q == 55831 mod 2^21` count `4`

## Potential

- status: `PROVED_POTENTIAL_DECREASE`
- proof: `n'/n < 6 for positive q` and `6^8 < 2^21`

## Ancestor Debt Example

- image local family: `q' == 9 mod 16`
- preimage: `q == 791 mod 2^11`
- ancestor status: `ANCESTOR_DEBT_UNPAID`
- debt paid: `False`
