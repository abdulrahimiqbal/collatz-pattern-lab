import json

import torch

from collatz_lab.proof_action_dataset import build_arg_parser, build_tiny_dataset
from collatz_lab.proof_action_eval import evaluate
from collatz_lab.proof_action_model import train
from collatz_lab.utils import save_yaml


def test_tiny_eval_writes_verifier_metrics(tmp_path) -> None:
    data_dir = tmp_path / "data"
    args = build_arg_parser().parse_args(["build-tiny", "--out", str(data_dir), "--num-traces", "2", "--seed", "1337"])
    build_tiny_dataset(args)
    cfg = {
        "run": {"id": "RUN-T", "description": "tiny test"},
        "data": {"rows": str(data_dir / "rows.jsonl"), "train_splits": ["train"], "val_splits": ["train"]},
        "model": {
            "d_model": 16,
            "encoder_layers": 1,
            "decoder_layers": 1,
            "heads": 4,
            "ffn_dim": 32,
            "max_state_len": 256,
            "max_action_len": 96,
            "max_vocab_size": 512,
        },
        "training": {"max_steps": 1, "batch_size": 2, "lr": 0.001, "warmup_steps": 1, "seed": 1337},
        "evaluation": {"splits": ["train"], "max_examples": 2, "beam_size": 8, "top_k": 5, "use_action_memory": True},
        "output": {"dir": str(tmp_path / "out")},
    }
    config = tmp_path / "config.yaml"
    save_yaml(cfg, config)

    train(config)
    summary = evaluate(config)

    assert summary["syntax_valid_rate"] >= 0.99
    assert summary["action_parse_rate"] >= 0.99
    assert summary["top1_verifier_accept_rate"] >= 0.99
    assert (tmp_path / "out" / "eval_summary.json").exists()
    assert (tmp_path / "out" / "generated_actions.jsonl").exists()
    assert (tmp_path / "out" / "run_result.json").exists()
