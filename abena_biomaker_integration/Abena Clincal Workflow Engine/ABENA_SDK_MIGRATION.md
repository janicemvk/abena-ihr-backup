# Abena SDK Migration Guide

## Overview

The ClinicalWorkflowEngine has been updated to use the Abena SDK instead of having its own authentication and data management systems. This provides centralized handling of:

- Authentication & permissions
- Privacy & encryption
- Audit logging
- Blockchain integration

## Key Changes

### 1. ClinicalWorkflowEngine Constructor

**BEFORE (❌ Wrong - has its own auth/data):**
```javascript
constructor(moduleRegistry, fhirClient) {
  this.moduleRegistry = moduleRegistry;
  this.fhirClient = fhirClient;
  this.validator = new FHIRValidator();
  this.decisionSupport = new ClinicalDecisionSupport();
  this.stateManager = new WorkflowStateManager();
  // ...
}
```

**AFTER (✅ Correct - uses Abena SDK):**
```javascript
constructor(moduleRegistry, options = {}) {
  this.moduleRegistry = moduleRegistry;
  
  // Initialize Abena SDK with service URLs
  this.abena = new AbenaSDK({
    authServiceUrl: options.authServiceUrl || 'http://localhost:3001',
    dataServiceUrl: options.dataServiceUrl || 'http://localhost:8001',
    privacyServiceUrl: options.privacyServiceUrl || 'http://localhost:8002',
    blockchainServiceUrl: options.blockchainServiceUrl || 'http://localhost:8003'
  });
  
  // Initialize utility classes with Abena SDK configuration
  this.validator = new FHIRValidator(options);
  this.decisionSupport = new ClinicalDecisionSupport(options);
  this.stateManager = new WorkflowStateManager(options);
  // ...
}
```

### 2. Patient Data Access

**BEFORE:**
```javascript
async getPatientData(patientId) {
  return await this.fhirClient.read({ resourceType: 'Patient', id: patientId });
}
```

**AFTER:**
```javascript
async getPatientData(patientId) {
  // Use Abena SDK to get patient data with auto-handled auth & privacy
  return await this.abena.getPatientData(patientId, 'clinical_workflow_engine');
}
```

### 3. Clinical Data Storage

**BEFORE:**
```javascript
async storeWorkflowResults(workflow, summary) {
  // Implementation would create appropriate FHIR resources
}
```

**AFTER:**
```javascript
async storeWorkflowResults(workflow, summary) {
  // Store workflow results using Abena SDK with auto-handled privacy & audit logging
  const workflowResource = {
    resourceType: 'CarePlan',
    // ... FHIR resource structure
  };

  await this.abena.storeClinicalData(workflow.patientId, workflowResource, 'workflow_results');
}
```

### 4. Notifications

**BEFORE:**
```javascript
async notifyClinicalStaff(workflow, eventType) {
  // Notify clinical staff of workflow issues
}
```

**AFTER:**
```javascript
async notifyClinicalStaff(workflow, eventType) {
  // Use Abena SDK to send notifications with auto-handled audit logging
  const notification = {
    type: 'clinical_alert',
    priority: 'high',
    // ... notification structure
  };

  await this.abena.sendNotification(notification, 'clinical_workflow_engine');
}
```

## Updated Utility Classes

### FHIRValidator
- Now uses Abena SDK for FHIR validation
- Auto-handled audit logging for validation operations

### ClinicalDecisionSupport
- Uses Abena SDK to get patient clinical context
- Enhanced privacy handling for clinical data access

### WorkflowStateManager
- Uses Abena SDK for state transition logging
- Auto-handled audit logging for workflow state changes

## Benefits

1. **Centralized Security**: All authentication, authorization, and privacy controls are handled by the Abena SDK
2. **Automatic Audit Logging**: All operations are automatically logged for compliance
3. **Privacy Compliance**: Patient data is automatically encrypted and privacy controls are enforced
4. **Blockchain Integration**: Clinical data can be automatically stored on blockchain for immutability
5. **Simplified Development**: Focus on business logic instead of security infrastructure

## Usage Example

```javascript
import ClinicalWorkflowEngine from './src/ClinicalWorkflowEngine.js';

// Initialize with Abena SDK configuration
const workflowEngine = new ClinicalWorkflowEngine(
  moduleRegistry,
  {
    authServiceUrl: 'http://localhost:3001',
    dataServiceUrl: 'http://localhost:8001',
    privacyServiceUrl: 'http://localhost:8002',
    blockchainServiceUrl: 'http://localhost:8003'
  }
);

// Start a workflow - auth & privacy handled automatically
const workflowId = await workflowEngine.startWorkflow(
  'patient-intake',
  'patient-123',
  { userId: 'clinician-456' }
);

// Route data - all security handled by Abena SDK
const results = await workflowEngine.routePatientData(
  'patient-123',
  'lab-results',
  labData
);
```

## Migration Checklist

- [x] Update ClinicalWorkflowEngine constructor
- [x] Replace FHIR client with Abena SDK
- [x] Update patient data access methods
- [x] Update clinical data storage methods
- [x] Update notification methods
- [x] Update utility classes
- [x] Add proper error handling
- [x] Update documentation
- [x] Create usage examples

## Dependencies

Make sure to install the Abena SDK:

```bash
npm install @abena/sdk
```

## Configuration

The Abena SDK requires configuration for the following services:

- **Auth Service**: Handles authentication and authorization
- **Data Service**: Manages clinical data storage and retrieval
- **Privacy Service**: Handles data encryption and privacy controls
- **Blockchain Service**: Provides blockchain integration for audit trails

All services should be running and accessible before using the ClinicalWorkflowEngine. 