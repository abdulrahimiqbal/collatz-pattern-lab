"""Mine candidate residue-class descent rules from datasets and model reports."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from rich.console import Console
from sklearn.cluster import KMeans

from .collatz import first_descent_time
from .probes import extract_representations, summarize_clusters
from .utils import save_json, write_jsonl


def _positive_rows(frame: pd.DataFrame) -> pd.DataFrame:
    n_int = frame["n"].map(int)
    return frame.loc[n_int > 0].assign(n_int=n_int[n_int > 0].to_numpy()).reset_index(drop=True)


def _descent_for_row(row: pd.Series, max_k: int) -> int | None:
    existing = row.get("first_descent_time", -1)
    try:
        existing_int = int(existing)
    except (TypeError, ValueError):
        existing_int = -1
    if 0 <= existing_int <= max_k:
        return existing_int
    if existing_int > max_k:
        return None
    return first_descent_time(int(row["n_int"]), max_steps=max_k)


def _candidate_from_values(
    values: list[pd.Series],
    modulus: int,
    residue: int,
    max_k: int,
    source: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    descents = [_descent_for_row(row, max_k=max_k) for row in values]
    if not descents or any(t is None for t in descents):
        return None
    suggested_k = max(int(t) for t in descents if t is not None)
    payload = {
        "modulus": modulus,
        "residue": residue,
        "claim": (
            f"exists k <= {max_k} such that C^k(n) < n "
            f"for all n ≡ {residue} mod {modulus}"
        ),
        "suggested_k": suggested_k,
        "support": len(values),
        "mean_first_descent_time": float(np.mean([int(t) for t in descents if t is not None])),
        "max_first_descent_time": suggested_k,
        "source": source,
    }
    if extra:
        payload.update(extra)
    return payload


def mine_residue_descent_candidates(
    data: str | Path,
    p_values: list[int] | None = None,
    min_support: int = 8,
    max_k: int = 120,
    source: str = "dataset_scan",
) -> list[dict[str, Any]]:
    """Find residues whose sampled examples all descend quickly.

    These are hypotheses only. The verifier must check them exactly.
    """

    frame = _positive_rows(pd.read_parquet(data))
    p_values = p_values or [4, 5, 6, 8, 10]
    candidates: list[dict[str, Any]] = []
    for p in p_values:
        modulus = 1 << p
        buckets: dict[int, list[pd.Series]] = {}
        for _, row in frame.iterrows():
            buckets.setdefault(int(row["n_int"]) % modulus, []).append(row)
        for residue, values in buckets.items():
            if len(values) < min_support:
                continue
            candidate = _candidate_from_values(values, modulus, residue, max_k, source)
            if candidate:
                candidates.append(candidate)
    candidates.sort(key=lambda row: (row["suggested_k"], -row["support"]))
    return candidates


def mine_model_cluster_descent_candidates(
    checkpoint: str | Path,
    data: str | Path,
    p_values: list[int] | None = None,
    min_support: int = 8,
    max_k: int = 180,
    limit: int | None = None,
    n_clusters: int = 12,
    cluster_out: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Use hidden-state clusters to prioritize residue-class descent hypotheses."""

    x, metadata, _ = extract_representations(checkpoint, data, limit=limit)
    clusters = KMeans(n_clusters=min(n_clusters, len(x)), n_init="auto", random_state=0).fit_predict(x)
    p_values = p_values or [4, 5, 6, 8, 10]
    rows: list[dict[str, Any]] = []
    for cluster, meta in zip(clusters.tolist(), metadata, strict=False):
        n_int = int(meta["n"])
        if n_int <= 0:
            continue
        rows.append(
            {
                **meta,
                "n_int": n_int,
                "cluster": int(cluster),
            }
        )

    candidates: list[dict[str, Any]] = []
    for cluster in sorted({row["cluster"] for row in rows}):
        cluster_rows = [pd.Series(row) for row in rows if row["cluster"] == cluster]
        if len(cluster_rows) < min_support:
            continue
        hard_rate = float(np.mean([int(row.get("hard_case", 0)) == 1 for row in cluster_rows]))
        for p in p_values:
            modulus = 1 << p
            buckets: dict[int, list[pd.Series]] = {}
            for row in cluster_rows:
                buckets.setdefault(int(row["n_int"]) % modulus, []).append(row)
            for residue, values in buckets.items():
                if len(values) < min_support:
                    continue
                candidate = _candidate_from_values(
                    values,
                    modulus,
                    residue,
                    max_k,
                    source="model_cluster",
                    extra={
                        "cluster": int(cluster),
                        "cluster_support": len(cluster_rows),
                        "cluster_hard_case_rate": hard_rate,
                    },
                )
                if candidate:
                    candidates.append(candidate)
    candidates.sort(key=lambda row: (row["suggested_k"], -row["support"], row.get("cluster", -1)))

    if cluster_out:
        save_json(summarize_clusters(x, metadata, n_clusters=n_clusters), cluster_out)
    return candidates


def _lifted_candidate_from_meta(
    meta: dict[str, Any],
    max_k: int,
    source: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    n = int(meta["n"])
    if n <= 0:
        return None
    existing = int(meta.get("first_descent_time", -1))
    k = existing if 0 < existing <= max_k else first_descent_time(n, max_steps=max_k)
    if k is None or k <= 0 or k > max_k:
        return None
    modulus = 1 << int(k)
    residue = n % modulus
    payload = {
        "modulus": modulus,
        "residue": residue,
        "suggested_k": int(k),
        "support": 1,
        "source": source,
        "sample_n": n,
        "sample_bits": abs(n).bit_length(),
        "parent_residue_mod_64": n % 64,
        "parent_residue_mod_1024": n % 1024,
        "v2_3n_plus_1": int(meta.get("v2_3n_plus_1", -1)),
        "descent_bucket": int(meta.get("descent_bucket", -1)),
        "hard_case": int(meta.get("hard_case", -1)),
        "claim": (
            f"for all n ≡ {residue} mod 2^{int(k)}, "
            f"C^{int(k)}(n) < n"
        ),
    }
    if extra:
        payload.update(extra)
    return payload


def mine_lifted_descent_candidates(
    data: str | Path,
    checkpoint: str | Path | None = None,
    max_k: int = 180,
    limit: int | None = 20000,
    max_candidates: int = 256,
    n_clusters: int = 12,
    hard_only: bool = True,
    cluster_out: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Mine parity-stable lifted descent candidates.

    Instead of proposing a small sampled rule such as ``n == a mod 1024``, this
    lifts each representative with descent time ``k`` to ``n == a mod 2^k``.
    The verifier can then prove or reject the exact affine descent rule.
    """

    if checkpoint:
        x, metadata, _ = extract_representations(checkpoint, data, limit=limit)
        clusters = KMeans(n_clusters=min(n_clusters, len(x)), n_init="auto", random_state=0).fit_predict(x)
        cluster_summary = summarize_clusters(x, metadata, n_clusters=n_clusters)
        if cluster_out:
            save_json(cluster_summary, cluster_out)
        metas: list[dict[str, Any]] = []
        for cluster, meta in zip(clusters.tolist(), metadata, strict=False):
            summary = cluster_summary.get(str(cluster), {})
            metas.append(
                {
                    **meta,
                    "cluster": int(cluster),
                    "cluster_hard_case_rate": float(summary.get("hard_case_rate", 0.0)),
                    "cluster_support": int(summary.get("size", 0)),
                }
            )
        source = "lifted_model_cluster"
    else:
        frame = _positive_rows(pd.read_parquet(data))
        if limit is not None and len(frame) > limit:
            frame = frame.sample(n=limit, random_state=0)
        metas = [row.to_dict() for _, row in frame.iterrows()]
        source = "lifted_dataset"

    candidates_by_key: dict[tuple[int, int, int], dict[str, Any]] = {}
    for meta in metas:
        n = int(meta["n"])
        if n <= 0:
            continue
        if hard_only and int(meta.get("hard_case", 0)) != 1:
            continue
        extra = {}
        if "cluster" in meta:
            extra = {
                "cluster": int(meta["cluster"]),
                "cluster_hard_case_rate": float(meta.get("cluster_hard_case_rate", 0.0)),
                "cluster_support": int(meta.get("cluster_support", 0)),
            }
        candidate = _lifted_candidate_from_meta(meta, max_k=max_k, source=source, extra=extra)
        if candidate is None:
            continue
        key = (int(candidate["modulus"]), int(candidate["residue"]), int(candidate["suggested_k"]))
        if key in candidates_by_key:
            candidates_by_key[key]["support"] += 1
            candidates_by_key[key].setdefault("sample_ns", [candidates_by_key[key]["sample_n"]])
            candidates_by_key[key]["sample_ns"].append(candidate["sample_n"])
        else:
            candidates_by_key[key] = candidate

    candidates = list(candidates_by_key.values())
    candidates.sort(
        key=lambda row: (
            -float(row.get("cluster_hard_case_rate", 0.0)),
            int(row["suggested_k"]),
            -int(row["support"]),
            int(row.get("parent_residue_mod_1024", 0)),
        )
    )
    return candidates[:max_candidates]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mine candidate Collatz descent rules.")
    parser.add_argument("--checkpoint", default=None, help="Accepted for workflow symmetry; not trusted as proof.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-k", type=int, default=120)
    parser.add_argument("--min-support", type=int, default=8)
    parser.add_argument("--mode", choices=["dataset", "model_cluster", "lifted"], default="dataset")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--n-clusters", type=int, default=12)
    parser.add_argument("--cluster-out", default=None)
    parser.add_argument("--max-candidates", type=int, default=256)
    parser.add_argument("--include-non-hard", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.mode == "lifted":
        candidates = mine_lifted_descent_candidates(
            args.data,
            checkpoint=args.checkpoint,
            max_k=args.max_k,
            limit=args.limit,
            max_candidates=args.max_candidates,
            n_clusters=args.n_clusters,
            hard_only=not args.include_non_hard,
            cluster_out=args.cluster_out,
        )
    elif args.mode == "model_cluster":
        if not args.checkpoint:
            raise ValueError("--checkpoint is required for --mode model_cluster")
        candidates = mine_model_cluster_descent_candidates(
            args.checkpoint,
            args.data,
            min_support=args.min_support,
            max_k=args.max_k,
            limit=args.limit,
            n_clusters=args.n_clusters,
            cluster_out=args.cluster_out,
        )
    else:
        candidates = mine_residue_descent_candidates(
            args.data,
            min_support=args.min_support,
            max_k=args.max_k,
            source="dataset_scan",
        )
    write_jsonl(candidates, args.out)
    Console().print(f"Wrote {len(candidates)} candidates to {args.out}")


if __name__ == "__main__":
    main()
