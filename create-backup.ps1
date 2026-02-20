# ABENA Database Backup Script
# Creates a backup of the ABENA database before security integration

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ABENA Database Backup Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Step 1: Check if Docker is running
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if containers are running
Write-Host ""
Write-Host "Step 2: Checking ABENA containers..." -ForegroundColor Yellow
$postgresRunning = docker ps --filter "name=abena-postgres" --format "{{.Names}}" 2>$null

if (-not $postgresRunning) {
    Write-Host "[INFO] ABENA containers not running. Starting them..." -ForegroundColor Yellow
    Write-Host ""
    
    # Start containers
    Write-Host "Starting ABENA system (this may take 1-2 minutes)..." -ForegroundColor Cyan
    docker-compose up -d
    
    Write-Host "Waiting for database to be ready..." -ForegroundColor Cyan
    Start-Sleep -Seconds 30
    
    # Check again
    $postgresRunning = docker ps --filter "name=abena-postgres" --format "{{.Names}}" 2>$null
    
    if (-not $postgresRunning) {
        Write-Host "[ERROR] Could not start ABENA containers" -ForegroundColor Red
        Write-Host "Please run: docker-compose up -d" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "[OK] Container found: $postgresRunning" -ForegroundColor Green

# Step 3: Test database connection
Write-Host ""
Write-Host "Step 3: Testing database connection..." -ForegroundColor Yellow
$dbTest = docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT 1;" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Database connection successful" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Cannot connect to database" -ForegroundColor Red
    Write-Host "Error: $dbTest" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check if postgres is healthy: docker ps" -ForegroundColor White
    Write-Host "2. Check logs: docker logs abena-postgres" -ForegroundColor White
    Write-Host "3. Wait a bit longer for database to initialize" -ForegroundColor White
    exit 1
}

# Step 4: Create backups directory
Write-Host ""
Write-Host "Step 4: Preparing backup directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path ".\backups" | Out-Null
Write-Host "[OK] Backup directory ready: .\backups\" -ForegroundColor Green

# Step 5: Create backup
Write-Host ""
Write-Host "Step 5: Creating database backup..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = ".\backups\backup_manual_$timestamp.sql"

Write-Host "Backup file: $backupFile" -ForegroundColor Cyan
Write-Host "This may take a minute..." -ForegroundColor Cyan

try {
    docker exec abena-postgres pg_dump -U abena_user abena_ihr > $backupFile 2>&1
    
    if (Test-Path $backupFile) {
        $fileSize = (Get-Item $backupFile).Length
        $sizeKB = [math]::Round($fileSize/1KB, 2)
        $sizeMB = [math]::Round($fileSize/1MB, 2)
        
        if ($fileSize -gt 10000) {
            Write-Host "[OK] Backup created successfully!" -ForegroundColor Green
            Write-Host "  File: $backupFile" -ForegroundColor Cyan
            Write-Host "  Size: $sizeKB KB ($sizeMB MB)" -ForegroundColor Cyan
        } else {
            Write-Host "[WARN] Backup file seems very small ($fileSize bytes)" -ForegroundColor Yellow
            Write-Host "The database might be empty or backup failed" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[ERROR] Backup file was not created" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Backup failed: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Verify backup (optional)
Write-Host ""
Write-Host "Step 6: Verifying backup..." -ForegroundColor Yellow
$backupContent = Get-Content $backupFile -TotalCount 10
$hasData = $backupContent | Select-String -Pattern "PostgreSQL database dump|CREATE TABLE|INSERT INTO"

if ($hasData) {
    Write-Host "[OK] Backup file contains valid SQL data" -ForegroundColor Green
} else {
    Write-Host "[WARN] Backup file may not contain valid data" -ForegroundColor Yellow
    Write-Host "First few lines:" -ForegroundColor Cyan
    Get-Content $backupFile -TotalCount 5 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Backup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backup Details:" -ForegroundColor Yellow
Write-Host "  Location: $backupFile" -ForegroundColor Cyan
Write-Host "  Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""
Write-Host "All Backups:" -ForegroundColor Yellow
Get-ChildItem ".\backups\*.sql" | ForEach-Object {
    $size = [math]::Round($_.Length/1KB, 2)
    Write-Host "  $($_.Name) - $size KB - $($_.LastWriteTime)" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Your database is now backed up safely" -ForegroundColor White
Write-Host "2. You can proceed with security integration:" -ForegroundColor White
Write-Host "   .\COMPLETE_SECURITY_INTEGRATION_CLEAN.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "To restore this backup if needed:" -ForegroundColor Yellow
Write-Host "  Get-Content '$backupFile' | docker exec -i abena-postgres psql -U abena_user -d abena_ihr" -ForegroundColor Cyan
Write-Host ""

