# Security Integration Scripts - Quick Guide

## 🚀 Quick Start

I've created automated scripts to help you integrate the security package. You have **three options**:

---

## Option 1: Complete Automated Integration (Recommended)

**Run everything in one go:**

```powershell
.\COMPLETE_SECURITY_INTEGRATION.ps1
```

This will:
- ✅ Execute all steps 1-8
- ✅ Backup your database
- ✅ Migrate passwords
- ✅ Update services
- ✅ Test authentication

**Time:** ~15-20 minutes  
**User Input:** Requires confirmation at key steps

---

## Option 2: Step-by-Step (More Control)

**Run each phase separately:**

### Phase 1: Initial Setup (Steps 1-5)
```powershell
.\integrate-security.ps1
```
What it does:
- ✓ Copies security files
- ✓ Installs dependencies
- ✓ Generates JWT secret
- ✓ Tests security modules
- ✓ Backs up database

### Phase 2: Password Migration (Step 6)
```powershell
.\migrate-passwords.ps1
```
What it does:
- ✓ Runs dry-run migration
- ✓ Shows what will change
- ✓ Asks for confirmation
- ✓ Migrates passwords to bcrypt
- ✓ Verifies migration

### Phase 3: Service Updates (Steps 7-8)
```powershell
.\update-services-security.ps1
```
What it does:
- ✓ Creates security integration module
- ✓ Updates ABENA IHR
- ✓ Restarts services
- ✓ Tests authentication

---

## Option 3: Manual Integration

Follow the detailed guide in:
- `INTEGRATION_PLAN_QUANTUM_SECURITY.md` (comprehensive)
- `QUICK_INTEGRATION_GUIDE.md` (fast-track)

---

## 📋 Scripts Overview

| Script | Purpose | Time | Risk |
|--------|---------|------|------|
| `COMPLETE_SECURITY_INTEGRATION.ps1` | All-in-one | 15-20 min | Low |
| `integrate-security.ps1` | Initial setup | 5-7 min | Very Low |
| `migrate-passwords.ps1` | Password migration | 3-5 min | Low |
| `update-services-security.ps1` | Service updates | 5-10 min | Low |

---

## 🔒 What Gets Changed

### Database
- All passwords migrated from plain text to bcrypt
- Backups created automatically before changes

### Configuration
- JWT secret added to `.env` file
- Security dependencies installed

### Code
- Security integration module created in `abena_ihr/src/`
- Instructions provided for updating `main.py`

### Services
- ABENA IHR gets security middleware
- Rate limiting enabled
- JWT authentication enforced

---

## 🆘 Troubleshooting

### Script Won't Run

```powershell
# Enable script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Dependencies Fail to Install

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install manually
cd security-package
pip install -r requirements.txt
```

### Database Backup Fails

```powershell
# Check if PostgreSQL container is running
docker ps | findstr postgres

# Manual backup
docker exec abena-postgres pg_dump -U abena_user abena_ihr > backup_manual.sql
```

### Migration Fails

```powershell
# Restore from backup
docker-compose down
Get-Content .\backups\backup_pre_security_*.sql | docker exec -i abena-postgres psql -U abena_user -d abena_ihr
docker-compose up -d
```

---

## ✅ Verification Checklist

After running the scripts, verify:

```powershell
# 1. Check security files exist
Test-Path ".\security-package\utils\password_security.py"

# 2. Check JWT secret is set
cat .env | findstr JWT_SECRET_KEY

# 3. Check passwords are hashed
docker exec abena-postgres psql -U abena_user -d abena_ihr -c "SELECT email, substring(hashed_password, 1, 10) FROM users LIMIT 3;"

# 4. Check backups exist
Get-ChildItem .\backups\

# 5. Test authentication
curl -X POST http://localhost:4002/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"dr.johnson@abena.com","password":"Abena2024Secure"}'
```

---

## 📁 Files Created

After running scripts, you'll have:

```
abena-backup/
├── security-package/                    # Security modules
│   ├── utils/
│   ├── middleware/
│   ├── validation/
│   └── ...
├── backups/                             # Database backups
│   ├── backup_pre_security_*.sql
│   └── backup_pre_migration_*.sql
├── abena_ihr/
│   ├── src/
│   │   └── security_integration.py      # New security module
│   └── SECURITY_UPDATE_INSTRUCTIONS.txt # Integration guide
├── integrate-security.ps1               # Phase 1 script
├── migrate-passwords.ps1                # Phase 2 script
├── update-services-security.ps1         # Phase 3 script
└── COMPLETE_SECURITY_INTEGRATION.ps1    # All-in-one script
```

---

## 🎯 Next Steps After Integration

1. **Test user workflows:**
   - Provider login
   - Patient login
   - Appointment booking
   - Data access

2. **Update other services:**
   - auth-service
   - background-modules
   - telemedicine platform
   - frontend apps

3. **Monitor logs:**
   ```powershell
   docker-compose logs -f abena-ihr
   ```

4. **Run tests:**
   ```powershell
   pytest security-package\tests\ -v
   ```

---

## 📚 Documentation

- **Main Guide:** `INTEGRATION_PLAN_QUANTUM_SECURITY.md`
- **Quick Guide:** `QUICK_INTEGRATION_GUIDE.md`
- **Security Details:** `security-package\IMPLEMENTATION_GUIDE.md`
- **Package Overview:** `security-package\README.md`

---

## 🚀 Recommended Approach

**For most users:**

1. Read this README
2. Run: `.\COMPLETE_SECURITY_INTEGRATION.ps1`
3. Follow the prompts
4. Test authentication
5. Update other services as needed

**Estimated total time:** 20-30 minutes

---

## 💡 Tips

- **Always backup first** - Scripts do this automatically
- **Read the output** - Scripts provide detailed feedback
- **Test thoroughly** - Verify each step works
- **Keep backups** - Don't delete backup files
- **Monitor logs** - Watch for errors after integration

---

## ✅ Success Indicators

You'll know it worked when:

- ✓ No plain text passwords in database
- ✓ Login works with hashed passwords
- ✓ JWT tokens are required for API access
- ✓ Rate limiting triggers after many requests
- ✓ Invalid credentials are rejected
- ✓ No security vulnerabilities remain

---

**Ready to secure your ABENA system? Run the script!** 🔒

```powershell
.\COMPLETE_SECURITY_INTEGRATION.ps1
```

---

**Created:** December 5, 2025  
**Version:** 1.0  
**Status:** Ready to Use

