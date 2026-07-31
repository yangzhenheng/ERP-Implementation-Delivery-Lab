#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
source .venv/bin/activate
mkdir -p logs
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/uvicorn.log 2>&1 &
echo $! > logs/app.pid
echo "Started FastAPI PID $(cat logs/app.pid)"
