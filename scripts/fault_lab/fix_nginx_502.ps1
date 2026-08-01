param(
    [string]$ConfigPath = "deploy/nginx/erp.conf",
    [string]$ComposeFile = "docker-compose.yml"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker command not found. Start/install Docker Desktop before running fault lab."
}

$backupPath = "$ConfigPath.v3_502_backup"
if (Test-Path $backupPath) {
    Copy-Item -LiteralPath $backupPath -Destination $ConfigPath -Force
    Remove-Item -LiteralPath $backupPath -Force
} else {
    $content = Get-Content -Raw -Encoding UTF8 $ConfigPath
    $content = $content -replace "proxy_pass http://app:8999;", "proxy_pass http://app:8000;"
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Resolve-Path $ConfigPath), $content, $utf8NoBom)
}

docker compose -f $ComposeFile restart nginx
Write-Output "Nginx config restored and nginx restarted."
