param(
    [Parameter(Mandatory = $true)][string]$BackupFile,
    [string]$DbHost = $env:DB_HOST,
    [string]$DbPort = $env:DB_PORT,
    [string]$DbName = $env:DB_NAME,
    [string]$DbUser = $env:DB_USER
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    Write-Error "Backup file not found: $BackupFile"
}

if (-not $DbHost) { $DbHost = "127.0.0.1" }
if (-not $DbPort) { $DbPort = "3306" }
if (-not $DbName) { $DbName = "erp_demo" }
if (-not $DbUser) { $DbUser = "erp_user" }

if (-not (Get-Command mysql -ErrorAction SilentlyContinue)) {
    Write-Error "mysql not found. Install MySQL client tools or run inside the MySQL container."
}

Get-Content -Raw -Encoding UTF8 $BackupFile | mysql -h $DbHost -P $DbPort -u $DbUser -p $DbName
Write-Output "restore completed"
