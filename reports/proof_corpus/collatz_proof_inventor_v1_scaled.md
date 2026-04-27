# Proof-Inventor Corpus

- status: `SCALED_PROOF_CORPUS_BUILT`
- examples: `100000`
- task counts: `{'collatz_structure_to_proof_dsl': 64755, 'successor_family_to_debt_verifier_target': 164, 'rank_repair_from_counterexample': 1, 'mixed_modulus_debt_transition_trace': 1312, 'mixed_modulus_debt_blocker_to_repair_action': 4, 'affine_height_proof_dsl': 80, 'verifier_feedback_to_repair_action': 17677, 'strict_theorem_repair': 1, 'preflight_blocker_to_repair_action': 6, 'general_formal_proof_pattern': 16000}`
- source counts: `{'high_parent_bypass': 329, 'mixed_modulus_debt_verifier': 1316, 'cycle_mining': 80, 'proof_attempt_replay': 95, 'strict_theorem_verifier': 1, 'run_preflight': 6, 'formal_proof_seed': 6, 'synthetic_formal_proof': 15994, 'synthetic_high_parent_successor': 64591, 'synthetic_verifier_replay': 17582}`
- label counts: `{'PROPOSE_MIXED_MODULUS_STATE': 32460, 'TRY_MIXED_MODULUS_DEBT_VERIFIER': 32478, 'PROPOSE_DEBT_RANK': 3201, 'VERIFY_MIXED_MODULUS_DEBT_TRANSITION': 7300, 'REPAIR_MIXED_MODULUS_DEBT_RANK': 5736, 'PROVE_UNBOUNDED_VALUATION_CLOSURE': 1466, 'MAP_MIXED_STATE_TO_GLOBAL_OBLIGATION': 1, 'TRY_SCC_RANKING': 81, 'REFINE_LOCAL_FRONTIER_CERTIFICATES': 19, 'PROVE_GLOBAL_PARENT_TRANSITION_TEMPLATE': 19, 'PROVE_PARAMETRIC_LIFTING_LEMMA': 19, 'STRICT_THEOREM_COMPILER_REPAIR': 21, 'SELF_CORRECT_PROOF_DSL': 7601, 'PROPOSE_PROOF_DSL': 9598}`
- verifier status counts: `{'PASS': 39760, 'REDUCED': 32459, 'FAIL_REQUIRES_REPAIR': 5121, 'FAIL_REQUIRES_DEBT_RANK': 614, 'FAIL': 5966, 'PROVED_HEIGHT_DECREASE_ON_REPEAT': 80, 'PROOF_PATTERN': 16000}`
- stream mix: `{'general_formal_proof': 16000, 'collatz_structural': 65000, 'verifier_replay': 19000}`

## Scaling Target

predict typed proof programs and repair actions from exact mathematical state plus verifier feedback
