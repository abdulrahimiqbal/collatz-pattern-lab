"""Evaluation CLI and metrics."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import torch
from rich.console import Console
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from .dataset import CollatzDataset, collate_batch
from .encode import PAD, decode_tokens, vocab_size_for_base
from .models import build_model
from .utils import save_json


def exact_sequence_accuracy(logits: torch.Tensor, labels: torch.Tensor) -> tuple[float, float]:
    preds = logits.argmax(dim=-1)
    mask = labels.ne(PAD)
    token_correct = (preds.eq(labels) & mask).sum().float()
    token_total = mask.sum().clamp_min(1)
    seq_correct = ((preds.eq(labels) | ~mask).all(dim=1)).float().mean()
    return float(seq_correct.item()), float((token_correct / token_total).item())


@torch.no_grad()
def evaluate_checkpoint(
    checkpoint_path: str | Path,
    data: str | Path,
    out: str | Path | None = None,
    show_progress: bool = True,
    failures_out: str | Path | None = None,
    max_failures: int = 10000,
) -> dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = checkpoint["config"]
    task = config.get("task", "v2")
    base = int(config.get("base", 2))
    signed = bool(config.get("model", {}).get("signed", False))
    dataset = CollatzDataset(data, split=None, task=task, base=base)
    loader = DataLoader(dataset, batch_size=int(config.get("batch_size", 128)), shuffle=False, collate_fn=collate_batch)
    model = build_model(config, vocab_size=vocab_size_for_base(base, signed=signed), task=task).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    totals = {
        "n": 0,
        "exact_sequence_correct": 0.0,
        "token_correct": 0.0,
        "token_total": 0.0,
        "v2_correct": 0.0,
        "v2_total": 0.0,
        "descent_abs_error": 0.0,
        "descent_total": 0.0,
        "descent_bucket_correct": 0.0,
        "descent_bucket_total": 0.0,
        "hard_case_correct": 0.0,
        "hard_case_total": 0.0,
        "negative_cycle_correct": 0.0,
        "negative_cycle_total": 0.0,
        "parity_correct": 0.0,
        "parity_total": 0.0,
        "parity_prefix_correct": 0.0,
        "parity_prefix_total": 0.0,
        "positive_sequence_correct": 0.0,
        "positive_sequence_total": 0.0,
        "negative_sequence_correct": 0.0,
        "negative_sequence_total": 0.0,
        "hybrid_syracuse_correct": 0.0,
        "hybrid_syracuse_total": 0.0,
        "hybrid_valid_division": 0.0,
        "positive_hybrid_syracuse_correct": 0.0,
        "positive_hybrid_syracuse_total": 0.0,
        "negative_hybrid_syracuse_correct": 0.0,
        "negative_hybrid_syracuse_total": 0.0,
    }
    grouped: dict[str, dict[str, float]] = {}
    rows_for_grouping: list[dict[str, Any]] = []
    failure_rows: list[dict[str, Any]] = []
    for batch in tqdm(loader, desc="eval", unit="batch", disable=not show_progress):
        batch = {key: value.to(device) if torch.is_tensor(value) else value for key, value in batch.items()}
        decoder_input = batch["target_ids"][:, :-1] if batch["target_ids"].size(1) >= 2 else None
        outputs = model(batch["input_ids"], decoder_input_ids=decoder_input, attention_mask=batch["attention_mask"])
        batch_size = batch["input_ids"].size(0)
        totals["n"] += batch_size
        if outputs.get("logits") is not None and batch["target_ids"].size(1) >= 2:
            labels = batch["target_ids"][:, 1:]
            preds = outputs["logits"].argmax(dim=-1)
            mask = labels.ne(PAD)
            seq_correct = (preds.eq(labels) | ~mask).all(dim=1)
            seq_acc, tok_acc = exact_sequence_accuracy(outputs["logits"], labels)
            totals["exact_sequence_correct"] += seq_acc * batch_size
            token_mask = labels.ne(PAD)
            totals["token_correct"] += tok_acc * float(token_mask.sum().item())
            totals["token_total"] += float(token_mask.sum().item())
            for idx, (meta, ok) in enumerate(zip(batch["metadata"], seq_correct.cpu().tolist(), strict=False)):
                sign = int(meta.get("sign", 1))
                if sign > 0:
                    totals["positive_sequence_total"] += 1
                    totals["positive_sequence_correct"] += float(ok)
                else:
                    totals["negative_sequence_total"] += 1
                    totals["negative_sequence_correct"] += float(ok)
                rows_for_grouping.append(
                    {
                        **meta,
                        "sequence_correct": float(ok),
                        "correct": float(ok),
                        "n_int": int(meta["n"]),
                    }
                )
                if failures_out and not ok and len(failure_rows) < max_failures:
                    pred_tokens = preds[idx].detach().cpu().tolist()
                    label_tokens = labels[idx].detach().cpu().tolist()
                    first_diff = next(
                        (
                            j
                            for j, (pred_token, label_token) in enumerate(zip(pred_tokens, label_tokens, strict=False))
                            if int(pred_token) != int(label_token)
                        ),
                        None,
                    )
                    n_int = int(meta["n"])
                    row = {
                        "failure_type": "sequence",
                        "n": str(meta["n"]),
                        "n_int": n_int,
                        "sign": sign,
                        "bit_length": abs(n_int).bit_length(),
                        "bits": int(meta.get("bits", -1)),
                        "base": int(meta.get("base", -1)),
                        "split": meta.get("split", ""),
                        "task": meta.get("task", ""),
                        "true_syracuse_next": meta.get("syracuse_next", ""),
                        "pred_syracuse_next": str(decode_tokens(pred_tokens, base=base, lsb_first=bool(meta.get("lsb_first", True)))),
                        "first_diff_token_index": first_diff,
                        "v2_3n_plus_1": int(meta.get("v2_3n_plus_1", -1)),
                        "descent_bucket": int(meta.get("descent_bucket", -1)),
                        "hard_case": int(meta.get("hard_case", -1)),
                        "negative_cycle_id": int(meta.get("negative_cycle_id", -1)),
                    }
                    for p in [4, 5, 6, 8, 10, 12, 13, 14, 16]:
                        row[f"residue_mod_{1 << p}"] = n_int % (1 << p)
                    failure_rows.append(row)
        if outputs.get("v2_logits") is not None:
            v2_mask = batch.get("mask_v2", batch["labels_v2"].ge(0))
            labels = batch["labels_v2"].clamp_min(0).clamp_max(31)
            probs = torch.softmax(outputs["v2_logits"], dim=-1)
            preds = probs.argmax(dim=-1)
            correct = preds.eq(labels) & v2_mask
            totals["v2_correct"] += float(correct.sum().item())
            totals["v2_total"] += float(v2_mask.sum().item())
            for idx, meta in enumerate(batch["metadata"]):
                if not bool(v2_mask[idx].item()) or not meta.get("syracuse_next"):
                    continue
                n_int = int(meta["n"])
                pred_v2 = int(preds[idx].item())
                divisor = 1 << pred_v2
                numerator = 3 * n_int + 1
                valid = numerator % divisor == 0
                candidate = numerator // divisor if valid else None
                true_next = int(meta["syracuse_next"])
                ok = valid and candidate == true_next
                sign = int(meta.get("sign", 1))
                totals["hybrid_syracuse_total"] += 1
                totals["hybrid_syracuse_correct"] += float(ok)
                totals["hybrid_valid_division"] += float(valid)
                if sign > 0:
                    totals["positive_hybrid_syracuse_total"] += 1
                    totals["positive_hybrid_syracuse_correct"] += float(ok)
                else:
                    totals["negative_hybrid_syracuse_total"] += 1
                    totals["negative_hybrid_syracuse_correct"] += float(ok)
            if outputs.get("logits") is None:
                for meta, ok in zip(batch["metadata"], correct.cpu().tolist(), strict=False):
                    rows_for_grouping.append({**meta, "correct": float(ok), "n_int": int(meta["n"])})
            if failures_out and len(failure_rows) < max_failures:
                wrong = (preds.ne(labels) & v2_mask).nonzero(as_tuple=False).flatten().detach().cpu().tolist()
                top_probs, top_classes = probs.topk(k=min(5, probs.size(-1)), dim=-1)
                labels_cpu = labels.detach().cpu()
                preds_cpu = preds.detach().cpu()
                top_probs_cpu = top_probs.detach().cpu()
                top_classes_cpu = top_classes.detach().cpu()
                for idx in wrong:
                    if len(failure_rows) >= max_failures:
                        break
                    meta = batch["metadata"][idx]
                    n_int = int(meta["n"])
                    true_v2 = int(labels_cpu[idx].item())
                    pred_v2 = int(preds_cpu[idx].item())
                    row = {
                        "failure_type": "v2",
                        "n": str(meta["n"]),
                        "n_int": n_int,
                        "sign": int(meta.get("sign", 1)),
                        "bit_length": abs(n_int).bit_length(),
                        "bits": int(meta.get("bits", -1)),
                        "base": int(meta.get("base", -1)),
                        "split": meta.get("split", ""),
                        "task": meta.get("task", ""),
                        "true_v2": true_v2,
                        "pred_v2": pred_v2,
                        "true_probability": float(probs[idx, true_v2].item()),
                        "pred_probability": float(probs[idx, pred_v2].item()),
                        "top_classes": [int(x) for x in top_classes_cpu[idx].tolist()],
                        "top_probabilities": [float(x) for x in top_probs_cpu[idx].tolist()],
                    }
                    for p in [4, 5, 6, 8, 10, 12, 13, 14, 16]:
                        row[f"residue_mod_{1 << p}"] = n_int % (1 << p)
                    failure_rows.append(row)
        if outputs.get("descent_logits") is not None:
            descent_mask = batch.get("mask_descent", batch["labels_descent"].ge(0))
            labels = batch["labels_descent"][descent_mask].clamp_min(0)
            preds = outputs["descent_logits"].squeeze(-1)[descent_mask]
            totals["descent_abs_error"] += float((preds - labels).abs().sum().item())
            totals["descent_total"] += float(descent_mask.sum().item())
        if outputs.get("descent_bucket_logits") is not None:
            mask = batch.get("mask_descent_bucket", batch["labels_descent_bucket"].ge(0))
            labels = batch["labels_descent_bucket"][mask].clamp_min(0)
            preds = outputs["descent_bucket_logits"][mask].argmax(dim=-1)
            totals["descent_bucket_correct"] += float(preds.eq(labels).sum().item())
            totals["descent_bucket_total"] += float(mask.sum().item())
        if outputs.get("hard_case_logits") is not None:
            mask = batch.get("mask_hard_case", batch["labels_hard_case"].ge(0))
            labels = batch["labels_hard_case"][mask].clamp_min(0).clamp_max(1)
            preds = outputs["hard_case_logits"][mask].argmax(dim=-1)
            totals["hard_case_correct"] += float(preds.eq(labels).sum().item())
            totals["hard_case_total"] += float(mask.sum().item())
        if outputs.get("negative_cycle_logits") is not None:
            mask = batch.get("mask_negative_cycle", batch["labels_negative_cycle"].ge(0))
            labels = batch["labels_negative_cycle"][mask].clamp_min(0)
            preds = outputs["negative_cycle_logits"][mask].argmax(dim=-1)
            totals["negative_cycle_correct"] += float(preds.eq(labels).sum().item())
            totals["negative_cycle_total"] += float(mask.sum().item())
        if outputs.get("parity_logits") is not None:
            labels = batch["labels_parity_prefix"]
            mask = batch["mask_parity_prefix"]
            logits = outputs["parity_logits"][:, : labels.size(1)]
            preds = logits.sigmoid().ge(0.5)
            per_row = (preds.eq(labels.bool()) | ~mask).all(dim=1)
            totals["parity_correct"] += float((preds.eq(labels.bool()) & mask).sum().item())
            totals["parity_total"] += float(mask.sum().item())
            totals["parity_prefix_correct"] += float(per_row.sum().item())
            totals["parity_prefix_total"] += batch_size

    metrics: dict[str, Any] = {
        "examples": totals["n"],
        "exact_sequence_accuracy": (
            None if totals["token_total"] == 0 else totals["exact_sequence_correct"] / max(totals["n"], 1)
        ),
        "token_accuracy": None if totals["token_total"] == 0 else totals["token_correct"] / totals["token_total"],
        "v2_accuracy": None if totals["v2_total"] == 0 else totals["v2_correct"] / totals["v2_total"],
        "descent_mae": None if totals["descent_total"] == 0 else totals["descent_abs_error"] / totals["descent_total"],
        "descent_bucket_accuracy": (
            None if totals["descent_bucket_total"] == 0 else totals["descent_bucket_correct"] / totals["descent_bucket_total"]
        ),
        "hard_case_accuracy": None if totals["hard_case_total"] == 0 else totals["hard_case_correct"] / totals["hard_case_total"],
        "negative_cycle_accuracy": (
            None if totals["negative_cycle_total"] == 0 else totals["negative_cycle_correct"] / totals["negative_cycle_total"]
        ),
        "parity_bit_accuracy": None if totals["parity_total"] == 0 else totals["parity_correct"] / totals["parity_total"],
        "parity_prefix_accuracy": (
            None if totals["parity_prefix_total"] == 0 else totals["parity_prefix_correct"] / totals["parity_prefix_total"]
        ),
        "positive_exact_sequence_accuracy": (
            None
            if totals["positive_sequence_total"] == 0
            else totals["positive_sequence_correct"] / totals["positive_sequence_total"]
        ),
        "negative_exact_sequence_accuracy": (
            None
            if totals["negative_sequence_total"] == 0
            else totals["negative_sequence_correct"] / totals["negative_sequence_total"]
        ),
        "hybrid_v2_syracuse_accuracy": (
            None
            if totals["hybrid_syracuse_total"] == 0
            else totals["hybrid_syracuse_correct"] / totals["hybrid_syracuse_total"]
        ),
        "hybrid_v2_valid_division_rate": (
            None
            if totals["hybrid_syracuse_total"] == 0
            else totals["hybrid_valid_division"] / totals["hybrid_syracuse_total"]
        ),
        "positive_hybrid_v2_syracuse_accuracy": (
            None
            if totals["positive_hybrid_syracuse_total"] == 0
            else totals["positive_hybrid_syracuse_correct"] / totals["positive_hybrid_syracuse_total"]
        ),
        "negative_hybrid_v2_syracuse_accuracy": (
            None
            if totals["negative_hybrid_syracuse_total"] == 0
            else totals["negative_hybrid_syracuse_correct"] / totals["negative_hybrid_syracuse_total"]
        ),
    }
    if rows_for_grouping:
        frame = pd.DataFrame(rows_for_grouping)
        frame["bit_length"] = frame["n_int"].map(lambda value: abs(int(value)).bit_length())
        metrics["accuracy_by_bit_length"] = frame.groupby("bit_length")["correct"].mean().to_dict()
        if "sign" in frame:
            metrics["accuracy_by_sign"] = frame.groupby("sign")["correct"].mean().to_dict()
        metrics["accuracy_by_residue_class"] = {}
        for p in [1, 2, 3, 4, 5, 6, 8, 10, 12]:
            modulus = 1 << p
            frame[f"residue_mod_{modulus}"] = frame["n_int"] % modulus
            metrics["accuracy_by_residue_class"][f"mod_{modulus}"] = (
                frame.groupby(f"residue_mod_{modulus}")["correct"].mean().to_dict()
            )
        metrics["accuracy_by_base"] = frame.groupby("base")["correct"].mean().to_dict()
        larger = frame[frame["bit_length"] > int(config.get("bits_train", 0))]
        metrics["ood_accuracy_larger_bits"] = None if larger.empty else float(larger["correct"].mean())
        hard = frame[frame["max_height_ratio"] >= frame["max_height_ratio"].quantile(0.9)]
        metrics["hard_case_sequence_accuracy"] = None if hard.empty else float(hard["correct"].mean())
    if out:
        save_json(metrics, out)
    if failures_out:
        save_json(failure_rows, failures_out)
    return metrics


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a Collatz model checkpoint.")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default=None)
    parser.add_argument("--failures-out", default=None)
    parser.add_argument("--max-failures", type=int, default=10000)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    metrics = evaluate_checkpoint(
        args.checkpoint,
        args.data,
        out=args.out,
        failures_out=args.failures_out,
        max_failures=args.max_failures,
    )
    Console().print(metrics)


if __name__ == "__main__":
    main()
