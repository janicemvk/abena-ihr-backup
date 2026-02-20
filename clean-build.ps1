# Clean Build Script for ABENA Blockchain
Write-Host "=== ABENA Blockchain Clean Build ===" -ForegroundColor Cyan

# Step 1: Kill any running cargo processes
Write-Host "`n[1/5] Stopping background processes..." -ForegroundColor Yellow
Get-Process cargo -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process rustc -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Step 2: Clean build artifacts
Write-Host "[2/5] Cleaning build artifacts..." -ForegroundColor Yellow
if (Test-Path "Cargo.lock") {
    Remove-Item "Cargo.lock" -Force
}
& "$env:USERPROFILE\.cargo\bin\cargo.exe" clean
Write-Host "✓ Cleaned" -ForegroundColor Green

# Step 3: Update dependencies (download SDK)
Write-Host "[3/5] Updating dependencies (this may take a few minutes)..." -ForegroundColor Yellow
& "$env:USERPROFILE\.cargo\bin\cargo.exe" update 2>&1 | Out-Null
Write-Host "✓ Dependencies updated" -ForegroundColor Green

# Step 4: Patch enum conflict
Write-Host "[4/5] Patching enum conflict in SDK..." -ForegroundColor Yellow
& ".\fix-enum-conflict.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Warning: Could not auto-patch. You may need to patch manually." -ForegroundColor Yellow
}

# Step 5: Build
Write-Host "[5/5] Building project (this will take 15-30 minutes)..." -ForegroundColor Yellow
Write-Host "Starting build at $(Get-Date)" -ForegroundColor Gray

$buildOutput = & "$env:USERPROFILE\.cargo\bin\cargo.exe" build --release 2>&1

# Check if build succeeded
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓✓✓ BUILD SUCCESSFUL ✓✓✓" -ForegroundColor Green
    Write-Host "Binary location: target\release\abena-node.exe" -ForegroundColor Cyan
} else {
    Write-Host "`n✗ BUILD FAILED" -ForegroundColor Red
    Write-Host "`nLast 50 lines of output:" -ForegroundColor Yellow
    $buildOutput | Select-Object -Last 50
    Write-Host "`nFull error log saved to: build-error.log" -ForegroundColor Yellow
    $buildOutput | Out-File -FilePath "build-error.log" -Encoding UTF8
}

Write-Host "`nBuild completed at $(Get-Date)" -ForegroundColor Gray
