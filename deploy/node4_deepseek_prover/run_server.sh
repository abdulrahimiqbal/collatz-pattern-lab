#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/deepseek-prover-v2-service}"
cd "$APP_DIR"

source .venv/bin/activate

export HF_HOME="${HF_HOME:-$APP_DIR/hf_home}"
export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-Prover-V2-7B}"
export LOAD_IN_4BIT="${LOAD_IN_4BIT:-1}"
export GPU_MAX_MEMORY="${GPU_MAX_MEMORY:-11GiB}"
export CPU_MAX_MEMORY="${CPU_MAX_MEMORY:-80GiB}"
export MAX_TOTAL_TOKENS="${MAX_TOTAL_TOKENS:-8192}"
export DEFAULT_MAX_NEW_TOKENS="${DEFAULT_MAX_NEW_TOKENS:-1024}"
export MAX_NEW_TOKENS_LIMIT="${MAX_NEW_TOKENS_LIMIT:-4096}"
export PORT="${PORT:-8000}"

mkdir -p "$HF_HOME" logs

exec python -m uvicorn server:app --host 0.0.0.0 --port "$PORT"
