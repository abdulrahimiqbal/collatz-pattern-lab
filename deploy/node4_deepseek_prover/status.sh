#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/deepseek-prover-v2-service}"
PORT="${PORT:-8000}"
cd "$APP_DIR"

if [[ -f server.pid ]] && kill -0 "$(cat server.pid)" 2>/dev/null; then
  echo "process: running pid $(cat server.pid)"
else
  echo "process: not running"
fi

curl -fsS "http://127.0.0.1:${PORT}/health" || true
echo
