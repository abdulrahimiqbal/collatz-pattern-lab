import json
from pathlib import Path

import pytest

from collatz_lab.proof_action_run032 import run_global_ranking_invariant_discovery
from collatz_lab.replay_strict_proof import replay_manifest


ROOT = Path(__file__).resolve().parents[1]
RUN030 = ROOT / "reports/runs/RUN-030-top-level-theorem-certificates-after-s3-s6-hardening"


def _sha(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_with_artifact(tmp_path: Path, artifact_name: str, payload: str, suffix: str) -> Path:
    manifest = json.loads((ROOT / "proof_manifest.json").read_text(encoding="utf-8"))
    artifact_path = tmp_path / f"{artifact_name}{suffix}"
    artifact_path.write_text(payload, encoding="utf-8")
    for entry in manifest["artifacts"]:
        if entry["name"] == artifact_name:
            entry["path"] = str(artifact_path)
            entry["sha256"] = _sha(artifact_path)
            break
    else:  # pragma: no cover - fixture corruption guard
        raise AssertionError(f"artifact missing from fixture manifest: {artifact_name}")
    manifest_path = tmp_path / "proof_manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return manifest_path


def test_run030_current_replay_has_exact_ranking_blocker() -> None:
    result = json.loads((RUN030 / "run_result.json").read_text(encoding="utf-8"))
    replay = json.loads((RUN030 / "root_manifest_replay_result.json").read_text(encoding="utf-8"))
    sccs = [json.loads(line) for line in (RUN030 / "unresolved_sccs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    assert result["top_level_certificates_generated"] == 5
    assert result["top_level_replay_pass"] == 3
    assert result["s3_exact_certificate_count"] == 182
    assert result["s4_exact_certificate_count"] == 135
    assert result["s6_exact_certificate_count"] == 28
    assert result["ranking_blocker"] == "GLOBAL_RANKING_INVARIANT_REQUIRED"
    assert replay["hash_failure_count"] == 0
    assert replay["strict_verifier"] == "FAIL"
    assert {row["obligation_id"] for row in replay["unknown_obligations"]} == {
        "top_level:well_founded_ranking_certificate",
        "top_level:descent_implication_certificate",
    }
    assert len(sccs) == 1
    assert sccs[0]["nodes"] == [f"P{i}" for i in range(12, 25)]


@pytest.mark.parametrize(
    ("artifact_name", "root_type"),
    [
        ("s3_debt_certificates", "S3_CERTIFICATE"),
        ("parent_transition_certificates", "S4_CERTIFICATE"),
        ("s6_lemma_certificates", "S6_CERTIFICATE"),
    ],
)
def test_removed_lower_layer_certificate_fails_strict_replay(tmp_path: Path, artifact_name: str, root_type: str) -> None:
    source = next(entry for entry in json.loads((ROOT / "proof_manifest.json").read_text())["artifacts"] if entry["name"] == artifact_name)
    rows = (ROOT / source["path"]).read_text(encoding="utf-8").splitlines()
    manifest_path = _manifest_with_artifact(tmp_path, artifact_name, "\n".join(rows[1:]) + "\n", ".jsonl")

    replay = replay_manifest(manifest_path)

    assert replay["strict_verifier"] == "FAIL"
    assert root_type in {row["node_type"] for row in replay["root_unsound_certificates"]}


def test_removed_ranking_certificate_fails_strict_replay(tmp_path: Path) -> None:
    graph_entry = next(entry for entry in json.loads((ROOT / "proof_manifest.json").read_text())["artifacts"] if entry["name"] == "proof_dependency_graph_frozen")
    graph = json.loads((ROOT / graph_entry["path"]).read_text(encoding="utf-8"))
    graph["top_level_certificates"].pop("well_founded_ranking_certificate")
    manifest_path = _manifest_with_artifact(tmp_path, "proof_dependency_graph_frozen", json.dumps(graph, sort_keys=True), ".json")

    replay = replay_manifest(manifest_path)

    assert replay["strict_verifier"] == "FAIL"
    assert any(row["obligation_id"] == "top_level:well_founded_ranking_certificate" for row in replay["unknown_obligations"])


def test_run032_reports_global_ranking_invariant_required(tmp_path: Path) -> None:
    cfg = tmp_path / "run032.yaml"
    cfg.write_text(
        "\n".join(
            [
                "global_ranking_invariant_discovery_run032:",
                f"  out_dir: {tmp_path / 'out'}",
                f"  unresolved_sccs: {RUN030 / 'unresolved_sccs.jsonl'}",
            ]
        ),
        encoding="utf-8",
    )

    result = run_global_ranking_invariant_discovery(cfg)

    assert result["status"] == "GLOBAL_RANKING_INVARIANT_REQUIRED"
    assert result["accepted_candidate_count"] == 0
    assert result["unresolved_scc_count"] == 1
