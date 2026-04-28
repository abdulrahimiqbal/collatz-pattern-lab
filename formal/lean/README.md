# Lean Formalization Status

`CollatzProofCandidate.lean` is a postulate-free Lean 4 file for the theorem bridge:

```text
descent theorem -> every positive integer reaches 1
```

It does not yet formalize the 485-node replayed RUN-024 certificate graph. The
remaining work for a full Lean proof is to port the strict replay checker and
all certificate payload semantics into Lean, then prove `DescentTheorem`.

RUN-027 modules live under `formal/lean/Collatz/`.

Local checks:

```bash
lake build Collatz.Run024Data
lake env lean formal/lean/CollatzProofCandidate.lean
```

Current RUN-027 milestone: `S4_CHECKER_PORTED`.

Lean now typechecks generated RUN-024 literal data and proves all 135 generated
S4 parent-transition certificates satisfy the formal S4 arithmetic consistency
claim in `Collatz.Checkers`.  S6 and top-level certificate soundness are still
explicit formalization gaps.
