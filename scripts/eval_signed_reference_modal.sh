#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${1:-/mnt/collatz/runs/latest}"
RUN_ID="$(basename "${RUN_DIR}")"
CHECKPOINT="${RUN_DIR}/checkpoint.pt"
REPORT_ROOT="/mnt/collatz/reports"
MODAL=(.venv/bin/python -m modal run modal_app.py::eval_remote)

run_eval() {
  local name="$1"
  local data_path="$2"
  "${MODAL[@]}" \
    --checkpoint-path "${CHECKPOINT}" \
    --data-path "${data_path}" \
    --out "${REPORT_ROOT}/${RUN_ID}_eval_${name}.json" \
    --failures-out "${REPORT_ROOT}/${RUN_ID}_failures_${name}.json" \
    --max-failures 10000
}

run_eval "id_bits48_signed_100k" \
  "/mnt/collatz/data/multitask/base24_bits48_id_eval_100k.parquet"

run_eval "ood_bits56_positive_100k" \
  "/mnt/collatz/data/multitask/base24_bits56_positive_ood_100k.parquet"

run_eval "ood_bits64_positive_100k" \
  "/mnt/collatz/data/multitask/base24_bits64_positive_ood_100k.parquet"

run_eval "ood_bits56_negative_100k" \
  "/mnt/collatz/data/multitask/base24_bits56_negative_ood_100k.parquet"

run_eval "ood_bits64_negative_100k" \
  "/mnt/collatz/data/multitask/base24_bits64_negative_ood_100k.parquet"

run_eval "hard_positive_bits56_100k" \
  "/mnt/collatz/data/multitask/base24_bits56_positive_hard_cases_eval_100k.parquet"

run_eval "residue_holdout_bits48_100k" \
  "/mnt/collatz/data/multitask/base24_bits48_residue_holdout_100k.parquet"
