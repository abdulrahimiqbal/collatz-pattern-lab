# Collatz Proof-Discovery Runs

| Run | Title | Verifier | Proof Confidence | Proof Progress | Discovery Score | Next Step |
| --- | --- | --- | ---: | ---: | ---: | --- |
| RUN-014-proof-action-v2-hard-retrain-small-a100 | Proof-action v2 hard-curriculum retrain small A100 | FAIL | 0.00% | 0.00% | 5.71% | Do not launch big model; weakest layer: raw model proposals weak on hard frontier gate-progress choices. |
| RUN-013-proof-action-v2-hard-trace-mining | Proof-action v2 hard trace mining | FAIL | 0.00% | 0.00% | 10.00% | Use the mined hard traces in RUN-014 small retraining, then rerun the frontier benchmark; do not launch the big model yet. |
| RUN-012-proof-action-v2-frontier-search-small-a100 | Proof-action v2 frontier search diagnostics using RUN-011 checkpoint | FAIL | 0.00% | 87.50% | 65.50% | NO-GO for big: raw frontier proposals are syntactically valid, but budgeted search does not beat random at 1000 calls. |
| RUN-011-proof-action-v2-ranker-small-a100 | Proof-action v2 small A100 with closed-vs-reduced ranker | FAIL | 0.00% | 100.00% | 100.00% | NO-GO for big: top-1/top-5 equality is saturation, but random-baseline lift is only 1.77x and top-5 close lift is 0. |
| RUN-010-proof-action-v2-small-a100 | Proof-action v2 small A100 interface validation | FAIL | 0.00% | 80.27% | 8.65% | Proof-action interface works, but do not launch the big model until the missed small-run gates pass. |
| RUN-009-proof-transformer-a100-partial | Partial A100 proof-transformer evaluation stopped at 70 percent | FAIL | 0.00% | 26.05% | 0.00% | Do not continue blind GPU scaling. Improve proof-targeted objectives and symbolic parsing; the partial Transformer must first generate verifier-actionable mixed-modulus debt-rank claims. |
| RUN-008-proof-dsl-generator | Proof-DSL generator with mixed-modulus proposal | FAIL | 0.00% | 26.05% | 0.00% | Implement the mixed-modulus debt verifier and train the proof model on its PASS/FAIL/repair traces. |
| RUN-007-forced-high-parent-diagnostic | Forced high-parent valuation diagnostic | FAIL | 0.00% | 26.05% | 0.00% | Prove exact global parent-state transition templates; local P6 coverage is not enough. |
| RUN-006-top10-parent-debt-audit | Top-10 parent debt closure audit | FAIL | 0.00% | 26.05% | 0.00% | Prove exact global parent-state transition templates; local P6 coverage is not enough. |
| RUN-005-weighted-parent-state-progress | Weighted parent-state progress accounting | FAIL | 0.00% | 40.14% | 0.00% | Implement exact parent-state transition ranking/induction for the top weighted low-h buckets; closing the top two weighted buckets would exceed 60% finite P6 coverage. |
| RUN-004-obligation-conditioned-proof-search | Obligation-conditioned proof-action search | FAIL | 0.00% | 2.33% | 7.58% | Expand exact proof-action executors for the blocking obligations; do not spend more on local certificate mining until an existing graph node closes. |
| RUN-003-density-max-family-search-step13000 | Density-max family search from step13000 | FAIL | 0.00% | 2.33% | 54.62% | Improve candidate mining and proof-obligation targeting, then rerun the reference pipeline. |
| RUN-002-verifier-guided-compression-v1 | Verifier-guided lifted-family compression v1 | FAIL | 0.00% | 2.33% | 44.57% | Improve candidate mining and proof-obligation targeting, then rerun the reference pipeline. |
| RUN-001-a10g-reference-step3000 | A10G reference checkpoint step 3000 | FAIL | 0.00% | 2.33% | 29.14% | Improve candidate mining and proof-obligation targeting, then rerun the reference pipeline. |
| RUN-000-current-baseline | Current signed multitask baseline | FAIL | 0.00% | 2.33% | 29.78% | Prioritize symbolic compression of verified lifted certificates before spending more on scale. |

## Run Template

- run id:
- model/config:
- data:
- commands:
- checkpoint:
- eval metrics:
- candidate counts:
- verifier result:
- proof attempt:
- proof attempt evaluation:
- proof confidence:
- proof progress:
- model discovery score:
- what worked:
- what failed:
- exact next step:

## Run Details

## RUN-000-current-baseline: Current signed multitask baseline

- created: `2026-04-25T23:44:13Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `2.33%`
- model discovery score: `29.78%`
- checkpoint: `/mnt/collatz/runs/20260424_222430_multitask_base24/checkpoint.pt`

## Scores

- dynamics: `56.25%`
- exact_candidate_verification: `33.33%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `12.39%`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Prioritize symbolic compression of verified lifted certificates before spending more on scale.

## Commands

- `scripts/eval_signed_reference_modal.sh /mnt/collatz/runs/20260424_222430_multitask_base24`
- `scripts/run_signed_reference_analysis.sh /mnt/collatz/runs/20260424_222430_multitask_base24`
- `python -m collatz_lab.proof_verifier --proof-graph reports/proof_graph_latest.json --global-obligations reports/parent_state_global_obligations.json --out reports/collatz_descent_theorem_candidate.json`

## Notes

- Backfilled from existing local and remote_reports artifacts.
- Strict verifier remains the authority; exact lifted leaves do not imply global closure.

## RUN-001-a10g-reference-step3000: A10G reference checkpoint step 3000

- created: `2026-04-26T00:14:38Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `2.33%`
- model discovery score: `29.14%`
- checkpoint: `/mnt/collatz/runs/RUN-001-a10g-reference/checkpoint_step3000.pt`

## Scores

- dynamics: `52.82%`
- exact_candidate_verification: `33.33%`
- certificate_compression: `1.56%`
- verifier_backed_actions: `12.39%`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Improve candidate mining and proof-obligation targeting, then rerun the reference pipeline.

## RUN-002-verifier-guided-compression-v1: Verifier-guided lifted-family compression v1

- created: `2026-04-26T00:27:19Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `2.33%`
- model discovery score: `44.57%`
- checkpoint: `/mnt/collatz/runs/RUN-001-a10g-reference/checkpoint_step3000.pt`

## Scores

- dynamics: `52.82%`
- exact_candidate_verification: `33.33%`
- certificate_compression: `63.28%`
- verifier_backed_actions: `12.39%`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Improve candidate mining and proof-obligation targeting, then rerun the reference pipeline.

## RUN-003-density-max-family-search-step13000: Density-max family search from step13000

- created: `2026-04-26T01:05:09Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `2.33%`
- model discovery score: `54.62%`
- checkpoint: `/mnt/collatz/runs/RUN-001-a10g-reference/checkpoint_step13000.pt`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `100.00%`
- certificate_compression: `73.54%`
- verifier_backed_actions: `12.39%`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Improve candidate mining and proof-obligation targeting, then rerun the reference pipeline.

## RUN-004-obligation-conditioned-proof-search: Obligation-conditioned proof-action search

- created: `2026-04-26T01:30:56Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `2.33%`
- model discovery score: `7.58%`
- checkpoint: `n/a`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `75.76%`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Expand exact proof-action executors for the blocking obligations; do not spend more on local certificate mining until an existing graph node closes.

## RUN-005-weighted-parent-state-progress: Weighted parent-state progress accounting

- created: `2026-04-26T01:48:12Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `40.14%`
- model discovery score: `0.00%`
- checkpoint: `n/a`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `0.00%`

## Proof Progress Breakdown

- selected metric: `weighted_p6_finite_frontier_coverage`
- selected numerator: `420864`
- selected denominator: `1048576`
- selected source: `reports/residual_frontier_63mod64_q20.json`
- selected status: `finite_depth_diagnostic_not_global_proof`
- strict graph comparator: `10` / `429` = `2.33%`
- strict graph source: `reports/proof_graph_latest.json`
- canonicalized graph comparator: `10` / `142` = `7.04%`
- duplicate graph groups: `105`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Implement exact parent-state transition ranking/induction for the top weighted low-h buckets; closing the top two weighted buckets would exceed 60% finite P6 coverage.

## RUN-006-top10-parent-debt-audit: Top-10 parent debt closure audit

- created: `2026-04-26T13:30:43Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `26.05%`
- model discovery score: `0.00%`
- checkpoint: `n/a`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `0.00%`

## Proof Progress Breakdown

- selected metric: `evaluated_proof_attempt_weighted_gate_score`
- selected numerator: `26.0546875`
- selected denominator: `100.0`
- selected source: `proof_attempt.json`
- selected status: `proof_attempt_evaluation_not_proof_confidence`

## Proof Attempt Evaluation

- metric: `evaluated_proof_attempt_weighted_gate_score`
- verified weight: `26.0546875` / `100.0`
- blocking steps: `['S2-p6-local-frontier', 'S3-global-parent-transitions', 'S4-parametric-lifting', 'S5-debt-induction', 'S6-strict-theorem-verifier']`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Prove exact global parent-state transition templates; local P6 coverage is not enough.

## RUN-007-forced-high-parent-diagnostic: Forced high-parent valuation diagnostic

- created: `2026-04-26T14:38:34Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `26.05%`
- model discovery score: `0.00%`
- checkpoint: `n/a`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `0.00%`

## Artifacts

- central_proof_attempts_log: `proof_attempts.jsonl`
- proof_attempt: `reports/runs/RUN-007-forced-high-parent-diagnostic/proof_attempt.json`
- proof_attempt_search: `reports/runs/RUN-007-forced-high-parent-diagnostic/proof_attempt_search.json`
- proof_attempts_log: `reports/runs/RUN-007-forced-high-parent-diagnostic/proof_attempts.jsonl`
- proof_evaluation: `reports/runs/RUN-007-forced-high-parent-diagnostic/proof_evaluation.json`

## Proof Progress Breakdown

- selected metric: `evaluated_proof_attempt_weighted_gate_score`
- selected numerator: `26.0546875`
- selected denominator: `100.0`
- selected source: `proof_attempt.json`
- selected status: `proof_attempt_evaluation_not_proof_confidence`

## Proof Attempt Evaluation

- metric: `evaluated_proof_attempt_weighted_gate_score`
- verified weight: `26.0546875` / `100.0`
- blocking steps: `['S3-global-parent-transitions', 'S4-parametric-lifting', 'S5-debt-induction', 'S2-p6-local-frontier', 'S6-strict-theorem-verifier']`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Prove exact global parent-state transition templates; local P6 coverage is not enough.

## RUN-008-proof-dsl-generator: Proof-DSL generator with mixed-modulus proposal

- created: `2026-04-26T19:05:39Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `26.05%`
- model discovery score: `0.00%`
- checkpoint: `reports/runs/RUN-008-proof-dsl-generator/proof_dsl_model.pkl`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `0.00%`

## Artifacts

- central_proof_attempts_log: `proof_attempts.jsonl`
- proof_attempt: `reports/runs/RUN-008-proof-dsl-generator/proof_attempt.json`
- proof_attempts_log: `reports/runs/RUN-008-proof-dsl-generator/proof_attempts.jsonl`
- proof_evaluation: `reports/runs/RUN-008-proof-dsl-generator/proof_evaluation.json`

## Proof Progress Breakdown

- selected metric: `evaluated_proof_attempt_weighted_gate_score`
- selected numerator: `26.0546875`
- selected denominator: `100.0`
- selected source: `proof_attempt.json`
- selected status: `proof_attempt_evaluation_not_proof_confidence`

## Proof Attempt Evaluation

- metric: `evaluated_proof_attempt_weighted_gate_score`
- verified weight: `26.0546875` / `100.0`
- blocking steps: `['S2-p6-local-frontier', 'S3-global-parent-transitions', 'S4-parametric-lifting', 'S5-debt-induction', 'S6-strict-theorem-verifier']`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Implement the mixed-modulus debt verifier and train the proof model on its PASS/FAIL/repair traces.

## RUN-009-proof-transformer-a100-partial: Partial A100 proof-transformer evaluation stopped at 70 percent

- created: `2026-04-27T11:53:00Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `26.05%`
- model discovery score: `0.00%`
- checkpoint: `/mnt/collatz/reports/proof_transformer/RUN-009-proof-transformer-a100/checkpoint.pt`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `0.00%`

## Artifacts

- central_proof_attempts_log: `proof_attempts.jsonl`
- model_proof_proposal: `reports/runs/RUN-009-proof-transformer-a100-partial/model_proof_proposal.json`
- model_proof_verification: `reports/runs/RUN-009-proof-transformer-a100-partial/model_proof_verification.json`
- proof_attempt: `reports/runs/RUN-009-proof-transformer-a100-partial/proof_attempt.json`
- proof_attempts_log: `reports/runs/RUN-009-proof-transformer-a100-partial/proof_attempts.jsonl`
- proof_evaluation: `reports/runs/RUN-009-proof-transformer-a100-partial/proof_evaluation.json`

## Proof Progress Breakdown

- selected metric: `evaluated_proof_attempt_weighted_gate_score`
- selected numerator: `26.0546875`
- selected denominator: `100.0`
- selected source: `proof_attempt.json`
- selected status: `proof_attempt_evaluation_not_proof_confidence`

## Proof Attempt Evaluation

- metric: `evaluated_proof_attempt_weighted_gate_score`
- verified weight: `26.0546875` / `100.0`
- blocking steps: `['S2-p6-local-frontier', 'S3-global-parent-transitions', 'S4-parametric-lifting', 'S5-debt-induction', 'S6-strict-theorem-verifier']`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Do not continue blind GPU scaling. Improve proof-targeted objectives and symbolic parsing; the partial Transformer must first generate verifier-actionable mixed-modulus debt-rank claims.

## RUN-012-proof-action-v2-frontier-search-small-a100: Proof-action v2 frontier search diagnostics

- verifier status: `FAIL`
- proof confidence: `0.00%`
- frontier progress: `87.50%`
- gate delta per 1000 calls: `0.655`
- checkpoint: `remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/final_checkpoint.pt`

## Frontier Eval Build

- total rows: `1129`
- easy_one_step: `25`
- medium_3_to_5_step: `180`
- hard_10_to_30_step: `180`
- trap_states: `160`
- s3_frontier: `220`
- s4_lifting_frontier: `135`
- s6_strict_frontier: `9`
- heldout_modulus_challenge: `220`

## Raw Proposal Evaluation

- raw_model_top1_accept_rate: `1.0`
- raw_model_top5_accept_rate: `1.0`
- raw_model_top10_accept_rate: `1.0`
- raw_model_top1_close_rate: `1.0`
- raw_model_top5_close_rate: `1.0`
- raw_model_top10_close_rate: `1.0`
- raw_model_top5_gate_progress_rate: `0.655`
- raw_mrr_first_gate_progress_action: `0.4778333333333334`
- unique_raw_actions_per_state_mean: `7.549`
- duplicate_raw_action_rate: `0.0`

## Budgeted Search Evaluation

- closure_at_10_calls: `0.875`
- closure_at_100_calls: `0.875`
- closure_at_1000_calls: `0.875`
- closure_at_5000_calls: `0.875`
- improvement_vs_random_at_1000_calls: `1.0`
- improvement_vs_heuristic_at_1000_calls: `1.0`
- dead_end_rate: `0.125`
- trap_state_success_rate: `1.0`
- trap_state_dead_end_rate: `0.0`
- random_trap_state_dead_end_rate: `0.8709677419354839`
- s3_gate_delta_per_1000_calls: `0.354`
- s4_gate_delta_per_1000_calls: `0.301`
- s6_gate_delta_per_1000_calls: `0.0`
- go_no_go: `NO-GO`

## Leakage

- exact_state_hash_overlap: `0`
- exact_action_overlap: `3`
- residue_overlap: `6`
- modulus_overlap: `0`
- branch_id_overlap: `133`
- lemma_id_overlap: `9`
- near_duplicate_state_rate: `0.3224092116917626`
- near_duplicate_trace_rate: `0.0`

## Artifacts

- frontier_eval_build_summary: `remote_reports/proof_action_v2/RUN-012-proof-action-v2-frontier-search-small-a100/frontier_eval_build_summary.json`
- raw_proposal_eval_summary: `remote_reports/proof_action_v2/RUN-012-proof-action-v2-frontier-search-small-a100/raw_proposal_eval_summary.json`
- budgeted_search_summary: `remote_reports/proof_action_v2/RUN-012-proof-action-v2-frontier-search-small-a100/budgeted_search_summary.json`
- leakage_report: `remote_reports/proof_action_v2/RUN-012-proof-action-v2-frontier-search-small-a100/leakage_report.json`
- baseline_comparison: `remote_reports/proof_action_v2/RUN-012-proof-action-v2-frontier-search-small-a100/baseline_comparison.json`
- frontier_search_traces: `remote_reports/proof_action_v2/RUN-012-proof-action-v2-frontier-search-small-a100/frontier_search_traces.jsonl`

## Next Step

The true next bottleneck is hard-positive frontier data/search benchmarking, not model size. Current search avoids trap dead ends, but the frontier benchmark still gives random and heuristic baselines the same 1000-call closure rate. Before scaling, add deeper nonlocal states where progress requires model-ranked action sequences that random cannot find within budget.

## RUN-011-proof-action-v2-ranker-small-a100: Proof-action v2 small A100 with closed-vs-reduced ranker

- created: `2026-04-27T14:24:31Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `100.00%`
- model discovery score: `100.00%`
- checkpoint: `/mnt/collatz/remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/final_checkpoint.pt`

## Scores

- typed syntax: `100.00%`
- verifier-backed actions: `100.00%`
- heldout closure/reduction: `100.00%`
- random legal-action close rate: `56.45%`
- improvement vs random: `1.77x`

## Artifacts

- proof_action_eval: `remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/eval_summary.json`
- stratified_eval: `remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/stratified_eval_summary.json`
- topk_diversity: `remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/topk_diversity_summary.json`
- ranked_candidates: `remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/ranked_candidates.jsonl`
- proof_attempt: `remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/proof_action_attempt.json`

## Proof Action Evaluation

- syntax_valid_rate: `1.0`
- action_parse_rate: `1.0`
- degenerate_output_rate: `0.0`
- unique_actions_per_state_mean: `5.904296875`
- top1_verifier_accept_rate: `1.0`
- top5_verifier_accept_rate: `1.0`
- top5_accept_lift: `0.0`
- top1_close_rate: `1.0`
- top5_close_rate: `1.0`
- top5_close_lift: `0.0`
- trace_replay_close_rate: `1.0`
- heldout_obligation_close_rate: `1.0`
- S3 accepted actions: `376`
- S4 accepted actions: `306`
- S6 accepted actions: `24`
- S3 closure/reduction actions: `271`
- S4 closure/reduction actions: `204`
- S6 closure/reduction actions: `16`
- strict_theorem_verifier_result: `FAIL`
- go_no_go: `NO-GO`
- top1/top5 diagnosis: `expected saturation: top-1 already accepts nearly every state where top-5 accepts`

## Blocking Obligations

- random legal-action baseline remains too strong for the current candidate pool
- top-5 close lift is `0.0`, so the candidate set does not yet demonstrate search depth beyond top-1

## Next Step

Before any big model, make the held-out evaluation candidate pool non-oracular and harder: score model top-k before verifier bonuses, include syntactically legal rejected/no-progress candidates in the baseline pool, and require top-5 to recover closures missed by top-1.

## RUN-010-proof-action-v2-small-a100: Proof-action v2 small A100 interface validation

- created: `2026-04-27T13:50:31Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `80.27%`
- model discovery score: `8.65%`
- checkpoint: `/mnt/collatz/remote_reports/proof_action_v2/RUN-010-proof-action-v2-small-a100/final_checkpoint.pt`

## Scores

- certificate_compression: `0.00%`
- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- verifier_backed_actions: `86.52%`

## Artifacts

- central_proof_attempts_log: `proof_attempts.jsonl`
- proof_action_eval: `remote_reports/proof_action_v2/RUN-010-proof-action-v2-small-a100/eval_summary.json`
- proof_attempt: `remote_reports/proof_action_v2/RUN-010-proof-action-v2-small-a100/proof_action_attempt.json`
- proof_attempts_log: `remote_reports/proof_action_v2/RUN-010-proof-action-v2-small-a100/proof_attempts.jsonl`

## Proof Action Evaluation

- syntax_valid_rate: `1.0`
- action_parse_rate: `1.0`
- top1_verifier_accept_rate: `0.865234375`
- top5_verifier_accept_rate: `0.865234375`
- trace_replay_close_rate: `0.802734375`
- heldout_obligation_close_rate: `0.802734375`
- strict_theorem_verifier_result: `FAIL`
- go_no_go: `NO-GO`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Proof-action interface works, but do not launch the big model until the missed small-run gates pass.

## RUN-013-proof-action-v2-hard-trace-mining: Proof-action v2 hard trace mining

- created: `2026-04-27T15:44:05Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `0.00%`
- model discovery score: `10.00%`
- checkpoint: `remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/final_checkpoint.pt`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `100.00%`

## Artifacts

- central_proof_attempts_log: `proof_attempts.jsonl`
- proof_action_hard_trace_mining: `remote_reports/proof_action_v2/RUN-013-proof-action-v2-hard-trace-mining/run_result.json`

## Proof Action Hard Trace Mining

- mined_hard_traces_count: `140`
- median_trace_depth: `8.0`
- trace_depth_min: `7`
- trace_depth_max: `12`
- s3_trace_count: `60`
- s4_trace_count: `60`
- s6_trace_count: `20`
- random_success_rate_at_same_budget: `0.0`
- heuristic_success_rate_at_same_budget: `0.0`
- accepted_hard_positive_count: `140`
- exact_state_hash_overlap: `0`
- near_duplicate_trace_rate: `0.0`
- strict_theorem_verifier_result: `FAIL`
- proof_confidence_percent: `0.0`
- go_no_go_run014: `GO`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Use the mined hard traces in RUN-014 small retraining, then rerun the frontier benchmark; do not launch the big model yet.

## RUN-014-proof-action-v2-hard-retrain-small-a100: Proof-action v2 hard-curriculum retrain small A100

- created: `2026-04-27T18:20:48Z`
- verifier status: `FAIL`
- proof confidence: `0.00%`
- proof progress: `0.00%`
- model discovery score: `5.71%`
- checkpoint: `remote_reports/proof_action_v2/RUN-014-proof-action-v2-hard-retrain-small-a100/final_checkpoint.pt`

## Scores

- dynamics: `0.00%`
- exact_candidate_verification: `0.00%`
- certificate_compression: `0.00%`
- verifier_backed_actions: `57.14%`

## Artifacts

- central_proof_attempts_log: `proof_attempts.jsonl`
- proof_action_frontier_search: `remote_reports/proof_action_v2/RUN-014-proof-action-v2-hard-retrain-small-a100/budgeted_search_summary.json`
- proof_action_hard_retrain_eval: `remote_reports/proof_action_v2/RUN-014-proof-action-v2-hard-retrain-small-a100/hard_retrain_combined_eval.json`

## Proof Action Frontier Search

- raw_model_top1_accept_rate: `1.0`
- raw_model_top5_accept_rate: `1.0`
- raw_model_top10_accept_rate: `1.0`
- raw_model_top1_close_rate: `1.0`
- raw_model_top5_close_rate: `1.0`
- raw_model_top10_close_rate: `1.0`
- raw_model_top5_gate_progress_rate: `0.453125`
- raw_mrr_first_gate_progress_action: `0.33367047991071586`
- closure_at_100_calls: `0.893`
- closure_at_1000_calls: `0.893`
- gate_delta_per_1000_calls: `0.6693999999999997`
- s3_gate_delta_per_1000_calls: `0.354`
- s4_gate_delta_per_1000_calls: `0.301`
- s6_gate_delta_per_1000_calls: `0.014400000000000005`
- trap_state_success_rate: `1.0`
- trap_state_dead_end_rate: `0.0`
- improvement_vs_random_at_1000_calls: `1.0`
- improvement_vs_heuristic_at_1000_calls: `1.0`
- strict_theorem_verifier_result: `FAIL`
- go_no_go: `NO-GO`

## Proof Action Hard Retrain

- syntax_valid_rate: `1.0`
- action_parse_rate: `1.0`
- original_eval_regression_vs_RUN011: `0.0`
- raw_top5_gate_progress_rate: `0.453125`
- raw_mrr_first_gate_progress_action: `0.33367047991071586`
- closure_at_1000_calls: `0.893`
- gate_delta_per_1000_calls: `0.6693999999999997`
- s3_gate_delta_per_1000_calls: `0.354`
- s4_gate_delta_per_1000_calls: `0.301`
- s6_gate_delta_per_1000_calls: `0.014400000000000005`
- hard_holdout_closure_at_1000_calls: `0.5714285714285714`
- hard_holdout_improvement_vs_random: `1.0`
- hard_holdout_improvement_vs_heuristic: `1.0`
- s6_blockers_reduced: `18`
- s6_new_accepted_lemmas_not_in_train: `33`
- strict_theorem_verifier: `FAIL`
- proof_confidence: `0.0`
- go_no_go_big: `NO-GO`

## Blocking Obligations

- `P6_q20_finite_frontier_coverage`
- `unresolved_bucket:t=0:a=6:h=1`
- `unresolved_bucket:t=1:a=7:h=1`
- `unresolved_bucket:t=0:a=6:h=2`
- `unresolved_bucket:t=2:a=8:h=1`
- `unresolved_bucket:t=1:a=7:h=2`
- `unresolved_bucket:t=3:a=9:h=1`
- `unresolved_bucket:t=2:a=8:h=2`
- `unresolved_bucket:t=0:a=6:h=3`
- `unresolved_bucket:t=4:a=10:h=1`

## Next Step

Do not launch big model; weakest layer: raw model proposals weak on hard frontier gate-progress choices.

