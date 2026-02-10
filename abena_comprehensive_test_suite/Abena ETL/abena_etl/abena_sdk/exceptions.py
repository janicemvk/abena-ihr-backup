"""
Abena SDK Exceptions

Custom exception classes for the Abena SDK to provide clear error handling
and meaningful error messages.
"""

from typing import Optional, Dict, Any


class AbenaException(Exception):
    """Base exception for all Abena SDK errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AuthenticationError(AbenaException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTH_ERROR", details)


class AuthorizationError(AbenaException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Authorization failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHZ_ERROR", details)


class ConfigurationError(AbenaException):
    """Raised when SDK configuration is invalid"""
    
    def __init__(self, message: str = "Invalid configuration", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)


class DataTransformationError(AbenaException):
    """Raised when data transformation fails"""
    
    def __init__(self, message: str = "Data transformation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "TRANSFORM_ERROR", details)


class FHIRConversionError(AbenaException):
    """Raised when FHIR conversion fails"""
    
    def __init__(self, message: str = "FHIR conversion failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "FHIR_ERROR", details)


class AnalyticsError(AbenaException):
    """Raised when analytics operations fail"""
    
    def __init__(self, message: str = "Analytics operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "ANALYTICS_ERROR", details)


class ConnectionError(AbenaException):
    """Raised when connection to external services fails"""
    
    def __init__(self, message: str = "Connection failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONNECTION_ERROR", details)


class ValidationError(AbenaException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details) 