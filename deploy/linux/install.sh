#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from app.db import init_db; init_db(); print('database initialized')"
echo "Install finished. Start with deploy/linux/start.sh or docker compose up -d."
