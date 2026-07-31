# Docker Full Stack Verification

This project includes Docker Compose services for FastAPI, MySQL 8, Redis and Nginx.

## Current Machine Status

On 2026-07-31, Docker Desktop installation was attempted with:

```powershell
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements --silent
```

Result: installer downloaded and verified, but installation required Administrator/UAC permission and failed with exit code `4294967291`.

## Install Docker Desktop

Open PowerShell as Administrator, then run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_docker_windows.ps1
```

Restart Windows if Docker asks for it.

## Verify Docker

```powershell
docker --version
docker compose version
```

## Run Full Stack Verification

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_full_stack.ps1
```

The script checks:

- Docker CLI
- `docker compose up -d --build`
- Nginx route through `http://localhost`
- FastAPI health and dashboard
- MySQL query
- Redis ping
- MySQL backup file creation

## Stop Services

```powershell
docker compose down
```
