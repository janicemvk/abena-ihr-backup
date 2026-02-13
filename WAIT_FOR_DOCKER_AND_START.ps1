# Wait for Docker Desktop to be ready, then start ABENA Demo

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Waiting for Docker Desktop..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker Desktop process is running
$maxWait = 120  # 2 minutes max wait
$waited = 0
$dockerProcess = $null

Write-Host "Waiting for Docker Desktop process..." -ForegroundColor Yellow
while ($waited -lt $maxWait) {
    $dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
    if ($dockerProcess) {
        Write-Host "[OK] Docker Desktop process detected" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 3
    $waited += 3
    if ($waited % 15 -eq 0) {
        Write-Host "  Still waiting... ($waited seconds)" -ForegroundColor Gray
    }
}

if (-not $dockerProcess) {
    Write-Host "[WARNING] Docker Desktop process not detected after $maxWait seconds" -ForegroundColor Yellow
    Write-Host "Please check Docker Desktop manually and ensure it's running." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Waiting for Docker daemon to be ready..." -ForegroundColor Yellow
Write-Host "This may take 30-60 seconds..." -ForegroundColor White
Write-Host ""

# Wait for Docker daemon
$waited = 0
$daemonReady = $false

while ($waited -lt $maxWait) {
    try {
        $result = docker ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Docker daemon is ready!" -ForegroundColor Green
            $daemonReady = $true
            break
        }
    } catch {
        # Continue waiting
    }
    
    Start-Sleep -Seconds 5
    $waited += 5
    
    if ($waited % 15 -eq 0) {
        Write-Host "  Still waiting for daemon... ($waited seconds)" -ForegroundColor Gray
    }
}

if (-not $daemonReady) {
    Write-Host "[WARNING] Docker daemon not ready after $maxWait seconds" -ForegroundColor Yellow
    Write-Host "You may need to wait a bit longer." -ForegroundColor Yellow
    Write-Host "Check Docker Desktop window for status." -ForegroundColor Yellow
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













