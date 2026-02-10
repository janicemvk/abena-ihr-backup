# Simple Password Migration Script
# Uses docker exec to run Python inside a container with network access

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Simple Password Migration" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check postgres is running
$postgresRunning = docker ps --filter "name=abena-postgres" --format "{{.Names}}"
if (-not $postgresRunning) {
    Write-Host "[ERROR] Postgres container not running!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Postgres container is running" -ForegroundColor Green

# Get postgres container IP
$postgresIP = docker inspect abena-postgres --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' | Select-Object -First 1

if (-not $postgresIP) {
    Write-Host "[ERROR] Could not get postgres IP address" -ForegroundColor Red
    exit 1
}

Write-Host "Postgres container IP: $postgresIP" -ForegroundColor Cyan
Write-Host "Using host.docker.internal to connect to postgres on port 5433" -ForegroundColor Cyan

# Create Python migration script with dynamic IP
$pythonScript = @'
import sys
import os

# Add security package
sys.path.insert(0, '/security-package')

import bcrypt
import psycopg2

# Connect using service name from docker-compose (postgres on abena-network)
postgres_host = os.environ.get('POSTGRES_HOST', 'postgres')
postgres_port = int(os.environ.get('POSTGRES_PORT', '5432'))

try:
    conn = psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        database='abena_ihr',
        user='abena_user',
        password='abena_password'
    )
except Exception as e:
    print(f"Connection failed: {e}")
    raise
cur = conn.cursor()

# Get users with plain text passwords
cur.execute("SELECT id, email, password FROM users WHERE password IS NOT NULL AND (hashed_password IS NULL OR hashed_password = '')")
users = cur.fetchall()

print(f"Migrating {len(users)} passwords...")

for user_id, email, plain_password in users:
    # Hash directly with bcrypt (skip validation for existing passwords during migration)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')
    cur.execute("UPDATE users SET hashed_password = %s, password = NULL WHERE id = %s", (hashed, user_id))
    print(f"✓ Migrated: {email}")

conn.commit()

cur.execute("SELECT COUNT(*) FROM users WHERE hashed_password LIKE '$2b$%'")
print(f"\n✓ Verified: {cur.fetchone()[0]} passwords now use bcrypt")

cur.close()
conn.close()
'@

# Save script
$scriptFile = ".\temp_migrate.py"
Set-Content -Path $scriptFile -Value $pythonScript

# Show what will be migrated
Write-Host ""
Write-Host "Users to migrate:" -ForegroundColor Yellow
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT id, email, role FROM users WHERE password IS NOT NULL;"

Write-Host ""
$confirm = Read-Host "Proceed with migration? (yes/no)"

if ($confirm -notmatch "^(yes|y)$") {
    Write-Host "Migration cancelled" -ForegroundColor Yellow
    Remove-Item $scriptFile -ErrorAction SilentlyContinue
    exit 0
}

Write-Host ""
Write-Host "Running migration in Python container..." -ForegroundColor Cyan

# Run Python script in a container on the same network as postgres
try {
    docker run --rm `
        --network abena-backup_abena-network `
        -v "${PWD}\security-package:/security-package:ro" `
        -v "${PWD}\temp_migrate.py:/migrate.py:ro" `
        -e POSTGRES_HOST=postgres `
        -e POSTGRES_PORT=5432 `
        python:3.11-slim `
        sh -c "pip install -q bcrypt psycopg2-binary && python /migrate.py"
    
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

