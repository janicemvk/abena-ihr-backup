# 🎯 Admin Portal - New Features Implementation Plan

## ✅ **Completed Features**

### 1. Medical Coding Assistant ✅
- **Location:** `/admin/medical-coding`
- **Features:**
  - CPT code lookup and search
  - ICD-10 code lookup and search
  - Intelligent code suggestions based on search
  - Category filtering
  - Code details modal with copy functionality
  - Common CPT modifiers reference
- **Status:** ✅ Created and added to navigation

---

## 🚧 **In Progress / Planned Features**

### 2. Multi-User Admin Management

#### **Current State:**
- Single mock admin user (`admin@abena-ihr.com`)
- Mock authentication via NextAuth.js
- No real user database connection

#### **Required Changes:**

##### **A. User Service API Client**
- **File:** `src/lib/services/userService.ts`
- **Purpose:** Connect to backend user management
- **Options:**
  1. **Integration Bridge** (port 8081) - If it has user management endpoints
  2. **Auth Service** (port 3002) - If it has user CRUD operations
  3. **New User Service** - Create dedicated user management service

##### **B. Update Authentication**
- **File:** `src/app/api/auth/[...nextauth]/route.ts`
- **Changes:**
  - Connect to real user database (via Integration Bridge or Auth Service)
  - Support multiple admin users
  - Role-based access control (Admin, Super Admin, etc.)
  - User session management

##### **C. Update Users Page**
- **File:** `src/app/admin/users/page.tsx`
- **Changes:**
  - Connect to User Service API
  - Real CRUD operations
  - User role management
  - User status management (Active/Inactive)
  - Password reset functionality

##### **D. Role-Based Permissions**
- **File:** `src/lib/utils/permissions.ts` (new)
- **Features:**
  - Permission checking utilities
  - Role definitions
  - Feature access control

---

## 🔌 **Integration Bridge Connection**

### **Question: Do we need to connect to Integration Bridge?**

**Answer: It depends on your architecture:**

#### **Option 1: Connect to Integration Bridge** ✅ Recommended
- **Pros:**
  - Centralized user management
  - Single source of truth
  - Already has database connection
  - Can leverage existing authentication

- **Cons:**
  - Need to add user management endpoints to bridge
  - More complex integration

- **Implementation:**
  1. Check if Integration Bridge has user management endpoints
  2. If not, add endpoints to `integration-bridge/server.js`:
     - `GET /api/users` - List all users
     - `GET /api/users/:id` - Get user by ID
     - `POST /api/users` - Create user
     - `PUT /api/users/:id` - Update user
     - `DELETE /api/users/:id` - Delete user
     - `POST /api/users/:id/reset-password` - Reset password

#### **Option 2: Use Auth Service Directly**
- **Pros:**
  - Simpler if Auth Service already has user management
  - Direct connection

- **Cons:**
  - May need to extend Auth Service
  - Less centralized

#### **Option 3: Create Dedicated User Service**
- **Pros:**
  - Clean separation of concerns
  - Follows microservices pattern

- **Cons:**
  - More services to maintain
  - Need to create new service

---

## 📋 **Recommended Implementation Steps**

### **Phase 1: Multi-User Admin (Week 7)**

1. **Check Integration Bridge capabilities**
   ```bash
   # Check if bridge has user endpoints
   curl http://localhost:8081/api/users
   ```

2. **Create User Service API Client**
   - Connect to Integration Bridge or Auth Service
   - Implement CRUD operations

3. **Update Authentication**
   - Connect to real user database
   - Support multiple admin users
   - Add role management

4. **Update Users Page**
   - Connect to User Service
   - Implement real user management

5. **Add Role-Based Permissions**
   - Create permissions utility
   - Add permission checks to admin pages

### **Phase 2: Enhanced Medical Coding (Week 8)**

1. **Connect to Medical Coding API** (if available)
2. **Add code validation**
3. **Add code history/audit trail**
4. **Add favorite codes**
5. **Add code combinations/suggestions**

---

## 🗄️ **Database Schema Needed**

If creating new user management, you'll need:

```sql
CREATE TABLE admin_users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  role VARCHAR(50) DEFAULT 'admin', -- admin, super_admin, billing_admin, etc.
  status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended
  telephone VARCHAR(20),
  pager VARCHAR(20),
  office_number VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP,
  created_by UUID REFERENCES admin_users(user_id)
);

CREATE TABLE admin_user_permissions (
  permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES admin_users(user_id),
  permission_type VARCHAR(100), -- manage_users, manage_billing, manage_coding, etc.
  granted BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎯 **Next Steps**

1. **Decide on integration approach** (Bridge vs Auth Service vs New Service)
2. **Check existing endpoints** in Integration Bridge
3. **Create User Service API client**
4. **Update authentication to support multiple users**
5. **Test multi-user functionality**

---

## 📝 **Notes**

- Medical Coding Assistant is ready to use
- Can be enhanced with API integration later
- Multi-user functionality requires backend connection
- Integration Bridge is recommended for centralized management

