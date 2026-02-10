# 🚀 ABENA Database Migration Guide
## From Local to Live Server

---

## ✅ SUCCESS! Your Database is Ready

I've successfully exported your entire working ABENA database from Docker!

### 📦 What Was Exported

```
✅ Complete database backup created!

📊 Database Contents:
   - 78 tables (all schemas)
   - 8 patients with full data
   - All sequences and relationships
   - 309 KB uncompressed
   - 48 KB compressed
```

---

## 🎯 Why This Approach is BEST

### ❌ Old Way (Manual SQL Files)
- Need to run 5 different SQL files
- Files might be out of sync
- Manual sequence updates needed
- Risk of missing data
- Complex troubleshooting

### ✅ New Way (Database Export/Import)
- **Single file** with everything
- **Exact copy** of working system
- **All data included** (8 patients ready for demo)
- **Automatic sequences** (no manual updates)
- **One command** to import

---

## 📁 Exported Files Location

Your files are in: `database_exports/`

```
1. abena_database_full_20251010_153829.sql.gz (48 KB) ⭐ Use this one
2. abena_database_full_20251010_153829.sql (309 KB) - Uncompressed
3. export_manifest_20251010_153829.txt - Documentation
```

**Recommended**: Use the `.gz` compressed file (48 KB) for faster transfer!

---

## 🚀 Step-by-Step: Migrate to Live Server

### Step 1: Transfer Files to Live Server

```bash
# Copy the compressed database dump
scp database_exports/abena_database_full_20251010_153829.sql.gz user@your-live-server:/path/to/abena/

# Copy the import script
scp import-live-database.sh user@your-live-server:/path/to/abena/

# Copy docker-compose.yml (if needed)
scp docker-compose.yml user@your-live-server:/path/to/abena/
```

### Step 2: SSH to Live Server

```bash
ssh user@your-live-server
cd /path/to/abena
```

### Step 3: Run Import Script

```bash
# Make script executable
chmod +x import-live-database.sh

# Run import (it will ask for database credentials)
./import-live-database.sh abena_database_full_20251010_153829.sql.gz
```

**The script will:**
1. ✅ Extract the compressed file automatically
2. ✅ Test database connection
3. ✅ Backup existing database (if any)
4. ✅ Drop and recreate database
5. ✅ Import all data and schemas
6. ✅ Update sequences automatically
7. ✅ Verify import (check patient count)
8. ✅ Give you the DATABASE_URL to use

### Step 4: Update Docker Configuration

The import script will show you something like:
```yaml
DATABASE_URL=postgresql://your_user:your_password@your_host:5432/abena_ihr
```

Copy that and update your `docker-compose.yml`:

```bash
nano docker-compose.yml

# Find all instances of DATABASE_URL and replace with the new one
# Use Ctrl+W to search, Ctrl+O to save, Ctrl+X to exit
```

### Step 5: Restart ABENA Services

```bash
# Restart all services to use new database
docker-compose restart

# Or do a full restart
docker-compose down
docker-compose up -d

# Check status
docker-compose ps
```

### Step 6: Verify Everything Works

```bash
# Test demo orchestrator
curl http://localhost:4020/api/demo/status

# Test ABENA IHR health
curl http://localhost:4002/health

# Open in browser
# http://your-server-ip:4020
```

---

## 🔧 Using Docker-Based Import (Alternative)

If your live server also uses Docker PostgreSQL:

### Option 1: Import to Docker PostgreSQL

```bash
# On live server with Docker running
cd /path/to/abena

# Extract the dump
gunzip abena_database_full_20251010_153829.sql.gz

# Import directly to Docker container
docker exec -i abena-postgres psql -U abena_user -d postgres < abena_database_full_20251010_153829.sql

# Or create fresh database first
docker exec abena-postgres psql -U abena_user -d postgres -c "DROP DATABASE IF EXISTS abena_ihr;"
docker exec abena-postgres psql -U abena_user -d postgres -c "CREATE DATABASE abena_ihr;"
docker exec -i abena-postgres psql -U abena_user -d abena_ihr < abena_database_full_20251010_153829.sql
```

### Option 2: Use Docker Volume

```bash
# Copy SQL file into Docker container
docker cp abena_database_full_20251010_153829.sql.gz abena-postgres:/tmp/

# Execute inside container
docker exec abena-postgres bash -c "cd /tmp && gunzip abena_database_full_20251010_153829.sql.gz"
docker exec abena-postgres psql -U abena_user -d postgres -f /tmp/abena_database_full_20251010_153829.sql
```

---

## ✅ What You Get After Import

Once imported, your live server will have:

### Database Contents:
- ✅ **78 tables** - All schemas and structures
- ✅ **8 patients** - Ready for demo
- ✅ **Complete data** - Clinical records, appointments, etc.
- ✅ **Sequences** - Auto-incrementing IDs set correctly
- ✅ **Relationships** - Foreign keys and constraints
- ✅ **Exact copy** of working local system

### Demo Data Includes:
- ✅ Patient records with demographics
- ✅ Provider information (Dr. Emily Johnson)
- ✅ Appointments and schedules
- ✅ Clinical data and observations
- ✅ Prescriptions and medications
- ✅ Lab results and biomarkers
- ✅ User accounts (patients and providers)
- ✅ Authentication credentials

---

## 🔍 Verification Checklist

After import, verify:

### 1. Database Level
```bash
# Check patient count
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT COUNT(*) FROM patients;"
# Should return: 8

# Check table count
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
# Should return: 78

# Check providers
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT first_name, last_name, email FROM providers;"
# Should show: Dr. Emily Johnson
```

### 2. Service Level
```bash
# ABENA IHR health check
curl http://localhost:4002/health
# Should return: {"status":"healthy", ...}

# Demo orchestrator status
curl http://localhost:4020/api/demo/status
# Should return: {"status":"idle", ...}
```

### 3. Browser Level
- [ ] Demo orchestrator loads: `http://your-server:4020`
- [ ] Shows 3 demo scenarios
- [ ] Telemedicine works: `http://your-server:8000`
- [ ] Provider dashboard works: `http://your-server:4009`
- [ ] Patient dashboard works: `http://your-server:4010`

---

## 🆘 Troubleshooting

### Issue: Import Script Can't Connect

**Error**: "Cannot connect to database"

**Solutions**:
1. Check PostgreSQL is running: `systemctl status postgresql` or `docker ps | grep postgres`
2. Verify host/port: Usually `localhost:5432`
3. Check firewall: `sudo ufw status`
4. Test connection manually: `psql -h localhost -U abena_user -d postgres`

### Issue: Permission Denied

**Error**: "permission denied for database"

**Solutions**:
1. Make sure you're using a superuser or database owner
2. Grant permissions: `GRANT ALL ON DATABASE abena_ihr TO abena_user;`
3. Try with postgres user: `sudo -u postgres psql`

### Issue: Database Already Exists

**Error**: "database already exists"

**Solutions**:
The import script handles this automatically by:
1. Creating backup of existing database
2. Dropping old database
3. Creating fresh database
4. Importing new data

If manual: 
```bash
psql -U abena_user -d postgres -c "DROP DATABASE abena_ihr;"
psql -U abena_user -d postgres -c "CREATE DATABASE abena_ihr;"
```

### Issue: Services Can't Connect After Import

**Error**: Services show database connection errors

**Solutions**:
1. Update DATABASE_URL in docker-compose.yml
2. Restart services: `docker-compose restart`
3. Check environment variables: `docker exec service-name env | grep DATABASE`
4. Verify database is accessible from containers

---

## 📊 File Size Comparison

| Method | Size | Transfer Time* | Setup Time |
|--------|------|---------------|------------|
| **Compressed Dump** | 48 KB | < 1 second | 2 minutes |
| Manual SQL Files | ~350 KB | 3-5 seconds | 15-30 minutes |
| Full Docker Volume | ~100 MB | 30-60 seconds | 5 minutes |

*Approximate on 10 Mbps connection

---

## 🎯 Summary

### What We Created:

1. ✅ **export-local-database.sh** - Export from local Docker
2. ✅ **import-live-database.sh** - Import to live server  
3. ✅ **Database dump** - 48 KB compressed, complete backup
4. ✅ **Manifest file** - Documentation of export

### What You Need to Do:

1. ✅ Transfer files to live server (3 files, ~50 KB total)
2. ✅ Run import script (one command)
3. ✅ Update docker-compose.yml (copy DATABASE_URL)
4. ✅ Restart services (docker-compose restart)
5. ✅ Test demo (open browser)

### Time Required:

- **File transfer**: < 1 minute
- **Import process**: 2-3 minutes
- **Service restart**: 1-2 minutes
- **Total**: ~5 minutes! 🚀

---

## 🔐 Security Notes

### Before Going Live:

1. ⚠️ **Change passwords** - Don't use "abena_password" on live
2. ⚠️ **Update secrets** - Generate new JWT secrets
3. ⚠️ **Configure SSL** - Use HTTPS for production
4. ⚠️ **Restrict access** - Configure firewall properly
5. ⚠️ **Backup regularly** - Schedule automated backups

### Database Credentials:

The export script strips:
- ❌ Ownership information (--no-owner)
- ❌ Privilege grants (--no-privileges)
- ✅ Schema and data (included)
- ✅ Sequences (included)

You can use different credentials on live server!

---

## 📞 Need Help?

### Common Questions:

**Q: Can I import to different PostgreSQL versions?**  
A: Yes! Export is compatible with PostgreSQL 13, 14, 15+

**Q: Will this work with AWS RDS / Cloud databases?**  
A: Yes! Just provide the RDS endpoint as the host

**Q: Can I schedule regular exports?**  
A: Yes! Add to cron: `0 2 * * * /path/to/export-local-database.sh`

**Q: How do I export again after making changes?**  
A: Just run: `./export-local-database.sh` - It creates timestamped files

---

**Created**: October 10, 2025  
**Export Created**: abena_database_full_20251010_153829.sql.gz  
**Status**: ✅ Ready for migration  
**Next Step**: Transfer to live server and import!

---

## 🎉 Final Note

This is **much better** than manually running SQL files because:
- ✅ Single source of truth (your working database)
- ✅ No version mismatches
- ✅ No missing data
- ✅ Faster and simpler
- ✅ Includes sequences and relationships
- ✅ Automated verification

**Your local system is working perfectly** - now you can clone it exactly to your live server! 🚀

