# 🚀 ABENA Live Server Deployment Checklist

## Current Status
- ✅ **Local (localhost)**: Working perfectly
- ⚠️ **Live Server**: Demo not working - likely database issues

---

## 🎯 Main Issue: Database Configuration

### Why Demo Isn't Working on Live Server

**Most likely causes (in order of probability):**

1. ❌ **Database not initialized** - Empty database with no demo data
2. ❌ **Wrong connection string** - Services can't connect to database
3. ❌ **Missing environment variables** - Docker containers using wrong config
4. ❌ **SQL files not loaded** - Database schema/data not imported
5. ❌ **Network/firewall issues** - Services can't reach database

---

## 📋 Pre-Deployment Checklist

### Step 1: Database Setup (CRITICAL)

- [ ] **Verify database exists on live server**
  ```bash
  psql -h YOUR_HOST -U YOUR_USER -d postgres -c "\l"
  ```

- [ ] **Create ABENA database if needed**
  ```bash
  psql -h YOUR_HOST -U YOUR_USER -d postgres -c "CREATE DATABASE abena_ihr;"
  ```

- [ ] **Load SQL initialization files** (in this order):
  - [ ] `IHR Database.sql` (main schema - 129 KB)
  - [ ] `ABENA PATIENT DATABASE.sql` (patient data - 35 KB)
  - [ ] `ABENA CLINICAL DATA.sql` (clinical data - 110 KB)
  - [ ] `ABENA BLOCKCHAIN STATUS.sql` (blockchain - 45 KB)
  - [ ] `ABENA IHR.sql` (IHR config - 34 KB)

- [ ] **Verify data loaded**
  ```bash
  psql -h YOUR_HOST -U YOUR_USER -d abena_ihr -c "SELECT COUNT(*) FROM patients;"
  # Should return 8 or more
  ```

### Step 2: Environment Configuration

- [ ] **Update DATABASE_URL in docker-compose.yml**
  ```yaml
  # Change from:
  DATABASE_URL=postgresql://abena_user:abena_password@postgres:5432/abena_ihr
  
  # To your live server:
  DATABASE_URL=postgresql://LIVE_USER:LIVE_PASSWORD@LIVE_HOST:LIVE_PORT/abena_ihr
  ```

- [ ] **Update all services that use database** (check these):
  - [ ] auth-service
  - [ ] abena-ihr
  - [ ] background-modules
  - [ ] business-rules
  - [ ] telemedicine
  - [ ] ecdome-intelligence
  - [ ] biomarker-integration
  - [ ] provider-workflow
  - [ ] unified-integration
  - [ ] data-ingestion

### Step 3: File Transfer

- [ ] **Upload SQL files to live server**
  ```bash
  scp "ABENA PATIENT DATABASE.sql" user@live-server:/path/to/abena/
  scp "IHR Database.sql" user@live-server:/path/to/abena/
  scp "ABENA CLINICAL DATA.sql" user@live-server:/path/to/abena/
  scp "ABENA BLOCKCHAIN STATUS.sql" user@live-server:/path/to/abena/
  scp "ABENA IHR.sql" user@live-server:/path/to/abena/
  ```

- [ ] **Upload docker-compose.yml** with updated config
- [ ] **Upload all service directories**
- [ ] **Upload .env file** (if using environment file)

### Step 4: Network & Security

- [ ] **Open required ports on firewall**
  - [ ] 4020 (Demo Orchestrator)
  - [ ] 8000 (Telemedicine)
  - [ ] 4009 (Provider Dashboard)
  - [ ] 4010 (Patient Dashboard)
  - [ ] 4002 (ABENA IHR API)
  - [ ] 5432/5433 (PostgreSQL - if external)
  - [ ] 6379/6380 (Redis)

- [ ] **Configure SSL/TLS if needed**
- [ ] **Setup domain names** (if using DNS)
- [ ] **Configure reverse proxy** (if using Nginx/Apache)

### Step 5: Docker Setup on Live Server

- [ ] **Install Docker** (if not already installed)
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  ```

- [ ] **Install Docker Compose**
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

- [ ] **Verify installations**
  ```bash
  docker --version
  docker-compose --version
  ```

---

## 🚀 Deployment Steps

### 1. Database Initialization

```bash
# On live server
cd /path/to/abena

# Make setup script executable
chmod +x setup-live-database.sh

# IMPORTANT: Edit the script first to set your database credentials
nano setup-live-database.sh

# Run database setup
./setup-live-database.sh
```

### 2. Update Docker Configuration

```bash
# Update docker-compose.yml with live database credentials
nano docker-compose.yml

# Find all DATABASE_URL entries and update them
# Example:
#   DATABASE_URL=postgresql://your_user:your_password@your_host:5432/abena_ihr
```

### 3. Start Services

```bash
# Pull/build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Verify Services

```bash
# Check demo orchestrator
curl http://localhost:4020/api/demo/status

# Check ABENA IHR health
curl http://localhost:4002/health

# Check logs if issues
docker-compose logs demo-orchestrator
docker-compose logs abena-ihr
```

---

## ✅ Verification Tests

After deployment, test these:

### 1. Database Connection
- [ ] Services can connect to database
- [ ] Database has data (8+ patients)
- [ ] All tables exist and populated

### 2. Demo Orchestrator
- [ ] Page loads: `http://your-server:4020`
- [ ] Shows 3 demo scenarios
- [ ] API returns data: `http://your-server:4020/api/demo/status`

### 3. Main Applications
- [ ] Telemedicine loads: `http://your-server:8000`
- [ ] Provider dashboard loads: `http://your-server:4009`
- [ ] Patient dashboard loads: `http://your-server:4010`
- [ ] eCDome intelligence loads: `http://your-server:4005`

### 4. Backend Services
- [ ] ABENA IHR health check passes
- [ ] Authentication works
- [ ] Demo can fetch patient data
- [ ] All services show in docker ps

---

## 🔧 Troubleshooting

### Demo Not Showing

**Check 1: Database Connection**
```bash
# On live server
docker logs abena-ihr | grep -i "database\|connection\|error"
```

**Check 2: Database Has Data**
```bash
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT COUNT(*) FROM patients;"
```

**Check 3: Environment Variables**
```bash
docker exec abena-demo-orchestrator env | grep DATABASE
```

### Services Can't Connect

**Check 1: Network**
```bash
docker network ls
docker network inspect abena_all_abena-network
```

**Check 2: Service Logs**
```bash
docker-compose logs --tail=50 [service-name]
```

---

## 📊 Current Local vs Live Comparison

### Local (Working) ✅
```yaml
Database Host: postgres (Docker internal)
Database Port: 5433:5432
Database User: abena_user
Database Password: abena_password
Database Name: abena_ihr
Patient Count: 8
Status: All services operational
```

### Live (Need to Configure) ⚠️
```yaml
Database Host: ??? (needs configuration)
Database Port: ??? (needs configuration)
Database User: ??? (needs configuration)
Database Password: ??? (needs configuration)
Database Name: ??? (might not exist)
Patient Count: ??? (probably 0)
Status: Demo not working - needs database setup
```

---

## 🎯 Quick Fix for Live Server

If you just want to get it working quickly:

1. **Run database setup script** (provided: `setup-live-database.sh`)
2. **Update docker-compose.yml** with correct DATABASE_URL
3. **Restart services**: `docker-compose restart`
4. **Test**: Open `http://your-server:4020`

---

## 📝 Important Notes

- **Backup first**: Always backup live database before making changes
- **Test locally first**: Make sure everything works on localhost (✅ Done!)
- **Use secure passwords**: Don't use "abena_password" on live server
- **Monitor logs**: Watch logs during first deployment
- **Document changes**: Update ABENA_CHANGES_LOG.md after deployment

---

**Created**: October 10, 2025  
**Status**: Ready for deployment  
**Local System**: ✅ Verified working  
**Next Step**: Configure live server database

