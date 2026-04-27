import torch

from collatz_lab.dataset import CollatzDataset, collate_batch
from collatz_lab.encode import vocab_size_for_base
from collatz_lab.generate import generate_rows, write_parquet
from collatz_lab.models import build_model
from collatz_lab.train import compute_loss


def test_signed_multitask_dataset_masks(tmp_path) -> None:
    path = tmp_path / "signed.parquet"
    rows = generate_rows(
        task="multitask",
        base=24,
        bits=8,
        n_rows=20,
        signed=True,
        sign_mode="mixed",
        sample_mode="random",
        split_method="all_train",
        show_progress=False,
    )
    write_parquet(rows, path)
    dataset = CollatzDataset(path, split="train", task="multitask", base=24)
    batch = collate_batch([dataset[i] for i in range(len(dataset))])
    signs = [int(item["metadata"]["sign"]) for item in [dataset[i] for i in range(len(dataset))]]
    assert 1 in signs
    assert -1 in signs
    assert batch["mask_hard_case"].sum().item() == signs.count(1)
    assert batch["mask_negative_cycle"].sum().item() == signs.count(-1)
    assert batch["labels_parity_prefix"].shape[1] == 32


def test_signed_multitask_model_loss_forward(tmp_path) -> None:
    path = tmp_path / "signed.parquet"
    rows = generate_rows(
        task="multitask",
        base=24,
        bits=8,
        n_rows=8,
        signed=True,
        sign_mode="mixed",
        sample_mode="random",
        split_method="all_train",
        show_progress=False,
    )
    write_parquet(rows, path)
    dataset = CollatzDataset(path, split="train", task="multitask", base=24)
    batch = collate_batch([dataset[i] for i in range(len(dataset))])
    config = {
        "task": "multitask",
        "base": 24,
        "model": {
            "type": "seq2seq",
            "signed": True,
            "d_model": 32,
            "n_heads": 4,
            "n_layers": 1,
            "dropout": 0.0,
            "max_seq_len": 64,
            "parity_prefix_len": 32,
            "num_negative_cycles": 100,
        },
    }
    model = build_model(config, vocab_size=vocab_size_for_base(24, signed=True), task="multitask")
    decoder_input = batch["target_ids"][:, :-1]
    outputs = model(batch["input_ids"], decoder_input_ids=decoder_input, attention_mask=batch["attention_mask"])
    assert outputs["logits"] is not None
    assert outputs["v2_logits"] is not None
    assert outputs["descent_bucket_logits"] is not None
    assert outputs["hard_case_logits"] is not None
    assert outputs["parity_logits"] is not None
    assert outputs["negative_cycle_logits"] is not None
    loss, metrics = compute_loss(
        outputs,
        batch,
        task="multitask",
        loss_weights={
            "sequence": 1.0,
            "v2": 0.3,
            "descent_bucket": 0.2,
            "hard_case": 0.2,
            "parity": 0.1,
            "negative_cycle": 0.2,
        },
    )
    assert torch.isfinite(loss)
    assert "negative_cycle_acc" in metrics
