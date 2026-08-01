param(
    [string]$DbHost = $env:DB_HOST,
    [string]$DbPort = $env:DB_PORT,
    [string]$DbName = $env:DB_NAME,
    [string]$DbUser = $env:DB_USER,
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"

if (-not $DbHost) { $DbHost = "127.0.0.1" }
if (-not $DbPort) { $DbPort = "3306" }
if (-not $DbName) { $DbName = "erp_demo" }
if (-not $DbUser) { $DbUser = "erp_user" }

if (-not (Get-Command mysqldump -ErrorAction SilentlyContinue)) {
    Write-Error "mysqldump not found. Install MySQL client tools or run inside the MySQL container."
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$out = Join-Path $OutputDir "$DbName`_$timestamp.sql"

mysqldump -h $DbHost -P $DbPort -u $DbUser -p --single-transaction $DbName | Out-File -FilePath $out -Encoding utf8
Write-Output $out
