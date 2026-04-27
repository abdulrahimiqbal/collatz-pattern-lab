# RUN-009 Preflight

- status: `NOT_READY_FOR_RUN9`
- ready for RUN-009: `False`
- local smoke ready: `False`
- blocking checks: `['trained_on_same_corpus_size', 'proof_model_is_scaling_target_not_bootstrap']`
- thresholds: `{'min_examples': 100000, 'min_general_formal': 10000, 'min_collatz_structural': 50000, 'min_verifier_replay': 10000, 'allow_bootstrap_model': False}`
- observed: `{'corpus_examples': 100000, 'jsonl_rows': 100000, 'stream_mix': {'collatz_structural': 65000, 'general_formal_proof': 16000, 'verifier_replay': 19000}, 'model_kind': 'Tfidf char n-gram retrieval + LogisticRegression task/action/outcome heads', 'model_status': 'TRAINED_BOOTSTRAP_COLLATZ_PROOF_INVENTOR', 'top_actions': ['TRY_MIXED_MODULUS_DEBT_VERIFIER', 'VERIFY_MIXED_MODULUS_DEBT_TRANSITION', 'REPAIR_MIXED_MODULUS_DEBT_RANK', 'PROPOSE_MIXED_MODULUS_STATE', 'PROPOSE_PROOF_DSL', 'SELF_CORRECT_PROOF_DSL'], 'accepted_claim_count': 1, 'total_claim_count': 4, 'proof_confidence_percent': 0.0}`

## Checks

- `proof_corpus_report_exists`: `PASS`
- `proof_corpus_jsonl_matches_report`: `PASS`
- `proof_corpus_large_enough_for_scaling_run`: `PASS`
- `general_formal_proof_stream_large_enough`: `PASS`
- `collatz_structural_stream_large_enough`: `PASS`
- `verifier_replay_stream_large_enough`: `PASS`
- `proof_inventor_training_report_exists`: `PASS`
- `proof_inventor_checkpoint_exists`: `PASS`
- `trained_on_same_corpus_size`: `FAIL`
- `proof_model_is_scaling_target_not_bootstrap`: `FAIL`
- `all_training_streams_present`: `PASS`
- `dry_run_proposal_exists`: `PASS`
- `dry_run_verification_exists`: `PASS`
- `proof_confidence_is_verifier_gated`: `PASS`
- `proof_candidate_has_verifier_accepted_claim`: `PASS`
- `model_targets_current_math_blocker`: `PASS`
- `exact_high_parent_successor_family_available`: `PASS`
- `mixed_modulus_debt_verifier_available`: `PASS`

## Next Step

Do not treat RUN-009 as scaling-law-ready: expand proof data, train a non-bootstrap proof model, and add the mixed-modulus debt verifier before the serious run.
