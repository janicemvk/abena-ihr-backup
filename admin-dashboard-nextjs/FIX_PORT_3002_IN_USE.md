# 🔧 Fix "Port 3002 Already in Use" Error

## 🐛 **The Problem**

Port 3002 is already being used by another process. You need to either:
1. Stop the process using port 3002
2. Use a different port

## ✅ **Solution 1: Find and Stop What's Using Port 3002**

### **Step 1: Find What's Using Port 3002**
```powershell
netstat -ano | findstr :3002
```

This will show you the Process ID (PID) using the port.

### **Step 2: Stop the Process**
```powershell
# Replace <PID> with the number from Step 1
taskkill /PID <PID> /F
```

### **Step 3: Start Admin Portal**
```powershell
$env:PORT=3002; npm run dev
```

---

## ✅ **Solution 2: Use a Different Port (Easier)**

Just use a different port like 3003:

```powershell
$env:PORT=3003; npm run dev
```

Then access at: **http://localhost:3003/admin**

---

## 🎯 **Quick Fix (Recommended)**

Use port 3003 instead:

```powershell
cd "c:\Next-JS\admin 2\Project Admin"
$env:PORT=3003; npm run dev
```

**Access at:** http://localhost:3003/admin

---

## 📝 **Permanent Fix: Set Port in .env.local**

Create a file `.env.local` in the admin portal directory:

```env
PORT=3003
```

Then just run:
```powershell
npm run dev
```

It will automatically use port 3003.

---

**Try Solution 2 first - it's the quickest!** 🚀


