# 🚀 ABENA Quick Demo Start Guide

**Good Morning!** Here's everything you need to get ABENA ready for demonstration.

---

## ⚡ Quick Start (3 Steps)

### Step 1: Start Docker Desktop
- Ensure Docker Desktop is running
- Wait 30-60 seconds for it to fully start

### Step 2: Run Startup Script
```powershell
cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-backup"
.\START_ABENA_DEMO.ps1
```

### Step 3: Open Dashboards
- **Provider Dashboard:** http://localhost:4009
- **Patient Dashboard:** http://localhost:4010
- **Admin Dashboard:** http://localhost:8080 (Next.js Admin Portal for provider admin staff)

---

## 🔗 System Connections Overview

### Integration Bridge: Unified Integration Hub
**Port:** 4008  
**URL:** http://localhost:4008  
**Purpose:** Connects all systems together

### Key Connections:

1. **eCBome Intelligence System** (Port 4005)
   - Analyzes endocannabinoid system
   - Provides 12-module analysis
   - Connected to: Provider Dashboard, Quantum Healthcare

2. **Quantum Healthcare** (Port 5000)
   - Advanced quantum analysis
   - Uses data from eCBome and ABENA IHR
   - Connected to: Provider Dashboard, eCBome Intelligence

3. **Provider Dashboard** (Port 4009)
   - Clinical interface
   - Displays eCBome and Quantum analysis
   - Connected to: All backend services

4. **Patient Dashboard** (Port 4010)
   - Patient-facing interface
   - Shows health summaries
   - Connected to: ABENA IHR Core

5. **Admin Dashboard** (Port 8080)
   - System administration
   - Monitors all services
   - Connected to: All systems

---

## 📊 Demo Flow

### 1. Show eCBome Analysis
- Open Provider Dashboard
- Select patient (e.g., PAT-001)
- View "eCBome Components" - shows 12-module breakdown
- View "eCBome Timeline" - shows 24-hour activity

### 2. Show Quantum Analysis
- In Provider Dashboard
- Scroll to "Quantum Health Analysis"
- Click "Run Quantum Analysis"
- Show results: scores, interactions, recommendations

### 3. Show Integration
- Open Unified Integration Hub (port 4008)
- Show system connections
- Demonstrate real-time data flow

---

## 🎯 Key Integration Points

| System | Port | Connected To | Purpose |
|--------|------|--------------|---------|
| eCBome Intelligence | 4005 | Provider Dashboard, Quantum | 12-module analysis |
| Quantum Healthcare | 5000 | Provider Dashboard, eCBome, IHR | Quantum analysis |
| Provider Dashboard | 4009 | All systems | Clinical interface |
| Patient Dashboard | 4010 | IHR Core | Patient view |
| Unified Integration | 4008 | All systems | Integration bridge |
| API Gateway | 8081 | All systems | Request routing |

---

## ✅ Verification Checklist

After starting, verify:
- [ ] Provider Dashboard loads: http://localhost:4009
- [ ] Patient Dashboard loads: http://localhost:4010
- [ ] eCBome Intelligence: http://localhost:4005
- [ ] Quantum Healthcare: http://localhost:5000
- [ ] Unified Integration Hub: http://localhost:4008

---

## 📚 Documentation Files

1. **START_ABENA_DEMO.ps1** - Automated startup script
2. **ABENA_SYSTEM_CONNECTIONS.md** - Complete architecture diagram
3. **DEMO_GUIDE.md** - Detailed demo walkthrough
4. **QUICK_DEMO_START.md** - This file (quick reference)

---

## 🆘 Quick Troubleshooting

**Services won't start?**
- Check Docker Desktop is running
- Wait 30 seconds after Docker starts
- Run: `docker ps` to see running containers

**Can't access dashboards?**
- Check ports aren't in use: `netstat -ano | findstr :4009`
- Restart services: `docker-compose restart provider-dashboard`

**Integration not working?**
- Check Unified Integration Hub: http://localhost:4008
- Verify all services are on `abena-network`
- Check logs: `docker logs abena-unified-integration`

---

**Ready to demo!** 🎉

Run `.\START_ABENA_DEMO.ps1` and you're all set!


