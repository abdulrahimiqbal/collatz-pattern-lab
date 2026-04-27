import json

import torch

from collatz_lab.proof_transformer import ProofCorpusTextDataset, build_vocab, collate_proof_batch, train_proof_transformer
from collatz_lab.proof_transformer_eval import evaluate_checkpoint
from collatz_lab.models import TinySeq2SeqTransformer


def test_proof_transformer_dataset_encodes_prompt_and_target() -> None:
    rows = [
        {
            "source": "synthetic_formal_proof",
            "task": "general_formal_proof_pattern",
            "label": "PROPOSE_PROOF_DSL",
            "verifier_status": "PROOF_PATTERN",
            "tags": ["proof"],
            "prompt": "prove x = x",
            "target": "reflexivity",
        }
    ]
    vocab = build_vocab(rows)
    dataset = ProofCorpusTextDataset(rows, vocab, max_input_len=32, max_target_len=24)
    item = dataset[0]

    assert item["input_ids"].dtype == torch.long
    assert item["target_ids"].dtype == torch.long
    assert item["input_ids"][0].item() == 1
    assert item["target_ids"][0].item() == 1


def test_collate_proof_batch_pads_attention_mask() -> None:
    rows = [
        {
            "source": "s",
            "task": "t",
            "label": "a",
            "verifier_status": "PASS",
            "prompt": "short",
            "target": "x",
        },
        {
            "source": "s",
            "task": "t",
            "label": "a",
            "verifier_status": "PASS",
            "prompt": "longer prompt",
            "target": "longer target",
        },
    ]
    vocab = build_vocab(rows)
    dataset = ProofCorpusTextDataset(rows, vocab, max_input_len=64, max_target_len=64)
    batch = collate_proof_batch([dataset[0], dataset[1]])

    assert batch["input_ids"].shape[0] == 2
    assert batch["target_ids"].shape[0] == 2
    assert batch["attention_mask"].dtype == torch.bool


def test_train_proof_transformer_resumes_from_checkpoint(tmp_path) -> None:
    rows = [
        {
            "source": "synthetic_formal_proof",
            "task": "general_formal_proof_pattern",
            "label": "PROPOSE_PROOF_DSL",
            "verifier_status": "PROOF_PATTERN",
            "prompt": f"prove x = x case {index}",
            "target": "reflexivity",
        }
        for index in range(8)
    ]
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    checkpoint = tmp_path / "checkpoint.pt"
    report = tmp_path / "report.json"

    train_proof_transformer(
        corpus,
        checkpoint,
        report,
        max_examples=None,
        max_steps=2,
        batch_size=2,
        d_model=16,
        n_heads=4,
        n_layers=1,
        max_input_len=64,
        max_target_len=32,
        checkpoint_every=1,
    )
    resumed = train_proof_transformer(
        corpus,
        checkpoint,
        report,
        max_examples=None,
        max_steps=4,
        batch_size=2,
        d_model=16,
        n_heads=4,
        n_layers=1,
        max_input_len=64,
        max_target_len=32,
        checkpoint_every=1,
        resume_from=checkpoint,
    )

    saved = torch.load(checkpoint, map_location="cpu")
    assert saved["step"] == 4
    assert resumed["resumed"] is True
    assert resumed["resume_start_step"] == 2
    assert resumed["train_steps_completed"] == 4


def test_evaluate_checkpoint_writes_proof_attempt_bundle(tmp_path) -> None:
    vocab = build_vocab(
        [
            {
                "source": "s",
                "task": "t",
                "label": "PROPOSE_PROOF_DSL",
                "verifier_status": "UNKNOWN",
                "prompt": "mixed modulus debt rank z(k) mod",
                "target": "PROPOSE_DEBT_RANK",
            }
        ]
    )
    model = TinySeq2SeqTransformer(
        vocab_size=len(vocab.chars) + 4,
        d_model=16,
        n_heads=4,
        n_layers=1,
        dropout=0.0,
        max_seq_len=64,
    )
    checkpoint = tmp_path / "checkpoint.pt"
    torch.save(
        {
            "model_state": model.state_dict(),
            "vocab": vocab.to_json(),
            "config": {"d_model": 16, "n_heads": 4, "n_layers": 1, "max_input_len": 64, "max_target_len": 32},
            "step": 7,
        },
        checkpoint,
    )
    theorem = tmp_path / "theorem.json"
    theorem.write_text(json.dumps({"verifier_status": "FAIL", "unknown_obligations": [{}]}), encoding="utf-8")
    progress = tmp_path / "progress.json"
    progress.write_text(json.dumps({"proof_progress_percent": 12.5}), encoding="utf-8")
    global_obligations = tmp_path / "global.json"
    global_obligations.write_text(json.dumps({"obligations": []}), encoding="utf-8")
    high_parent = tmp_path / "high_parent.json"
    high_parent.write_text(
        json.dumps(
            {
                "status": "MIXED_MODULUS_BYPASS_BUILT",
                "all_sample_checks_passed": True,
                "mixed_successor_family_count": 4,
            }
        ),
        encoding="utf-8",
    )
    debt = tmp_path / "debt.json"
    debt.write_text(json.dumps({"status": "OPEN", "proof_closed": False}), encoding="utf-8")

    report = evaluate_checkpoint(
        run_id="RUN-T",
        checkpoint_path=checkpoint,
        out_dir=tmp_path / "out",
        high_parent_bypass_path=high_parent,
        mixed_modulus_debt_path=debt,
        theorem_candidate_path=theorem,
        progress_report_path=progress,
        global_obligations_path=global_obligations,
        debt_induction_path=debt,
        central_attempts_log_path=tmp_path / "attempts.jsonl",
        max_new_tokens=1,
        device="cpu",
    )

    assert report["schema"] == "collatz_lab.proof_transformer_evaluation"
    assert report["proof_confidence_percent"] == 0.0
    assert (tmp_path / "out" / "proof_attempt.json").exists()
    assert (tmp_path / "out" / "proof_evaluation.json").exists()
    assert (tmp_path / "attempts.jsonl").exists()
