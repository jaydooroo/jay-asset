# Build and deploy the backend with AWS SAM.
#
#   .\scripts\deploy-backend.ps1
#   .\scripts\deploy-backend.ps1 -SchedulesState DISABLED   # pause schedules
#
# Reads TIINGO_API_KEY from backend\.env.aws.local (see backend\.env.aws.example).
param(
    [ValidateSet("ENABLED", "DISABLED")]
    [string]$SchedulesState = "ENABLED"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# Old hand-built packages inside backend/ would be copied into the Lambda by
# `sam build` and push it past the 250 MB limit.
$stale = @("backend\lambda_build", "backend\lambda_pkg") + (Get-ChildItem backend\deployment*.zip -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
$stale = $stale | Where-Object { Test-Path $_ }
if ($stale) {
    Write-Error ("Remove old build artifacts before deploying:`n  " + ($stale -join "`n  "))
    exit 1
}

& "$PSScriptRoot\load-backend-env.ps1"
if (-not $env:TIINGO_API_KEY) {
    Write-Error "TIINGO_API_KEY is missing from backend\.env.aws.local"
    exit 1
}

# Terminals opened before installing SAM CLI have a stale PATH.
if (-not (Get-Command sam -ErrorAction SilentlyContinue)) {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
if (-not (Get-Command sam -ErrorAction SilentlyContinue)) {
    Write-Error "SAM CLI not found. Install it: winget install Amazon.SAM-CLI"
    exit 1
}

sam build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

sam deploy --parameter-overrides `
    "TiingoApiKey=$env:TIINGO_API_KEY" `
    "SchedulesState=$SchedulesState"
exit $LASTEXITCODE
