# Abena SDK Integration Guide

## Overview

This guide demonstrates the correct pattern for integrating with the Abena IHR (Integrated Health Records) system using the Abena SDK for authentication, data access, privacy, and audit logging.

## ✅ Correct Pattern (Abena SDK)

```javascript
import AbenaSDK from '@abena/sdk';

class SomeModule {
  constructor() {
    // ✅ Correct - Uses Abena SDK
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }

  async someMethod(patientId, userId) {
    // ✅ Correct - Auto-handled auth & permissions
    const patientData = await this.abena.getPatientData(patientId, 'module_purpose');
    
    // ✅ Correct - Auto-handled privacy & encryption
    // ✅ Correct - Auto-handled audit logging
    
    // ✅ Correct - Focus on business logic
    return this.processData(patientData);
  }
}
```

## Key Benefits

### 1. **Automatic Authentication & Authorization**
- No need to implement custom auth logic
- Built-in permission checking
- Role-based access control
- Session management

### 2. **Built-in Privacy Protection**
- Automatic data encryption
- Privacy compliance (HIPAA, GDPR)
- Data anonymization
- Consent management

### 3. **Comprehensive Audit Logging**
- Automatic audit trail
- Compliance reporting
- Data access tracking
- Change history

### 4. **Focus on Business Logic**
- Less boilerplate code
- Reduced security vulnerabilities
- Faster development
- Easier maintenance

### 5. **Consistent Security**
- Standardized security practices
- Regular security updates
- Penetration testing
- Compliance validation

## Implementation Examples

### Clinical Outcomes Module

The `ClinicalOutcomesModule` demonstrates the correct pattern for clinical data management:

```javascript
import ClinicalOutcomesModule from './ClinicalOutcomesModule.js';

const clinicalModule = new ClinicalOutcomesModule({
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
});

// Get patient outcomes with automatic auth & privacy
const outcomes = await clinicalModule.getPatientOutcomes('PATIENT_001', 'DR_SMITH');

// Record pain assessment with validation and audit
const result = await clinicalModule.recordPainAssessment('PATIENT_001', 'DR_SMITH', {
  current_pain: 6.5,
  average_pain_24h: 6.0,
  worst_pain_24h: 8.0,
  least_pain_24h: 4.0,
  pain_interference: 6.5
});
```

### Available Methods

1. **`getPatientOutcomes(patientId, userId)`**
   - Retrieves patient clinical outcomes data
   - Auto-handles auth, privacy, and audit

2. **`recordPainAssessment(patientId, userId, assessmentData)`**
   - Records new pain assessment
   - Validates data and auto-audits

3. **`getPatientProgress(patientId, userId, outcomeType)`**
   - Analyzes patient progress over time
   - Compares baseline to current assessments

4. **`generateClinicalReport(patientId, userId, reportOptions)`**
   - Generates comprehensive clinical reports
   - Includes trends and recommendations

5. **`updateTreatmentPlan(patientId, userId, treatmentPlan)`**
   - Updates patient treatment plans
   - Validates plan structure and auto-audits

## Setup Guide

### Step 1: Install Abena SDK

```bash
npm install @abena/sdk
```

### Step 2: Initialize Module with Abena SDK

```javascript
import AbenaSDK from '@abena/sdk';

class YourModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }
}
```

### Step 3: Use Abena SDK for Data Operations

```javascript
async getPatientData(patientId, userId) {
  // Auto-handled auth, privacy, and audit
  const data = await this.abena.getPatientData(patientId, 'data_retrieval');
  return data;
}

async storePatientData(patientId, userId, data) {
  // Auto-handled auth, privacy, and audit
  const result = await this.abena.storePatientData(patientId, 'data_storage', {
    ...data,
    created_by: userId,
    created_at: new Date().toISOString()
  });
  return result;
}
```

## Configuration Options

### Abena SDK Configuration

```javascript
const abenaConfig = {
  authServiceUrl: 'http://localhost:3001',      // Authentication service
  dataServiceUrl: 'http://localhost:8001',      // Data storage service
  privacyServiceUrl: 'http://localhost:8002',   // Privacy/encryption service
  blockchainServiceUrl: 'http://localhost:8003' // Blockchain audit service
};
```

### Environment-Specific Configurations

**Development:**
```javascript
{
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
}
```

**Staging:**
```javascript
{
  authServiceUrl: 'https://auth-staging.abena.com',
  dataServiceUrl: 'https://data-staging.abena.com',
  privacyServiceUrl: 'https://privacy-staging.abena.com',
  blockchainServiceUrl: 'https://blockchain-staging.abena.com'
}
```

**Production:**
```javascript
{
  authServiceUrl: 'https://auth.abena.com',
  dataServiceUrl: 'https://data.abena.com',
  privacyServiceUrl: 'https://privacy.abena.com',
  blockchainServiceUrl: 'https://blockchain.abena.com'
}
```

## Error Handling

The Abena SDK provides comprehensive error handling:

```javascript
try {
  const data = await this.abena.getPatientData(patientId, 'purpose');
  return data;
} catch (error) {
  if (error.code === 'AUTH_UNAUTHORIZED') {
    // Handle authentication errors
    throw new Error('User not authorized to access this data');
  } else if (error.code === 'PRIVACY_VIOLATION') {
    // Handle privacy violations
    throw new Error('Privacy policy violation detected');
  } else if (error.code === 'DATA_NOT_FOUND') {
    // Handle missing data
    throw new Error('Patient data not found');
  } else {
    // Handle other errors
    console.error('Abena SDK error:', error);
    throw new Error('Failed to retrieve patient data');
  }
}
```

## Testing

### Unit Testing with Abena SDK

```javascript
import { jest } from '@jest/globals';
import ClinicalOutcomesModule from './ClinicalOutcomesModule.js';

// Mock the Abena SDK
jest.mock('@abena/sdk');

describe('ClinicalOutcomesModule', () => {
  let module;
  let mockAbenaSDK;

  beforeEach(() => {
    mockAbenaSDK = {
      getPatientData: jest.fn(),
      storePatientData: jest.fn()
    };
    
    // Mock the AbenaSDK constructor
    const AbenaSDK = require('@abena/sdk');
    AbenaSDK.mockImplementation(() => mockAbenaSDK);
    
    module = new ClinicalOutcomesModule();
  });

  test('getPatientOutcomes should use Abena SDK', async () => {
    const mockData = { patientId: 'PATIENT_001', assessments: [] };
    mockAbenaSDK.getPatientData.mockResolvedValue(mockData);

    const result = await module.getPatientOutcomes('PATIENT_001', 'DR_SMITH');

    expect(mockAbenaSDK.getPatientData).toHaveBeenCalledWith(
      'PATIENT_001',
      'clinical_outcomes_analysis'
    );
    expect(result).toBeDefined();
  });
});
```

## Security Considerations

### Data Protection
- All data is automatically encrypted at rest and in transit
- Privacy policies are automatically enforced
- Data access is logged and audited

### Authentication
- Multi-factor authentication support
- Session management and timeout
- Role-based access control

### Compliance
- HIPAA compliance for healthcare data
- GDPR compliance for EU data
- SOC 2 Type II certification
- Regular security audits

## Best Practices

### 1. **Always Use Purpose Strings**
```javascript
// ✅ Good - Clear purpose for data access
await this.abena.getPatientData(patientId, 'clinical_outcomes_analysis');

// ❌ Bad - Unclear purpose
await this.abena.getPatientData(patientId, 'general');
```

### 2. **Handle Errors Appropriately**
```javascript
try {
  const data = await this.abena.getPatientData(patientId, 'purpose');
  return data;
} catch (error) {
  // Log error for debugging
  console.error('Abena SDK error:', error);
  
  // Return user-friendly error
  throw new Error('Unable to retrieve patient data at this time');
}
```

### 3. **Validate Input Data**
```javascript
async recordPainAssessment(patientId, userId, assessmentData) {
  // ✅ Good - Validate before sending to SDK
  this.validatePainAssessment(assessmentData);
  
  const result = await this.abena.storePatientData(patientId, 'pain_assessment', assessmentData);
  return result;
}
```

### 4. **Use TypeScript for Better Type Safety**
```typescript
interface PainAssessmentData {
  current_pain: number;
  average_pain_24h: number;
  worst_pain_24h: number;
  least_pain_24h: number;
  pain_interference: number;
}

async recordPainAssessment(
  patientId: string, 
  userId: string, 
  assessmentData: PainAssessmentData
): Promise<AssessmentResult> {
  // TypeScript provides compile-time validation
  return await this.abena.storePatientData(patientId, 'pain_assessment', assessmentData);
}
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check service URLs are correct
   - Verify user credentials
   - Ensure proper permissions

2. **Data Not Found**
   - Verify patient ID exists
   - Check data access permissions
   - Confirm data hasn't been deleted

3. **Privacy Violations**
   - Review privacy policies
   - Check consent status
   - Verify data retention policies

### Getting Help

- **Documentation**: [Abena SDK Docs](https://docs.abena.com/sdk)
- **Support**: [support@abena.com](mailto:support@abena.com)
- **Community**: [Abena Developer Forum](https://forum.abena.com)

## Conclusion

Using the Abena SDK pattern provides significant benefits:

- **Reduced Development Time**: No need to implement auth, privacy, or audit systems
- **Improved Security**: Built-in security features and regular updates
- **Better Compliance**: Automatic compliance with healthcare regulations
- **Easier Maintenance**: Standardized approach across all modules
- **Focus on Business Logic**: Developers can concentrate on application features

By following this pattern, you ensure your application is secure, compliant, and maintainable while reducing development complexity. 