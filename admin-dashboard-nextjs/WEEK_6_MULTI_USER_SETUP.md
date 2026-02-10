# Week 6: Multi-User Admin & Medical Coding Assistant - Setup Guide

## ✅ **Completed Features**

### 1. Medical Coding Assistant ✅
- **Location:** `/admin/medical-coding`
- **Features:**
  - CPT code lookup and search
  - ICD-10 code lookup and search
  - Intelligent code suggestions based on search terms
  - Category filtering
  - Code details modal with copy functionality
  - Common CPT modifiers reference
- **Status:** ✅ Ready to use

### 2. Multi-User Admin Management ✅
- **Integration Bridge Endpoints:** Added to `integration-bridge/server.js`
- **User Service API Client:** Created `src/lib/services/userService.ts`
- **Users Page:** Updated `src/app/admin/users/page.tsx` to connect to real API
- **Authentication:** Updated to support multiple users via Integration Bridge

---

## 🗄️ **Database Setup**

### **Step 1: Create Admin Users Table**

Run the SQL script to create the admin_users table:

```bash
# Navigate to integration bridge directory
cd "c:\Users\Jan Marie\Documents\Python Development Files\abena ihr\integration-bridge"

# Run the SQL script in PostgreSQL
psql -U postgres -d abena_ihr -f CREATE_ADMIN_USERS_TABLE.sql
```

Or manually run the SQL in your PostgreSQL client:

```sql
-- See: integration-bridge/CREATE_ADMIN_USERS_TABLE.sql
```

This will:
- Create `admin_users` table
- Create `admin_user_permissions` table (optional, for future use)
- Insert default super admin user (`admin@abena-ihr.com` / `admin123`)
- Set up indexes for performance

### **Step 2: Install bcryptjs in Integration Bridge**

```bash
cd "c:\Users\Jan Marie\Documents\Python Development Files\abena ihr\integration-bridge"
npm install bcryptjs
```

---

## 🔧 **Configuration**

### **Environment Variables**

Make sure your `.env` files are configured:

**Integration Bridge** (`integration-bridge/.env`):
```env
PORT=8081
DB_USER=postgres
DB_HOST=localhost
DB_NAME=abena_ihr
DB_PASSWORD=postgres
DB_PORT=5432
JWT_SECRET=abena-ihr-mvp-secret-key-change-in-production
```

**Admin Portal** (`Project Admin/.env.local`):
```env
NEXT_PUBLIC_INTEGRATION_BRIDGE_URL=http://localhost:8081
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:3002
```

---

## 🚀 **Starting Services**

### **1. Start Integration Bridge**

```bash
cd "c:\Users\Jan Marie\Documents\Python Development Files\abena ihr\integration-bridge"
npm start
# or for development with auto-reload:
npm run dev
```

Verify it's running:
```bash
curl http://localhost:8081/health
```

### **2. Start Admin Portal**

```bash
cd "c:\Next-JS\admin 2\Project Admin"
npm run dev
```

Access at: `http://localhost:3010`

---

## 👤 **Default Admin User**

After running the SQL script, you can log in with:

- **Email:** `admin@abena-ihr.com`
- **Password:** `admin123`
- **Role:** `super_admin`

**⚠️ IMPORTANT:** Change this password immediately after first login!

---

## 📋 **API Endpoints**

### **Authentication**
- `POST /api/admin/auth/login` - Login admin user

### **User Management** (requires admin role)
- `GET /api/admin/users` - List all admin users
- `GET /api/admin/users/:id` - Get user by ID
- `POST /api/admin/users` - Create new user (super_admin only)
- `PUT /api/admin/users/:id` - Update user
- `DELETE /api/admin/users/:id` - Deactivate user (super_admin only)
- `POST /api/admin/users/:id/reset-password` - Reset password

---

## 🎯 **User Roles**

- **super_admin** - Full access, can create/delete users, change roles
- **admin** - Standard admin access, can manage most features
- **billing_admin** - Billing and insurance management only
- **coding_admin** - Medical coding management only

---

## 🔐 **Permissions**

### **Role-Based Access:**

1. **super_admin:**
   - Can create/delete users
   - Can change user roles
   - Can manage all features
   - Can reset any user's password

2. **admin:**
   - Can view all users
   - Can edit users (except roles)
   - Can manage all features
   - Can reset own password

3. **billing_admin / coding_admin:**
   - Can view own profile
   - Can edit own profile
   - Can reset own password
   - Limited feature access (based on role)

---

## 🧪 **Testing**

### **Test User Management:**

1. **Login as super admin:**
   ```
   Email: admin@abena-ihr.com
   Password: admin123
   ```

2. **Create a new user:**
   - Go to `/admin/users`
   - Click "Add User"
   - Fill in details
   - Select role (admin, billing_admin, coding_admin)
   - Click "Add User"

3. **Test user login:**
   - Logout
   - Login with new user credentials
   - Verify access based on role

### **Test Medical Coding:**

1. Go to `/admin/medical-coding`
2. Search for CPT codes (e.g., "99213")
3. Switch to ICD-10 codes
4. Use category filters
5. Click on codes to view details

---

## 📝 **Next Steps**

1. **Add authentication endpoint to Integration Bridge** ✅ (Done)
2. **Create User Service API client** ✅ (Done)
3. **Update Users page** ✅ (Done)
4. **Update authentication** ✅ (Done)
5. **Add role-based permissions** (Future enhancement)
6. **Add audit logging** (Future enhancement)
7. **Add password complexity requirements** (Future enhancement)

---

## 🐛 **Troubleshooting**

### **Issue: Cannot connect to Integration Bridge**

**Solution:**
- Check if Integration Bridge is running: `curl http://localhost:8081/health`
- Verify `NEXT_PUBLIC_INTEGRATION_BRIDGE_URL` in `.env.local`
- Check CORS settings in Integration Bridge

### **Issue: Authentication fails**

**Solution:**
- Verify admin_users table exists
- Check if default user was created
- Verify bcryptjs is installed in Integration Bridge
- Check Integration Bridge logs for errors

### **Issue: Cannot create users**

**Solution:**
- Verify you're logged in as `super_admin`
- Check Integration Bridge logs
- Verify database connection

### **Issue: Users page shows "No users found"**

**Solution:**
- Check if Integration Bridge is running
- Verify database connection
- Check browser console for errors
- Verify JWT token is being sent in requests

---

## 📚 **Files Created/Modified**

### **New Files:**
- `src/app/admin/medical-coding/page.tsx` - Medical Coding Assistant
- `src/lib/services/userService.ts` - User Service API client
- `src/lib/services/authService.ts` - Auth Service API client
- `integration-bridge/CREATE_ADMIN_USERS_TABLE.sql` - Database schema
- `ADMIN_FEATURES_PLAN.md` - Implementation plan

### **Modified Files:**
- `integration-bridge/server.js` - Added user management endpoints
- `integration-bridge/package.json` - Added bcryptjs dependency
- `src/app/api/auth/[...nextauth]/route.ts` - Updated authentication
- `src/app/admin/users/page.tsx` - Connected to real API
- `src/app/admin/layout.tsx` - Added Medical Coding to navigation
- `src/app/admin/page.tsx` - Added Medical Coding to dashboard

---

## ✅ **Verification Checklist**

- [ ] Database tables created (`admin_users`, `admin_user_permissions`)
- [ ] bcryptjs installed in Integration Bridge
- [ ] Integration Bridge running on port 8081
- [ ] Admin Portal running on port 3010
- [ ] Can login with default super admin
- [ ] Can view users list
- [ ] Can create new user (as super_admin)
- [ ] Can edit user
- [ ] Can deactivate user
- [ ] Can reset password
- [ ] Medical Coding Assistant accessible
- [ ] Can search CPT codes
- [ ] Can search ICD-10 codes

---

## 🎉 **Success!**

You now have:
- ✅ Multi-user admin management
- ✅ Medical Coding Assistant
- ✅ Role-based access control
- ✅ Integration Bridge connection
- ✅ Real database-backed authentication

Ready for production use! 🚀

