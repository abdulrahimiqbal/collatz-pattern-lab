import torch

from collatz_lab.proof_action_candidate_selector import SELECTOR_OUTCOME_CLASSES
from collatz_lab.proof_action_model import ProofActionSeq2Seq


def test_candidate_selector_cross_encoder_shapes() -> None:
    model = ProofActionSeq2Seq(
        vocab_size=32,
        d_model=16,
        encoder_layers=1,
        decoder_layers=1,
        heads=2,
        ffn_dim=32,
        dropout=0.0,
        max_seq_len=16,
        use_candidate_selector_head=True,
    )
    input_ids = torch.randint(4, 32, (2, 3, 7))
    attention_mask = input_ids.ne(0)

    outputs = model.score_candidate_pairs(input_ids, attention_mask)

    assert outputs["selector_score"].shape == (2, 3)
    assert outputs["utility_pred"].shape == (2, 3)
    assert outputs["outcome_logits"].shape == (2, 3, len(SELECTOR_OUTCOME_CLASSES))
