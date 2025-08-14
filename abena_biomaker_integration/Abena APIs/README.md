# Abena Healthcare API

A modern healthcare API system built with the **Abena SDK** for unified authentication, data management, privacy compliance, and blockchain integration.

## 🚀 Features

- **Unified Abena SDK**: Single SDK for all healthcare operations
- **Auto-handled Authentication**: No more manual auth checks
- **Auto-handled Privacy Compliance**: Built-in GDPR/HIPAA compliance
- **Auto-handled Audit Logging**: Automatic access tracking
- **Auto-handled Blockchain Recording**: Immutable audit trail
- **Focus on Business Logic**: 90% less boilerplate code

## 📦 Installation

```bash
npm install
```

## 🔧 Configuration

Set up your environment variables in `.env`:

```env
AUTH_SERVICE_URL=http://localhost:3001
DATA_SERVICE_URL=http://localhost:8001
PRIVACY_SERVICE_URL=http://localhost:8002
BLOCKCHAIN_SERVICE_URL=http://localhost:8003
```

## 🧪 Testing

Run the migration test suite:

```bash
npm test
```

Or start the demo:

```bash
npm start
```

## 📚 Usage

### Basic SDK Usage

```javascript
const AbenaSDK = require('./lib/abena-sdk');

const abena = new AbenaSDK({
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
});

// Get patient data (auto-handles auth, privacy, audit)
const patientData = await abena.getPatientData('PAT-123', 'clinical_review');

// Save patient data (auto-handles auth, privacy, audit, blockchain)
const result = await abena.savePatientData('PAT-123', updates, 'data_update');
```

### Module Examples

See `examples/migration-example.js` for complete module implementations:

- `PatientDataModule` - Patient profile management
- `ClinicalDataModule` - Lab results and vital signs
- `UserManagementModule` - User profile management

## 🔄 Migration from Custom Auth/Database

This project demonstrates the migration from custom authentication and database patterns to the unified Abena SDK.

### Before (❌ Custom Implementation)
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

### After (✅ Abena SDK)
```javascript
const AbenaSDK = require('./lib/abena-sdk');

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

## 📊 Benefits

- **90% reduction** in boilerplate code
- **Automatic compliance** with privacy regulations
- **Consistent security** policies across all modules
- **Easier maintenance** with unified error handling
- **Better scalability** with centralized services
- **Focus on business logic** instead of infrastructure

## 📖 Documentation

- [Migration Guide](docs/migration-guide.md) - Complete migration instructions
- [Examples](examples/) - Real-world usage examples
- [Test Suite](test-migration.js) - Migration verification tests

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Abena SDK                                │
├─────────────────────────────────────────────────────────────┤
│  🔐 Auth Service    📊 Data Service                         │
│  🔒 Privacy Service  ⛓️ Blockchain Service                  │
├─────────────────────────────────────────────────────────────┤
│  Auto-handled: Authentication, Authorization, Privacy,     │
│  Audit Logging, Blockchain Recording, Error Handling       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Your Business Logic                          │
│  - Patient Management    - Clinical Data                   │
│  - User Management       - Analytics                       │
└─────────────────────────────────────────────────────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For questions about the Abena SDK or migration process:
- Check the [Migration Guide](docs/migration-guide.md)
- Review the [Examples](examples/)
- Run the [Test Suite](test-migration.js) 