"""
Unit tests for Abena Security Exceptions

Tests all exception classes and their functionality.
"""

from abena_ihr_security.sdk.exceptions import (
    AbenaSecurityException,
    ComplianceException,
    EncryptionException,
    AuditException,
    ConfigurationException,
    BusinessRuleException,
    DataMaskingException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    DatabaseException,
    ConnectionException,
    TimeoutException,
    ResourceNotFoundException,
)


class TestAbenaSecurityException:
    """Test cases for base AbenaSecurityException"""

    def test_base_exception_creation(self):
        """Test base exception creation"""
        exception = AbenaSecurityException(
            message="Test error message",
            error_code="TEST_ERROR",
            details={"key": "value"},
        )

        assert str(exception) == "Test error message"
        assert exception.message == "Test error message"
        assert exception.error_code == "TEST_ERROR"
        assert exception.details == {"key": "value"}

    def test_base_exception_defaults(self):
        """Test base exception with default values"""
        exception = AbenaSecurityException("Simple error")

        assert exception.message == "Simple error"
        assert exception.error_code is None
        assert exception.details == {}

    def test_base_exception_to_dict(self):
        """Test base exception to_dict method"""
        exception = AbenaSecurityException(
            message="Test error",
            error_code="TEST_ERROR",
            details={"detail_key": "detail_value"},
        )

        result = exception.to_dict()

        assert result["error_type"] == "AbenaSecurityException"
        assert result["message"] == "Test error"
        assert result["error_code"] == "TEST_ERROR"
        assert result["details"]["detail_key"] == "detail_value"


class TestComplianceException:
    """Test cases for ComplianceException"""

    def test_compliance_exception_creation(self):
        """Test compliance exception creation"""
        exception = ComplianceException(
            message="HIPAA violation detected",
            violations=["access_control_001", "audit_control_002"],
            rule_id="rule_123",
        )

        assert exception.message == "HIPAA violation detected"
        assert exception.error_code == "COMPLIANCE_VIOLATION"
        assert exception.violations == [
            "access_control_001",
            "audit_control_002"
        ]
        assert exception.rule_id == "rule_123"

    def test_compliance_exception_defaults(self):
        """Test compliance exception with default values"""
        exception = ComplianceException("Simple compliance error")

        assert exception.message == "Simple compliance error"
        assert exception.error_code == "COMPLIANCE_VIOLATION"
        assert exception.violations == []
        assert exception.rule_id is None


class TestEncryptionException:
    """Test cases for EncryptionException"""

    def test_encryption_exception_creation(self):
        """Test encryption exception creation"""
        exception = EncryptionException(
            message="Key not found", key_id="key_123", operation="encrypt"
        )

        assert exception.message == "Key not found"
        assert exception.error_code == "ENCRYPTION_ERROR"
        assert exception.key_id == "key_123"
        assert exception.operation == "encrypt"

    def test_encryption_exception_defaults(self):
        """Test encryption exception with default values"""
        exception = EncryptionException("Simple encryption error")

        assert exception.message == "Simple encryption error"
        assert exception.error_code == "ENCRYPTION_ERROR"
        assert exception.key_id is None
        assert exception.operation is None


class TestAuditException:
    """Test cases for AuditException"""

    def test_audit_exception_creation(self):
        """Test audit exception creation"""
        exception = AuditException(
            message="Audit logging failed",
            event_id="event_123",
            audit_level="high"
        )

        assert exception.message == "Audit logging failed"
        assert exception.error_code == "AUDIT_ERROR"
        assert exception.event_id == "event_123"
        assert exception.audit_level == "high"

    def test_audit_exception_defaults(self):
        """Test audit exception with default values"""
        exception = AuditException("Simple audit error")

        assert exception.message == "Simple audit error"
        assert exception.error_code == "AUDIT_ERROR"
        assert exception.event_id is None
        assert exception.audit_level is None


class TestConfigurationException:
    """Test cases for ConfigurationException"""

    def test_configuration_exception_creation(self):
        """Test configuration exception creation"""
        exception = ConfigurationException(
            message="Invalid configuration",
            config_id="config_123",
            config_type="integration",
        )

        assert exception.message == "Invalid configuration"
        assert exception.error_code == "CONFIGURATION_ERROR"
        assert exception.config_id == "config_123"
        assert exception.config_type == "integration"

    def test_configuration_exception_defaults(self):
        """Test configuration exception with default values"""
        exception = ConfigurationException("Simple config error")

        assert exception.message == "Simple config error"
        assert exception.error_code == "CONFIGURATION_ERROR"
        assert exception.config_id is None
        assert exception.config_type is None


class TestBusinessRuleException:
    """Test cases for BusinessRuleException"""

    def test_business_rule_exception_creation(self):
        """Test business rule exception creation"""
        exception = BusinessRuleException(
            message="Rule validation failed",
            rule_id="rule_123",
            rule_type="validation"
        )

        assert exception.message == "Rule validation failed"
        assert exception.error_code == "BUSINESS_RULE_ERROR"
        assert exception.rule_id == "rule_123"
        assert exception.rule_type == "validation"

    def test_business_rule_exception_defaults(self):
        """Test business rule exception with default values"""
        exception = BusinessRuleException("Simple rule error")

        assert exception.message == "Simple rule error"
        assert exception.error_code == "BUSINESS_RULE_ERROR"
        assert exception.rule_id is None
        assert exception.rule_type is None


class TestDataMaskingException:
    """Test cases for DataMaskingException"""

    def test_data_masking_exception_creation(self):
        """Test data masking exception creation"""
        exception = DataMaskingException(
            message="Masking failed",
            field_name="ssn",
            masking_type="redaction"
        )

        assert exception.message == "Masking failed"
        assert exception.error_code == "DATA_MASKING_ERROR"
        assert exception.field_name == "ssn"
        assert exception.masking_type == "redaction"

    def test_data_masking_exception_defaults(self):
        """Test data masking exception with default values"""
        exception = DataMaskingException("Simple masking error")

        assert exception.message == "Simple masking error"
        assert exception.error_code == "DATA_MASKING_ERROR"
        assert exception.field_name is None
        assert exception.masking_type is None


class TestValidationException:
    """Test cases for ValidationException"""

    def test_validation_exception_creation(self):
        """Test validation exception creation"""
        exception = ValidationException(
            message="Validation failed",
            field_name="email",
            validation_type="format"
        )

        assert exception.message == "Validation failed"
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.field_name == "email"
        assert exception.validation_type == "format"

    def test_validation_exception_defaults(self):
        """Test validation exception with default values"""
        exception = ValidationException("Simple validation error")

        assert exception.message == "Simple validation error"
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.field_name is None
        assert exception.validation_type is None


class TestAuthenticationException:
    """Test cases for AuthenticationException"""

    def test_authentication_exception_creation(self):
        """Test authentication exception creation"""
        exception = AuthenticationException(
            message="Authentication failed",
            user_id="user_123",
            auth_method="password"
        )

        assert exception.message == "Authentication failed"
        assert exception.error_code == "AUTHENTICATION_ERROR"
        assert exception.user_id == "user_123"
        assert exception.auth_method == "password"

    def test_authentication_exception_defaults(self):
        """Test authentication exception with default values"""
        exception = AuthenticationException("Simple auth error")

        assert exception.message == "Simple auth error"
        assert exception.error_code == "AUTHENTICATION_ERROR"
        assert exception.user_id is None
        assert exception.auth_method is None


class TestAuthorizationException:
    """Test cases for AuthorizationException"""

    def test_authorization_exception_creation(self):
        """Test authorization exception creation"""
        exception = AuthorizationException(
            message="Access denied",
            user_id="user_123",
            resource="patient_data",
            action="read",
        )

        assert exception.message == "Access denied"
        assert exception.error_code == "AUTHORIZATION_ERROR"
        assert exception.user_id == "user_123"
        assert exception.resource == "patient_data"
        assert exception.action == "read"

    def test_authorization_exception_defaults(self):
        """Test authorization exception with default values"""
        exception = AuthorizationException("Simple authorization error")

        assert exception.message == "Simple authorization error"
        assert exception.error_code == "AUTHORIZATION_ERROR"
        assert exception.user_id is None
        assert exception.resource is None
        assert exception.action is None


class TestDatabaseException:
    """Test cases for DatabaseException"""

    def test_database_exception_creation(self):
        """Test database exception creation"""
        exception = DatabaseException(
            message="Database connection failed",
            table_name="audit_logs",
            operation="insert",
        )

        assert exception.message == "Database connection failed"
        assert exception.error_code == "DATABASE_ERROR"
        assert exception.table_name == "audit_logs"
        assert exception.operation == "insert"

    def test_database_exception_defaults(self):
        """Test database exception with default values"""
        exception = DatabaseException("Simple database error")

        assert exception.message == "Simple database error"
        assert exception.error_code == "DATABASE_ERROR"
        assert exception.table_name is None
        assert exception.operation is None


class TestConnectionException:
    """Test cases for ConnectionException"""

    def test_connection_exception_creation(self):
        """Test connection exception creation"""
        exception = ConnectionException(
            message="Service connection failed",
            service_name="redis",
            endpoint="localhost:6379",
        )

        assert exception.message == "Service connection failed"
        assert exception.error_code == "CONNECTION_ERROR"
        assert exception.service_name == "redis"
        assert exception.endpoint == "localhost:6379"

    def test_connection_exception_defaults(self):
        """Test connection exception with default values"""
        exception = ConnectionException("Simple connection error")

        assert exception.message == "Simple connection error"
        assert exception.error_code == "CONNECTION_ERROR"
        assert exception.service_name is None
        assert exception.endpoint is None


class TestTimeoutException:
    """Test cases for TimeoutException"""

    def test_timeout_exception_creation(self):
        """Test timeout exception creation"""
        exception = TimeoutException(
            message="Operation timed out",
            timeout_seconds=30,
            operation="encryption"
        )

        assert exception.message == "Operation timed out"
        assert exception.error_code == "TIMEOUT_ERROR"
        assert exception.timeout_seconds == 30
        assert exception.operation == "encryption"

    def test_timeout_exception_defaults(self):
        """Test timeout exception with default values"""
        exception = TimeoutException("Simple timeout error")

        assert exception.message == "Simple timeout error"
        assert exception.error_code == "TIMEOUT_ERROR"
        assert exception.timeout_seconds is None
        assert exception.operation is None


class TestResourceNotFoundException:
    """Test cases for ResourceNotFoundException"""

    def test_resource_not_found_exception_creation(self):
        """Test resource not found exception creation"""
        exception = ResourceNotFoundException(
            message="Key not found",
            resource_type="encryption_key",
            resource_id="key_123",
        )

        assert exception.message == "Key not found"
        assert exception.error_code == "RESOURCE_NOT_FOUND"
        assert exception.resource_type == "encryption_key"
        assert exception.resource_id == "key_123"

    def test_resource_not_found_exception_defaults(self):
        """Test resource not found exception with default values"""
        exception = ResourceNotFoundException("Simple not found error")

        assert exception.message == "Simple not found error"
        assert exception.error_code == "RESOURCE_NOT_FOUND"
        assert exception.resource_type is None
        assert exception.resource_id is None


class TestExceptionInheritance:
    """Test exception inheritance hierarchy"""

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from AbenaSecurityException"""
        exceptions = [
            ComplianceException("test"),
            EncryptionException("test"),
            AuditException("test"),
            ConfigurationException("test"),
            BusinessRuleException("test"),
            DataMaskingException("test"),
            ValidationException("test"),
            AuthenticationException("test"),
            AuthorizationException("test"),
            DatabaseException("test"),
            ConnectionException("test"),
            TimeoutException("test"),
            ResourceNotFoundException("test"),
        ]

        for exception in exceptions:
            assert isinstance(exception, AbenaSecurityException)
            assert isinstance(exception, Exception)

    def test_exception_error_codes(self):
        """Test that all exceptions have unique error codes"""
        error_codes = set()
        exceptions = [
            ComplianceException("test"),
            EncryptionException("test"),
            AuditException("test"),
            ConfigurationException("test"),
            BusinessRuleException("test"),
            DataMaskingException("test"),
            ValidationException("test"),
            AuthenticationException("test"),
            AuthorizationException("test"),
            DatabaseException("test"),
            ConnectionException("test"),
            TimeoutException("test"),
            ResourceNotFoundException("test"),
        ]

        for exception in exceptions:
            assert exception.error_code is not None
            assert exception.error_code not in error_codes
            error_codes.add(exception.error_code)
