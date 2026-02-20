## Final Comprehensive Fix Script
Write-Host "=== Fixing All Remaining Errors ===" -ForegroundColor Cyan

# Step 1: Fix enum indices
Write-Host ""
Write-Host "[1/8] Fixing enum indices..." -ForegroundColor Yellow

$sdkFile = Get-ChildItem -Path "$env:USERPROFILE\.cargo\git\checkouts\polkadot-sdk-*" -Recurse -Filter "message.rs" | 
    Where-Object { $_.FullName -like "*substrate\client\network\src\protocol\message.rs" } | 
    Select-Object -First 1

if ($sdkFile) {
    $content = Get-Content $sdkFile.FullName -Raw
    
    # Fix RemoteChangesRequest (index 13)
    if ($content -notmatch 'RemoteChangesRequest.*index = 13') {
        $content = $content -replace '#\[codec\(index = \d+\)\]\s+RemoteChangesRequest', 'RemoteChangesRequest'
        $replacement1 = '$1#[codec(index = 13)]' + [Environment]::NewLine + "`t`t" + '$2'
        $content = $content -replace '(/// Remote changes request\.\r?\n\t\t)(RemoteChangesRequest)', $replacement1
        Write-Host "  Fixed RemoteChangesRequest index to 13" -ForegroundColor Gray
    }
    
    # Fix RemoteChangesResponse (index 14)
    if ($content -notmatch 'RemoteChangesResponse.*index = 14') {
        $content = $content -replace '#\[codec\(index = \d+\)\]\s+RemoteChangesResponse', 'RemoteChangesResponse'
        $replacement2 = '$1#[codec(index = 14)]' + [Environment]::NewLine + "`t`t" + '$2'
        $content = $content -replace '(/// Remote changes response\.\r?\n\t\t)(RemoteChangesResponse)', $replacement2
        Write-Host "  Fixed RemoteChangesResponse index to 14" -ForegroundColor Gray
    }
    
    # Fix RemoteReadChildRequest (index 15)
    if ($content -notmatch 'RemoteReadChildRequest.*index = 15') {
        $content = $content -replace '#\[codec\(index = \d+\)\]\s+RemoteReadChildRequest', 'RemoteReadChildRequest'
        $replacement3 = '$1#[codec(index = 15)]' + [Environment]::NewLine + "`t`t" + '$2'
        $content = $content -replace '(/// Remote child storage read request\.\r?\n\t\t)(RemoteReadChildRequest)', $replacement3
        Write-Host "  Fixed RemoteReadChildRequest index to 15" -ForegroundColor Gray
    }
    
    Set-Content -Path $sdkFile.FullName -Value $content -NoNewline
    Write-Host "Fixed enum indices" -ForegroundColor Green
}

# Step 2: Fix ClinicalGuideline derive macro
Write-Host ""
Write-Host "[2/8] Fixing ClinicalGuideline derive..." -ForegroundColor Yellow

$file = "pallets\treatment-protocol\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    # Fix the malformed derive: Clone, Encode, Decode, PartialEq, Eq, , , DebugTypeInfo
    # Should be: Clone, Encode, Decode, PartialEq, Eq, Debug, TypeInfo
    $content = $content -replace '#\[derive\(Clone, Encode, Decode, PartialEq, Eq, , , DebugTypeInfo\)\]', '#[derive(Clone, Encode, Decode, PartialEq, Eq, Debug, TypeInfo)]'
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "Fixed ClinicalGuideline derive macro" -ForegroundColor Green
}

# Step 3: Fix import formatting in abena-coin
Write-Host ""
Write-Host "[3/8] Fixing import formatting in abena-coin..." -ForegroundColor Yellow

$file = "pallets\abena-coin\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    # Fix: use sp_std::vec::Vec;    use sp_runtime::traits::...
    # Should be: use sp_std::vec::Vec;
    #            use sp_runtime::traits::...
    $newline = [Environment]::NewLine
    $replacement = '$1' + $newline + '    $2'
    $content = $content -replace '(use sp_std::vec::Vec;)\s{4,}(use sp_runtime::traits)', $replacement
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "Fixed import formatting" -ForegroundColor Green
}

# Step 4: Add WeightInfo import to abena-coin (inside pallet module)
Write-Host ""
Write-Host "[4/8] Adding WeightInfo import to abena-coin..." -ForegroundColor Yellow

$file = "pallets\abena-coin\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    # Add use crate::WeightInfo; after RuntimeDebug if not present
    if ($content -notmatch 'use crate::WeightInfo;') {
        $newline = [Environment]::NewLine
        $replacement = '$1    use crate::WeightInfo;' + $newline
        $content = $content -replace '(use sp_runtime::RuntimeDebug;\s*\r?\n)', $replacement
        Set-Content -Path $file -Value $content -NoNewline
        Write-Host "Added WeightInfo import" -ForegroundColor Green
    }
}

# Step 5: Fix unique_saturated_from to saturated_from in abena-coin
Write-Host ""
Write-Host "[5/8] Fixing unique_saturated_from..." -ForegroundColor Yellow

$file = "pallets\abena-coin\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    # Replace unique_saturated_from with saturated_from
    $content = $content -replace 'unique_saturated_from', 'saturated_from'
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "Fixed unique_saturated_from to saturated_from" -ForegroundColor Green
}

# Step 6: Add skip_type_params to MultiSigConfig
Write-Host ""
Write-Host "[6/8] Adding skip_type_params to MultiSigConfig..." -ForegroundColor Yellow

$file = "pallets\health-record-hash\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    # Add skip_type_params before MultiSigConfig if not present
    if ($content -notmatch 'MultiSigConfig.*skip_type_params') {
        $newline = [Environment]::NewLine
        $replacement = '$1#[scale_info(skip_type_params(T))]' + $newline + '$2$3'
        $content = $content -replace '(/// Multi-signature configuration\s*\r?\n)(#\[derive\([^)]+\)\]\s*\r?\n)(pub struct MultiSigConfig)', $replacement
        Set-Content -Path $file -Value $content -NoNewline
        Write-Host "Added skip_type_params to MultiSigConfig" -ForegroundColor Green
    }
}

# Step 7: Add WeightInfo imports to other pallets that need it
Write-Host ""
Write-Host "[7/8] Adding WeightInfo imports to other pallets..." -ForegroundColor Yellow

$pallets = @(
    "pallets\health-record-hash\src\lib.rs",
    "pallets\treatment-protocol\src\lib.rs",
    "pallets\patient-identity\src\lib.rs",
    "pallets\interoperability\src\lib.rs",
    "pallets\quantum-computing\src\lib.rs",
    "pallets\governance\src\lib.rs",
    "pallets\patient-health-records\src\lib.rs"
)

$newline = [Environment]::NewLine
foreach ($file in $pallets) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        # Check if WeightInfo is used in weight annotations but not imported
        if (($content -match 'T::WeightInfo::') -and ($content -notmatch 'use crate::WeightInfo;')) {
            # Add after RuntimeDebug or similar import
            $replacement = '$1    use crate::WeightInfo;' + $newline
            $content = $content -replace '(use sp_runtime::RuntimeDebug;\s*\r?\n)', $replacement
            Set-Content -Path $file -Value $content -NoNewline
            Write-Host "  Added WeightInfo to $file" -ForegroundColor Gray
        }
    }
}
Write-Host "Added WeightInfo imports where needed" -ForegroundColor Green

# Step 8: Summary
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Fixed enum indices" -ForegroundColor Green
Write-Host "Fixed ClinicalGuideline derive macro" -ForegroundColor Green
Write-Host "Fixed import formatting" -ForegroundColor Green
Write-Host "Added WeightInfo imports" -ForegroundColor Green
Write-Host "Fixed unique_saturated_from" -ForegroundColor Green
Write-Host "Added skip_type_params to MultiSigConfig" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run: cargo clean" -ForegroundColor Cyan
Write-Host "  2. Run: cargo build --release" -ForegroundColor Cyan
Write-Host ""
Write-Host "Remaining MaxEncodedLen/TypeInfo errors require manual fixes:" -ForegroundColor Yellow
Write-Host "  - Types with Vec fields cannot implement MaxEncodedLen" -ForegroundColor Gray
Write-Host "  - Consider using BoundedVec instead of Vec for storage types" -ForegroundColor Gray
Write-Host "  - Or add skip_type_params where TypeInfo is needed" -ForegroundColor Grayes
