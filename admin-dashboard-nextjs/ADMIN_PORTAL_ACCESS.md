# 🚀 Admin Portal - How to Access

## 📍 **Location**
The Admin Portal is located at:
```
c:\Next-JS\admin 2\Project Admin\
```

## 🏃 **How to Start the Admin Portal**

### **Step 1: Navigate to the Admin Portal Directory**
```powershell
cd "c:\Next-JS\admin 2\Project Admin"
```

### **Step 2: Install Dependencies (if needed)**
```powershell
npm install
```

### **Step 3: Start the Development Server**
```powershell
npm run dev
```

### **Step 4: Access the Admin Portal**
Open your browser and navigate to:
- **Main Page:** http://localhost:3010
- **Admin Dashboard:** http://localhost:3010/admin
- **Login Page:** http://localhost:3010/login

---

## 📋 **Available Admin Pages**

Once you're in the admin portal, you can access:

1. **Dashboard** - `/admin`
   - Overview of all admin features
   - Quick access to all management tools

2. **User Management** - `/admin/users`
   - Create, edit, and manage user accounts
   - View user roles and status

3. **Appointment Management** - `/admin/appointments`
   - View and manage all appointments
   - Calendar view of appointments
   - Create/edit/delete appointments

4. **Analytics** - `/admin/analytics`
   - System performance metrics
   - Recent activity feed
   - Statistics dashboard

5. **Billing** - `/admin/billing`
   - Manage billing and insurance claims

6. **Communications** - `/admin/communications`
   - Manage provider and patient communications

7. **Feedback** - `/admin/feedback`
   - Track and analyze patient satisfaction

8. **Settings** - `/admin/config`
   - System configuration and preferences

---

## 🔌 **API Services Created**

We've created API service files that connect to your foundational services:

1. **Appointment Service** - `src/lib/services/appointmentService.ts`
   - Connects to Appointment Service (port 3009)

2. **Clinical Notes Service** - `src/lib/services/clinicalNotesService.ts`
   - Connects to Clinical Notes Service (port 3008)

3. **Treatment Plan Service** - `src/lib/services/treatmentPlanService.ts`
   - Connects to Treatment Plan Service (port 3007)

**Note:** The admin pages currently use mock data. To connect them to real APIs, you'll need to update the pages to use these service files.

---

## 🎯 **Quick Start Commands**

```powershell
# Navigate to admin portal
cd "c:\Next-JS\admin 2\Project Admin"

# Install dependencies (first time only)
npm install

# Start the server
npm run dev

# Then open: http://localhost:3010/admin
```

---

## ⚠️ **Important Notes**

1. **Port:** The admin portal runs on port 3010 (configured in package.json)
2. **Dependencies:** Make sure Node.js and npm are installed
3. **Backend Services:** For full functionality, start the foundational services:
   - Appointment Service (port 3009)
   - Clinical Notes Service (port 3008)
   - Treatment Plan Service (port 3007)

---

## 🔄 **Next Steps**

To fully integrate the admin portal with your backend services:

1. Update `/admin/appointments` page to use `appointmentService.ts`
2. Create `/admin/clinical-notes` page using `clinicalNotesService.ts`
3. Create `/admin/treatment-plans` page using `treatmentPlanService.ts`
4. Update navigation in `admin/layout.tsx` to include new pages

---

**Ready to start? Run the commands above and visit http://localhost:3010/admin!** 🚀

