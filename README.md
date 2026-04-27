# Collatz Pattern Discovery Lab

`collatz-pattern-lab` is a Python/PyTorch research environment for ML-assisted Collatz pattern discovery. It generates exact Collatz-derived datasets, trains small-to-medium neural models locally or on Modal GPUs, probes learned representations, mines candidate mathematical structure, and sends every mathematical candidate through exact verification.

This is not a project to "train a model to prove Collatz." Neural models are hypothesis generators. Candidate residue classes, descent rules, potential functions, hard-case clusters, or symbolic hypotheses must pass the exact verifier before they are treated as mathematical findings.

## Research Goal

Build an ML-assisted research environment for studying Collatz dynamics.

The central research question:

> Can ML find a new representation of Collatz dynamics that is useful for proof search?

Recent transformer work on Collatz-like long-step prediction suggests that models can learn residue-class structure rather than merely memorize examples. Accuracy was strongly affected by numeral base: bases such as 24 and 32 performed much better than poorly aligned bases such as 3 and 11. Error analysis suggested that the difficult part was learning loop/control length rather than elementary arithmetic. This makes Collatz a useful target for representation learning and interpretability.

The broader mathematical target is inspired by the known "almost all" direction. Tao proved that almost all Collatz orbits attain almost bounded values in a logarithmic-density sense, but that still leaves the universal "every integer" gap. This project should focus on exceptional and hard cases, because those are where new structure would matter most.

## Current Status

The package is `collatz_lab`. Modal is configured with a persistent volume named `collatz-pattern-lab` mounted at `/mnt/collatz`.

Recent experiments:

- `v2` base-2 structure learning generalized well after targeted high-valuation fine-tuning.
- Syracuse base-24 next-step prediction learned the 40-bit regime well but did not length-generalize to 48-bit exact outputs.

Key run artifacts:

- v2 fine-tuned checkpoint: `/mnt/collatz/runs/20260424_171902_v2_base2/checkpoint.pt`
- Syracuse base-24 checkpoint: `/mnt/collatz/runs/20260424_185818_syracuse_base24/checkpoint.pt`
- Syracuse train shard: `/mnt/collatz/data/syracuse/base24_bits40_train_1m.parquet`
- Syracuse 40-bit holdout shard: `/mnt/collatz/data/syracuse/base24_bits40_id_eval_100k.parquet`
- Syracuse 48-bit OOD shard: `/mnt/collatz/data/syracuse/base24_bits48_ood_100k.parquet`

Latest Syracuse metrics:

- 40-bit holdout exact sequence accuracy: `0.998730`
- 40-bit holdout token accuracy: `0.999490`
- 48-bit OOD exact sequence accuracy: `0.006710`
- 48-bit OOD token accuracy: `0.790854`

Interpretation: the current Syracuse model is not the final model. It is the first serious dynamics checkpoint. The next target is a single signed reference architecture that combines what has worked so far: LSB-first digit encoding, base 24 or 32, mixed bit-length training, high-valuation and hard-case sampling, negative-cycle examples, and multitask heads for proof-relevant quantities.

## Symbolic residual frontier analysis

The current proof-discovery layer focuses on the hard parent region:

```text
n = 64q - 1
```

The ML model may propose where structure lives, but the model does not prove anything. Exact symbolic families are only mathematical findings when labeled `PROVED_INFINITE_FAMILY`; finite-depth verification is not a universal proof; numeric potential search is a scaffold unless later converted to exact inequalities.

Useful commands:

```bash
pytest

python -m collatz_lab.burst \
  --a-min 6 --a-max 20 \
  --out reports/burst_families_a6_a20.json

python -m collatz_lab.frontier_strata \
  --q-depth 20 \
  --residual-report reports/residual_frontier_63mod64_q20.json \
  --out reports/frontier_strata_63mod64_q20.json

python -m collatz_lab.return_maps \
  --a-min 6 \
  --a-max 20 \
  --h-min 1 \
  --h-max 20 \
  --out reports/parent_return_maps_a6_a20_h1_h20.json

python -m collatz_lab.parent_graph \
  --q-depth 20 \
  --residual-report reports/residual_frontier_63mod64_q20.json \
  --burst-report reports/burst_families_a6_a20.json \
  --return-report reports/parent_return_maps_a6_a20_h1_h20.json \
  --out reports/parent_transition_graph_q20.json

python -m collatz_lab.cube_compress \
  --residual-report reports/residual_frontier_63mod64_q20.json \
  --q-depth 20 \
  --sets residual_certified,unknown,k16,k19,k21,k24,k26 \
  --out reports/cube_compression_q20.json

python -m collatz_lab.signature \
  --residual-report reports/residual_frontier_63mod64_q20.json \
  --q-depth 20 \
  --set residual_certified \
  --sample-or-all all \
  --out reports/signatures_residual_certified_q20.parquet

python -m collatz_lab.potential \
  --graph reports/parent_transition_graph_q20.json \
  --out reports/potential_parent_q20.json

python -m collatz_lab.theorem_report \
  --q-depth 20 \
  --out reports/theorem_candidate_parent_63mod64_q20.json

python -m collatz_lab.adaptive_refine \
  --parent 63mod64 \
  --focus-depth 7 \
  --focus-residue 23 \
  --extra-depth 16 \
  --require-a 6 \
  --require-h 1 \
  --require-post-burst-mod64 63 \
  --require-returns-to-parent true \
  --out reports/refine_sharp_return_a6_h1_q23mod128_extra16_q23.json

python -m collatz_lab.sharp_return \
  --q-depth 23 \
  --out reports/sharp_return_tower_q23.json

python -m collatz_lab.parent_states \
  --a-min 1 \
  --a-max 20 \
  --out reports/parent_states_a1_a20_samples.json

python -m collatz_lab.cycle_certificates \
  --out reports/cycle_certificates_sharp_q23.json

python -m collatz_lab.cycle_miner \
  --return-report reports/parent_return_maps_a6_a20_h1_h20.json \
  --q-depth 23 \
  --max-cycle-length 2 \
  --out reports/cycle_mining_parent_returns_q23.json

python -m collatz_lab.adic_basin \
  --q-depth 23 \
  --out reports/adic_basin_q23.json

python -m collatz_lab.debt \
  --out reports/debt_demo.json

python -m collatz_lab.cube_lifter \
  --cube-report reports/cube_compression_q20.json \
  --burst-report reports/burst_families_a6_a20.json \
  --return-report reports/parent_return_maps_a6_a20_h1_h20.json \
  --out reports/P6_cube_lift_report.json

python -m collatz_lab.proof_obligations \
  --out reports/proof_obligations_parent_P6.json

python -m collatz_lab.proof_env \
  --obligations reports/proof_obligations_parent_P6.json \
  --beam-size 5 \
  --trace-out data/proof_traces/proof_policy_run_v1.jsonl \
  --out reports/proof_policy_run_v1.json

python -m collatz_lab.parent_state_system \
  --a-min 1 \
  --a-max 20 \
  --r-depth 7 \
  --out reports/parent_state_system_a1_a20_r7.json

python -m collatz_lab.valuation_closure \
  --return-report reports/parent_return_maps_a6_a20_h1_h20.json \
  --max-depth 1 \
  --out reports/valuation_closure_parent_returns.json

python -m collatz_lab.scc_ranker \
  --sharp-q23 \
  --out reports/scc_ranker_smoke.json

python -m collatz_lab.falsifier \
  --out reports/falsifier_report.json

python -m collatz_lab.proof_controller \
  --obligations reports/proof_obligations_parent_P6.json \
  --beam-size 5 \
  --rounds 1 \
  --trace-out data/proof_traces/proof_controller_v1.jsonl \
  --out reports/proof_controller_v1.json

python -m collatz_lab.proof_controller \
  --obligations reports/proof_obligations_parent_P6.json \
  --mode fixed-point \
  --max-rounds 100 \
  --beam-size 16 \
  --graph-out reports/proof_graph_latest.json \
  --trace-out data/proof_traces/proof_controller_fixed_point.jsonl \
  --out reports/proof_controller_fixed_point.json

python -m collatz_lab.parametric_a \
  --depth 8 \
  --a-min 1 \
  --a-max 64 \
  --out reports/parametric_a_depth8.json

python -m collatz_lab.p6_subtheorem \
  --proof-obligations reports/proof_obligations_parent_P6.json \
  --proof-graph reports/proof_graph_latest.json \
  --out reports/P6_descent_subtheorem.json

python -m collatz_lab.global_parent_obligations \
  --parent-state-system reports/parent_state_system_a1_a20_r7.json \
  --parametric-a reports/parametric_a_depth8.json \
  --out reports/parent_state_global_obligations.json \
  --theorem-out reports/parent_state_global_theorem_candidate.json

python -m collatz_lab.proof_policy_model \
  --traces data/proof_traces/proof_policy_run_v1.jsonl \
  --model-out reports/proof_policy_model_v1.pkl \
  --report-out reports/proof_policy_model_v1.json

python -m collatz_lab.proof_verifier \
  --proof-graph reports/proof_graph_latest.json \
  --global-obligations reports/parent_state_global_obligations.json \
  --out reports/collatz_descent_theorem_candidate.json
```

The main exact grammar being mined is:

```text
n = 2^a r - 1
  -> 3^a r - 1
  -> (3^a r - 1) / 2^h
```

Outcomes are labeled as burst descent, return to the `63 mod 64` parent, leave-parent branch, finite-depth certification, or unknown.

The proof-policy layer treats open obligations as a verifier-backed proof game:

```text
open obligation -> structured proof action -> exact verifier result -> reward/trace
```

The first policy is a heuristic seed policy. It does not prove Collatz; it creates machine-checkable proof traces for future model training on actions such as `TRY_ADIC_BASIN`, `SPLIT_BY_H`, `PROMOTE_TO_PARENT_STATE`, and `TRY_ANCESTOR_COMPOSITION`.

The canonical proof verifier is intentionally strict: `reports/collatz_descent_theorem_candidate.json` must remain `FAIL` until universal parent-state coverage, exact transition validity, SCC termination, and ancestor descent are all closed with no unknown obligations.

The one-step-away proof compiler stores persistent closure state in `reports/proof_graph_latest.json`. In this graph, an action result of `REDUCED` is never proof closure: the parent closes only by a direct exact certificate or once all child obligations close. The global parent-state report separates universal entry coverage (`evens descend`, `odds enter some P_a`) from the still-open mathematical obligation of proving all parent-state transitions terminate.

## Run Tracking and Proof Confidence

Every proof-discovery run should end with a run result and an entry in `runs.md`.
The scoring policy is deliberately verifier-gated:

- `proof_confidence_percent` is `100` only when the strict proof verifier returns `PASS`; otherwise it is `0`.
- `proof_progress_percent` measures exact proof-graph closure progress.
- `model_discovery_score_percent` measures useful model/discovery signals, but never by itself implies a proof.

Backfill the current baseline from existing artifacts:

```bash
python -m collatz_lab.run_pipeline backfill-baseline
```

Create the planned A10G reference command bundle:

```bash
python -m collatz_lab.run_pipeline plan-a10g-reference
```

After a run completes and artifacts are available locally, assemble the official run record:

```bash
python -m collatz_lab.run_pipeline assemble \
  --run-id RUN-001-a10g-reference \
  --title "A10G reference run" \
  --config-path configs/syracuse_multitask_reference_modal.yaml \
  --checkpoint-path /mnt/collatz/runs/RUN-001-a10g-reference/checkpoint.pt \
  --append-runs
```

## Core Maps

The standard Collatz map is:

```text
C(n) = n / 2      if n is even
C(n) = 3n + 1     if n is odd
```

The one-division shortcut map is:

```text
T(n) = n / 2          if n is even
T(n) = (3n + 1) / 2   if n is odd
```

The odd-only Syracuse map is:

```text
S(n) = (3n + 1) / 2^v2(3n + 1)
```

for odd `n`, where `v2(3n + 1)` is the number of factors of two dividing `3n + 1`.

The odd-only map is especially useful because it exposes the important local quantity:

```text
v2(3n + 1)
```

## ML Tasks

The first version should support these tasks.

Task A: valuation prediction

- Input: `n`
- Target: `v2(3n + 1)` for odd `n`
- Purpose: teaches binary suffix and residue-class structure.

Task B: odd-successor prediction

- Input: `n`
- Target: `S(n) = (3n + 1) / 2^v2(3n + 1)`
- Purpose: main sequence-to-sequence dynamics task.

Task C: first descent prediction

- Input: `n`
- Target: `sigma(n) = min { k : C^k(n) < n }`
- Purpose: connects directly to proof search. A theorem of the form `forall n > 1, exists k, C^k(n) < n` would prove Collatz by descent.

Task D: parity prefix prediction

- Input: `n`
- Target: `(parity(C^0(n)), ..., parity(C^(K-1)(n)))`
- Purpose: tests whether the model understands residue classes modulo powers of two.

Task E: hard-case classification

- Input: `n`
- Target: whether `n` is unusually slow to descend
- Purpose: oversample and identify cases most likely to reveal missing structure.

## Data Strategy

Use generated data as the primary source. Collatz data is deterministic, infinite, cheap, and exact. Online datasets may be useful for comparison, but synthetic generation gives better control over bit length, numeral base, hard-case sampling, and train/test splits.

Large integers are stored as strings in Parquet to avoid silent overflow in fixed-width integer columns.

Suggested shard layout:

```text
data/
  raw/
  processed/
  shards/
    task=syracuse/base=2/bits=32/shard_00000.parquet
    task=syracuse/base=24/bits=32/shard_00000.parquet
    task=descent/base=2/bits=48/shard_00000.parquet
```

Each row should include:

- `n`
- `input_digits`
- `target_digits`
- `base`
- `bit_length`
- `parity_prefix`
- `v2_3n_plus_1`
- `syracuse_next`
- `first_descent_time`
- `max_height_ratio`
- `total_stopping_time_capped`
- `split`

Use multiple bases:

```text
2, 8, 10, 16, 24, 32
```

Use both digit orders:

- MSB-first: normal reading order
- LSB-first: least significant digit first

The LSB-first version is important because Collatz structure is heavily controlled by low-order bits.

Train/test splits should not just be random. Use three split types:

- random split
- numeric-range split: train on smaller bit lengths, test on larger bit lengths
- residue holdout: hold out selected residue classes modulo `2^p`

The range split is crucial because the goal is structural generalization, not memorization.

## Model Architecture

The project should converge on one main reference architecture rather than wandering through many unrelated models. Small baselines and ablations are still useful, but only as controls. The main candidate is a multitask encoder-decoder Transformer trained to learn Collatz structure, not just one output format.

Reference model: Collatz Multitask Transformer

- Input representation: signed integer digits in base `24` or `32`, LSB-first.
- Signed encoding: positive `n` uses the existing token layout; negative `n` inserts a base-specific `NEG` token before the digits of `abs(n)`.
- Encoder: Transformer encoder over the input digits of `n`.
- Decoder: autoregressive Transformer decoder for sequence targets such as `S(n)`.
- Shared representation: pooled encoder state used by auxiliary heads.
- Context length: long enough for the largest trained bit length in the selected base.
- Precision: `bf16` on Modal GPU.
- Checkpointing: every `1000` steps or better for long runs.

Recommended first serious configuration:

Tracked in `configs/syracuse_multitask_reference_modal.yaml`.

```yaml
task: multitask
base: 24
lsb_first: true
batch_size: 512
model:
  type: seq2seq
  signed: true
  d_model: 256
  n_heads: 8
  n_layers: 6
  dropout: 0.1
  max_seq_len: 128
optimizer:
  lr: 0.0002
  weight_decay: 0.01
training:
  precision: bf16
  max_train_steps: 30000
  eval_every: 500
  checkpoint_every: 1000
  grad_clip: 1.0
modal:
  gpu: A10G
```

Scale-up candidate after the first mixed-bit run:

```yaml
model:
  d_model: 384
  n_heads: 8
  n_layers: 8
  dropout: 0.1
training:
  max_train_steps: 50000
modal:
  gpu: A100
```

Multitask heads:

- sequence head: predicts the odd-only Syracuse successor `S(n)`
- valuation head: predicts `v2(3n + 1)`
- descent head: predicts or buckets first descent time `sigma(n)`
- hard-case head: predicts whether `n` is unusually slow to descend
- parity head: predicts a prefix of Collatz parities
- negative-cycle head: predicts the known signed Collatz cycle reached by a negative row

The shared encoder is the most important object. The decoder tells us whether the representation supports computation of the next Syracuse state. The heads tell us whether the same representation encodes proof-relevant structure: low-order residues, valuation, descent, and hard-case behavior.

## Reference Training Recipe

The next serious version should not train only on one bit length. The Syracuse 40-bit run learned the same-size task well but failed badly on 48-bit exact sequence accuracy, so the reference model must train across a range.

Primary recipe:

- base: `24` first, `32` as the main backup
- digit order: LSB-first
- train bit lengths: mixed `24, 32, 40, 48`
- sign mix: `50/50` positive and negative rows in the first signed reference run
- validation bit lengths: held-out rows from the same bit lengths
- OOD bit lengths: `56` and `64`
- training data: random rows plus high-valuation rows plus slow-descent/hard-case rows plus negative-cycle examples
- eval data: separate ID, OOD, residue-holdout, and hard-case shards

Curriculum:

1. Warm up on `v2(3n + 1)` and parity-prefix structure.
2. Train the multitask model on signed Syracuse successor, `v2`, first descent, hard-case, parity, and negative-cycle labels.
3. Fine-tune on hard cases and residue classes where the model is confidently wrong.
4. Freeze no mathematical claim until the exact verifier confirms it.

Control experiments should be narrow:

- base `24` vs base `32`
- LSB-first vs MSB-first
- with vs without hard-case oversampling
- single-task Syracuse vs multitask Syracuse

The goal is not to search endlessly over architectures. The goal is to make one reference model strong enough to feed the discovery and verifier layer.

## Interpretability And Discovery

Accuracy alone is not the point. After training, run probes.

Probe questions:

- Can hidden states linearly recover `n mod 2^p`?
- Can hidden states recover `v2(3n + 1)`?
- Do hard cases cluster?
- Does the model learn different concepts in different bases?
- Which residues produce systematic errors?
- Which inputs are confidently mispredicted?

Then mine candidate rules:

```text
n == a (mod 2^p)  =>  C^k(n) < n
```

The project should include a `discover.py` tool that takes model errors, high-confidence predictions, and hard-case clusters, then proposes residue-class rules.

Those rules must be passed to an exact verifier. Neural predictions are not proof.

## Exact Verification

The verifier should check candidate descent rules exactly when possible.

For a fixed parity prefix of length `m`, Collatz has an affine form:

```text
C^m(n) = (3^r n + B) / 2^s
```

where `r` is the number of odd steps and `B, s` depend on the parity pattern.

The verifier should:

1. Take a candidate rule: residue `a mod M`, step bound `k`.
2. Symbolically compute the parity prefix for `n = a mod M` when stable.
3. Derive or empirically confirm the affine expression.
4. Prove the inequality `C^k(n) < n` for all `n` in that residue class, when possible.
5. Return `PASS`, `FAIL`, `NEEDS_LARGER_MODULUS`, or `COUNTEREXAMPLE`.

A successful output is not "model accuracy = 99%." A successful output is more like:

```text
For modulus 2^20, 97.3% of residue classes have verified descent rules under k <= 180.
The remaining classes are clustered into 12 families.
The model proposes a smaller set of symbolic descriptions for those families.
```

That would be mathematically useful.

## Modal Infrastructure

Use Modal for GPU training, sweeps, and larger data generation. Use Modal Volumes for persistent data, checkpoints, logs, and reports.

Training jobs should checkpoint regularly. Long jobs should be resumable from the latest checkpoint, because Modal function calls have a maximum timeout and cloud jobs can be interrupted.

Suggested Modal layout:

```text
/mnt/collatz/
  data/
  checkpoints/
  runs/
  tensorboard/
  reports/
```

Commands should look like:

```bash
python -m modal run modal_app.py::generate_remote \
  --task syracuse \
  --base 24 \
  --bits 40 \
  --n 1000000 \
  --out /mnt/collatz/data/syracuse/base24_bits40_train_1m.parquet
```

```bash
python -m modal run modal_app.py::train_remote \
  --config-path configs/syracuse_base24.yaml
```

```bash
python -m modal run modal_app.py::sweep_remote \
  --sweep-config-path configs/sweeps/base_ablation.yaml
```

```bash
python -m modal run modal_app.py::analyze_remote --run-id RUN_ID
```

For first experiments, A10G is enough. Larger GPU classes can be used when sweeps or model size justify the cost.

## Milestones

Milestone 1: data and baselines

Deliver:

- local data generator
- Collatz math utilities
- PyTorch dataset
- baseline MLP
- basic Transformer
- local training loop
- Modal training function

Success:

- Can train on `v2(3n + 1)` and `S(n)` for small bit lengths.
- Can evaluate by base and bit length.

Milestone 2: reproduce known ML behavior

Deliver:

- base ablation: `2, 8, 10, 16, 24, 32`
- MSB-first vs LSB-first
- accuracy by residue class modulo `2^p`
- failure case dashboard

Success:

- Models show residue-class learning and base sensitivity.

Milestone 3: proof-useful labels

Deliver:

- first descent time dataset
- hard-case mining
- max-height labels
- out-of-distribution tests

Success:

- Model identifies hard classes better than random and simple math baselines.

Milestone 4: discovery and verifier

Deliver:

- candidate residue-rule miner
- exact checker
- counterexample generator
- report generator

Success:

- System proposes descent rules and verifies them exactly for nontrivial residue families.

## Main Risks

- The model may learn shallow digit tricks instead of deep structure.
- The model may generalize across random splits but fail across bit-length splits.
- High prediction accuracy may not translate into proof-useful insight.
- Residue-class certificates may explode in size and become mathematically uninteresting.
- The verifier may pass many small rules without revealing a compressible pattern.

To reduce these risks, every experiment should include:

- range-based test split
- residue holdout split
- hard-case evaluation
- interpretable probes
- exact verification of any discovered rule

## Local Setup

```bash
cd collatz-pattern-lab
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Example Commands

Generate a local dataset:

```bash
python -m collatz_lab.generate \
  --task syracuse \
  --base 24 \
  --bits 40 \
  --n 100000 \
  --out data/shards/syracuse_base24_bits40.parquet \
  --lsb-first true \
  --seed 0
```

Generate a signed mixed multitask shard:

```bash
python -m collatz_lab.generate \
  --task multitask \
  --base 24 \
  --bits 24 \
  --n 250000 \
  --out data/shards/multitask_base24_bits24_signed_250k.parquet \
  --lsb-first true \
  --signed true \
  --sign-mode mixed \
  --sample-mode mixed \
  --positive-fraction 0.5 \
  --v2-min 8 \
  --v2-max 16 \
  --split all_train \
  --seed 24
```

Train locally:

```bash
python -m collatz_lab.train --config configs/v2_base2.yaml
```

Run training on Modal:

```bash
python -m modal run modal_app.py::train_remote --config-path configs/syracuse_base24.yaml
```

Evaluate a checkpoint:

```bash
python -m collatz_lab.eval --checkpoint runs/latest/checkpoint.pt --data data/test_v2.parquet
```

Run probes:

```bash
python -m collatz_lab.probes \
  --checkpoint runs/latest/checkpoint.pt \
  --data data/test_v2.parquet \
  --out reports/probes.json
```

Mine candidate rules:

```bash
python -m collatz_lab.discover \
  --checkpoint runs/latest/checkpoint.pt \
  --data data/test_v2.parquet \
  --out reports/candidates.jsonl
```

Verify candidate rules:

```bash
python -m collatz_lab.verifier \
  --rules reports/candidates.jsonl \
  --samples-per-rule 1000 \
  --max-t 120
```

Run the signed reference analysis pipeline:

```bash
./scripts/run_signed_reference_analysis.sh /mnt/collatz/runs/20260424_222430_multitask_base24
```

Proof-miner quality is measured by exact verifier results, not model confidence. A better miner should increase:

- exact `PASS` count
- verified hard-case coverage
- pass rate after counterexample search
- compression of many verified lifted residues into fewer symbolic families

The lifted miner proposes parity-stable rules of the form `n == a mod 2^k`, then sends them to the verifier. These are legitimate local descent certificates when the verifier returns `PASS`, but they still need compression before they become mathematically interesting families.

Compress verified lifted certificates:

```bash
python -m collatz_lab.compress \
  --verification reports/verification_hard_positive_lifted.json \
  --out-json reports/lifted_compression.json \
  --out-md reports/lifted_compression.md
```

Extract proof-relevant signatures and q-space coordinates:

```bash
python -m collatz_lab.signature \
  --rules reports/verification_hard_positive_lifted.json \
  --burst-length 6 \
  --out-jsonl reports/lifted_signatures.jsonl \
  --out-parquet reports/lifted_signatures.parquet
```

Mine symbolic families from verified certificates:

```bash
python -m collatz_lab.family_miner \
  --verification reports/verification_hard_positive_lifted.json \
  --burst-length 6 \
  --out-json reports/family_mining.json \
  --out-md reports/family_mining.md \
  --out-table reports/family_mining.parquet
```

Build a finite-modulus frontier of unresolved residue classes:

```bash
python -m collatz_lab.frontier \
  --mod-power 20 \
  --max-steps 120 \
  --out reports/frontier_p20_k120.parquet \
  --summary-out reports/frontier_p20_k120_summary.json
```

Search for a finite-state logarithmic potential over verified transitions:

```bash
python -m collatz_lab.potential \
  --transitions reports/lifted_signatures.jsonl \
  --out reports/potential.json
```

## Research Discipline

Machine learning results in this repository are exploratory. A model can suggest residues, clusters, hard cases, or symbolic candidates worth inspecting, but it cannot prove a Collatz statement. Treat every neural result as a hypothesis until exact verification succeeds.
