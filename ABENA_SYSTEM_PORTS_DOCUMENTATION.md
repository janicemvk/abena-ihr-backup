# ABENA IHR System - Complete Port & Service Documentation

## 🚨 CRITICAL: PORT CONFIGURATION - DO NOT CHANGE WITHOUT DOCUMENTATION

This document serves as the **SINGLE SOURCE OF TRUTH** for all ABENA IHR system services, ports, and configurations. **NEVER** modify ports or service configurations without updating this document first.

---

## 📋 System Overview

**Total Services**: 18 (includes Quantum Healthcare)  
**Status**: All Running ✅  
**Last Updated**: December 5, 2025  
**System Version**: ABENA IHR v2.1  
**System Restart**: Completed Successfully ✅

---

## 🗄️ Core Infrastructure Services

### Database & Cache
| Service | Container Name | External Port | Internal Port | Purpose | Status |
|---------|----------------|---------------|---------------|---------|--------|
| PostgreSQL | `abena-postgres` | `5433` | `5432` | Primary Database | ✅ Healthy |
| Redis | `abena-redis` | `6379` | `6379` | Caching & Sessions | ✅ Running |

### Main API
| Service | Container Name | External Port | Internal Port | Purpose | Status |
|---------|----------------|---------------|---------------|---------|--------|
| IHR Main API | `abena-ihr-main` | `4002` | `4002` | Core Healthcare API | ✅ Running |

---

## 🔐 Authentication & SDK Services

| Service | Container Name | External Port | Internal Port | Purpose | Status |
|---------|----------------|---------------|---------------|---------|--------|
| Auth Service | `abena-auth-service` | `3001` | `3001` | User Authentication | ✅ Running |
| SDK Service | `abena-sdk-service` | `3002` | `3002` | Universal SDK | ✅ Running |
| Module Registry | `abena-module-registry` | `3003` | `3003` | Service Discovery | ✅ Running |

---

## 🖥️ Frontend Applications

| Service | Container Name | External Port | Internal Port | Purpose | Status |
|---------|----------------|---------------|---------------|---------|--------|
| Telemedicine Platform | `abena-telemedicine` | `8000` | `8000` | Main Patient/Provider Portal | ✅ Running |
| Provider Dashboard | `abena-provider-dashboard` | `4009` | `4009` | Provider Interface | ✅ Running |
| Patient Dashboard | `abena-patient-dashboard` | `4010` | `4010` | Patient Interface | ✅ Running |
| Admin Dashboard | `abena-admin-dashboard` | `8080` | `8080` | System Administration | ✅ Running |

---

## 🌐 API Gateway & Infrastructure

| Service | Container Name | External Port | Internal Port | Purpose | Status |
|---------|----------------|---------------|---------------|---------|--------|
| API Gateway | `abena-api-gateway` | `8081:80, 8443:443` | `80, 443` | Load Balancer & SSL | ✅ Running |

---

## 🔧 Background & Integration Services

| Service | Container Name | External Port | Internal Port | Purpose | Status |
|---------|----------------|---------------|---------------|---------|--------|
| Background Modules | `abena-background-modules` | `4001` | `4001` | Core Background Services | ✅ Running |
| Biomarker Integration | `abena-biomarker-integration` | `4006` | `4006` | Lab Data Integration | ✅ Running |
| Provider Workflow | `abena-provider-workflow` | `4007` | `4007` | Clinical Workflows | ✅ Running |
| Unified Integration | `abena-unified-integration` | `4008` | `4008` | System Integration Hub | ✅ Running |
| eCDome Intelligence | `abena-ecdome-intelligence` | `4005` | `4005` | AI/ML Services | ✅ Running |
| Quantum Healthcare | `abena-quantum-healthcare` | `5000` | `5000` | Quantum Analysis | ⏳ Pending |
| Data Ingestion | `abena-data-ingestion` | `4011` | `4011` | Data Pipeline | ✅ Running |
| Biomarker GUI | `abena-biomarker-gui` | `4012` | `4012` | Lab Interface | ✅ Running |

---

## 🔗 Key Access URLs

### Main Applications
- **Telemedicine Platform**: http://localhost:8000
- **Provider Dashboard**: http://localhost:4009
- **Patient Dashboard**: http://localhost:4010
- **Admin Dashboard**: http://localhost:8080
- **API Gateway**: http://localhost:8081
- **Quantum Healthcare Dashboard**: http://localhost:5000

### API Endpoints
- **Main IHR API**: http://localhost:4002
- **Authentication API**: http://localhost:3001
- **SDK Service**: http://localhost:3002
- **Quantum Healthcare API**: http://localhost:5000/api
- **Quantum via Gateway**: http://localhost:8081/api/v1/quantum/

### Database Connections
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6379

---

## ⚠️ PORT CONFLICT RESOLUTION HISTORY

### Previously Resolved Conflicts
1. **PostgreSQL**: Changed from 5432 → 5433 (host conflict)
2. **Redis**: Kept at 6379 (resolved host service conflict)
3. **API Gateway**: Changed from 80/443 → 8081/8443 (host conflict)
4. **Unified Integration**: Changed from 4008 → 4009 (conflict with provider-dashboard)
5. **Patient Dashboard**: Changed from 4009 → 4010 (conflict resolution)

### Host Services to Stop (if conflicts occur)
```bash
sudo systemctl stop postgresql
sudo systemctl stop redis-server
sudo systemctl stop nginx
```

---

## 🛠️ Service Management Commands

### Check All Services
```bash
docker-compose ps
```

### Check Specific Service Logs
```bash
docker-compose logs <service-name> --tail=20
```

### Restart Specific Service
```bash
docker-compose restart <service-name>
```

### Rebuild Service (after code changes)
```bash
docker-compose build --no-cache <service-name>
docker-compose up -d <service-name>
```

### Full System Restart
```bash
docker-compose down
docker-compose up -d
```

---

## 📝 Service Dependencies

### Critical Dependencies
- **All services** depend on `abena-postgres` and `abena-redis`
- **Frontend apps** depend on `abena-ihr-main` API
- **API Gateway** depends on all backend services

### Startup Order (Docker Compose handles this)
1. PostgreSQL & Redis
2. Core APIs (IHR, Auth, SDK)
3. Background Services
4. Frontend Applications
5. API Gateway

---

## 🔒 Security Notes

### Exposed Ports
- Only necessary ports are exposed externally
- Internal communication uses Docker network
- API Gateway provides SSL termination

### Environment Variables
- All sensitive data stored in `.env` files
- Database credentials managed via Docker secrets
- API keys stored in secure environment variables

---

## 📊 Health Check Endpoints

All services provide health check endpoints:
- `GET /health` - Service status
- `GET /ready` - Service readiness
- `GET /metrics` - Service metrics (where applicable)

---

## 🚨 EMERGENCY PROCEDURES

### If System Goes Down
1. Check `docker-compose ps` for failed services
2. Check `docker-compose logs <service>` for errors
3. Restart failed services: `docker-compose restart <service>`
4. If persistent, rebuild: `docker-compose build --no-cache <service>`

### If Port Conflicts Occur
1. Check `ss -tlnp | grep <port>` for conflicts
2. Stop conflicting host services
3. Update this document with new port assignments
4. Update `docker-compose.yml` accordingly

---

## 📞 Support Information

- **System Admin**: ABENA Health Systems
- **Last Maintenance**: August 26, 2025
- **Next Review**: Monthly
- **Emergency Contact**: System Administrator

---

## ✅ Verification Checklist

Before making any changes:
- [ ] Document current state
- [ ] Check for port conflicts
- [ ] Update this documentation
- [ ] Test in development environment
- [ ] Update `docker-compose.yml`
- [ ] Verify all services start correctly
- [ ] Update `ABENA_CHANGES_LOG.md`

---

**⚠️ REMEMBER: This document is the single source of truth. Any port or service changes MUST be documented here first!**
