"""Post-process exact lifted Collatz descent certificates."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from rich.console import Console

from .collatz import parity_prefix
from .verifier import affine_for_parity_prefix


def _load_verification_rows(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected verifier rows in {path}")
    return data


def _rule_key(rule: dict[str, Any], exact: dict[str, Any]) -> tuple[int, int, int]:
    modulus = int(exact.get("modulus", rule.get("modulus")))
    residue = int(exact.get("residue", rule.get("residue"))) % modulus
    k = int(exact.get("k", rule.get("suggested_k")))
    return modulus, residue, k


def _certificate_signature(rule: dict[str, Any], exact: dict[str, Any]) -> dict[str, Any]:
    modulus, residue, k = _rule_key(rule, exact)
    representative = residue if residue > 0 else modulus
    prefix = parity_prefix(representative, k)
    a, b, d = affine_for_parity_prefix(prefix)
    odd_steps = sum(prefix)
    return {
        "modulus": modulus,
        "residue": residue,
        "k": k,
        "odd_steps": odd_steps,
        "parent_residue_mod_64": int(rule.get("parent_residue_mod_64", representative % 64)),
        "parent_residue_mod_1024": int(rule.get("parent_residue_mod_1024", representative % 1024)),
        "affine_A": a,
        "affine_B": b,
        "affine_D": d,
        "affine_signature": f"A={a};B={b};D={d}",
        "contraction_margin_num": d - a,
        "source": rule.get("source", ""),
        "cluster": rule.get("cluster"),
        "support": int(rule.get("support", 1)),
        "sample_n": rule.get("sample_n"),
    }


def summarize_lifted_certificates(
    verification_rows: list[dict[str, Any]],
    compression_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize exact PASS lifted rules without claiming global closure."""

    compression_report = compression_report or {}
    deduped: dict[tuple[int, int, int], dict[str, Any]] = {}
    status_counts: Counter[str] = Counter()
    for row in verification_rows:
        exact = dict(row.get("exact", {}))
        rule = dict(row.get("rule", {}))
        status = str(exact.get("status", "MISSING"))
        status_counts[status] += 1
        if status != "PASS":
            continue
        key = _rule_key(rule, exact)
        if key not in deduped:
            deduped[key] = _certificate_signature(rule, exact)
        else:
            deduped[key]["support"] += int(rule.get("support", 1))

    certificates = list(deduped.values())
    certificates.sort(key=lambda row: (row["k"], row["parent_residue_mod_64"], row["residue"]))

    def count_by(field: str) -> list[dict[str, Any]]:
        counts = Counter(row[field] for row in certificates)
        return [
            {"value": value, "count": count}
            for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    grouped: dict[str, dict[str, Any]] = {}
    buckets: defaultdict[tuple[int, int, int, str], list[dict[str, Any]]] = defaultdict(list)
    for cert in certificates:
        key = (
            int(cert["parent_residue_mod_64"]),
            int(cert["k"]),
            int(cert["odd_steps"]),
            str(cert["affine_signature"]),
        )
        buckets[key].append(cert)
    for index, (key, rows) in enumerate(sorted(buckets.items(), key=lambda item: (-len(item[1]), item[0]))):
        parent_residue, k, odd_steps, affine_signature = key
        grouped[f"group_{index:04d}"] = {
            "parent_residue_mod_64": parent_residue,
            "k": k,
            "odd_steps": odd_steps,
            "affine_signature": affine_signature,
            "certificate_count": len(rows),
            "residues": [int(row["residue"]) for row in rows[:20]],
        }

    raw_leaf_count = int(
        compression_report.get("raw_leaf_count", compression_report.get("raw_verified_leaves", len(certificates)))
    )
    compressed_leaf_count = int(
        compression_report.get("compressed_leaf_count", compression_report.get("compressed_leaves", len(certificates)))
    )
    merged_leaf_count = int(compression_report.get("merged_leaf_count", compression_report.get("merged_leaves", 0)))
    union_density_all_integers = compression_report.get(
        "selected_union_density_all_integers",
        compression_report.get("union_density_all_integers"),
    )
    union_density_percent = compression_report.get(
        "selected_union_density_percent",
        compression_report.get("union_density_percent"),
    )
    exact_pass_count = len(certificates)
    exact_total = len(verification_rows)
    global_claim_status = (
        "LOCAL_CERTIFICATES_ONLY_NEEDS_COMPRESSION"
        if exact_pass_count
        else "NO_VERIFIED_LIFTED_CERTIFICATES"
    )
    compression_status = "NO_MERGES_FOUND" if raw_leaf_count and merged_leaf_count == 0 else "COMPRESSION_FOUND_MERGES"

    return {
        "status": global_claim_status,
        "compression_status": compression_status,
        "global_proof_closure": False,
        "reason": (
            "Exact lifted certificates prove only their parity-stable residue leaves; "
            "they do not close a global proof obligation unless a verified coverage/compression step is added."
        ),
        "verification_total": exact_total,
        "verification_status_counts": dict(status_counts),
        "verified_leaf_count": exact_pass_count,
        "raw_leaf_count": raw_leaf_count,
        "compressed_leaf_count": compressed_leaf_count,
        "merged_leaf_count": merged_leaf_count,
        "union_density_all_integers": union_density_all_integers,
        "union_density_percent": union_density_percent,
        "family_search_status": compression_report.get("status"),
        "candidate_count": compression_report.get("candidate_count"),
        "candidate_pass_count": compression_report.get("candidate_pass_count"),
        "selected_family_count": compression_report.get("selected_family_count"),
        "selected_generalized_family_count": compression_report.get("selected_generalized_family_count"),
        "selected_union_density_percent": compression_report.get("selected_union_density_percent"),
        "parent_residue_mod_64": count_by("parent_residue_mod_64"),
        "k_values": count_by("k"),
        "odd_step_counts": count_by("odd_steps"),
        "affine_group_count": len(grouped),
        "top_affine_groups": list(grouped.values())[:20],
        "certificates_sample": certificates[:20],
    }


def summarize_lifted_certificates_file(
    verification_path: str | Path,
    out: str | Path | None = None,
    compression_path: str | Path | None = None,
) -> dict[str, Any]:
    rows = _load_verification_rows(verification_path)
    compression = None
    if compression_path:
        compression = json.loads(Path(compression_path).read_text(encoding="utf-8"))
    summary = summarize_lifted_certificates(rows, compression)
    if out:
        output_path = Path(out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize verified lifted Collatz certificates.")
    parser.add_argument("--verification", required=True)
    parser.add_argument("--compression", default=None)
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    summary = summarize_lifted_certificates_file(args.verification, out=args.out, compression_path=args.compression)
    Console().print(
        {
            "out": args.out,
            "verified_leaf_count": summary["verified_leaf_count"],
            "compression_status": summary["compression_status"],
            "global_proof_closure": summary["global_proof_closure"],
        }
    )


if __name__ == "__main__":
    main()
