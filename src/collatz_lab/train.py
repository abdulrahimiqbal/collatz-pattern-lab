"""Training CLI."""

from __future__ import annotations

import argparse
import itertools
import shutil
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from rich.console import Console
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from .dataset import CollatzDataset, collate_batch
from .encode import PAD, vocab_size_for_base
from .generate import generate_rows, write_parquet
from .models import build_model
from .utils import load_yaml, save_json, save_yaml, set_seed


def find_data_paths(config: dict[str, Any]) -> list[Path]:
    data_cfg = config.get("data", {})
    explicit = data_cfg.get("paths") or data_cfg.get("train_paths")
    if explicit:
        if isinstance(explicit, (str, Path)):
            explicit = [explicit]
        return [Path(p) for p in explicit]
    paths = sorted(Path("data").glob("**/*.parquet"))
    if paths:
        return paths
    return []


def ensure_data(config: dict[str, Any], console: Console) -> list[Path]:
    paths = find_data_paths(config)
    if paths:
        return paths
    task = config.get("task", "v2")
    base = int(config.get("base", 2))
    bits = int(config.get("bits_train", 16))
    out = Path("data") / "autogen" / f"{task}_base{base}_bits{bits}_smoke.parquet"
    console.print(f"[yellow]No parquet shards found; generating a small smoke shard at {out}[/yellow]")
    rows = generate_rows(
        task=task,
        base=base,
        bits=bits,
        n_rows=int(config.get("autogen_rows", 2048)),
        lsb_first=bool(config.get("lsb_first", True)),
        seed=int(config.get("seed", 0)),
        signed=bool(config.get("model", {}).get("signed", False)),
        sign_mode=str(config.get("data", {}).get("sign_mode", "mixed")),
        sample_mode=str(config.get("data", {}).get("sample_mode", "random")),
        show_progress=False,
    )
    write_parquet(rows, out)
    return [out]


def make_run_dir(config: dict[str, Any]) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    task = config.get("task", "task")
    base = config.get("base", "base")
    root = Path(config.get("run_root", "runs"))
    run_name = config.get("run_name")
    run_dir = root / str(run_name) if run_name else root / f"{stamp}_{task}_base{base}"
    run_dir.mkdir(parents=True, exist_ok=True)
    latest = root / "latest"
    try:
        if latest.exists() or latest.is_symlink():
            latest.unlink()
        latest.symlink_to(run_dir.name)
    except OSError:
        pass
    return run_dir


def cycle(loader: DataLoader) -> Any:
    while True:
        yield from loader


def move_batch(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    return {
        key: value.to(device) if torch.is_tensor(value) else value
        for key, value in batch.items()
    }


def compute_loss(
    outputs: dict[str, torch.Tensor | None],
    batch: dict[str, Any],
    task: str,
    loss_weights: dict[str, float] | None = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    losses: list[torch.Tensor] = []
    metrics: dict[str, float] = {}
    weights = loss_weights or {}

    def weight(name: str, default: float = 1.0) -> float:
        return float(weights.get(name, default))

    target_ids = batch["target_ids"]
    if weight("sequence") > 0 and task in {"syracuse", "multitask"} and target_ids.size(1) >= 2 and outputs.get("logits") is not None:
        logits = outputs["logits"]
        assert logits is not None
        labels = target_ids[:, 1:].contiguous()
        seq_loss = F.cross_entropy(
            logits.reshape(-1, logits.size(-1)),
            labels.reshape(-1),
            ignore_index=PAD,
        )
        losses.append(seq_loss * weight("sequence"))
        with torch.no_grad():
            mask = labels.ne(PAD)
            preds = logits.argmax(dim=-1)
            token_acc = (preds.eq(labels) & mask).sum().float() / mask.sum().clamp_min(1)
            metrics["token_acc"] = float(token_acc.item())
            metrics["seq_loss"] = float(seq_loss.item())
    if weight("v2") > 0 and task in {"v2", "multitask"} and outputs.get("v2_logits") is not None:
        mask = batch.get("mask_v2", batch["labels_v2"].ge(0))
        labels = batch["labels_v2"][mask].clamp_min(0).clamp_max(31)
        logits = outputs["v2_logits"][mask]
        v2_loss = logits.sum() * 0 if labels.numel() == 0 else F.cross_entropy(logits, labels)
        losses.append(v2_loss * weight("v2"))
        with torch.no_grad():
            metrics["v2_acc"] = 0.0 if labels.numel() == 0 else float(logits.argmax(dim=-1).eq(labels).float().mean().item())
            metrics["v2_loss"] = float(v2_loss.item())
    if weight("descent") > 0 and task in {"descent", "multitask"} and outputs.get("descent_logits") is not None:
        mask = batch.get("mask_descent", batch["labels_descent"].ge(0))
        labels = batch["labels_descent"][mask].clamp_min(0).unsqueeze(-1)
        preds = outputs["descent_logits"][mask]
        descent_loss = preds.sum() * 0 if labels.numel() == 0 else F.l1_loss(preds, labels)
        losses.append(descent_loss * weight("descent"))
        metrics["descent_mae"] = float(descent_loss.item())
    if weight("descent_bucket") > 0 and task == "multitask" and outputs.get("descent_bucket_logits") is not None:
        mask = batch.get("mask_descent_bucket", batch["labels_descent_bucket"].ge(0))
        labels = batch["labels_descent_bucket"][mask].clamp_min(0)
        logits = outputs["descent_bucket_logits"][mask]
        bucket_loss = logits.sum() * 0 if labels.numel() == 0 else F.cross_entropy(logits, labels)
        losses.append(bucket_loss * weight("descent_bucket"))
        with torch.no_grad():
            metrics["descent_bucket_acc"] = 0.0 if labels.numel() == 0 else float(logits.argmax(dim=-1).eq(labels).float().mean().item())
            metrics["descent_bucket_loss"] = float(bucket_loss.item())
    if weight("hard_case") > 0 and task == "multitask" and outputs.get("hard_case_logits") is not None:
        mask = batch.get("mask_hard_case", batch["labels_hard_case"].ge(0))
        labels = batch["labels_hard_case"][mask].clamp_min(0).clamp_max(1)
        logits = outputs["hard_case_logits"][mask]
        hard_loss = logits.sum() * 0 if labels.numel() == 0 else F.cross_entropy(logits, labels)
        losses.append(hard_loss * weight("hard_case"))
        with torch.no_grad():
            metrics["hard_case_acc"] = 0.0 if labels.numel() == 0 else float(logits.argmax(dim=-1).eq(labels).float().mean().item())
            metrics["hard_case_loss"] = float(hard_loss.item())
    if weight("parity") > 0 and task == "multitask" and outputs.get("parity_logits") is not None:
        labels = batch["labels_parity_prefix"]
        mask = batch["mask_parity_prefix"]
        logits = outputs["parity_logits"][:, : labels.size(1)]
        parity_loss_all = F.binary_cross_entropy_with_logits(logits, labels, reduction="none")
        parity_loss = (parity_loss_all * mask.float()).sum() / mask.float().sum().clamp_min(1.0)
        losses.append(parity_loss * weight("parity"))
        with torch.no_grad():
            preds = logits.sigmoid().ge(0.5)
            metrics["parity_bit_acc"] = float((preds.eq(labels.bool()) & mask).sum().float().div(mask.sum().clamp_min(1)).item())
            metrics["parity_loss"] = float(parity_loss.item())
    if weight("negative_cycle") > 0 and task == "multitask" and outputs.get("negative_cycle_logits") is not None:
        mask = batch.get("mask_negative_cycle", batch["labels_negative_cycle"].ge(0))
        labels = batch["labels_negative_cycle"][mask].clamp_min(0)
        logits = outputs["negative_cycle_logits"][mask]
        cycle_loss = logits.sum() * 0 if labels.numel() == 0 else F.cross_entropy(logits, labels)
        losses.append(cycle_loss * weight("negative_cycle"))
        with torch.no_grad():
            metrics["negative_cycle_acc"] = 0.0 if labels.numel() == 0 else float(logits.argmax(dim=-1).eq(labels).float().mean().item())
            metrics["negative_cycle_loss"] = float(cycle_loss.item())
    if not losses:
        raise RuntimeError(f"No loss was configured for task={task}")
    total = torch.stack(losses).sum()
    metrics["loss"] = float(total.item())
    return total, metrics


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    loader: DataLoader,
    task: str,
    device: torch.device,
    max_batches: int = 10,
    loss_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    model.eval()
    totals: dict[str, float] = {}
    count = 0
    for batch in itertools.islice(loader, max_batches):
        batch = move_batch(batch, device)
        decoder_input = batch["target_ids"][:, :-1] if batch["target_ids"].size(1) >= 2 else None
        outputs = model(batch["input_ids"], decoder_input_ids=decoder_input, attention_mask=batch["attention_mask"])
        _, metrics = compute_loss(outputs, batch, task, loss_weights=loss_weights)
        for key, value in metrics.items():
            totals[key] = totals.get(key, 0.0) + value
        count += 1
    model.train()
    return {f"val_{key}": value / max(count, 1) for key, value in totals.items()}


def save_checkpoint(
    path: Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    config: dict[str, Any],
    step: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "config": config,
            "step": step,
        },
        path,
    )


def train(config_path: str | Path, resume: str | Path | None = None) -> Path:
    console = Console()
    config = load_yaml(config_path)
    set_seed(int(config.get("seed", 0)))
    task = config.get("task", "v2")
    base = int(config.get("base", 2))
    batch_size = int(config.get("batch_size", 128))
    data_paths = ensure_data(config, console)
    run_dir = make_run_dir(config)
    shutil.copy2(config_path, run_dir / "config.yaml")
    save_yaml(config, run_dir / "resolved_config.yaml")

    train_ds = CollatzDataset(data_paths, split="train", task=task, base=base)
    try:
        val_ds = CollatzDataset(data_paths, split="val", task=task, base=base)
    except ValueError:
        val_ds = train_ds
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_batch)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_batch)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_cfg = config.get("model", {})
    signed = bool(model_cfg.get("signed", False))
    vocab_size = vocab_size_for_base(base, signed=signed)
    max_seq_len = int(model_cfg.get("max_seq_len", 512))
    model = build_model(config, vocab_size=vocab_size, task=task, max_seq_len=max_seq_len).to(device)
    opt_cfg = config.get("optimizer", {})
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(opt_cfg.get("lr", 3e-4)),
        weight_decay=float(opt_cfg.get("weight_decay", 0.01)),
    )
    start_step = 0
    if resume:
        checkpoint = torch.load(resume, map_location=device)
        model.load_state_dict(checkpoint["model_state"])
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        start_step = int(checkpoint.get("step", 0))

    training_cfg = config.get("training", {})
    loss_weights = training_cfg.get("loss_weights", {})
    max_train_steps = int(training_cfg.get("max_train_steps", 10))
    eval_every = int(training_cfg.get("eval_every", max(1, max_train_steps // 2)))
    checkpoint_every = int(training_cfg.get("checkpoint_every", max_train_steps))
    grad_clip = float(training_cfg.get("grad_clip", 1.0))
    precision = str(training_cfg.get("precision", "fp32")).lower()
    use_amp = device.type == "cuda" and precision in {"fp16", "bf16"}
    amp_dtype = torch.bfloat16 if precision == "bf16" else torch.float16
    try:
        scaler = torch.amp.GradScaler("cuda", enabled=use_amp and precision == "fp16")
    except TypeError:  # pragma: no cover - compatibility with older PyTorch.
        scaler = torch.cuda.amp.GradScaler(enabled=use_amp and precision == "fp16")

    writer = None
    try:
        from torch.utils.tensorboard import SummaryWriter

        writer = SummaryWriter(log_dir=str(run_dir / "tensorboard"))
    except Exception as exc:  # pragma: no cover - tensorboard is optional at runtime
        console.print(f"[yellow]TensorBoard unavailable: {exc}[/yellow]")

    metrics_history: list[dict[str, float | int]] = []
    iterator = cycle(train_loader)
    model.train()
    progress = tqdm(
        range(start_step + 1, max_train_steps + 1),
        desc="train",
        unit="step",
        disable=bool(training_cfg.get("disable_progress", False)),
    )
    for step in progress:
        batch = move_batch(next(iterator), device)
        decoder_input = batch["target_ids"][:, :-1] if batch["target_ids"].size(1) >= 2 else None
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=amp_dtype, enabled=use_amp):
            outputs = model(batch["input_ids"], decoder_input_ids=decoder_input, attention_mask=batch["attention_mask"])
            loss, metrics = compute_loss(outputs, batch, task, loss_weights=loss_weights)
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        scaler.step(optimizer)
        scaler.update()
        progress.set_postfix(loss=f"{metrics['loss']:.4f}")
        if writer:
            for key, value in metrics.items():
                writer.add_scalar(f"train/{key}", value, step)
        record: dict[str, float | int] = {"step": step, **metrics}
        if step % eval_every == 0 or step == max_train_steps:
            val_metrics = evaluate(model, val_loader, task=task, device=device, loss_weights=loss_weights)
            record.update(val_metrics)
            if writer:
                for key, value in val_metrics.items():
                    writer.add_scalar(key.replace("val_", "val/"), value, step)
        metrics_history.append(record)
        if step % checkpoint_every == 0 or step == max_train_steps:
            save_checkpoint(run_dir / "checkpoint.pt", model, optimizer, config, step)
            save_checkpoint(run_dir / f"checkpoint_step{step}.pt", model, optimizer, config, step)
            save_json(metrics_history, run_dir / "metrics.json")
    if writer:
        writer.close()
    console.print(f"[green]Training complete. Run directory: {run_dir}[/green]")
    return run_dir


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a Collatz model.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--resume", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    train(args.config, resume=args.resume)


if __name__ == "__main__":
    main()
