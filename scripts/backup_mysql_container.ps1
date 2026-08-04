param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$EnvFile = ".env",
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker command not found. Start/install Docker Desktop before running container backup."
}

python scripts/mysql_backup_restore_lab.py `
    --compose-file $ComposeFile `
    --backup-only `
    --output-dir artifacts/v31
