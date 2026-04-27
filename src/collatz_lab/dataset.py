"""PyTorch dataset for generated Parquet shards."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd
import torch
from torch.utils.data import Dataset

from .encode import PAD


def _as_list(value: Any) -> list[int]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    if hasattr(value, "tolist"):
        value = value.tolist()
    return [int(x) for x in list(value)]


class CollatzDataset(Dataset[dict[str, Any]]):
    """Load one or more generated Parquet shards."""

    def __init__(
        self,
        paths: str | Path | Sequence[str | Path],
        split: str | None = None,
        task: str | None = None,
        base: int | None = None,
        limit: int | None = None,
    ) -> None:
        if isinstance(paths, (str, Path)):
            paths = [paths]
        frames = [pd.read_parquet(path) for path in paths]
        if not frames:
            raise ValueError("At least one parquet path is required")
        frame = pd.concat(frames, ignore_index=True)
        if split is not None and "split" in frame.columns:
            frame = frame[frame["split"] == split]
        if task is not None and "task" in frame.columns:
            frame = frame[frame["task"].isin([task, "multitask"])]
        if base is not None and "base" in frame.columns:
            frame = frame[frame["base"] == base]
        if limit is not None and len(frame) > limit:
            frame = frame.sample(n=limit, random_state=0)
        if frame.empty:
            raise ValueError("No rows remained after dataset filters")
        self.frame = frame.reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int) -> dict[str, Any]:
        row = self.frame.iloc[index].to_dict()
        input_ids = torch.tensor(_as_list(row.get("input_digits")), dtype=torch.long)
        target_ids = torch.tensor(_as_list(row.get("target_digits")), dtype=torch.long)
        labels_v2 = int(row.get("v2_3n_plus_1", -100))
        labels_descent = int(row.get("first_descent_time", -100))
        labels_descent_bucket = int(row.get("descent_bucket", -100))
        labels_hard_case = int(row.get("hard_case", -100))
        labels_negative_cycle = int(row.get("negative_cycle_id", -100))
        parity_prefix = torch.tensor(_as_list(row.get("parity_prefix")), dtype=torch.float)
        sign = int(row.get("sign", 1))
        descent_label_mask = bool(row.get("descent_label_mask", sign > 0))
        hard_case_label_mask = bool(row.get("hard_case_label_mask", sign > 0))
        negative_cycle_label_mask = bool(row.get("negative_cycle_label_mask", sign < 0))
        metadata = {
            "n": row.get("n"),
            "sign": sign,
            "abs_bit_length": int(row.get("abs_bit_length", abs(int(row.get("n", 1))).bit_length())),
            "base": int(row.get("base", -1)),
            "bits": int(row.get("bits", -1)),
            "lsb_first": bool(row.get("lsb_first", True)),
            "signed": bool(row.get("signed", False)),
            "split": row.get("split", ""),
            "task": row.get("task", ""),
            "syracuse_next": row.get("syracuse_next", ""),
            "v2_3n_plus_1": labels_v2,
            "first_descent_time": labels_descent,
            "descent_bucket": labels_descent_bucket,
            "hard_case": labels_hard_case,
            "negative_cycle_id": labels_negative_cycle,
            "cycle_entry_time_capped": int(row.get("cycle_entry_time_capped", -1)),
            "max_height_ratio": float(row.get("max_height_ratio", 0.0)),
        }
        return {
            "input_ids": input_ids,
            "target_ids": target_ids,
            "labels_v2": torch.tensor(labels_v2, dtype=torch.long),
            "labels_descent": torch.tensor(labels_descent, dtype=torch.float),
            "labels_descent_bucket": torch.tensor(labels_descent_bucket, dtype=torch.long),
            "labels_hard_case": torch.tensor(labels_hard_case, dtype=torch.long),
            "labels_negative_cycle": torch.tensor(labels_negative_cycle, dtype=torch.long),
            "labels_parity_prefix": parity_prefix,
            "mask_v2": torch.tensor(labels_v2 >= 0, dtype=torch.bool),
            "mask_descent": torch.tensor(descent_label_mask and labels_descent >= 0, dtype=torch.bool),
            "mask_descent_bucket": torch.tensor(descent_label_mask and labels_descent_bucket >= 0, dtype=torch.bool),
            "mask_hard_case": torch.tensor(hard_case_label_mask and labels_hard_case >= 0, dtype=torch.bool),
            "mask_negative_cycle": torch.tensor(negative_cycle_label_mask and labels_negative_cycle >= 0, dtype=torch.bool),
            "mask_parity_prefix": torch.ones_like(parity_prefix, dtype=torch.bool),
            "attention_mask": torch.ones_like(input_ids, dtype=torch.bool),
            "metadata": metadata,
        }


def pad_1d(sequences: list[torch.Tensor], pad_value: int = PAD) -> torch.Tensor:
    max_len = max((seq.numel() for seq in sequences), default=0)
    if max_len == 0:
        return torch.empty((len(sequences), 0), dtype=torch.long)
    out = torch.full((len(sequences), max_len), pad_value, dtype=sequences[0].dtype)
    for i, seq in enumerate(sequences):
        if seq.numel():
            out[i, : seq.numel()] = seq
    return out


def collate_batch(batch: list[dict[str, Any]]) -> dict[str, Any]:
    input_ids = pad_1d([item["input_ids"] for item in batch], pad_value=PAD)
    target_ids = pad_1d([item["target_ids"] for item in batch], pad_value=PAD)
    labels_parity_prefix = pad_1d([item["labels_parity_prefix"] for item in batch], pad_value=0)
    mask_parity_prefix = pad_1d([item["mask_parity_prefix"] for item in batch], pad_value=0).bool()
    attention_mask = input_ids.ne(PAD)
    return {
        "input_ids": input_ids,
        "target_ids": target_ids,
        "labels_v2": torch.stack([item["labels_v2"] for item in batch]),
        "labels_descent": torch.stack([item["labels_descent"] for item in batch]),
        "labels_descent_bucket": torch.stack([item["labels_descent_bucket"] for item in batch]),
        "labels_hard_case": torch.stack([item["labels_hard_case"] for item in batch]),
        "labels_negative_cycle": torch.stack([item["labels_negative_cycle"] for item in batch]),
        "labels_parity_prefix": labels_parity_prefix.float(),
        "mask_v2": torch.stack([item["mask_v2"] for item in batch]),
        "mask_descent": torch.stack([item["mask_descent"] for item in batch]),
        "mask_descent_bucket": torch.stack([item["mask_descent_bucket"] for item in batch]),
        "mask_hard_case": torch.stack([item["mask_hard_case"] for item in batch]),
        "mask_negative_cycle": torch.stack([item["mask_negative_cycle"] for item in batch]),
        "mask_parity_prefix": mask_parity_prefix,
        "attention_mask": attention_mask,
        "metadata": [item["metadata"] for item in batch],
    }
