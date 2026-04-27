# Top-Bucket Closure Audit

- status: `TOP_BUCKET_CLOSURE_AUDIT_NOT_COLLATZ_PROOF`
- selected progress: `40.13671875`%
- baseline certified q-classes: `420864`
- denominator q-classes: `1048576`
- target q-classes: `533504`
- closed target q-classes: `0`
- target progress if all top 10 closed: `91.015625`%

This audit does not count a bucket as closed unless every child branch has an exact closure certificate.

## Bucket Results

### unresolved_bucket:t=0:a=6:h=1

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `161792`
- split matches weighted report: `True`
- burst affine: `A=729`, `D=128`, `A-D=601`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 5, 'REDUCED_BY_HEIGHT_RANKED_SELF_RETURN': 1}`

### unresolved_bucket:t=1:a=7:h=1

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `100352`
- split matches weighted report: `True`
- burst affine: `A=2187`, `D=256`, `A-D=1931`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 6}`

### unresolved_bucket:t=0:a=6:h=2

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `61440`
- split matches weighted report: `True`
- burst affine: `A=729`, `D=256`, `A-D=473`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 5}`

### unresolved_bucket:t=2:a=8:h=1

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `58368`
- split matches weighted report: `True`
- burst affine: `A=6561`, `D=512`, `A-D=6049`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 6}`

### unresolved_bucket:t=1:a=7:h=2

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `41984`
- split matches weighted report: `True`
- burst affine: `A=2187`, `D=512`, `A-D=1675`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 5}`

### unresolved_bucket:t=3:a=9:h=1

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `31744`
- split matches weighted report: `True`
- burst affine: `A=19683`, `D=1024`, `A-D=18659`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 6}`

### unresolved_bucket:t=2:a=8:h=2

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `26624`
- split matches weighted report: `True`
- burst affine: `A=6561`, `D=1024`, `A-D=5537`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 5}`

### unresolved_bucket:t=0:a=6:h=3

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `19456`
- split matches weighted report: `True`
- burst affine: `A=729`, `D=512`, `A-D=217`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 3, 'REDUCED_BY_HEIGHT_RANKED_SELF_RETURN': 1}`

### unresolved_bucket:t=4:a=10:h=1

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `16384`
- split matches weighted report: `True`
- burst affine: `A=59049`, `D=2048`, `A-D=57001`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 6}`

### unresolved_bucket:t=1:a=7:h=3

- status: `NEEDS_DEBT_CARRYING_PARENT_INDUCTION`
- unknown q-classes: `15360`
- split matches weighted report: `True`
- burst affine: `A=2187`, `D=1024`, `A-D=1163`
- child status counts: `{'BLOCKED_BY_UNPAID_ANCESTOR_DEBT': 4}`

## Next Step

Prove a debt-carrying parent-state induction lemma that pays the expansion created by low-h transitions; only then rerun the top-10 closure audit.
