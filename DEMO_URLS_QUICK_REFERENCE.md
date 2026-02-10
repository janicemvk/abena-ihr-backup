# 🎯 ABENA Demo - All Dashboard & System URLs
## Quick Reference Guide

**Last Updated:** December 15, 2025

---

## ✅ Currently Running Services

| Service | URL | Port | Status |
|---------|-----|------|--------|
| **Provider Dashboard** | http://localhost:4009 | 4009 | ✅ Running |
| **eCBome Intelligence** | http://localhost:4005 | 4005 | ✅ Running |

---

## 📊 All Dashboard URLs

### 1. **Provider Dashboard** ✅ RUNNING
**URL:** http://localhost:4009  
**Port:** 4009  
**Container:** abena-provider-dashboard  
**What it shows:**
- Patient selection and management
- Real-time vital signs
- **eCBome Components** (12-module breakdown)
- **eCBome Timeline** (24-hour activity)
- **Quantum Health Analysis** (with "Run Quantum Analysis" button)
- Predictive alerts
- Clinical recommendations

**Status:** ✅ **READY TO SHOW**

---

### 2. **Patient Dashboard** ⏳ NEEDS BUILD
**URL:** http://localhost:4010  
**Port:** 4010  
**Container:** abena-patient-dashboard  
**What it shows:**
- Patient-facing health summary
- Personal health metrics
- eCBome health score
- Health trends

**Note:** Needs build directory. To start:
```powershell
cd "ECDome material 3 folders\Patient interface ecdome monitoring dashboard"
npm run build
cd ..\..\..
docker-compose -f docker-compose.simple.yml up -d patient-dashboard
```

---

### 3. **Admin Dashboard** (Next.js - Provider Admin Staff) ⏳ NEEDS BUILD
**URL:** http://localhost:8080  
**Port:** 8080  
**Container:** abena-admin-dashboard  
**What it shows:**
- User account management
- System configuration
- Data analytics
- Appointment management
- Clinical notes
- Treatment plans
- Quantum analysis monitoring
- Billing & insurance
- Medical coding assistant
- Communication hub
- Patient feedback

**Note:** This is the Next.js admin dashboard copied from `C:\Next-JS\admin 2\Project Admin`.  
**To build and start:**
```powershell
docker-compose -f docker-compose.simple.yml build admin-dashboard
docker-compose -f docker-compose.simple.yml up -d admin-dashboard
```

---

## 🔬 Analysis System URLs

### 4. **eCBome Intelligence System** ✅ RUNNING
**URL:** http://localhost:4005  
**Port:** 4005  
**Container:** abena-ecdome-intelligence  
**What it shows:**
- Standalone eCBome analysis interface
- 12-module analysis dashboard
- Real-time endocannabinoid system monitoring
- Pattern recognition
- Predictive analytics

**Status:** ✅ **READY TO SHOW**

---

### 5. **Quantum Healthcare** ⏳ NEEDS START
**URL:** http://localhost:5000  
**Port:** 5000  
**Container:** abena-quantum-healthcare  
**What it shows:**
- Quantum analysis dashboard
- Quantum health scores
- System balance metrics
- Drug interaction analysis
- Analysis history

**API Endpoints:**
- Health: http://localhost:5000/health
- Demo Results: http://localhost:5000/api/demo-results
- Analyze: http://localhost:5000/api/analyze

**To start:**
```powershell
docker-compose -f docker-compose.simple.yml up -d quantum-healthcare
```

---

## 🔗 Integration & Gateway URLs

### 6. **Unified Integration Hub** ⏳ NEEDS BUILD
**URL:** http://localhost:4008  
**Port:** 4008  
**Container:** abena-unified-integration  
**What it shows:**
- System connection map
- Real-time data flow visualization
- Cross-module synchronization status
- Integration health

**Note:** Needs build directory. May need to build first.

---

### 7. **API Gateway** ⏳ NEEDS START
**URL:** http://localhost:8081  
**Port:** 8081  
**Container:** abena-api-gateway  
**What it shows:**
- API routing
- Service discovery
- Load balancing

**To start:**
```powershell
docker-compose -f docker-compose.simple.yml up -d api-gateway
```

---

## 🎬 Recommended Demo Sequence

### For Quick Demo (What's Currently Running):

1. **Start with Provider Dashboard** (http://localhost:4009) ✅
   - Show patient selection
   - Demonstrate eCBome Components
   - Show eCBome Timeline
   - Run Quantum Analysis (if Quantum service is started)

2. **Show eCBome Intelligence** (http://localhost:4005) ✅
   - Standalone eCBome interface
   - Show 12-module analysis
   - Demonstrate AI insights

3. **Start Quantum Healthcare** (http://localhost:5000)
   ```powershell
   docker-compose -f docker-compose.simple.yml up -d quantum-healthcare
   ```
   - Wait 30 seconds
   - Show Quantum analysis dashboard
   - Demonstrate analysis capabilities

---

## 🚀 Quick Start All Available Services

```powershell
# Start Quantum Healthcare (if not running)
docker-compose -f docker-compose.simple.yml up -d quantum-healthcare

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String -Pattern "dashboard|quantum|ecdome"
```

---

## 📋 Copy-Paste URLs for Demo

```
✅ READY NOW:
Provider Dashboard:     http://localhost:4009
eCBome Intelligence:   http://localhost:4005

⏳ CAN START:
Quantum Healthcare:     http://localhost:5000

⏳ NEEDS BUILD:
Patient Dashboard:      http://localhost:4010
Admin Dashboard:        http://localhost:8080
Unified Integration:    http://localhost:4008
API Gateway:           http://localhost:8081
```

---

## ✅ Verification Commands

```powershell
# Check what's running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test Provider Dashboard
Invoke-WebRequest -Uri http://localhost:4009 -UseBasicParsing

# Test eCBome Intelligence
Invoke-WebRequest -Uri http://localhost:4005 -UseBasicParsing

# Test Quantum Healthcare (after starting)
Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing
```

---

**For your demo, you can show:**
1. ✅ **Provider Dashboard** (http://localhost:4009) - Shows eCBome and Quantum analysis
2. ✅ **eCBome Intelligence** (http://localhost:4005) - Standalone eCBome system
3. ⏳ **Quantum Healthcare** (http://localhost:5000) - Start it with the command above

These three will give you a complete demonstration of the integrated system!


