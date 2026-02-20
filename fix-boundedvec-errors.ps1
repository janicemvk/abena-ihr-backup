## Script to Fix Remaining BoundedVec Errors
Write-Host "=== Fixing Remaining BoundedVec Errors ===" -ForegroundColor Cyan

# Step 1: Add MaxEncodedLen to enums
Write-Host ""
Write-Host "[1/6] Adding MaxEncodedLen to enums..." -ForegroundColor Yellow

# treatment-protocol enums
$file = "pallets\treatment-protocol\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to TreatmentType, Modality, ProtocolStatus
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum TreatmentType)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum Modality)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum ProtocolStatus)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    
    # Convert Vec<u8> in enum variants to BoundedVec
    $content = $content -replace 'Other\(Vec<u8>\)', 'Other(BoundedVec<u8, ConstU32<256>>)'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated treatment-protocol enums" -ForegroundColor Gray
}

# health-record-hash enums
$file = "pallets\health-record-hash\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to RecordType, AuditAction
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum RecordType)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum AuditAction)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated health-record-hash enums" -ForegroundColor Gray
}

# quantum-computing enums
$file = "pallets\quantum-computing\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to QuantumJobType, JobStatus, QuantumCapability
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum QuantumJobType)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum JobStatus)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum QuantumCapability)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated quantum-computing enums" -ForegroundColor Gray
}

# governance enums
$file = "pallets\governance\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to EmergencyInterventionType
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub enum EmergencyInterventionType)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated governance enums" -ForegroundColor Gray
}

# treatment-protocol: ContraindicationStatus
$file = "pallets\treatment-protocol\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to ContraindicationStatus
    $content = $content -replace '(#\[derive\([^)]*TypeInfo\)\]\s*\r?\n)(pub struct ContraindicationStatus)', '$1#[derive(MaxEncodedLen)]' + [Environment]::NewLine + '$2'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Added MaxEncodedLen to ContraindicationStatus" -ForegroundColor Gray
}

Write-Host "Added MaxEncodedLen to enums" -ForegroundColor Green

# Step 2: Add Debug to ClinicalGuideline
Write-Host ""
Write-Host "[2/6] Adding Debug to ClinicalGuideline..." -ForegroundColor Yellow

$file = "pallets\treatment-protocol\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add Debug to ClinicalGuideline
    $content = $content -replace '(#\[derive\(Clone, Encode, Decode, PartialEq, Eq, TypeInfo, MaxEncodedLen\)\]\s*\r?\n)(#\[scale_info\(skip_type_params\(T\)\)\]\s*\r?\n)(pub struct ClinicalGuideline)', '$1#[derive(Debug)]' + [Environment]::NewLine + '$2$3'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "Added Debug to ClinicalGuideline" -ForegroundColor Green
}

# Step 3: Fix Vec to BoundedVec conversions in function code
Write-Host ""
Write-Host "[3/6] Fixing Vec to BoundedVec conversions..." -ForegroundColor Yellow
Write-Host "  Note: This requires manual fixes in function code" -ForegroundColor Gray
Write-Host "  Use BoundedVec::try_from() or BoundedVec::truncate_from()" -ForegroundColor Gray

# Step 4: Fix BoundedVec.push() issues
Write-Host ""
Write-Host "[4/6] Fixing BoundedVec.push() issues..." -ForegroundColor Yellow
Write-Host "  Note: BoundedVec doesn't support .push() directly" -ForegroundColor Gray
Write-Host "  Use .try_mutate() or convert to Vec, modify, then convert back" -ForegroundColor Gray

# Step 5: Summary
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Added MaxEncodedLen to enums"
Write-Host "Added Debug to ClinicalGuideline"
Write-Host ""
Write-Host "Remaining manual fixes needed:" -ForegroundColor Yellow
Write-Host "  1. Convert Vec to BoundedVec in function parameters and assignments"
Write-Host "  2. Fix BoundedVec.push() calls (use try_mutate or similar)"
Write-Host "  3. Convert Vec::new() to BoundedVec::default() or BoundedVec::try_from(vec![])"
Write-Host "  4. Fix Option<Vec<u8>> to Option<BoundedVec<u8, ConstU32<N>>>"
Write-Host ""
Write-Host "Next: Run cargo build --release to see remaining errors" -ForegroundColor Green


