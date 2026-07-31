param(
    [string]$BaseUrl = "http://localhost",
    [string]$DbName = "erp_demo",
    [string]$DbUser = "erp_user",
    [string]$DbPassword = "erp_password_change_me"
)

$ErrorActionPreference = "Stop"

function Pass($Name) { Write-Host "[PASS] $Name" -ForegroundColor Green }
function Fail($Name, $Reason) { Write-Host "[FAIL] $Name - $Reason" -ForegroundColor Red; exit 1 }

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Fail "Docker CLI" "docker command not found. Install Docker Desktop and restart the terminal."
}

docker --version
docker compose version
Pass "Docker CLI"

docker compose up -d --build
Pass "docker compose up"

$deadline = (Get-Date).AddMinutes(5)
do {
    Start-Sleep -Seconds 5
    $ps = docker compose ps
    Write-Host $ps
    $healthOk = $true
    foreach ($svc in @("mysql", "redis", "app", "nginx")) {
        if ($ps -notmatch $svc) { $healthOk = $false }
    }
} until ($healthOk -or (Get-Date) -gt $deadline)

python scripts/verify_deployment.py --base-url $BaseUrl
if ($LASTEXITCODE -ne 0) { Fail "HTTP verification" "API or Nginx check failed" }
Pass "HTTP verification"

docker compose exec -T mysql mysql -u$DbUser -p$DbPassword $DbName -e "SELECT COUNT(*) AS customers FROM customers;"
if ($LASTEXITCODE -ne 0) { Fail "MySQL query" "customer count query failed" }
Pass "MySQL query"

docker compose exec -T redis redis-cli ping
if ($LASTEXITCODE -ne 0) { Fail "Redis ping" "redis-cli ping failed" }
Pass "Redis ping"

New-Item -ItemType Directory -Force -Path backups | Out-Null
$backup = "backups/full_stack_verify.sql"
docker compose exec -T mysql mysqldump -u$DbUser -p$DbPassword --single-transaction $DbName | Out-File -Encoding utf8 $backup
if (-not (Test-Path $backup) -or ((Get-Item $backup).Length -le 0)) { Fail "MySQL backup" "backup file was not created" }
Pass "MySQL backup"

docker compose exec -T mysql mysql -u$DbUser -p$DbPassword $DbName -e "SELECT 1;"
if ($LASTEXITCODE -ne 0) { Fail "MySQL restore readiness" "mysql client check failed" }
Pass "MySQL restore readiness"

Write-Host "Full stack verification completed."
