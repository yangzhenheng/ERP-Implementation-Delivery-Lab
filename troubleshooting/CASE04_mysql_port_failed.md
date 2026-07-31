# CASE04 MySQL Port Connection Failed

Safety: local demo only.

## Symptom

Database client cannot connect to port 3306.

## Logs

Docker MySQL logs may show startup or initialization error.

## Commands

```bash
docker compose ps mysql
docker compose logs mysql
ss -lntp | grep 3306
mysqladmin ping -h 127.0.0.1 -P 3306 -u erp_user -p
```

## Root Cause

MySQL container not started, port conflict, or health check has not passed.

## Solution

Check port conflict and restart MySQL:

```bash
docker compose restart mysql
docker compose ps
```
