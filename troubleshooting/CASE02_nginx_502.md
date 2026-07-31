# CASE02 Nginx 502

Safety: local demo only.

## Symptom

Browser can open `http://localhost`, but Nginx returns `502 Bad Gateway`.

## Logs

Nginx error log shows upstream connection failed.

## Commands

```bash
docker compose ps
docker compose logs nginx
docker compose logs app
curl http://127.0.0.1:8000/health
ss -lntp | grep 8000
```

## Root Cause

FastAPI is not running, app health check failed, or Nginx upstream points to the wrong host/port.

## Solution

Fix upstream config and restart services:

```bash
docker compose restart app nginx
curl http://localhost/health
```
