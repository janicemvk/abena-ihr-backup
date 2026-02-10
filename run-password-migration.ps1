# Wrapper script to run password migration with correct Python path

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Password Migration Runner" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include security-package
$env:PYTHONPATH = "$PWD\security-package;$env:PYTHONPATH"

# Set database URL
$env:DATABASE_URL = "postgresql://abena_user:abena_password@localhost:5433/abena_ihr"

# Check if we have users to migrate
Write-Host "Checking current password status..." -ForegroundColor Yellow
$plainTextCount = docker exec abena-postgres psql -U abena_user -d abena_ihr -t -c "SELECT COUNT(*) FROM users WHERE password IS NOT NULL AND (hashed_password IS NULL OR hashed_password = '');"
$plainTextCount = $plainTextCount.Trim()

Write-Host "Found $plainTextCount users with plain text passwords" -ForegroundColor Cyan
Write-Host ""

if ([int]$plainTextCount -eq 0) {
    Write-Host "[INFO] No plain text passwords to migrate" -ForegroundColor Yellow
    Write-Host "Either passwords are already hashed or no users exist" -ForegroundColor Yellow
    exit 0
}

# Dry run
Write-Host "=== DRY RUN ===" -ForegroundColor Yellow
Write-Host "Showing what will be migrated (no changes made)..." -ForegroundColor Cyan
Write-Host ""

docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT id, email, role, CASE WHEN password IS NOT NULL THEN 'Has plain password' ELSE 'No password' END as status FROM users;"

Write-Host ""
Write-Host "These $plainTextCount password(s) will be migrated to bcrypt" -ForegroundColor Yellow
Write-Host ""

$response = Read-Host "Do you want to proceed with migration? (yes/no)"

if ($response -notmatch "^(yes|y)$") {
    Write-Host "Migration cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "=== ACTUAL MIGRATION ===" -ForegroundColor Green
Write-Host "Migrating passwords to bcrypt..." -ForegroundColor Yellow
Write-Host ""

# Show current status directly
Write-Host ""
Write-Host "Current password status:" -ForegroundColor Cyan
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT id, email, role, CASE WHEN password IS NOT NULL THEN 'Plain text' WHEN hashed_password IS NOT NULL THEN 'Already hashed' ELSE 'No password' END as password_status FROM users;"

# Check if psycopg2 is installed
Write-Host ""
Write-Host "Checking for psycopg2..." -ForegroundColor Yellow
$psycopg2Check = python -c "import psycopg2; print('OK')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing psycopg2..." -ForegroundColor Yellow
    python -m pip install psycopg2-binary
}

# Now let's hash the passwords using Python directly
Write-Host ""
Write-Host "Hashing passwords..." -ForegroundColor Cyan

$pythonScript = @'
import sys
import os

# Add security package to path (from host, use relative path)
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
security_path = os.path.join(script_dir, 'security-package')
if os.path.exists(security_path):
    sys.path.insert(0, security_path)
else:
    # Try current directory
    sys.path.insert(0, os.path.join(os.getcwd(), 'security-package'))

from utils.password_security import PasswordSecurity
import psycopg2

# Connect to database (from host, use 127.0.0.1 and external port)
import os
conn = psycopg2.connect(
    host='127.0.0.1',
    port=5433,  # External port mapped from container
    database='abena_ihr',
    user='abena_user',
    password='abena_password'
)
cur = conn.cursor()

# Get users with plain text passwords
cur.execute("SELECT id, email, password FROM users WHERE password IS NOT NULL AND (hashed_password IS NULL OR hashed_password = '')")
users = cur.fetchall()

print(f"Migrating {len(users)} passwords...")

for user_id, email, plain_password in users:
    # Hash the password
    hashed = PasswordSecurity.hash_password(plain_password)
    
    # Update the user
    cur.execute(
        "UPDATE users SET hashed_password = %s, password = NULL WHERE id = %s",
        (hashed, user_id)
    )
    print(f"✓ Migrated password for: {email}")

# Commit changes
conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM users WHERE hashed_password LIKE '$2b$%'")
bcrypt_count = cur.fetchone()[0]
print(f"\n✓ Verified: {bcrypt_count} passwords now use bcrypt")

cur.close()
conn.close()
'@

# Save Python script
$tempPyFile = ".\temp_migration.py"
Set-Content -Path $tempPyFile -Value $pythonScript

# Copy security package and script to a temp location for docker
Write-Host "Preparing migration environment..." -ForegroundColor Yellow

# Use docker run with Python to execute the migration
# This ensures we can connect to postgres container
Write-Host "Running migration inside Docker container..." -ForegroundColor Cyan

# Create a docker command that runs Python with access to postgres
$dockerMigrationScript = @'
import sys
import os

# Add security package
sys.path.insert(0, '/security-package')

from utils.password_security import PasswordSecurity
import psycopg2

# Connect to postgres container (using service name)
conn = psycopg2.connect(
    host='abena-postgres',
    port=5432,
    database='abena_ihr',
    user='abena_user',
    password='abena_password'
)
cur = conn.cursor()

cur.execute("SELECT id, email, password FROM users WHERE password IS NOT NULL AND (hashed_password IS NULL OR hashed_password = '')")
users = cur.fetchall()

print(f"Migrating {len(users)} passwords...")

for user_id, email, plain_password in users:
    hashed = PasswordSecurity.hash_password(plain_password)
    cur.execute("UPDATE users SET hashed_password = %s, password = NULL WHERE id = %s", (hashed, user_id))
    print(f"✓ Migrated: {email}")

conn.commit()

cur.execute("SELECT COUNT(*) FROM users WHERE hashed_password LIKE '$2b$%'")
print(f"\n✓ Verified: {cur.fetchone()[0]} passwords now use bcrypt")

cur.close()
conn.close()
'@

# Save docker version
$dockerPyFile = ".\temp_docker_migration.py"
Set-Content -Path $dockerPyFile -Value $dockerMigrationScript

# Run using docker exec on postgres container (it has Python)
# Or use a Python container on the same network
Write-Host "Installing Python dependencies in postgres container..." -ForegroundColor Yellow
docker exec abena-postgres sh -c "pip install bcrypt psycopg2-binary 2>/dev/null || echo 'Dependencies check'"

# Fix: Use 127.0.0.1 instead of localhost, and ensure psycopg2-binary is installed
Write-Host "Installing psycopg2-binary..." -ForegroundColor Yellow
python -m pip install psycopg2-binary -q

# Update Python script to use correct connection
$pythonScript = $pythonScript -replace "host='localhost'", "host='127.0.0.1'"
$pythonScript = $pythonScript -replace "port=5432", "port=5433"

# Save updated script
Set-Content -Path $tempPyFile -Value $pythonScript

# Run migration from host
Write-Host "Running migration from host..." -ForegroundColor Cyan
try {
    python $tempPyFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Password migration completed!" -ForegroundColor Green
        
        # Verify
        Write-Host ""
        Write-Host "Verifying migration..." -ForegroundColor Yellow
        docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT id, email, role, substring(hashed_password, 1, 20) as bcrypt_hash FROM users WHERE hashed_password IS NOT NULL;"
        
        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host "Migration Successful!" -ForegroundColor Green
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "All passwords are now securely hashed with bcrypt" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "[ERROR] Migration failed" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Migration failed: $_" -ForegroundColor Red
} finally {
    # Clean up
    Remove-Item $tempPyFile -ErrorAction SilentlyContinue
}

