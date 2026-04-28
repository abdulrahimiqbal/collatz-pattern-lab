# RUN-047 Missing Formalization Gaps

Status: `FORMALIZATION_GAP`.

Lean now inspects the final RUN-045/RUN-046 certificate payloads and proves:

- `run046_s3_sound : AllS3DebtClaims run046S3DebtCerts`
- `run046_s4_sound : AllS4ParentMapClaims run046S4ParentMapCerts`
- `run046_s6_sound : AllS6LemmaClaims run046S6LemmaCerts`
- `run046_kernel_empty : NaturalViabilityKernelEmpty run046NaturalKernelCert`
- `run046_top_level_sound : TopLevelCertificatesImplyDescent run046TopLevelCerts`

The natural-kernel theorem is a real arithmetic replay: Lean checks the denominator is positive and odd, the numerator is negative, the affine fixed-point equation holds, the lasso denominator is the declared power of two, the multiplier is odd, and no positive natural `q` can satisfy the generated fixed-point equation.

Remaining gaps before a full Lean proof:

- Missing S3 semantic bridge: the checked S3 debt fields are not yet connected to a theorem about actual iterates of `C`.
- Missing S4 semantic bridge: the checked parent-coordinate map arithmetic is not yet connected to actual parent-state transition semantics for all represented natural inputs.
- Missing S6 semantic bridge: the S6 payload dependency checks are structural/replay-consistency checks, not a Lean proof of the coverage, no-escape, induction, and lifting lemmas they name.
- Missing top-level coverage semantics: covered domain intervals are checked for arithmetic well-formedness, but Lean does not yet prove they cover every positive odd input entering a parent state.
- Missing well-foundedness proof bridge: ranked edge decreases and guarded SCC metadata are checked, but Lean does not yet derive absence of infinite non-descending Collatz paths.
- Missing descent theorem bridge: `TopLevelCertificatesImplyDescent run046TopLevelCerts` is a checked certificate-consistency claim, not `DescentTheorem`.

Because of these gaps, `run046_descent : DescentTheorem` and `collatz_conjecture : CollatzConjecture` are intentionally not declared.
