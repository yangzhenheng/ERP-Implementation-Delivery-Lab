param(
    [int]$DockerWaitSeconds = 300
)

$ErrorActionPreference = "Stop"

function Write-Step($Status, $Message) {
    Write-Output "[$Status] $Message"
}

function Resolve-NativeCommand($Name, [string[]]$FallbackPaths) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    foreach ($path in $FallbackPaths) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }
    return $null
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Step "BLOCKED" "Administrator PowerShell is required."
    Write-Output "Run: powershell -ExecutionPolicy Bypass -File scripts/bootstrap_windows_fullstack.ps1"
    exit 2
}

Write-Step "PASS" "Administrator PowerShell confirmed"
$wslFeature = Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
$vmpFeature = Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart

$restartNeeded = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending" -ErrorAction SilentlyContinue
if ($restartNeeded -or $wslFeature.RestartNeeded -or $vmpFeature.RestartNeeded) {
    Write-Step "BLOCKED" "RESTART_REQUIRED"
    Write-Output "Restart Windows, then rerun: powershell -ExecutionPolicy Bypass -File scripts/bootstrap_windows_fullstack.ps1"
    exit 3
}

$wslExe = Resolve-NativeCommand "wsl" @(
    "$env:WINDIR\Sysnative\wsl.exe",
    "$env:WINDIR\System32\wsl.exe"
)
if (-not $wslExe) {
    Write-Step "BLOCKED" "wsl.exe is not available. Restart Windows after enabling WSL features, then rerun this script."
    exit 7
}

& $wslExe --update
$wslList = & $wslExe -l -q 2>$null
if ($LASTEXITCODE -ne 0 -or ($wslList -notmatch "Ubuntu")) {
    Write-Step "BLOCKED" "Ubuntu-24.04 is not installed. Installing may open an interactive first-run prompt."
    & $wslExe --install -d Ubuntu-24.04
    Write-Output "After Ubuntu first-run finishes, rerun this script."
    exit 4
}

$wingetExe = Resolve-NativeCommand "winget" @(
    "$env:LOCALAPPDATA\Microsoft\WindowsApps\winget.exe"
)
if (-not $wingetExe) {
    Write-Step "BLOCKED" "winget is not available; install App Installer from Microsoft Store."
    exit 5
}

if (-not (Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe")) {
    & $wingetExe install -e --id Docker.DockerDesktop
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
