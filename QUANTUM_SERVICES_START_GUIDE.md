# Quantum Healthcare Services - Start Guide

**Quick Start Guide for Running Quantum Healthcare and Provider Dashboard**

---

## 🚀 Step-by-Step Startup Instructions

### Prerequisites Check

Before starting, ensure you have:
- ✅ Docker Desktop running
- ✅ Docker Compose installed
- ✅ All ABENA services configured

---

## Step 1: Start Quantum Healthcare Service

### Option A: Start Only Quantum Healthcare (Recommended for Testing)

```powershell
# Navigate to project root
cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-backup"

# Start quantum healthcare service
docker-compose up -d quantum-healthcare
```

### Option B: Start All Services (Including Quantum Healthcare)

```powershell
# Start all ABENA services including quantum healthcare
docker-compose up -d
```

### Verify Quantum Healthcare is Running

```powershell
# Check if container is running
docker ps | findstr quantum-healthcare

# Check logs
docker logs abena-quantum-healthcare

# Test health endpoint
curl http://localhost:5000/health

# Or in PowerShell:
Invoke-RestMethod -Uri http://localhost:5000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "quantum-healthcare",
  "database": "connected",
  "timestamp": "2025-12-05T..."
}
```

---

## Step 2: Start Provider Dashboard

### Start Provider Dashboard Service

```powershell
# Navigate to project root (if not already there)
cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-backup"

# Start provider dashboard
docker-compose up -d provider-dashboard
```

### Verify Provider Dashboard is Running

```powershell
# Check if container is running
docker ps | findstr provider-dashboard

# Check logs
docker logs abena-provider-dashboard

# Test dashboard (should return HTML)
Invoke-WebRequest -Uri http://localhost:4009 -UseBasicParsing
```

**Expected:** HTTP 200 response with HTML content

---

## 🔍 Troubleshooting

### Issue 1: Container Won't Start

**Symptoms:**
```
Error: Cannot connect to Docker daemon
```

**Solution:**
```powershell
# Check if Docker Desktop is running
Get-Process "Docker Desktop" -ErrorAction SilentlyContinue

# If not running, start Docker Desktop manually
# Then wait 30-60 seconds for it to fully start
```

---

### Issue 2: Port Already in Use

**Symptoms:**
```
Error: bind: address already in use
```

**Solution:**
```powershell
# Check what's using port 5000 (Quantum Healthcare)
netstat -ano | findstr :5000

# Check what's using port 4009 (Provider Dashboard)
netstat -ano | findstr :4009

# Stop the conflicting process or change port in docker-compose.yml
```

---

### Issue 3: Quantum Healthcare Can't Connect to Database

**Symptoms:**
```
Database connection failed
```

**Solution:**
```powershell
# Ensure PostgreSQL is running
docker ps | findstr postgres

# If not running, start it first
docker-compose up -d postgres

# Wait for postgres to be healthy (check logs)
docker logs abena-postgres

# Then start quantum healthcare
docker-compose up -d quantum-healthcare
```

---

### Issue 4: Provider Dashboard Can't Connect to Quantum API

**Symptoms:**
```
Failed to fetch quantum analysis
```

**Solution:**
```powershell
# 1. Verify quantum healthcare is running
docker ps | findstr quantum-healthcare

# 2. Test quantum API directly
Invoke-RestMethod -Uri http://localhost:5000/api/demo-results

# 3. Check if services are on same network
docker network inspect abena-network

# 4. Verify environment variables in provider dashboard
docker exec abena-provider-dashboard env | findstr QUANTUM
```

---

### Issue 5: Authentication Errors

**Symptoms:**
```
401 Unauthorized
Invalid token
```

**Solution:**
```powershell
# 1. Ensure auth service is running
docker-compose up -d auth-service

# 2. Get a valid token (login to ABENA IHR)
# Use the login endpoint to get a token
$body = @{
    email = "dr.johnson@abena.com"
    password = "SecureP@ss123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/auth/login" `
    -Method Post -Body $body -ContentType "application/json"

# Store token (for testing)
$token = $response.access_token
Write-Host "Token: $token"

# 3. Test quantum API with token
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/analyze" `
    -Method Post `
    -Headers $headers `
    -Body '{"patient_id":"123"}' `
    -ContentType "application/json"
```

---

## 📋 Complete Startup Sequence

For a complete startup of all required services:

```powershell
# 1. Navigate to project root
cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-backup"

# 2. Start infrastructure services first
docker-compose up -d postgres redis

# 3. Wait for postgres to be healthy (check logs)
Start-Sleep -Seconds 10
docker logs abena-postgres --tail 20

# 4. Start authentication service
docker-compose up -d auth-service

# 5. Start ABENA IHR (needed for patient data)
docker-compose up -d abena-ihr

# 6. Start eCDome Intelligence (needed for biomarkers)
docker-compose up -d ecdome-intelligence

# 7. Start Quantum Healthcare
docker-compose up -d quantum-healthcare

# 8. Start Provider Dashboard
docker-compose up -d provider-dashboard

# 9. Verify all services are running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## ✅ Verification Checklist

After starting services, verify everything is working:

- [ ] **PostgreSQL** is running and healthy
  ```powershell
  docker exec abena-postgres pg_isready -U abena_user
  ```

- [ ] **Redis** is running
  ```powershell
  docker exec abena-redis redis-cli ping
  # Should return: PONG
  ```

- [ ] **Auth Service** is accessible
  ```powershell
  Invoke-RestMethod -Uri http://localhost:3001/health
  ```

- [ ] **ABENA IHR** is accessible
  ```powershell
  Invoke-RestMethod -Uri http://localhost:4002/health
  ```

- [ ] **Quantum Healthcare** is accessible
  ```powershell
  Invoke-RestMethod -Uri http://localhost:5000/health
  ```

- [ ] **Provider Dashboard** is accessible
  ```powershell
  $response = Invoke-WebRequest -Uri http://localhost:4009 -UseBasicParsing
  $response.StatusCode  # Should be 200
  ```

---

## 🌐 Access URLs

Once services are running, access them at:

- **Provider Dashboard:** http://localhost:4009
- **Quantum Healthcare API:** http://localhost:5000
- **Quantum via Gateway:** http://localhost:8081/api/v1/quantum/
- **ABENA IHR API:** http://localhost:4002
- **Auth Service:** http://localhost:3001

---

## 🔧 Quick Commands Reference

```powershell
# View all running containers
docker ps

# View logs (follow)
docker logs -f abena-quantum-healthcare
docker logs -f abena-provider-dashboard

# Restart a service
docker-compose restart quantum-healthcare
docker-compose restart provider-dashboard

# Stop services
docker-compose stop quantum-healthcare provider-dashboard

# Remove containers (keeps data)
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build quantum-healthcare
```

---

## 📝 Next Steps After Starting

1. **Open Provider Dashboard:**
   - Navigate to http://localhost:4009
   - Login with provider credentials

2. **Select a Patient:**
   - Use the patient selector
   - Choose any patient from the list

3. **Run Quantum Analysis:**
   - Scroll to "Quantum Health Analysis" section
   - Click "Run Quantum Analysis" button
   - Wait for analysis to complete (10-30 seconds)
   - View results

4. **View Analysis History:**
   - Scroll to "Recent Analyses" section
   - Click on any previous analysis to view details

---

## 🆘 Still Having Issues?

### Check Service Logs

```powershell
# Quantum Healthcare logs
docker logs abena-quantum-healthcare --tail 50

# Provider Dashboard logs
docker logs abena-provider-dashboard --tail 50

# Check for errors
docker logs abena-quantum-healthcare 2>&1 | Select-String -Pattern "error|Error|ERROR|failed|Failed"
```

### Verify Network Connectivity

```powershell
# Check if services can communicate
docker exec abena-quantum-healthcare ping -c 2 postgres
docker exec abena-quantum-healthcare ping -c 2 abena-ihr
docker exec abena-provider-dashboard ping -c 2 quantum-healthcare
```

### Check Environment Variables

```powershell
# Quantum Healthcare env vars
docker exec abena-quantum-healthcare env | findstr -i "DATABASE\|AUTH\|ECDOME\|IHR"

# Provider Dashboard env vars
docker exec abena-provider-dashboard env | findstr -i "QUANTUM\|API"
```

---

**Last Updated:** December 5, 2025  
**Status:** Ready for Use



