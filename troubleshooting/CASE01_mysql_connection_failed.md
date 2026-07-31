# CASE01 MySQL Connection Failed

Safety: local demo only, recoverable by restoring `.env`.

## Symptom

`/health` returns database connection error when `APP_ENV=demo`.

## Logs

Application log shows access denied, unknown host or connection refused.

## Commands

```bash
cat .env
docker compose ps
docker compose logs mysql
mysql -h 127.0.0.1 -P 3306 -u erp_user -p -e "SELECT 1"
```

## Root Cause

Wrong DB host, port, username, password or database name.

## Solution

Fix `.env`, restart app, then verify:

```bash
docker compose restart app
curl http://localhost/health
```
