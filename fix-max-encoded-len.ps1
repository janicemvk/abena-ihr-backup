## Script to Fix MaxEncodedLen Errors by Converting Vec to BoundedVec
Write-Host "=== Fixing MaxEncodedLen Errors ===" -ForegroundColor Cyan
Write-Host "This script converts Vec to BoundedVec in structs used in storage" -ForegroundColor Yellow
Write-Host ""

# Define reasonable max lengths for different Vec types
# These can be adjusted based on your requirements
$maxLengths = @{
    "Vec<u8>" = 4096        # 4KB for byte arrays
    "Vec<AccountId>" = 100  # Max 100 signers/accounts
    "Vec<AchievementType>" = 50  # Max 50 achievements
    "Vec<Treatment>" = 100  # Max 100 treatments
    "Vec<QuantumCapability>" = 20  # Max 20 capabilities
    "Vec<PublicKey>" = 10   # Max 10 public keys
    "Vec<RecordVersion>" = 100  # Max 100 versions
    "Vec<AuditLogEntry>" = 1000  # Max 1000 audit log entries
    "Vec<RewardEntry>" = 1000    # Max 1000 reward entries
}

# Step 1: Add BoundedVec imports to all pallets
Write-Host "[1/4] Adding BoundedVec imports..." -ForegroundColor Yellow

$pallets = @(
    "pallets\patient-health-records\src\lib.rs",
    "pallets\governance\src\lib.rs",
    "pallets\treatment-protocol\src\lib.rs",
    "pallets\health-record-hash\src\lib.rs",
    "pallets\abena-coin\src\lib.rs",
    "pallets\interoperability\src\lib.rs",
    "pallets\patient-identity\src\lib.rs",
    "pallets\quantum-computing\src\lib.rs"
)

foreach ($file in $pallets) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        
        # Add BoundedVec and ConstU32 imports if not present
        # BoundedVec is in frame_support::bounded_vec
        # ConstU32 is in frame_support::traits
        if ($content -notmatch 'use frame_support::bounded_vec::BoundedVec') {
            # Add in the pallet module after frame_support imports
            if ($content -match 'use frame_support::\{[^}]*pallet_prelude::\*[^}]*\}') {
                # Add to the frame_support import block
                $content = $content -replace '(use frame_support::\{[^}]*pallet_prelude::\*[^}]*)(\})', '$1, bounded_vec::BoundedVec, traits::ConstU32$2'
            } elseif ($content -match 'use frame_support::pallet_prelude::\*') {
                # Add as separate import
                $content = $content -replace '(use frame_support::pallet_prelude::\*;)', '$1' + [Environment]::NewLine + '    use frame_support::{bounded_vec::BoundedVec, traits::ConstU32};'
            }
        }
        
        Set-Content -Path $file -Value $content -NoNewline
        Write-Host "  Updated imports in $file" -ForegroundColor Gray
    }
}
Write-Host "Added BoundedVec imports" -ForegroundColor Green

# Step 2: Convert Vec<u8> to BoundedVec<u8, ConstU32<4096>> in struct definitions
Write-Host ""
Write-Host "[2/4] Converting Vec<u8> to BoundedVec..." -ForegroundColor Yellow

# patient-health-records: EncryptedHealthRecord, EncryptionMetadataRecord
$file = "pallets\patient-health-records\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Convert Vec<u8> to BoundedVec<u8, ConstU32<4096>> in EncryptedHealthRecord
    $content = $content -replace '(\s+pub data: )Vec<u8>', '$1BoundedVec<u8, ConstU32<4096>>'
    
    # Convert Vec<u8> in EncryptionMetadataRecord
    $content = $content -replace '(\s+pub parameters: )Vec<u8>', '$1BoundedVec<u8, ConstU32<256>>'
    $content = $content -replace '(\s+pub kdf: )Vec<u8>', '$1BoundedVec<u8, ConstU32<128>>'
    $content = $content -replace '(\s+pub metadata: )Vec<u8>', '$1BoundedVec<u8, ConstU32<512>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated patient-health-records" -ForegroundColor Gray
}

# governance: GuidelineProposal, ProtocolProposal, EmergencyIntervention
$file = "pallets\governance\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    $content = $content -replace '(\s+pub guideline_content: )Vec<u8>', '$1BoundedVec<u8, ConstU32<8192>>'
    $content = $content -replace '(\s+pub protocol_content: )Vec<u8>', '$1BoundedVec<u8, ConstU32<8192>>'
    $content = $content -replace '(\s+pub reason: )Vec<u8>', '$1BoundedVec<u8, ConstU32<1024>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated governance" -ForegroundColor Gray
}

# treatment-protocol: TreatmentProtocol, ClinicalGuideline, ContraindicationStatus
$file = "pallets\treatment-protocol\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    $content = $content -replace '(\s+pub treatments: )Vec<Treatment>', '$1BoundedVec<Treatment, ConstU32<100>>'
    $content = $content -replace '(\s+pub details: )Vec<u8>', '$1BoundedVec<u8, ConstU32<4096>>'
    $content = $content -replace '(\s+pub dosage: )Vec<u8>', '$1BoundedVec<u8, ConstU32<512>>'
    $content = $content -replace '(\s+pub name: )Vec<u8>', '$1BoundedVec<u8, ConstU32<256>>'
    $content = $content -replace '(\s+pub version: )Vec<u8>', '$1BoundedVec<u8, ConstU32<64>>'
    $content = $content -replace '(\s+pub content: )Vec<u8>', '$1BoundedVec<u8, ConstU32<8192>>'
    $content = $content -replace '(\s+pub reasons: )Vec<u8>', '$1BoundedVec<u8, ConstU32<1024>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated treatment-protocol" -ForegroundColor Gray
}

# abena-coin: AchievementRecord
$file = "pallets\abena-coin\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    $content = $content -replace '(\s+pub unlocked_achievements: )Vec<AchievementType>', '$1BoundedVec<AchievementType, ConstU32<50>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated abena-coin" -ForegroundColor Gray
}

# interoperability: FHIRResourceMapping, CrossChainExchange, etc.
$file = "pallets\interoperability\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    $content = $content -replace '(\s+pub blockchain_record_id: )Vec<u8>', '$1BoundedVec<u8, ConstU32<256>>'
    $content = $content -replace '(\s+pub source_chain: )Vec<u8>', '$1BoundedVec<u8, ConstU32<64>>'
    $content = $content -replace '(\s+pub target_chain: )Vec<u8>', '$1BoundedVec<u8, ConstU32<64>>'
    $content = $content -replace '(\s+pub pharmacy_name: )Vec<u8>', '$1BoundedVec<u8, ConstU32<128>>'
    $content = $content -replace '(\s+pub endpoint: )Vec<u8>', '$1BoundedVec<u8, ConstU32<256>>'
    $content = $content -replace '(\s+pub lab_name: )Vec<u8>', '$1BoundedVec<u8, ConstU32<128>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated interoperability" -ForegroundColor Gray
}

# patient-identity: DIDDocument, PublicKey, etc.
$file = "pallets\patient-identity\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    $content = $content -replace '(\s+pub did: )Vec<u8>', '$1BoundedVec<u8, ConstU32<256>>'
    $content = $content -replace '(\s+pub public_keys: )Vec<PublicKey>', '$1BoundedVec<PublicKey, ConstU32<10>>'
    $content = $content -replace '(\s+pub key_type: )Vec<u8>', '$1BoundedVec<u8, ConstU32<64>>'
    $content = $content -replace '(\s+pub public_key: )Vec<u8>', '$1BoundedVec<u8, ConstU32<512>>'
    $content = $content -replace '(\s+pub key_id: )Vec<u8>', '$1BoundedVec<u8, ConstU32<128>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated patient-identity" -ForegroundColor Gray
}

# quantum-computing: QuantumJob, QuantumResult, IntegrationPoint
$file = "pallets\quantum-computing\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    $content = $content -replace '(\s+pub parameters: )Vec<u8>', '$1BoundedVec<u8, ConstU32<4096>>'
    $content = $content -replace '(\s+pub result_data: )Vec<u8>', '$1BoundedVec<u8, ConstU32<8192>>'
    $content = $content -replace '(\s+pub provider_name: )Vec<u8>', '$1BoundedVec<u8, ConstU32<128>>'
    $content = $content -replace '(\s+pub endpoint: )Vec<u8>', '$1BoundedVec<u8, ConstU32<256>>'
    $content = $content -replace '(\s+pub capabilities: )Vec<QuantumCapability>', '$1BoundedVec<QuantumCapability, ConstU32<20>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated quantum-computing" -ForegroundColor Gray
}

# health-record-hash: MultiSigConfig
$file = "pallets\health-record-hash\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    $content = $content -replace '(\s+pub authorized_signers: )Vec<T::AccountId>', '$1BoundedVec<T::AccountId, ConstU32<100>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated health-record-hash" -ForegroundColor Gray
}

Write-Host "Converted Vec<u8> and Vec<T> to BoundedVec" -ForegroundColor Green

# Step 3: Convert Vec<T> in storage types (RecordVersions, AuditLogs, RewardHistory)
Write-Host ""
Write-Host "[3/4] Converting Vec<T> in storage declarations..." -ForegroundColor Yellow

$file = "pallets\health-record-hash\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Convert Vec<RecordVersion<T>> to BoundedVec<RecordVersion<T>, ConstU32<100>>
    $content = $content -replace 'Vec<RecordVersion<T>>', 'BoundedVec<RecordVersion<T>, ConstU32<100>>'
    
    # Convert Vec<AuditLogEntry<T>> to BoundedVec<AuditLogEntry<T>, ConstU32<1000>>
    $content = $content -replace 'Vec<AuditLogEntry<T>>', 'BoundedVec<AuditLogEntry<T>, ConstU32<1000>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated storage types in health-record-hash" -ForegroundColor Gray
}

$file = "pallets\abena-coin\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Convert Vec<RewardEntry<T>> to BoundedVec<RewardEntry<T>, ConstU32<1000>>
    $content = $content -replace 'Vec<RewardEntry<T>>', 'BoundedVec<RewardEntry<T>, ConstU32<1000>>'
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Updated storage types in abena-coin" -ForegroundColor Gray
}

Write-Host "Converted Vec<T> in storage declarations" -ForegroundColor Green

# Step 4: Add MaxEncodedLen to enums and structs that can support it
Write-Host ""
Write-Host "[4/4] Adding MaxEncodedLen to enums and structs..." -ForegroundColor Yellow

# FHIRResourceType enum - add MaxEncodedLen to derive
$file = "pallets\interoperability\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to FHIRResourceType derive if not present
    if ($content -notmatch 'FHIRResourceType.*MaxEncodedLen') {
        $content = $content -replace '(#\[derive\([^)]*TypeInfo\))(\][^\n]*\n[^\n]*pub enum FHIRResourceType)', '$1, MaxEncodedLen$2'
    }
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Added MaxEncodedLen to FHIRResourceType" -ForegroundColor Gray
}

# CredentialType enum - add MaxEncodedLen to derive
$file = "pallets\patient-identity\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to CredentialType derive if not present
    if ($content -notmatch 'CredentialType.*MaxEncodedLen') {
        $content = $content -replace '(#\[derive\([^)]*TypeInfo\))(\][^\n]*\n[^\n]*pub enum CredentialType)', '$1, MaxEncodedLen$2'
    }
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Added MaxEncodedLen to CredentialType" -ForegroundColor Gray
}

# ContraindicationStatus - add MaxEncodedLen after converting Vec to BoundedVec
$file = "pallets\treatment-protocol\src\lib.rs"
if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Add MaxEncodedLen to ContraindicationStatus derive if not present and it now uses BoundedVec
    if (($content -match 'ContraindicationStatus.*BoundedVec') -and ($content -notmatch 'ContraindicationStatus.*MaxEncodedLen')) {
        $content = $content -replace '(#\[derive\([^)]*TypeInfo\))(\][^\n]*\n[^\n]*pub struct ContraindicationStatus)', '$1, MaxEncodedLen$2'
    }
    
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "  Added MaxEncodedLen to ContraindicationStatus" -ForegroundColor Gray
}

Write-Host "Added MaxEncodedLen to enums and fixed structs" -ForegroundColor Green

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Added BoundedVec and ConstU32 imports" -ForegroundColor Green
Write-Host "Converted Vec<u8> to BoundedVec<u8, ConstU32<N>>" -ForegroundColor Green
Write-Host "Converted Vec<T> to BoundedVec<T, ConstU32<N>>" -ForegroundColor Green
Write-Host "Converted Vec<T> in storage declarations" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the bounds (ConstU32<N>) and adjust if needed" -ForegroundColor Cyan
Write-Host "  2. Fix any code that uses these Vec fields (convert to BoundedVec)" -ForegroundColor Cyan
Write-Host "  3. Add MaxEncodedLen back to structs that now only use BoundedVec" -ForegroundColor Cyan
Write-Host "  4. Run: cargo build --release" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: You'll need to update all code that creates/modifies these fields" -ForegroundColor Yellow
Write-Host "to use BoundedVec::try_from() or BoundedVec::truncate_from()" -ForegroundColor Yellow

