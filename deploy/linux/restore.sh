#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: deploy/linux/restore.sh backups/file.sql"
  exit 2
fi

: "${DB_HOST:=127.0.0.1}"
: "${DB_PORT:=3306}"
: "${DB_NAME:=erp_demo}"
: "${DB_USER:=erp_user}"

mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p "$DB_NAME" < "$1"
echo "Restore finished from $1"
