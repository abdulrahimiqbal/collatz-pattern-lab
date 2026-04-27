# Proof Transformer Training

- status: `TRAINED_SHARED_PROOF_TRANSFORMER_SMOKE`
- model kind: `shared Transformer proof model`
- examples used: `1866`
- train steps: `2`
- parameters: `35221`
- metrics: `{'train_loss': 4.538505554199219, 'val_loss': 4.624379634857178}`
- scaling readiness: `{'has_general_proof_stream': True, 'has_collatz_structural_stream': True, 'has_verifier_replay_stream': True, 'shared_target': 'proof DSL + repair action + verifier outcome'}`

Small local settings are smoke tests. RUN-009 serious readiness is controlled by run9_preflight parameter-count and training-step thresholds.
