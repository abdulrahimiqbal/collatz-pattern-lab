# RUN-021 Strict Verifier Replay Hardening

- audit status: `PASS_FOR_VERIFIER_SOUNDNESS`
- strict verifier: `FAIL`
- verifier status: `FAIL`
- proof confidence: `0.0`%

RUN-021 succeeds by making the former strict PASS fail soundly unless every accepted node is backed by a replayable certificate payload.

## Root Unsound Certificates

- `S4_LIFT` (135): sample-only transition certificate; fix: attach and replay an exact HIGH_PARENT_SUCCESSOR_EXACT symbolic parent-transition payload
- `S6_LEMMA` (28): status-id lemma acceptance; fix: replace status/certificate identifiers with a replayable S6 lemma proof_payload
- `STRICT_THEOREM_TOP_LEVEL` (5): closed graph lacks explicit universal entry, coverage, transition, ranking, and descent certificates; fix: provide replayable top-level theorem certificates with hashes and proof payloads

## Strict Errors

- unknown obligations remain: 5
- coverage is not universal over all parent states P_a
- top-level certificate universal_entry_certificate does not replay
- top-level certificate parent_state_coverage_certificate does not replay
- top-level certificate transition_soundness_certificate does not replay
- top-level certificate well_founded_ranking_certificate does not replay
- top-level certificate descent_implication_certificate does not replay

## Source Run Downgrade

- source verifier status: `UNSOUND_PASS`
- source proof confidence: `0.0`
- reason: strict verifier PASS was downgraded because RUN-020 audit failed
