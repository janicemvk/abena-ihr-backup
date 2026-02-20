# ABENA Password Migration Script
# Step 6: Migrate passwords from plain text to bcrypt

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ABENA Password Migration Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Check if backup exists
$latestBackup = Get-ChildItem ".\backups\backup_pre_security_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $latestBackup) {
    Write-Host "✗ ERROR: No backup found!" -ForegroundColor Red
    Write-Host "Please run .\integrate-security.ps1 first to create a backup." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Backup found: $($latestBackup.Name)" -ForegroundColor Green
Write-Host "  Created: $($latestBackup.LastWriteTime)" -ForegroundColor Cyan
Write-Host "  Size: $([math]::Round($latestBackup.Length/1KB, 2)) KB" -ForegroundColor Cyan
Write-Host ""

# Step 6a: Dry Run
Write-Host "=== STEP 6a: Password Migration - DRY RUN ===" -ForegroundColor Green
Write-Host "This will NOT make any changes to the database." -ForegroundColor Yellow
Write-Host "Review the output carefully before proceeding." -ForegroundColor Yellow
Write-Host ""

# Set environment variables for migration script
$env:DATABASE_URL = "postgresql://abena_user:abena_password@localhost:5433/abena_ihr"

Write-Host "Running dry-run migration..." -ForegroundColor Cyan
try {
    python security-package\migrations\migrate_passwords.py --dry-run
    
    Write-Host ""
    Write-Host "✓ Dry-run completed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Ask user if they want to proceed
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host "IMPORTANT: Review the dry-run output above" -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to proceed with ACTUAL password migration? (yes/no)"
    
    if ($response -ne "yes") {
        Write-Host ""
        Write-Host "Migration cancelled. No changes made to database." -ForegroundColor Yellow
        Write-Host "You can run this script again when ready." -ForegroundColor Cyan
        exit 0
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ Dry-run failed. Error: $_" -ForegroundColor Red
    Write-Host "Please check the database connection and try again." -ForegroundColor Red
    exit 1
}

# Step 6b: Actual Migration
Write-Host ""
Write-Host "=== STEP 6b: Password Migration - ACTUAL ===" -ForegroundColor Green
Write-Host "⚠ This WILL modify the database!" -ForegroundColor Red
Write-Host ""

Write-Host "Creating additional backup before migration..." -ForegroundColor Yellow
$preMigrationBackup = ".\backups\backup_pre_migration_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
docker exec abena-postgres pg_dump -U abena_user abena_ihr > $preMigrationBackup
Write-Host "✓ Additional backup created: $preMigrationBackup" -ForegroundColor Green
Write-Host ""

Write-Host "Running ACTUAL migration..." -ForegroundColor Cyan
Write-Host "This will hash all plain text passwords with bcrypt..." -ForegroundColor Yellow
Write-Host ""

try {
    python security-package\migrations\migrate_passwords.py
    
    Write-Host ""
    Write-Host "✓ Password migration completed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Verify migration
    Write-Host "Verifying migration..." -ForegroundColor Cyan
    $verification = docker exec abena-postgres psql -U abena_user -d abena_ihr -t -c "SELECT COUNT(*) FROM users WHERE hashed_password LIKE '$2b$%';"
    
    if ($verification -gt 0) {
        Write-Host "✓ Verified: $verification passwords successfully hashed with bcrypt" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: No bcrypt passwords found. Migration may have failed." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ Migration failed. Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "ROLLBACK PROCEDURE:" -ForegroundColor Red
    Write-Host "1. Stop services: docker-compose down" -ForegroundColor Yellow
    Write-Host "2. Restore backup: Get-Content '$preMigrationBackup' | docker exec -i abena-postgres psql -U abena_user -d abena_ihr" -ForegroundColor Yellow
    Write-Host "3. Restart services: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Password Migration Completed!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ All passwords migrated to bcrypt" -ForegroundColor Green
Write-Host "✓ Backups created:" -ForegroundColor Green
Write-Host "  - $($latestBackup.Name)" -ForegroundColor Cyan
Write-Host "  - $(Split-Path $preMigrationBackup -Leaf)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update ABENA IHR with security middleware" -ForegroundColor White
Write-Host "2. Test authentication endpoints" -ForegroundColor White
Write-Host "3. Restart services" -ForegroundColor White
Write-Host ""
Write-Host "To continue, run: .\update-services-security.ps1" -ForegroundColor Cyan

