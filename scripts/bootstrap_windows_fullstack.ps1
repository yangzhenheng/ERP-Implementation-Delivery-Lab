param(
    [int]$DockerWaitSeconds = 300
)

$ErrorActionPreference = "Stop"

function Write-Step($Status, $Message) {
    Write-Output "[$Status] $Message"
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Step "BLOCKED" "Administrator PowerShell is required."
    Write-Output "Run: powershell -ExecutionPolicy Bypass -File scripts/bootstrap_windows_fullstack.ps1"
    exit 2
}

Write-Step "PASS" "Administrator PowerShell confirmed"
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart | Out-Null
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart | Out-Null

$restartNeeded = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending" -ErrorAction SilentlyContinue
if ($restartNeeded) {
    Write-Step "BLOCKED" "RESTART_REQUIRED"
    exit 3
}

wsl --update
$wslList = wsl -l -q 2>$null
if ($LASTEXITCODE -ne 0 -or ($wslList -notmatch "Ubuntu")) {
    Write-Step "BLOCKED" "Ubuntu-24.04 is not installed. Installing may open an interactive first-run prompt."
    wsl --install -d Ubuntu-24.04
    Write-Output "After Ubuntu first-run finishes, rerun this script."
    exit 4
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Step "BLOCKED" "winget is not available; install App Installer from Microsoft Store."
    exit 5
}

if (-not (Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe")) {
    winget install -e --id Docker.DockerDesktop
}

$dockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerDesktop) {
    Start-Process -FilePath $dockerDesktop -WindowStyle Hidden
}

$deadline = (Get-Date).AddSeconds($DockerWaitSeconds)
while ((Get-Date) -lt $deadline) {
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        docker version *> $null
        if ($LASTEXITCODE -eq 0) {
            docker compose version
            docker info
            Write-Step "PASS" "Docker Engine and Compose are available"
            exit 0
        }
    }
    Start-Sleep -Seconds 5
}

Write-Step "BLOCKED" "Docker Engine did not become available within $DockerWaitSeconds seconds"
exit 6
