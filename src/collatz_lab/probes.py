"""Representation probing utilities."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import torch
from rich.console import Console
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression, Ridge, RidgeClassifier
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from .dataset import CollatzDataset, collate_batch
from .encode import vocab_size_for_base
from .models import build_model
from .utils import save_json


@torch.no_grad()
def extract_representations(
    checkpoint_path: str | Path,
    data: str | Path,
    limit: int | None = None,
) -> tuple[np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = checkpoint["config"]
    task = config.get("task", "v2")
    base = int(config.get("base", 2))
    dataset = CollatzDataset(data, split=None, task=task, base=base, limit=limit)
    loader = DataLoader(dataset, batch_size=int(config.get("batch_size", 128)), shuffle=False, collate_fn=collate_batch)
    signed = bool(config.get("model", {}).get("signed", False))
    model = build_model(config, vocab_size=vocab_size_for_base(base, signed=signed), task=task).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    reps: list[np.ndarray] = []
    metadata: list[dict[str, Any]] = []
    for batch in tqdm(loader, desc="hidden states", unit="batch"):
        batch = {key: value.to(device) if torch.is_tensor(value) else value for key, value in batch.items()}
        outputs = model(batch["input_ids"], attention_mask=batch["attention_mask"])
        reps.append(outputs["pooled"].detach().cpu().numpy())
        metadata.extend(batch["metadata"])
    return np.concatenate(reps, axis=0), metadata, config


def summarize_clusters(
    x: np.ndarray,
    metadata: list[dict[str, Any]],
    n_clusters: int = 12,
) -> dict[str, Any]:
    if len(x) == 0:
        return {}
    kmeans = KMeans(n_clusters=min(n_clusters, len(x)), n_init="auto", random_state=0)
    clusters = kmeans.fit_predict(x)
    hard_threshold = np.quantile([m["max_height_ratio"] for m in metadata], 0.9)
    summaries: dict[str, Any] = {}
    for cluster in sorted(set(clusters.tolist())):
        idx = np.where(clusters == cluster)[0]
        rows = [metadata[int(i)] for i in idx]
        signs = [int(row.get("sign", 1)) for row in rows]
        positives = [row for row in rows if int(row.get("sign", 1)) > 0]
        residues_mod_64 = [int(row["n"]) % 64 for row in rows]
        residues_mod_1024 = [int(row["n"]) % 1024 for row in rows]
        v2_values = [int(row.get("v2_3n_plus_1", -1)) for row in rows]
        descent_buckets = [int(row.get("descent_bucket", -1)) for row in positives]
        negative_cycles = [int(row.get("negative_cycle_id", -1)) for row in rows if int(row.get("sign", 1)) < 0]

        def top_counts(values: list[int], k: int = 8) -> list[dict[str, int]]:
            counts: dict[int, int] = {}
            for value in values:
                counts[value] = counts.get(value, 0) + 1
            return [
                {"value": int(value), "count": int(count)}
                for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:k]
            ]

        summaries[str(cluster)] = {
            "size": int(len(rows)),
            "positive_fraction": float(sum(1 for sign in signs if sign > 0) / max(len(signs), 1)),
            "hard_case_rate": float(
                sum(float(row.get("max_height_ratio", 0.0)) >= hard_threshold for row in rows) / max(len(rows), 1)
            ),
            "mean_max_height_ratio": float(np.mean([float(row.get("max_height_ratio", 0.0)) for row in rows])),
            "mean_first_descent_time_positive": (
                None
                if not positives
                else float(np.mean([int(row.get("first_descent_time", -1)) for row in positives]))
            ),
            "top_v2": top_counts(v2_values),
            "top_residue_mod_64": top_counts(residues_mod_64),
            "top_residue_mod_1024": top_counts(residues_mod_1024),
            "top_descent_bucket": top_counts(descent_buckets),
            "top_negative_cycle_id": top_counts(negative_cycles),
        }
    return summaries


def run_probes(
    checkpoint: str | Path,
    data: str | Path,
    out: str | Path,
    plot_dir: str | Path | None = None,
    limit: int | None = None,
    n_clusters: int = 12,
    p_values: list[int] | None = None,
) -> dict[str, Any]:
    x, metadata, _ = extract_representations(checkpoint, data, limit=limit)
    n_values = np.array([int(m["n"]) for m in metadata], dtype=object)
    # Metadata intentionally stays compact in the dataset class. Recompute cheap probe labels exactly.
    from .collatz import first_descent_time, signed_cycle_id, signed_v2_3n_plus_1, v2

    y_v2 = np.array(
        [signed_v2_3n_plus_1(int(n)) if int(n) < 0 else v2(3 * int(n) + 1) for n in n_values],
        dtype=int,
    )
    y_sign = np.array([1 if int(n) > 0 else 0 for n in n_values], dtype=int)
    y_descent = np.array([first_descent_time(int(n), max_steps=1000) or 1000 if int(n) > 0 else 1000 for n in n_values], dtype=float)
    y_negative_cycle = np.array([signed_cycle_id(int(n), max_steps=1000)[0] if int(n) < 0 else -1 for n in n_values], dtype=int)
    x_train, x_test, idx_train, idx_test = train_test_split(
        x,
        np.arange(len(x)),
        test_size=0.25,
        random_state=0,
    )
    metrics: dict[str, Any] = {"examples": len(metadata), "limit": limit}
    p_values = p_values or [1, 2, 3, 4, 5, 6, 8, 10]
    for p in p_values:
        modulus = 1 << p
        y = np.array([int(n) % modulus for n in n_values], dtype=int)
        if len(set(y[idx_train].tolist())) < 2:
            metrics[f"mod_2^{p}_accuracy"] = None
            continue
        clf = RidgeClassifier(alpha=1.0)
        clf.fit(x_train, y[idx_train])
        pred = clf.predict(x_test)
        metrics[f"mod_2^{p}_accuracy"] = float(accuracy_score(y[idx_test], pred))
    if len(set(y_v2[idx_train].tolist())) < 2:
        metrics["v2_probe_accuracy"] = None
    else:
        clf_v2 = LogisticRegression(max_iter=1000)
        clf_v2.fit(x_train, y_v2[idx_train])
        metrics["v2_probe_accuracy"] = float(accuracy_score(y_v2[idx_test], clf_v2.predict(x_test)))
    if len(set(y_sign[idx_train].tolist())) < 2:
        metrics["sign_probe_accuracy"] = None
    else:
        clf_sign = LogisticRegression(max_iter=1000)
        clf_sign.fit(x_train, y_sign[idx_train])
        metrics["sign_probe_accuracy"] = float(accuracy_score(y_sign[idx_test], clf_sign.predict(x_test)))
    negative_idx = np.where(y_negative_cycle >= 0)[0]
    if len(set(y_negative_cycle[negative_idx].tolist())) > 1 and len(negative_idx) >= 8:
        train_neg = np.intersect1d(idx_train, negative_idx)
        test_neg = np.intersect1d(idx_test, negative_idx)
        if len(train_neg) and len(test_neg):
            clf_cycle = LogisticRegression(max_iter=1000)
            clf_cycle.fit(x[train_neg], y_negative_cycle[train_neg])
            metrics["negative_cycle_probe_accuracy"] = float(
                accuracy_score(y_negative_cycle[test_neg], clf_cycle.predict(x[test_neg]))
            )
    reg = Ridge(alpha=1.0)
    reg.fit(x_train, y_descent[idx_train])
    metrics["descent_probe_mae"] = float(mean_absolute_error(y_descent[idx_test], reg.predict(x_test)))
    metrics["cluster_summary"] = summarize_clusters(x, metadata, n_clusters=n_clusters)
    metrics["hard_case_cluster_rates"] = {
        cluster: summary["hard_case_rate"]
        for cluster, summary in metrics["cluster_summary"].items()
    }
    if plot_dir is None:
        plot_dir = Path(out).parent / "probe_plots"
    plot_dir = Path(plot_dir)
    plot_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4))
    plt.bar(metrics["hard_case_cluster_rates"].keys(), metrics["hard_case_cluster_rates"].values())
    plt.xlabel("cluster")
    plt.ylabel("hard-case rate")
    plt.tight_layout()
    plt.savefig(plot_dir / "hard_case_clusters.png")
    plt.close()
    save_json(metrics, out)
    return metrics


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train linear probes on hidden states.")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--plot-dir", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--n-clusters", type=int, default=12)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    metrics = run_probes(
        args.checkpoint,
        args.data,
        args.out,
        plot_dir=args.plot_dir,
        limit=args.limit,
        n_clusters=args.n_clusters,
    )
    Console().print(metrics)


if __name__ == "__main__":
    main()
