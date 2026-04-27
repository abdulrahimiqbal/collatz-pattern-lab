"""Tiny shared Transformer trainer for proof-inventor corpora.

This is the code path RUN-009 should scale up on GPU.  Local smoke training can
use very small settings, but the RUN-009 preflight requires a much larger
checkpoint and enough training steps before it counts as serious-ready.
"""

from __future__ import annotations

import argparse
import glob
import json
import random
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import torch
import torch.nn.functional as F
from rich.console import Console
from torch.utils.data import DataLoader, Dataset, IterableDataset

from .dataset import pad_1d
from .models import TinySeq2SeqTransformer


PROOF_TRANSFORMER_REPORT_SCHEMA = "collatz_lab.proof_transformer_training_report"
PAD = 0
BOS = 1
EOS = 2
UNK = 3
CHAR_OFFSET = 4


def _resolve_corpus_files(path: str | Path) -> list[Path]:
    text = str(path)
    if any(char in text for char in "*?[]"):
        return [Path(row) for row in sorted(glob.glob(text))]
    source = Path(path)
    if source.is_dir():
        return sorted(source.glob("*.jsonl"))
    return [source]


def _jsonl_rows(path: str | Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    rows = []
    for file_path in _resolve_corpus_files(path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if max_rows is not None and len(rows) >= max_rows:
                return rows
    return rows


def _load_report(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _input_text(row: dict[str, Any]) -> str:
    tags = " ".join(str(tag) for tag in row.get("tags", []))
    return "\n".join(
        [
            f"<TASK={row.get('task')}>",
            f"<SOURCE={row.get('source')}>",
            f"<LABEL={row.get('label')}>",
            f"<VERIFIER_STATUS={row.get('verifier_status')}>",
            f"<TAGS={tags}>",
            str(row.get("prompt", "")),
        ]
    )


def _target_text(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"<ACTION={row.get('label')}>",
            str(row.get("target", "")),
        ]
    )


def decode_text(ids: list[int] | torch.Tensor, vocab: "ProofCharVocab") -> str:
    """Decode model token ids back to text, skipping special tokens."""

    id_to_char = {index + CHAR_OFFSET: char for index, char in enumerate(vocab.chars)}
    values = ids.tolist() if torch.is_tensor(ids) else list(ids)
    chars: list[str] = []
    for value in values:
        token = int(value)
        if token in {PAD, BOS}:
            continue
        if token == EOS:
            break
        chars.append(id_to_char.get(token, ""))
    return "".join(chars)


@dataclass
class ProofCharVocab:
    chars: list[str]

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "ProofCharVocab":
        return cls(chars=[str(char) for char in payload.get("chars", [])])

    @property
    def stoi(self) -> dict[str, int]:
        return {char: index + CHAR_OFFSET for index, char in enumerate(self.chars)}

    def encode(self, text: str, max_len: int) -> torch.Tensor:
        mapping = self.stoi
        ids = [BOS]
        ids.extend(mapping.get(char, UNK) for char in text[: max(0, max_len - 2)])
        ids.append(EOS)
        return torch.tensor(ids, dtype=torch.long)

    def to_json(self) -> dict[str, Any]:
        return {"chars": self.chars, "special_tokens": {"PAD": PAD, "BOS": BOS, "EOS": EOS, "UNK": UNK}}


def build_vocab(rows: list[dict[str, Any]], max_chars: int = 512) -> ProofCharVocab:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(_input_text(row))
        counts.update(_target_text(row))
    chars = [char for char, _ in counts.most_common(max_chars)]
    return ProofCharVocab(chars=chars)


class ProofCorpusTextDataset(Dataset[dict[str, torch.Tensor]]):
    def __init__(
        self,
        rows: list[dict[str, Any]],
        vocab: ProofCharVocab,
        max_input_len: int = 768,
        max_target_len: int = 512,
    ) -> None:
        self.rows = rows
        self.vocab = vocab
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self.rows[index]
        return {
            "input_ids": self.vocab.encode(_input_text(row), self.max_input_len),
            "target_ids": self.vocab.encode(_target_text(row), self.max_target_len),
        }


class StreamingProofCorpusDataset(IterableDataset[dict[str, torch.Tensor]]):
    def __init__(
        self,
        files: list[Path],
        vocab: ProofCharVocab,
        max_input_len: int = 768,
        max_target_len: int = 512,
        seed: int = 9,
    ) -> None:
        self.files = files
        self.vocab = vocab
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len
        self.seed = seed

    def __iter__(self):
        rng = random.Random(self.seed)
        files = list(self.files)
        while True:
            rng.shuffle(files)
            for file_path in files:
                with file_path.open(encoding="utf-8") as handle:
                    for line in handle:
                        if not line.strip():
                            continue
                        row = json.loads(line)
                        yield {
                            "input_ids": self.vocab.encode(_input_text(row), self.max_input_len),
                            "target_ids": self.vocab.encode(_target_text(row), self.max_target_len),
                        }


def collate_proof_batch(batch: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
    input_ids = pad_1d([row["input_ids"] for row in batch], pad_value=PAD)
    target_ids = pad_1d([row["target_ids"] for row in batch], pad_value=PAD)
    return {
        "input_ids": input_ids,
        "target_ids": target_ids,
        "attention_mask": input_ids.ne(PAD),
    }


def _loss(model: TinySeq2SeqTransformer, batch: dict[str, torch.Tensor]) -> torch.Tensor:
    decoder_input = batch["target_ids"][:, :-1]
    labels = batch["target_ids"][:, 1:].contiguous()
    outputs = model(batch["input_ids"], decoder_input_ids=decoder_input, attention_mask=batch["attention_mask"])
    logits = outputs["logits"]
    assert logits is not None
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)), labels.reshape(-1), ignore_index=PAD)


@torch.no_grad()
def _eval_loss(
    model: TinySeq2SeqTransformer,
    loader: DataLoader,
    device: torch.device,
    max_batches: int = 5,
) -> float:
    model.eval()
    losses = []
    for index, batch in enumerate(loader):
        if index >= max_batches:
            break
        batch = {key: value.to(device) for key, value in batch.items()}
        losses.append(float(_loss(model, batch).item()))
    model.train()
    return sum(losses) / max(len(losses), 1)


def _write_json(path: str | Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _checkpoint_payload(
    model: TinySeq2SeqTransformer,
    optimizer: torch.optim.Optimizer,
    vocab: ProofCharVocab,
    *,
    d_model: int,
    n_heads: int,
    n_layers: int,
    max_input_len: int,
    max_target_len: int,
    step: int,
) -> dict[str, Any]:
    return {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "vocab": vocab.to_json(),
        "config": {
            "d_model": d_model,
            "n_heads": n_heads,
            "n_layers": n_layers,
            "max_input_len": max_input_len,
            "max_target_len": max_target_len,
        },
        "step": step,
    }


def _move_optimizer_state_to_device(optimizer: torch.optim.Optimizer, device: torch.device) -> None:
    for state in optimizer.state.values():
        for key, value in list(state.items()):
            if torch.is_tensor(value):
                state[key] = value.to(device)


def load_proof_transformer_checkpoint(
    checkpoint_path: str | Path,
    *,
    device: torch.device | None = None,
) -> tuple[TinySeq2SeqTransformer, ProofCharVocab, dict[str, Any]]:
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    config = dict(checkpoint.get("config") or {})
    vocab = ProofCharVocab.from_json(checkpoint.get("vocab", {}))
    if not vocab.chars:
        raise ValueError(f"checkpoint has no usable vocab: {checkpoint_path}")
    target_device = device or torch.device(
        "cuda"
        if torch.cuda.is_available()
        else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
    )
    model = TinySeq2SeqTransformer(
        vocab_size=len(vocab.chars) + CHAR_OFFSET,
        d_model=int(config.get("d_model", 128)),
        n_heads=int(config.get("n_heads", 4)),
        n_layers=int(config.get("n_layers", 4)),
        dropout=0.0,
        max_seq_len=max(int(config.get("max_input_len", 768)), int(config.get("max_target_len", 512))),
    ).to(target_device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, vocab, checkpoint


@torch.no_grad()
def generate_proof_text(
    model: TinySeq2SeqTransformer,
    vocab: ProofCharVocab,
    row: dict[str, Any],
    *,
    max_input_len: int = 768,
    max_new_tokens: int = 384,
    temperature: float = 0.0,
    top_k: int = 0,
    seed: int = 9,
    decoder_prefix: str = "",
) -> str:
    """Generate one proof-transformer target string from a corpus-style prompt row."""

    device = next(model.parameters()).device
    generator = torch.Generator(device=device)
    generator.manual_seed(seed)
    input_ids = vocab.encode(_input_text(row), max_input_len).unsqueeze(0).to(device)
    attention_mask = input_ids.ne(PAD)
    mapping = vocab.stoi
    prefix_ids = [mapping.get(char, UNK) for char in decoder_prefix]
    decoded = torch.tensor([[BOS, *prefix_ids]], dtype=torch.long, device=device)
    for _ in range(max_new_tokens):
        outputs = model(input_ids, decoder_input_ids=decoded, attention_mask=attention_mask)
        logits = outputs["logits"]
        assert logits is not None
        next_logits = logits[:, -1, :]
        if temperature and temperature > 0.0:
            next_logits = next_logits / temperature
            if top_k and top_k > 0:
                values, indices = torch.topk(next_logits, min(top_k, next_logits.size(-1)), dim=-1)
                probs = torch.softmax(values, dim=-1)
                sampled = torch.multinomial(probs, num_samples=1, generator=generator)
                next_token = indices.gather(-1, sampled)
            else:
                probs = torch.softmax(next_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1, generator=generator)
        else:
            next_token = torch.argmax(next_logits, dim=-1, keepdim=True)
        decoded = torch.cat([decoded, next_token], dim=1)
        if int(next_token.item()) == EOS:
            break
    return decode_text(decoded.squeeze(0), vocab)


def train_proof_transformer(
    corpus_path: str | Path,
    model_out: str | Path,
    report_out: str | Path,
    *,
    max_examples: int | None = 4096,
    corpus_report_path: str | Path | None = None,
    streaming: bool = False,
    vocab_sample_examples: int = 100_000,
    val_examples: int = 2048,
    max_steps: int = 100,
    batch_size: int = 16,
    d_model: int = 128,
    n_heads: int = 4,
    n_layers: int = 4,
    lr: float = 3e-4,
    seed: int = 9,
    max_input_len: int = 768,
    max_target_len: int = 512,
    max_vocab_chars: int = 512,
    progress_out: str | Path | None = None,
    progress_every: int = 100,
    checkpoint_every: int = 1000,
    resume_from: str | Path | None = None,
    commit_callback: Callable[[], None] | None = None,
) -> dict[str, Any]:
    random.seed(seed)
    torch.manual_seed(seed)
    files = _resolve_corpus_files(corpus_path)
    if not files:
        raise ValueError(f"no corpus files found for {corpus_path}")
    corpus_report = _load_report(corpus_report_path)
    rows = _jsonl_rows(corpus_path, max_rows=vocab_sample_examples if streaming else None)
    if not rows:
        raise ValueError("proof corpus is empty")
    random.shuffle(rows)
    if max_examples is not None and not streaming:
        rows = rows[:max_examples]
    split = max(1, int(0.9 * len(rows)))
    train_rows = rows[:split]
    val_rows = rows[split : split + val_examples] or rows[: min(len(rows), batch_size)]

    resume_checkpoint: dict[str, Any] | None = None
    resume_start_step = 0
    if resume_from is not None:
        resume_path = Path(resume_from)
        if not resume_path.exists():
            raise FileNotFoundError(f"resume checkpoint not found: {resume_path}")
        resume_checkpoint = torch.load(resume_path, map_location="cpu")
        resume_start_step = int(resume_checkpoint.get("step", 0))
        checkpoint_config = resume_checkpoint.get("config", {})
        d_model = int(checkpoint_config.get("d_model", d_model))
        n_heads = int(checkpoint_config.get("n_heads", n_heads))
        n_layers = int(checkpoint_config.get("n_layers", n_layers))
        max_input_len = int(checkpoint_config.get("max_input_len", max_input_len))
        max_target_len = int(checkpoint_config.get("max_target_len", max_target_len))
        vocab = ProofCharVocab.from_json(resume_checkpoint.get("vocab", {}))
        if not vocab.chars:
            raise ValueError(f"resume checkpoint has no usable vocab: {resume_path}")
    else:
        vocab = build_vocab(rows, max_chars=max_vocab_chars)

    train_ds = (
        StreamingProofCorpusDataset(files, vocab, max_input_len=max_input_len, max_target_len=max_target_len, seed=seed)
        if streaming
        else ProofCorpusTextDataset(train_rows, vocab, max_input_len=max_input_len, max_target_len=max_target_len)
    )
    val_ds = ProofCorpusTextDataset(val_rows, vocab, max_input_len=max_input_len, max_target_len=max_target_len)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=not streaming, collate_fn=collate_proof_batch)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_proof_batch)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TinySeq2SeqTransformer(
        vocab_size=len(vocab.chars) + CHAR_OFFSET,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        dropout=0.1,
        max_seq_len=max(max_input_len, max_target_len),
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    if resume_checkpoint is not None:
        model.load_state_dict(resume_checkpoint["model_state"])
        optimizer.load_state_dict(resume_checkpoint["optimizer_state"])
        _move_optimizer_state_to_device(optimizer, device)

    started = time.time()
    metrics: dict[str, float] = {}
    iterator = iter(train_loader)
    progress_every = max(1, int(progress_every))
    checkpoint_every = max(1, int(checkpoint_every))
    if resume_start_step >= max_steps:
        print(
            json.dumps(
                {
                    "proof_transformer_resume": {
                        "status": "CHECKPOINT_ALREADY_AT_OR_PAST_TARGET",
                        "resume_from": str(resume_from),
                        "resume_start_step": resume_start_step,
                        "max_steps": max_steps,
                    }
                },
                sort_keys=True,
            ),
            flush=True,
        )
    for step in range(resume_start_step + 1, max_steps + 1):
        try:
            batch = next(iterator)
        except StopIteration:
            iterator = iter(train_loader)
            batch = next(iterator)
        batch = {key: value.to(device) for key, value in batch.items()}
        loss = _loss(model, batch)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        metrics = {"train_loss": float(loss.item())}
        if step == 1 or step % progress_every == 0 or step == max_steps:
            elapsed = time.time() - started
            resumed_steps = max(step - resume_start_step, 1)
            steps_per_second = resumed_steps / max(elapsed, 1e-9)
            eta_seconds = (max_steps - step) / max(steps_per_second, 1e-9)
            progress = {
                "schema": "collatz_lab.proof_transformer_progress",
                "status": "RUNNING" if step < max_steps else "FINALIZING",
                "step": step,
                "resume_start_step": resume_start_step,
                "max_steps": max_steps,
                "progress_percent": 100.0 * step / max(max_steps, 1),
                "train_loss": float(loss.item()),
                "elapsed_seconds": elapsed,
                "steps_per_second": steps_per_second,
                "eta_seconds": eta_seconds,
                "examples_seen": step * batch_size,
                "parameter_count": parameter_count,
                "device": str(device),
                "model_out": str(model_out),
                "report_out": str(report_out),
                "resume_from": None if resume_from is None else str(resume_from),
            }
            _write_json(progress_out, progress)
            print(json.dumps({"proof_transformer_progress": progress}, sort_keys=True), flush=True)
            if commit_callback is not None:
                commit_callback()
        if step % checkpoint_every == 0 or step == max_steps:
            model_path = Path(model_out)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                _checkpoint_payload(
                    model,
                    optimizer,
                    vocab,
                    d_model=d_model,
                    n_heads=n_heads,
                    n_layers=n_layers,
                    max_input_len=max_input_len,
                    max_target_len=max_target_len,
                    step=step,
                ),
                model_path,
            )
            print(json.dumps({"proof_transformer_checkpoint": {"path": str(model_path), "step": step}}), flush=True)
            if commit_callback is not None:
                commit_callback()

    val_loss = _eval_loss(model, val_loader, device=device)
    checkpoint = _checkpoint_payload(
        model,
        optimizer,
        vocab,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        max_input_len=max_input_len,
        max_target_len=max_target_len,
        step=max_steps,
    )
    model_path = Path(model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, model_path)

    source_counts = Counter(str(row.get("source")) for row in rows)
    if corpus_report and corpus_report.get("source_counts"):
        source_counts = Counter({str(k): int(v) for k, v in corpus_report["source_counts"].items()})
    example_count = int((corpus_report or {}).get("example_count", len(rows)))
    report = {
        "schema": PROOF_TRANSFORMER_REPORT_SCHEMA,
        "version": 1,
        "status": "TRAINED_SHARED_PROOF_TRANSFORMER_SMOKE"
        if max_steps < 1000 or parameter_count < 100_000_000
        else "TRAINED_SHARED_PROOF_TRANSFORMER",
        "model_kind": "shared Transformer proof model",
        "model_path": str(model_path),
        "corpus_path": str(corpus_path),
        "corpus_report_path": None if corpus_report_path is None else str(corpus_report_path),
        "example_count": example_count,
        "training_examples_seen": max_steps * batch_size,
        "streaming": streaming,
        "train_rows": "streaming" if streaming else len(train_rows),
        "val_rows": len(val_rows),
        "train_steps_completed": max_steps,
        "resume_from": None if resume_from is None else str(resume_from),
        "resume_start_step": resume_start_step,
        "resumed": resume_checkpoint is not None,
        "parameter_count": parameter_count,
        "source_counts": dict(source_counts),
        "metrics": {**metrics, "val_loss": val_loss},
        "elapsed_seconds": time.time() - started,
        "scaling_law_readiness": {
            "has_general_proof_stream": any("formal" in source for source in source_counts),
            "has_collatz_structural_stream": any("high_parent" in source or "cycle" in source for source in source_counts),
            "has_verifier_replay_stream": any("verifier" in source or "replay" in source for source in source_counts),
            "shared_target": "proof DSL + repair action + verifier outcome",
        },
        "caveat": (
            "Small local settings are smoke tests. RUN-009 serious readiness is controlled by run9_preflight "
            "parameter-count and training-step thresholds."
        ),
    }
    report_path = Path(report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def write_training_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Proof Transformer Training",
        "",
        f"- status: `{report['status']}`",
        f"- model kind: `{report['model_kind']}`",
        f"- examples used: `{report['example_count']}`",
        f"- train steps: `{report['train_steps_completed']}`",
        f"- parameters: `{report['parameter_count']}`",
        f"- metrics: `{report['metrics']}`",
        f"- scaling readiness: `{report['scaling_law_readiness']}`",
        "",
        str(report["caveat"]),
        "",
    ]
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a proof-corpus Transformer smoke/scaling model.")
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--corpus-report", default=None)
    parser.add_argument("--model-out", required=True)
    parser.add_argument("--report-out", required=True)
    parser.add_argument("--report-md", default=None)
    parser.add_argument("--max-examples", type=int, default=4096)
    parser.add_argument("--streaming", action="store_true")
    parser.add_argument("--vocab-sample-examples", type=int, default=100000)
    parser.add_argument("--val-examples", type=int, default=2048)
    parser.add_argument("--max-steps", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--n-heads", type=int, default=4)
    parser.add_argument("--n-layers", type=int, default=4)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--max-input-len", type=int, default=768)
    parser.add_argument("--max-target-len", type=int, default=512)
    parser.add_argument("--max-vocab-chars", type=int, default=512)
    parser.add_argument("--progress-out", default=None)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--checkpoint-every", type=int, default=1000)
    parser.add_argument("--resume-from", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = train_proof_transformer(
        args.corpus,
        args.model_out,
        args.report_out,
        max_examples=args.max_examples,
        corpus_report_path=args.corpus_report,
        streaming=args.streaming,
        vocab_sample_examples=args.vocab_sample_examples,
        val_examples=args.val_examples,
        max_steps=args.max_steps,
        batch_size=args.batch_size,
        d_model=args.d_model,
        n_heads=args.n_heads,
        n_layers=args.n_layers,
        lr=args.lr,
        max_input_len=args.max_input_len,
        max_target_len=args.max_target_len,
        max_vocab_chars=args.max_vocab_chars,
        progress_out=args.progress_out,
        progress_every=args.progress_every,
        checkpoint_every=args.checkpoint_every,
        resume_from=args.resume_from,
    )
    write_training_markdown(report, args.report_md or Path(args.report_out).with_suffix(".md"))
    Console().print(
        {
            "model": report["model_path"],
            "report": args.report_out,
            "steps": report["train_steps_completed"],
            "parameters": report["parameter_count"],
            "val_loss": report["metrics"]["val_loss"],
        }
    )


if __name__ == "__main__":
    main()
