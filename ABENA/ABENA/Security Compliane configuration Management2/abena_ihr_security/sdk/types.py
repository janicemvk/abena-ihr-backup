"""
Abena Security SDK Types

This module defines all data types, enums, and structures
used by the Abena IHR Security SDK,
following Abena SDK patterns and providing type safety.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AuditAction(Enum):
    """Audit action types"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    MASK = "mask"
    DECRYPT = "decrypt"


class AuditResourceType(Enum):
    """Audit resource types"""

    PATIENT = "patient"
    OBSERVATION = "observation"
    USER = "user"
    INTEGRATION = "integration"
    CONFIGURATION = "configuration"
    REPORT = "report"
    SYSTEM = "system"


class ComplianceLevel(Enum):
    """Compliance levels"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"
    UNKNOWN = "unknown"


class MaskingType(Enum):
    """Data masking types"""

    REDACTION = "redaction"
    SUBSTITUTION = "substitution"
    SHUFFLING = "shuffling"
    ENCRYPTION = "encryption"
    TOKENIZATION = "tokenization"
    SYNTHETIC = "synthetic"


@dataclass
class SecurityContext:
    """
    Security context for operations

    Contains all security-related information for an operation,
    including user details, permissions, and session information.
    """

    user_id: str
    user_role: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    requested_fields: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "user_role": self.user_role,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "permissions": self.permissions,
            "requested_fields": self.requested_fields,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AuditEvent:
    """
    Audit event for logging

    Represents a single audit event that will be logged
    for compliance and security monitoring.
    """

    event_id: str
    timestamp: datetime
    user_id: Optional[str]
    action: AuditAction
    resource_type: AuditResourceType
    status: str  # success, failure, partial
    resource_id: Optional[str] = None
    user_role: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    compliance_flags: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "user_role": self.user_role,
            "action": self.action.value,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "status": self.status,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "compliance_flags": self.compliance_flags,
        }


@dataclass
class ComplianceResult:
    """
    Compliance validation result

    Contains the result of a compliance validation operation,
    including violations and recommendations.
    """

    compliant: bool
    violations: List[str]
    details: Dict[str, Any]
    timestamp: datetime
    recommendations: List[str] = field(default_factory=list)
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "compliant": self.compliant,
            "violations": self.violations,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "recommendations": self.recommendations,
            "score": self.score,
        }


@dataclass
class MaskingRule:
    """
    Data masking rule

    Defines how a specific field should be masked
    for privacy and security purposes.
    """

    field_name: str
    field_type: str  # name, ssn, email, phone, address, date_of_birth, etc.
    masking_type: MaskingType
    parameters: Dict[str, Any] = field(default_factory=dict)
    preserve_format: bool = True
    preserve_length: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field_name": self.field_name,
            "field_type": self.field_type,
            "masking_type": self.masking_type.value,
            "parameters": self.parameters,
            "preserve_format": self.preserve_format,
            "preserve_length": self.preserve_length,
        }


@dataclass
class BusinessRuleDefinition:
    """
    Business rule definition

    Defines a business rule for data validation, transformation,
    or compliance checking.
    """

    rule_id: str
    rule_name: str
    description: str
    rule_type: str  # validation, transformation, compliance
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    priority: int = 100
    is_active: bool = True
    compliance_category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "description": self.description,
            "rule_type": self.rule_type,
            "conditions": self.conditions,
            "actions": self.actions,
            "priority": self.priority,
            "is_active": self.is_active,
            "compliance_category": self.compliance_category,
        }


@dataclass
class EncryptionKeyInfo:
    """
    Encryption key information

    Contains information about an encryption key
    without exposing the actual key material.
    """

    key_id: str
    key_name: str
    key_type: str
    algorithm: str
    key_usage: str
    is_active: bool
    is_expired: bool
    days_until_expiry: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "key_id": self.key_id,
            "key_name": self.key_name,
            "key_type": self.key_type,
            "algorithm": self.algorithm,
            "key_usage": self.key_usage,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "days_until_expiry": self.days_until_expiry,
            "created_at": self.created_at.isoformat(),
            "expires_at": (self.expires_at.isoformat() if self.expires_at else None),
        }


@dataclass
class ComplianceReport:
    """
    Compliance report

    Contains a generated compliance report with findings
    and recommendations.
    """

    report_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    compliance_score: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    status: str = "draft"  # draft, final, archived
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "compliance_score": self.compliance_score,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "status": self.status,
            "generated_at": self.generated_at.isoformat(),
        }
