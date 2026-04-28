"""Build the RUN-020 proof audit package.

RUN-020 freezes the RUN-019 proof-action artifacts and audits whether the
strict verifier PASS is logically sound with respect to the original Collatz
descent theorem.  This module performs no training, no model inference, and no
search.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console


RUN_ID = "RUN-020-proof-audit-package"
DEFAULT_RUN019_DIR = Path("reports/runs/RUN-019-proof-action-v2-parent-residual-cert")
DEFAULT_OUT_DIR = Path("reports/runs/RUN-020-proof-audit-package")
KEY_SOURCE_FILES = [
    "src/collatz_lab/proof_verifier.py",
    "src/collatz_lab/proof_action_decode.py",
    "src/collatz_lab/proof_action_theorem_composer.py",
    "src/collatz_lab/proof_action_parent_residual.py",
    "src/collatz_lab/proof_action_dsl.py",
    "src/collatz_lab/proof_action_s6_analyzer.py",
]


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: str | Path, data: dict[str, Any]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return str(exc)


def _untracked_file_patch(path: str) -> str:
    if not Path(path).exists():
        return ""
    result = subprocess.run(["git", "diff", "--no-index", "--", "/dev/null", path], text=True, capture_output=True, check=False)
    return result.stdout


def _verifier_diff_since_run018() -> str:
    tracked = _run_git(
        [
            "diff",
            "HEAD",
            "--",
            "src/collatz_lab/proof_verifier.py",
            "src/collatz_lab/proof_action_decode.py",
            "src/collatz_lab/proof_action_theorem_composer.py",
        ]
    )
    return tracked + _untracked_file_patch("src/collatz_lab/proof_action_parent_residual.py")


def _accepted_action_trace(graph: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node_id, node in sorted((graph.get("nodes") or {}).items()):
        for index, accepted in enumerate(node.get("accepted_actions") or []):
            rows.append(
                {
                    "node_id": node_id,
                    "node_type": node.get("node_type"),
                    "node_status": node.get("status"),
                    "accepted_index": index,
                    "action": accepted.get("action"),
                    "action_text": accepted.get("action_text") or node.get("accepted_action_text"),
                    "verifier_check": accepted.get("verifier_check"),
                    "source": node.get("source", {}),
                    "evidence": node.get("evidence", {}),
                }
            )
    return rows


def _action_counts(trace: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in trace:
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        action_type = str(action.get("type", "UNKNOWN"))
        counts[action_type] = counts.get(action_type, 0) + 1
    return dict(sorted(counts.items()))


def _sample_based_accepts(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in trace:
        action = row.get("action") if isinstance(row.get("action"), dict) else {}
        check = row.get("verifier_check") if isinstance(row.get("verifier_check"), dict) else {}
        reason = str(check.get("reason", ""))
        if action.get("type") == "DERIVE_PARENT_TRANSITION" or "samples" in reason:
            out.append(row)
    return out


def _s6_status_accepts(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in trace
        if isinstance(row.get("action"), dict)
        and row["action"].get("type") == "VERIFY_S6_LEMMA"
        and str(row["action"].get("status")) in {"ACCEPT", "PASS"}
    ]


def _manifest(out_dir: Path, run019_dir: Path, generated_files: list[Path]) -> dict[str, Any]:
    artifact_paths = [
        run019_dir / "run_result.json",
        run019_dir / "parent_residual_certificate.json",
        run019_dir / "theorem_composer" / "theorem_dependency_graph.json",
        run019_dir / "theorem_composer" / "theorem_composition_report.json",
        run019_dir / "theorem_composer" / "verified_composition_actions.jsonl",
    ]
    source_hashes = {
        path: _sha256(path)
        for path in KEY_SOURCE_FILES
        if Path(path).exists()
    }
    package_hashes = {
        str(path.relative_to(out_dir)): _sha256(path)
        for path in generated_files
        if path.exists() and path.name != "certificate_hash_manifest.json"
    }
    artifact_hashes = {
        str(path): _sha256(path)
        for path in artifact_paths
        if path.exists()
    }
    return {
        "schema": "collatz_lab.proof_audit_hash_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run": str(run019_dir),
        "git_head": _run_git(["rev-parse", "HEAD"]).strip(),
        "git_status_short": _run_git(["status", "--short"]),
        "source_hashes": source_hashes,
        "run019_artifact_hashes": artifact_hashes,
        "package_hashes": package_hashes,
    }


def _theorem_statement() -> str:
    return """# Theorem Statement

Target theorem:

For every integer `n > 1`, there exists an integer `k >= 1` such that the `k`th standard Collatz iterate satisfies `C^k(n) < n`.

Here `C(n) = n / 2` when `n` is even, and `C(n) = 3n + 1` when `n` is odd.

## Descent Implies Collatz

If the target theorem is true, the full Collatz conjecture follows by strong induction on `n`.

Base case: `n = 1` is already in the terminal cycle.

Induction step: assume every integer `m` with `1 <= m < n` reaches `1`.  For `n > 1`, the descent theorem gives some iterate `C^k(n) = m < n`.  By the induction hypothesis, `m` reaches `1`; therefore `n` reaches `1`.

Audit result for checklist items A and B: PASS as a mathematical implication, independent of the current verifier implementation.
"""


def _strict_soundness_report(
    *,
    run_result: dict[str, Any],
    composer: dict[str, Any],
    trace: list[dict[str, Any]],
    sample_accepts: list[dict[str, Any]],
    s6_accepts: list[dict[str, Any]],
) -> str:
    return f"""# Strict Verifier Soundness Report

RUN-019 reported:

- strict verifier: `{run_result.get("strict_theorem_verifier_result")}`
- proof confidence: `{run_result.get("proof_confidence_percent")}`
- graph nodes accepted: `{composer.get("accepted_node_count")}` / `{composer.get("graph_node_count")}`
- open blockers: `{composer.get("open_blocker_count")}`

## Audit Verdict

`AUDIT_FAIL`

The strict verifier currently accepts a proof-action graph as universal once `open == []`.  It does not independently check that every accepted graph node is backed by a sound mathematical certificate.

Specific verifier gap:

- `src/collatz_lab/proof_verifier.py` promotes a closed proof-action graph to `UNIVERSAL_PARENT_STATES`.
- The node-level acceptance predicates in `src/collatz_lab/proof_action_decode.py` include syntactic/status checks and sample-based checks.
- Therefore graph closure is not yet the same thing as a fully checked theorem proof.

## Evidence

- accepted action trace rows: `{len(trace)}`
- accepted action types: `{json.dumps(_action_counts(trace), sort_keys=True)}`
- accepted `DERIVE_PARENT_TRANSITION` or sample-reason rows: `{len(sample_accepts)}`
- accepted `VERIFY_S6_LEMMA` rows whose action carries status `ACCEPT/PASS`: `{len(s6_accepts)}`

Checklist item E: FAIL.

Checklist item F: FAIL as an audit proof obligation.  The current audit cannot prove S3/S4/S6 lemmas do not assume the theorem they prove, because S6 verification accepts lemma-specific certificate identifiers and status flags rather than replaying a full theorem-independent proof object.

Checklist item G: FAIL.  `DERIVE_PARENT_TRANSITION` can be accepted from `sample_checks_passed` in state facts.

Checklist item H: FAIL.  A finite proof-action graph is promoted to universal parent-state coverage by the strict verifier when the graph has no open nodes.
"""


def _residual_parent_audit(parent_cert: dict[str, Any]) -> str:
    return f"""# Residual Parent Certificate Audit

Certificate: `{parent_cert.get("certificate_id")}`

- status: `{parent_cert.get("status")}`
- parent interpretation: `{parent_cert.get("parent_interpretation")}`
- parent level: `{parent_cert.get("parent_level")}`
- residual range: `[{parent_cert.get("residual_start")}, {parent_cert.get("residual_end")})`
- parent transition path: `{json.dumps(parent_cert.get("parent_transition_path", {}), sort_keys=True)}`
- S3 dependency count: `{parent_cert.get("s3_dependency_count")}`
- S4 dependency count: `{parent_cert.get("s4_dependency_count")}`
- S6 dependency count: `{parent_cert.get("s6_dependency_count")}`
- no-escape dependency count: `{parent_cert.get("no_escape_dependency_count")}`
- ranking delta: `{parent_cert.get("ranking_delta_num")}/{parent_cert.get("ranking_delta_den")}`

## Circularity Check

Checklist item D: PASS for structural non-circularity.

The certificate was built from the RUN-018 theorem graph, before the RUN-019 parent residual action was injected.  Its parent-transition path points to pre-existing accepted nodes, including `{(parent_cert.get("parent_transition_path") or {}).get("strict_node_id")}`.

## Remaining Soundness Caveat

The parent residual certificate is only as sound as the accepted graph nodes it references.  RUN-020 finds that the strict verifier has not yet independently certified those nodes as theorem-independent mathematical certificates.  This caveat is part of the overall `AUDIT_FAIL`.
"""


def _proof_outline(parent_cert: dict[str, Any], composer: dict[str, Any]) -> str:
    return f"""# Human-Readable Proof Outline

1. Prove the descent theorem: for every `n > 1`, some Collatz iterate falls below `n`.
2. Even `n > 2` descend immediately by `C(n) = n/2`.
3. Odd `n` are represented as parent states `P_a`: `n = 2^a q - 1` with `a = v2(n+1)` and `q` odd.
4. S3 nodes encode local debt/ranking decreases.
5. S4 nodes encode parent/lift transitions.
6. S6 nodes compose coverage, lifting, induction, no-escape, and strict blocker closure certificates.
7. RUN-018 left the residual class `n = 2^26 q - 1`.
8. RUN-019 replaces one-shot affine descent for that class with the parent residual certificate `{parent_cert.get("certificate_id")}`.
9. RUN-019 reports graph closure: `{composer.get("accepted_node_count")}/{composer.get("graph_node_count")}` nodes accepted and `{composer.get("open_blocker_count")}` open blockers.

Audit status: `AUDIT_FAIL`.

Reason: the outline is coherent as a proof plan, but the current verifier still treats graph closure and several local status/sample predicates as mathematical proof certificates.  External review should start at `strict_verifier_soundness_report.md` and `audit_failures_or_assumptions.md`.
"""


def _audit_failures() -> str:
    return """# AUDIT_FAIL: Exact Unsound Assumptions / Verifier Gaps

RUN-020 verdict: `AUDIT_FAIL`.

The RUN-019 proof candidate is not ready for external review as a proof.  It is ready for external review as a proof-engineering artifact with identified soundness gaps.

## Checklist

A. The theorem statement is really: for every `n > 1`, some Collatz iterate is smaller than `n`.

Status: PASS.

B. That descent theorem implies the full Collatz conjecture by induction.

Status: PASS.

C. Every positive integer is covered by the parent-state framework.

Status: PASS for representation only: even numbers descend immediately; odd numbers can be written as `2^a q - 1`.  FAIL for proof coverage because current universal coverage is inferred from graph closure.

D. The parent residual certificate for P26 is not circular.

Status: PASS structurally.  It depends on RUN-018 graph nodes, not on the RUN-019 parent residual node.  Its dependencies still need independent soundness audit.

E. The strict verifier does not accept graph closure unless every node has a sound mathematical certificate.

Status: FAIL.  A closed proof-action graph is promoted to `UNIVERSAL_PARENT_STATES`; node certificates are not independently replayed as mathematical proof objects.

F. S3/S4/S6 lemmas do not assume the theorem they prove.

Status: FAIL as audited.  The verifier accepts S6 lemma actions from lemma-specific certificate names/statuses, not from a theorem-independent proof replay.

G. No sample checks passed certificate is treated as universal proof unless backed by exact symbolic logic.

Status: FAIL.  `DERIVE_PARENT_TRANSITION` accepts `sample_checks_passed`.

H. No finite-depth diagnostic is treated as infinite coverage.

Status: FAIL.  The proof-action graph is finite, but the strict verifier marks closed graph coverage as universal.

I. The proof reproduces from a clean clone.

Status: FAIL.  The current proof candidate depends on ignored/generated `reports/runs` artifacts and remote checkpoints/Modal volume state.  The audit package includes a reproduction script, but a clean clone does not contain all required proof artifacts by default.

## Minimal Fix Direction

Do not train.  Replace graph-status acceptance with certificate replay:

- each accepted node must carry a machine-checkable mathematical certificate payload;
- sample checks may be diagnostics only;
- finite frontier coverage may not become universal coverage without an explicit universal theorem certificate;
- S6 lemma verification must replay lemma-specific proof objects rather than trusting status fields.
"""


def _reproduction_script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pytest -q

python -m collatz_lab.proof_action_audit_package \\
  --run019-dir reports/runs/RUN-019-proof-action-v2-parent-residual-cert \\
  --out reports/runs/RUN-020-proof-audit-package

echo "RUN-020 audit package written to reports/runs/RUN-020-proof-audit-package"
echo "Expected verdict: AUDIT_FAIL unless verifier soundness gaps have been repaired."
"""


def build_audit_package(run019_dir: str | Path = DEFAULT_RUN019_DIR, out_dir: str | Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    run019 = Path(run019_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    run_result = _load_json(run019 / "run_result.json")
    parent_cert = _load_json(run019 / "parent_residual_certificate.json")
    composer = _load_json(run019 / "theorem_composer" / "theorem_composition_report.json")
    graph = _load_json(run019 / "theorem_composer" / "theorem_dependency_graph.json")
    trace = _accepted_action_trace(graph)
    sample_accepts = _sample_based_accepts(trace)
    s6_accepts = _s6_status_accepts(trace)

    graph_frozen = {
        "schema": "collatz_lab.proof_action_frozen_dependency_graph",
        "version": 1,
        "run_id": RUN_ID,
        "source_run": str(run019),
        "source_report": str(run019 / "theorem_composer" / "theorem_dependency_graph.json"),
        "source_sha256": _sha256(run019 / "theorem_composer" / "theorem_dependency_graph.json"),
        "graph": graph,
    }

    outputs = {
        "theorem_statement.md": _theorem_statement(),
        "strict_verifier_soundness_report.md": _strict_soundness_report(
            run_result=run_result,
            composer=composer,
            trace=trace,
            sample_accepts=sample_accepts,
            s6_accepts=s6_accepts,
        ),
        "residual_parent_certificate_audit.md": _residual_parent_audit(parent_cert),
        "human_readable_proof_outline.md": _proof_outline(parent_cert, composer),
        "audit_failures_or_assumptions.md": _audit_failures(),
        "reproduction_script.sh": _reproduction_script(),
        "verifier_diff_since_RUN018.patch": _verifier_diff_since_run018(),
    }
    generated_paths: list[Path] = []
    for name, text in outputs.items():
        path = out / name
        path.write_text(text, encoding="utf-8")
        generated_paths.append(path)
    os.chmod(out / "reproduction_script.sh", os.stat(out / "reproduction_script.sh").st_mode | stat.S_IXUSR)

    _write_json(out / "proof_dependency_graph_frozen.json", graph_frozen)
    generated_paths.append(out / "proof_dependency_graph_frozen.json")
    _write_jsonl(out / "accepted_action_trace.jsonl", trace)
    generated_paths.append(out / "accepted_action_trace.jsonl")

    manifest = _manifest(out, run019, generated_paths)
    _write_json(out / "certificate_hash_manifest.json", manifest)
    generated_paths.append(out / "certificate_hash_manifest.json")

    summary = {
        "schema": "collatz_lab.proof_audit_package_summary",
        "version": 1,
        "run_id": RUN_ID,
        "verdict": "AUDIT_FAIL",
        "source_run": str(run019),
        "out_dir": str(out),
        "required_outputs": sorted(path.name for path in generated_paths),
        "run019_strict_verifier_result": run_result.get("strict_theorem_verifier_result"),
        "run019_proof_confidence_percent": run_result.get("proof_confidence_percent"),
        "graph_node_count": composer.get("graph_node_count"),
        "accepted_node_count": composer.get("accepted_node_count"),
        "open_blocker_count": composer.get("open_blocker_count"),
        "sample_based_accept_count": len(sample_accepts),
        "s6_status_accept_count": len(s6_accepts),
        "failure_summary": [
            "strict verifier promotes closed proof-action graph to universal coverage",
            "sample_checks_passed can discharge parent-transition actions",
            "S6 lemma verification trusts status/certificate identifiers rather than replaying proof payloads",
            "clean clone reproduction requires ignored/generated artifacts",
        ],
    }
    _write_json(out / "audit_summary.json", summary)
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build RUN-020 proof audit package.")
    parser.add_argument("--run019-dir", default=str(DEFAULT_RUN019_DIR))
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    summary = build_audit_package(args.run019_dir, args.out)
    Console().print(
        {
            "run_id": summary["run_id"],
            "verdict": summary["verdict"],
            "out_dir": summary["out_dir"],
            "sample_based_accept_count": summary["sample_based_accept_count"],
            "s6_status_accept_count": summary["s6_status_accept_count"],
        }
    )


if __name__ == "__main__":
    main()
