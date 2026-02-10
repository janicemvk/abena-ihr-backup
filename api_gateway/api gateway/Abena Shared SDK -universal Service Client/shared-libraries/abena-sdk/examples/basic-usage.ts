import AbenaSDK from '../src/index';

// Example: Basic SDK usage for clinical applications

async function basicUsageExample() {
  // Initialize the SDK
  const sdk = new AbenaSDK({
    authServiceUrl: 'https://auth.abena.health',
    dataServiceUrl: 'https://data.abena.health',
    privacyServiceUrl: 'https://privacy.abena.health',
    blockchainServiceUrl: 'https://blockchain.abena.health',
    timeout: 30000
  });

  try {
    // 1. Login to the system
    console.log('Logging in...');
    const { user, token } = await sdk.login('doctor@hospital.com', 'secure-password');
    console.log('Logged in as:', user.firstName, user.lastName);

    // 2. Check service health
    console.log('Checking service health...');
    const healthStatus = await sdk.healthCheck();
    console.log('Service health:', healthStatus);

    // 3. Get complete patient context
    console.log('Getting patient context...');
    const patientContext = await sdk.getCompletePatientContext(
      'patient-12345',
      user.id,
      'clinical_care'
    );

    console.log('Patient data retrieved successfully');
    console.log('Number of health records:', patientContext.healthRecords.length);
    console.log('Number of medications:', patientContext.medications.length);
    console.log('Risk score:', patientContext.auditInfo.riskScore);

    // 4. Get specific health records
    console.log('Getting recent lab results...');
    const labResults = await sdk.getPatientHealthRecords('patient-12345', {
      recordType: 'lab_result',
      dateFrom: '2023-01-01',
      dateTo: '2023-12-31'
    });

    console.log('Recent lab results:', labResults.length);

    // 5. Check patient consent
    console.log('Checking patient consent...');
    const hasConsent = await sdk.checkPatientConsent(
      'patient-12345',
      user.id,
      'clinical_care'
    );
    console.log('Patient consent granted:', hasConsent);

    // 6. Encrypt sensitive data
    console.log('Encrypting sensitive data...');
    const sensitiveData = {
      ssn: '123-45-6789',
      diagnosis: 'Hypertension'
    };
    
    const encryptedData = await sdk.encryptSensitiveData(
      sensitiveData,
      'demographics',
      'patient-12345'
    );
    console.log('Data encrypted successfully');

    // 7. Get audit trail
    console.log('Getting audit trail...');
    const auditTrail = await sdk.getAuditTrail('patient-12345');
    console.log('Audit trail entries:', auditTrail.length);

  } catch (error) {
    console.error('Error occurred:', error.message);
    
    if (error.message.includes('Access denied')) {
      console.error('Access control error - check permissions');
    } else if (error.message.includes('Service unavailable')) {
      console.error('Service availability error - check network connectivity');
    }
  }
}

// Example: Analytics usage
async function analyticsExample() {
  const sdk = new AbenaSDK({
    authServiceUrl: 'https://auth.abena.health',
    dataServiceUrl: 'https://data.abena.health',
    privacyServiceUrl: 'https://privacy.abena.health',
    blockchainServiceUrl: 'https://blockchain.abena.health'
  });

  try {
    // Login as researcher
    const { user } = await sdk.login('researcher@hospital.com', 'research-password');

    // Get anonymized dataset for research
    const anonymizedDataset = await sdk.getAnonymizedDataset(
      {
        patientCohort: ['patient-1', 'patient-2', 'patient-3'],
        dateRange: { from: '2023-01-01', to: '2023-12-31' },
        recordTypes: ['medication', 'lab_result'],
        includeFields: ['age', 'gender', 'diagnosis', 'medication_name']
      },
      {
        type: 'differential-privacy',
        epsilon: 1.0
      }
    );

    console.log('Anonymized dataset size:', anonymizedDataset.length);
    console.log('Dataset ready for analysis');

  } catch (error) {
    console.error('Analytics error:', error.message);
  }
}

// Example: Emergency access
async function emergencyAccessExample() {
  const sdk = new AbenaSDK({
    authServiceUrl: 'https://auth.abena.health',
    dataServiceUrl: 'https://data.abena.health',
    privacyServiceUrl: 'https://privacy.abena.health',
    blockchainServiceUrl: 'https://blockchain.abena.health'
  });

  try {
    // Login as emergency physician
    const { user } = await sdk.login('emergency@hospital.com', 'emergency-password');

    // Emergency access to patient data
    const emergencyContext = await sdk.getCompletePatientContext(
      'patient-12345',
      user.id,
      'emergency_care',
      true // emergency access flag
    );

    console.log('Emergency access granted');
    console.log('Patient allergies:', emergencyContext.allergies);
    console.log('Current medications:', emergencyContext.medications);

  } catch (error) {
    console.error('Emergency access error:', error.message);
  }
}

export { basicUsageExample, analyticsExample, emergencyAccessExample }; 