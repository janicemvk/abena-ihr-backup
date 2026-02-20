# Smart Contracts

This directory contains smart contracts for the Abena IHR blockchain service, providing immutable audit trails, consent management, and data integrity verification for healthcare records.

## Overview

The smart contracts are built using Hyperledger Fabric's contract API and provide the following key functionalities:

- **Health Record Management**: Create, read, update, and verify health records
- **Consent Management**: Grant and revoke patient consent for data access
- **Audit Logging**: Immutable audit trails for all blockchain operations
- **Data Integrity**: Cryptographic verification of data integrity
- **Access Control**: Role-based access control for healthcare data

## Files

### `health_record_contract.go`

The main smart contract for managing health records on the blockchain.

#### Key Features

- **Health Record Operations**:
  - `CreateHealthRecord`: Create new health records with consent verification
  - `GetHealthRecord`: Retrieve health records by ID
  - `UpdateHealthRecord`: Update existing health records with version control
  - `GetLatestHealthRecord`: Get the most recent health record for a patient

- **Consent Management**:
  - `GrantConsent`: Grant consent for data access with scope and expiry
  - `RevokeConsent`: Revoke previously granted consent
  - `GetConsentStatus`: Check current consent status

- **Data Integrity**:
  - `VerifyDataIntegrity`: Verify the integrity of health records
  - Cryptographic hashing and chain linking
  - Version control and audit trails

- **Audit Logging**:
  - Automatic audit log creation for all operations
  - `GetAuditTrail`: Retrieve complete audit trail for any resource
  - Immutable audit records with transaction IDs

#### Data Structures

- **HealthRecord**: Complete health record with metadata
- **ConsentRecord**: Patient consent information with expiry
- **AuditLog**: Immutable audit trail entries

#### Security Features

- Cryptographic hashing for data integrity
- Chain linking for tamper detection
- Role-based access control
- Consent verification before data access
- Immutable audit trails

## Usage

### Deploying the Contract

```bash
# Build the contract
go build -o health_record_contract

# Deploy to Hyperledger Fabric network
peer lifecycle chaincode package health_record_contract.tar.gz \
  --path ./smart_contracts \
  --lang golang \
  --label health_record_contract_1.0

peer lifecycle chaincode install health_record_contract.tar.gz
```

### Creating a Health Record

```go
// Create a new health record
err := contract.CreateHealthRecord(
    ctx,
    "patient123",
    "provider456",
    "vitals",
    encryptedData,
    dataHash,
    true, // consent granted
    map[string]string{"priority": "high"}
)
```

### Granting Consent

```go
// Grant consent for data access
err := contract.GrantConsent(
    ctx,
    "patient123",
    "provider456",
    "treatment",
    "vitals,medications",
    time.Now().AddDate(0, 6, 0) // 6 months expiry
)
```

### Verifying Data Integrity

```go
// Verify data integrity
isValid, err := contract.VerifyDataIntegrity(ctx, "record123")
if err != nil {
    log.Printf("Error verifying integrity: %v", err)
}
if isValid {
    log.Println("Data integrity verified")
}
```

## Configuration

The smart contract supports various configuration options:

- **Consent Types**: Treatment, research, billing, etc.
- **Access Scopes**: Specific data types or broad access
- **Expiry Periods**: Configurable consent expiry times
- **Audit Levels**: Detailed or summary audit logging

## Security Considerations

1. **Data Encryption**: All health data should be encrypted before storage
2. **Access Control**: Implement proper role-based access control
3. **Consent Verification**: Always verify consent before data access
4. **Audit Trails**: Maintain complete audit trails for compliance
5. **Key Management**: Secure key management for cryptographic operations

## Compliance

The smart contract is designed to comply with:

- **HIPAA**: Health Insurance Portability and Accountability Act
- **GDPR**: General Data Protection Regulation
- **HITECH**: Health Information Technology for Economic and Clinical Health
- **Local Healthcare Regulations**: Various regional healthcare data protection laws

## Testing

```bash
# Run unit tests
go test ./smart_contracts

# Run integration tests
go test ./smart_contracts -tags=integration

# Run with coverage
go test ./smart_contracts -cover
```

## Development

### Adding New Functions

1. Define the function in the contract struct
2. Implement proper validation and error handling
3. Add audit logging for the operation
4. Update documentation and tests

### Best Practices

- Always validate input parameters
- Implement proper error handling
- Create audit logs for all operations
- Use cryptographic hashing for data integrity
- Follow Hyperledger Fabric best practices
- Maintain backward compatibility

## Troubleshooting

### Common Issues

1. **Transaction Failures**: Check consent status and access permissions
2. **Data Integrity Errors**: Verify cryptographic hashes and chain links
3. **Performance Issues**: Optimize queries and use proper indexing
4. **Network Issues**: Check peer connectivity and consensus status

### Debugging

Enable debug logging in the contract configuration:

```go
// Enable debug mode
contract.SetDebugMode(true)
```

## Support

For issues and questions:

1. Check the main blockchain service documentation
2. Review Hyperledger Fabric documentation
3. Contact the development team
4. Submit issues through the project repository 