"""Modal entrypoints for remote Collatz experiments."""

from __future__ import annotations

import itertools
import tempfile
from pathlib import Path

import modal

app = modal.App("collatz-pattern-lab")
volume = modal.Volume.from_name("collatz-pattern-lab", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "numpy",
        "pandas",
        "pyarrow",
        "polars",
        "pydantic",
        "pyyaml",
        "tqdm",
        "matplotlib",
        "scikit-learn",
        "tensorboard",
        "modal",
        "pytest",
        "rich",
    )
    .add_local_dir("src", remote_path="/root/collatz-pattern-lab/src")
    .add_local_dir("configs", remote_path="/root/collatz-pattern-lab/configs")
    .add_local_dir("reports", remote_path="/root/collatz-pattern-lab/reports")
    .add_local_dir("certificate_store", remote_path="/root/collatz-pattern-lab/certificate_store")
    .add_local_file("proof_manifest.json", remote_path="/root/collatz-pattern-lab/proof_manifest.json")
    .add_local_file("proof_attempts.jsonl", remote_path="/root/collatz-pattern-lab/proof_attempts.jsonl")
)

MOUNT = "/mnt/collatz"


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def generate_remote(
    task: str,
    base: int,
    bits: int,
    n: int,
    out: str,
    lsb_first: bool = True,
    seed: int = 0,
    split_method: str = "random",
    parity_k: int = 32,
    max_steps: int = 10000,
    signed: bool = False,
    sign_mode: str = "positive",
    sample_mode: str = "random",
    positive_fraction: float = 0.5,
    v2_min: int | None = None,
    v2_max: int | None = None,
) -> str:
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.generate import generate_rows, generate_v2_targeted_rows, write_parquet

    use_targeted_v2 = task == "v2" and sample_mode == "random" and not signed and (
        v2_min is not None or v2_max is not None
    )
    if use_targeted_v2:
        if v2_min is None or v2_max is None:
            raise ValueError("v2_min and v2_max must be provided together")
        rows = generate_v2_targeted_rows(
            base=base,
            bits=bits,
            n_rows=n,
            v2_min=v2_min,
            v2_max=v2_max,
            lsb_first=lsb_first,
            seed=seed,
            split_method=split_method,
            parity_k=parity_k,
            max_steps=max_steps,
            signed=signed,
            show_progress=False,
        )
    else:
        rows = generate_rows(
            task=task,
            base=base,
            bits=bits,
            n_rows=n,
            lsb_first=lsb_first,
            seed=seed,
            split_method=split_method,
            parity_k=parity_k,
            max_steps=max_steps,
            signed=signed,
            sign_mode=sign_mode,
            sample_mode=sample_mode,
            positive_fraction=positive_fraction,
            v2_min=v2_min if v2_min is not None else 8,
            v2_max=v2_max if v2_max is not None else 16,
            show_progress=False,
        )
    write_parquet(rows, out)
    volume.commit()
    return out


@app.function(image=image, volumes={MOUNT: volume}, gpu="A10G", cpu=4.0, memory=32768, timeout=24 * 60 * 60)
def train_remote(config_path: str, resume: str | None = None, run_name: str | None = None) -> str:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.train import train
    from collatz_lab.utils import load_yaml, save_yaml

    os.chdir(MOUNT)
    local_config = Path(config_path)
    bundled = Path("/root/collatz-pattern-lab") / config_path
    if bundled.exists():
        local_config.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled, local_config)
    elif not local_config.exists():
        local_config.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled, local_config)
    cfg = load_yaml(local_config)
    cfg.setdefault("run_root", f"{MOUNT}/runs")
    if run_name:
        cfg["run_name"] = run_name
    save_yaml(cfg, local_config)
    run_dir = train(local_config, resume=resume)
    volume.commit()
    return str(run_dir)


@app.function(image=image, volumes={MOUNT: volume}, timeout=24 * 60 * 60)
def sweep_remote(sweep_config_path: str) -> list[str]:
    import copy
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.train import train
    from collatz_lab.utils import load_yaml, nested_set, save_yaml

    os.chdir(MOUNT)
    sweep = load_yaml(sweep_config_path)
    template = load_yaml(sweep["template"])
    keys = list(sweep["parameters"].keys())
    values = [sweep["parameters"][key] for key in keys]
    runs: list[str] = []
    for combo in itertools.product(*values):
        cfg = copy.deepcopy(template)
        for key, value in zip(keys, combo, strict=True):
            nested_set(cfg, key, value)
        cfg.setdefault("run_root", f"{MOUNT}/runs")
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            tmp = Path(f.name)
        save_yaml(cfg, tmp)
        runs.append(str(train(tmp)))
    volume.commit()
    return runs


@app.function(image=image, volumes={MOUNT: volume}, gpu="A10G", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def eval_remote(
    checkpoint_path: str,
    data_path: str,
    out: str | None = None,
    show_progress: bool = False,
    failures_out: str | None = None,
    max_failures: int = 10000,
) -> dict:
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.eval import evaluate_checkpoint

    metrics = evaluate_checkpoint(
        checkpoint_path,
        data_path,
        out=out or f"{MOUNT}/reports/eval_metrics.json",
        show_progress=show_progress,
        failures_out=failures_out,
        max_failures=max_failures,
    )
    volume.commit()
    return metrics


@app.function(image=image, volumes={MOUNT: volume}, gpu="A10G", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def probe_remote(
    checkpoint_path: str,
    data_path: str,
    out: str,
    plot_dir: str | None = None,
    limit: int | None = 20000,
    n_clusters: int = 12,
) -> dict:
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.probes import run_probes

    metrics = run_probes(
        checkpoint_path,
        data_path,
        out,
        plot_dir=plot_dir,
        limit=limit,
        n_clusters=n_clusters,
    )
    volume.commit()
    return metrics


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=16384, timeout=4 * 60 * 60)
def train_proof_policy_remote(traces: str, model_out: str, report_out: str) -> dict:
    import json
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_policy_model import build_training_report, save_policy_model, train_policy_from_traces
    from collatz_lab.proof_trace import load_traces

    bundle = train_policy_from_traces(load_traces(traces))
    save_policy_model(model_out, bundle)
    report = build_training_report(bundle)
    Path(report_out).parent.mkdir(parents=True, exist_ok=True)
    Path(report_out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def build_scaled_proof_corpus_remote(
    out: str = f"{MOUNT}/data/proof_corpus/collatz_proof_inventor_v1_10m_shards",
    report_out: str = f"{MOUNT}/reports/proof_corpus/collatz_proof_inventor_v1_10m.json",
    target_examples: int = 10000000,
    min_general_formal: int = 1000000,
    min_collatz_structural: int = 6000000,
    min_verifier_replay: int = 2000000,
    shard_size: int = 100000,
) -> dict:
    import json
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_corpus import write_report_markdown
    from collatz_lab.proof_corpus_scaler import build_scaled_proof_corpus_shards

    os.chdir(MOUNT)
    report = build_scaled_proof_corpus_shards(
        shard_dir=out,
        target_examples=target_examples,
        min_general_formal=min_general_formal,
        min_collatz_structural=min_collatz_structural,
        min_verifier_replay=min_verifier_replay,
        shard_size=shard_size,
    )
    serializable = report
    Path(report_out).parent.mkdir(parents=True, exist_ok=True)
    Path(report_out).write_text(json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report_markdown(serializable, Path(report_out).with_suffix(".md"))
    volume.commit()
    return serializable


@app.function(image=image, volumes={MOUNT: volume}, gpu="A10G", cpu=4.0, memory=32768, timeout=24 * 60 * 60)
def train_proof_transformer_remote(
    corpus: str = f"{MOUNT}/data/proof_corpus/collatz_proof_inventor_v1_10m_shards",
    corpus_report: str = f"{MOUNT}/reports/proof_corpus/collatz_proof_inventor_v1_10m.json",
    model_out: str = f"{MOUNT}/reports/proof_transformer/RUN-009-proof-transformer/checkpoint.pt",
    report_out: str = f"{MOUNT}/reports/proof_transformer/RUN-009-proof-transformer/training_report.json",
    progress_out: str = f"{MOUNT}/reports/proof_transformer/RUN-009-proof-transformer/progress.json",
    max_examples: int | None = None,
    max_steps: int = 100000,
    batch_size: int = 4,
    d_model: int = 512,
    n_heads: int = 8,
    n_layers: int = 16,
    streaming: bool = True,
    progress_every: int = 100,
    checkpoint_every: int = 1000,
    resume_from: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_transformer import train_proof_transformer, write_training_markdown

    os.chdir(MOUNT)
    report = train_proof_transformer(
        corpus,
        model_out,
        report_out,
        max_examples=max_examples,
        corpus_report_path=corpus_report,
        streaming=streaming,
        max_steps=max_steps,
        batch_size=batch_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        progress_out=progress_out,
        progress_every=progress_every,
        checkpoint_every=checkpoint_every,
        resume_from=resume_from,
        commit_callback=volume.commit,
    )
    write_training_markdown(report, Path(report_out).with_suffix(".md"))
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=24576, timeout=24 * 60 * 60)
def train_proof_transformer_a100_remote(
    corpus: str = f"{MOUNT}/data/proof_corpus/collatz_proof_inventor_v1_10m_shards",
    corpus_report: str = f"{MOUNT}/reports/proof_corpus/collatz_proof_inventor_v1_10m.json",
    model_out: str = f"{MOUNT}/reports/proof_transformer/RUN-009-proof-transformer-a100/checkpoint.pt",
    report_out: str = f"{MOUNT}/reports/proof_transformer/RUN-009-proof-transformer-a100/training_report.json",
    progress_out: str = f"{MOUNT}/reports/proof_transformer/RUN-009-proof-transformer-a100/progress.json",
    max_examples: int | None = None,
    max_steps: int = 100000,
    batch_size: int = 8,
    d_model: int = 512,
    n_heads: int = 8,
    n_layers: int = 16,
    streaming: bool = True,
    progress_every: int = 100,
    checkpoint_every: int = 1000,
    resume_from: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_transformer import train_proof_transformer, write_training_markdown

    os.chdir(MOUNT)
    report = train_proof_transformer(
        corpus,
        model_out,
        report_out,
        max_examples=max_examples,
        corpus_report_path=corpus_report,
        streaming=streaming,
        max_steps=max_steps,
        batch_size=batch_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        progress_out=progress_out,
        progress_every=progress_every,
        checkpoint_every=checkpoint_every,
        resume_from=resume_from,
        commit_callback=volume.commit,
    )
    write_training_markdown(report, Path(report_out).with_suffix(".md"))
    volume.commit()
    return report


def _copy_bundled_config(config_path: str) -> None:
    import shutil

    local_config = Path(config_path)
    bundled = Path("/root/collatz-pattern-lab") / config_path
    if bundled.exists():
        local_config.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled, local_config)


def _mounted_path(path: str | None) -> str | None:
    if not path:
        return path
    return path if path.startswith("/") else f"{MOUNT}/{path}"


def _checkpoint_step(path: Path) -> int:
    try:
        return int(path.stem.rsplit("_", 1)[-1])
    except Exception:
        return 0


def _copy_bundled_proof_inputs() -> None:
    import shutil

    root = Path("/root/collatz-pattern-lab")
    for path in (
        "reports/debt_induction/mixed_modulus_debt_verifier.json",
        "reports/debt_induction/high_parent_bypass_report.json",
        "reports/proof_replay_training.jsonl",
        "proof_attempts.jsonl",
    ):
        source = root / path
        target = Path(path)
        if source.exists() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def build_proof_action_v2_corpus(
    out: str = f"{MOUNT}/data/proof_action_v2",
    max_n: int = 100000,
    residue_k_min: int = 4,
    residue_k_max: int = 14,
    negatives_per_positive: int = 3,
    seed: int = 1337,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_dataset import build_dataset, build_arg_parser

    os.chdir(MOUNT)
    _copy_bundled_proof_inputs()
    parser = build_arg_parser()
    args = parser.parse_args(
        [
            "build",
            "--out",
            out,
            "--max-n",
            str(max_n),
            "--residue-k-min",
            str(residue_k_min),
            "--residue-k-max",
            str(residue_k_max),
            "--negatives-per-positive",
            str(negatives_per_positive),
            "--seed",
            str(seed),
        ]
    )
    report = build_dataset(args)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=24576, timeout=2 * 60 * 60)
def train_proof_action_v2_tiny_overfit(
    config_path: str = "configs/collatz_proof_action_v2_tiny_overfit.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_dataset import build_tiny_dataset, build_arg_parser
    from collatz_lab.proof_action_model import train

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    tiny_args = build_arg_parser().parse_args(
        ["build-tiny", "--out", f"{MOUNT}/data/proof_action_v2_tiny", "--num-traces", "10", "--seed", "1337"]
    )
    build_tiny_dataset(tiny_args)
    report = train(config_path)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=49152, timeout=8 * 60 * 60)
def train_proof_action_v2_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_model import train

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    report = train(config_path)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=24576, timeout=2 * 60 * 60)
def eval_proof_action_v2_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_eval import evaluate

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    summary = evaluate(config_path)
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=24576, timeout=2 * 60 * 60)
def run_proof_action_v2_search_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_search import run_search

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    result = run_search(config_path)
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def build_proof_action_v2_ranker_corpus(
    out: str = f"{MOUNT}/data/proof_action_v2_ranker",
    max_n: int = 100000,
    residue_k_min: int = 4,
    residue_k_max: int = 14,
    negatives_per_positive: int = 5,
    seed: int = 1337,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_dataset import build_dataset, build_arg_parser

    os.chdir(MOUNT)
    _copy_bundled_proof_inputs()
    parser = build_arg_parser()
    args = parser.parse_args(
        [
            "build",
            "--out",
            out,
            "--max-n",
            str(max_n),
            "--residue-k-min",
            str(residue_k_min),
            "--residue-k-max",
            str(residue_k_max),
            "--negatives-per-positive",
            str(negatives_per_positive),
            "--pairwise-ranker-examples",
            "true",
            "--stratified-splits",
            "true",
            "--seed",
            str(seed),
        ]
    )
    report = build_dataset(args)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=49152, timeout=8 * 60 * 60)
def train_proof_action_v2_ranker_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_ranker_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_model import train

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    report = train(config_path)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=24576, timeout=2 * 60 * 60)
def eval_proof_action_v2_ranker_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_ranker_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_eval import evaluate

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    summary = evaluate(config_path)
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=24576, timeout=2 * 60 * 60)
def run_proof_action_v2_ranker_search_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_ranker_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_search import run_search

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    result = run_search(config_path)
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def build_proof_action_v2_frontier_eval(
    out: str = f"{MOUNT}/data/proof_action_v2_frontier_eval",
    max_n: int = 1000000,
    residue_k_min: int = 10,
    residue_k_max: int = 22,
    seed: int = 1337,
) -> dict:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_dataset import build_arg_parser, build_frontier_eval_dataset

    os.chdir(MOUNT)
    _copy_bundled_proof_inputs()
    args = build_arg_parser().parse_args(
        [
            "build-frontier-eval",
            "--out",
            out,
            "--max-n",
            str(max_n),
            "--residue-k-min",
            str(residue_k_min),
            "--residue-k-max",
            str(residue_k_max),
            "--trap-states",
            "true",
            "--multi-step-states",
            "true",
            "--s3-s4-s6-focus",
            "true",
            "--seed",
            str(seed),
        ]
    )
    report = build_frontier_eval_dataset(args)
    artifact_dir = Path(f"{MOUNT}/remote_reports/proof_action_v2/RUN-012-proof-action-v2-frontier-search-small-a100")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    source = Path(out) / "frontier_eval_build_summary.json"
    if source.exists():
        shutil.copy2(source, artifact_dir / "frontier_eval_build_summary.json")
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=24576, timeout=2 * 60 * 60)
def eval_proof_action_v2_raw_proposals_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_frontier_search_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_frontier_eval import raw_proposal_eval

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    summary = raw_proposal_eval(config_path)
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_frontier_search_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_frontier_search_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_frontier_search import run_frontier_search

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    summary = run_frontier_search(config_path)
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def build_proof_action_v2_hard_frontier(
    out: str = f"{MOUNT}/data/proof_action_v2_hard_frontier",
    residue_k_min: int = 16,
    residue_k_max: int = 30,
    max_frontier_states: int = 50000,
    seed: int = 1337,
) -> dict:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_frontier_generator import build_hard_frontier_dataset

    os.chdir(MOUNT)
    _copy_bundled_proof_inputs()
    report = build_hard_frontier_dataset(
        out=out,
        residue_k_min=residue_k_min,
        residue_k_max=residue_k_max,
        max_frontier_states=max_frontier_states,
        s3=True,
        s4=True,
        s6=True,
        seed=seed,
    )
    artifact_dir = Path(f"{MOUNT}/remote_reports/proof_action_v2/RUN-013-proof-action-v2-hard-trace-mining")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    source = Path(out) / "hard_frontier_build_summary.json"
    if source.exists():
        shutil.copy2(source, artifact_dir / "hard_frontier_build_summary.json")
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=2 * 60 * 60)
def analyze_proof_action_v2_s6_blockers(
    out: str = f"{MOUNT}/data/proof_action_v2_s6",
) -> dict:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_s6_analyzer import analyze_s6_blockers
    from collatz_lab.proof_action_s6_lemma_generator import generate_s6_candidate_lemmas

    os.chdir(MOUNT)
    _copy_bundled_proof_inputs()
    report = analyze_s6_blockers(out=out)
    generate_s6_candidate_lemmas(blockers_path=Path(out) / "s6_blockers.jsonl", out=Path(out) / "s6_candidate_lemmas.jsonl")
    artifact_dir = Path(f"{MOUNT}/remote_reports/proof_action_v2/RUN-013-proof-action-v2-hard-trace-mining")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for name in ("s6_blocker_summary.json", "s6_candidate_lemmas.jsonl"):
        source = Path(out) / name
        if source.exists():
            shutil.copy2(source, artifact_dir / name)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=8 * 60 * 60)
def mine_proof_action_v2_hard_traces(
    config_path: str = "configs/collatz_proof_action_v2_hard_trace_mining.yaml",
) -> dict:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_trace_miner import mine_hard_traces

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    report = mine_hard_traces(
        config=config_path,
        frontier_dir=f"{MOUNT}/data/proof_action_v2_hard_frontier",
        checkpoint=f"{MOUNT}/remote_reports/proof_action_v2/RUN-011-proof-action-v2-ranker-small-a100/final_checkpoint.pt",
        out=f"{MOUNT}/data/proof_action_v2_hard_traces",
    )
    artifact_dir = Path(f"{MOUNT}/remote_reports/proof_action_v2/RUN-013-proof-action-v2-hard-trace-mining")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "mined_hard_traces.jsonl",
        "rejected_easy_traces.jsonl",
        "baseline_comparison.json",
        "hard_positive_filter_summary.json",
        "leakage_report.json",
        "run_result.json",
    ):
        source = Path(f"{MOUNT}/data/proof_action_v2_hard_traces") / name
        if source.exists():
            shutil.copy2(source, artifact_dir / name)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=2 * 60 * 60)
def build_proof_action_v2_hard_trace_dataset(
    out: str = f"{MOUNT}/data/proof_action_v2_hard_traces",
) -> dict:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_hard_trace_dataset import build_hard_trace_dataset

    os.chdir(MOUNT)
    report = build_hard_trace_dataset(traces=Path(out) / "mined_hard_traces.jsonl", out=out)
    artifact_dir = Path(f"{MOUNT}/remote_reports/proof_action_v2/RUN-013-proof-action-v2-hard-trace-mining")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for name in ("hard_trace_dataset_summary.json", "mining_summary.json"):
        source = Path(out) / name
        if source.exists():
            shutil.copy2(source, artifact_dir / name)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=2 * 60 * 60)
def build_proof_action_v2_hard_mix_dataset(
    out: str = f"{MOUNT}/data/proof_action_v2_hard_mix",
) -> dict:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_hard_mix_dataset import build_hard_mix_dataset

    os.chdir(MOUNT)
    report = build_hard_mix_dataset(
        original_dir=f"{MOUNT}/data/proof_action_v2",
        ranker_dir=f"{MOUNT}/data/proof_action_v2_ranker",
        hard_trace_dir=f"{MOUNT}/data/proof_action_v2_hard_traces",
        s6_dir=f"{MOUNT}/data/proof_action_v2_s6",
        out=out,
        hard_weight=4.0,
        s6_weight=5.0,
        ranker_weight=2.0,
        holdout_hard_traces=True,
        seed=1337,
    )
    artifact_dir = Path(f"{MOUNT}/remote_reports/proof_action_v2/RUN-014-proof-action-v2-hard-retrain-small-a100")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for name in ("mix_summary.json", "leakage_report.json"):
        source = Path(out) / name
        if source.exists():
            shutil.copy2(source, artifact_dir / name)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=2 * 60 * 60)
def build_proof_action_v2_gate_progress_fix_dataset(
    out: str = f"{MOUNT}/data/proof_action_v2_hard_mix_gate_progress",
) -> dict:
    import os
    import shutil
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_hard_mix_dataset import build_hard_mix_dataset

    os.chdir(MOUNT)
    report = build_hard_mix_dataset(
        original_dir=f"{MOUNT}/data/proof_action_v2",
        ranker_dir=f"{MOUNT}/data/proof_action_v2_ranker",
        hard_trace_dir=f"{MOUNT}/data/proof_action_v2_hard_traces",
        s6_dir=f"{MOUNT}/data/proof_action_v2_s6",
        frontier_dir=f"{MOUNT}/data/proof_action_v2_hard_frontier",
        out=out,
        hard_weight=4.0,
        s6_weight=5.0,
        ranker_weight=2.0,
        frontier_gate_progress_weight=12.0,
        holdout_hard_traces=True,
        seed=1337,
    )
    artifact_dir = Path(f"{MOUNT}/remote_reports/proof_action_v2/RUN-014B-proof-action-v2-gate-progress-fix-small-a100")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for name in ("mix_summary.json", "leakage_report.json"):
        source = Path(out) / name
        if source.exists():
            shutil.copy2(source, artifact_dir / name)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=49152, timeout=10 * 60 * 60)
def train_proof_action_v2_hard_retrain_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_hard_retrain_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_model import train

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    report = train(config_path)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def eval_proof_action_v2_hard_retrain_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_hard_retrain_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_hard_retrain_eval import run_hard_retrain_eval

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    summary = run_hard_retrain_eval(config_path)
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_gate_progress_fix_frontier_search_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_gate_progress_fix_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_frontier_search import run_frontier_search
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    checkpoint = str((cfg.get("evaluation") or {}).get("checkpoint") or (cfg.get("model") or {}).get("checkpoint"))
    output_dir = str((cfg.get("output") or {}).get("dir"))
    eval_dir = str((cfg.get("evaluation") or cfg.get("eval") or {}).get("frontier_eval_dir") or f"{MOUNT}/data/proof_action_v2_frontier_eval")
    summary = run_frontier_search(
        config_path,
        checkpoint=f"{MOUNT}/{checkpoint}" if checkpoint and not checkpoint.startswith("/") else checkpoint,
        eval_dir=f"{MOUNT}/{eval_dir}" if eval_dir and not eval_dir.startswith("/") else eval_dir,
        out=f"{MOUNT}/{output_dir}" if output_dir and not output_dir.startswith("/") else output_dir,
    )
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_hard_retrain_frontier_search_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_hard_retrain_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_frontier_search import run_frontier_search

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    summary = run_frontier_search(
        config_path,
        checkpoint=f"{MOUNT}/remote_reports/proof_action_v2/RUN-014-proof-action-v2-hard-retrain-small-a100/final_checkpoint.pt",
        eval_dir=f"{MOUNT}/data/proof_action_v2_frontier_eval",
        out=f"{MOUNT}/remote_reports/proof_action_v2/RUN-014-proof-action-v2-hard-retrain-small-a100",
    )
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=49152, timeout=10 * 60 * 60)
def train_proof_action_v2_candidate_selector_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_listwise_selector_small_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_candidate_selector_dataset import build_candidate_selector_dataset
    from collatz_lab.proof_action_model import train
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    data = cfg.get("data") or {}
    required_paths = [
        Path(str(data.get("candidate_sets") or "")),
        Path(str(data.get("val_candidate_sets") or "")),
        Path(str(data.get("hard_holdout_candidate_sets") or "")),
    ]
    if any(str(path) and (not path.exists() or path.stat().st_size == 0) for path in required_paths):
        build_candidate_selector_dataset(
            frontier_dir=f"{MOUNT}/data/proof_action_v2_hard_frontier",
            hard_trace_dir=f"{MOUNT}/data/proof_action_v2_hard_traces",
            s6_dir=f"{MOUNT}/data/proof_action_v2_s6",
            out=f"{MOUNT}/data/proof_action_v2_candidate_selector",
            min_candidates=5,
            require_gate_progress_candidate=True,
            require_accepted_low_utility_candidate=True,
            require_oracle_gap=0.75,
            seed=1337,
        )
    output_dir = Path(str((cfg.get("output") or {}).get("dir") or "remote_reports/proof_action_v2/RUN-015A-proof-action-v2-listwise-selector-small-a100"))
    final_checkpoint = output_dir / "final_checkpoint.pt"
    partials = sorted(output_dir.glob("checkpoint_step_*.pt"), key=_checkpoint_step)
    resume_checkpoint = str(partials[-1]) if partials and not final_checkpoint.exists() else None
    report = train(config_path, resume_checkpoint=resume_checkpoint)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=6 * 60 * 60)
def eval_proof_action_v2_candidate_selector_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_listwise_selector_small_a100.yaml",
    checkpoint: str | None = None,
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_candidate_selector_eval import evaluate_candidate_selector
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    checkpoint = str(checkpoint or (cfg.get("evaluation") or {}).get("checkpoint") or (cfg.get("model") or {}).get("checkpoint"))
    output_dir = str(output_dir or (cfg.get("output") or {}).get("dir"))
    eval_dir = str((cfg.get("evaluation") or cfg.get("eval") or {}).get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval")
    summary = evaluate_candidate_selector(
        config_path,
        checkpoint=_mounted_path(checkpoint),
        eval_dir=_mounted_path(eval_dir),
        out=_mounted_path(output_dir),
    )
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_candidate_selector_frontier_search_small_a100(
    config_path: str = "configs/collatz_proof_action_v2_listwise_selector_small_a100.yaml",
    checkpoint: str | None = None,
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_frontier_search import run_frontier_search
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    checkpoint = str(checkpoint or (cfg.get("evaluation") or {}).get("checkpoint") or (cfg.get("model") or {}).get("checkpoint"))
    output_dir = str(output_dir or (cfg.get("output") or {}).get("dir"))
    eval_dir = str((cfg.get("evaluation") or cfg.get("eval") or {}).get("frontier_eval_dir") or "data/proof_action_v2_frontier_eval")
    summary = run_frontier_search(
        config_path,
        checkpoint=_mounted_path(checkpoint),
        eval_dir=_mounted_path(eval_dir),
        out=_mounted_path(output_dir),
    )
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_theorem_composer_a100(
    config_path: str = "configs/collatz_proof_action_v2_theorem_composer_run016.yaml",
    checkpoint: str | None = None,
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_theorem_composer import run_theorem_composer
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    checkpoint = str(checkpoint or (cfg.get("evaluation") or {}).get("checkpoint") or (cfg.get("model") or {}).get("checkpoint"))
    output_dir = str(output_dir or (cfg.get("composer") or {}).get("out_dir") or (cfg.get("output") or {}).get("dir"))
    summary = run_theorem_composer(
        config_path,
        checkpoint=_mounted_path(checkpoint),
        frontier_dir=f"{MOUNT}/data/proof_action_v2_frontier_eval",
        s6_dir=f"{MOUNT}/data/proof_action_v2_s6",
        out=_mounted_path(output_dir),
    )
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_s6_lemma_repair_a100(
    config_path: str = "configs/collatz_proof_action_v2_s6_lemma_repair_run017.yaml",
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_s6_lemma_repair import run_s6_lemma_repair
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    output_dir = str(output_dir or (cfg.get("repair") or {}).get("out_dir") or "reports/runs/RUN-017-proof-action-v2-s6-lemma-repair")
    result = run_s6_lemma_repair(config_path, out=_mounted_path(output_dir))
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_residual_coverage_cert(
    config_path: str = "configs/collatz_proof_action_v2_residual_coverage_run018.yaml",
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_residual_coverage import run_residual_coverage_cert
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    output_dir = str(output_dir or (cfg.get("residual") or {}).get("out_dir") or "reports/runs/RUN-018-proof-action-v2-residual-coverage-cert")
    result = run_residual_coverage_cert(config_path, out=_mounted_path(output_dir))
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_parent_residual_cert(
    config_path: str = "configs/collatz_proof_action_v2_parent_residual_run019.yaml",
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_parent_residual import run_parent_residual_cert
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    output_dir = str(output_dir or (cfg.get("parent_residual") or {}).get("out_dir") or "reports/runs/RUN-019-proof-action-v2-parent-residual-cert")
    result = run_parent_residual_cert(config_path, out=_mounted_path(output_dir))
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_exact_s4_parent_transition_cert(
    config_path: str = "configs/collatz_proof_action_v2_parent_transition_run022.yaml",
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_parent_transition_cert import run_parent_transition_certificates
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    output_dir = str(
        output_dir
        or (cfg.get("parent_transition_certificates") or {}).get("out_dir")
        or "reports/runs/RUN-022-exact-s4-parent-transition-certificates"
    )
    result = run_parent_transition_certificates(config_path, out=_mounted_path(output_dir))
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_exact_s6_lemma_payloads(
    config_path: str = "configs/collatz_proof_action_v2_exact_s6_lemma_payloads_run023.yaml",
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_run023 import run_exact_s6_lemma_payloads
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    output_dir = str(
        output_dir
        or (cfg.get("s6_lemma_payloads") or {}).get("out_dir")
        or "reports/runs/RUN-023-exact-s6-lemma-payloads"
    )
    result = run_exact_s6_lemma_payloads(config_path, out=_mounted_path(output_dir))
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_top_level_theorem_certificates(
    config_path: str = "configs/collatz_proof_action_v2_top_level_theorem_certificates_run024.yaml",
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_run024 import run_top_level_theorem_certificates
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    output_dir = str(
        output_dir
        or (cfg.get("top_level_certificates") or {}).get("out_dir")
        or "reports/runs/RUN-024-top-level-theorem-certificates"
    )
    result = run_top_level_theorem_certificates(config_path, out=_mounted_path(output_dir))
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_external_audit_package(
    config_path: str = "configs/collatz_proof_action_v2_external_audit_run025.yaml",
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_run025 import run_external_audit_package
    from collatz_lab.utils import load_yaml

    os.chdir("/root/collatz-pattern-lab")
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    output_dir = str(
        output_dir
        or (cfg.get("external_audit") or {}).get("out_dir")
        or "reports/runs/RUN-025-proof-candidate-external-audit-package"
    )
    result = run_external_audit_package(config_path, out=output_dir)
    volume.commit()
    return result


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def run_proof_action_v2_theorem_composer(
    config_path: str = "configs/collatz_proof_action_v2_theorem_composer_run016.yaml",
    checkpoint: str | None = None,
    s6_dir: str | None = None,
    output_dir: str | None = None,
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_theorem_composer import run_theorem_composer
    from collatz_lab.utils import load_yaml

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    cfg = load_yaml(config_path)
    checkpoint = str(checkpoint or (cfg.get("evaluation") or {}).get("checkpoint") or (cfg.get("model") or {}).get("checkpoint"))
    output_dir = str(output_dir or (cfg.get("composer") or {}).get("out_dir") or (cfg.get("output") or {}).get("dir"))
    s6_dir = str(s6_dir or (cfg.get("composer") or {}).get("s6_dir") or "data/proof_action_v2_s6")
    summary = run_theorem_composer(
        config_path,
        checkpoint=_mounted_path(checkpoint),
        frontier_dir=f"{MOUNT}/data/proof_action_v2_frontier_eval",
        s6_dir=_mounted_path(s6_dir),
        out=_mounted_path(output_dir),
    )
    volume.commit()
    return summary


@app.function(image=image, volumes={MOUNT: volume}, gpu="A100-40GB", cpu=4.0, memory=65536, timeout=24 * 60 * 60)
def train_proof_action_v2_big_a100(
    config_path: str = "configs/collatz_proof_action_v2_big_a100.yaml",
) -> dict:
    import os
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.proof_action_model import train

    os.chdir(MOUNT)
    _copy_bundled_config(config_path)
    report = train(config_path)
    volume.commit()
    return report


@app.function(image=image, volumes={MOUNT: volume}, gpu="A10G", cpu=4.0, memory=32768, timeout=4 * 60 * 60)
def discover_remote(
    data_path: str,
    out: str,
    checkpoint_path: str | None = None,
    mode: str = "dataset",
    cluster_out: str | None = None,
    max_k: int = 180,
    min_support: int = 20,
    limit: int | None = 20000,
    n_clusters: int = 12,
    max_candidates: int = 256,
    include_non_hard: bool = False,
) -> str:
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.discover import (
        mine_lifted_descent_candidates,
        mine_model_cluster_descent_candidates,
        mine_residue_descent_candidates,
    )
    from collatz_lab.utils import write_jsonl

    if mode == "lifted":
        candidates = mine_lifted_descent_candidates(
            data_path,
            checkpoint=checkpoint_path,
            max_k=max_k,
            limit=limit,
            max_candidates=max_candidates,
            n_clusters=n_clusters,
            hard_only=not include_non_hard,
            cluster_out=cluster_out,
        )
    elif mode == "model_cluster":
        if checkpoint_path is None:
            raise ValueError("checkpoint_path is required for mode='model_cluster'")
        candidates = mine_model_cluster_descent_candidates(
            checkpoint_path,
            data_path,
            min_support=min_support,
            max_k=max_k,
            limit=limit,
            n_clusters=n_clusters,
            cluster_out=cluster_out,
        )
    elif mode == "dataset":
        candidates = mine_residue_descent_candidates(
            data_path,
            min_support=min_support,
            max_k=max_k,
            source="dataset_scan",
        )
    else:
        raise ValueError("mode must be 'dataset', 'model_cluster', or 'lifted'")
    write_jsonl(candidates, out)
    volume.commit()
    return out


@app.function(image=image, volumes={MOUNT: volume}, timeout=4 * 60 * 60)
def verify_remote(
    rules_path: str,
    out: str,
    samples_per_rule: int = 500,
    max_t: int = 180,
    search_limit: int = 200000,
) -> str:
    import json
    import sys

    sys.path.insert(0, "/root/collatz-pattern-lab/src")
    from collatz_lab.verifier import verify_rules_file

    results = verify_rules_file(
        rules_path,
        samples_per_rule=samples_per_rule,
        max_t=max_t,
        search_limit=search_limit,
    )
    output_path = Path(out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    volume.commit()
    return str(output_path)


@app.function(image=image, volumes={MOUNT: volume}, timeout=4 * 60 * 60)
def analyze_remote(run_id: str) -> str:
    report_path = Path(MOUNT) / "reports" / f"{run_id}_analysis.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        f"# Analysis for {run_id}\n\nAdd probe, discovery, and verifier outputs here.\n",
        encoding="utf-8",
    )
    volume.commit()
    return str(report_path)
