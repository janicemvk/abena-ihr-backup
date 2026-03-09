# Find the sc-network source file in Cargo's git cache
$checkoutsDir = Join-Path $env:USERPROFILE ".cargo\git\checkouts"
$sdkDirs = Get-ChildItem -Path $checkoutsDir -Directory -Filter "polkadot-sdk-*" -ErrorAction SilentlyContinue
$sdkPath = $null
foreach ($dir in $sdkDirs) {
    $revDirs = Get-ChildItem -Path $dir.FullName -Directory -ErrorAction SilentlyContinue
    if ($revDirs) {
        $sdkPath = $revDirs[0]  # Use first rev (e.g. 3c3d6fc)
        break
    }
}

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

# Consensus has index 6; variants after it get implicit 6,7,8... causing duplicate.
# Add explicit indices to RemoteCallRequest through RemoteReadChildRequest.
$replacements = @(
    @{ Pattern = '(\s+/// Remote method call request\.\r?\n)(\s+RemoteCallRequest)'; Replacement = "`$1    #[codec(index = 7)]`n`$2" }
    @{ Pattern = '(\s+/// Remote method call response\.\r?\n)(\s+RemoteCallResponse)'; Replacement = "`$1    #[codec(index = 8)]`n`$2" }
    @{ Pattern = '(\s+/// Remote storage read request\.\r?\n)(\s+RemoteReadRequest)'; Replacement = "`$1    #[codec(index = 9)]`n`$2" }
    @{ Pattern = '(\s+/// Remote storage read response\.\r?\n)(\s+RemoteReadResponse)'; Replacement = "`$1    #[codec(index = 10)]`n`$2" }
    @{ Pattern = '(\s+/// Remote header request\.\r?\n)(\s+RemoteHeaderRequest)'; Replacement = "`$1    #[codec(index = 11)]`n`$2" }
    @{ Pattern = '(\s+/// Remote header response\.\r?\n)(\s+RemoteHeaderResponse)'; Replacement = "`$1    #[codec(index = 12)]`n`$2" }
    @{ Pattern = '(\s+/// Remote changes request\.\r?\n)(\s+RemoteChangesRequest)'; Replacement = "`$1    #[codec(index = 13)]`n`$2" }
    @{ Pattern = '(\s+/// Remote changes response\.\r?\n)(\s+RemoteChangesResponse)'; Replacement = "`$1    #[codec(index = 14)]`n`$2" }
    @{ Pattern = '(\s+/// Remote child storage read request\.\r?\n)(\s+RemoteReadChildRequest)'; Replacement = "`$1    #[codec(index = 15)]`n`$2" }
)

$modified = $false
foreach ($r in $replacements) {
    if ($content -match $r.Pattern) {
        $content = $content -replace $r.Pattern, $r.Replacement
        $modified = $true
    }
}

if ($modified) {
    Set-Content -Path $messageFile -Value $content -NoNewline
    Write-Host "✓ Fixed enum conflict: Added explicit codec indices" -ForegroundColor Green
} else {
    Write-Host 'Patterns not found - file may already be patched.' -ForegroundColor Yellow
}
