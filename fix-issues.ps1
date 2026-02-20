# Fix dependencies
Write-Host "Installing missing dependencies..." -ForegroundColor Yellow
pip install bcrypt==4.1.1
pip install bleach==6.1.0
pip install python-jose[cryptography]==3.3.0

# Check if Docker is running
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Test database connection
Write-Host "`nTesting database connection..." -ForegroundColor Yellow
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT 1;"
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Database connection working" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Cannot connect to database" -ForegroundColor Red
}

Write-Host "`nAll fixed! You can now run:" -ForegroundColor Green
Write-Host "  .\COMPLETE_SECURITY_INTEGRATION_CLEAN.ps1" -ForegroundColor Cyan