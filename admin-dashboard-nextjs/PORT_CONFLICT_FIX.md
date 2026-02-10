# 🔧 Port Conflict Fix - Admin Portal vs Provider Dashboard

## 🐛 **The Problem**

Both the **Admin Portal** (Next.js) and **Provider Dashboard** (React) are trying to use port 3001, causing a conflict. When you visit `http://localhost:3001/admin`, you're seeing the Provider Dashboard instead.

## 🔍 **How to Identify Which App is Running**

### **Check Your Running Terminals:**

1. **Provider Dashboard** (React):
   - Location: `ECBome material 3 folders\Provider interface eCBome Monitoring Dashboard`
   - Default port: 3000 (or 3001 if 3000 is taken)
   - Command: `npm start`

2. **Admin Portal** (Next.js):
   - Location: `c:\Next-JS\admin 2\Project Admin`
   - Default port: 3000 (or 3001 if 3000 is taken)
   - Command: `npm run dev`

## ✅ **Solution: Use Different Ports**

### **Option 1: Run Admin Portal on a Different Port (Recommended)**

Stop the admin portal and restart it on a specific port:

```powershell
# Stop the current admin portal (Ctrl+C)

# Set a custom port and restart
cd "c:\Next-JS\admin 2\Project Admin"
$env:PORT=3002; npm run dev
```

Or create a `.env.local` file in the admin portal directory:

```env
PORT=3002
```

Then restart:
```powershell
npm run dev
```

**Access the admin portal at:** http://localhost:3002/admin

---

### **Option 2: Run Provider Dashboard on a Different Port**

Stop the provider dashboard and restart it on a specific port:

```powershell
# Stop the provider dashboard (Ctrl+C)

# Navigate to provider dashboard
cd "c:\Users\Jan Marie\Documents\Python Development Files\ECBome material 3 folders\Provider interface eCBome Monitoring Dashboard"

# Set custom port
$env:PORT=3002; npm start
```

Or create a `.env` file in the provider dashboard directory:

```env
PORT=3002
```

Then restart:
```powershell
npm start
```

**Access the provider dashboard at:** http://localhost:3002

---

## 🎯 **Recommended Port Configuration**

To avoid conflicts, use these ports:

| Application | Port | URL |
|------------|------|-----|
| **Provider Dashboard** | 3000 | http://localhost:3000 |
| **Admin Portal** | 3002 | http://localhost:3002/admin |
| **Patient Dashboard** | 5173 | http://localhost:5173 |
| **Appointment Service** | 3009 | http://localhost:3009 |
| **Clinical Notes Service** | 3008 | http://localhost:3008 |
| **Treatment Plan Service** | 3007 | http://localhost:3007 |

---

## 🚀 **Quick Fix Steps**

1. **Stop both applications** (Ctrl+C in their terminals)

2. **Start Provider Dashboard on port 3000:**
   ```powershell
   cd "c:\Users\Jan Marie\Documents\Python Development Files\ECBome material 3 folders\Provider interface eCBome Monitoring Dashboard"
   $env:PORT=3000; npm start
   ```

3. **Start Admin Portal on port 3002:**
   ```powershell
   cd "c:\Next-JS\admin 2\Project Admin"
   $env:PORT=3002; npm run dev
   ```

4. **Access:**
   - Admin Portal: http://localhost:3002/admin
   - Provider Dashboard: http://localhost:3000

---

## 📝 **Permanent Fix: Create .env Files**

### **For Admin Portal:**
Create `c:\Next-JS\admin 2\Project Admin\.env.local`:
```env
PORT=3002
```

### **For Provider Dashboard:**
Create `.env` in the provider dashboard directory:
```env
PORT=3000
```

This way, each app will always use its designated port!

---

**After fixing the port conflict, you should see the Admin Dashboard at http://localhost:3002/admin** ✅


