# AUDIT_FAIL: Exact Unsound Assumptions / Verifier Gaps

RUN-020 verdict: `AUDIT_FAIL`.

The RUN-019 proof candidate is not ready for external review as a proof.  It is ready for external review as a proof-engineering artifact with identified soundness gaps.

## Checklist

A. The theorem statement is really: for every `n > 1`, some Collatz iterate is smaller than `n`.

Status: PASS.

B. That descent theorem implies the full Collatz conjecture by induction.

Status: PASS.

C. Every positive integer is covered by the parent-state framework.

Status: PASS for representation only: even numbers descend immediately; odd numbers can be written as `2^a q - 1`.  FAIL for proof coverage because current universal coverage is inferred from graph closure.

D. The parent residual certificate for P26 is not circular.

Status: PASS structurally.  It depends on RUN-018 graph nodes, not on the RUN-019 parent residual node.  Its dependencies still need independent soundness audit.

E. The strict verifier does not accept graph closure unless every node has a sound mathematical certificate.

Status: FAIL.  A closed proof-action graph is promoted to `UNIVERSAL_PARENT_STATES`; node certificates are not independently replayed as mathematical proof objects.

F. S3/S4/S6 lemmas do not assume the theorem they prove.

Status: FAIL as audited.  The verifier accepts S6 lemma actions from lemma-specific certificate names/statuses, not from a theorem-independent proof replay.

G. No sample checks passed certificate is treated as universal proof unless backed by exact symbolic logic.

Status: FAIL.  `DERIVE_PARENT_TRANSITION` accepts `sample_checks_passed`.

H. No finite-depth diagnostic is treated as infinite coverage.

Status: FAIL.  The proof-action graph is finite, but the strict verifier marks closed graph coverage as universal.

I. The proof reproduces from a clean clone.

Status: FAIL.  The current proof candidate depends on ignored/generated `reports/runs` artifacts and remote checkpoints/Modal volume state.  The audit package includes a reproduction script, but a clean clone does not contain all required proof artifacts by default.

## Minimal Fix Direction

Do not train.  Replace graph-status acceptance with certificate replay:

- each accepted node must carry a machine-checkable mathematical certificate payload;
- sample checks may be diagnostics only;
- finite frontier coverage may not become universal coverage without an explicit universal theorem certificate;
- S6 lemma verification must replay lemma-specific proof objects rather than trusting status fields.
