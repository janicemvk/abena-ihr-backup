# Direct Password Migration - Runs Python from host
# Uses the same connection method as docker exec

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Direct Password Migration" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check postgres is running
$postgresRunning = docker ps --filter "name=abena-postgres" --format "{{.Names}}"
if (-not $postgresRunning) {
    Write-Host "[ERROR] Postgres container not running!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Postgres container is running" -ForegroundColor Green

# Show users to migrate
Write-Host ""
Write-Host "Users to migrate:" -ForegroundColor Yellow
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT id, email, role FROM users WHERE password IS NOT NULL;"

Write-Host ""
$confirm = Read-Host "Proceed with migration? (yes/no)"

if ($confirm -notmatch "^(yes|y)$") {
    Write-Host "Migration cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Migrating passwords..." -ForegroundColor Cyan

# Create Python script that runs inside postgres container
$pythonScript = @'
import sys
import os
import subprocess

# We'll use psql commands to hash passwords
# Get users with plain passwords
import json

# Connect via psql subprocess
users_query = "SELECT id, email, password FROM users WHERE password IS NOT NULL AND (hashed_password IS NULL OR hashed_password = '');"

# We'll hash each password using Python bcrypt and update via psql
import bcrypt

# Get users
import subprocess
result = subprocess.run(
    ['psql', '-U', 'abena_user', '-d', 'abena_ihr', '-t', '-A', '-F', '|', '-c', users_query],
    capture_output=True,
    text=True,
    env=os.environ
)

users = []
for line in result.stdout.strip().split('\n'):
    if line and '|' in line:
        parts = line.split('|')
        if len(parts) >= 3:
            users.append({
                'id': parts[0].strip(),
                'email': parts[1].strip(),
                'password': parts[2].strip()
            })

print(f"Migrating {len(users)} passwords...")

for user in users:
    # Hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(user['password'].encode('utf-8'), salt).decode('utf-8')
    
    # Update via psql
    update_query = f"UPDATE users SET hashed_password = '{hashed}', password = NULL WHERE id = {user['id']};"
    subprocess.run(
        ['psql', '-U', 'abena_user', '-d', 'abena_ihr', '-c', update_query],
        env=os.environ
    )
    print(f"✓ Migrated: {user['email']}")

# Verify
verify_result = subprocess.run(
    ['psql', '-U', 'abena_user', '-d', 'abena_ihr', '-t', '-c', "SELECT COUNT(*) FROM users WHERE hashed_password LIKE '$2b$%';"],
    capture_output=True,
    text=True,
    env=os.environ
)
count = verify_result.stdout.strip()
print(f"\n✓ Verified: {count} passwords now use bcrypt")
'@

# Save script
$scriptFile = ".\temp_direct_migrate.py"
Set-Content -Path $scriptFile -Value $pythonScript

# Run inside postgres container (it should have Python)
Write-Host "Running migration inside postgres container..." -ForegroundColor Cyan

try {
    # Copy script to container
    docker cp $scriptFile abena-postgres:/tmp/migrate.py
    
    # Install bcrypt in container if needed
    docker exec abena-postgres sh -c "pip install bcrypt 2>/dev/null || python3 -m pip install bcrypt 2>/dev/null || echo 'bcrypt check'"
    
    # Run migration
    docker exec -e PGPASSWORD=abena_password abena-postgres python3 /tmp/migrate.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Migration completed!" -ForegroundColor Green
        
        # Verify
        Write-Host ""
        Write-Host "Verifying migration..." -ForegroundColor Yellow
        docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT id, email, role, substring(hashed_password, 1, 20) as hash FROM users WHERE hashed_password IS NOT NULL;"
        
        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host "Migration Successful!" -ForegroundColor Green
        Write-Host "=====================================" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Migration failed" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Migration failed: $_" -ForegroundColor Red
} finally {
    Remove-Item $scriptFile -ErrorAction SilentlyContinue
}

