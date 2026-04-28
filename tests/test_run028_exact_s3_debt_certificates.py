import json
import subprocess
from pathlib import Path

from collatz_lab.proof_action_run028 import run_exact_s3_debt_certificates
from collatz_lab.replay_strict_proof import replay_manifest


def test_run028_generates_exact_s3_debt_certificates_and_replays_manifest(tmp_path: Path) -> None:
    cfg = tmp_path / "run028.yaml"
    cfg.write_text(
        "\n".join(
            [
                "s3_debt_certificates:",
                f"  out_dir: {tmp_path / 'out'}",
                "  proof_graph: certificate_store/run024_proof_dependency_graph_frozen.json",
                "  accepted_action_trace: certificate_store/run024_accepted_action_trace.jsonl",
                "  write_repo_replay_bundle: false",
            ]
        ),
        encoding="utf-8",
    )

    result = run_exact_s3_debt_certificates(cfg)
    replay = replay_manifest(tmp_path / "out" / "proof_manifest.json")

    assert result["s3_debt_certificates_generated"] == 182
    assert result["s3_debt_replay_pass"] == 182
    assert result["failed_s3_debt_certificate_count"] == 0
    assert result["hash_failure_count"] == 0
    assert replay["hash_failure_count"] == 0
    assert not any(row["node_type"] == "S3_DEBT" for row in replay["root_unsound_certificates"])

    cert_rows = [
        json.loads(line)
        for line in (tmp_path / "out" / "s3_debt_certificates.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(cert_rows) == 182
    first_cert = cert_rows[0]["s3_debt_certificate"]
    assert "exact_congruence_certificate" in first_cert
    assert "debt_measure_definition" in first_cert
    assert "local_descent_certificate" in first_cert


def test_lean_generated_run024_data_builds_without_sorry_or_axioms() -> None:
    build = subprocess.run(
        ["lake", "build", "Collatz.Run024Data"],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert build.returncode == 0, build.stdout

    scan = subprocess.run(
        ["rg", r"\baxiom\b|sorry|admit", "formal/lean", "scripts/generate_lean_run024_data.py"],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert scan.returncode == 1, scan.stdout
