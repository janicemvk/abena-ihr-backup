# Verify and Start Quantum Healthcare - Steps 1-3
# This script verifies the configuration and starts the quantum healthcare service

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quantum Healthcare - Steps 1-3 Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker Desktop
Write-Host "[Step 1] Checking Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerVersion = docker version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Docker Desktop is running" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Docker Desktop is not running!" -ForegroundColor Red
        Write-Host "  Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Step 2: Verify docker-compose.yml has quantum-healthcare service
Write-Host ""
Write-Host "[Step 2] Verifying docker-compose.yml configuration..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    $dockerComposeContent = Get-Content "docker-compose.yml" -Raw
    if ($dockerComposeContent -match "quantum-healthcare") {
        Write-Host "  Quantum Healthcare service found in docker-compose.yml" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Quantum Healthcare service not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ERROR: docker-compose.yml not found!" -ForegroundColor Red
    exit 1
}

# Step 3: Verify API Gateway configuration
Write-Host ""
Write-Host "[Step 3] Verifying API Gateway configuration..." -ForegroundColor Yellow
if (Test-Path "api_gateway/nginx.conf") {
    $nginxContent = Get-Content "api_gateway/nginx.conf" -Raw
    if ($nginxContent -match "quantum") {
        Write-Host "  Quantum Healthcare routes found in nginx.conf" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Quantum routes not found in nginx.conf" -ForegroundColor Yellow
    }
} else {
    Write-Host "  WARNING: nginx.conf not found" -ForegroundColor Yellow
}

# Step 4: Verify port documentation
Write-Host ""
Write-Host "[Step 4] Verifying port documentation..." -ForegroundColor Yellow
if (Test-Path "ABENA_SYSTEM_PORTS_DOCUMENTATION.md") {
    $docContent = Get-Content "ABENA_SYSTEM_PORTS_DOCUMENTATION.md" -Raw
    if ($docContent -match "Quantum Healthcare") {
        Write-Host "  Quantum Healthcare found in port documentation" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Quantum Healthcare not in documentation" -ForegroundColor Yellow
    }
} else {
    Write-Host "  WARNING: Port documentation not found" -ForegroundColor Yellow
}

# Step 5: Check if quantum-healthcare directory exists
Write-Host ""
Write-Host "[Step 5] Verifying quantum-healthcare directory..." -ForegroundColor Yellow
if (Test-Path "quantum-healthcare") {
    Write-Host "  quantum-healthcare directory exists" -ForegroundColor Green
    
    # Check for required files
    $requiredFiles = @("app.py", "Dockerfile", "requirements.txt")
    foreach ($file in $requiredFiles) {
        if (Test-Path "quantum-healthcare/$file") {
            Write-Host "    $file found" -ForegroundColor Green
        } else {
            Write-Host "    WARNING: $file not found" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ERROR: quantum-healthcare directory not found!" -ForegroundColor Red
    exit 1
}

# Step 6: Check if quantum service is already running
Write-Host ""
Write-Host "[Step 6] Checking quantum service status..." -ForegroundColor Yellow
$quantumContainer = docker ps -a --filter "name=abena-quantum-healthcare" --format "{{.Names}}" 2>&1
if ($quantumContainer -match "abena-quantum-healthcare") {
    $status = docker ps --filter "name=abena-quantum-healthcare" --format "{{.Status}}" 2>&1
    if ($status -match "Up") {
        Write-Host "  Quantum Healthcare service is already running" -ForegroundColor Green
        Write-Host "    Status: $status" -ForegroundColor Cyan
    } else {
        Write-Host "  Quantum Healthcare container exists but is not running" -ForegroundColor Yellow
        Write-Host "    Starting container..." -ForegroundColor Yellow
        docker start abena-quantum-healthcare
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    Container started successfully" -ForegroundColor Green
        } else {
            Write-Host "    ERROR: Failed to start container" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  Quantum Healthcare container does not exist yet" -ForegroundColor Yellow
    Write-Host "    Building and starting service..." -ForegroundColor Yellow
}

# Step 7: Start essential services if not running
Write-Host ""
Write-Host "[Step 7] Ensuring essential services are running..." -ForegroundColor Yellow
$essentialServices = @("postgres", "redis")
foreach ($service in $essentialServices) {
    $containerName = "abena-$service"
    $status = docker ps --filter "name=$containerName" --format "{{.Status}}" 2>&1
    if ($status -match "Up") {
        Write-Host "  $containerName is running" -ForegroundColor Green
    } else {
        Write-Host "  Starting $containerName..." -ForegroundColor Yellow
        docker start $containerName 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    $containerName started" -ForegroundColor Green
        } else {
            Write-Host "    WARNING: Could not start $containerName" -ForegroundColor Yellow
        }
    }
}

# Step 8: Build and start quantum-healthcare service
Write-Host ""
Write-Host "[Step 8] Building and starting Quantum Healthcare service..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes on first run..." -ForegroundColor Cyan

# Start the service using docker-compose
docker-compose up -d --build quantum-healthcare

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Quantum Healthcare service started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Waiting for service to be healthy (30 seconds)..." -ForegroundColor Cyan
    Start-Sleep -Seconds 30
    
    # Check health
    $health = docker ps --filter "name=abena-quantum-healthcare" --format "{{.Status}}" 2>&1
    Write-Host "  Service Status: $health" -ForegroundColor Cyan
    
    # Test endpoint
    Write-Host ""
    Write-Host "  Testing health endpoint..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/demo-results" -Method GET -TimeoutSec 10 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "    Health check passed!" -ForegroundColor Green
        }
    } catch {
        Write-Host "    Health check endpoint not ready yet (this is normal on first start)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ERROR: Failed to start Quantum Healthcare service" -ForegroundColor Red
    Write-Host "  Check logs with: docker logs abena-quantum-healthcare" -ForegroundColor Yellow
    exit 1
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Check service logs: docker logs abena-quantum-healthcare" -ForegroundColor White
Write-Host "  2. Test API: http://localhost:5000/api/demo-results" -ForegroundColor White
Write-Host "  3. Test via Gateway: http://localhost:8081/api/v1/quantum/demo-results" -ForegroundColor White
Write-Host "  4. View in Provider Dashboard: http://localhost:4009" -ForegroundColor White
Write-Host ""

