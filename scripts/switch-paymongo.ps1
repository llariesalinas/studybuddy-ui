param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'prod')]
    [string]$Mode
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot 'backend'
$targetPath = Join-Path $backendDir '.env'

$sourceName = if ($Mode -eq 'dev') { '.env.dev' } else { '.env.production' }
$sourcePath = Join-Path $backendDir $sourceName

if (-not (Test-Path $sourcePath)) {
    throw "Missing $sourceName at $sourcePath"
}

if (-not (Test-Path $targetPath)) {
    throw "Missing active env file at $targetPath"
}

$modeValues = @{}
Get-Content -LiteralPath $sourcePath | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith('#') -or $line -notmatch '^[A-Za-z_][A-Za-z0-9_]*=') {
        return
    }

    $key, $value = $line -split '=', 2
    if ($key -in @(
        'PAYMONGO_SECRET_KEY',
        'PAYMONGO_WALLET_ID',
        'PAYMONGO_CASHOUT_CALLBACK_URL',
        'PAYMONGO_CASHOUT_CALLBACK_SECRET',
        'PAYMONGO_CASHOUT_MOCK',
        'FRONTEND_URL'
    )) {
        $modeValues[$key] = $value
    }
}

if ($modeValues.Count -eq 0) {
    throw "No PayMongo keys found in $sourceName"
}

$existingKeys = @{}
$existingLines = Get-Content -LiteralPath $targetPath
$updatedLines = foreach ($line in $existingLines) {
    $trimmed = $line.Trim()
    if ($trimmed -match '^[A-Za-z_][A-Za-z0-9_]*=') {
        $key, $value = $trimmed -split '=', 2
        if ($modeValues.ContainsKey($key)) {
            $existingKeys[$key] = $true
            "$key=$($modeValues[$key])"
            continue
        }

        $existingKeys[$key] = $true
    }

    $line
}

foreach ($key in $modeValues.Keys) {
    if (-not $existingKeys.ContainsKey($key)) {
        $updatedLines += "$key=$($modeValues[$key])"
    }
}

$updatedLines | Set-Content -LiteralPath $targetPath
Write-Host "Switched PayMongo env to $Mode by updating $targetPath"
