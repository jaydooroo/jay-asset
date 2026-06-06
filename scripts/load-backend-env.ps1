param(
    [string]$Path = "backend\.env.aws.local"
)

if (-not (Test-Path $Path)) {
    Write-Error "Env file not found: $Path"
    Write-Host "Create it from the example: Copy-Item backend\.env.aws.example backend\.env.aws.local"
    exit 1
}

Get-Content $Path | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        return
    }

    $parts = $line -split "=", 2
    if ($parts.Count -ne 2) {
        Write-Warning "Skipping invalid env line: $line"
        return
    }

    $name = $parts[0].Trim()
    $value = $parts[1].Trim()

    if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
        $value = $value.Substring(1, $value.Length - 2)
    }

    Set-Item -Path "Env:$name" -Value $value
    Write-Host "Loaded $name"
}

# AWS mode should not use the local DynamoDB endpoint.
Remove-Item Env:\MARKET_DYNAMODB_ENDPOINT_URL -ErrorAction SilentlyContinue
Write-Host "Removed MARKET_DYNAMODB_ENDPOINT_URL for AWS mode, if it existed."
