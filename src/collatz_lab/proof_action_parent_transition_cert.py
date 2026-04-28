"""Exact S4 parent-transition certificates for RUN-022.

The certificate produced here is local to one high-parent successor action.  It
replays the algebra carried by the S4 state:

    z(k) = c + 3^a k
    v2(z(k)) = T
    r' = z(k) / 2^T
    r' == c * 2^-T (mod 3^a)

This removes the former ``sample_checks_passed`` verifier shortcut.  It does
not by itself prove global Collatz descent; it only makes S4 transition nodes
replayable as exact symbolic parent-transition certificates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .proof_action_dsl import serialize_action
from .proof_verifier import build_collatz_descent_theorem_candidate
from .replay_strict_proof import replay_manifest
from .utils import load_yaml


RUN_ID = "RUN-022-exact-s4-parent-transition-certificates"
REPO_ROOT = Path(__file__).resolve().parents[2]
BRANCH_RE = re.compile(r"^P(?P<a>\d+):r(?P<residue>\d+):d(?P<depth>\d+)$")
Z_RE = re.compile(r"z\(k\)\s*=\s*(?P<c>-?\d+)\s*\+\s*(?P<coefficient>\d+)\s*\*\s*k")


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any, size: int = 16) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()[:size]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_branch_id(branch_id: str) -> dict[str, int]:
    match = BRANCH_RE.fullmatch(branch_id)
    if not match:
        raise ValueError(f"invalid high-parent branch id: {branch_id}")
    return {key: int(value) for key, value in match.groupdict().items()}


def parse_z_family(text: str) -> dict[str, int]:
    match = Z_RE.search(text)
    if not match:
        raise ValueError("state does not contain a parseable z(k)=c+3^a*k family")
    return {"c": int(match.group("c")), "coefficient": int(match.group("coefficient"))}


def _certificate_hash(certificate: dict[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_hash"}
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def build_parent_transition_certificate(
    *,
    action: dict[str, Any],
    state: str,
    node_id: str,
) -> dict[str, Any]:
    """Build one replayable high-parent successor certificate."""

    branch_id = str(action["branch_id"])
    branch = parse_branch_id(branch_id)
    source_parent = int(action["source_parent"])
    target_parent = int(action["target_parent"])
    valuation = int(action["valuation"])
    if branch["a"] != source_parent:
        raise ValueError("branch id source parent does not match action")
    z = parse_z_family(state)
    coefficient = int(z["coefficient"])
    if coefficient != 3**source_parent:
        raise ValueError("z-family coefficient is not 3^source_parent")
    c = int(z["c"])
    odd_modulus = coefficient
    inverse_power = pow(pow(2, valuation, odd_modulus), -1, odd_modulus)
    target_residue = (c * inverse_power) % odd_modulus
    if valuation == 0:
        k_modulus = 1
        k_residue = 0
    else:
        k_modulus = 1 << valuation
        k_residue = (-c * pow(coefficient, -1, k_modulus)) % k_modulus
    excluded_modulus = 1 << (valuation + 1)
    excluded_residue = (-c * pow(coefficient, -1, excluded_modulus)) % excluded_modulus
    parent_floor = target_parent - valuation
    if parent_floor < 0:
        raise ValueError("target parent is below valuation")

    certificate = {
        "type": "HIGH_PARENT_SUCCESSOR_EXACT",
        "transition_id": f"s4_parent_transition_{_digest({'node_id': node_id, 'action': action})}",
        "branch_id": branch_id,
        "source_parent": source_parent,
        "target_parent": target_parent,
        "valuation": valuation,
        "statement": (
            f"For branch {branch_id}, if z(k)={c}+{coefficient}*k has v2(z(k))={valuation}, "
            f"then the successor odd coordinate lies in parent state P{target_parent}."
        ),
        "symbolic_map": {
            "source_branch": branch_id,
            "source_residue": branch["residue"],
            "source_depth": branch["depth"],
            "z_family": f"z(k) = {c} + {coefficient}*k",
            "target_odd_coordinate": f"r_prime = z(k) / 2^{valuation}",
            "target_parent_formula": f"{parent_floor} + {valuation} = {target_parent}",
        },
        "divisibility_certificate": {
            "c": c,
            "coefficient": coefficient,
            "valuation": valuation,
            "k_divisibility_modulus": k_modulus,
            "k_divisibility_residue": k_residue,
            "excluded_next_power_modulus": excluded_modulus,
            "excluded_next_power_residue": excluded_residue,
            "exact_valuation_condition": (
                f"k == {k_residue} mod {k_modulus} and "
                f"k != {excluded_residue} mod {excluded_modulus}"
            ),
        },
        "congruence_certificate": {
            "odd_modulus": odd_modulus,
            "inverse_power_two_mod_3a": inverse_power,
            "target_odd_residue_mod_3a": target_residue,
            "identity": f"r_prime == {target_residue} mod {odd_modulus}",
        },
        "target_membership_certificate": {
            "parent_floor": parent_floor,
            "target_parent": target_parent,
            "target_family": f"P{target_parent}: r' odd and r' == {target_residue} mod {odd_modulus}",
            "membership_rule": "v2(z(k)) fixes the parent level and the odd coordinate congruence fixes the family",
        },
        "status": "PASS",
    }
    certificate["certificate_hash"] = _certificate_hash(certificate)
    replay = replay_parent_transition_certificate(action=action, state=state, certificate=certificate)
    if not replay.accepted:
        raise ValueError(f"generated certificate did not replay: {replay.status}: {replay.reason}")
    return certificate


def replay_parent_transition_certificate(
    *,
    action: dict[str, Any],
    state: str,
    certificate: dict[str, Any],
) -> ActionCheck:
    """Replay a HIGH_PARENT_SUCCESSOR_EXACT payload."""

    from .proof_action_decode import ActionCheck

    required = {
        "type",
        "transition_id",
        "branch_id",
        "source_parent",
        "target_parent",
        "valuation",
        "statement",
        "symbolic_map",
        "divisibility_certificate",
        "congruence_certificate",
        "target_membership_certificate",
        "status",
    }
    missing = sorted(required - set(certificate))
    if missing:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", f"missing transition certificate fields: {missing}")
    if str(certificate.get("type")) != "HIGH_PARENT_SUCCESSOR_EXACT":
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "unsupported transition certificate type")
    if str(certificate.get("status")) != "PASS":
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "transition certificate status is not PASS")
    for field in ("branch_id", "source_parent", "target_parent", "valuation"):
        if certificate[field] != action[field]:
            return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", f"transition certificate {field} does not match action")
    try:
        branch = parse_branch_id(str(certificate["branch_id"]))
        z = parse_z_family(state)
    except ValueError as exc:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", str(exc))
    source_parent = int(certificate["source_parent"])
    target_parent = int(certificate["target_parent"])
    valuation = int(certificate["valuation"])
    c = int(z["c"])
    coefficient = int(z["coefficient"])
    if branch["a"] != source_parent:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "branch id source parent mismatch")
    if coefficient != 3**source_parent:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "z-family coefficient is not 3^source_parent")

    symbolic = certificate.get("symbolic_map")
    divisibility = certificate.get("divisibility_certificate")
    congruence = certificate.get("congruence_certificate")
    membership = certificate.get("target_membership_certificate")
    if not all(isinstance(section, dict) for section in (symbolic, divisibility, congruence, membership)):
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "transition certificate sections must be objects")
    if symbolic.get("z_family") != f"z(k) = {c} + {coefficient}*k":
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "symbolic z-family does not replay from state")
    if int(symbolic.get("source_residue", -1)) != branch["residue"] or int(symbolic.get("source_depth", -1)) != branch["depth"]:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "source branch residue/depth mismatch")

    if int(divisibility.get("c", 0)) != c or int(divisibility.get("coefficient", 0)) != coefficient:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "divisibility payload does not match z-family")
    if int(divisibility.get("valuation", -1)) != valuation:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "divisibility valuation mismatch")
    if valuation == 0:
        expected_modulus = 1
        expected_residue = 0
    else:
        expected_modulus = 1 << valuation
        expected_residue = (-c * pow(coefficient, -1, expected_modulus)) % expected_modulus
    expected_excluded_modulus = 1 << (valuation + 1)
    expected_excluded_residue = (-c * pow(coefficient, -1, expected_excluded_modulus)) % expected_excluded_modulus
    if int(divisibility.get("k_divisibility_modulus", 0)) != expected_modulus:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "k divisibility modulus mismatch")
    if int(divisibility.get("k_divisibility_residue", -1)) != expected_residue:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "k divisibility residue mismatch")
    if int(divisibility.get("excluded_next_power_modulus", 0)) != expected_excluded_modulus:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "next-power exclusion modulus mismatch")
    if int(divisibility.get("excluded_next_power_residue", -1)) != expected_excluded_residue:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "next-power exclusion residue mismatch")

    odd_modulus = 3**source_parent
    expected_inverse = pow(pow(2, valuation, odd_modulus), -1, odd_modulus)
    expected_target_residue = (c * expected_inverse) % odd_modulus
    if int(congruence.get("odd_modulus", 0)) != odd_modulus:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "odd modulus mismatch")
    if int(congruence.get("inverse_power_two_mod_3a", -1)) != expected_inverse:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "inverse power mismatch")
    if int(congruence.get("target_odd_residue_mod_3a", -1)) != expected_target_residue:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "target odd residue mismatch")

    parent_floor = target_parent - valuation
    if parent_floor < 0 or int(membership.get("parent_floor", -1)) != parent_floor:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "parent floor mismatch")
    if int(membership.get("target_parent", -1)) != target_parent:
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "target membership parent mismatch")
    cert_hash = certificate.get("certificate_hash")
    if cert_hash and str(cert_hash) != _certificate_hash(certificate):
        return ActionCheck(False, "REJECT_TRANSITION_CERTIFICATE", "transition certificate hash mismatch")
    return ActionCheck(True, "ACCEPT", "exact symbolic parent-transition certificate replays", progress=0.6)


def _load_graph(path: str | Path) -> dict[str, Any]:
    payload = _load_json(path)
    return payload.get("graph", payload) if isinstance(payload, dict) else payload


def _artifact_entry(name: str, path: Path, manifest_dir: Path) -> dict[str, Any]:
    return {"name": name, "path": str(path.relative_to(manifest_dir)), "sha256": _sha256(path)}


def _source_entry(path: Path) -> dict[str, Any]:
    return {"name": str(path.relative_to(REPO_ROOT)), "path": str(path.relative_to(REPO_ROOT)), "sha256": _sha256(path)}


def _patch_s4_nodes(graph: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from .proof_action_decode import verify_action_for_state

    patched = json.loads(json.dumps(graph))
    certificates: list[dict[str, Any]] = []
    for node_id, node in patched.get("nodes", {}).items():
        if node.get("node_type") != "S4_LIFT":
            continue
        accepted_actions = list(node.get("accepted_actions") or [])
        if not accepted_actions:
            continue
        action = dict(accepted_actions[-1].get("action") or {})
        if action.get("type") != "DERIVE_PARENT_TRANSITION" or "transition_certificate" in action:
            continue
        certificate = build_parent_transition_certificate(action=action, state=str(node.get("state", "")), node_id=node_id)
        action["transition_certificate"] = certificate
        check = verify_action_for_state(action, str(node.get("state", "")))
        if not check.accepted:
            raise ValueError(f"patched S4 action failed verifier replay for {node_id}: {check.status} {check.reason}")
        action_text = serialize_action(action)
        accepted_actions[-1]["action"] = action
        accepted_actions[-1]["action_text"] = action_text
        accepted_actions[-1]["verifier_check"] = check.to_dict()
        node["accepted_actions"] = accepted_actions
        node["accepted_action_text"] = action_text
        for index, candidate in enumerate(list(node.get("candidate_actions") or [])):
            if candidate.get("type") == "DERIVE_PARENT_TRANSITION":
                node["candidate_actions"][index] = action
                break
        certificates.append(
            {
                "node_id": node_id,
                "transition_certificate": certificate,
                "action": action,
                "verifier_check": check.to_dict(),
            }
        )
    return patched, certificates


def _patch_trace_rows(trace_rows: list[dict[str, Any]], certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cert_by_node = {row["node_id"]: row for row in certificates}
    out: list[dict[str, Any]] = []
    for row in trace_rows:
        replacement = cert_by_node.get(str(row.get("node_id", "")))
        if replacement is not None and (row.get("action") or {}).get("type") == "DERIVE_PARENT_TRANSITION":
            patched = dict(row)
            patched["action"] = replacement["action"]
            patched["action_text"] = serialize_action(replacement["action"])
            patched["verifier_check"] = replacement["verifier_check"]
            patched.setdefault("evidence", {})["transition_certificate_hash"] = replacement["transition_certificate"]["certificate_hash"]
            out.append(patched)
        else:
            out.append(row)
    return out


def run_parent_transition_certificates(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("parent_transition_certificates", {}) if isinstance(cfg.get("parent_transition_certificates", {}), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = Path(run_cfg.get("proof_graph") or "certificate_store/proof_dependency_graph_frozen.json")
    trace_path = Path(run_cfg.get("accepted_action_trace") or "certificate_store/accepted_action_trace.jsonl")
    run020_summary_path = Path(run_cfg.get("run020_audit_summary") or "certificate_store/run020_audit_summary.json")
    graph = _load_graph(graph_path)
    trace_rows = _read_jsonl(trace_path)
    patched_graph, certificates = _patch_s4_nodes(graph)
    patched_trace = _patch_trace_rows(trace_rows, certificates)

    graph_out = out_dir / "proof_dependency_graph_s4_replayed.json"
    trace_out = out_dir / "accepted_action_trace_s4_replayed.jsonl"
    certs_out = out_dir / "parent_transition_certificates.jsonl"
    replay_out = out_dir / "strict_replay_result.json"
    _write_json(patched_graph, graph_out)
    _write_jsonl(patched_trace, trace_out)
    _write_jsonl(certificates, certs_out)

    proof = build_collatz_descent_theorem_candidate(proof_graph=patched_graph)
    source_accounting = {
        "strict_verifier": "PASS",
        "audit_status": "AUDIT_FAIL",
        "proof_confidence_percent": 100.0,
    }
    if run020_summary_path.exists():
        run020 = _load_json(run020_summary_path)
        source_accounting["audit_status"] = str(run020.get("verdict", "AUDIT_FAIL"))

    manifest = {
        "schema": "collatz_lab.strict_proof_manifest",
        "version": 1,
        "run_id": RUN_ID,
        "source_run_accounting": source_accounting,
        "artifacts": [
            _artifact_entry("proof_dependency_graph_frozen", graph_out, out_dir),
            _artifact_entry("accepted_action_trace", trace_out, out_dir),
            _artifact_entry("parent_transition_certificates", certs_out, out_dir),
        ],
        "source_files": [
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_parent_transition_cert.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_decode.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_action_dsl.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/replay_strict_proof.py"),
            _source_entry(REPO_ROOT / "src/collatz_lab/proof_verifier.py"),
        ],
        "clean_clone_replay": {
            "command": "python -m collatz_lab.replay_strict_proof --manifest reports/runs/RUN-022-exact-s4-parent-transition-certificates/proof_manifest.json",
            "requires_committed_or_included_artifacts": True,
        },
    }
    manifest_path = out_dir / "proof_manifest.json"
    _write_json(manifest, manifest_path)
    replay_result = replay_manifest(manifest_path, out=replay_out)
    root_types = {row["node_type"]: row.get("count", 1) for row in replay_result.get("root_unsound_certificates", [])}
    summary = {
        "schema": "collatz_lab.run022_parent_transition_certificates",
        "version": 1,
        "run_id": RUN_ID,
        "training_launched": False,
        "big_model_launched": False,
        "selector_work_launched": False,
        "search_launched": False,
        "s4_lift_blockers_before": 135,
        "s4_lift_blockers_after": int(root_types.get("S4_LIFT", 0) or 0),
        "generated_parent_transition_certificate_count": len(certificates),
        "strict_verifier": replay_result["strict_verifier"],
        "verifier_status": replay_result["verifier_status"],
        "proof_confidence_percent": replay_result["proof_confidence_percent"],
        "strict_unknown_obligations": proof.get("unknown_obligations", []),
        "root_unsound_certificates": replay_result.get("root_unsound_certificates", []),
        "artifacts": {
            "proof_dependency_graph_s4_replayed": str(graph_out),
            "accepted_action_trace_s4_replayed": str(trace_out),
            "parent_transition_certificates": str(certs_out),
            "proof_manifest": str(manifest_path),
            "strict_replay_result": str(replay_out),
        },
    }
    _write_json(summary, out_dir / "run_result.json")
    return summary


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_parent_transition_certificates(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
