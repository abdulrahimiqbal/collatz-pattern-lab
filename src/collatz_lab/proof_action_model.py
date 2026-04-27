"""Policy/value Transformer for typed proof-action generation."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import random
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from rich.console import Console
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

from .models import PositionalEncoding, masked_mean
from .proof_action_tokenizer import BOS, EOS, PAD, SPECIAL_TOKENS, ProofActionTokenizer, build_tokenizer, pad_1d
from .utils import load_yaml, save_yaml


PROOF_ACTION_MODEL_REPORT_SCHEMA = "collatz_lab.proof_action_model_training_report"


class ProofActionSeq2Seq(nn.Module):
    """Encoder-decoder policy with a shared encoder value head."""

    def __init__(
        self,
        *,
        vocab_size: int,
        d_model: int = 384,
        encoder_layers: int = 8,
        decoder_layers: int = 6,
        heads: int = 6,
        ffn_dim: int = 1536,
        dropout: float = 0.1,
        max_seq_len: int = 2048,
        use_value_head: bool = True,
        use_ranker_head: bool = False,
    ) -> None:
        super().__init__()
        self.use_value_head = use_value_head
        self.use_ranker_head = use_ranker_head
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position = PositionalEncoding(d_model, max_seq_len=max_seq_len, dropout=dropout)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        dec_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=encoder_layers, enable_nested_tensor=False)
        self.decoder = nn.TransformerDecoder(dec_layer, num_layers=decoder_layers)
        self.output = nn.Linear(d_model, vocab_size)
        self.value_head = nn.Sequential(nn.LayerNorm(d_model), nn.Linear(d_model, 1))
        self.ranker_head = nn.Sequential(
            nn.LayerNorm(d_model * 4),
            nn.Linear(d_model * 4, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, 1),
        )

    def encode(self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None) -> torch.Tensor:
        hidden = self.position(self.token_embedding(input_ids))
        key_padding = ~attention_mask.bool() if attention_mask is not None else None
        return self.encoder(hidden, src_key_padding_mask=key_padding)

    def forward(
        self,
        input_ids: torch.Tensor,
        decoder_input_ids: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
        action_input_ids: torch.Tensor | None = None,
        action_attention_mask: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor | None]:
        memory = self.encode(input_ids, attention_mask=attention_mask)
        pooled = masked_mean(memory, attention_mask)
        logits = None
        if decoder_input_ids is not None and decoder_input_ids.numel() > 0:
            tgt = self.position(self.token_embedding(decoder_input_ids))
            tgt_len = decoder_input_ids.size(1)
            causal = nn.Transformer.generate_square_subsequent_mask(tgt_len, device=tgt.device)
            memory_key_padding = ~attention_mask.bool() if attention_mask is not None else None
            decoded = self.decoder(tgt, memory, tgt_mask=causal, memory_key_padding_mask=memory_key_padding)
            logits = self.output(decoded)
        rank_score = None
        if action_input_ids is not None:
            rank_score = self.rank_actions_from_pooled(
                pooled,
                action_input_ids,
                action_attention_mask=action_attention_mask,
            )
        value = self.value_head(pooled).squeeze(-1) if self.use_value_head else None
        return {"logits": logits, "value": value, "pooled": pooled, "rank_score": rank_score}

    def rank_actions_from_pooled(
        self,
        state_pooled: torch.Tensor,
        action_input_ids: torch.Tensor,
        *,
        action_attention_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        action_memory = self.encode(action_input_ids, attention_mask=action_attention_mask)
        action_pooled = masked_mean(action_memory, action_attention_mask)
        features = torch.cat(
            [state_pooled, action_pooled, torch.abs(state_pooled - action_pooled), state_pooled * action_pooled],
            dim=-1,
        )
        return self.ranker_head(features).squeeze(-1)

    def rank_actions(
        self,
        input_ids: torch.Tensor,
        action_input_ids: torch.Tensor,
        *,
        attention_mask: torch.Tensor | None = None,
        action_attention_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        memory = self.encode(input_ids, attention_mask=attention_mask)
        pooled = masked_mean(memory, attention_mask)
        return self.rank_actions_from_pooled(pooled, action_input_ids, action_attention_mask=action_attention_mask)


def _resolve_rows(path: str | Path) -> list[dict[str, Any]]:
    text = str(path)
    files: list[Path]
    if any(char in text for char in "*?[]"):
        files = [Path(item) for item in sorted(glob.glob(text))]
    elif Path(path).is_dir():
        files = sorted(Path(path).glob("*.jsonl"))
    else:
        files = [Path(path)]
    rows: list[dict[str, Any]] = []
    for file_path in files:
        if not file_path.exists():
            continue
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


@dataclass
class TrainConfig:
    rows_path: str
    output_dir: str
    pairs_path: str | None = None
    max_state_len: int = 2048
    max_action_len: int = 128
    max_vocab_size: int = 16384
    d_model: int = 384
    encoder_layers: int = 8
    decoder_layers: int = 6
    heads: int = 6
    ffn_dim: int = 1536
    dropout: float = 0.1
    batch_size: int = 16
    max_steps: int = 1000
    lr: float = 2e-4
    weight_decay: float = 0.01
    warmup_steps: int = 1000
    policy_loss_weight: float = 1.0
    value_loss_weight: float = 0.3
    ranker_loss_weight: float = 0.7
    gradient_clip: float = 1.0
    seed: int = 1337
    checkpoint_every: int = 500
    progress_every: int = 50
    bf16: bool = False
    use_value_head: bool = True
    use_ranker_head: bool = False
    pair_batch_size: int = 16
    train_splits: tuple[str, ...] = ("train",)
    val_splits: tuple[str, ...] = ("val", "test", "challenge")
    init_checkpoint: str | None = None
    s6_policy_loss_weight: float = 1.0
    hard_trace_policy_loss_weight: float = 1.0
    accepted_good_vs_dead_end_pair_weight: float = 1.0


def _as_tuple(value: Any, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def config_from_yaml(path: str | Path) -> TrainConfig:
    cfg = load_yaml(path)
    data = cfg.get("data", {})
    model = cfg.get("model", {})
    training = cfg.get("training", {})
    loss = cfg.get("loss", {})
    output = cfg.get("output", {})
    rows_path = str(data.get("rows") or data.get("dataset") or Path(data.get("dir", "data/proof_action_v2")) / "rows.jsonl")
    return TrainConfig(
        rows_path=rows_path,
        output_dir=str(output.get("dir") or cfg.get("output_dir") or "reports/proof_action_v2/run"),
        pairs_path=str(data.get("pairs") or Path(data.get("dir", Path(rows_path).parent)) / "train_pairs.jsonl")
        if data.get("pairs") or data.get("dir")
        else None,
        max_state_len=int(model.get("max_state_len", 2048)),
        max_action_len=int(model.get("max_action_len", 128)),
        max_vocab_size=int(model.get("max_vocab_size", 16384)),
        d_model=int(model.get("d_model", 384)),
        encoder_layers=int(model.get("encoder_layers", 8)),
        decoder_layers=int(model.get("decoder_layers", 6)),
        heads=int(model.get("heads", 6)),
        ffn_dim=int(model.get("ffn_dim", 1536)),
        dropout=float(model.get("dropout", 0.1)),
        batch_size=int(training.get("batch_size", 16)),
        max_steps=int(training.get("max_steps", 1000)),
        lr=float(training.get("lr", 2e-4)),
        weight_decay=float(training.get("weight_decay", 0.01)),
        warmup_steps=int(training.get("warmup_steps", 1000)),
        policy_loss_weight=float(loss.get("policy_weight", training.get("policy_loss_weight", 1.0))),
        value_loss_weight=float(loss.get("value_weight", training.get("value_loss_weight", 0.3))),
        ranker_loss_weight=float(loss.get("ranker_weight", training.get("ranker_loss_weight", 0.7))),
        gradient_clip=float(training.get("gradient_clip", 1.0)),
        seed=int(training.get("seed", 1337)),
        checkpoint_every=int(training.get("checkpoint_every", 500)),
        progress_every=int(training.get("progress_every", 50)),
        bf16=bool(training.get("bf16", False)),
        use_value_head=bool(model.get("use_value_head", True)),
        use_ranker_head=bool(model.get("use_ranker_head", False)),
        pair_batch_size=int(training.get("pair_batch_size", training.get("batch_size", 16))),
        train_splits=_as_tuple(data.get("train_splits"), ("train",)),
        val_splits=_as_tuple(data.get("val_splits"), ("val", "test", "challenge")),
        init_checkpoint=model.get("init_checkpoint") or training.get("init_checkpoint"),
        s6_policy_loss_weight=float(loss.get("s6_policy_weight", 1.0)),
        hard_trace_policy_loss_weight=float(loss.get("hard_trace_policy_weight", 1.0)),
        accepted_good_vs_dead_end_pair_weight=float(loss.get("accepted_good_vs_dead_end_pair_weight", 1.0)),
    )


class ProofActionRows(Dataset[dict[str, torch.Tensor]]):
    def __init__(self, rows: list[dict[str, Any]], tokenizer: ProofActionTokenizer, cfg: TrainConfig) -> None:
        self.rows = rows
        self.tokenizer = tokenizer
        self.cfg = cfg

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self.rows[index]
        reward = float(row.get("reward", 0.0) or 0.0)
        value_target = 1.0 if row.get("eventually_closed") else max(0.0, min(1.0, reward))
        accepted = 1.0 if row.get("verifier_status") == "ACCEPT" else 0.0
        source_family = str(row.get("source_family") or row.get("mix_source") or row.get("source") or "")
        sample_weight = float(row.get("sample_weight", 1.0) or 1.0)
        hard_flag = 1.0 if "hard_trace" in source_family or "frontier_gate_progress" in source_family else 0.0
        s6_flag = 1.0 if str(row.get("gate", "")).startswith("S6") or "s6" in source_family else 0.0
        original_flag = 1.0 if source_family.startswith("original") else 0.0
        return {
            "input_ids": self.tokenizer.encode(str(row["state"]), self.cfg.max_state_len),
            "target_ids": self.tokenizer.encode(str(row["target_action_text"]), self.cfg.max_action_len),
            "value_target": torch.tensor(value_target, dtype=torch.float),
            "policy_weight": torch.tensor(accepted, dtype=torch.float),
            "sample_weight": torch.tensor(sample_weight, dtype=torch.float),
            "hard_trace_flag": torch.tensor(hard_flag, dtype=torch.float),
            "s6_flag": torch.tensor(s6_flag, dtype=torch.float),
            "original_flag": torch.tensor(original_flag, dtype=torch.float),
        }


class ProofActionPairRows(Dataset[dict[str, torch.Tensor]]):
    def __init__(self, rows: list[dict[str, Any]], tokenizer: ProofActionTokenizer, cfg: TrainConfig) -> None:
        self.rows = rows
        self.tokenizer = tokenizer
        self.cfg = cfg

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self.rows[index]
        sample_weight = float(row.get("sample_weight", 1.0) or 1.0)
        if row.get("reason") == "accepted_good_vs_accepted_dead_end":
            sample_weight *= self.cfg.accepted_good_vs_dead_end_pair_weight
        return {
            "input_ids": self.tokenizer.encode(str(row["state"]), self.cfg.max_state_len),
            "better_ids": self.tokenizer.encode(str(row["better_action"]), self.cfg.max_action_len),
            "worse_ids": self.tokenizer.encode(str(row["worse_action"]), self.cfg.max_action_len),
            "sample_weight": torch.tensor(sample_weight, dtype=torch.float),
            "dead_end_pair_flag": torch.tensor(1.0 if row.get("reason") == "accepted_good_vs_accepted_dead_end" else 0.0, dtype=torch.float),
        }


def collate_action_batch(batch: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
    input_ids = pad_1d([row["input_ids"] for row in batch], pad_value=PAD)
    target_ids = pad_1d([row["target_ids"] for row in batch], pad_value=PAD)
    return {
        "input_ids": input_ids,
        "target_ids": target_ids,
        "attention_mask": input_ids.ne(PAD),
        "value_target": torch.stack([row["value_target"] for row in batch]),
        "policy_weight": torch.stack([row["policy_weight"] for row in batch]),
        "sample_weight": torch.stack([row["sample_weight"] for row in batch]),
        "hard_trace_flag": torch.stack([row["hard_trace_flag"] for row in batch]),
        "s6_flag": torch.stack([row["s6_flag"] for row in batch]),
        "original_flag": torch.stack([row["original_flag"] for row in batch]),
    }


def collate_pair_batch(batch: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
    input_ids = pad_1d([row["input_ids"] for row in batch], pad_value=PAD)
    better_ids = pad_1d([row["better_ids"] for row in batch], pad_value=PAD)
    worse_ids = pad_1d([row["worse_ids"] for row in batch], pad_value=PAD)
    return {
        "input_ids": input_ids,
        "attention_mask": input_ids.ne(PAD),
        "better_ids": better_ids,
        "better_attention_mask": better_ids.ne(PAD),
        "worse_ids": worse_ids,
        "worse_attention_mask": worse_ids.ne(PAD),
        "sample_weight": torch.stack([row["sample_weight"] for row in batch]),
        "dead_end_pair_flag": torch.stack([row["dead_end_pair_flag"] for row in batch]),
    }


def _loss(model: ProofActionSeq2Seq, batch: dict[str, torch.Tensor], cfg: TrainConfig) -> tuple[torch.Tensor, dict[str, float]]:
    decoder_input = batch["target_ids"][:, :-1]
    labels = batch["target_ids"][:, 1:].contiguous()
    outputs = model(batch["input_ids"], decoder_input_ids=decoder_input, attention_mask=batch["attention_mask"])
    logits = outputs["logits"]
    assert logits is not None
    token_loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), labels.reshape(-1), ignore_index=PAD, reduction="none")
    token_loss = token_loss.reshape(labels.shape)
    token_mask = labels.ne(PAD).float()
    per_row = (token_loss * token_mask).sum(dim=1) / token_mask.sum(dim=1).clamp_min(1.0)
    row_weight = batch.get("sample_weight", torch.ones_like(batch["policy_weight"]))
    row_weight = row_weight * (1.0 + (cfg.hard_trace_policy_loss_weight - 1.0) * batch.get("hard_trace_flag", torch.zeros_like(row_weight)))
    row_weight = row_weight * (1.0 + (cfg.s6_policy_loss_weight - 1.0) * batch.get("s6_flag", torch.zeros_like(row_weight)))
    policy_weight = batch["policy_weight"] * row_weight
    policy_loss = (per_row * policy_weight).sum() / policy_weight.sum().clamp_min(1.0)
    value_logits = outputs["value"]
    if value_logits is not None:
        value_per_row = F.binary_cross_entropy_with_logits(value_logits, batch["value_target"], reduction="none")
        value_loss = (value_per_row * row_weight).sum() / row_weight.sum().clamp_min(1.0)
    else:
        value_loss = policy_loss.new_tensor(0.0)
    loss = cfg.policy_loss_weight * policy_loss + cfg.value_loss_weight * value_loss
    hard_mask = batch.get("hard_trace_flag", torch.zeros_like(per_row)) > 0
    s6_mask = batch.get("s6_flag", torch.zeros_like(per_row)) > 0
    original_mask = batch.get("original_flag", torch.zeros_like(per_row)) > 0

    def masked_policy(mask: torch.Tensor) -> float:
        weight = policy_weight * mask.float()
        if float(weight.sum().detach().item()) <= 0.0:
            return 0.0
        return float(((per_row * weight).sum() / weight.sum().clamp_min(1.0)).detach().item())

    return loss, {
        "policy_loss": float(policy_loss.detach().item()),
        "value_loss": float(value_loss.detach().item()),
        "hard_trace_loss": masked_policy(hard_mask),
        "s6_loss": masked_policy(s6_mask),
        "original_replay_loss": masked_policy(original_mask),
    }


def _ranker_loss(model: ProofActionSeq2Seq, batch: dict[str, torch.Tensor]) -> tuple[torch.Tensor, dict[str, float]]:
    state_ids = batch["input_ids"]
    state_mask = batch["attention_mask"]
    better = model.rank_actions(
        state_ids,
        batch["better_ids"],
        attention_mask=state_mask,
        action_attention_mask=batch["better_attention_mask"],
    )
    worse = model.rank_actions(
        state_ids,
        batch["worse_ids"],
        attention_mask=state_mask,
        action_attention_mask=batch["worse_attention_mask"],
    )
    margin = better - worse
    per_row = F.softplus(-margin)
    weights = batch.get("sample_weight", torch.ones_like(per_row))
    loss = (per_row * weights).sum() / weights.sum().clamp_min(1.0)
    dead_mask = batch.get("dead_end_pair_flag", torch.zeros_like(per_row)) > 0
    dead_loss = (per_row[dead_mask].mean() if dead_mask.any() else per_row.new_tensor(0.0))
    return loss, {
        "ranker_loss": float(loss.detach().item()),
        "ranker_margin": float(margin.detach().mean().item()),
        "pairwise_dead_end_loss": float(dead_loss.detach().item()),
    }


def _lr_scale(step: int, max_steps: int, warmup_steps: int) -> float:
    if warmup_steps > 0 and step <= warmup_steps:
        return step / warmup_steps
    progress = (step - warmup_steps) / max(max_steps - warmup_steps, 1)
    return 0.5 * (1.0 + math.cos(math.pi * min(1.0, max(0.0, progress))))


def _checkpoint_payload(
    model: ProofActionSeq2Seq,
    optimizer: torch.optim.Optimizer,
    tokenizer: ProofActionTokenizer,
    cfg: TrainConfig,
    step: int,
    action_memory: dict[str, str],
) -> dict[str, Any]:
    return {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "tokenizer": tokenizer.to_json(),
        "config": cfg.__dict__,
        "step": step,
        "action_memory": action_memory,
    }


def _state_key(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def load_checkpoint(path: str | Path, *, device: torch.device | None = None) -> tuple[ProofActionSeq2Seq, ProofActionTokenizer, dict[str, Any]]:
    checkpoint = torch.load(path, map_location="cpu")
    tokenizer = ProofActionTokenizer.from_json(checkpoint["tokenizer"])
    cfg_data = dict(checkpoint.get("config") or {})
    target_device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ProofActionSeq2Seq(
        vocab_size=tokenizer.vocab_size,
        d_model=int(cfg_data.get("d_model", 384)),
        encoder_layers=int(cfg_data.get("encoder_layers", 8)),
        decoder_layers=int(cfg_data.get("decoder_layers", 6)),
        heads=int(cfg_data.get("heads", 6)),
        ffn_dim=int(cfg_data.get("ffn_dim", 1536)),
        dropout=0.0,
        max_seq_len=max(int(cfg_data.get("max_state_len", 2048)), int(cfg_data.get("max_action_len", 128))),
        use_value_head=bool(cfg_data.get("use_value_head", True)),
        use_ranker_head=bool(cfg_data.get("use_ranker_head", False)),
    ).to(target_device)
    model.load_state_dict(checkpoint["model_state"], strict=False)
    model.eval()
    return model, tokenizer, checkpoint


def _load_init_checkpoint_weights(model: ProofActionSeq2Seq, tokenizer: ProofActionTokenizer, init_checkpoint: str | Path) -> dict[str, Any]:
    """Warm-start from a checkpoint, expanding token embeddings by token text."""

    checkpoint = torch.load(init_checkpoint, map_location="cpu")
    old_tokenizer = ProofActionTokenizer.from_json(checkpoint["tokenizer"])
    old_state = checkpoint["model_state"]
    current = model.state_dict()
    copied: list[str] = []
    skipped: list[str] = []
    for key, value in old_state.items():
        if key not in current:
            skipped.append(key)
            continue
        if current[key].shape == value.shape:
            current[key] = value
            copied.append(key)
            continue
        if key == "token_embedding.weight" and current[key].dim() == 2 and value.dim() == 2:
            merged = current[key].clone()
            merged[: min(len(SPECIAL_TOKENS), merged.size(0), value.size(0))] = value[
                : min(len(SPECIAL_TOKENS), merged.size(0), value.size(0))
            ]
            for token, old_index in old_tokenizer.token_to_id.items():
                new_index = tokenizer.token_to_id.get(token)
                if new_index is not None and old_index < value.size(0) and new_index < merged.size(0):
                    merged[new_index] = value[old_index]
            current[key] = merged
            copied.append(key)
            continue
        if key == "output.weight" and current[key].dim() == 2 and value.dim() == 2:
            merged = current[key].clone()
            merged[: min(len(SPECIAL_TOKENS), merged.size(0), value.size(0))] = value[
                : min(len(SPECIAL_TOKENS), merged.size(0), value.size(0))
            ]
            for token, old_index in old_tokenizer.token_to_id.items():
                new_index = tokenizer.token_to_id.get(token)
                if new_index is not None and old_index < value.size(0) and new_index < merged.size(0):
                    merged[new_index] = value[old_index]
            current[key] = merged
            copied.append(key)
            continue
        if key == "output.bias" and current[key].dim() == 1 and value.dim() == 1:
            merged = current[key].clone()
            merged[: min(len(SPECIAL_TOKENS), merged.size(0), value.size(0))] = value[
                : min(len(SPECIAL_TOKENS), merged.size(0), value.size(0))
            ]
            for token, old_index in old_tokenizer.token_to_id.items():
                new_index = tokenizer.token_to_id.get(token)
                if new_index is not None and old_index < value.size(0) and new_index < merged.size(0):
                    merged[new_index] = value[old_index]
            current[key] = merged
            copied.append(key)
            continue
        skipped.append(key)
    model.load_state_dict(current, strict=False)
    return {
        "init_checkpoint": str(init_checkpoint),
        "copied_tensor_count": len(copied),
        "skipped_tensor_count": len(skipped),
        "old_vocab_size": old_tokenizer.vocab_size,
        "new_vocab_size": tokenizer.vocab_size,
    }


def _sample_weights(rows: list[dict[str, Any]]) -> list[float]:
    weights = []
    for row in rows:
        try:
            weights.append(max(1e-6, float(row.get("sample_weight", 1.0) or 1.0)))
        except Exception:
            weights.append(1.0)
    return weights


@torch.no_grad()
def greedy_generate_action_text(
    model: ProofActionSeq2Seq,
    tokenizer: ProofActionTokenizer,
    state: str,
    *,
    max_state_len: int,
    max_action_len: int,
) -> str:
    device = next(model.parameters()).device
    input_ids = tokenizer.encode(state, max_state_len).unsqueeze(0).to(device)
    attention_mask = input_ids.ne(PAD)
    decoded = torch.tensor([[BOS]], dtype=torch.long, device=device)
    for _ in range(max_action_len - 1):
        outputs = model(input_ids, decoder_input_ids=decoded, attention_mask=attention_mask)
        logits = outputs["logits"]
        assert logits is not None
        next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
        decoded = torch.cat([decoded, next_token], dim=1)
        if int(next_token.item()) == EOS:
            break
    return tokenizer.decode(decoded.squeeze(0))


@torch.no_grad()
def score_action_components(
    model: ProofActionSeq2Seq,
    tokenizer: ProofActionTokenizer,
    state: str,
    action_texts: list[str],
    *,
    max_state_len: int,
    max_action_len: int,
) -> list[dict[str, float]]:
    if not action_texts:
        return []
    device = next(model.parameters()).device
    input_one = tokenizer.encode(state, max_state_len)
    action_ids = [tokenizer.encode(text, max_action_len) for text in action_texts]
    input_ids = pad_1d([input_one for _ in action_texts], pad_value=PAD).to(device)
    target_ids = pad_1d(action_ids, pad_value=PAD).to(device)
    attention_mask = input_ids.ne(PAD)
    decoder_input = target_ids[:, :-1]
    labels = target_ids[:, 1:].contiguous()
    outputs = model(input_ids, decoder_input_ids=decoder_input, attention_mask=attention_mask)
    logits = outputs["logits"]
    assert logits is not None
    log_probs = torch.log_softmax(logits, dim=-1)
    gathered = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    mask = labels.ne(PAD)
    policy_scores = (gathered * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
    values = outputs["value"]
    value_scores = torch.sigmoid(values) if values is not None else torch.zeros_like(policy_scores)
    rank_scores = model.rank_actions(
        input_ids,
        target_ids,
        attention_mask=attention_mask,
        action_attention_mask=target_ids.ne(PAD),
    )
    return [
        {
            "policy_score": float(policy_scores[index].item()),
            "value_score": float(value_scores[index].item()),
            "ranker_score": float(rank_scores[index].item()),
        }
        for index in range(len(action_texts))
    ]


@torch.no_grad()
def score_action_texts(
    model: ProofActionSeq2Seq,
    tokenizer: ProofActionTokenizer,
    state: str,
    action_texts: list[str],
    *,
    max_state_len: int,
    max_action_len: int,
) -> list[float]:
    components = score_action_components(
        model,
        tokenizer,
        state,
        action_texts,
        max_state_len=max_state_len,
        max_action_len=max_action_len,
    )
    scores = []
    for item in components:
        score = item["policy_score"]
        score += 0.05 * item["value_score"]
        score += 0.05 * item["ranker_score"]
        scores.append(float(score))
    return scores


def train(config_path: str | Path) -> dict[str, Any]:
    cfg = config_from_yaml(config_path)
    random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)
    rows = _resolve_rows(cfg.rows_path)
    if not rows:
        raise ValueError(f"no proof-action rows found at {cfg.rows_path}")
    pair_rows = _resolve_rows(cfg.pairs_path) if cfg.pairs_path and Path(cfg.pairs_path).exists() else []
    train_rows = [row for row in rows if row.get("split") in cfg.train_splits]
    val_rows = [row for row in rows if row.get("split") in cfg.val_splits] or rows[: min(len(rows), 64)]
    if not train_rows:
        train_rows = rows
    vocab_rows = list(rows)
    for pair in pair_rows[: max(len(rows), 1)]:
        vocab_rows.append({"state": pair.get("state", ""), "target_action_text": pair.get("better_action", "")})
        vocab_rows.append({"state": pair.get("state", ""), "target_action_text": pair.get("worse_action", "")})
    tokenizer = build_tokenizer(vocab_rows, max_vocab_size=cfg.max_vocab_size)

    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer.save(output_dir / "vocab.json")
    save_yaml({"resolved": cfg.__dict__}, output_dir / "train_config_resolved.yaml")
    shutil.copy2(config_path, output_dir / "train_config_source.yaml")

    train_ds = ProofActionRows(train_rows, tokenizer, cfg)
    val_ds = ProofActionRows(val_rows, tokenizer, cfg)
    train_weights = _sample_weights(train_rows)
    train_sampler = WeightedRandomSampler(train_weights, num_samples=max(len(train_weights), cfg.batch_size), replacement=True) if any(abs(weight - 1.0) > 1e-9 for weight in train_weights) else None
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=train_sampler is None, sampler=train_sampler, collate_fn=collate_action_batch)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, collate_fn=collate_action_batch)
    pair_loader = None
    if pair_rows and cfg.ranker_loss_weight > 0:
        train_pair_rows = [row for row in pair_rows if row.get("split") in cfg.train_splits] or pair_rows
        pair_ds = ProofActionPairRows(train_pair_rows, tokenizer, cfg)
        pair_weights = _sample_weights(train_pair_rows)
        pair_sampler = WeightedRandomSampler(pair_weights, num_samples=max(len(pair_weights), cfg.pair_batch_size), replacement=True) if any(abs(weight - 1.0) > 1e-9 for weight in pair_weights) else None
        pair_loader = DataLoader(pair_ds, batch_size=cfg.pair_batch_size, shuffle=pair_sampler is None, sampler=pair_sampler, collate_fn=collate_pair_batch)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ProofActionSeq2Seq(
        vocab_size=tokenizer.vocab_size,
        d_model=cfg.d_model,
        encoder_layers=cfg.encoder_layers,
        decoder_layers=cfg.decoder_layers,
        heads=cfg.heads,
        ffn_dim=cfg.ffn_dim,
        dropout=cfg.dropout,
        max_seq_len=max(cfg.max_state_len, cfg.max_action_len),
        use_value_head=cfg.use_value_head,
        use_ranker_head=cfg.use_ranker_head,
    )
    init_report: dict[str, Any] | None = None
    if cfg.init_checkpoint:
        init_path = Path(cfg.init_checkpoint)
        if init_path.exists():
            init_report = _load_init_checkpoint_weights(model, tokenizer, init_path)
        else:
            init_report = {"init_checkpoint": str(init_path), "loaded": False, "reason": "not found"}
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    action_memory = {
        _state_key(str(row["state"])): str(row["target_action_text"])
        for row in train_rows
        if row.get("verifier_status") == "ACCEPT"
    }

    iterator = iter(train_loader)
    pair_iterator = iter(pair_loader) if pair_loader is not None else None
    started = time.time()
    latest_metrics: dict[str, float] = {}
    for step in range(1, cfg.max_steps + 1):
        try:
            batch = next(iterator)
        except StopIteration:
            iterator = iter(train_loader)
            batch = next(iterator)
        batch = {key: value.to(device) for key, value in batch.items()}
        for group in optimizer.param_groups:
            group["lr"] = cfg.lr * _lr_scale(step, cfg.max_steps, cfg.warmup_steps)
        model.train()
        loss, loss_parts = _loss(model, batch, cfg)
        if pair_loader is not None and pair_iterator is not None:
            try:
                pair_batch = next(pair_iterator)
            except StopIteration:
                pair_iterator = iter(pair_loader)
                pair_batch = next(pair_iterator)
            pair_batch = {key: value.to(device) for key, value in pair_batch.items()}
            rank_loss, rank_parts = _ranker_loss(model, pair_batch)
            loss = loss + cfg.ranker_loss_weight * rank_loss
            loss_parts.update(rank_parts)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.gradient_clip)
        optimizer.step()
        latest_metrics = {"train_loss": float(loss.item()), **loss_parts, "lr": float(optimizer.param_groups[0]["lr"])}

        if step == 1 or step % cfg.progress_every == 0 or step == cfg.max_steps:
            elapsed = time.time() - started
            progress = {
                "schema": "collatz_lab.proof_action_model_progress",
                "status": "RUNNING" if step < cfg.max_steps else "FINALIZING",
                "step": step,
                "max_steps": cfg.max_steps,
                "progress_percent": 100.0 * step / max(cfg.max_steps, 1),
                "elapsed_seconds": elapsed,
                "steps_per_second": step / max(elapsed, 1e-9),
                "parameter_count": parameter_count,
                "device": str(device),
                "total_loss": latest_metrics.get("train_loss", 0.0),
                "hard_trace_loss": latest_metrics.get("hard_trace_loss", 0.0),
                "s6_loss": latest_metrics.get("s6_loss", 0.0),
                "original_replay_loss": latest_metrics.get("original_replay_loss", 0.0),
                "validation_hard_close_metrics": {},
                "validation_s6_metrics": {},
                **latest_metrics,
            }
            (output_dir / "progress.json").write_text(json.dumps(progress, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps({"proof_action_progress": progress}, sort_keys=True), flush=True)

        if step % cfg.checkpoint_every == 0 or step == cfg.max_steps:
            torch.save(
                _checkpoint_payload(model, optimizer, tokenizer, cfg, step, action_memory),
                output_dir / f"checkpoint_step_{step}.pt",
            )

    model.eval()
    val_losses = []
    with torch.no_grad():
        for index, batch in enumerate(val_loader):
            if index >= 10:
                break
            batch = {key: value.to(device) for key, value in batch.items()}
            val_loss, _ = _loss(model, batch, cfg)
            val_losses.append(float(val_loss.item()))
    final_checkpoint = output_dir / "final_checkpoint.pt"
    torch.save(_checkpoint_payload(model, optimizer, tokenizer, cfg, cfg.max_steps, action_memory), final_checkpoint)
    report = {
        "schema": PROOF_ACTION_MODEL_REPORT_SCHEMA,
        "version": 1,
        "status": "TRAINED_PROOF_ACTION_V2_POLICY_VALUE",
        "model_name": "CollatzProofAction-v2",
        "config_path": str(config_path),
        "rows_path": cfg.rows_path,
        "output_dir": str(output_dir),
        "checkpoint_path": str(final_checkpoint),
        "row_count": len(rows),
        "pair_rows": len(pair_rows),
        "train_rows": len(train_rows),
        "val_rows": len(val_rows),
        "train_steps_completed": cfg.max_steps,
        "parameter_count": parameter_count,
        "init_checkpoint_report": init_report,
        "metrics": {**latest_metrics, "val_loss": sum(val_losses) / max(len(val_losses), 1)},
        "interface_rule": "checkpoint utility is judged by free generated typed actions checked by the verifier",
    }
    (output_dir / "training_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train/evaluate typed proof-action policy models.")
    sub = parser.add_subparsers(dest="command", required=True)
    train_cmd = sub.add_parser("train")
    train_cmd.add_argument("--config", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.command == "train":
        report = train(args.config)
        Console().print(report)


if __name__ == "__main__":
    main()
