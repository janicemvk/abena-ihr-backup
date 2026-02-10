# Abena IHR CI/CD Tests

This directory contains comprehensive testing infrastructure for the Abena IHR microservices platform, ensuring healthcare compliance, security, performance, and reliability.

## Overview

The test suite covers multiple testing types to ensure the healthcare platform meets industry standards and regulatory requirements:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service-to-service communication testing
- **Security Tests**: HIPAA compliance, authentication, authorization, and data protection
- **Load Tests**: Performance and scalability testing
- **Performance Tests**: Response time and resource usage monitoring

## Directory Structure

```
tests/
├── integration-tests.py      # Comprehensive integration test suite
├── load-tests.js            # k6 load testing scripts
├── security-tests.py        # Security and compliance testing
├── test-runner.sh          # Main test orchestration script
└── README.md               # This file
```

## Test Types

### 1. Unit Tests

**Purpose**: Test individual components and functions in isolation.

**Coverage**:
- Service business logic
- Data models and validation
- Utility functions
- Error handling

**Running Unit Tests**:
```bash
# Run all unit tests
./test-runner.sh unit

# Run specific service unit tests
cd foundational-services/patient-engagement-service
python -m pytest tests/ -v
```

### 2. Integration Tests

**Purpose**: Test service-to-service communication and end-to-end workflows.

**Coverage**:
- API endpoints and responses
- Database operations
- Message queue interactions
- Authentication flows
- Healthcare-specific workflows

**Key Test Scenarios**:
- Patient registration and profile management
- Appointment booking and management
- Clinical decision support analysis
- HL7/FHIR data ingestion
- Blockchain health record operations
- Privacy and security operations

**Running Integration Tests**:
```bash
# Run all integration tests
./test-runner.sh integration

# Run specific integration test file
python integration-tests.py
```

### 3. Security Tests

**Purpose**: Ensure HIPAA compliance, data protection, and security best practices.

**Coverage**:
- Authentication and authorization
- Data encryption and anonymization
- Input validation and injection prevention
- Audit logging
- Rate limiting
- Blockchain security

**Security Test Categories**:
- **Authentication Tests**: Password policies, JWT validation, token expiration
- **Authorization Tests**: Role-based access control, cross-user data access prevention
- **Data Protection Tests**: Encryption at rest, anonymization, secure data handling
- **Input Validation Tests**: SQL injection prevention, XSS prevention
- **Compliance Tests**: HIPAA headers, audit logging requirements
- **Blockchain Tests**: Immutability, consent management security

**Running Security Tests**:
```bash
# Run all security tests
./test-runner.sh security

# Run specific security test file
python security-tests.py
```

### 4. Load Tests

**Purpose**: Test system performance under various load conditions.

**Coverage**:
- Concurrent user simulation
- API response times
- System throughput
- Resource utilization
- Scalability limits

**Load Test Scenarios**:
- Patient portal usage patterns
- Provider workflow simulation
- Data ingestion load testing
- Clinical decision support analysis
- Blockchain operations

**Running Load Tests**:
```bash
# Run all load tests
./test-runner.sh load

# Run k6 load tests directly
k6 run load-tests.js
```

### 5. Performance Tests

**Purpose**: Monitor and validate system performance metrics.

**Coverage**:
- Response time analysis
- Throughput measurement
- Resource usage monitoring
- Performance regression detection

**Running Performance Tests**:
```bash
# Run all performance tests
./test-runner.sh performance
```

## Test Configuration

### Environment Variables

```bash
# Test environment configuration
export TEST_BASE_URL="https://api.abena-ihr.com"
export TEST_ENVIRONMENT="staging"
export PARALLEL_TESTS="false"
export TEST_TIMEOUT="300"
export REPORT_DIR="test-reports"
export COVERAGE_THRESHOLD="80"
```

### Test Data

The test suite uses predefined test data for consistent testing:

- **Test Users**: Patient, provider, and admin accounts
- **Sample Data**: HL7 messages, FHIR resources, clinical data
- **Mock Services**: External service simulations

## Running Tests

### Complete Test Suite

```bash
# Run all tests
./test-runner.sh all
```

### Individual Test Types

```bash
# Unit tests only
./test-runner.sh unit

# Integration tests only
./test-runner.sh integration

# Security tests only
./test-runner.sh security

# Load tests only
./test-runner.sh load

# Performance tests only
./test-runner.sh performance
```

### Manual Test Execution

```bash
# Python integration tests
cd infrastructure/ci-cd/tests
python integration-tests.py

# Security tests
python security-tests.py

# Load tests with k6
k6 run load-tests.js
```

## Test Reports

### Report Structure

```
test-reports/
├── unit/                    # Unit test results
├── integration/            # Integration test results
├── security/              # Security test results
├── load/                  # Load test results
├── coverage/              # Code coverage reports
└── test_report_*.html     # HTML test reports
```

### Report Types

1. **JUnit XML**: Standard test result format
2. **Coverage Reports**: Code coverage analysis
3. **Security Reports**: Vulnerability and compliance reports
4. **Performance Reports**: Load test metrics and analysis
5. **HTML Reports**: Human-readable test summaries

## Healthcare Compliance

### HIPAA Compliance Testing

- **Data Encryption**: Verify sensitive data is encrypted at rest and in transit
- **Access Controls**: Test role-based access and authentication
- **Audit Logging**: Ensure all access to PHI is logged
- **Data Anonymization**: Test PII removal capabilities
- **Secure Communication**: Verify TLS/SSL implementation

### GDPR Compliance Testing

- **Data Portability**: Test data export capabilities
- **Right to be Forgotten**: Test data deletion workflows
- **Consent Management**: Verify consent tracking and management
- **Data Minimization**: Test data collection limits

## Security Testing

### Authentication Testing

- Strong password policy enforcement
- Multi-factor authentication
- Session management
- Token validation and expiration

### Authorization Testing

- Role-based access control (RBAC)
- Resource-level permissions
- Cross-user data access prevention
- API endpoint protection

### Data Protection Testing

- Encryption at rest and in transit
- Data anonymization and pseudonymization
- Secure data disposal
- Backup encryption

### Input Validation Testing

- SQL injection prevention
- Cross-site scripting (XSS) prevention
- Command injection prevention
- Input sanitization

## Performance Testing

### Load Testing Metrics

- **Response Time**: 95th percentile < 500ms
- **Throughput**: Requests per second
- **Error Rate**: < 1% under normal load
- **Resource Usage**: CPU, memory, disk utilization

### Scalability Testing

- Horizontal scaling validation
- Database performance under load
- Cache effectiveness
- Message queue performance

## Continuous Integration

### CI/CD Pipeline Integration

The test suite is designed to integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd infrastructure/ci-cd/tests
    ./test-runner.sh all

- name: Upload Test Results
  uses: actions/upload-artifact@v2
  with:
    name: test-reports
    path: test-reports/
```

### Test Automation

- **Pre-deployment**: Full test suite execution
- **Post-deployment**: Smoke tests and health checks
- **Scheduled**: Security scans and performance monitoring
- **On-demand**: Manual test execution for debugging

## Troubleshooting

### Common Issues

1. **Service Unavailable**: Check if all microservices are running
2. **Authentication Failures**: Verify test user credentials
3. **Database Connection**: Ensure database is accessible
4. **Network Issues**: Check firewall and network policies

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
./test-runner.sh all

# Verbose test output
python integration-tests.py --verbose
```

### Test Data Reset

```bash
# Reset test database
./scripts/reset-test-db.sh

# Clear test cache
rm -rf test-reports/
```

## Best Practices

### Test Development

1. **Test Isolation**: Each test should be independent
2. **Data Cleanup**: Clean up test data after execution
3. **Realistic Data**: Use realistic healthcare data for testing
4. **Error Scenarios**: Test both success and failure cases
5. **Performance**: Keep tests fast and efficient

### Test Maintenance

1. **Regular Updates**: Keep test data current
2. **Version Control**: Track test changes with code changes
3. **Documentation**: Document test scenarios and expected results
4. **Monitoring**: Monitor test execution times and success rates

## Dependencies

### Required Tools

- **Python 3.8+**: For Python-based tests
- **Node.js 16+**: For JavaScript tests
- **k6**: For load testing
- **curl**: For API testing
- **Docker**: For containerized test environments

### Python Dependencies

```bash
pip install pytest requests pytest-cov
```

### Node.js Dependencies

```bash
npm install -g k6
```

## Support

For questions or issues with the test suite:

1. Check the troubleshooting section
2. Review test logs and reports
3. Consult the main project documentation
4. Contact the development team

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Include appropriate documentation
3. Ensure tests are healthcare-compliant
4. Add test data and mock services as needed
5. Update this README with new test information 