# Diagnose and Fix Postgres Container Issues

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Postgres Diagnosis Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if container exists
Write-Host "Checking container status..." -ForegroundColor Yellow
docker ps -a --filter "name=abena-postgres"

Write-Host ""
Write-Host "Checking container logs (last 50 lines)..." -ForegroundColor Yellow
docker logs abena-postgres --tail 50

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Analysis & Fix" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Try to restart
Write-Host "Attempting to restart postgres..." -ForegroundColor Yellow
docker restart abena-postgres

Start-Sleep -Seconds 10

# Check if it's running now
$status = docker ps --filter "name=abena-postgres" --format "{{.Status}}"

if ($status -match "Up") {
    Write-Host "[OK] Postgres is now running!" -ForegroundColor Green
    Write-Host "Status: $status" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Testing connection..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT 1;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database connection works!" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now proceed with:" -ForegroundColor Green
        Write-Host "  .\migrate-passwords-clean.ps1" -ForegroundColor Cyan
    }
} else {
    Write-Host "[ERROR] Postgres won't stay running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common causes:" -ForegroundColor Yellow
    Write-Host "1. SQL init files have errors" -ForegroundColor White
    Write-Host "2. Database already exists with conflicts" -ForegroundColor White
    Write-Host "3. Port 5432 already in use inside container" -ForegroundColor White
    Write-Host ""
    Write-Host "Try these fixes:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Remove init files temporarily" -ForegroundColor Cyan
    Write-Host "  Rename SQL files to .sql.bak" -ForegroundColor White
    Write-Host "  docker-compose down -v" -ForegroundColor White
    Write-Host "  docker-compose up -d postgres" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Start fresh database" -ForegroundColor Cyan
    Write-Host "  docker-compose down -v" -ForegroundColor White
    Write-Host "  docker volume rm abena-backup_postgres_data" -ForegroundColor White
    Write-Host "  docker-compose up -d postgres redis" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3: Check the logs above for specific errors" -ForegroundColor Cyan
}

