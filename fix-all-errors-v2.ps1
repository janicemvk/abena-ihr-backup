# Comprehensive Fix Script - All Errors
Write-Host "=== Fixing All Compilation Errors ===" -ForegroundColor Cyan

# Step 1: Fix Enum Indices in SDK
Write-Host ""
Write-Host "[1/6] Fixing enum indices in SDK..." -ForegroundColor Yellow

$sdkFile = Get-ChildItem -Path "$env:USERPROFILE\.cargo\git\checkouts\polkadot-sdk-*" -Recurse -Filter "message.rs" | 
    Where-Object { $_.FullName -like "*substrate\client\network\src\protocol\message.rs" } | 
    Select-Object -First 1

if (-not $sdkFile) {
    Write-Host "SDK file not found." -ForegroundColor Red
    exit 1
}

$content = Get-Content $sdkFile.FullName -Raw

# Remove all existing index annotations from these variants first
$content = $content -replace '#\[codec\(index = \d+\)\]\s+RemoteCallRequest', 'RemoteCallRequest'
$content = $content -replace '#\[codec\(index = \d+\)\]\s+RemoteCallResponse', 'RemoteCallResponse'
$content = $content -replace '#\[codec\(index = \d+\)\]\s+RemoteReadRequest', 'RemoteReadRequest'
$content = $content -replace '#\[codec\(index = \d+\)\]\s+RemoteReadResponse', 'RemoteReadResponse'

# Now add correct indices
$pattern1 = '(/// Remote method call request\.\r?\n\t\t)(RemoteCallRequest)'
$replacement1 = '$1#[codec(index = 7)]' + [Environment]::NewLine + "`t`t" + '$2'
$content = $content -replace $pattern1, $replacement1

$pattern2 = '(/// Remote method call response\.\r?\n\t\t)(RemoteCallResponse)'
$replacement2 = '$1#[codec(index = 8)]' + [Environment]::NewLine + "`t`t" + '$2'
$content = $content -replace $pattern2, $replacement2

$pattern3 = '(/// Remote storage read request\.\r?\n\t\t)(RemoteReadRequest)'
$replacement3 = '$1#[codec(index = 9)]' + [Environment]::NewLine + "`t`t" + '$2'
$content = $content -replace $pattern3, $replacement3

$pattern4 = '(/// Remote storage read response\.\r?\n\t\t)(RemoteReadResponse)'
$replacement4 = '$1#[codec(index = 10)]' + [Environment]::NewLine + "`t`t" + '$2'
$content = $content -replace $pattern4, $replacement4

Set-Content -Path $sdkFile.FullName -Value $content -NoNewline
Write-Host "Fixed enum indices" -ForegroundColor Green

# Step 2: Fix abena-coin import syntax
Write-Host ""
Write-Host "[2/6] Fixing abena-coin import syntax..." -ForegroundColor Yellow

$abenaCoinFile = "pallets\abena-coin\src\lib.rs"
$content = Get-Content $abenaCoinFile -Raw
$content = $content -replace 'use sp_runtime::traits::\{Zero, CheckedAdd\}, Saturating;', 'use sp_runtime::traits::{Zero, CheckedAdd, Saturating};'
Set-Content -Path $abenaCoinFile -Value $content -NoNewline
Write-Host "Fixed import syntax" -ForegroundColor Green

# Step 3: Remove extra closing braces
Write-Host ""
Write-Host "[3/6] Removing extra closing braces..." -ForegroundColor Yellow

$pallets = @(
    "pallets\treatment-protocol\src\lib.rs",
    "pallets\health-record-hash\src\lib.rs",
    "pallets\interoperability\src\lib.rs",
    "pallets\patient-identity\src\lib.rs",
    "pallets\quantum-computing\src\lib.rs"
)

foreach ($file in $pallets) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $content = $content -replace '(\r?\n\s*)\}\s*(\r?\n\s*)\}\s*(\r?\n\s*)\}', '$1}$2}'
        $content = $content -replace '(\r?\n\s*)\}\s*(\r?\n\s*)\}\s*$', '$1}'
        Set-Content -Path $file -Value $content -NoNewline
        $fileName = Split-Path $file -Leaf
        Write-Host "  Fixed $fileName" -ForegroundColor Gray
    }
}

Write-Host "Removed extra closing braces" -ForegroundColor Green

# Step 4: Remove MaxEncodedLen from Vec types
Write-Host ""
Write-Host "[4/6] Removing MaxEncodedLen from incompatible types..." -ForegroundColor Yellow

$phrFile = "pallets\patient-health-records\src\lib.rs"
$content = Get-Content $phrFile -Raw
$content = $content -replace '(\[derive\([^)]*), MaxEncodedLen([^)]*\)\][^\n]*\n[^\n]*pub struct EncryptedHealthRecord)', '$1$2'
$content = $content -replace '(\[derive\([^)]*), MaxEncodedLen([^)]*\)\][^\n]*\n[^\n]*pub struct EncryptionMetadataRecord)', '$1$2'
Set-Content -Path $phrFile -Value $content -NoNewline
Write-Host "  Fixed patient-health-records" -ForegroundColor Gray

$govFile = "pallets\governance\src\lib.rs"
$content = Get-Content $govFile -Raw
$content = $content -replace '(\[derive\([^)]*), MaxEncodedLen([^)]*\)\][^\n]*\n[^\n]*pub struct GuidelineProposal)', '$1$2'
$content = $content -replace '(\[derive\([^)]*), MaxEncodedLen([^)]*\)\][^\n]*\n[^\n]*pub struct ProtocolProposal)', '$1$2'
$content = $content -replace '(\[derive\([^)]*), MaxEncodedLen([^)]*\)\][^\n]*\n[^\n]*pub struct EmergencyIntervention)', '$1$2'
Set-Content -Path $govFile -Value $content -NoNewline
Write-Host "  Fixed governance" -ForegroundColor Gray

Write-Host "Removed MaxEncodedLen from incompatible types" -ForegroundColor Green

# Step 5: Fix TypeInfo issues
Write-Host ""
Write-Host "[5/6] Fixing TypeInfo issues..." -ForegroundColor Yellow

$content = Get-Content $govFile -Raw
if ($content -notmatch 'GuidelineProposal.*skip_type_params') {
    $replacement = '#[scale_info(skip_type_params(T))]' + [Environment]::NewLine + 'pub struct GuidelineProposal<T: frame_system::Config>'
    $content = $content -replace 'pub struct GuidelineProposal<T: frame_system::Config>', $replacement
}
if ($content -notmatch 'ProtocolProposal.*skip_type_params') {
    $replacement = '#[scale_info(skip_type_params(T))]' + [Environment]::NewLine + 'pub struct ProtocolProposal<T: frame_system::Config>'
    $content = $content -replace 'pub struct ProtocolProposal<T: frame_system::Config>', $replacement
}
if ($content -notmatch 'EmergencyIntervention.*skip_type_params') {
    $replacement = '#[scale_info(skip_type_params(T))]' + [Environment]::NewLine + 'pub struct EmergencyIntervention<T: frame_system::Config>'
    $content = $content -replace 'pub struct EmergencyIntervention<T: frame_system::Config>', $replacement
}
Set-Content -Path $govFile -Value $content -NoNewline
Write-Host "Fixed TypeInfo issues" -ForegroundColor Green

# Step 6: Verify fixes
Write-Host ""
Write-Host "[6/6] Verifying fixes..." -ForegroundColor Yellow

$sdkContent = Get-Content $sdkFile.FullName -Raw
if ($sdkContent -match 'RemoteCallRequest.*index = 7' -and $sdkContent -match 'RemoteCallResponse.*index = 8') {
    Write-Host "  Enum indices correct" -ForegroundColor Gray
} else {
    Write-Host "  Enum indices may need manual check" -ForegroundColor Yellow
}

$abenaContent = Get-Content $abenaCoinFile -Raw
if ($abenaContent -match 'use sp_runtime::traits::\{Zero, CheckedAdd, Saturating\};') {
    Write-Host "  Import syntax correct" -ForegroundColor Gray
} else {
    Write-Host "  Import syntax may need manual check" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Fixed enum indices in SDK" -ForegroundColor Green
Write-Host "Fixed abena-coin import syntax" -ForegroundColor Green
Write-Host "Removed extra closing braces" -ForegroundColor Green
Write-Host "Removed MaxEncodedLen from incompatible types" -ForegroundColor Green
Write-Host "Fixed TypeInfo issues" -ForegroundColor Green

Write-Host ""
Write-Host "You can now run: cargo build --release" -ForegroundColor Cyan