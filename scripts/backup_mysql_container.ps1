param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$EnvFile = ".env",
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"

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
    throw "docker command not found. Start/install Docker Desktop before running container backup."
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $OutputDir "$dbName`_$timestamp.sql"

$dumpArgs = @(
    "compose", "-f", $ComposeFile, "exec", "-T", "mysql",
    "mysqldump",
    "-uroot",
    "-p$rootPassword",
    "--single-transaction",
    "--routines",
    "--triggers",
    "--default-character-set=utf8mb4",
    $dbName
)

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "docker"
$dumpArgs | ForEach-Object { [void]$psi.ArgumentList.Add($_) }
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$process = [System.Diagnostics.Process]::Start($psi)
$stdout = $process.StandardOutput.ReadToEnd()
$stderr = $process.StandardError.ReadToEnd()
$process.WaitForExit()

if ($process.ExitCode -ne 0) {
    throw "mysqldump failed: $stderr"
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Resolve-Path -LiteralPath $OutputDir).Path + [System.IO.Path]::DirectorySeparatorChar + [System.IO.Path]::GetFileName($backupFile), $stdout, $utf8NoBom)

$info = Get-Item $backupFile
if ($info.Length -le 0) {
    throw "Backup file is empty: $backupFile"
}

Write-Output "backup_file=$backupFile"
Write-Output "backup_size=$($info.Length)"
