# RUN-026 Technical Proof Note

## Status

This repository contains a clean-replay, verifier-passing Collatz proof
candidate at tag `proof-candidate-run024`, commit
`507542eb8b1d77fa97f8d778548b6320289eea0f`.

This note should not be read as a claim that Collatz has been externally
proved.  The correct claim is narrower:

> We have a clean-replay, verifier-passing Collatz proof candidate in our
> repository.

RUN-025 established that the Python replay layer reproduces the proof candidate
from committed artifacts, rejects adversarial mutations, and checks that the
top-level theorem statement is exactly the Collatz descent theorem plus the
standard induction bridge to convergence.

## Theorem Statement

The machine-checked proof object states the descent theorem:

```text
forall n > 1 exists k >= 1 such that C^k(n) < n
```

where `C` is the usual Collatz map on positive integers:

```text
C(n) = n / 2        if n is even
C(n) = 3n + 1      if n is odd
```

The proof object also states the standard consequence:

```text
forall n > 1 exists t >= 0 such that C^t(n) = 1
```

The second statement follows from the first by strong induction on `n`.

## RUN-024 Proof Object

RUN-024 introduced five replayed top-level certificates:

1. `universal_entry_certificate`
2. `parent_state_coverage_certificate`
3. `transition_soundness_certificate`
4. `well_founded_ranking_certificate`
5. `descent_implication_certificate`

The strict verifier returns PASS only when all five replay, all S4 transition
certificates replay, all S6 lemma payloads replay, manifest hashes match, and
no graph obligations remain open.

The frozen proof object is:

```text
certificate_store/run024_final_proof_object.json
```

The root manifest replay command is:

```bash
python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json
```

## RUN-025 Audit Results

RUN-025 generated:

```text
reports/runs/RUN-025-proof-candidate-external-audit-package/
```

It passed:

- clean clone replay
- manifest-only replay after deleting generated folders
- network-disabled replay
- certificate hash mutation rejection
- top-level theorem mutation rejection
- S4 transition certificate removal rejection
- S6 lemma certificate removal rejection
- ranking certificate removal rejection
- exact theorem statement check
- exact descent implication check

The RUN-025 result is:

```text
AUDIT_PASS: proof candidate ready for external review
```

## Lean Formalization

The Lean file is:

```text
formal/lean/CollatzProofCandidate.lean
```

It defines the Collatz map, iterates, reachability of `1`, and the descent
theorem.  It proves, without axioms or `sorry`, that the descent theorem implies
Collatz convergence:

```lean
theorem descent_implies_convergence
    (descent : DescentTheorem) :
    forall n : Nat, n > 0 -> ReachesOne n
```

It also proves that Collatz iterates preserve positivity.  The local check is:

```bash
lean formal/lean/CollatzProofCandidate.lean
```

This Lean file does not yet prove `DescentTheorem`; it proves the theorem bridge
that turns a formalized descent theorem into full convergence.

## Rocq Formalization

The Rocq/Coq file is:

```text
formal/rocq/CollatzProofCandidate.v
```

It proves the analogous theorem bridge:

```coq
Theorem descent_implies_convergence :
  positive_iterates ->
  descent_theorem ->
  forall n : nat, n > 0 -> reaches_one n.
```

Rocq/Coq is not installed in this local environment, so the file has not been
checked here.  It is written against standard libraries and should be checked
with:

```bash
coqc formal/rocq/CollatzProofCandidate.v
# or
rocq compile formal/rocq/CollatzProofCandidate.v
```

## What Is Still Missing For A Full Lean/Rocq Proof

The full proof assistant port is not complete.

The missing step is to port the Python strict verifier and the 485-node
certificate graph into Lean and Rocq.  In particular, a full formal proof must
replace each Python replay check with proof-assistant definitions and theorems:

- exact S4 `HIGH_PARENT_SUCCESSOR_EXACT` transition replay
- exact S6 lemma payload replay
- residual parent certificate replay
- coverage certificate replay
- no-escape certificate replay
- top-level coverage, transition soundness, and ranking certificates
- canonical hash or artifact-integrity story inside or outside the assistant

Only after those certificate semantics are formalized can Lean/Rocq prove
`DescentTheorem` rather than assuming it as an input to the theorem bridge.

## Recommended Next Formalization Run

The next honest step is:

```text
RUN-027-proof-assistant-certificate-replay-port
```

Goal:

Port the strict replay checker for the frozen RUN-024 certificate graph into
Lean first, then Rocq.  The target theorem should be:

```text
run024_certificates_replay -> DescentTheorem
```

combined with the already-formalized theorem bridge:

```text
DescentTheorem -> Collatz convergence
```

Until that port exists, the repository has a verifier-passing proof candidate
and a formalized proof bridge, not a complete Lean/Rocq proof of Collatz.
