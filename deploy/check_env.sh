#!/usr/bin/env bash
set -euo pipefail

echo "== Manufacturing ERP Implementation Lab Environment Check =="
echo "[OS]"; uname -a || true
echo "[Release]"; cat /etc/os-release || true
echo "[CPU]"; nproc || true
echo "[Memory]"; free -h || true
echo "[Disk]"; df -h || true
echo "[Python]"; python3 --version || true
echo "[Docker]"; docker --version || true
echo "[Docker Compose]"; docker compose version || true
echo "[Ports]"; ss -lntp | grep -E ':80|:8000|:3306|:6379' || true
echo "[Network]"; ping -c 2 127.0.0.1 || true
echo "[Health]"; curl -fsS http://127.0.0.1:8000/health || true
