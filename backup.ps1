# ABENA Blockchain Backup Script
# Creates a timestamped backup of the entire project

Write-Host "=== ABENA Blockchain Backup ===" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupDir = "backups"
$backupName = "abena-blockchain-backup-$timestamp"
$backupPath = Join-Path $backupDir $backupName

# Create backup directory if it doesn't exist
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "Created backup directory: $backupDir" -ForegroundColor Green
}

Write-Host "Creating backup: $backupName" -ForegroundColor Yellow

# Exclude target directory and other build artifacts
$excludeItems = @(
    "target",
    "*.log",
    "*.pdb",
    ".git",
    "backups"
)

# Create temporary exclude file
$excludeFile = Join-Path $env:TEMP "backup-exclude-$timestamp.txt"
$excludeItems | Out-File -FilePath $excludeFile -Encoding ASCII

try {
    # Use robocopy for efficient backup (Windows)
    $source = Get-Location
    $destination = Join-Path (Resolve-Path $backupDir) $backupName
    
    # Create destination directory
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    
    # Copy files excluding build artifacts
    robocopy $source $destination /E /XD target .git backups /XF *.log *.pdb /NFL /NDL /NJH /NJS | Out-Null
    
    # Create a manifest file
    $manifest = @"
ABENA Blockchain Backup Manifest
================================
Backup Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Backup Location: $destination

Project Contents:
- 11 Custom Pallets
- Runtime Configuration
- Node Implementation
- Tests and Benchmarks
- Documentation

Pallets:
1. Patient Health Records
2. ABENA Coin
3. Quantum Computing
4. Patient Identity
5. Health Record Hash
6. Treatment Protocol
7. Interoperability
8. Governance
9. Fee Management (NEW)
10. Access Control (NEW)
11. Account Management (NEW)

Git Status:
$(git log --oneline -1 2>$null)
"@
    
    $manifest | Out-File -FilePath (Join-Path $destination "BACKUP_MANIFEST.txt") -Encoding UTF8
    
    Write-Host ""
    Write-Host "Backup completed successfully!" -ForegroundColor Green
    Write-Host "Backup location: $destination" -ForegroundColor Cyan
    Write-Host ""
    
    # Show backup size
    $backupSize = (Get-ChildItem -Path $destination -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "Backup size: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Yellow
    
} catch {
    Write-Host "Error during backup: $_" -ForegroundColor Red
    exit 1
} finally {
    # Clean up exclude file
    if (Test-Path $excludeFile) {
        Remove-Item $excludeFile -Force
    }
}

Write-Host ""
Write-Host "=== Backup Complete ===" -ForegroundColor Cyan


