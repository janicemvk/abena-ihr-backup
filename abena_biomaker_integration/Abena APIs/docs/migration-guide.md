# Migration Guide: From Custom Auth/Database to Abena SDK

## Overview

This guide shows how to migrate from custom authentication and database management to using the unified Abena SDK, which automatically handles authentication, privacy compliance, audit logging, and blockchain recording.

## Before vs After

### ❌ Before (Custom Implementation)

```javascript
class SomeModule {
  constructor() {
    this.database = new Database();
    this.authSystem = new CustomAuth();
  }

  async someMethod(patientId, userId) {
    // Manual authentication check
    const isAuthenticated = await this.authSystem.verifyToken(userId);
    if (!isAuthenticated) {
      throw new Error('Authentication failed');
    }
    
    // Manual permission check
    const hasPermission = await this.authSystem.checkPermission(userId, 'read_patient_data');
    if (!hasPermission) {
      throw new Error('Insufficient permissions');
    }
    
    // Manual privacy compliance check
    const consentGiven = await this.database.query(
      'SELECT consent_settings FROM patients WHERE patient_id = $1',
      [patientId]
    );
    if (!consentGiven.rows[0]?.consent_settings?.data_sharing) {
      throw new Error('Patient consent not given');
    }
    
    // Manual audit logging
    await this.database.query(
      'INSERT INTO patient_access_log (patient_id, accessed_by, access_type) VALUES ($1, $2, $3)',
      [patientId, userId, 'READ']
    );
    
    // Finally get the actual data
    const result = await this.database.query(
      'SELECT * FROM patients WHERE patient_id = $1',
      [patientId]
    );
    
    return this.processData(result.rows[0]);
  }
}
```

### ✅ After (Abena SDK)

```javascript
const AbenaSDK = require('@abena/sdk');

class SomeModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }

  async someMethod(patientId, userId) {
    // 1. Auto-handled auth & permissions
    const patientData = await this.abena.getPatientData(patientId, 'module_purpose');
    
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    
    // 4. Focus on your business logic
    return this.processData(patientData);
  }
}
```

## Step-by-Step Migration

### Step 1: Install Abena SDK

```bash
npm install @abena/sdk
```

### Step 2: Update Module Constructors

Replace custom database and auth initialization with Abena SDK:

```javascript
// Before
constructor() {
  this.database = new Database();
  this.authSystem = new CustomAuth();
}

// After
constructor() {
  this.abena = new AbenaSDK({
    authServiceUrl: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
    dataServiceUrl: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
    privacyServiceUrl: process.env.PRIVACY_SERVICE_URL || 'http://localhost:8002',
    blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
  });
}
```

### Step 3: Replace Data Access Methods

#### For Patient Data:

```javascript
// Before
const result = await this.database.query(
  'SELECT * FROM patients WHERE patient_id = $1',
  [patientId]
);

// After
const patientData = await this.abena.getPatientData(patientId, 'module_purpose');
```

#### For Clinical Data:

```javascript
// Before
const result = await this.database.query(
  'SELECT * FROM lab_results WHERE patient_id = $1',
  [patientId]
);

// After
const clinicalData = await this.abena.getClinicalData(patientId, 'lab_results', 'clinical_review');
```

#### For User Data:

```javascript
// Before
const result = await this.database.query(
  'SELECT * FROM users WHERE user_id = $1',
  [userId]
);

// After
const userData = await this.abena.getUserData(userId, 'user_profile_view');
```

### Step 4: Replace Data Saving Methods

```javascript
// Before
await this.database.query(
  'UPDATE patients SET first_name = $1, last_name = $2 WHERE patient_id = $3',
  [firstName, lastName, patientId]
);

// After
await this.abena.savePatientData(patientId, {
  firstName,
  lastName
}, 'patient_data_update');
```

## Real-World Migration Examples

### Example 1: Patient Routes Migration

#### Before (`routes/patients.js`):

```javascript
router.get('/:patientId', [
  authenticate,
  authorize(['doctor', 'nurse', 'admin'])
], asyncHandler(async (req, res) => {
  const { patientId } = req.params;
  
  // Manual auth check
  if (!req.user) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  
  // Manual permission check
  if (!['doctor', 'nurse', 'admin'].includes(req.user.role)) {
    return res.status(403).json({ error: 'Insufficient privileges' });
  }
  
  // Manual privacy check
  const consentResult = await getPatientDB().query(
    'SELECT consent_settings FROM patients WHERE patient_id = $1',
    [patientId]
  );
  
  if (!consentResult.rows[0]?.consent_settings?.data_sharing) {
    return res.status(403).json({ error: 'Patient consent not given' });
  }
  
  // Manual audit logging
  await logPatientAccess(req, patientId, 'READ', { endpoint: '/patients/:patientId' });
  
  // Get patient data
  const result = await getPatientDB().query(
    'SELECT * FROM patients WHERE patient_id = $1',
    [patientId]
  );
  
  res.json({ success: true, data: result.rows[0] });
}));
```

#### After (`routes/patients.js`):

```javascript
const AbenaSDK = require('@abena/sdk');

const abena = new AbenaSDK({
  authServiceUrl: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
  dataServiceUrl: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
  privacyServiceUrl: process.env.PRIVACY_SERVICE_URL || 'http://localhost:8002',
  blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
});

router.get('/:patientId', asyncHandler(async (req, res) => {
  const { patientId } = req.params;
  
  // All auth, privacy, and audit handled automatically
  const patientData = await abena.getPatientData(patientId, 'patient_profile_view');
  
  res.json({ success: true, data: patientData });
}));
```

### Example 2: Clinical Routes Migration

#### Before (`routes/clinical.js`):

```javascript
router.get('/:patientId/lab-results', [
  authenticate,
  authorize(['doctor', 'nurse', 'admin'])
], asyncHandler(async (req, res) => {
  const { patientId } = req.params;
  
  // Manual auth and permission checks...
  // Manual privacy compliance checks...
  // Manual audit logging...
  
  const result = await getClinicalDB().query(
    'SELECT * FROM lab_results WHERE patient_id = $1 ORDER BY collected_date DESC',
    [patientId]
  );
  
  res.json({ success: true, data: result.rows });
}));
```

#### After (`routes/clinical.js`):

```javascript
router.get('/:patientId/lab-results', asyncHandler(async (req, res) => {
  const { patientId } = req.params;
  
  // All auth, privacy, and audit handled automatically
  const labData = await abena.getClinicalData(patientId, 'lab_results', 'clinical_review');
  
  res.json({ success: true, data: labData.results });
}));
```

## Benefits of Migration

### 1. **Reduced Code Complexity**
- Eliminates manual authentication, authorization, and privacy checks
- Removes boilerplate database queries
- Simplifies error handling

### 2. **Automatic Compliance**
- Built-in privacy compliance checks
- Automatic audit logging
- Blockchain recording for data integrity

### 3. **Better Security**
- Centralized security policies
- Automatic encryption/decryption
- Consistent access controls

### 4. **Easier Maintenance**
- Single point of configuration
- Unified error handling
- Consistent logging across all modules

### 5. **Focus on Business Logic**
- Developers can focus on core functionality
- Less time spent on infrastructure concerns
- Faster development cycles

## Environment Variables

Add these to your `.env` file:

```env
AUTH_SERVICE_URL=http://localhost:3001
DATA_SERVICE_URL=http://localhost:8001
PRIVACY_SERVICE_URL=http://localhost:8002
BLOCKCHAIN_SERVICE_URL=http://localhost:8003
```

## Testing the Migration

Create a test script to verify the migration:

```javascript
const { PatientDataModule } = require('./examples/migration-example');

async function testMigration() {
  const patientModule = new PatientDataModule();
  
  try {
    const profile = await patientModule.getPatientProfile('PAT-123');
    console.log('✅ Migration successful:', profile);
  } catch (error) {
    console.error('❌ Migration failed:', error);
  }
}

testMigration();
```

## Rollback Plan

If you need to rollback, you can:

1. Keep the old code commented out during migration
2. Use feature flags to switch between old and new implementations
3. Maintain backward compatibility during the transition period

## Support

For questions about the migration process, refer to:
- Abena SDK documentation
- Migration examples in `/examples/`
- Test cases in `/tests/` 