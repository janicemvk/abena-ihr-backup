# Find the sc-network source file in Cargo's git cache
$sdkPath = Get-ChildItem -Path "$env:USERPROFILE\.cargo\git\checkouts\polkadot-sdk-*" -Recurse -Directory | 
    Where-Object { $_.FullName -like "*polkadot-stable2407*" } | 
    Select-Object -First 1

if (-not $sdkPath) {
    Write-Host "SDK not found. Run 'cargo build' first to download dependencies." -ForegroundColor Yellow
    exit 1
}

$messageFile = Join-Path $sdkPath.FullName "substrate\client\network\src\protocol\message.rs"

if (-not (Test-Path $messageFile)) {
    Write-Host "File not found: $messageFile" -ForegroundColor Yellow
    Write-Host "Please run 'cargo update' first to download the SDK." -ForegroundColor Yellow
    exit 1
}

Write-Host "Patching: $messageFile" -ForegroundColor Cyan

# Read the file
$content = Get-Content $messageFile -Raw

# Find RemoteCallResponse and change its index from 6 to 7
# Look for the pattern with index = 6 before RemoteCallResponse
if ($content -match '(?s)(\s+#\[codec\(index = 6\)\]\s+RemoteCallResponse)') {
    $content = $content -replace '(\s+#\[codec\(index = 6\)\]\s+RemoteCallResponse)', '        #[codec(index = 7)]
        RemoteCallResponse'
    Set-Content -Path $messageFile -Value $content -NoNewline
    Write-Host "✓ Fixed enum conflict: Changed RemoteCallResponse index from 6 to 7" -ForegroundColor Green
} else {
    Write-Host "Pattern not found. Searching for RemoteCallResponse..." -ForegroundColor Yellow
    if ($content -match 'RemoteCallResponse') {
        Write-Host "Found RemoteCallResponse. Checking current index..." -ForegroundColor Yellow
        # Try alternative pattern
        if ($content -match '(?s)(RemoteCallResponse.*?index = )(\d+)') {
            $currentIndex = $matches[2]
            Write-Host "Current index: $currentIndex" -ForegroundColor Yellow
        }
        Write-Host "Manual edit may be needed." -ForegroundColor Yellow
    } else {
        Write-Host "RemoteCallResponse not found in file." -ForegroundColor Red
    }
}
