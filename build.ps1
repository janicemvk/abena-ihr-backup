# ABENA Blockchain Build Script
# Runs Windows mermaid fix first, then builds the project

$ErrorActionPreference = "Stop"

Write-Host "Fetching dependencies (ensures polkadot-sdk checkout exists)..." -ForegroundColor Cyan
cargo fetch

Write-Host "Running Windows mermaid path fix..." -ForegroundColor Cyan
$null = cargo build -p abena-build-fix 2>&1
# Fix package runs build script; continue even if build had warnings

Write-Host "Fixing enum index conflict in sc-network..." -ForegroundColor Cyan
& "$PSScriptRoot\fix-enum-conflict.ps1"

Write-Host "Building release..." -ForegroundColor Cyan
cargo build --release
exit $LASTEXITCODE
