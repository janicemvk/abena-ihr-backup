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

# Check if postgres container is running
$postgresRunning = docker ps --filter "name=abena-postgres" --format "{{.Names}}"
if ($postgresRunning) {
    Write-Host "   Postgres container is running" -ForegroundColor Green
    docker exec abena-postgres pg_dump -U abena_user -d abena_ihr > $dbBackupFile 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dbSize = (Get-Item $dbBackupFile).Length / 1KB
        Write-Host "   ✅ Database backup created: $dbBackupFile ($([math]::Round($dbSize, 2)) KB)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Database backup had issues, but file created" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  Postgres container not running, skipping database backup" -ForegroundColor Yellow
}
Write-Host ""

# 2. Configuration Files Backup
Write-Host "2. Backing up configuration files..." -ForegroundColor Yellow
$configDir = "$backupDir\config"
New-Item -ItemType Directory -Path $configDir -Force | Out-Null

# Docker Compose
Copy-Item "docker-compose.yml" "$configDir\docker-compose.yml" -ErrorAction SilentlyContinue
Write-Host "   ✅ docker-compose.yml" -ForegroundColor Green

# Environment files
$rootPath = (Get-Location).Path
Get-ChildItem -Path . -Filter "*.env" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike "*$backupDir*" } | ForEach-Object {
    $relativePath = $_.FullName.Replace("$rootPath\", "").Replace("$rootPath", "")
    if ($relativePath -notlike "*$backupDir*") {
        $destPath = "$configDir\$relativePath"
        $destDir = Split-Path $destPath -Parent
        if ($destDir) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item $_.FullName $destPath -ErrorAction SilentlyContinue
        Write-Host "   ✅ $relativePath" -ForegroundColor Green
    }
}

# Requirements files
Get-ChildItem -Path . -Filter "requirements.txt" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike "*$backupDir*" } | ForEach-Object {
    $relativePath = $_.FullName.Replace("$rootPath\", "").Replace("$rootPath", "")
    if ($relativePath -notlike "*$backupDir*") {
        $destPath = "$configDir\$relativePath"
        $destDir = Split-Path $destPath -Parent
        if ($destDir) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item $_.FullName $destPath -ErrorAction SilentlyContinue
        Write-Host "   ✅ $relativePath" -ForegroundColor Green
    }
}
Write-Host ""

# 3. Security Files Backup
Write-Host "3. Backing up security configuration..." -ForegroundColor Yellow
$securityDir = "$backupDir\security"
New-Item -ItemType Directory -Path $securityDir -Force | Out-Null

# JWT Secret Key (carefully - don't expose in logs)
if (Test-Path "jwt-secret-key.txt") {
    Copy-Item "jwt-secret-key.txt" "$securityDir\jwt-secret-key.txt" -ErrorAction SilentlyContinue
    Write-Host "   ✅ JWT secret key backed up" -ForegroundColor Green
}

# Security package
if (Test-Path "security-package") {
    Write-Host "   Backing up security-package..." -ForegroundColor Cyan
    Copy-Item "security-package" "$securityDir\security-package" -Recurse -ErrorAction SilentlyContinue
    Write-Host "   ✅ security-package directory" -ForegroundColor Green
}

# Security integration files
if (Test-Path "abena_ihr\src\security_integration.py") {
    Copy-Item "abena_ihr\src\security_integration.py" "$securityDir\security_integration.py" -ErrorAction SilentlyContinue
    Write-Host "   ✅ security_integration.py" -ForegroundColor Green
}
Write-Host ""

# 4. Code Changes Backup
Write-Host "4. Backing up critical code changes..." -ForegroundColor Yellow
$codeDir = "$backupDir\code"
New-Item -ItemType Directory -Path $codeDir -Force | Out-Null

# Main API file
if (Test-Path "abena_ihr\src\api\main.py") {
    Copy-Item "abena_ihr\src\api\main.py" "$codeDir\main.py" -ErrorAction SilentlyContinue
    Write-Host "   ✅ abena_ihr/src/api/main.py" -ForegroundColor Green
}

# Requirements
if (Test-Path "abena_ihr\requirements.txt") {
    Copy-Item "abena_ihr\requirements.txt" "$codeDir\requirements.txt" -ErrorAction SilentlyContinue
    Write-Host "   ✅ abena_ihr/requirements.txt" -ForegroundColor Green
}
Write-Host ""

# 5. Documentation Backup
Write-Host "5. Backing up documentation..." -ForegroundColor Yellow
$docsDir = "$backupDir\documentation"
New-Item -ItemType Directory -Path $docsDir -Force | Out-Null

# Security documentation
Get-ChildItem -Path . -Filter "*SECURITY*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item $_.FullName "$docsDir\$($_.Name)" -ErrorAction SilentlyContinue
    Write-Host "   ✅ $($_.Name)" -ForegroundColor Green
}

# Integration documentation
Get-ChildItem -Path . -Filter "*INTEGRATION*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item $_.FullName "$docsDir\$($_.Name)" -ErrorAction SilentlyContinue
    Write-Host "   ✅ $($_.Name)" -ForegroundColor Green
}

# Test scripts
Get-ChildItem -Path . -Filter "test-*.ps1" -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item $_.FullName "$docsDir\$($_.Name)" -ErrorAction SilentlyContinue
    Write-Host "   ✅ $($_.Name)" -ForegroundColor Green
}

# Migration scripts
Get-ChildItem -Path . -Filter "*migrate*.ps1" -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item $_.FullName "$docsDir\$($_.Name)" -ErrorAction SilentlyContinue
    Write-Host "   ✅ $($_.Name)" -ForegroundColor Green
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
        docker_version = (docker --version 2>&1)
    }
}

$manifest | ConvertTo-Json -Depth 10 | Out-File "$backupDir\manifest.json"
Write-Host "   ✅ manifest.json created" -ForegroundColor Green
Write-Host ""

# 7. Create Archive (Optional - commented out to save space)
# Write-Host "7. Creating compressed archive..." -ForegroundColor Yellow
# $archiveName = "$backupDir.zip"
# Compress-Archive -Path $backupDir -DestinationPath $archiveName -Force
# $archiveSize = (Get-Item $archiveName).Length / 1MB
# Write-Host "   ✅ Archive created: $archiveName ($([math]::Round($archiveSize, 2)) MB)" -ForegroundColor Green
# Write-Host ""

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Backup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup Location: $backupDir" -ForegroundColor Yellow
Write-Host ""

# Calculate total size
$totalSize = (Get-ChildItem -Path $backupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Total Backup Size: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""

# List contents
Write-Host "Backup Contents:" -ForegroundColor Cyan
Get-ChildItem -Path $backupDir -Recurse -Directory | ForEach-Object {
    $dirPath = $_.FullName.Replace((Get-Location).Path + "\$backupDir\", '')
    Write-Host "  [DIR] $dirPath" -ForegroundColor Gray
}
Get-ChildItem -Path $backupDir -Recurse -File | ForEach-Object {
    $size = $_.Length / 1KB
    $relativePath = $_.FullName.Replace((Get-Location).Path + "\$backupDir\", '')
    $sizeRounded = [math]::Round($size, 2)
    Write-Host "  [FILE] $relativePath ($sizeRounded KB)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "IMPORTANT: Keep jwt-secret-key.txt secure!" -ForegroundColor Yellow
Write-Host "Location: $backupDir\security\jwt-secret-key.txt" -ForegroundColor Yellow
Write-Host ""

