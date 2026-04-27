# Proof Transformer Training

- status: `TRAINED_SHARED_PROOF_TRANSFORMER_SMOKE`
- model kind: `shared Transformer proof model`
- examples used: `256`
- train steps: `2`
- parameters: `244824`
- metrics: `{'train_loss': 4.571718215942383, 'val_loss': 4.5352184772491455}`
- scaling readiness: `{'has_general_proof_stream': True, 'has_collatz_structural_stream': True, 'has_verifier_replay_stream': True, 'shared_target': 'proof DSL + repair action + verifier outcome'}`

Small local settings are smoke tests. RUN-009 serious readiness is controlled by run9_preflight parameter-count and training-step thresholds.
