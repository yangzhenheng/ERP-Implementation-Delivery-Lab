param(
    [Parameter(Mandatory = $true)][string]$BackupFile,
    [string]$ComposeFile = "docker-compose.yml",
    [string]$EnvFile = ".env"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

if (-not (Test-Path $EnvFile)) {
    throw "Missing .env file. Create it from .env.example with local demo passwords first."
}

Get-Content $EnvFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
    }
}

$dbName = if ($env:DB_NAME) { $env:DB_NAME } else { "erp_demo" }
$rootPassword = $env:MYSQL_ROOT_PASSWORD
if (-not $rootPassword) {
    throw "MYSQL_ROOT_PASSWORD is missing in .env"
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker command not found. Start/install Docker Desktop before running container restore."
}

docker compose -f $ComposeFile exec -T mysql mysql -uroot "-p$rootPassword" -e "DROP DATABASE IF EXISTS $dbName; CREATE DATABASE $dbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
Get-Content -Raw -Encoding UTF8 $BackupFile | docker compose -f $ComposeFile exec -T mysql mysql -uroot "-p$rootPassword" $dbName
Write-Output "restore completed for $dbName"
