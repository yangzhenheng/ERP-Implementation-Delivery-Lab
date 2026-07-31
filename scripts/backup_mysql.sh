#!/usr/bin/env bash
set -euo pipefail

mkdir -p backups
: "${DB_HOST:=127.0.0.1}"
: "${DB_PORT:=3306}"
: "${DB_NAME:=erp_demo}"
: "${DB_USER:=erp_user}"

OUT="backups/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p --single-transaction "$DB_NAME" > "$OUT"
echo "$OUT"
