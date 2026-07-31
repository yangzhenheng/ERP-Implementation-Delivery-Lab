$ErrorActionPreference = "Stop"

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Run this script from an Administrator PowerShell window." -ForegroundColor Yellow
    Write-Host "Docker Desktop installation requires UAC/admin rights and may require a restart."
    exit 1
}

winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements

Write-Host "Docker Desktop installer finished. Restart Windows if prompted, then reopen PowerShell and run:"
Write-Host "docker --version"
Write-Host "docker compose version"
Write-Host "powershell -ExecutionPolicy Bypass -File scripts/verify_full_stack.ps1"
