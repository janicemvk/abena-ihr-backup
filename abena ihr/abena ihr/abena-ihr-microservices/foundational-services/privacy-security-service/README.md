# Abena IHR Privacy & Security Service

A comprehensive privacy and security service for the Abena IHR microservices architecture, providing data encryption, anonymization, access control, and audit functionality.

## Features

### 🔐 Encryption & Key Management
- **Symmetric Encryption**: AES-256 encryption for data at rest and in transit
- **Asymmetric Encryption**: RSA-2048 for key exchange and digital signatures
- **Key Rotation**: Automated encryption key rotation with configurable intervals
- **Hardware Security Module (HSM) Support**: Optional HSM integration for enhanced security

### 🕵️ Data Anonymization
- **K-Anonymity**: Ensures each record is indistinguishable from at least k-1 other records
- **Differential Privacy**: Adds calibrated noise to protect individual privacy
- **Pseudonymization**: Creates consistent pseudonyms for patient data
- **PHI Redaction**: Automatic detection and redaction of Protected Health Information

### 🔒 Access Control
- **Role-Based Access Control (RBAC)**: Granular permissions based on user roles
- **Patient-Provider Relationships**: Dynamic access based on care relationships
- **Emergency Access**: Time-limited emergency access with audit trails
- **Risk-Based Authentication**: Dynamic risk scoring for access decisions

### 📊 Audit & Compliance
- **Comprehensive Audit Logging**: All security events logged with context
- **Compliance Reporting**: Built-in reports for HIPAA, GDPR, and other regulations
- **Data Retention Policies**: Automated data lifecycle management
- **Security KPIs**: Real-time security metrics and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Privacy & Security Service               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Encryption  │  │Anonymization│  │Access Control│        │
│  │   Manager   │  │   Manager   │  │   Manager   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Audit     │  │   Consent   │  │   Key       │        │
│  │   Logger    │  │  Management │  │ Management  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+

### Environment Setup

1. **Clone the repository**
```bash
cd abena-ihr-microservices/foundational-services/privacy-security-service
```

2. **Set environment variables**
```bash
# Create .env file
cp .env.example .env

# Generate master encryption key
export MASTER_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "MASTER_KEY=$MASTER_KEY" >> .env
```

3. **Start the service**
```bash
# Using Docker Compose
docker-compose up -d

# Or run locally
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Database Setup

The service will automatically create the database schema on first run. For manual setup:

```bash
# Connect to PostgreSQL
psql -h localhost -p 5433 -U postgres -d abena_ihr_security

# Run schema
\i schema.sql
```

## API Endpoints

### Health Check
```http
GET /health
```

### Encryption Operations
```http
POST /encrypt
Content-Type: application/json

{
  "data": "sensitive patient data",
  "data_type": "patient_medical_record",
  "patient_id": "PAT123",
  "purpose": "storage",
  "retention_period": 2555
}
```

```http
POST /decrypt
Content-Type: application/json

{
  "encrypted_data": "gAAAAABk...",
  "encryption_key_id": "uuid-here",
  "purpose": "clinical_review"
}
```

### Anonymization Operations
```http
POST /anonymize
Content-Type: application/json

{
  "dataset": [
    {"age": 45, "zip_code": "12345", "diagnosis": "diabetes"},
    {"age": 47, "zip_code": "12345", "diagnosis": "hypertension"}
  ],
  "anonymization_type": "k-anonymity",
  "quasi_identifiers": ["age", "zip_code"],
  "k_value": 5
}
```

```http
POST /pseudonymize
Content-Type: application/json

{
  "data": "patient name",
  "patient_id": "PAT123"
}
```

### Access Control
```http
POST /check-access
Content-Type: application/json

{
  "resource_type": "patient_data",
  "resource_id": "PAT123",
  "action": "read",
  "purpose": "clinical_care",
  "patient_id": "PAT123"
}
```

### Audit & Monitoring
```http
GET /audit-log?start_date=2024-01-01&limit=100
```

```http
POST /rotate-keys
```

## Security Features

### Encryption Standards
- **AES-256-GCM**: For symmetric encryption
- **RSA-2048-OAEP**: For asymmetric encryption
- **PBKDF2-SHA256**: For key derivation
- **Fernet**: For authenticated encryption

### Privacy Protection
- **K-Anonymity**: Minimum group size of 5 for anonymized data
- **Differential Privacy**: Epsilon of 1.0 for noise calibration
- **PHI Detection**: Regex patterns for SSN, phone, email, addresses
- **Pseudonymization**: HMAC-based deterministic pseudonyms

### Access Control
- **RBAC**: 5 predefined roles (admin, security_officer, provider, researcher, patient)
- **Patient Relationships**: Dynamic access based on care relationships
- **Emergency Access**: 24-hour time-limited emergency access
- **Risk Scoring**: Dynamic risk assessment for access decisions

### Audit & Compliance
- **Comprehensive Logging**: All security events logged with full context
- **Data Retention**: 7-year retention for audit logs (HIPAA compliant)
- **Key Rotation**: 90-day automatic key rotation
- **Compliance Reports**: Built-in reporting for regulatory requirements

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/abena_ihr_security` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `MASTER_KEY` | Auto-generated | Master encryption key (32-byte base64) |
| `KEY_ROTATION_DAYS` | `90` | Days between key rotations |
| `K_ANONYMITY_THRESHOLD` | `5` | Minimum group size for k-anonymity |
| `DIFFERENTIAL_PRIVACY_EPSILON` | `1.0` | Privacy budget for differential privacy |
| `AUDIT_RETENTION_DAYS` | `2555` | Days to retain audit logs (7 years) |

### Database Configuration

The service uses PostgreSQL with the following key tables:

- **encryption_keys**: Stores encrypted data encryption keys
- **security_audit_log**: Comprehensive security event logging
- **access_audit_log**: Access control decision logging
- **roles/permissions**: RBAC configuration
- **patient_provider_relationships**: Dynamic access relationships
- **pseudonym_mappings**: Patient pseudonym mappings

## Development

### Local Development Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up database**
```bash
# Start PostgreSQL and Redis
docker-compose up postgres redis -d

# Run migrations
psql -h localhost -p 5433 -U postgres -d abena_ihr_security -f schema.sql
```

3. **Run tests**
```bash
pytest tests/
```

4. **Code formatting**
```bash
black .
isort .
flake8 .
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test categories
pytest tests/test_encryption.py
pytest tests/test_anonymization.py
pytest tests/test_access_control.py
```

## Production Deployment

### Security Considerations

1. **Master Key Management**
   - Store master key in secure key management system (AWS KMS, Azure Key Vault, etc.)
   - Rotate master key regularly
   - Use hardware security modules (HSM) for production

2. **Network Security**
   - Use TLS 1.3 for all communications
   - Implement proper firewall rules
   - Use VPN for administrative access

3. **Database Security**
   - Enable encryption at rest
   - Use connection pooling with SSL
   - Implement proper backup encryption

4. **Monitoring & Alerting**
   - Monitor failed access attempts
   - Alert on unusual access patterns
   - Regular security log reviews

### Docker Deployment

```bash
# Build production image
docker build -t abena-privacy-security:latest .

# Run with production settings
docker run -d \
  --name privacy-security \
  -p 8002:8002 \
  -e MASTER_KEY=$MASTER_KEY \
  -e DATABASE_URL=$DATABASE_URL \
  -e REDIS_URL=$REDIS_URL \
  abena-privacy-security:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: privacy-security-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: privacy-security
  template:
    metadata:
      labels:
        app: privacy-security
    spec:
      containers:
      - name: privacy-security
        image: abena-privacy-security:latest
        ports:
        - containerPort: 8002
        env:
        - name: MASTER_KEY
          valueFrom:
            secretKeyRef:
              name: privacy-security-secrets
              key: master-key
```

## Monitoring & Observability

### Health Checks
- **Service Health**: `/health` endpoint
- **Database Connectivity**: Automatic connection pool monitoring
- **Redis Connectivity**: Cache availability monitoring

### Metrics
- Encryption operations per day
- Failed access attempts
- Average risk scores
- Key rotation events
- Anonymization job success rates

### Logging
- Structured JSON logging with correlation IDs
- Security event logging with full context
- Performance metrics and timing information
- Error tracking with stack traces

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL is running
   - Verify connection string format
   - Ensure database exists and schema is loaded

2. **Encryption Errors**
   - Verify MASTER_KEY is set correctly
   - Check key format (base64 encoded)
   - Ensure sufficient entropy for key generation

3. **Access Control Issues**
   - Verify user roles and permissions
   - Check patient-provider relationships
   - Review audit logs for access attempts

4. **Performance Issues**
   - Monitor database connection pool
   - Check Redis cache hit rates
   - Review query performance with EXPLAIN

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
uvicorn main:app --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Review the documentation and troubleshooting guide 