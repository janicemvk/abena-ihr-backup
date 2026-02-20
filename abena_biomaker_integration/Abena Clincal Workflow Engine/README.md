# Abena Clinical Workflow Engine

A sophisticated clinical workflow engine designed to automate and manage healthcare processes while ensuring compliance with clinical standards and best practices. Built on the Abena SDK for centralized security, privacy, and audit logging.

## Features

- **Workflow Management**: Define, execute, and monitor clinical workflows
- **Clinical Decision Support**: Integrated rules engine for clinical decision making
- **FHIR Integration**: Native support for FHIR resources and validation via Abena SDK
- **State Management**: Robust workflow state tracking and history
- **Multi-modal Care**: Support for traditional and alternative medicine workflows
- **Error Handling**: Comprehensive error management and recovery
- **Real-time Monitoring**: Active workflow monitoring and alerts
- **Security & Privacy**: Auto-handled authentication, encryption, and audit logging via Abena SDK

## Standard Workflows

1. **Patient Intake**
   - Demographics collection
   - Insurance verification
   - Medical history
   - Initial assessment
   - Care plan generation

2. **Lab Results Processing**
   - Result ingestion
   - Validation
   - Clinical interpretation
   - Provider notification
   - Patient notification

3. **Medication Management**
   - Prescription validation
   - Drug interaction checking
   - Allergy verification
   - Dosage calculation
   - Prescription routing

4. **Comprehensive Care**
   - Traditional assessment
   - TCM evaluation
   - Ayurveda evaluation
   - Functional medicine analysis
   - Nutrition assessment
   - Integrated care planning

## Installation

```bash
npm install
```

## Usage

```javascript
import ClinicalWorkflowEngine from './src/ClinicalWorkflowEngine';

// Initialize the engine with Abena SDK configuration
const engine = new ClinicalWorkflowEngine(moduleRegistry, {
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
});

// Start a workflow (auth & privacy handled automatically)
const workflowId = await engine.startWorkflow('patient-intake', 'patient123', {
  userId: 'clinician-456',
  priority: 'high',
  context: { /* additional context */ }
});

// Route patient data (all security handled by Abena SDK)
const results = await engine.routePatientData('patient123', 'lab-results', labData);

// Monitor workflow status
const status = engine.getWorkflowStatus(workflowId);
```

## Dependencies

- **@abena/sdk**: Centralized authentication, privacy, audit logging, and blockchain integration

## Development

```bash
# Run tests
npm test

# Lint code
npm run lint
```

## Architecture

The engine consists of several key components:

1. **Core Engine**: Main workflow orchestration with Abena SDK integration
2. **FHIR Validator**: FHIR resource validation via Abena SDK
3. **Clinical Decision Support**: Clinical rules engine with privacy-aware data access
4. **State Manager**: Workflow state tracking with audit logging

## Abena SDK Services

The engine requires the following Abena services to be running:

- **Auth Service** (port 3001): Handles authentication and authorization
- **Data Service** (port 8001): Manages clinical data storage and retrieval
- **Privacy Service** (port 8002): Handles data encryption and privacy controls
- **Blockchain Service** (port 8003): Provides blockchain integration for audit trails

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For support, please open an issue in the GitHub repository. 