# Create Basic Database Schema for Security Integration

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setting Up Database Schema" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Create basic schema SQL
$schemaSQL = @'
-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255),
    hashed_password VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'patient',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create providers table
CREATE TABLE IF NOT EXISTS providers (
    provider_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    specialization VARCHAR(100),
    department VARCHAR(100),
    npi_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    medical_record_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test provider
INSERT INTO users (email, password, first_name, last_name, role)
VALUES ('dr.johnson@abena.com', 'Abena2024Secure', 'Emily', 'Johnson', 'provider')
ON CONFLICT (email) DO NOTHING;

INSERT INTO providers (email, first_name, last_name, specialization, department)
VALUES ('dr.johnson@abena.com', 'Emily', 'Johnson', 'Neurology', 'Clinical')
ON CONFLICT (email) DO NOTHING;

-- Insert test patient
INSERT INTO users (email, password, first_name, last_name, role)
VALUES ('john.doe@example.com', 'Abena2024Secure', 'John', 'Doe', 'patient')
ON CONFLICT (email) DO NOTHING;

INSERT INTO patients (email, first_name, last_name, medical_record_number)
VALUES ('john.doe@example.com', 'John', 'Doe', 'MRN001')
ON CONFLICT (email) DO NOTHING;

-- Verify setup
SELECT 'Users created:' as info, COUNT(*) as count FROM users
UNION ALL
SELECT 'Providers created:', COUNT(*) FROM providers
UNION ALL
SELECT 'Patients created:', COUNT(*) FROM patients;
'@

# Save to temp file
$tempSQLFile = ".\temp_schema.sql"
Set-Content -Path $tempSQLFile -Value $schemaSQL

Write-Host "Creating database schema..." -ForegroundColor Yellow

# Execute SQL
$result = Get-Content $tempSQLFile | docker exec -i abena-postgres psql -U abena_user -d abena_ihr

Write-Host ""
Write-Host $result
Write-Host ""

# Clean up temp file
Remove-Item $tempSQLFile -ErrorAction SilentlyContinue

# Verify tables exist
Write-Host "Verifying tables..." -ForegroundColor Yellow
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "\dt"

Write-Host ""
Write-Host "Checking user data..." -ForegroundColor Yellow
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT id, email, role, substring(password, 1, 10) as pwd FROM users;"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Database Schema Ready!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Test accounts created:" -ForegroundColor Yellow
Write-Host "  Provider: dr.johnson@abena.com / Abena2024Secure" -ForegroundColor Cyan
Write-Host "  Patient: john.doe@example.com / Abena2024Secure" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Passwords are currently plain text!" -ForegroundColor Red
Write-Host "They will be migrated to bcrypt in the next step." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next step: Run password migration" -ForegroundColor Green
Write-Host "  .\migrate-passwords-clean.ps1" -ForegroundColor Cyan
Write-Host ""

