# Comprehensive Backup Script for ABENA System
# Backs up database, configurations, code, and documentation

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ABENA System Comprehensive Backup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Create backup directory with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backup_$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "Backup directory: $backupDir" -ForegroundColor Green
Write-Host ""

# 1. Database Backup
Write-Host "1. Backing up PostgreSQL database..." -ForegroundColor Yellow
$dbBackupFile = "$backupDir\abena_database_backup_$timestamp.sql"

$postgresRunning = docker ps --filter "name=abena-postgres" --format "{{.Names}}"
if ($postgresRunning) {
    Write-Host "   Postgres container is running" -ForegroundColor Green
    docker exec abena-postgres pg_dump -U abena_user -d abena_ihr > $dbBackupFile 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dbSize = (Get-Item $dbBackupFile).Length / 1KB
        Write-Host "   [OK] Database backup created: $dbSize KB" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Database backup had issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [SKIP] Postgres container not running" -ForegroundColor Yellow
}
Write-Host ""

# 2. Configuration Files Backup
Write-Host "2. Backing up configuration files..." -ForegroundColor Yellow
$configDir = "$backupDir\config"
New-Item -ItemType Directory -Path $configDir -Force | Out-Null

# Docker Compose
if (Test-Path "docker-compose.yml") {
    Copy-Item "docker-compose.yml" "$configDir\docker-compose.yml" -ErrorAction SilentlyContinue
    Write-Host "   [OK] docker-compose.yml" -ForegroundColor Green
}

# Key configuration files (non-recursive to avoid issues)
$configFiles = @(
    "abena_ihr\requirements.txt",
    "abena_ihr\Dockerfile",
    "abena_ihr\env.example"
)

foreach ($file in $configFiles) {
    if (Test-Path $file) {
        $fileName = Split-Path $file -Leaf
        Copy-Item $file "$configDir\$fileName" -ErrorAction SilentlyContinue
        Write-Host "   [OK] $fileName" -ForegroundColor Green
    }
}
Write-Host ""

# 3. Security Files Backup
Write-Host "3. Backing up security configuration..." -ForegroundColor Yellow
$securityDir = "$backupDir\security"
New-Item -ItemType Directory -Path $securityDir -Force | Out-Null

# JWT Secret Key
if (Test-Path "jwt-secret-key.txt") {
    Copy-Item "jwt-secret-key.txt" "$securityDir\jwt-secret-key.txt" -ErrorAction SilentlyContinue
    Write-Host "   [OK] JWT secret key backed up" -ForegroundColor Green
}

# Security integration file
if (Test-Path "abena_ihr\src\security_integration.py") {
    Copy-Item "abena_ihr\src\security_integration.py" "$securityDir\security_integration.py" -ErrorAction SilentlyContinue
    Write-Host "   [OK] security_integration.py" -ForegroundColor Green
}

# Security package key files only (not full recursive copy)
$securityPackageDir = "$securityDir\security-package"
New-Item -ItemType Directory -Path "$securityPackageDir\middleware" -Force | Out-Null
New-Item -ItemType Directory -Path "$securityPackageDir\utils" -Force | Out-Null
New-Item -ItemType Directory -Path "$securityPackageDir\validation" -Force | Out-Null

$securityFiles = @(
    "security-package\middleware\auth_middleware.py",
    "security-package\middleware\rate_limit.py",
    "security-package\utils\password_security.py",
    "security-package\validation\input_validation.py",
    "security-package\requirements.txt",
    "security-package\README.md"
)

foreach ($file in $securityFiles) {
    if (Test-Path $file) {
        $relativePath = $file.Replace("security-package\", "")
        $destPath = "$securityPackageDir\$relativePath"
        $destDir = Split-Path $destPath -Parent
        if ($destDir) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item $file $destPath -ErrorAction SilentlyContinue
        Write-Host "   [OK] $relativePath" -ForegroundColor Green
    }
}
Write-Host ""

# 4. Code Changes Backup
Write-Host "4. Backing up critical code changes..." -ForegroundColor Yellow
$codeDir = "$backupDir\code"
New-Item -ItemType Directory -Path $codeDir -Force | Out-Null

# Main API file
if (Test-Path "abena_ihr\src\api\main.py") {
    Copy-Item "abena_ihr\src\api\main.py" "$codeDir\main.py" -ErrorAction SilentlyContinue
    Write-Host "   [OK] main.py" -ForegroundColor Green
}
Write-Host ""

# 5. Documentation Backup
Write-Host "5. Backing up documentation..." -ForegroundColor Yellow
$docsDir = "$backupDir\documentation"
New-Item -ItemType Directory -Path $docsDir -Force | Out-Null

# Security documentation
$docFiles = @(
    "SECURITY_INTEGRATION_COMPLETE.md",
    "SECURITY_INTEGRATION_STATUS.md",
    "INTEGRATION_PLAN_QUANTUM_SECURITY.md",
    "QUICK_INTEGRATION_GUIDE.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Copy-Item $file "$docsDir\$file" -ErrorAction SilentlyContinue
        Write-Host "   [OK] $file" -ForegroundColor Green
    }
}

# Test scripts
$scriptFiles = @(
    "test-login.ps1",
    "test-protected-endpoints.ps1",
    "migrate-passwords-simple.ps1",
    "setup-database-schema.ps1"
)

foreach ($file in $scriptFiles) {
    if (Test-Path $file) {
        Copy-Item $file "$docsDir\$file" -ErrorAction SilentlyContinue
        Write-Host "   [OK] $file" -ForegroundColor Green
    }
}
Write-Host ""

# 6. Create Backup Manifest
Write-Host "6. Creating backup manifest..." -ForegroundColor Yellow
$manifest = @{
    timestamp = $timestamp
    backup_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    backup_directory = $backupDir
    components = @{
        database = if ($postgresRunning) { "backed_up" } else { "skipped_postgres_not_running" }
        configuration = "backed_up"
        security = "backed_up"
        code = "backed_up"
        documentation = "backed_up"
    }
    system_info = @{
        hostname = $env:COMPUTERNAME
        os = (Get-CimInstance Win32_OperatingSystem).Caption
    }
}

$manifest | ConvertTo-Json -Depth 10 | Out-File "$backupDir\manifest.json"
Write-Host "   [OK] manifest.json created" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Backup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup Location: $backupDir" -ForegroundColor Yellow
Write-Host ""

# Calculate total size
$totalSize = (Get-ChildItem -Path $backupDir -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Total Backup Size: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""

# List main directories
Write-Host "Backup Structure:" -ForegroundColor Cyan
Get-ChildItem -Path $backupDir -Directory | ForEach-Object {
    $dirSize = (Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1KB
    Write-Host "  [DIR] $($_.Name) ($([math]::Round($dirSize, 2)) KB)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "IMPORTANT: Keep jwt-secret-key.txt secure!" -ForegroundColor Yellow
Write-Host "Location: $backupDir\security\jwt-secret-key.txt" -ForegroundColor Yellow
Write-Host ""


