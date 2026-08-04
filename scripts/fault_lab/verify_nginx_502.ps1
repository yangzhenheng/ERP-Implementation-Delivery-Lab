param(
    [string]$BaseUrl = "http://localhost",
    [string]$DirectUrl = "http://localhost:8000",
    [ValidateSet("Fault", "Recovery")]
    [string]$Mode = "Fault"
)

$ErrorActionPreference = "Stop"

function Get-StatusCode([string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        return [int]$response.StatusCode
    } catch {
        if ($_.Exception.Response) {
            return [int]$_.Exception.Response.StatusCode
        }
        throw
    }
}

$nginxStatus = Get-StatusCode "$BaseUrl/health"
$directStatus = Get-StatusCode "$DirectUrl/health"

Write-Output "nginx_health_status=$nginxStatus"
Write-Output "fastapi_direct_status=$directStatus"

if ($Mode -eq "Fault") {
    if ($nginxStatus -ne 502 -or $directStatus -ne 200) {
        throw "Fault verification requires Nginx=502 and FastAPI=200; got Nginx=$nginxStatus FastAPI=$directStatus."
    }
} elseif ($nginxStatus -ne 200 -or $directStatus -ne 200) {
    throw "Recovery verification requires Nginx=200 and FastAPI=200; got Nginx=$nginxStatus FastAPI=$directStatus."
}

Write-Output "$Mode verification passed."
