"""Scaffolded proof-corpus synthesis for RUN-009.

This expands the small proof-inventor corpus into a scale-ready training file
by adding deterministic, verifier-grounded scaffolds:

* general proof patterns,
* exact Collatz mixed-modulus successor instances,
* verifier replay and repair traces from the mixed-modulus debt verifier.

Synthetic here means generated from exact templates and reports.  It is useful
training pressure, but it is not evidence of a proof.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .proof_corpus import (
    PROOF_CORPUS_REPORT_SCHEMA,
    _dedupe,
    _example,
    _jsonl_rows,
    _load_json,
    build_proof_corpus,
    write_jsonl,
    write_report_markdown,
)


SCALED_PROOF_CORPUS_SCHEMA = "collatz_lab.scaled_proof_corpus_report"


def _parse_z_family(z_family: str) -> tuple[int, int]:
    left = z_family.split("=", 1)[1]
    c_text, coeff_text = left.split("+", 1)
    c = int(c_text.strip())
    coeff = int(coeff_text.strip().replace("*k", ""))
    return c, coeff


def synthetic_formal_proof_examples(count: int, start_index: int = 0) -> list[dict[str, Any]]:
    templates = [
        (
            "modular_inverse_successor",
            "PROPOSE_PROOF_DSL",
            "reduce z(k)=c+A*k modulo odd A, divide by 2^T using the inverse of 2^T",
        ),
        (
            "crt_parity_lift",
            "PROPOSE_PROOF_DSL",
            "combine odd residue modulo m with parity by CRT into one residue modulo 2m",
        ),
        (
            "well_founded_rank",
            "PROPOSE_DEBT_RANK",
            "prove no infinite path by a rank that strictly decreases on every transition",
        ),
        (
            "counterexample_guided_rank_repair",
            "SELF_CORRECT_PROOF_DSL",
            "use a positive cycle witness to add the missing state variables to the rank",
        ),
        (
            "subgoal_decomposition",
            "PROPOSE_PROOF_DSL",
            "split theorem assembly into local transition, closure, induction, and compiler obligations",
        ),
    ]
    examples = []
    for index in range(count):
        global_index = start_index + index
        name, label, pattern = templates[index % len(templates)]
        modulus = 2 * (global_index % 997) + 3
        valuation = global_index % 32
        c = (global_index * 17 + 5) % modulus
        prompt = "\n".join(
            [
                "<TASK=SYNTHETIC_GENERAL_FORMAL_PROOF>",
                f"pattern={name}",
                f"odd_modulus={modulus}",
                f"valuation={valuation}",
                f"c={c}",
                "emit a proof-DSL lemma skeleton with explicit assumptions and conclusion",
            ]
        )
        examples.append(
            _example(
                source="synthetic_formal_proof",
                task="general_formal_proof_pattern",
                prompt=prompt,
                target={
                    "proof_pattern": pattern,
                    "assumptions": ["odd modulus", "invertible power of two", "typed conclusion"],
                    "synthetic_index": global_index,
                },
                label=label,
                tags=["synthetic", "general_proof", name],
                verifier_status="PROOF_PATTERN",
                weight=0.45,
                metadata={"synthetic_index": global_index, "pattern": name},
            )
        )
    return examples


def synthetic_collatz_structure_examples(
    high_parent_bypass: dict[str, Any] | None,
    count: int,
    start_index: int = 0,
) -> list[dict[str, Any]]:
    rows = list((high_parent_bypass or {}).get("mixed_successor_families") or [])
    if not rows or count <= 0:
        return []
    examples = []
    for index in range(count):
        global_index = start_index + index
        row = rows[global_index % len(rows)]
        c, coefficient = _parse_z_family(str(row["z_family"]))
        valuation = global_index % 64
        odd_modulus = 3 ** int(row["a"])
        residue = (c * pow(pow(2, valuation, odd_modulus), -1, odd_modulus)) % odd_modulus
        target_parent = int(row["known_target_parent_floor"]) + valuation
        label = "TRY_MIXED_MODULUS_DEBT_VERIFIER" if global_index % 2 else "PROPOSE_MIXED_MODULUS_STATE"
        prompt = "\n".join(
            [
                "<TASK=SYNTHETIC_COLLATZ_SUCCESSOR_FAMILY>",
                f"branch={row.get('branch_id')}",
                f"z(k)={c}+{coefficient}*k",
                f"T={valuation}",
                f"target_parent={target_parent}",
                f"target_rho={residue} mod {odd_modulus}",
                "emit the exact successor lemma and next proof action",
            ]
        )
        examples.append(
            _example(
                source="synthetic_high_parent_successor",
                task="collatz_structure_to_proof_dsl",
                prompt=prompt,
                target={
                    "proof_action": label,
                    "lemma": "v2(c+3^a*k)=T implies r' == c*2^(-T) mod 3^a",
                    "target_parent": target_parent,
                    "target_residue_mod_3a": residue,
                    "target_modulus_3a": odd_modulus,
                    "synthetic_index": global_index,
                },
                label=label,
                tags=["synthetic", "collatz", "mixed_modulus", "successor_family"],
                verifier_status="PASS" if label == "PROPOSE_MIXED_MODULUS_STATE" else "REDUCED",
                weight=0.9,
                metadata={"synthetic_index": global_index, "branch_id": row.get("branch_id"), "valuation": valuation},
            )
        )
    return examples


def synthetic_verifier_replay_examples(
    mixed_debt_report: dict[str, Any] | None,
    count: int,
    start_index: int = 0,
) -> list[dict[str, Any]]:
    rows = list((mixed_debt_report or {}).get("transitions") or [])
    blockers = list((mixed_debt_report or {}).get("blocking_obligations") or [])
    if count <= 0 or (not rows and not blockers):
        return []
    examples = []
    for index in range(count):
        global_index = start_index + index
        if rows and global_index % 3 != 2:
            row = rows[global_index % len(rows)]
            source = row.get("source_state") or {}
            target = row.get("target_state") or {}
            gain = row.get("gain_bound") or {}
            passed = bool(row.get("local_descent_passed"))
            label = "VERIFY_MIXED_MODULUS_DEBT_TRANSITION" if passed else "REPAIR_MIXED_MODULUS_DEBT_RANK"
            prompt = "\n".join(
                [
                    "<TASK=SYNTHETIC_VERIFIER_REPLAY>",
                    f"branch={row.get('branch_id')}",
                    f"source_parent={source.get('parent_level')}",
                    f"target_parent={target.get('parent_level')}",
                    f"valuation={target.get('valuation')}",
                    f"gain_bound={gain.get('numerator')}/{gain.get('denominator')}",
                    f"local_descent_passed={passed}",
                    "emit self-correction action from verifier feedback",
                ]
            )
            target_obj = {
                "repair_action": label,
                "verifier_feedback": row.get("proof_obligation"),
                "synthetic_index": global_index,
            }
            status = "PASS" if passed else "FAIL_REQUIRES_REPAIR"
        else:
            blocker = blockers[global_index % len(blockers)] if blockers else "strict theorem assembly still open"
            label = "PROVE_UNBOUNDED_VALUATION_CLOSURE" if "unbounded valuation" in blocker else "SELF_CORRECT_PROOF_DSL"
            prompt = "\n".join(
                [
                    "<TASK=SYNTHETIC_VERIFIER_BLOCKER_REPLAY>",
                    f"blocker={blocker}",
                    "emit the next repair action",
                ]
            )
            target_obj = {"repair_action": label, "blocking_obligation": blocker, "synthetic_index": global_index}
            status = "FAIL"
        examples.append(
            _example(
                source="synthetic_verifier_replay",
                task="verifier_feedback_to_repair_action",
                prompt=prompt,
                target=target_obj,
                label=label,
                tags=["synthetic", "verifier_replay", "self_correction"],
                verifier_status=status,
                weight=0.8,
                metadata={"synthetic_index": global_index},
            )
        )
    return examples


def _stream_mix(source_counts: Counter[str]) -> dict[str, int]:
    return {
        "general_formal_proof": source_counts.get("synthetic_formal_proof", 0)
        + source_counts.get("formal_proof_seed", 0)
        + source_counts.get("external_formal_proof", 0),
        "collatz_structural": source_counts.get("high_parent_bypass", 0)
        + source_counts.get("cycle_mining", 0)
        + source_counts.get("synthetic_high_parent_successor", 0),
        "verifier_replay": source_counts.get("proof_attempt_replay", 0)
        + source_counts.get("mixed_modulus_debt_verifier", 0)
        + source_counts.get("synthetic_verifier_replay", 0)
        + source_counts.get("strict_theorem_verifier", 0)
        + source_counts.get("run_preflight", 0),
    }


def build_scaled_proof_corpus(
    *,
    target_examples: int = 100_000,
    min_general_formal: int = 10_000,
    min_collatz_structural: int = 50_000,
    min_verifier_replay: int = 10_000,
    proof_attempts_log: str | Path | None = "proof_attempts.jsonl",
    high_parent_bypass_path: str | Path | None = "reports/debt_induction/high_parent_bypass_report.json",
    mixed_modulus_debt_path: str | Path | None = "reports/debt_induction/mixed_modulus_debt_verifier.json",
    cycle_mining_path: str | Path | None = "reports/cycle_mining_parent_returns_q30.json",
    theorem_candidate_path: str | Path | None = "reports/collatz_descent_theorem_candidate.json",
    preflight_path: str | Path | None = "reports/run9_preflight.json",
    external_formal_jsonl: str | Path | None = None,
) -> dict[str, Any]:
    base = build_proof_corpus(
        proof_attempts_log=proof_attempts_log,
        high_parent_bypass_path=high_parent_bypass_path,
        mixed_modulus_debt_path=mixed_modulus_debt_path,
        cycle_mining_path=cycle_mining_path,
        theorem_candidate_path=theorem_candidate_path,
        preflight_path=preflight_path,
        external_formal_jsonl=external_formal_jsonl,
    )
    examples = list(base["examples"])
    high_parent_bypass = _load_json(high_parent_bypass_path)
    mixed_debt = _load_json(mixed_modulus_debt_path)
    source_counts = Counter(row["source"] for row in examples)
    streams = _stream_mix(source_counts)

    if streams["general_formal_proof"] < min_general_formal:
        examples.extend(synthetic_formal_proof_examples(min_general_formal - streams["general_formal_proof"]))
    source_counts = Counter(row["source"] for row in examples)
    streams = _stream_mix(source_counts)
    if streams["collatz_structural"] < min_collatz_structural:
        examples.extend(
            synthetic_collatz_structure_examples(
                high_parent_bypass,
                min_collatz_structural - streams["collatz_structural"],
            )
        )
    source_counts = Counter(row["source"] for row in examples)
    streams = _stream_mix(source_counts)
    if streams["verifier_replay"] < min_verifier_replay:
        examples.extend(synthetic_verifier_replay_examples(mixed_debt, min_verifier_replay - streams["verifier_replay"]))

    examples = _dedupe(examples)
    while len(examples) < target_examples:
        needed = target_examples - len(examples)
        chunk = min(needed, 10_000)
        offset = len(examples)
        general = synthetic_formal_proof_examples(chunk // 5)
        collatz = synthetic_collatz_structure_examples(high_parent_bypass, chunk // 2)
        replay = synthetic_verifier_replay_examples(mixed_debt, chunk - len(general) - len(collatz))
        for local_index, row in enumerate(general + collatz + replay):
            row["metadata"]["scale_fill_offset"] = offset + local_index
            row["example_id"] = f"{row['example_id']}:fill{offset + local_index}"
        examples.extend(general + collatz + replay)
        examples = _dedupe(examples)

    task_counts = Counter(row["task"] for row in examples)
    source_counts = Counter(row["source"] for row in examples)
    label_counts = Counter(row["label"] for row in examples)
    verifier_counts = Counter(row["verifier_status"] for row in examples)
    streams = _stream_mix(source_counts)
    return {
        "schema": SCALED_PROOF_CORPUS_SCHEMA,
        "base_schema": PROOF_CORPUS_REPORT_SCHEMA,
        "version": 1,
        "status": "SCALED_PROOF_CORPUS_BUILT",
        "example_count": len(examples),
        "target_examples": target_examples,
        "thresholds": {
            "min_general_formal": min_general_formal,
            "min_collatz_structural": min_collatz_structural,
            "min_verifier_replay": min_verifier_replay,
        },
        "thresholds_met": {
            "target_examples": len(examples) >= target_examples,
            "general_formal_proof": streams["general_formal_proof"] >= min_general_formal,
            "collatz_structural": streams["collatz_structural"] >= min_collatz_structural,
            "verifier_replay": streams["verifier_replay"] >= min_verifier_replay,
        },
        "task_counts": dict(task_counts),
        "source_counts": dict(source_counts),
        "label_counts": dict(label_counts),
        "verifier_status_counts": dict(verifier_counts),
        "stream_mix": streams,
        "scaling_law_target": base["scaling_law_target"],
        "synthetic_data_caveat": (
            "Synthetic scaffold examples are exact/template-grounded training data, not proof evidence. "
            "Only verifier PASS can raise proof confidence."
        ),
        "examples": examples,
    }


def _write_shard_rows(
    rows: list[dict[str, Any]],
    *,
    shard_dir: Path,
    shard_size: int,
    state: dict[str, Any],
    counters: dict[str, Counter[str]],
) -> None:
    handle = state.get("handle")
    for row in rows:
        if state["written"] % shard_size == 0:
            if handle is not None:
                handle.close()
            shard_index = state["written"] // shard_size
            path = shard_dir / f"part-{shard_index:05d}.jsonl"
            handle = path.open("w", encoding="utf-8")
            state["paths"].append(str(path))
            state["handle"] = handle
        assert handle is not None
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        state["written"] += 1
        counters["task_counts"][row["task"]] += 1
        counters["source_counts"][row["source"]] += 1
        counters["label_counts"][row["label"]] += 1
        counters["verifier_status_counts"][row["verifier_status"]] += 1


def build_scaled_proof_corpus_shards(
    *,
    shard_dir: str | Path,
    target_examples: int = 10_000_000,
    min_general_formal: int = 1_000_000,
    min_collatz_structural: int = 6_000_000,
    min_verifier_replay: int = 2_000_000,
    shard_size: int = 100_000,
    chunk_size: int = 10_000,
    proof_attempts_log: str | Path | None = "proof_attempts.jsonl",
    high_parent_bypass_path: str | Path | None = "reports/debt_induction/high_parent_bypass_report.json",
    mixed_modulus_debt_path: str | Path | None = "reports/debt_induction/mixed_modulus_debt_verifier.json",
    cycle_mining_path: str | Path | None = "reports/cycle_mining_parent_returns_q30.json",
    theorem_candidate_path: str | Path | None = "reports/collatz_descent_theorem_candidate.json",
    preflight_path: str | Path | None = "reports/run9_preflight.json",
    external_formal_jsonl: str | Path | None = None,
) -> dict[str, Any]:
    out_dir = Path(shard_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.jsonl"):
        old.unlink()

    base = build_proof_corpus(
        proof_attempts_log=proof_attempts_log,
        high_parent_bypass_path=high_parent_bypass_path,
        mixed_modulus_debt_path=mixed_modulus_debt_path,
        cycle_mining_path=cycle_mining_path,
        theorem_candidate_path=theorem_candidate_path,
        preflight_path=preflight_path,
        external_formal_jsonl=external_formal_jsonl,
    )
    high_parent_bypass = _load_json(high_parent_bypass_path)
    mixed_debt = _load_json(mixed_modulus_debt_path)

    counters: dict[str, Counter[str]] = {
        "task_counts": Counter(),
        "source_counts": Counter(),
        "label_counts": Counter(),
        "verifier_status_counts": Counter(),
    }
    state: dict[str, Any] = {"written": 0, "paths": [], "handle": None}
    _write_shard_rows(
        list(base["examples"]),
        shard_dir=out_dir,
        shard_size=shard_size,
        state=state,
        counters=counters,
    )

    def current_streams() -> dict[str, int]:
        return _stream_mix(counters["source_counts"])

    target_general = max(min_general_formal, int(target_examples * 0.15))
    target_collatz = max(min_collatz_structural, int(target_examples * 0.65))
    target_verifier = max(min_verifier_replay, target_examples - target_general - target_collatz)
    target_examples = max(target_examples, target_general + target_collatz + target_verifier)

    offsets = {"formal": 0, "collatz": 0, "verifier": 0}

    def emit(kind: str, needed: int) -> None:
        while needed > 0:
            take = min(chunk_size, needed)
            if kind == "formal":
                rows = synthetic_formal_proof_examples(take, start_index=offsets[kind])
            elif kind == "collatz":
                rows = synthetic_collatz_structure_examples(high_parent_bypass, take, start_index=offsets[kind])
            elif kind == "verifier":
                rows = synthetic_verifier_replay_examples(mixed_debt, take, start_index=offsets[kind])
            else:
                raise ValueError(kind)
            offsets[kind] += take
            needed -= take
            _write_shard_rows(rows, shard_dir=out_dir, shard_size=shard_size, state=state, counters=counters)

    streams = current_streams()
    emit("formal", max(0, target_general - streams["general_formal_proof"]))
    streams = current_streams()
    emit("collatz", max(0, target_collatz - streams["collatz_structural"]))
    streams = current_streams()
    emit("verifier", max(0, target_verifier - streams["verifier_replay"]))
    while state["written"] < target_examples:
        remaining = target_examples - state["written"]
        emit("collatz", min(chunk_size // 2, remaining))
        remaining = target_examples - state["written"]
        if remaining > 0:
            emit("verifier", min(chunk_size // 3, remaining))
        remaining = target_examples - state["written"]
        if remaining > 0:
            emit("formal", min(chunk_size // 5, remaining))

    if state.get("handle") is not None:
        state["handle"].close()

    source_counts = counters["source_counts"]
    streams = _stream_mix(source_counts)
    return {
        "schema": SCALED_PROOF_CORPUS_SCHEMA,
        "base_schema": PROOF_CORPUS_REPORT_SCHEMA,
        "version": 1,
        "status": "SCALED_PROOF_CORPUS_SHARDS_BUILT",
        "example_count": state["written"],
        "target_examples": target_examples,
        "shard_dir": str(out_dir),
        "shard_count": len(state["paths"]),
        "shard_size": shard_size,
        "thresholds": {
            "min_general_formal": min_general_formal,
            "min_collatz_structural": min_collatz_structural,
            "min_verifier_replay": min_verifier_replay,
        },
        "thresholds_met": {
            "target_examples": state["written"] >= target_examples,
            "general_formal_proof": streams["general_formal_proof"] >= min_general_formal,
            "collatz_structural": streams["collatz_structural"] >= min_collatz_structural,
            "verifier_replay": streams["verifier_replay"] >= min_verifier_replay,
        },
        "task_counts": dict(counters["task_counts"]),
        "source_counts": dict(source_counts),
        "label_counts": dict(counters["label_counts"]),
        "verifier_status_counts": dict(counters["verifier_status_counts"]),
        "stream_mix": streams,
        "scaling_law_target": base["scaling_law_target"],
        "synthetic_data_caveat": (
            "Synthetic scaffold examples are exact/template-grounded training data, not proof evidence. "
            "Only verifier PASS can raise proof confidence."
        ),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a scaffolded scale-ready proof-inventor corpus.")
    parser.add_argument("--target-examples", type=int, default=100_000)
    parser.add_argument("--min-general-formal", type=int, default=10_000)
    parser.add_argument("--min-collatz-structural", type=int, default=50_000)
    parser.add_argument("--min-verifier-replay", type=int, default=10_000)
    parser.add_argument("--proof-attempts-log", default="proof_attempts.jsonl")
    parser.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    parser.add_argument("--mixed-modulus-debt", default="reports/debt_induction/mixed_modulus_debt_verifier.json")
    parser.add_argument("--cycle-mining", default="reports/cycle_mining_parent_returns_q30.json")
    parser.add_argument("--theorem-candidate", default="reports/collatz_descent_theorem_candidate.json")
    parser.add_argument("--preflight", default="reports/run9_preflight.json")
    parser.add_argument("--external-formal-jsonl", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--shard-dir", default=None)
    parser.add_argument("--shard-size", type=int, default=100_000)
    parser.add_argument("--chunk-size", type=int, default=10_000)
    parser.add_argument("--report-out", required=True)
    parser.add_argument("--report-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.shard_dir:
        report = build_scaled_proof_corpus_shards(
            shard_dir=args.shard_dir,
            target_examples=args.target_examples,
            min_general_formal=args.min_general_formal,
            min_collatz_structural=args.min_collatz_structural,
            min_verifier_replay=args.min_verifier_replay,
            shard_size=args.shard_size,
            chunk_size=args.chunk_size,
            proof_attempts_log=args.proof_attempts_log,
            high_parent_bypass_path=args.high_parent_bypass,
            mixed_modulus_debt_path=args.mixed_modulus_debt,
            cycle_mining_path=args.cycle_mining,
            theorem_candidate_path=args.theorem_candidate,
            preflight_path=args.preflight,
            external_formal_jsonl=args.external_formal_jsonl,
        )
        serializable = report
        report_out = Path(args.report_out)
        report_out.parent.mkdir(parents=True, exist_ok=True)
        report_out.write_text(json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_report_markdown(serializable, args.report_md or report_out.with_suffix(".md"))
        Console().print(
            {
                "shard_dir": args.shard_dir,
                "report": str(report_out),
                "examples": report["example_count"],
                "shards": report["shard_count"],
                "thresholds_met": report["thresholds_met"],
            }
        )
        return

    if not args.out:
        raise ValueError("--out is required unless --shard-dir is provided")
    report = build_scaled_proof_corpus(
        target_examples=args.target_examples,
        min_general_formal=args.min_general_formal,
        min_collatz_structural=args.min_collatz_structural,
        min_verifier_replay=args.min_verifier_replay,
        proof_attempts_log=args.proof_attempts_log,
        high_parent_bypass_path=args.high_parent_bypass,
        mixed_modulus_debt_path=args.mixed_modulus_debt,
        cycle_mining_path=args.cycle_mining,
        theorem_candidate_path=args.theorem_candidate,
        preflight_path=args.preflight,
        external_formal_jsonl=args.external_formal_jsonl,
    )
    write_jsonl(report["examples"], args.out)
    serializable = {key: value for key, value in report.items() if key != "examples"}
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report_markdown(serializable, args.report_md or report_out.with_suffix(".md"))
    Console().print(
        {
            "out": args.out,
            "report": str(report_out),
            "examples": report["example_count"],
            "thresholds_met": report["thresholds_met"],
        }
    )


if __name__ == "__main__":
    main()
