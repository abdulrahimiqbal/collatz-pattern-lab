"""Small PyTorch models for Collatz sequence and classification tasks."""

from __future__ import annotations

import math
from typing import Any

import torch
from torch import nn


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_seq_len: int, dropout: float = 0.0) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        position = torch.arange(max_seq_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_seq_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term[: pe[:, 1::2].shape[1]])
        self.register_buffer("pe", pe.unsqueeze(0), persistent=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:, : x.size(1)]
        return self.dropout(x)


def masked_mean(hidden: torch.Tensor, attention_mask: torch.Tensor | None) -> torch.Tensor:
    if attention_mask is None:
        return hidden.mean(dim=1)
    mask = attention_mask.to(hidden.dtype).unsqueeze(-1)
    denom = mask.sum(dim=1).clamp_min(1.0)
    return (hidden * mask).sum(dim=1) / denom


class TinySeq2SeqTransformer(nn.Module):
    """Compact encoder/decoder Transformer with optional classification heads."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 128,
        n_heads: int = 4,
        n_layers: int = 4,
        dropout: float = 0.1,
        max_seq_len: int = 512,
        v2_head: bool = False,
        descent_head: bool = False,
        descent_bucket_head: bool = False,
        hard_case_head: bool = False,
        parity_head: bool = False,
        negative_cycle_head: bool = False,
        num_v2_classes: int = 32,
        num_descent_outputs: int = 1,
        num_descent_buckets: int = 10,
        parity_prefix_len: int = 32,
        num_negative_cycles: int = 100,
    ) -> None:
        super().__init__()
        self.vocab_size = vocab_size
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position = PositionalEncoding(d_model, max_seq_len=max_seq_len, dropout=dropout)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4 * d_model,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4 * d_model,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers, enable_nested_tensor=False)
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=n_layers)
        self.output = nn.Linear(d_model, vocab_size)
        self.v2_head = nn.Linear(d_model, num_v2_classes) if v2_head else None
        self.descent_head = nn.Linear(d_model, num_descent_outputs) if descent_head else None
        self.descent_bucket_head = nn.Linear(d_model, num_descent_buckets) if descent_bucket_head else None
        self.hard_case_head = nn.Linear(d_model, 2) if hard_case_head else None
        self.parity_head = nn.Linear(d_model, parity_prefix_len) if parity_head else None
        self.negative_cycle_head = nn.Linear(d_model, num_negative_cycles) if negative_cycle_head else None

    def encode(self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None) -> torch.Tensor:
        src_key_padding_mask = ~attention_mask.bool() if attention_mask is not None else None
        hidden = self.position(self.token_embedding(input_ids))
        return self.encoder(hidden, src_key_padding_mask=src_key_padding_mask)

    def forward(
        self,
        input_ids: torch.Tensor,
        decoder_input_ids: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor | None]:
        memory = self.encode(input_ids, attention_mask=attention_mask)
        pooled = masked_mean(memory, attention_mask)
        logits = None
        if decoder_input_ids is not None and decoder_input_ids.numel() > 0:
            tgt = self.position(self.token_embedding(decoder_input_ids))
            tgt_len = decoder_input_ids.size(1)
            causal_mask = nn.Transformer.generate_square_subsequent_mask(tgt_len, device=tgt.device)
            memory_key_padding_mask = ~attention_mask.bool() if attention_mask is not None else None
            decoded = self.decoder(
                tgt,
                memory,
                tgt_mask=causal_mask,
                memory_key_padding_mask=memory_key_padding_mask,
            )
            logits = self.output(decoded)
        return {
            "logits": logits,
            "hidden_states": memory,
            "pooled": pooled,
            "v2_logits": self.v2_head(pooled) if self.v2_head is not None else None,
            "descent_logits": self.descent_head(pooled) if self.descent_head is not None else None,
            "descent_bucket_logits": self.descent_bucket_head(pooled) if self.descent_bucket_head is not None else None,
            "hard_case_logits": self.hard_case_head(pooled) if self.hard_case_head is not None else None,
            "parity_logits": self.parity_head(pooled) if self.parity_head is not None else None,
            "negative_cycle_logits": self.negative_cycle_head(pooled) if self.negative_cycle_head is not None else None,
        }


class DecoderOnlyTransformer(nn.Module):
    """Small causal Transformer for next-token style experiments."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 128,
        n_heads: int = 4,
        n_layers: int = 4,
        dropout: float = 0.1,
        max_seq_len: int = 512,
    ) -> None:
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position = PositionalEncoding(d_model, max_seq_len=max_seq_len, dropout=dropout)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4 * d_model,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.transformer = nn.TransformerEncoder(layer, num_layers=n_layers, enable_nested_tensor=False)
        self.output = nn.Linear(d_model, vocab_size)

    def forward(self, input_ids: torch.Tensor) -> dict[str, torch.Tensor]:
        hidden = self.position(self.token_embedding(input_ids))
        seq_len = input_ids.size(1)
        causal_mask = nn.Transformer.generate_square_subsequent_mask(seq_len, device=input_ids.device)
        hidden = self.transformer(hidden, mask=causal_mask)
        return {"logits": self.output(hidden), "hidden_states": hidden}


class MLPBinaryBaseline(nn.Module):
    """Simple baseline for low-base classifier tasks."""

    def __init__(
        self,
        vocab_size: int,
        max_seq_len: int,
        hidden_dim: int = 256,
        output_dim: int = 32,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 16)
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(max_seq_len * 16, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, input_ids: torch.Tensor) -> dict[str, torch.Tensor]:
        return {"v2_logits": self.net(self.embedding(input_ids))}


def build_model(config: dict[str, Any], vocab_size: int, task: str, max_seq_len: int = 512) -> nn.Module:
    model_cfg = config.get("model", {})
    model_type = model_cfg.get("type", "seq2seq")
    common = {
        "vocab_size": vocab_size,
        "d_model": int(model_cfg.get("d_model", 128)),
        "n_heads": int(model_cfg.get("n_heads", 4)),
        "n_layers": int(model_cfg.get("n_layers", 4)),
        "dropout": float(model_cfg.get("dropout", 0.1)),
        "max_seq_len": int(model_cfg.get("max_seq_len", max_seq_len)),
    }
    if model_type in {"seq2seq", "encoder_classifier"}:
        is_multitask = task == "multitask"
        return TinySeq2SeqTransformer(
            **common,
            v2_head=task in {"v2", "multitask"} or model_type == "encoder_classifier",
            descent_head=task == "descent" or bool(model_cfg.get("descent_regression_head", False)),
            descent_bucket_head=is_multitask or bool(model_cfg.get("descent_bucket_head", False)),
            hard_case_head=is_multitask or bool(model_cfg.get("hard_case_head", False)),
            parity_head=is_multitask or bool(model_cfg.get("parity_head", False)),
            negative_cycle_head=is_multitask or bool(model_cfg.get("negative_cycle_head", False)),
            num_descent_buckets=int(model_cfg.get("num_descent_buckets", 10)),
            parity_prefix_len=int(model_cfg.get("parity_prefix_len", 32)),
            num_negative_cycles=int(model_cfg.get("num_negative_cycles", 100)),
        )
    if model_type == "decoder_only":
        return DecoderOnlyTransformer(**common)
    if model_type == "mlp_binary":
        return MLPBinaryBaseline(
            vocab_size=vocab_size,
            max_seq_len=int(model_cfg.get("max_seq_len", max_seq_len)),
            hidden_dim=int(model_cfg.get("hidden_dim", 256)),
            output_dim=int(model_cfg.get("output_dim", 32)),
        )
    raise ValueError(f"Unknown model type: {model_type}")
