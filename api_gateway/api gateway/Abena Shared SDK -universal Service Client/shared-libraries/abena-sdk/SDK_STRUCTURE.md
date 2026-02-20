# Abena SDK Structure

## Overview
The Abena SDK is a comprehensive TypeScript library that provides a unified interface for all Abena IHR (Integrated Health Records) modules. It handles authentication, data access, privacy controls, and blockchain audit logging.

## Directory Structure

```
shared-libraries/abena-sdk/
├── src/
│   ├── index.ts              # Main SDK implementation
│   ├── types.ts              # TypeScript interfaces and types
│   └── __tests__/
│       └── sdk.test.ts       # Unit tests
├── examples/
│   └── basic-usage.ts        # Usage examples
├── package.json              # NPM package configuration
├── tsconfig.json             # TypeScript configuration
├── jest.config.js            # Jest testing configuration
├── .eslintrc.js              # ESLint configuration
├── .gitignore                # Git ignore rules
├── README.md                 # Comprehensive documentation
├── LICENSE                   # MIT license
├── demo.js                   # Simple demo script
└── SDK_STRUCTURE.md          # This file
```

## Core Components

### 1. Main SDK (`src/index.ts`)
- **AbenaSDK Class**: Main SDK class with all functionality
- **Service Clients**: Axios instances for each service (auth, data, privacy, blockchain)
- **Authentication Methods**: Login, token verification, access validation
- **Data Access Methods**: Patient data retrieval with access control
- **Privacy & Security**: Encryption, anonymization, consent management
- **Blockchain Methods**: Audit logging, data integrity verification
- **Data Ingestion**: Support for HL7, FHIR, and custom formats
- **Convenience Methods**: Module-specific helpers for clinical and analytics use cases

### 2. Types (`src/types.ts`)
- **Interfaces**: All TypeScript interfaces for data structures
- **Error Classes**: Custom error types for better error handling
- **Type Definitions**: Comprehensive type definitions for all SDK features

### 3. Testing (`src/__tests__/sdk.test.ts`)
- **Unit Tests**: Comprehensive test coverage for all SDK methods
- **Mocking**: Axios mocking for isolated testing
- **Test Scenarios**: Authentication, data access, privacy, blockchain, utilities

## Key Features

### 🔐 Authentication
- Single sign-on across all services
- MFA support
- Token management
- Access validation

### 📊 Data Access
- Unified patient data access
- Automatic access control
- Emergency access support
- Record filtering and pagination

### 🛡️ Privacy & Security
- Data encryption/decryption
- Dataset anonymization (k-anonymity, differential privacy)
- Consent management
- Risk scoring

### ⛓️ Blockchain Audit
- Immutable audit trail
- Data integrity verification
- Access logging
- Transaction tracking

### 🔄 Data Ingestion
- HL7 message support
- FHIR resource ingestion
- Vital signs and lab results
- Custom data formats

### 📈 Analytics
- Secure anonymized datasets
- Research-ready data
- Privacy-preserving analytics
- Cohort analysis support

## Service Architecture

The SDK connects to four main services:

1. **Authentication Service** (`authServiceUrl`)
   - User authentication and authorization
   - Access control validation
   - Token management

2. **Data Service** (`dataServiceUrl`)
   - Patient data storage and retrieval
   - Health records management
   - Data ingestion endpoints

3. **Privacy Service** (`privacyServiceUrl`)
   - Data encryption/decryption
   - Anonymization algorithms
   - Consent management

4. **Blockchain Service** (`blockchainServiceUrl`)
   - Audit trail logging
   - Data integrity verification
   - Immutable record keeping

## Usage Patterns

### Clinical Modules
```typescript
const context = await sdk.getCompletePatientContext(
  patientId, userId, 'clinical_care'
);
```

### Analytics Modules
```typescript
const dataset = await sdk.getAnonymizedDataset(
  criteria, anonymizationConfig
);
```

### Emergency Access
```typescript
const emergencyData = await sdk.getCompletePatientContext(
  patientId, userId, 'emergency_care', true
);
```

## Development Workflow

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Build SDK**
   ```bash
   npm run build
   ```

3. **Run Tests**
   ```bash
   npm test
   npm run test:coverage
   ```

4. **Lint Code**
   ```bash
   npm run lint
   ```

5. **Development Mode**
   ```bash
   npm run dev
   ```

## Configuration

The SDK requires configuration for all four services:

```typescript
const sdk = new AbenaSDK({
  authServiceUrl: 'https://auth.abena.health',
  dataServiceUrl: 'https://data.abena.health',
  privacyServiceUrl: 'https://privacy.abena.health',
  blockchainServiceUrl: 'https://blockchain.abena.health',
  timeout: 30000
});
```

## Error Handling

The SDK provides comprehensive error handling:

- **AccessDeniedError**: When access is denied
- **ServiceUnavailableError**: When services are down
- **ValidationError**: For invalid input data
- **AbenaSDKError**: Base error class for all SDK errors

## Security Features

- **Automatic Access Control**: All data access is validated
- **Encryption**: Sensitive data is automatically encrypted
- **Audit Logging**: All access is logged to blockchain
- **Consent Management**: Patient consent is verified
- **Risk Scoring**: Access requests are risk-assessed

## Performance Considerations

- **Connection Pooling**: Axios instances are reused
- **Timeout Configuration**: Configurable timeouts per service
- **Graceful Degradation**: Blockchain failures don't break main operations
- **Caching**: Auth tokens are cached for performance

## Future Enhancements

- **WebSocket Support**: Real-time data updates
- **Offline Mode**: Local data caching
- **Batch Operations**: Bulk data processing
- **Custom Protocols**: Additional healthcare data formats
- **Mobile SDK**: React Native and Flutter versions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details. 