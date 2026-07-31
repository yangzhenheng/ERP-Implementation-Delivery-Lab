#!/usr/bin/env bash
set -euo pipefail

echo "== OS =="
uname -a || true
cat /etc/os-release || true

echo "== CPU =="
nproc || true
top -bn1 | head -5 || true

echo "== Memory =="
free -h || true

echo "== Disk =="
df -h || true

echo "== Runtime =="
python3 --version || true
docker --version || true
docker compose version || true

echo "== Ports =="
ss -lntp | grep -E ':80|:8000|:3306|:6379' || true

echo "== Network =="
ping -c 2 127.0.0.1 || true
curl -I --max-time 3 http://127.0.0.1:8000/health || true

echo "== MySQL =="
mysql --version || true

echo "== Redis =="
redis-cli --version || true
