#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/deepseek-prover-v2-service}"
cd "$APP_DIR"

if [[ ! -f server.pid ]]; then
  echo "not running: server.pid missing"
  exit 0
fi

pid="$(cat server.pid)"
if kill -0 "$pid" 2>/dev/null; then
  kill "$pid"
  echo "stopped: pid $pid"
else
  echo "not running: stale pid $pid"
fi
rm -f server.pid
