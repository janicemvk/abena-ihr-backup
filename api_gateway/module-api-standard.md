# Abena IHR Module API Standard

This document defines the standard API interface that all Abena IHR modules must implement to ensure consistent integration and communication.

## 🏗️ Standard API Structure

All modules must implement the following base endpoints:

### Health Check
```
GET /health
Response: { "status": "healthy", "module": "module-name", "version": "1.0.0" }
```

### Module Information
```
GET /info
Response: {
  "id": "module-id",
  "name": "Module Name",
  "version": "1.0.0",
  "description": "Module description",
  "endpoints": {
    "health": "/health",
    "info": "/info",
    "api": "/api/v1"
  },
  "dependencies": ["sdk-service", "other-module"],
  "capabilities": ["feature1", "feature2"]
}
```

### API Base Path
```
/api/v1/
```

## 📋 Required Headers

All API requests must include:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
X-Module-ID: <module-id>
X-Request-ID: <uuid>
```

## 🔄 Standard Response Format

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2024-01-01T00:00:00Z",
  "requestId": "uuid",
  "errors": null
}
```

## 🚨 Error Response Format

```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "timestamp": "2024-01-01T00:00:00Z",
  "requestId": "uuid",
  "errors": [
    {
      "code": "ERROR_CODE",
      "field": "field_name",
      "message": "Detailed error message"
    }
  ]
}
```

## 📊 Module-Specific API Endpoints

### 1. 12 Core Background Modules

```javascript
// Start all modules
POST /api/v1/modules/start
Body: { patientId: "string", userId: "string" }

// Get comprehensive analysis
GET /api/v1/analysis
Query: { patientId: "string", includeEcbome: boolean }

// Stop all modules
POST /api/v1/modules/stop
Body: { patientId: "string" }

// Get module status
GET /api/v1/modules/status
Query: { patientId: "string" }
```

### 2. Abena IHR Main System

```javascript
// Patient management
GET /api/v1/patients
POST /api/v1/patients
GET /api/v1/patients/{patientId}
PUT /api/v1/patients/{patientId}

// Clinical outcomes
GET /api/v1/outcomes
POST /api/v1/outcomes
GET /api/v1/outcomes/{outcomeId}
PUT /api/v1/outcomes/{outcomeId}

// Analytics
GET /api/v1/analytics/patient/{patientId}
GET /api/v1/analytics/outcomes
POST /api/v1/analytics/reports
```

### 3. Business Rule Engine

```javascript
// Rule management
GET /api/v1/rules
POST /api/v1/rules
GET /api/v1/rules/{ruleId}
PUT /api/v1/rules/{ruleId}
DELETE /api/v1/rules/{ruleId}

// Conflict resolution
POST /api/v1/conflicts/process
GET /api/v1/conflicts/{conflictId}
PUT /api/v1/conflicts/{conflictId}/resolve

// Decision support
POST /api/v1/decisions/evaluate
GET /api/v1/decisions/{decisionId}
```

### 4. Telemedicine Platform

```javascript
// Appointment management
GET /api/v1/appointments
POST /api/v1/appointments
GET /api/v1/appointments/{appointmentId}
PUT /api/v1/appointments/{appointmentId}

// Consultations
POST /api/v1/consultations/start
GET /api/v1/consultations/{consultationId}
PUT /api/v1/consultations/{consultationId}/end

// Recordings
GET /api/v1/recordings/{consultationId}
POST /api/v1/recordings/upload
```

### 5. eCdome Intelligence System

```javascript
// Analysis
POST /api/v1/analysis/ecbome
GET /api/v1/analysis/{analysisId}

// Pattern recognition
GET /api/v1/patterns/{patientId}
POST /api/v1/patterns/detect

// Predictions
GET /api/v1/predictions/{patientId}
POST /api/v1/predictions/generate
```

### 6. Biomarker Integration

```javascript
// Lab results
GET /api/v1/lab-results/{patientId}
POST /api/v1/lab-results/ingest
PUT /api/v1/lab-results/{resultId}

// Biomarkers
GET /api/v1/biomarkers/{patientId}
POST /api/v1/biomarkers/process
GET /api/v1/biomarkers/trends/{patientId}

// Integration
POST /api/v1/integration/sync
GET /api/v1/integration/status
```

### 7. Provider Workflow Integration

```javascript
// Workflows
GET /api/v1/workflows
POST /api/v1/workflows
GET /api/v1/workflows/{workflowId}
PUT /api/v1/workflows/{workflowId}

// Tasks
GET /api/v1/tasks/{providerId}
POST /api/v1/tasks
PUT /api/v1/tasks/{taskId}/complete

// Automation
POST /api/v1/automation/trigger
GET /api/v1/automation/rules
```

### 8. Unified Integration Layer

```javascript
// Orchestration
POST /api/v1/orchestration/coordinate
GET /api/v1/orchestration/status

// Coordination
POST /api/v1/coordination/sync
GET /api/v1/coordination/status

// Integration
POST /api/v1/integration/connect
GET /api/v1/integration/health
```

## 🔐 Authentication & Authorization

All modules must use the shared Abena SDK for authentication:

```javascript
const { AbenaSDK } = require('@abena/sdk');

const sdk = new AbenaSDK({
    authServiceUrl: process.env.AUTH_SERVICE_URL,
    dataServiceUrl: process.env.DATA_SERVICE_URL,
    privacyServiceUrl: process.env.PRIVACY_SERVICE_URL,
    blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL
});

// Verify requests
app.use(async (req, res, next) => {
    try {
        await sdk.verifyRequest(req);
        next();
    } catch (error) {
        res.status(401).json({ error: 'Unauthorized' });
    }
});
```

## 📡 Inter-Module Communication

Modules can communicate with each other using the SDK:

```javascript
// Call another module's API
const response = await sdk.callModuleAPI('background-modules', '/api/v1/analysis', {
    patientId: 'patient-123'
});

// Subscribe to events from other modules
await sdk.subscribeToModuleEvents('background-modules', 'analysis_complete', (data) => {
    // Handle event
});
```

## 🧪 Testing Requirements

Each module must provide:

1. **Health check endpoint** for monitoring
2. **Integration tests** for API endpoints
3. **Mock data** for development
4. **Documentation** for all endpoints

## 📈 Monitoring & Logging

All modules must implement:

```javascript
// Structured logging
const logger = sdk.getLogger();

logger.info('Operation completed', {
    module: 'module-name',
    operation: 'operation-name',
    patientId: 'patient-123',
    duration: 150
});

// Metrics collection
await sdk.recordMetric('api_request_duration', 150, {
    endpoint: '/api/v1/analysis',
    module: 'background-modules'
});
```

## 🚀 Deployment Requirements

Each module must provide:

1. **Dockerfile** for containerization
2. **docker-compose.yml** for local development
3. **Environment variables** configuration
4. **Health check** for container orchestration

## 📋 Implementation Checklist

- [ ] Implement standard health check endpoint
- [ ] Implement module info endpoint
- [ ] Use Abena SDK for authentication
- [ ] Follow standard response format
- [ ] Implement proper error handling
- [ ] Add structured logging
- [ ] Provide API documentation
- [ ] Include integration tests
- [ ] Create Docker configuration
- [ ] Register with module registry 