#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/deepseek-prover-v2-service}"
cd "$APP_DIR"
mkdir -p logs

if [[ -f server.pid ]] && kill -0 "$(cat server.pid)" 2>/dev/null; then
  echo "already running: pid $(cat server.pid)"
  exit 0
fi

nohup ./run_server.sh > logs/server.log 2>&1 &
echo "$!" > server.pid
echo "started: pid $(cat server.pid)"
echo "log: $APP_DIR/logs/server.log"
