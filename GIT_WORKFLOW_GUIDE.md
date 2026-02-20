# 🔄 ABENA Git Workflow for Live Deployment

## ✅ What to Commit to Git

### DO Commit (Code & Scripts):
- ✅ All source code and configurations
- ✅ docker-compose.yml
- ✅ Dockerfiles
- ✅ Database setup scripts (.sh files)
- ✅ Documentation files (.md files)
- ✅ SQL schema files (original 5 files)
- ✅ package.json files
- ✅ Requirements files

### DON'T Commit (Data & Secrets):
- ❌ database_exports/ folder (48 KB - 309 KB dumps)
- ❌ *.sql database dumps
- ❌ *.sql.gz compressed dumps
- ❌ .env files with passwords
- ❌ node_modules/
- ❌ Temporary files
- ❌ Log files

**Why?** Database dumps are data, not code. Transfer them separately via SCP.

---

## 🚀 Recommended Workflow

### Step 1: Commit Code to Git (Local Machine)

```bash
cd /home/narabhit/Downloads/abena_all

# Check what will be committed
git status

# Add the new files
git add export-local-database.sh
git add import-live-database.sh
git add setup-live-database.sh
git add DATABASE_MIGRATION_GUIDE.md
git add LIVE_DEPLOYMENT_CHECKLIST.md
git add QUICK_START_GUIDE.md
git add SYSTEM_RESTART_REPORT_2025-10-10.md
git add ABENA_CHANGES_LOG.md
git add .gitignore

# Or add all at once (careful!)
# git add .

# Commit with descriptive message
git commit -m "Add database migration tools and deployment documentation

- Added export-local-database.sh for database backup
- Added import-live-database.sh for live server import
- Added comprehensive deployment guides
- Updated ABENA_CHANGES_LOG.md with system restart info
- Added .gitignore rules for database exports"

# Push to your branch
git push origin abena_live
```

### Step 2: Pull on Live Server

```bash
# SSH to live server
ssh user@your-live-server

# Navigate to project directory
cd /path/to/abena

# Pull latest code
git pull origin abena_live

# Make scripts executable
chmod +x export-local-database.sh
chmod +x import-live-database.sh
chmod +x setup-live-database.sh
```

### Step 3: Transfer Database Separately (SCP)

```bash
# From local machine, transfer database dump
scp database_exports/abena_database_full_20251010_153829.sql.gz user@live-server:/path/to/abena/

# This is fast! (48 KB file)
# Estimated time: < 1 second on decent connection
```

### Step 4: Import Database on Live Server

```bash
# SSH to live server (if not already there)
ssh user@live-server
cd /path/to/abena

# Run import script
./import-live-database.sh abena_database_full_20251010_153829.sql.gz

# Follow prompts to enter:
# - Database host
# - Database port
# - Database user
# - Database password
```

### Step 5: Configure and Start Services

```bash
# Update docker-compose.yml with DATABASE_URL from import script

# Start Docker services
docker-compose up -d

# Check status
docker-compose ps

# Test
curl http://localhost:4020/api/demo/status
```

---

## 📋 Complete Deployment Checklist

### On Local Machine:

- [ ] **Test everything works** (already done ✅)
- [ ] **Export database** (already done ✅)
  ```bash
  ./export-local-database.sh
  ```
- [ ] **Commit code to git**
  ```bash
  git add .
  git commit -m "Deployment ready with migration tools"
  git push origin abena_live
  ```
- [ ] **Transfer database dump via SCP**
  ```bash
  scp database_exports/*.sql.gz user@server:/path/to/abena/
  ```

### On Live Server:

- [ ] **Pull latest code**
  ```bash
  git pull origin abena_live
  ```
- [ ] **Make scripts executable**
  ```bash
  chmod +x *.sh
  ```
- [ ] **Import database**
  ```bash
  ./import-live-database.sh <database_file>
  ```
- [ ] **Update docker-compose.yml**
  - Set correct DATABASE_URL
  - Update any environment-specific configs
- [ ] **Start services**
  ```bash
  docker-compose up -d
  ```
- [ ] **Verify everything works**
  ```bash
  # Check containers
  docker-compose ps
  
  # Test demo
  curl http://localhost:4020/api/demo/status
  
  # Test IHR
  curl http://localhost:4002/health
  
  # Open browser
  http://your-server-ip:4020
  ```

---

## 🔐 Security Best Practices

### Before Pushing to Git:

1. **Check for sensitive data**
   ```bash
   git diff --cached
   ```

2. **Verify .gitignore is working**
   ```bash
   git status --ignored
   ```

3. **Don't commit passwords**
   - Use environment variables
   - Use .env files (add to .gitignore)
   - Use secrets management

### On Live Server:

1. **Use different passwords** than local
2. **Use environment files** for configuration
3. **Secure database access** with firewall rules
4. **Use SSH keys** for git pull (not passwords)

---

## 🎯 Why This Workflow?

### Benefits:

✅ **Code in Git** - Version control, history, collaboration
✅ **Data Separate** - Fast transfer, no git bloat
✅ **Clean Repository** - Only code, not data
✅ **Easy Updates** - Just `git pull` on server
✅ **Secure** - Sensitive data not in git history

### Git = Code | SCP = Data

```
┌─────────────────┐         ┌─────────────────┐
│  Local Machine  │         │   Live Server   │
├─────────────────┤         ├─────────────────┤
│                 │         │                 │
│  Git Push  ────────────────▶  Git Pull      │  (Code & Scripts)
│                 │         │                 │
│  SCP      ─────────────────▶  Receive       │  (Database Dump)
│                 │         │                 │
└─────────────────┘         └─────────────────┘
```

---

## 📊 File Size Comparison

What goes where:

| Files | Method | Size | Why |
|-------|--------|------|-----|
| **Code & Scripts** | Git | ~5 MB | Version control |
| **Database Dump** | SCP | 48 KB | Data, not code |
| **Documentation** | Git | ~50 KB | Reference |
| **node_modules** | Neither | ~200 MB | Rebuild on server |

---

## 🔄 Alternative: Database in Git (Not Recommended)

If you really want to put database in git:

```bash
# NOT RECOMMENDED but possible
git add database_exports/*.sql.gz
git commit -m "Add database dump"
git push
```

**Why NOT recommended:**
- ❌ Makes repository bloated
- ❌ Database dumps change frequently
- ❌ Git not designed for binary/data files
- ❌ Cloning becomes slow
- ❌ History becomes messy

**Better approach:** Use SCP (already set up for you!)

---

## 🚨 Common Issues & Solutions

### Issue: "Git won't let me push large files"

**Solution:** That's why we use .gitignore! Database dumps shouldn't be in git.
```bash
git rm --cached database_exports/*.sql.gz
git commit -m "Remove database dumps from git"
```

### Issue: "I accidentally committed passwords"

**Solution:** Remove from history (dangerous!)
```bash
# Better: Regenerate passwords and update
# Then remove from history:
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all
```

### Issue: "Can't pull on server - conflicts"

**Solution:** Stash local changes or reset
```bash
# Option 1: Stash
git stash
git pull
git stash pop

# Option 2: Reset (careful!)
git fetch origin
git reset --hard origin/abena_live
```

---

## 📝 Quick Command Reference

### Local Machine (Your Laptop):
```bash
# 1. Export database
./export-local-database.sh

# 2. Commit to git
git add .
git commit -m "Your message"
git push origin abena_live

# 3. Transfer database
scp database_exports/*.sql.gz user@server:/path/
```

### Live Server:
```bash
# 1. Pull code
git pull origin abena_live

# 2. Import database
./import-live-database.sh <file>

# 3. Start services
docker-compose up -d

# 4. Test
curl http://localhost:4020/api/demo/status
```

---

## 🎯 Recommended Approach for You

Based on your setup:

### 1️⃣ Commit Scripts & Docs (Use Git)
```bash
git add *.sh *.md .gitignore
git commit -m "Add deployment tools and documentation"
git push origin abena_live
```

### 2️⃣ Transfer Database (Use SCP)
```bash
scp database_exports/*.sql.gz user@server:/path/to/abena/
```

### 3️⃣ On Server (Pull & Import)
```bash
git pull origin abena_live
./import-live-database.sh <database_file>
docker-compose up -d
```

**This way:**
- ✅ Git stays clean (code only)
- ✅ Database transfers fast (SCP)
- ✅ Easy to update (git pull)
- ✅ Secure (no passwords in git)

---

## ✅ Summary

**Best Practice Workflow:**

1. **Code → Git** (push/pull)
2. **Data → SCP** (direct transfer)
3. **Scripts → Git** (version controlled)
4. **Secrets → Environment** (not in git)

**Time Required:**
- Git push: ~30 seconds
- Git pull on server: ~10 seconds  
- SCP database: ~1 second (48 KB)
- Import database: ~3 minutes
- Start services: ~1 minute
- **Total: ~5 minutes!**

---

**Created**: October 10, 2025  
**Status**: Ready to deploy  
**Next Step**: Commit to git, then pull on server! 🚀

