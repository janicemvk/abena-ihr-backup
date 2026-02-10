# ABENA System Integration Architecture
## Complete Connection Map for Demo

**Date:** December 15, 2025  
**Status:** ✅ Ready for Demonstration

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                              │
│                                                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Provider         │  │ Patient          │  │ Admin             │   │
│  │ Dashboard        │  │ Dashboard        │  │ Dashboard         │   │
│  │ Port: 4009       │  │ Port: 4010       │  │ Port: 8080        │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘   │
│           │                     │                      │              │
└───────────┼─────────────────────┼──────────────────────┼──────────────┘
            │                     │                      │
            └─────────────────────┼──────────────────────┘
                                  │
            ┌─────────────────────┴──────────────────────┐
            │         API GATEWAY (Port 8081)             │
            │  • Authentication & Authorization           │
            │  • Request Routing                          │
            │  • Rate Limiting                            │
            └─────────────────────┬──────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────▼────────┐    ┌───────────▼──────────┐   ┌─────────▼──────────┐
│ Unified        │    │ eCBome Intelligence  │   │ Quantum Healthcare │
│ Integration    │    │ Port: 4005           │   │ Port: 5000         │
│ Hub            │    │                      │   │                    │
│ Port: 4008     │    │ • 12-Module Analysis │   │ • Quantum Analysis │
│                │    │ • Pattern Recognition│   │ • Risk Assessment  │
│ • Cross-module │    │ • Predictive Alerts  │   │ • Drug Interactions│
│   Sync         │    │ • Timeline Analysis  │   │ • Recommendations  │
│ • Data Bridge  │    └───────────┬──────────┘   └─────────┬──────────┘
│ • Event Bus    │                │                        │
└───────┬────────┘                │                        │
        │                         │                        │
        └─────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   ABENA IHR CORE API      │
                    │   Port: 4002              │
                    │                           │
                    │ • Patient Data            │
                    │ • Clinical Records        │
                    │ • Authentication          │
                    │ • Data Management         │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Background Modules      │
                    │   Port: 4001             │
                    │                           │
                    │ • 12 Core Modules         │
                    │ • Real-time Processing    │
                    │ • Data Aggregation        │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   PostgreSQL Database     │
                    │   Port: 5433              │
                    │                           │
                    │ • Patient Records         │
                    │ • Analysis Results        │
                    │ • System Data             │
                    └───────────────────────────┘
```

---

## 🔗 Integration Connections

### 1. **Provider Dashboard ↔ eCBome Intelligence**

**Connection Type:** REST API + WebSocket  
**Purpose:** Display real-time eCBome analysis and 12-module data

**Data Flow:**
```
Provider Dashboard (4009)
    ↓ HTTP GET /api/ecbome/analysis
eCBome Intelligence (4005)
    ↓ Returns: 12-module analysis, timeline data, component scores
Provider Dashboard
    ↓ Displays: eCBome Components, Timeline, Module Analysis
```

**Key Components:**
- `EcdomeComponents.js` - Shows 12-module breakdown
- `EcdomeTimeline.js` - 24-hour activity timeline
- `ModuleAnalysis.js` - Detailed module analysis

---

### 2. **Provider Dashboard ↔ Quantum Healthcare**

**Connection Type:** REST API  
**Purpose:** Run quantum analysis and display results

**Data Flow:**
```
Provider Dashboard (4009)
    ↓ POST /api/analyze (with patient data)
Quantum Healthcare (5000)
    ↓ Processes: Patient symptoms, biomarkers, medications
    ↓ Returns: Quantum health score, system balance, recommendations
Provider Dashboard
    ↓ Displays: QuantumResults component
```

**Key Components:**
- `QuantumResults.js` - Quantum analysis display
- `quantumService.js` - API client for quantum service

**Integration Points:**
- Patient data from ABENA IHR Core
- Biomarker data from eCBome Intelligence
- Results stored in PostgreSQL

---

### 3. **Quantum Healthcare ↔ eCBome Intelligence**

**Connection Type:** REST API  
**Purpose:** Get biomarker and endocannabinoid system data

**Data Flow:**
```
Quantum Healthcare (5000)
    ↓ GET /api/biomarkers/{patientId}
eCBome Intelligence (4005)
    ↓ Returns: Endocannabinoid levels, receptor activity, module scores
Quantum Healthcare
    ↓ Uses in quantum analysis calculations
```

**Environment Variables:**
- `ECDOME_API=http://ecdome-intelligence:4005`

---

### 4. **Quantum Healthcare ↔ ABENA IHR Core**

**Connection Type:** REST API  
**Purpose:** Get patient data, medications, symptoms

**Data Flow:**
```
Quantum Healthcare (5000)
    ↓ GET /api/v1/patients/{patientId}
ABENA IHR Core (4002)
    ↓ Returns: Patient demographics, medications, symptoms, history
Quantum Healthcare
    ↓ Uses in quantum analysis
```

**Environment Variables:**
- `ABENA_IHR_API=http://abena-ihr:4002`

---

### 5. **Unified Integration Hub ↔ All Systems**

**Connection Type:** REST API + Event Bus  
**Purpose:** Coordinate data flow between all systems

**Data Flow:**
```
Unified Integration Hub (4008)
    ↓ Monitors all services
    ↓ Synchronizes data between systems
    ↓ Provides event bus for real-time updates
All Systems
    ↓ Subscribe to events
    ↓ Receive synchronized data
```

**Key Features:**
- Cross-module data synchronization
- Event-driven architecture
- Real-time updates
- Conflict resolution

---

### 6. **Patient Dashboard ↔ All Backend Services**

**Connection Type:** REST API via API Gateway  
**Purpose:** Patient-facing view of their health data

**Data Flow:**
```
Patient Dashboard (4010)
    ↓ GET /api/v1/patient/{id}/dashboard
API Gateway (8081)
    ↓ Routes to appropriate services
ABENA IHR Core / eCBome / Quantum
    ↓ Returns aggregated patient data
Patient Dashboard
    ↓ Displays: Health summary, trends, recommendations
```

---

## 📊 Data Flow Examples

### Example 1: Running Quantum Analysis from Provider Dashboard

```
1. Provider selects patient in Provider Dashboard (4009)
   ↓
2. Provider clicks "Run Quantum Analysis" button
   ↓
3. Provider Dashboard calls Quantum Healthcare API (5000)
   POST /api/analyze
   Body: { patient_id, symptoms, medications }
   ↓
4. Quantum Healthcare fetches patient data from ABENA IHR (4002)
   GET /api/v1/patients/{patient_id}
   ↓
5. Quantum Healthcare fetches biomarker data from eCBome (4005)
   GET /api/biomarkers/{patient_id}
   ↓
6. Quantum Healthcare performs analysis
   - Processes symptoms
   - Analyzes biomarkers
   - Checks drug interactions
   - Calculates quantum health score
   ↓
7. Quantum Healthcare stores results in PostgreSQL
   INSERT INTO quantum_analyses (...)
   ↓
8. Quantum Healthcare returns results to Provider Dashboard
   { quantum_health_score, system_balance, recommendations, ... }
   ↓
9. Provider Dashboard displays results in QuantumResults component
```

### Example 2: Viewing eCBome Analysis

```
1. Provider selects patient in Provider Dashboard (4009)
   ↓
2. Provider Dashboard requests eCBome data
   GET /api/ecbome/analysis/{patient_id}
   ↓
3. eCBome Intelligence (4005) processes request
   - Retrieves patient data from ABENA IHR (4002)
   - Analyzes 12 modules
   - Generates timeline data
   ↓
4. eCBome Intelligence returns data
   { components: {...}, timeline: [...], scores: {...} }
   ↓
5. Provider Dashboard displays:
   - EcdomeComponents: 12-module breakdown
   - EcdomeTimeline: 24-hour activity chart
   - ModuleAnalysis: Detailed module insights
```

---

## 🔐 Authentication Flow

```
User Login
    ↓
Provider/Patient Dashboard
    ↓ POST /api/v1/auth/login
API Gateway (8081)
    ↓ Routes to ABENA IHR Core (4002)
ABENA IHR Core
    ↓ Validates credentials
    ↓ Returns JWT token
Dashboard
    ↓ Stores token in localStorage
    ↓ Uses token for all API calls
```

**Token Usage:**
- All API calls include: `Authorization: Bearer {token}`
- Token validated by each service
- Role-based access control enforced

---

## 🌐 Service URLs for Demo

### Dashboards
- **Provider Dashboard:** http://localhost:4009
- **Patient Dashboard:** http://localhost:4010
- **Admin Dashboard:** http://localhost:8080

### Analysis Systems
- **eCBome Intelligence:** http://localhost:4005
- **Quantum Healthcare:** http://localhost:5000
- **Quantum API:** http://localhost:5000/api

### Integration
- **Unified Integration Hub:** http://localhost:4008
- **API Gateway:** http://localhost:8081

### Core Services
- **ABENA IHR API:** http://localhost:4002
- **Background Modules:** http://localhost:4001

---

## 🎯 Demo Walkthrough

### Step 1: Start All Services
```powershell
.\START_ABENA_DEMO.ps1
```

### Step 2: Open Provider Dashboard
1. Navigate to http://localhost:4009
2. Select a patient (e.g., PAT-001: James Wilson)

### Step 3: View eCBome Analysis
1. Scroll to "eCBome Components" section
2. See 12-module breakdown with scores
3. View "eCBome Timeline" for 24-hour activity
4. Check "Module Analysis" for detailed insights

### Step 4: Run Quantum Analysis
1. Scroll to "Quantum Health Analysis" section
2. Click "Run Quantum Analysis" button
3. Wait 10-30 seconds for analysis
4. View results:
   - Quantum Health Score
   - System Balance
   - Drug Interactions
   - Recommendations

### Step 5: Check Integration Hub
1. Navigate to http://localhost:4008
2. View system connections
3. See real-time data synchronization
4. Monitor cross-module events

### Step 6: Verify Connections
1. Check API Gateway: http://localhost:8081/health
2. Verify eCBome: http://localhost:4005/health
3. Verify Quantum: http://localhost:5000/health
4. Check ABENA IHR: http://localhost:4002/health

---

## 🔧 Troubleshooting Connections

### Issue: Provider Dashboard can't connect to Quantum Healthcare

**Check:**
```powershell
# Verify Quantum Healthcare is running
docker ps | findstr quantum-healthcare

# Test Quantum API directly
Invoke-RestMethod -Uri http://localhost:5000/health

# Check network connectivity
docker network inspect abena-network
```

**Solution:**
- Ensure Quantum Healthcare container is running
- Verify both services are on `abena-network`
- Check firewall settings

### Issue: eCBome data not showing

**Check:**
```powershell
# Verify eCBome Intelligence is running
docker ps | findstr ecdome-intelligence

# Test eCBome API
Invoke-RestMethod -Uri http://localhost:4005/health

# Check Provider Dashboard logs
docker logs abena-provider-dashboard --tail 50
```

**Solution:**
- Restart eCBome Intelligence service
- Verify patient data exists in database
- Check API endpoint configuration

---

## 📝 Integration Status

| Connection | Status | Notes |
|------------|--------|-------|
| Provider Dashboard ↔ eCBome Intelligence | ✅ Active | Real-time data display |
| Provider Dashboard ↔ Quantum Healthcare | ✅ Active | Quantum analysis integration |
| Quantum Healthcare ↔ eCBome Intelligence | ✅ Active | Biomarker data exchange |
| Quantum Healthcare ↔ ABENA IHR Core | ✅ Active | Patient data retrieval |
| Unified Integration Hub ↔ All Systems | ✅ Active | Cross-module synchronization |
| Patient Dashboard ↔ Backend Services | ✅ Active | Via API Gateway |
| Admin Dashboard ↔ All Systems | ✅ Active | System monitoring |

---

**Last Updated:** December 15, 2025  
**System Version:** ABENA IHR v2.1  
**Status:** ✅ Ready for Demonstration








