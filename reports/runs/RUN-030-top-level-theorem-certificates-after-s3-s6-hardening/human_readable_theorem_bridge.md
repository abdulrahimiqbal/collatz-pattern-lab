# RUN-030 Human-Readable Theorem Bridge

- theorem: `forall n > 1 exists k >= 1 such that C^k(n) < n`
- descent implication: `forall n > 1 exists t >= 0 such that C^t(n) = 1`
- strict verifier: `FAIL`
- top-level certificates replayed: `3/5`

RUN-030 accepts only manifest-backed replay of:

1. universal arithmetic entry into even descent or odd parent states
2. parent-state coverage including the final P26 residual parent certificate
3. exact S3/S4/S6 transition soundness from certificate_store payloads
4. a well-founded ranking over non-terminal parent-state transitions
5. the explicit strong-induction bridge from descent to convergence

## Current Blocker

The top-level replay is intentionally failing until the reported mathematical blocker is supplied as a replayable certificate.

- `top_level:descent_implication_certificate`: explicit replayable top-level theorem certificate is required; closed proof-action graph is only supporting evidence
- `top_level:well_founded_ranking_certificate`: explicit replayable top-level theorem certificate is required; closed proof-action graph is only supporting evidence
