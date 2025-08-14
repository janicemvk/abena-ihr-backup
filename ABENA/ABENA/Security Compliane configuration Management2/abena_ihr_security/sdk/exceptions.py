"""
Abena Security SDK Exceptions

This module defines all exception classes used by the Abena IHR Security SDK,
following Abena SDK patterns and providing clear error handling.
"""

from typing import Optional, Dict, Any


class AbenaSecurityException(Exception):
    """
    Base exception for Abena Security SDK

    This is the base exception class for all security-related errors
    in the Abena IHR system.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the exception

        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class ComplianceException(AbenaSecurityException):
    """
    Exception raised for compliance violations

    Raised when a compliance validation fails or when
    there are HIPAA or other regulatory violations.
    """

    def __init__(
        self,
        message: str,
        violations: Optional[list] = None,
        rule_id: Optional[str] = None,
    ):
        """
        Initialize compliance exception

        Args:
            message: Error message
            violations: List of compliance violations
            rule_id: ID of the violated rule
        """
        super().__init__(message, error_code="COMPLIANCE_VIOLATION")
        self.violations = violations or []
        self.rule_id = rule_id


class EncryptionException(AbenaSecurityException):
    """
    Exception raised for encryption/decryption errors

    Raised when encryption or decryption operations fail,
    including key management issues.
    """

    def __init__(
        self,
        message: str,
        key_id: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        """
        Initialize encryption exception

        Args:
            message: Error message
            key_id: ID of the key involved in the error
            operation: Type of operation that failed
        """
        super().__init__(message, error_code="ENCRYPTION_ERROR")
        self.key_id = key_id
        self.operation = operation


class AuditException(AbenaSecurityException):
    """
    Exception raised for audit logging errors

    Raised when audit trail logging fails or when
    audit data cannot be processed.
    """

    def __init__(
        self,
        message: str,
        event_id: Optional[str] = None,
        audit_level: Optional[str] = None,
    ):
        """
        Initialize audit exception

        Args:
            message: Error message
            event_id: ID of the audit event that failed
            audit_level: Level of audit logging that failed
        """
        super().__init__(message, error_code="AUDIT_ERROR")
        self.event_id = event_id
        self.audit_level = audit_level


class ConfigurationException(AbenaSecurityException):
    """
    Exception raised for configuration errors

    Raised when configuration management fails or when
    configuration data is invalid.
    """

    def __init__(
        self,
        message: str,
        config_id: Optional[str] = None,
        config_type: Optional[str] = None,
    ):
        """
        Initialize configuration exception

        Args:
            message: Error message
            config_id: ID of the configuration that failed
            config_type: Type of configuration that failed
        """
        super().__init__(message, error_code="CONFIGURATION_ERROR")
        self.config_id = config_id
        self.config_type = config_type


class BusinessRuleException(AbenaSecurityException):
    """
    Exception raised for business rule errors

    Raised when business rule processing fails or when
    business rules are invalid.
    """

    def __init__(
        self,
        message: str,
        rule_id: Optional[str] = None,
        rule_type: Optional[str] = None,
    ):
        """
        Initialize business rule exception

        Args:
            message: Error message
            rule_id: ID of the rule that failed
            rule_type: Type of rule that failed
        """
        super().__init__(message, error_code="BUSINESS_RULE_ERROR")
        self.rule_id = rule_id
        self.rule_type = rule_type


class DataMaskingException(AbenaSecurityException):
    """
    Exception raised for data masking errors

    Raised when data masking operations fail or when
    masking rules are invalid.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        masking_type: Optional[str] = None,
    ):
        """
        Initialize data masking exception

        Args:
            message: Error message
            field_name: Name of the field that failed masking
            masking_type: Type of masking that failed
        """
        super().__init__(message, error_code="DATA_MASKING_ERROR")
        self.field_name = field_name
        self.masking_type = masking_type


class ValidationException(AbenaSecurityException):
    """
    Exception raised for validation errors

    Raised when data validation fails or when
    validation rules are violated.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        validation_type: Optional[str] = None,
    ):
        """
        Initialize validation exception

        Args:
            message: Error message
            field_name: Name of the field that failed validation
            validation_type: Type of validation that failed
        """
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field_name = field_name
        self.validation_type = validation_type


class AuthenticationException(AbenaSecurityException):
    """
    Exception raised for authentication errors

    Raised when user authentication fails or when
    authentication credentials are invalid.
    """

    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        auth_method: Optional[str] = None,
    ):
        """
        Initialize authentication exception

        Args:
            message: Error message
            user_id: ID of the user that failed authentication
            auth_method: Authentication method that failed
        """
        super().__init__(message, error_code="AUTHENTICATION_ERROR")
        self.user_id = user_id
        self.auth_method = auth_method


class AuthorizationException(AbenaSecurityException):
    """
    Exception raised for authorization errors

    Raised when user authorization fails or when
    access permissions are insufficient.
    """

    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
    ):
        """
        Initialize authorization exception

        Args:
            message: Error message
            user_id: ID of the user that failed authorization
            resource: Resource that was denied access
            action: Action that was denied
        """
        super().__init__(message, error_code="AUTHORIZATION_ERROR")
        self.user_id = user_id
        self.resource = resource
        self.action = action


class DatabaseException(AbenaSecurityException):
    """
    Exception raised for database errors

    Raised when database operations fail or when
    database connections are lost.
    """

    def __init__(
        self,
        message: str,
        table_name: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        """
        Initialize database exception

        Args:
            message: Error message
            table_name: Name of the table involved in the error
            operation: Type of database operation that failed
        """
        super().__init__(message, error_code="DATABASE_ERROR")
        self.table_name = table_name
        self.operation = operation


class ConnectionException(AbenaSecurityException):
    """
    Exception raised for connection errors

    Raised when external service connections fail or when
    network connectivity is lost.
    """

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        """
        Initialize connection exception

        Args:
            message: Error message
            service_name: Name of the service that failed to connect
            endpoint: Endpoint that failed to connect
        """
        super().__init__(message, error_code="CONNECTION_ERROR")
        self.service_name = service_name
        self.endpoint = endpoint


class TimeoutException(AbenaSecurityException):
    """
    Exception raised for timeout errors

    Raised when operations exceed their timeout limits
    or when services are unresponsive.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        operation: Optional[str] = None,
    ):
        """
        Initialize timeout exception

        Args:
            message: Error message
            timeout_seconds: Number of seconds that exceeded the timeout
            operation: Type of operation that timed out
        """
        super().__init__(message, error_code="TIMEOUT_ERROR")
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class ResourceNotFoundException(AbenaSecurityException):
    """
    Exception raised when resources are not found

    Raised when requested resources (keys, configs, rules, etc.)
    cannot be found in the system.
    """

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        """
        Initialize resource not found exception

        Args:
            message: Error message
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found
        """
        super().__init__(message, error_code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id
