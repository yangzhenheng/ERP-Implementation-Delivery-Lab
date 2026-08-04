param(
    [Parameter(Mandatory = $true)][string]$BackupFile,
    [string]$ComposeFile = "docker-compose.yml",
    [string]$EnvFile = ".env"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker command not found. Start/install Docker Desktop before running container restore."
}

python scripts/mysql_backup_restore_lab.py `
    --compose-file $ComposeFile `
    --backup-file $BackupFile `
    --output-dir artifacts/v31
