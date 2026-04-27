"""Verifier-backed closure audit for high-weight P6 frontier buckets.

This module is deliberately stricter than the weighted-progress diagnostic:
it recomputes the exact finite transition split for each target bucket and
counts q-class mass as newly closed only when every child branch has an exact
closure certificate that pays ancestor descent debt.  Parent-level decreases
are useful structure, but they are not proof closure by themselves because the
low-h burst block expands the ancestor value.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .cycle_certificates import certify_affine_return_map
from .cycle_miner import affine_return_from_parent_return_row
from .parent_state_system import classify_parent_residue
from .proof_schema import CLOSED_STATUSES
from .return_maps import derive_parent_return_maps


def parent_burst_affine_on_n(a: int, h: int) -> dict[str, Any]:
    """Return the exact affine block for one forced parent burst on ``n``.

    For ``n = 2**a*r - 1`` and ``h = v2(3**a*r - 1)``, the post-burst value is

        ``(3**a*n + 3**a - 2**a) / 2**(a+h)``.
    """

    if a < 1:
        raise ValueError("a must be positive")
    if h < 0:
        raise ValueError("h must be non-negative")
    A = 3**a
    B = A - (1 << a)
    D = 1 << (a + h)
    return {
        "A": A,
        "B": B,
        "D": D,
        "A_minus_D": A - D,
        "expands_ancestor_value": A >= D,
        "log_growth": math.log(A / D),
    }


def _group_parent_split(a: int, h: int, r_depth: int) -> list[dict[str, Any]]:
    groups: dict[int, list[dict[str, Any]]] = {}
    for r in range(1, 1 << r_depth, 2):
        row = classify_parent_residue(a, r, r_depth)
        if row["h"] != h:
            continue
        groups.setdefault(int(row["a_next"]), []).append(row)
    children: list[dict[str, Any]] = []
    for a_next, rows in sorted(groups.items()):
        if a_next < a:
            relation = "lower"
        elif a_next == a:
            relation = "self"
        else:
            relation = "higher"
        children.append(
            {
                "a_next": a_next,
                "relation": relation,
                "residue_count": len(rows),
                "sample_r_residues": [int(row["r_residue"]) for row in rows[:12]],
            }
        )
    return children


def _return_map_certificate(a: int, h: int) -> dict[str, Any] | None:
    rows = derive_parent_return_maps(a, a, h, h)
    if not rows:
        return None
    row = rows[0]
    if not row.get("sample_check_passed"):
        return {
            "status": "UNKNOWN",
            "reason": "derived parent return map failed its exact sample check",
            "return_map": row,
        }
    return_map = affine_return_from_parent_return_row(row)
    cert = certify_affine_return_map(return_map)
    return {
        "status": cert["status"],
        "return_map": return_map.to_dict(),
        "certificate": cert,
    }


def _child_closure_status(a: int, h: int, child: dict[str, Any], block: dict[str, Any]) -> dict[str, Any]:
    relation = str(child["relation"])
    if relation == "higher":
        return {
            **child,
            "closure_status": "NEEDS_SPLIT",
            "is_closed": False,
            "reason": "transition raises parent level; no well-founded rank is available",
        }
    if relation == "lower":
        if not bool(block["expands_ancestor_value"]):
            return {
                **child,
                "closure_status": "CLOSED_BY_ANCESTOR_DESCENT",
                "is_closed": True,
                "reason": "the burst block itself pays ancestor descent debt",
            }
        return {
            **child,
            "closure_status": "BLOCKED_BY_UNPAID_ANCESTOR_DEBT",
            "is_closed": False,
            "reason": (
                "parent level decreases, but the low-h burst expands n; a debt-carrying "
                "induction theorem is required before this can close"
            ),
        }
    if relation == "self":
        cert = _return_map_certificate(a, h)
        if cert and cert.get("status") == "PROVED_HEIGHT_DECREASE_ON_REPEAT":
            return {
                **child,
                "closure_status": "REDUCED_BY_HEIGHT_RANKED_SELF_RETURN",
                "is_closed": False,
                "reason": (
                    "the exact self-return cannot repeat forever, but exits still need "
                    "ancestor-debt closure before the parent bucket is closed"
                ),
                "self_return_certificate": cert,
            }
        return {
            **child,
            "closure_status": "NEEDS_SELF_RETURN_RANKING",
            "is_closed": False,
            "reason": "self transition lacks a height-ranking certificate",
            "self_return_certificate": cert,
        }
    return {
        **child,
        "closure_status": "UNKNOWN",
        "is_closed": False,
        "reason": f"unknown transition relation {relation!r}",
    }


def _debt_certificate_covers_bucket(bucket: dict[str, Any], debt_induction_report: dict[str, Any] | None) -> bool:
    if not debt_induction_report:
        return False
    if debt_induction_report.get("status") != "PROVED_DEBT_CARRYING_PARENT_INDUCTION":
        return False
    if not debt_induction_report.get("ready_for_run7"):
        return False
    targets = {str(item) for item in debt_induction_report.get("target_obligations", [])}
    return str(bucket.get("obligation_id")) in targets


def audit_bucket(
    bucket: dict[str, Any],
    r_depth: int = 7,
    debt_induction_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    a = int(bucket["a"])
    h = int(bucket["h"])
    expected_split = bucket.get("parent_transition_split") or {}
    expected_children = expected_split.get("children") or []
    block = parent_burst_affine_on_n(a, h)
    actual_children = _group_parent_split(a, h, r_depth)
    actual_counts = {(row["a_next"], row["relation"]): row["residue_count"] for row in actual_children}
    expected_counts = {
        (int(row["a_next"]), str(row["relation"])): int(row["residue_count"])
        for row in expected_children
    }
    split_matches = not expected_counts or expected_counts == actual_counts
    audited_children = [
        _child_closure_status(a, h, child, block)
        for child in actual_children
    ]
    debt_certificate_covers_bucket = _debt_certificate_covers_bucket(bucket, debt_induction_report)
    if debt_certificate_covers_bucket:
        audited_children = [
            {
                **child,
                "closure_status": "CLOSED_BY_TRANSITION_TO_CLOSED_STATE",
                "is_closed": True,
                "reason": "covered by a verified debt-carrying parent-state induction certificate",
            }
            for child in audited_children
        ]
    closed = bool(audited_children) and all(bool(child["is_closed"]) for child in audited_children)
    if closed:
        status = "CLOSED_BY_TRANSITION_TO_CLOSED_STATE"
    elif any(child["closure_status"] == "BLOCKED_BY_UNPAID_ANCESTOR_DEBT" for child in audited_children):
        status = "NEEDS_DEBT_CARRYING_PARENT_INDUCTION"
    else:
        status = "NEEDS_SPLIT"
    return {
        "rank": int(bucket.get("rank", 0)),
        "obligation_id": str(bucket["obligation_id"]),
        "a": a,
        "h": h,
        "t": int(bucket.get("t", a - 6)),
        "unknown_q_classes": int(bucket.get("unknown_q_classes", bucket.get("q_class_count", 0)) or 0),
        "bucket_weight_percent": float(bucket.get("bucket_weight_percent", bucket.get("percent_of_frontier", 0.0)) or 0.0),
        "status": status,
        "is_closed": status in CLOSED_STATUSES,
        "split_matches_weighted_report": split_matches,
        "debt_induction_certificate_applied": debt_certificate_covers_bucket,
        "parent_burst_affine_on_n": block,
        "child_status_counts": dict(Counter(str(child["closure_status"]) for child in audited_children)),
        "children": audited_children,
    }


def build_top_bucket_closure_report(
    weighted_report: dict[str, Any],
    top_n: int = 10,
    r_depth: int = 7,
    debt_induction_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    breakdown = dict(weighted_report.get("proof_progress_breakdown") or {})
    selected = dict(breakdown.get("selected") or {})
    baseline_numerator = int(selected.get("numerator", 0))
    denominator = int(selected.get("denominator", 0))
    target_buckets = list(weighted_report.get("target_buckets") or [])[:top_n]
    audits = [
        audit_bucket(bucket, r_depth=r_depth, debt_induction_report=debt_induction_report)
        for bucket in target_buckets
    ]
    closed_q_classes = sum(int(row["unknown_q_classes"]) for row in audits if row["is_closed"])
    target_q_classes = sum(int(row["unknown_q_classes"]) for row in audits)
    numerator = baseline_numerator + closed_q_classes
    proof_progress_percent = 0.0 if denominator <= 0 else numerator / denominator * 100.0
    target_if_all_closed_percent = 0.0 if denominator <= 0 else (baseline_numerator + target_q_classes) / denominator * 100.0
    blocked_by_debt = [
        row["obligation_id"]
        for row in audits
        if row["status"] == "NEEDS_DEBT_CARRYING_PARENT_INDUCTION"
    ]
    selected.update(
        {
            "numerator": numerator,
            "denominator": denominator,
            "percent": proof_progress_percent,
            "status": "finite_depth_diagnostic_not_global_proof",
            "run6_added_closed_q_classes": closed_q_classes,
            "run6_closed_bucket_count": sum(1 for row in audits if row["is_closed"]),
            "run6_target_bucket_count": len(audits),
        }
    )
    breakdown["selected"] = selected
    return {
        "status": "TOP_BUCKET_CLOSURE_AUDIT_NOT_COLLATZ_PROOF",
        "proof_progress_metric": "weighted_p6_finite_frontier_coverage_after_exact_top_bucket_audit",
        "proof_progress_percent": proof_progress_percent,
        "proof_progress_breakdown": breakdown,
        "baseline_certified_q_classes": baseline_numerator,
        "denominator_q_classes": denominator,
        "top_n": top_n,
        "target_q_classes": target_q_classes,
        "closed_target_q_classes": closed_q_classes,
        "closed_target_bucket_count": sum(1 for row in audits if row["is_closed"]),
        "target_bucket_count": len(audits),
        "target_progress_if_all_top_n_closed_percent": target_if_all_closed_percent,
        "blocked_by_debt_induction": blocked_by_debt,
        "debt_induction_status": None if debt_induction_report is None else debt_induction_report.get("status"),
        "ready_for_run7": bool(debt_induction_report and debt_induction_report.get("ready_for_run7")),
        "useful_action_rate": 0.0,
        "model_guided_obligation_closure_rate": 0.0,
        "interpretation": (
            "Run 6 recomputed the exact top-bucket parent-transition splits and did not "
            "count parent-level decreases as closure when the low-h burst block expands "
            "the ancestor value. Closing these buckets requires a debt-carrying parent "
            "induction theorem, not another weighted-progress relabel."
        ),
        "next_step": (
            "Prove a debt-carrying parent-state induction lemma that pays the expansion "
            "created by low-h transitions; only then rerun the top-10 closure audit."
        ),
        "target_buckets": audits,
    }


def write_top_bucket_closure_markdown(report: dict[str, Any], out: str | Path) -> None:
    lines = [
        "# Top-Bucket Closure Audit",
        "",
        f"- status: `{report['status']}`",
        f"- selected progress: `{report['proof_progress_percent']}`%",
        f"- baseline certified q-classes: `{report['baseline_certified_q_classes']}`",
        f"- denominator q-classes: `{report['denominator_q_classes']}`",
        f"- target q-classes: `{report['target_q_classes']}`",
        f"- closed target q-classes: `{report['closed_target_q_classes']}`",
        f"- target progress if all top {report['top_n']} closed: `{report['target_progress_if_all_top_n_closed_percent']}`%",
        "",
        "This audit does not count a bucket as closed unless every child branch has an exact closure certificate.",
        "",
        "## Bucket Results",
        "",
    ]
    for bucket in report["target_buckets"]:
        block = bucket["parent_burst_affine_on_n"]
        lines.extend(
            [
                f"### {bucket['obligation_id']}",
                "",
                f"- status: `{bucket['status']}`",
                f"- unknown q-classes: `{bucket['unknown_q_classes']}`",
                f"- split matches weighted report: `{bucket['split_matches_weighted_report']}`",
                f"- burst affine: `A={block['A']}`, `D={block['D']}`, `A-D={block['A_minus_D']}`",
                f"- child status counts: `{bucket['child_status_counts']}`",
                "",
            ]
        )
    lines.extend(["## Next Step", "", str(report["next_step"]), ""])
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit exact closure of top weighted P6 frontier buckets.")
    parser.add_argument("--weighted-report", required=True)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--r-depth", type=int, default=7)
    parser.add_argument("--debt-induction-report", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-md", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    weighted_report = json.loads(Path(args.weighted_report).read_text(encoding="utf-8"))
    debt_induction_report = (
        json.loads(Path(args.debt_induction_report).read_text(encoding="utf-8"))
        if args.debt_induction_report
        else None
    )
    report = build_top_bucket_closure_report(
        weighted_report,
        top_n=args.top_n,
        r_depth=args.r_depth,
        debt_induction_report=debt_induction_report,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out = Path(args.out_md) if args.out_md else out.with_suffix(".md")
    write_top_bucket_closure_markdown(report, md_out)
    Console().print(
        {
            "out": str(out),
            "markdown": str(md_out),
            "closed_target_bucket_count": report["closed_target_bucket_count"],
            "proof_progress_percent": report["proof_progress_percent"],
        }
    )


if __name__ == "__main__":
    main()
