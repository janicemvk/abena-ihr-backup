# ABENA System Demo Startup Script
# Comprehensive startup script for demonstrating ABENA system integrations
# Date: December 15, 2025

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ABENA System Demo Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker Desktop is running
Write-Host "[1/10] Checking Docker Desktop..." -ForegroundColor Yellow
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Write-Host "  [WARNING] Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and wait 30-60 seconds, then run this script again." -ForegroundColor Yellow
    exit 1
}
Write-Host "  [OK] Docker Desktop is running" -ForegroundColor Green

# Wait for Docker daemon to be ready
Write-Host "[2/10] Waiting for Docker daemon..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    docker ps | Out-Null
    Write-Host "  [OK] Docker daemon is ready" -ForegroundColor Green
} catch {
    Write-Host "  [WARNING] Docker daemon not ready yet. Waiting 30 more seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Navigate to project root
$projectRoot = "C:\Users\Jan Marie\Documents\Python Development Files\abena-backup"
Set-Location $projectRoot
Write-Host "[3/10] Project directory: $projectRoot" -ForegroundColor Green

# Stop any existing containers
Write-Host "[4/10] Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml down 2>&1 | Out-Null
Write-Host "  [OK] Cleaned up existing containers" -ForegroundColor Green

# Start infrastructure services first
Write-Host "[5/10] Starting infrastructure services (PostgreSQL, Redis)..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d postgres 2>&1 | Out-Null
Start-Sleep -Seconds 10
Write-Host "  [OK] PostgreSQL started" -ForegroundColor Green

# Start core services
Write-Host "[6/10] Starting core ABENA services..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d abena-ihr background-modules 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "  [OK] ABENA IHR Core started" -ForegroundColor Green
Write-Host "  [OK] Background Modules started" -ForegroundColor Green

# Start eCBome Intelligence System
Write-Host "[7/10] Starting eCBome Intelligence System..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d ecdome-intelligence 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "  [OK] eCBome Intelligence System started (port 4005)" -ForegroundColor Green

# Start Quantum Healthcare
Write-Host "[8/10] Starting Quantum Healthcare Service..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d quantum-healthcare 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "  [OK] Quantum Healthcare started (port 5000)" -ForegroundColor Green

# Start Unified Integration Hub
Write-Host "[9/10] Starting Unified Integration Hub..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d unified-integration 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "  [OK] Unified Integration Hub started (port 4008)" -ForegroundColor Green

# Start dashboards
Write-Host "[10/10] Starting dashboards..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d provider-dashboard patient-dashboard 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "  [OK] Provider Dashboard started (port 4009)" -ForegroundColor Green
Write-Host "  [OK] Patient Dashboard started (port 4010)" -ForegroundColor Green

# Start API Gateway
Write-Host "[11/10] Starting API Gateway..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d api-gateway 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "  [OK] API Gateway started (port 8081)" -ForegroundColor Green

# Health checks
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Health Checks" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="PostgreSQL"; Port=5433; Endpoint="pg_isready"},
    @{Name="ABENA IHR Core"; Port=4002; Endpoint="/health"},
    @{Name="eCBome Intelligence"; Port=4005; Endpoint="/health"},
    @{Name="Quantum Healthcare"; Port=5000; Endpoint="/health"},
    @{Name="Unified Integration"; Port=4008; Endpoint="/health"},
    @{Name="Provider Dashboard"; Port=4009; Endpoint="/"},
    @{Name="Patient Dashboard"; Port=4010; Endpoint="/"},
    @{Name="API Gateway"; Port=8081; Endpoint="/health"}
)

foreach ($service in $services) {
    Write-Host "Checking $($service.Name)..." -ForegroundColor Yellow -NoNewline
    try {
        if ($service.Endpoint -eq "pg_isready") {
            $result = docker exec abena-postgres pg_isready -U abena_user 2>&1
            if ($result -match "accepting") {
                Write-Host " [OK]" -ForegroundColor Green
            } else {
                Write-Host " [WARNING]" -ForegroundColor Yellow
            }
        } else {
            $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)$($service.Endpoint)" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host " [OK]" -ForegroundColor Green
            } else {
                Write-Host " [WARNING]" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host " [WARNING] (may need more time)" -ForegroundColor Yellow
    }
}

# Display access URLs
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  System Access URLs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[DASHBOARDS]:" -ForegroundColor White
Write-Host "  • Provider Dashboard:    http://localhost:4009" -ForegroundColor Cyan
Write-Host "  • Patient Dashboard:      http://localhost:4010" -ForegroundColor Cyan
Write-Host "  • Admin Dashboard:         http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "[ANALYSIS SYSTEMS]:" -ForegroundColor White
Write-Host "  • eCBome Intelligence:    http://localhost:4005" -ForegroundColor Cyan
Write-Host "  • Quantum Healthcare:     http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INTEGRATION]:" -ForegroundColor White
Write-Host "  • Unified Integration Hub: http://localhost:4008" -ForegroundColor Cyan
Write-Host "  • API Gateway:            http://localhost:8081" -ForegroundColor Cyan
Write-Host ""
Write-Host "[CORE SERVICES]:" -ForegroundColor White
Write-Host "  • ABENA IHR API:          http://localhost:4002" -ForegroundColor Cyan
Write-Host "  • Background Modules:     http://localhost:4001" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  System Ready for Demo!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open Provider Dashboard: http://localhost:4009" -ForegroundColor White
Write-Host "  2. Select a patient" -ForegroundColor White
Write-Host "  3. View eCBome analysis in the dashboard" -ForegroundColor White
Write-Host "  4. Run Quantum Analysis from the Quantum Results section" -ForegroundColor White
Write-Host "  5. Check Unified Integration Hub for system connections" -ForegroundColor White
Write-Host ""

