# Business Rule Engine (Abena SDK)

A comprehensive business rule engine for handling application-specific conflict policies and business logic, designed for healthcare and enterprise applications. Built on the Abena SDK for seamless integration with authentication, data management, privacy controls, and blockchain audit trails.

## Features

- **Abena SDK Integration**: Seamless integration with Abena services for auth, data, privacy, and blockchain
- **Rule Management**: Add, update, enable/disable business rules with full audit trails
- **Conflict Resolution**: Process data conflicts with intelligent resolution strategies
- **Rule Categories**: Clinical, Administrative, Regulatory, and Privacy rules
- **Priority-based Processing**: Execute rules in priority order
- **Metadata Support**: Rich metadata for rule targeting and filtering
- **Export/Import**: Backup and transfer rule configurations
- **Statistics**: Track rule usage and performance
- **Error Handling**: Robust error handling with detailed logging
- **Privacy Controls**: Automatic privacy compliance and data protection
- **Blockchain Audit**: Immutable audit trails for all operations

## Installation

```bash
npm install business-rule-engine
```

Or clone the repository:

```bash
git clone https://github.com/yourusername/business-rule-engine.git
cd business-rule-engine
npm install
```

## Quick Start

```javascript
import BusinessRuleEngine from './BusinessRuleEngine.js';

// Create a new rule engine instance with Abena SDK
const ruleEngine = new BusinessRuleEngine({
    authServiceUrl: 'http://localhost:3001',
    dataServiceUrl: 'http://localhost:8001',
    privacyServiceUrl: 'http://localhost:8002',
    blockchainServiceUrl: 'http://localhost:8003'
});

// Process a conflict with user authentication
const conflictData = {
    id: 'CONFLICT_001',
    type: 'medication_dosage',
    patientId: 'P12345',
    conflictingValues: [
        { value: '10mg', timestamp: '2025-06-19T10:00:00Z', source: 'ehr' },
        { value: '15mg', timestamp: '2025-06-19T11:00:00Z', source: 'pharmacy' }
    ],
    previousDosage: 5
};

const result = await ruleEngine.processConflict(conflictData, 'USER_12345');
console.log(result);
```

## Running Examples

```bash
# Run the comprehensive example
npm start

# Or run directly
node example.js
```

## API Reference

### Constructor

```javascript
const ruleEngine = new BusinessRuleEngine(config);
```

Creates a new Business Rule Engine instance with Abena SDK integration.

**Configuration Options:**
- `authServiceUrl` (String): Abena Auth Service URL
- `dataServiceUrl` (String): Abena Data Service URL
- `privacyServiceUrl` (String): Abena Privacy Service URL
- `blockchainServiceUrl` (String): Abena Blockchain Service URL

### Core Methods

#### `addRule(ruleConfig, userId)`

Adds a new business rule to the engine with Abena data service integration.

**Parameters:**
- `ruleConfig` (Object): Rule configuration object
- `userId` (String): User ID for authentication and audit trails

**Rule Configuration Properties:**
- `id` (String, optional): Unique rule identifier
- `name` (String): Human-readable rule name
- `category` (String): Rule category (clinical, administrative, regulatory, privacy)
- `description` (String): Rule description
- `condition` (Function): Function that returns boolean to determine if rule applies
- `action` (Function): Async function to execute when rule fires (receives Abena SDK instance)
- `priority` (Number, optional): Rule priority (lower = higher priority, default: 5)
- `enabled` (Boolean, optional): Whether rule is enabled (default: true)
- `metadata` (Object, optional): Additional metadata for rule targeting

**Returns:** Promise<String> - Rule ID

**Example:**
```javascript
const ruleId = await ruleEngine.addRule({
    id: 'custom_rule',
    name: 'Custom Conflict Resolution',
    category: ruleEngine.ruleCategories.CLINICAL,
    description: 'Handle custom conflicts',
    condition: (data) => data.type === 'custom_type',
    action: async (data, abena) => {
        // Access patient data with privacy controls
        const patientData = await abena.getPatientData(data.patientId, 'custom_purpose');
        return { resolution: 'custom_action' };
    },
    priority: 1,
    metadata: {
        conflictTypes: ['custom_type'],
        dataSources: ['system_a', 'system_b']
    }
}, 'USER_12345');
```

#### `processConflict(conflictData, userId)`

Processes a conflict through all applicable rules with Abena integration.

**Parameters:**
- `conflictData` (Object): Conflict data to process
- `userId` (String): User ID for authentication and audit trails

**Conflict Data Properties:**
- `id` (String): Unique conflict identifier
- `type` (String): Conflict type
- `patientId` (String): Patient identifier
- `conflictingValues` (Array): Array of conflicting values
- `sources` (Array, optional): Data sources involved
- Additional properties as needed by specific rules

**Returns:** Promise<Object> - Processing results with blockchain audit trail

**Example:**
```javascript
const result = await ruleEngine.processConflict({
    id: 'CONFLICT_001',
    type: 'medication_dosage',
    patientId: 'P12345',
    conflictingValues: [
        { value: '10mg', timestamp: '2025-06-19T10:00:00Z', source: 'ehr' },
        { value: '15mg', timestamp: '2025-06-19T11:00:00Z', source: 'pharmacy' }
    ]
}, 'USER_12345');
```

#### `updateRule(ruleId, updates, userId)`

Updates an existing rule with Abena data service integration.

**Parameters:**
- `ruleId` (String): Rule identifier
- `updates` (Object): Properties to update
- `userId` (String): User ID for authentication and audit trails

**Returns:** Promise<Boolean> - Success status

#### `toggleRule(ruleId, enabled, userId)`

Enables or disables a rule with Abena data service integration.

**Parameters:**
- `ruleId` (String): Rule identifier
- `enabled` (Boolean): Enable/disable status
- `userId` (String): User ID for authentication and audit trails

**Returns:** Promise<Boolean> - Success status

### Utility Methods

#### `getRulesByCategory(category, userId)`

Gets all rules in a specific category with Abena data service integration.

**Parameters:**
- `category` (String): Rule category
- `userId` (String): User ID for authentication

**Returns:** Promise<Array> - Rules in the category

#### `getRuleStats(userId)`

Gets rule engine statistics with Abena data service integration.

**Parameters:**
- `userId` (String): User ID for authentication

**Returns:** Promise<Object> - Statistics including total rules, enabled rules, and counts by category

#### `exportRules(userId)`

Exports all rules for backup/transfer with Abena data service integration.

**Parameters:**
- `userId` (String): User ID for authentication

**Returns:** Promise<Array> - All rule configurations

#### `importRules(rulesArray, userId)`

Imports rules from backup with Abena data service integration.

**Parameters:**
- `rulesArray` (Array): Array of rule configurations
- `userId` (String): User ID for authentication

#### `getConflictHistory(patientId, userId)`

Gets conflict processing history for a patient with privacy controls.

**Parameters:**
- `patientId` (String): Patient identifier
- `userId` (String): User ID for authentication

**Returns:** Promise<Array> - Conflict processing history

#### `getRuleAuditTrail(ruleId, userId)`

Gets audit trail for rule changes with blockchain integration.

**Parameters:**
- `ruleId` (String): Rule identifier
- `userId` (String): User ID for authentication

**Returns:** Promise<Array> - Audit trail entries

## Default Rules

The engine comes with several pre-configured rules that integrate with Abena services:

### Clinical Rules

1. **Medication Dosage Conflict Resolution**
   - Handles conflicts in medication dosages between systems
   - Integrates with Abena data service for patient medication history
   - Prefers most recent prescription
   - Flags for physician review if dosage increase > 2x

2. **Lab Result Value Conflict**
   - Handles conflicts in lab result values
   - Integrates with Abena data service for patient lab history
   - Uses average if values within 10% variance
   - Flags for review if high variance

### Administrative Rules

3. **Patient Demographics Conflict**
   - Handles conflicts in patient demographic information
   - Integrates with Abena data service for patient demographic history
   - Requires manual review for critical fields (DOB, SSN, MRN)
   - Uses most recent value for non-critical fields

### Privacy Rules

4. **Privacy Consent Conflict Resolution**
   - Handles conflicts in patient privacy and consent settings
   - Integrates with Abena privacy service for patient privacy settings
   - Always uses most restrictive privacy settings
   - Requires audit trail via blockchain

## Abena SDK Integration

The Business Rule Engine leverages the Abena SDK for:

### Authentication & Authorization
- Automatic user authentication and permission checking
- Role-based access control for rule management
- Secure API access with JWT tokens

### Data Management
- Centralized data storage with privacy controls
- Automatic data encryption and decryption
- Version control and data lineage tracking

### Privacy Controls
- Automatic privacy compliance checking
- Patient consent validation
- Data anonymization and pseudonymization

### Blockchain Audit
- Immutable audit trails for all operations
- Tamper-proof logging of rule changes
- Transparent conflict resolution history

## Rule Categories

- **CLINICAL**: Medical and clinical decision rules
- **ADMINISTRATIVE**: Administrative and operational rules
- **REGULATORY**: Compliance and regulatory rules
- **PRIVACY**: Privacy and consent management rules

## Conflict Types

The engine supports various conflict types:

- `medication_dosage`: Medication dosage conflicts
- `lab_result`: Laboratory result conflicts
- `patient_demographics`: Patient demographic conflicts
- `privacy_consent`: Privacy and consent conflicts
- Custom types can be added as needed

## Data Sources

Supported data sources include:

- `ehr`: Electronic Health Record
- `pharmacy`: Pharmacy system
- `lab_system`: Laboratory system
- `registration`: Registration system
- `insurance`: Insurance system
- `patient_portal`: Patient portal
- `manual_entry`: Manual data entry
- `provider_input`: Provider input
- `legal`: Legal system

## Error Handling

The engine includes robust error handling:

- Rule execution errors are caught and logged
- Failed rules don't stop processing of other rules
- Error details are included in processing results
- Graceful degradation when rules fail
- Automatic retry mechanisms for transient failures

## Performance Considerations

- Rules are executed in priority order
- Processing stops when a rule indicates `stopProcessing: true`
- Rule filtering is optimized for performance
- Large rule sets are supported efficiently
- Abena SDK provides caching and optimization

## Security & Compliance

- HIPAA compliance through Abena privacy service
- GDPR compliance with automatic consent management
- SOC 2 Type II compliance with audit trails
- End-to-end encryption for all data
- Zero-knowledge architecture for sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the examples
- Contact Abena SDK support

## Version History

- **2.0.0**: Abena SDK integration
  - Full Abena SDK integration
  - Async/await patterns
  - Blockchain audit trails
  - Privacy controls
  - Enhanced security
- **1.0.0**: Initial release with core functionality
  - Rule management
  - Conflict processing
  - Default clinical rules
  - Export/import functionality 