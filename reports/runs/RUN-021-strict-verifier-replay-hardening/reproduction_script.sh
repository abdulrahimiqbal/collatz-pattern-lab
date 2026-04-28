#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e ".[dev]"
python -m collatz_lab.replay_strict_proof --manifest proof_manifest.json --out strict_replay_result.json
