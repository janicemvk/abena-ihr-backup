# Abena SDK

Universal SDK for all Abena IHR (Integrated Health Records) modules. This SDK provides a unified interface for authentication, data access, privacy controls, and blockchain audit logging across all Abena healthcare modules.

## Features

- 🔐 **Unified Authentication** - Single sign-on across all services
- 🛡️ **Privacy & Security** - Built-in encryption, anonymization, and consent management
- 📊 **Data Access** - Unified patient data access with automatic access control
- ⛓️ **Blockchain Audit** - Immutable audit trail for all data access
- 🔄 **Data Ingestion** - Support for HL7, FHIR, and custom data formats
- 📈 **Analytics Ready** - Secure anonymized datasets for research

## Installation

```bash
npm install @abena/sdk
```

## Quick Start

```typescript
import AbenaSDK from '@abena/sdk';

// Initialize the SDK
const sdk = new AbenaSDK({
  authServiceUrl: 'https://auth.abena.health',
  dataServiceUrl: 'https://data.abena.health',
  privacyServiceUrl: 'https://privacy.abena.health',
  blockchainServiceUrl: 'https://blockchain.abena.health',
  timeout: 30000
});

// Login
const { user, token } = await sdk.login('doctor@hospital.com', 'password');

// Get complete patient context
const patientContext = await sdk.getCompletePatientContext(
  'patient-123',
  user.id,
  'clinical_care'
);

console.log('Patient data:', patientContext.patient);
console.log('Health records:', patientContext.healthRecords);
```

## Configuration

```typescript
interface AbenaConfig {
  authServiceUrl: string;        // Authentication service URL
  dataServiceUrl: string;        // Data access service URL
  privacyServiceUrl: string;     // Privacy & encryption service URL
  blockchainServiceUrl: string;  // Blockchain audit service URL
  apiKey?: string;              // Optional API key
  timeout?: number;             // Request timeout in milliseconds
}
```

## Core Features

### Authentication

```typescript
// Login with MFA support
const { user, token } = await sdk.login('user@example.com', 'password', 'mfa-token');

// Verify existing token
const user = await sdk.verifyToken('existing-jwt-token');

// Validate service access
const access = await sdk.validateServiceAccess('patient-123', 'read', 'data_access');
```

### Patient Data Access

```typescript
// Get comprehensive patient data
const patientData = await sdk.getPatientData('patient-123', 'clinical_care', {
  includeRecords: true,
  includeConsents: true,
  includeAuditLog: true,
  emergency: false
});

// Get specific health records
const records = await sdk.getPatientHealthRecords('patient-123', {
  recordType: 'medication',
  dateFrom: '2023-01-01',
  dateTo: '2023-12-31'
});
```

### Privacy & Security

```typescript
// Encrypt sensitive data
const encrypted = await sdk.encryptSensitiveData(
  { ssn: '123-45-6789' },
  'demographics',
  'patient-123'
);

// Decrypt data
const decrypted = await sdk.decryptSensitiveData(
  encrypted,
  'key-id',
  'clinical_care'
);

// Anonymize dataset for research
const anonymized = await sdk.anonymizeDataset(dataset, {
  anonymizationType: 'k-anonymity',
  quasiIdentifiers: ['age', 'gender', 'zip_code'],
  kValue: 5
});

// Check patient consent
const hasConsent = await sdk.checkPatientConsent(
  'patient-123',
  'provider-456',
  'research_analytics'
);
```

### Blockchain Audit

```typescript
// Log access to blockchain (automatic in most methods)
const txId = await sdk.logBlockchainAccess(
  'patient-123',
  'READ',
  'clinical_care',
  { riskScore: 0.1 }
);

// Verify data integrity
const isVerified = await sdk.verifyDataIntegrity('record-789');

// Get audit trail
const auditTrail = await sdk.getAuditTrail('patient-123', '2023-01-01', '2023-12-31');
```

### Data Ingestion

```typescript
// Ingest various data formats
await sdk.ingestVitalSigns(vitalSignsData);
await sdk.ingestLabResults(labResultsData);
await sdk.ingestHL7Message(hl7Message);
await sdk.ingestFHIRResource(fhirResource);
```

## Module-Specific Methods

### Clinical Modules

```typescript
// Get complete patient context for clinical decision support
const context = await sdk.getCompletePatientContext(
  'patient-123',
  'doctor-456',
  'clinical_care',
  false // emergency access
);

// Access includes:
// - Patient demographics
// - Health records
// - Medications
// - Allergies
// - Vital signs
// - Lab results
// - Risk factors
// - Audit information
```

### Analytics Modules

```typescript
// Get anonymized dataset for research
const dataset = await sdk.getAnonymizedDataset(
  {
    patientCohort: ['patient-1', 'patient-2'],
    dateRange: { from: '2023-01-01', to: '2023-12-31' },
    recordTypes: ['medication', 'lab_result'],
    includeFields: ['age', 'gender', 'diagnosis']
  },
  {
    type: 'differential-privacy',
    epsilon: 1.0
  }
);
```

## Error Handling

The SDK provides comprehensive error handling with detailed error messages:

```typescript
try {
  const data = await sdk.getPatientData('patient-123', 'clinical_care');
} catch (error) {
  if (error.message.includes('Access denied')) {
    // Handle access control errors
    console.log('Access denied:', error.message);
  } else if (error.message.includes('Service unavailable')) {
    // Handle service availability errors
    console.log('Service unavailable:', error.message);
  }
}
```

## Health Monitoring

```typescript
// Check health of all services
const healthStatus = await sdk.healthCheck();
console.log('Service health:', healthStatus);
// Output: { auth: true, data: true, privacy: true, blockchain: false }
```

## Token Management

```typescript
// Set token manually
sdk.setAuthToken('your-jwt-token');

// Clear token
sdk.clearAuthToken();
```

## Development

```bash
# Install dependencies
npm install

# Build the SDK
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Watch mode for development
npm run dev
```

## API Reference

### Classes

- `AbenaSDK` - Main SDK class

### Interfaces

- `AbenaConfig` - SDK configuration
- `PatientData` - Patient data structure
- `User` - User information
- `AccessResult` - Access validation result

### Methods

#### Authentication
- `login(email, password, mfaToken?)` - User authentication
- `verifyToken(token)` - Token verification
- `validateServiceAccess(patientId, action, service)` - Access validation

#### Data Access
- `getPatientData(patientId, purpose, options?)` - Get patient data
- `getPatientHealthRecords(patientId, filters?)` - Get health records

#### Privacy & Security
- `encryptSensitiveData(data, dataType, patientId?)` - Encrypt data
- `decryptSensitiveData(encryptedData, keyId, purpose)` - Decrypt data
- `anonymizeDataset(dataset, config)` - Anonymize data
- `checkPatientConsent(patientId, providerId, purpose)` - Check consent

#### Blockchain
- `logBlockchainAccess(patientId, action, purpose, metadata?)` - Log access
- `verifyDataIntegrity(recordId)` - Verify data integrity
- `getAuditTrail(patientId, dateFrom?, dateTo?)` - Get audit trail

#### Data Ingestion
- `ingestVitalSigns(vitalSigns)` - Ingest vital signs
- `ingestLabResults(labResults)` - Ingest lab results
- `ingestHL7Message(hl7Message)` - Ingest HL7 messages
- `ingestFHIRResource(fhirResource)` - Ingest FHIR resources

#### Convenience Methods
- `getCompletePatientContext(patientId, userId, purpose, emergencyAccess?)` - Complete context
- `getAnonymizedDataset(criteria, anonymizationConfig)` - Anonymized dataset

#### Utilities
- `healthCheck()` - Service health check
- `setAuthToken(token)` - Set auth token
- `clearAuthToken()` - Clear auth token

## License

MIT License - see LICENSE file for details.

## Support

For support and questions, please contact the Abena Health Systems development team or create an issue in the repository. 