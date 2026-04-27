#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${1:-/mnt/collatz/runs/20260424_222430_multitask_base24}"
RUN_ID="$(basename "${RUN_DIR}")"
CHECKPOINT="${RUN_DIR}/checkpoint.pt"
REPORT_ROOT="/mnt/collatz/reports"
LIMIT="${LIMIT:-20000}"
N_CLUSTERS="${N_CLUSTERS:-12}"

modal_run() {
  .venv/bin/python -m modal run "$@"
}

modal_run modal_app.py::probe_remote \
  --checkpoint-path "${CHECKPOINT}" \
  --data-path /mnt/collatz/data/multitask/base24_bits48_residue_holdout_100k.parquet \
  --out "${REPORT_ROOT}/${RUN_ID}_probes_residue_holdout_bits48.json" \
  --plot-dir "${REPORT_ROOT}/${RUN_ID}_probe_plots_residue_holdout_bits48" \
  --limit "${LIMIT}" \
  --n-clusters "${N_CLUSTERS}"

modal_run modal_app.py::probe_remote \
  --checkpoint-path "${CHECKPOINT}" \
  --data-path /mnt/collatz/data/multitask/base24_bits56_positive_hard_cases_eval_100k.parquet \
  --out "${REPORT_ROOT}/${RUN_ID}_probes_hard_positive_bits56.json" \
  --plot-dir "${REPORT_ROOT}/${RUN_ID}_probe_plots_hard_positive_bits56" \
  --limit "${LIMIT}" \
  --n-clusters "${N_CLUSTERS}"

modal_run modal_app.py::discover_remote \
  --data-path /mnt/collatz/data/multitask/base24_bits56_positive_hard_cases_eval_100k.parquet \
  --out "${REPORT_ROOT}/${RUN_ID}_candidates_hard_positive_dataset.jsonl" \
  --mode dataset \
  --max-k 180 \
  --min-support 20

modal_run modal_app.py::discover_remote \
  --data-path /mnt/collatz/data/multitask/base24_bits56_positive_hard_cases_eval_100k.parquet \
  --checkpoint-path "${CHECKPOINT}" \
  --out "${REPORT_ROOT}/${RUN_ID}_candidates_hard_positive_model_cluster.jsonl" \
  --cluster-out "${REPORT_ROOT}/${RUN_ID}_clusters_hard_positive_bits56.json" \
  --mode model_cluster \
  --max-k 180 \
  --min-support 20 \
  --limit "${LIMIT}" \
  --n-clusters "${N_CLUSTERS}"

modal_run modal_app.py::verify_remote \
  --rules-path "${REPORT_ROOT}/${RUN_ID}_candidates_hard_positive_dataset.jsonl" \
  --out "${REPORT_ROOT}/${RUN_ID}_verification_hard_positive_dataset.json" \
  --samples-per-rule 500 \
  --max-t 180 \
  --search-limit 200000

modal_run modal_app.py::verify_remote \
  --rules-path "${REPORT_ROOT}/${RUN_ID}_candidates_hard_positive_model_cluster.jsonl" \
  --out "${REPORT_ROOT}/${RUN_ID}_verification_hard_positive_model_cluster.json" \
  --samples-per-rule 500 \
  --max-t 180 \
  --search-limit 200000

modal_run modal_app.py::discover_remote \
  --data-path /mnt/collatz/data/multitask/base24_bits56_positive_hard_cases_eval_100k.parquet \
  --checkpoint-path "${CHECKPOINT}" \
  --out "${REPORT_ROOT}/${RUN_ID}_candidates_hard_positive_lifted.jsonl" \
  --cluster-out "${REPORT_ROOT}/${RUN_ID}_clusters_hard_positive_lifted.json" \
  --mode lifted \
  --max-k 180 \
  --limit "${LIMIT}" \
  --n-clusters "${N_CLUSTERS}" \
  --max-candidates 256

modal_run modal_app.py::verify_remote \
  --rules-path "${REPORT_ROOT}/${RUN_ID}_candidates_hard_positive_lifted.jsonl" \
  --out "${REPORT_ROOT}/${RUN_ID}_verification_hard_positive_lifted.json" \
  --samples-per-rule 200 \
  --max-t 180 \
  --search-limit 200000
