# RUN-007 Preflight

- status: `NOT_READY_FOR_RUN7`
- ready for RUN-007: `False`
- diagnostic run allowed: `False`
- force diagnostic run: `False`
- blocking checks: `['debt_induction_gate_ready', 'variable_depth_certificate_ready', 'symbolic_high_parent_branches_closed', 'mixed_modulus_debt_verifier_ready', 'selected_attempt_has_new_exact_evidence']`

## Checks

- `proof_attempt_beam_exists`: `PASS`
- `per_run_attempt_ledger_updated`: `PASS`
- `central_attempt_ledger_updated`: `PASS`
- `proof_replay_training_ready`: `PASS`
- `debt_induction_gate_ready`: `FAIL`
- `variable_depth_certificate_ready`: `FAIL`
- `symbolic_high_parent_branch_executor_built`: `PASS`
- `symbolic_high_parent_branches_closed`: `FAIL`
- `mixed_modulus_high_parent_bypass_built`: `PASS`
- `mixed_modulus_debt_verifier_ready`: `FAIL`
- `selected_attempt_has_new_exact_evidence`: `FAIL`

## Next Step

Do not launch RUN-007; fix the failing required preflight checks first.
