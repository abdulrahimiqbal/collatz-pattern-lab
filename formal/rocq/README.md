# Rocq Formalization Status

`CollatzProofCandidate.v` is an axiom-free Rocq/Coq theorem-bridge file:

```text
positive iterates + descent theorem -> every positive integer reaches 1
```

Rocq/Coq is not installed in this local environment, so this file has not been
machine-checked here. It is written against standard Coq/Rocq libraries:

```bash
coqc formal/rocq/CollatzProofCandidate.v
# or, with newer Rocq tooling:
rocq compile formal/rocq/CollatzProofCandidate.v
```

The finite RUN-024 certificate replay still has to be ported to Rocq before
this becomes a full Rocq proof of Collatz.
