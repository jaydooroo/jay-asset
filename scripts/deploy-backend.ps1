# Build and deploy the backend with AWS SAM.
#
#   .\scripts\deploy-backend.ps1
#   .\scripts\deploy-backend.ps1 -SchedulesState DISABLED   # pause schedules
#   .\scripts\deploy-backend.ps1 -BuildOnly                 # test and build, no deploy
#
# Reads TIINGO_API_KEY and optionally ALERT_EMAIL from backend\.env.aws.local
# (see backend\.env.aws.example).
param(
    [ValidateSet("ENABLED", "DISABLED")]
    [string]$SchedulesState = "ENABLED",
    [switch]$BuildOnly
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# Runs before the env file is loaded, so tests cannot reach real AWS or Tiingo.
$python = "backend\.venv\Scripts\python.exe"
if (Test-Path $python) { $python = (Resolve-Path $python).Path } else { $python = "python" }
Push-Location backend
& $python -m pytest
$testExit = $LASTEXITCODE
Pop-Location
if ($testExit -ne 0) {
    Write-Error "Backend tests failed; not deploying."
    exit 1
}

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

# `sam build` copies everything in backend/ into the package, including the
# local secrets file. The Lambda gets its settings from template.yaml instead.
$package = ".aws-sam\build\ApiFunction"
foreach ($name in @(".env*", "tests", "research", "scripts", ".pytest_cache", "pytest.ini", "requirements-dev.txt", "README.md", "NEW_STRATEGY_CHECKLIST.md")) {
    Get-ChildItem -Path $package -Filter $name -Force | Remove-Item -Recurse -Force
}
if (Get-ChildItem -Path $package -Filter ".env*" -Force) {
    Write-Error "Env files are still in the Lambda package; not deploying."
    exit 1
}

if ($BuildOnly) { exit 0 }

$overrides = @("TiingoApiKey=$env:TIINGO_API_KEY", "SchedulesState=$SchedulesState")
if ($env:ALERT_EMAIL) { $overrides += "AlertEmail=$env:ALERT_EMAIL" }
sam deploy --parameter-overrides $overrides
exit $LASTEXITCODE
