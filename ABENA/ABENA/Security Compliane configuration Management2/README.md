# Abena IHR Security Module

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](https://abenahealthcare.com)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Security: HIPAA Compliant](https://img.shields.io/badge/Security-HIPAA%20Compliant-green.svg)](https://www.hhs.gov/hipaa/)

Comprehensive security, compliance, and configuration management for the Abena IHR (Integrated Health Records) system, following the **Abena Shared SDK - Universal Service Client** pattern.

## 🏥 Overview

The Abena IHR Security Module provides enterprise-grade security, compliance, and configuration management capabilities for healthcare applications. Built following Abena SDK patterns, it ensures HIPAA compliance, data protection, and secure integration management.

## ✨ Key Features

### 🔐 Security Services
- **Encryption/Decryption**: AES-256-GCM and RSA-2048/4096 support
- **Key Management**: Secure key generation, rotation, and lifecycle management
- **Data Masking**: PII/PHI anonymization with multiple masking strategies
- **Tokenization**: Reversible data tokenization for secure processing

### 📋 Compliance Management
- **HIPAA Compliance**: Automated validation and reporting
- **Audit Trails**: Comprehensive logging for regulatory requirements
- **Compliance Reports**: Automated generation and monitoring
- **Policy Enforcement**: Business rules for compliance validation

### ⚙️ Configuration Management
- **Integration Configs**: Secure storage and management of external system configurations
- **Business Rules Engine**: Dynamic rule processing for data validation and transformation
- **Environment Management**: Multi-environment configuration support

### 🛡️ Data Protection
- **Access Control**: Role-based permissions and authorization
- **Data Integrity**: Checksums and digital signatures
- **Secure Communication**: Encrypted data transmission
- **Audit Logging**: Tamper-evident audit trails

## 🚀 Quick Start

### Installation

```bash
pip install abena-ihr-security
```

### Basic Usage

```python
import asyncio
from abena_ihr_security.sdk import AbenaSecurityClient, AbenaSecurityConfig, SecurityContext

async def main():
    # Initialize configuration
    config = AbenaSecurityConfig.from_env()
    
    # Create security client
    client = AbenaSecurityClient(config)
    await client.initialize()
    
    # Create security context
    context = SecurityContext(
        user_id="user_123",
        user_role="nurse",
        action="read",
        resource_type="patient",
        source_ip="192.168.1.100"
    )
    
    # Process data with security
    patient_data = {
        "id": "patient_456",
        "name": "John Doe",
        "ssn": "123-45-6789",
        "date_of_birth": "1985-03-15"
    }
    
    result = await client.process_data_with_security(patient_data, context, "read")
    print(f"Processing result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 API Reference

### Core Components

#### AbenaSecurityClient
The main client interface for all security operations.

```python
from abena_ihr_security.sdk import AbenaSecurityClient

client = AbenaSecurityClient(config)
await client.initialize()

# Process data with security
result = await client.process_data_with_security(data, context, operation)

# Encrypt/decrypt data
encrypted = await client.encrypt_data(data, key_id)
decrypted = await client.decrypt_data(encrypted_data, key_id)

# Apply data masking
masked_data = await client.mask_data(data, context="nurse")

# Validate compliance
compliance_result = await client.validate_compliance(context)

# Get configurations
config = await client.get_configuration("Epic_EMR")

# Apply business rules
rules_result = await client.apply_business_rules(data, "validation")
```

#### SecurityContext
Defines the security context for operations.

```python
from abena_ihr_security.sdk import SecurityContext

context = SecurityContext(
    user_id="user_123",
    user_role="physician",
    action="read",
    resource_type="patient",
    resource_id="patient_456",
    source_ip="192.168.1.100",
    user_agent="Mozilla/5.0...",
    permissions=["read_patient", "write_observations"],
    requested_fields=["name", "date_of_birth", "medications"]
)
```

### Configuration

#### AbenaSecurityConfig
Comprehensive configuration management.

```python
from abena_ihr_security.sdk import AbenaSecurityConfig

# From environment variables
config = AbenaSecurityConfig.from_env()

# From file
config = AbenaSecurityConfig.from_file("config.json")

# Custom configuration
config = AbenaSecurityConfig(
    database_url="postgresql://user:pass@localhost/abena_ihr",
    redis_url="redis://localhost:6379",
    master_key_path="/secure/master.key",
    compliance_framework="HIPAA",
    masking_enabled=True
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/abena_ihr
REDIS_URL=redis://localhost:6379

# Security Configuration
MASTER_KEY_PATH=/secure/master.key
ENCRYPTION_ALGORITHM=AES_256_GCM
KEY_ROTATION_DAYS=365

# Audit Configuration
AUDIT_LOG_LEVEL=INFO
AUDIT_RETENTION_DAYS=2555
AUDIT_BATCH_SIZE=100

# Compliance Configuration
COMPLIANCE_FRAMEWORK=HIPAA
COMPLIANCE_CHECK_INTERVAL=3600
COMPLIANCE_REPORT_RETENTION_DAYS=2555

# Data Masking Configuration
MASKING_ENABLED=true
TOKENIZATION_ENABLED=true

# Business Rules Configuration
RULES_AUTO_RELOAD=true
RULES_CACHE_TTL=300

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/abena/abena-ihr-security.log

# Performance Configuration
MAX_CONNECTIONS=20
CONNECTION_TIMEOUT=30
REQUEST_TIMEOUT=60

# Development Configuration
DEBUG_MODE=false
TEST_MODE=false
```

### Configuration File

```json
{
  "database_url": "postgresql://user:pass@localhost/abena_ihr",
  "redis_url": "redis://localhost:6379",
  "master_key_path": "/secure/master.key",
  "encryption_algorithm": "AES_256_GCM",
  "key_rotation_days": 365,
  "audit_log_level": "INFO",
  "audit_retention_days": 2555,
  "compliance_framework": "HIPAA",
  "masking_enabled": true,
  "tokenization_enabled": true,
  "rules_auto_reload": true,
  "log_level": "INFO",
  "max_connections": 20,
  "debug_mode": false
}
```

## 🏗️ Architecture

### Module Structure

```
abena_ihr_security/
├── __init__.py                 # Main package initialization
├── sdk/                        # Abena SDK interface
│   ├── __init__.py            # SDK initialization
│   ├── client.py              # Universal Service Client
│   ├── config.py              # Configuration management
│   ├── types.py               # Data types and enums
│   └── exceptions.py          # Exception classes
├── core/                       # Core security services
│   ├── __init__.py            # Core services initialization
│   ├── module_layer.py        # Module layer orchestrator
│   ├── encryption_service.py  # Encryption/decryption service
│   ├── audit_generator.py     # Audit trail generator
│   └── data_masking.py        # Data masking service
├── models/                     # Database models
│   ├── __init__.py            # Models initialization
│   ├── audit_models.py        # Audit log models
│   ├── encryption_models.py   # Encryption key models
│   ├── config_models.py       # Configuration models
│   └── compliance_models.py   # Compliance report models
├── compliance/                 # Compliance services
│   ├── __init__.py            # Compliance initialization
│   └── hipaa_validator.py     # HIPAA compliance validator
├── config/                     # Configuration services
│   ├── __init__.py            # Config initialization
│   └── manager.py             # Configuration manager
└── rules/                      # Business rules engine
    ├── __init__.py            # Rules initialization
    └── engine.py              # Business rules engine
```

### Service Architecture

The module follows a layered architecture:

1. **SDK Layer**: Universal Service Client interface
2. **Core Layer**: Fundamental security services
3. **Service Layer**: Specialized services (compliance, config, rules)
4. **Data Layer**: Database models and persistence

## 🔒 Security Features

### Encryption
- **Symmetric**: AES-256-GCM for data encryption
- **Asymmetric**: RSA-2048/4096 for key exchange and signing
- **Key Management**: Secure key generation, rotation, and storage
- **Key Usage**: Separate keys for different purposes (data, audit, communication)

### Data Masking
- **Redaction**: Pattern-based data masking
- **Substitution**: Synthetic data replacement
- **Tokenization**: Reversible data tokenization
- **Shuffling**: Date and value shuffling
- **Synthetic**: Statistically similar synthetic data

### Compliance
- **HIPAA Validation**: Automated compliance checking
- **Audit Logging**: Comprehensive event logging
- **Policy Enforcement**: Business rules for compliance
- **Reporting**: Automated compliance reports

## 📊 Monitoring & Reporting

### Compliance Dashboard

```python
# Get compliance dashboard
dashboard = await client.get_compliance_dashboard()
print(f"HIPAA Compliance Score: {dashboard['compliance_summary']['hipaa_compliance_score']}%")
print(f"Total Violations: {dashboard['compliance_summary']['total_violations']}")
```

### Audit Trail

```python
# Log audit event
event = AuditEvent(
    event_id=str(uuid.uuid4()),
    timestamp=datetime.utcnow(),
    user_id="user_123",
    action=AuditAction.READ,
    resource_type=AuditResourceType.PATIENT,
    resource_id="patient_456",
    status="success"
)

event_id = await client.log_audit_event(event)
```

### Compliance Reports

```python
# Generate compliance report
start_date = datetime.utcnow() - timedelta(days=30)
end_date = datetime.utcnow()

report = await client.generate_compliance_report(start_date, end_date)
print(f"Compliance Score: {report['compliance_score']}%")
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=abena_ihr_security tests/

# Run specific test
pytest tests/test_encryption.py::test_encrypt_data
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Run with database
pytest tests/integration/ --db-url=postgresql://test:test@localhost/test_db
```

### Security Tests

```bash
# Run security tests
pytest tests/security/

# Run compliance tests
pytest tests/compliance/
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Create secure directories
RUN mkdir -p /secure /var/log/abena

# Set permissions
RUN chmod 700 /secure
RUN chown -R nobody:nogroup /app /var/log/abena

# Switch to non-root user
USER nobody

# Run application
CMD ["python", "-m", "abena_ihr_security"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  abena-ihr-security:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/abena_ihr
      - REDIS_URL=redis://redis:6379
      - MASTER_KEY_PATH=/secure/master.key
    volumes:
      - ./secure:/secure:ro
      - ./logs:/var/log/abena
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: abena_ihr
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 📈 Performance

### Benchmarks

- **Encryption**: ~1000 operations/second (AES-256-GCM)
- **Data Masking**: ~5000 records/second
- **Audit Logging**: ~10000 events/second
- **Compliance Validation**: ~1000 checks/second

### Optimization

- **Connection Pooling**: Configurable connection limits
- **Caching**: Redis-based caching for configurations and rules
- **Batch Processing**: Bulk operations for audit logging
- **Async Operations**: Non-blocking I/O for all operations

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/abenahealthcare/abena-ihr-security.git
cd abena-ihr-security

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

### Code Style

```bash
# Format code
black abena_ihr_security/

# Lint code
flake8 abena_ihr_security/

# Type checking
mypy abena_ihr_security/

# Security scanning
bandit -r abena_ihr_security/
```

## 📄 License

This software is proprietary and confidential. Copyright © 2024 Abena Healthcare Solutions. All rights reserved.

## 🤝 Contributing

This is a proprietary module for Abena Healthcare Solutions. For internal contributions, please follow the Abena development guidelines.

## 📞 Support

For support and questions:

- **Email**: dev@abenahealthcare.com
- **Documentation**: https://abena-ihr-security.readthedocs.io/
- **Issues**: Internal issue tracking system

## 🔗 Related Projects

- **Abena IHR Core**: Core healthcare data management
- **Abena Analytics**: Healthcare analytics and reporting
- **Abena Integration Hub**: External system integrations

---

**Built with ❤️ by the Abena Development Team** 