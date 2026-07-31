#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
if [ -f logs/app.pid ]; then
  kill "$(cat logs/app.pid)" || true
  rm -f logs/app.pid
  echo "Stopped FastAPI"
else
  pkill -f "uvicorn app.main:app" || true
  echo "No pid file found; attempted process cleanup"
fi
