# ABENA Docker Desktop Starter + Demo Script
# Starts Docker Desktop and then runs the demo startup script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Docker Desktop..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker Desktop is already running
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProcess) {
    Write-Host "[OK] Docker Desktop is already running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting ABENA Demo..." -ForegroundColor Yellow
    & ".\START_ABENA_DEMO.ps1"
    exit 0
}

# Try to start Docker Desktop
Write-Host "[1/3] Attempting to start Docker Desktop..." -ForegroundColor Yellow

# Common Docker Desktop installation paths
$dockerPaths = @(
    "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe",
    "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe",
    "$env:LOCALAPPDATA\Docker\Docker Desktop.exe"
)

$dockerFound = $false
foreach ($path in $dockerPaths) {
    if (Test-Path $path) {
        Write-Host "  Found Docker Desktop at: $path" -ForegroundColor Green
        Start-Process -FilePath $path
        $dockerFound = $true
        break
    }
}

if (-not $dockerFound) {
    Write-Host "[WARNING] Could not find Docker Desktop installation." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Docker Desktop manually:" -ForegroundColor Yellow
    Write-Host "  1. Open Docker Desktop from Start Menu" -ForegroundColor White
    Write-Host "  2. Wait 30-60 seconds for it to fully start" -ForegroundColor White
    Write-Host "  3. Run: .\START_ABENA_DEMO.ps1" -ForegroundColor White
    exit 1
}

Write-Host "[2/3] Waiting for Docker Desktop to start..." -ForegroundColor Yellow
Write-Host "  This may take 30-60 seconds..." -ForegroundColor White

# Wait for Docker Desktop process to appear
$maxWait = 60
$waited = 0
while ($waited -lt $maxWait) {
    $dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
    if ($dockerProcess) {
        Write-Host "  [OK] Docker Desktop process started" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
    $waited += 2
    Write-Host "  Waiting... ($waited seconds)" -ForegroundColor Gray
}

if (-not $dockerProcess) {
    Write-Host "[WARNING] Docker Desktop process did not start within $maxWait seconds" -ForegroundColor Yellow
    Write-Host "  Please check Docker Desktop manually and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host "[3/3] Waiting for Docker daemon to be ready..." -ForegroundColor Yellow

# Wait for Docker daemon to be ready
$maxWait = 90
$waited = 0
while ($waited -lt $maxWait) {
    try {
        docker ps 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Docker daemon is ready!" -ForegroundColor Green
            break
        }
    } catch {
        # Continue waiting
    }
    Start-Sleep -Seconds 3
    $waited += 3
    if ($waited % 15 -eq 0) {
        Write-Host "  Still waiting... ($waited seconds)" -ForegroundColor Gray
    }
}

try {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] Docker daemon not ready after $maxWait seconds" -ForegroundColor Yellow
        Write-Host "  You may need to wait a bit longer, then run: .\START_ABENA_DEMO.ps1" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "[WARNING] Could not verify Docker daemon" -ForegroundColor Yellow
    Write-Host "  Please wait a bit longer, then run: .\START_ABENA_DEMO.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Desktop is Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting ABENA Demo..." -ForegroundColor Yellow
Write-Host ""

# Run the demo startup script
& ".\START_ABENA_DEMO.ps1"













