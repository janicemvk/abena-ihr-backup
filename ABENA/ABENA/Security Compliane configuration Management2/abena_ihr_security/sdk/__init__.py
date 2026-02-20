"""
Abena IHR Security SDK

This module provides the core Abena SDK interface for security, compliance,
and configuration management following the Abena
Shared SDK - Universal Service Client pattern.

The SDK provides a unified interface for:
- Security Services (Encryption, Audit, Data Masking)
- Compliance Validation (HIPAA, Regulatory)
- Configuration Management (Integration Configs, Business Rules)
- Module Layer Orchestration
"""

from .client import AbenaSecurityClient
from .config import AbenaSecurityConfig
from .exceptions import (
    AbenaSecurityException,
    ComplianceException,
    EncryptionException,
)
from .types import (
    SecurityContext,
    ComplianceResult,
    AuditEvent,
    MaskingRule,
    AuditAction,
    AuditResourceType,
)

__version__ = "1.0.0"
__author__ = "Abena Development Team"

__all__ = [
    "AbenaSecurityClient",
    "AbenaSecurityConfig",
    "AbenaSecurityException",
    "ComplianceException",
    "EncryptionException",
    "SecurityContext",
    "ComplianceResult",
    "AuditEvent",
    "MaskingRule",
    "AuditAction",
    "AuditResourceType",
]
