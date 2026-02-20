# Restore Database After Docker Compose Start
# This restores the migrated passwords and schema

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Restoring Database After Compose Start" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Wait for postgres to be ready
Write-Host "Waiting for postgres to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check if postgres is running
$postgresRunning = docker ps --filter "name=abena-postgres" --format "{{.Names}}"
if (-not $postgresRunning) {
    Write-Host "[ERROR] Postgres container not running!" -ForegroundColor Red
    Write-Host "Please start it first: docker-compose up -d postgres" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Postgres is running" -ForegroundColor Green

# Find the latest backup with data
$backupFile = Get-ChildItem ".\backups\backup_with_data_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $backupFile) {
    Write-Host "[WARN] No backup file found. Creating schema from scratch..." -ForegroundColor Yellow
    
    # Create schema
    .\setup-database-schema.ps1
    
    # Migrate passwords
    Write-Host ""
    Write-Host "Migrating passwords..." -ForegroundColor Yellow
    .\migrate-passwords-simple.ps1
} else {
    Write-Host "Restoring from backup: $($backupFile.Name)" -ForegroundColor Cyan
    
    # Restore backup
    Get-Content $backupFile | docker exec -i abena-postgres psql -U abena_user -d abena_ihr
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database restored successfully" -ForegroundColor Green
        
        # Verify passwords are hashed
        Write-Host ""
        Write-Host "Verifying password migration..." -ForegroundColor Yellow
        $bcryptCount = docker exec abena-postgres psql -U abena_user -d abena_ihr -t -c "SELECT COUNT(*) FROM users WHERE hashed_password LIKE '$2b$%';"
        $bcryptCount = $bcryptCount.Trim()
        
        if ([int]$bcryptCount -gt 0) {
            Write-Host "[OK] Verified: $bcryptCount passwords are hashed with bcrypt" -ForegroundColor Green
        } else {
            Write-Host "[WARN] No bcrypt passwords found. Running migration..." -ForegroundColor Yellow
            .\migrate-passwords-simple.ps1
        }
    } else {
        Write-Host "[ERROR] Restore failed" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Database Ready!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now start ABENA IHR:" -ForegroundColor Yellow
Write-Host "  docker-compose up -d abena-ihr" -ForegroundColor Cyan
Write-Host ""

