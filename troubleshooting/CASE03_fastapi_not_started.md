# CASE03 FastAPI Not Started

Safety: local demo only.

## Symptom

`curl http://127.0.0.1:8000/health` cannot connect.

## Logs

`logs/uvicorn.log` may show missing dependency or database initialization failure.

## Commands

```bash
ps aux | grep uvicorn
tail -n 100 logs/uvicorn.log
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Root Cause

Service was not started, dependency missing, port occupied or startup failed.

## Solution

Install dependencies, free the port, restart:

```bash
bash deploy/linux/restart.sh
curl http://127.0.0.1:8000/health
```
