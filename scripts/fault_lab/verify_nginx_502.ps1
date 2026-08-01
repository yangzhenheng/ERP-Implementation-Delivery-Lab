param(
    [string]$BaseUrl = "http://localhost",
    [string]$DirectUrl = "http://localhost:8000"
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

if ($directStatus -ne 200) {
    throw "FastAPI direct health must remain 200 during Nginx 502 fault."
}

if ($nginxStatus -notin @(200, 502)) {
    throw "Unexpected Nginx health status: $nginxStatus"
}
