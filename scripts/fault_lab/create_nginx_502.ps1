param(
    [string]$ConfigPath = "deploy/nginx/erp.conf",
    [string]$ComposeFile = "docker-compose.yml"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    throw "Nginx config not found: $ConfigPath"
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker command not found. Start/install Docker Desktop before running fault lab."
}

$backupPath = "$ConfigPath.v3_502_backup"
Copy-Item -LiteralPath $ConfigPath -Destination $backupPath -Force

$content = Get-Content -Raw -Encoding UTF8 $ConfigPath
if ($content -notmatch "proxy_pass http://app:8000;") {
    throw "Expected proxy_pass http://app:8000; not found. Refusing to modify unexpected config."
}

$content = $content -replace "proxy_pass http://app:8000;", "proxy_pass http://app:8999;"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Resolve-Path $ConfigPath), $content, $utf8NoBom)

docker compose -f $ComposeFile restart nginx
Write-Output "Nginx 502 fault injected. Backup: $backupPath"
