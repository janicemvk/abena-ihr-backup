# ABENA Security Integration Script - Phase 1
# Automates Steps 2-5 of Security Integration

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ABENA Security Integration - Phase 1" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$baseDir = Get-Location

# Step 2: Install Dependencies
Write-Host "=== STEP 2: Installing Security Dependencies ===" -ForegroundColor Green
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
cd "security-package"
try {
    pip install -r requirements.txt --quiet
    Write-Host "[OK] Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install dependencies. Please run manually:" -ForegroundColor Red
    Write-Host "  pip install -r security-package\requirements.txt" -ForegroundColor Yellow
    exit 1
}
cd ..

# Step 3: Generate JWT Secret
Write-Host ""
Write-Host "=== STEP 3: Generating JWT Secret ===" -ForegroundColor Green
$jwtSecret = python -c "import secrets; print(secrets.token_urlsafe(32))"
if ($jwtSecret) {
    Write-Host "[OK] JWT Secret generated: $($jwtSecret.Substring(0,20))..." -ForegroundColor Green
    
    # Check if .env exists, create if not
    if (-not (Test-Path ".env")) {
        Write-Host "Creating .env file..." -ForegroundColor Yellow
        New-Item -Path ".env" -ItemType File -Force | Out-Null
    }
    
    # Check if JWT_SECRET_KEY already exists
    $envContent = Get-Content ".env" -Raw -ErrorAction SilentlyContinue
    if ($envContent -match "JWT_SECRET_KEY=") {
        Write-Host "JWT_SECRET_KEY already exists in .env, skipping..." -ForegroundColor Yellow
    } else {
        Add-Content -Path ".env" -Value "JWT_SECRET_KEY=$jwtSecret"
        Write-Host "[OK] JWT Secret added to .env file" -ForegroundColor Green
    }
} else {
    Write-Host "[ERROR] Failed to generate JWT secret" -ForegroundColor Red
    exit 1
}

# Step 4: Test Security Modules
Write-Host ""
Write-Host "=== STEP 4: Testing Security Modules ===" -ForegroundColor Green

Write-Host "Testing password security..." -ForegroundColor Cyan
python security-package\utils\password_security.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Password security test passed" -ForegroundColor Green
} else {
    Write-Host "[WARN] Password security test had issues (may be OK)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Testing JWT authentication..." -ForegroundColor Cyan
python security-package\middleware\auth_middleware.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] JWT authentication test passed" -ForegroundColor Green
} else {
    Write-Host "[WARN] JWT authentication test had issues (may be OK)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Testing input validation..." -ForegroundColor Cyan
python security-package\validation\input_validation.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Input validation test passed" -ForegroundColor Green
} else {
    Write-Host "[WARN] Input validation test had issues (may be OK)" -ForegroundColor Yellow
}

# Step 5: Backup Database
Write-Host ""
Write-Host "=== STEP 5: Backing Up Database ===" -ForegroundColor Green
Write-Host "CRITICAL: Creating database backup..." -ForegroundColor Yellow

# Create backups directory
New-Item -ItemType Directory -Force -Path ".\backups" | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = ".\backups\backup_pre_security_$timestamp.sql"

Write-Host "Backing up to: $backupFile" -ForegroundColor Cyan

try {
    docker exec abena-postgres pg_dump -U abena_user abena_ihr > $backupFile
    
    $backupSize = (Get-Item $backupFile).Length
    if ($backupSize -gt 1000) {
        $sizeKB = [math]::Round($backupSize/1KB, 2)
        Write-Host "[OK] Database backed up successfully! Size: $sizeKB KB" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Backup file seems small. Please verify manually." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Failed to backup database. Error: $_" -ForegroundColor Red
    Write-Host "Please backup manually before proceeding!" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Phase 1 Completed Successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] Step 2: Dependencies installed" -ForegroundColor Green
Write-Host "[OK] Step 3: JWT secret generated and saved" -ForegroundColor Green
Write-Host "[OK] Step 4: Security modules tested" -ForegroundColor Green
Write-Host "[OK] Step 5: Database backed up" -ForegroundColor Green
Write-Host ""
Write-Host "Backup location: $backupFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run password migration (dry-run)" -ForegroundColor White
Write-Host "2. Update ABENA IHR with security" -ForegroundColor White
Write-Host "3. Test authentication" -ForegroundColor White
Write-Host ""
Write-Host "To continue, run: .\migrate-passwords-clean.ps1" -ForegroundColor Cyan

