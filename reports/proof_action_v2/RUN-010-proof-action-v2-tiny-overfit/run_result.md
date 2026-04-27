# RUN-010-proof-action-v2-tiny-overfit: Tiny proof-action v2 overfit/replay gate

- created: `2026-04-27T13:30:07Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `100.00%`
- model discovery score: `100.00%`
- checkpoint: `reports/proof_action_v2/RUN-010-proof-action-v2-tiny-overfit/final_checkpoint.pt`

## Scores

- verifier_backed_actions: `100.00%`
- heldout_closure: `100.00%`
- typed_syntax: `100.00%`

## Artifacts

- eval_summary: `reports/proof_action_v2/RUN-010-proof-action-v2-tiny-overfit/eval_summary.json`
- generated_actions: `reports/proof_action_v2/RUN-010-proof-action-v2-tiny-overfit/generated_actions.jsonl`
- proof_action_attempt: `reports/proof_action_v2/RUN-010-proof-action-v2-tiny-overfit/proof_action_attempt.json`
- verifier_checked_actions: `reports/proof_action_v2/RUN-010-proof-action-v2-tiny-overfit/verifier_checked_actions.jsonl`

## Proof Action Evaluation

- syntax_valid_rate: `1.0`
- action_parse_rate: `1.0`
- top1_verifier_accept_rate: `1.0`
- top5_verifier_accept_rate: `1.0`
- trace_replay_close_rate: `1.0`
- heldout_obligation_close_rate: `1.0`
- strict_theorem_verifier_result: `FAIL`
- go_no_go: `NO-GO`

## Blocking Obligations

- `S3/S4 challenge action gate`

## Next Step

Fix the smallest failing proof-action gate before scaling the big model.

## Commands

- `python -m collatz_lab.proof_action_model train --config configs/collatz_proof_action_v2_tiny_overfit.yaml`
- `python -m collatz_lab.proof_action_eval --config configs/collatz_proof_action_v2_tiny_overfit.yaml`

## Notes

- Strict theorem confidence is verifier-gated and remains 0 unless the theorem verifier passes.
