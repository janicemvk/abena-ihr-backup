"""
Unit tests for Abena Security SDK Types

Tests all data types, enums, and structures used by the SDK.
"""

from datetime import datetime, timezone

from abena_ihr_security.sdk.types import (
    AuditAction,
    AuditResourceType,
    ComplianceLevel,
    MaskingType,
    SecurityContext,
    AuditEvent,
    ComplianceResult,
    MaskingRule,
    BusinessRuleDefinition,
    EncryptionKeyInfo,
    ComplianceReport,
)

datetime.now(timezone.utc)


class TestEnums:
    """Test cases for enum classes"""

    def test_audit_action_enum(self):
        """Test AuditAction enum values"""
        assert AuditAction.CREATE.value == "create"
        assert AuditAction.READ.value == "read"
        assert AuditAction.UPDATE.value == "update"
        assert AuditAction.DELETE.value == "delete"
        assert AuditAction.LOGIN.value == "login"
        assert AuditAction.LOGOUT.value == "logout"
        assert AuditAction.EXPORT.value == "export"
        assert AuditAction.IMPORT.value == "import"
        assert AuditAction.MASK.value == "mask"
        assert AuditAction.DECRYPT.value == "decrypt"

    def test_audit_resource_type_enum(self):
        """Test AuditResourceType enum values"""
        assert AuditResourceType.PATIENT.value == "patient"
        assert AuditResourceType.OBSERVATION.value == "observation"
        assert AuditResourceType.USER.value == "user"
        assert AuditResourceType.INTEGRATION.value == "integration"
        assert AuditResourceType.CONFIGURATION.value == "configuration"
        assert AuditResourceType.REPORT.value == "report"
        assert AuditResourceType.SYSTEM.value == "system"

    def test_compliance_level_enum(self):
        """Test ComplianceLevel enum values"""
        assert ComplianceLevel.COMPLIANT.value == "compliant"
        assert ComplianceLevel.NON_COMPLIANT.value == "non_compliant"
        assert ComplianceLevel.NEEDS_REVIEW.value == "needs_review"
        assert ComplianceLevel.UNKNOWN.value == "unknown"

    def test_masking_type_enum(self):
        """Test MaskingType enum values"""
        assert MaskingType.REDACTION.value == "redaction"
        assert MaskingType.SUBSTITUTION.value == "substitution"
        assert MaskingType.SHUFFLING.value == "shuffling"
        assert MaskingType.ENCRYPTION.value == "encryption"
        assert MaskingType.TOKENIZATION.value == "tokenization"
        assert MaskingType.SYNTHETIC.value == "synthetic"


class TestSecurityContext:
    """Test cases for SecurityContext"""

    def test_security_context_creation(self):
        """Test SecurityContext creation with all fields"""
        context = SecurityContext(
            user_id="test_user",
            user_role="nurse",
            action="read",
            resource_type="patient",
            resource_id="patient_123",
            source_ip="192.168.1.100",
            user_agent="Mozilla/5.0...",
            session_id="session_456",
            permissions=["read_patient", "write_observations"],
            requested_fields=["name", "date_of_birth", "medications"],
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
        )

        assert context.user_id == "test_user"
        assert context.user_role == "nurse"
        assert context.action == "read"
        assert context.resource_type == "patient"
        assert context.resource_id == "patient_123"
        assert context.source_ip == "192.168.1.100"
        assert context.user_agent == "Mozilla/5.0..."
        assert context.session_id == "session_456"
        assert context.permissions == ["read_patient", "write_observations"]
        assert context.requested_fields == [
            "name",
            "date_of_birth",
            "medications"
        ]
        assert context.timestamp == datetime(2024, 1, 1, 12, 0, 0)

    def test_security_context_creation_minimal(self):
        """Test SecurityContext creation with minimal fields"""
        context = SecurityContext(
            user_id="test_user",
            user_role="nurse",
            action="read",
            resource_type="patient",
        )

        assert context.user_id == "test_user"
        assert context.user_role == "nurse"
        assert context.action == "read"
        assert context.resource_type == "patient"
        assert context.resource_id is None
        assert context.source_ip is None
        assert context.user_agent is None
        assert context.session_id is None
        assert context.permissions == []
        assert context.requested_fields == []
        assert isinstance(context.timestamp, datetime)

    def test_security_context_to_dict(self):
        """Test SecurityContext to_dict method"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        context = SecurityContext(
            user_id="test_user",
            user_role="nurse",
            action="read",
            resource_type="patient",
            resource_id="patient_123",
            source_ip="192.168.1.100",
            user_agent="Mozilla/5.0...",
            session_id="session_456",
            permissions=["read_patient"],
            requested_fields=["name", "date_of_birth"],
            timestamp=timestamp,
        )

        result = context.to_dict()

        assert result["user_id"] == "test_user"
        assert result["user_role"] == "nurse"
        assert result["action"] == "read"
        assert result["resource_type"] == "patient"
        assert result["resource_id"] == "patient_123"
        assert result["source_ip"] == "192.168.1.100"
        assert result["user_agent"] == "Mozilla/5.0..."
        assert result["session_id"] == "session_456"
        assert result["permissions"] == ["read_patient"]
        assert result["requested_fields"] == ["name", "date_of_birth"]
        assert result["timestamp"] == timestamp.isoformat()


class TestAuditEvent:
    """Test cases for AuditEvent"""

    def test_audit_event_creation(self):
        """Test AuditEvent creation with all fields"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        event = AuditEvent(
            event_id="event_123",
            timestamp=timestamp,
            user_id="test_user",
            user_role="nurse",
            action=AuditAction.READ,
            resource_type=AuditResourceType.PATIENT,
            resource_id="patient_456",
            source_ip="192.168.1.100",
            user_agent="Mozilla/5.0...",
            request_data={"patient_id": "patient_456"},
            response_data={"status": "success"},
            status="success",
            error_message=None,
            processing_time=0.5,
            compliance_flags=["data_masked", "audit_logged"],
        )

        assert event.event_id == "event_123"
        assert event.timestamp == timestamp
        assert event.user_id == "test_user"
        assert event.user_role == "nurse"
        assert event.action == AuditAction.READ
        assert event.resource_type == AuditResourceType.PATIENT
        assert event.resource_id == "patient_456"
        assert event.source_ip == "192.168.1.100"
        assert event.user_agent == "Mozilla/5.0..."
        assert event.request_data == {"patient_id": "patient_456"}
        assert event.response_data == {"status": "success"}
        assert event.status == "success"
        assert event.error_message is None
        assert event.processing_time == 0.5
        assert event.compliance_flags == ["data_masked", "audit_logged"]

    def test_audit_event_creation_minimal(self):
        """Test AuditEvent creation with minimal fields"""
        event = AuditEvent(
            event_id="event_123",
            timestamp=datetime.now(timezone.utc),
            user_id="test_user",
            action=AuditAction.READ,
            resource_type=AuditResourceType.PATIENT,
            resource_id="patient_456",
            status="success",
        )

        assert event.event_id == "event_123"
        assert event.user_id == "test_user"
        assert event.action == AuditAction.READ
        assert event.resource_type == AuditResourceType.PATIENT
        assert event.resource_id == "patient_456"
        assert event.status == "success"
        assert event.user_role is None
        assert event.source_ip is None
        assert event.user_agent is None
        assert event.request_data is None
        assert event.response_data is None
        assert event.error_message is None
        assert event.processing_time is None
        assert event.compliance_flags is None

    def test_audit_event_to_dict(self):
        """Test AuditEvent to_dict method"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        event = AuditEvent(
            event_id="event_123",
            timestamp=timestamp,
            user_id="test_user",
            user_role="nurse",
            action=AuditAction.READ,
            resource_type=AuditResourceType.PATIENT,
            resource_id="patient_456",
            source_ip="192.168.1.100",
            user_agent="Mozilla/5.0...",
            request_data={"patient_id": "patient_456"},
            response_data={"status": "success"},
            status="success",
            error_message="No errors",
            processing_time=0.5,
            compliance_flags=["data_masked"],
        )

        result = event.to_dict()

        assert result["event_id"] == "event_123"
        assert result["timestamp"] == timestamp.isoformat()
        assert result["user_id"] == "test_user"
        assert result["user_role"] == "nurse"
        assert result["action"] == "read"
        assert result["resource_type"] == "patient"
        assert result["resource_id"] == "patient_456"
        assert result["source_ip"] == "192.168.1.100"
        assert result["user_agent"] == "Mozilla/5.0..."
        assert result["request_data"] == {"patient_id": "patient_456"}
        assert result["response_data"] == {"status": "success"}
        assert result["status"] == "success"
        assert result["error_message"] == "No errors"
        assert result["processing_time"] == 0.5
        assert result["compliance_flags"] == ["data_masked"]


class TestComplianceResult:
    """Test cases for ComplianceResult"""

    def test_compliance_result_creation_compliant(self):
        """Test ComplianceResult creation for compliant case"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        result = ComplianceResult(
            compliant=True,
            violations=[],
            details={"rule_1": {"status": "compliant"}},
            timestamp=timestamp,
            recommendations=["Continue current practices"],
            score=95.5,
        )

        assert result.compliant is True
        assert result.violations == []
        assert result.details == {"rule_1": {"status": "compliant"}}
        assert result.timestamp == timestamp
        assert result.recommendations == ["Continue current practices"]
        assert result.score == 95.5

    def test_compliance_result_creation_non_compliant(self):
        """Test ComplianceResult creation for non-compliant case"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        result = ComplianceResult(
            compliant=False,
            violations=["access_control_001", "audit_control_002"],
            details={
                "access_control_001": {
                    "status": "non_compliant",
                    "reason": "Insufficient access controls",
                },
                "audit_control_002": {
                    "status": "non_compliant",
                    "reason": "Missing audit logs",
                },
            },
            timestamp=timestamp,
            recommendations=[
                "Implement stronger access controls",
                "Enable comprehensive audit logging",
            ],
            score=65.0,
        )

        assert result.compliant is False
        assert result.violations == ["access_control_001", "audit_control_002"]
        assert len(result.details) == 2
        assert result.timestamp == timestamp
        assert len(result.recommendations) == 2
        assert result.score == 65.0

    def test_compliance_result_to_dict(self):
        """Test ComplianceResult to_dict method"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        result = ComplianceResult(
            compliant=False,
            violations=["rule_1"],
            details={"rule_1": {"status": "non_compliant"}},
            timestamp=timestamp,
            recommendations=["Fix rule 1"],
            score=75.0,
        )

        dict_result = result.to_dict()

        assert dict_result["compliant"] is False
        assert dict_result["violations"] == ["rule_1"]
        assert dict_result["details"] == (
            {"rule_1": {"status": "non_compliant"}}
        )
        assert dict_result["timestamp"] == timestamp.isoformat()
        assert dict_result["recommendations"] == ["Fix rule 1"]
        assert dict_result["score"] == 75.0


class TestMaskingRule:
    """Test cases for MaskingRule"""

    def test_masking_rule_creation(self):
        """Test MaskingRule creation"""
        rule = MaskingRule(
            field_name="ssn",
            field_type="ssn",
            masking_type=MaskingType.REDACTION,
            parameters={
                "pattern": "\\d{3}-\\d{2}-\\d{4}",
                "replacement": "XXX-XX-XXXX",
            },
            preserve_format=True,
            preserve_length=True,
        )

        assert rule.field_name == "ssn"
        assert rule.field_type == "ssn"
        assert rule.masking_type == MaskingType.REDACTION
        assert rule.parameters == {
            "pattern": "\\d{3}-\\d{2}-\\d{4}",
            "replacement": "XXX-XX-XXXX",
        }
        assert rule.preserve_format is True
        assert rule.preserve_length is True

    def test_masking_rule_to_dict(self):
        """Test MaskingRule to_dict method"""
        rule = MaskingRule(
            field_name="email",
            field_type="email",
            masking_type=MaskingType.SUBSTITUTION,
            parameters={"domain": "example.com"},
            preserve_format=True,
            preserve_length=False,
        )

        result = rule.to_dict()

        assert result["field_name"] == "email"
        assert result["field_type"] == "email"
        assert result["masking_type"] == "substitution"
        assert result["parameters"] == {"domain": "example.com"}
        assert result["preserve_format"] is True
        assert result["preserve_length"] is False


class TestBusinessRuleDefinition:
    """Test cases for BusinessRuleDefinition"""

    def test_business_rule_definition_creation(self):
        """Test BusinessRuleDefinition creation"""
        rule = BusinessRuleDefinition(
            rule_id="rule_123",
            rule_name="Patient Data Validation",
            description="Validates patient data for completeness and accuracy",
            rule_type="validation",
            conditions=[
                {"field": "ssn", "operator": "not_empty"},
                {"field": "date_of_birth", "operator": "valid_date"},
            ],
            actions=[
                {"action": "log_violation", "message": "Invalid patient data"},
                {
                    "action": "reject_request",
                    "reason": "Data validation failed"
                },
            ],
            priority=100,
            is_active=True,
            compliance_category="HIPAA",
        )

        assert rule.rule_id == "rule_123"
        assert rule.rule_name == "Patient Data Validation"
        assert rule.description == (
            "Validates patient data for completeness and accuracy"
        )
        assert rule.rule_type == "validation"
        assert len(rule.conditions) == 2
        assert len(rule.actions) == 2
        assert rule.priority == 100
        assert rule.is_active is True
        assert rule.compliance_category == "HIPAA"

    def test_business_rule_definition_to_dict(self):
        """Test BusinessRuleDefinition to_dict method"""
        rule = BusinessRuleDefinition(
            rule_id="rule_456",
            rule_name="Data Masking Rule",
            description="Applies masking to sensitive fields",
            rule_type="transformation",
            conditions=[{
                "field": "ssn",
                "operator": "contains_sensitive_data"
            }],
            actions=[
                {
                    "action": "mask_field",
                    "field": "ssn",
                    "method": "redaction"
                }
            ],
            priority=200,
            is_active=True,
        )

        result = rule.to_dict()

        assert result["rule_id"] == "rule_456"
        assert result["rule_name"] == "Data Masking Rule"
        assert result["description"] == "Applies masking to sensitive fields"
        assert result["rule_type"] == "transformation"
        assert len(result["conditions"]) == 1
        assert len(result["actions"]) == 1
        assert result["priority"] == 200
        assert result["is_active"] is True
        assert result["compliance_category"] is None


class TestEncryptionKeyInfo:
    """Test cases for EncryptionKeyInfo"""

    def test_encryption_key_info_creation(self):
        """Test EncryptionKeyInfo creation"""
        created_at = datetime(2024, 1, 1, 12, 0, 0)
        expires_at = datetime(2025, 1, 1, 12, 0, 0)

        key_info = EncryptionKeyInfo(
            key_id="key_123",
            key_name="AES-256-GCM-Master",
            key_type="symmetric",
            algorithm="AES_256_GCM",
            key_usage="data_encryption",
            is_active=True,
            is_expired=False,
            days_until_expiry=365,
            created_at=created_at,
            expires_at=expires_at,
        )

        assert key_info.key_id == "key_123"
        assert key_info.key_name == "AES-256-GCM-Master"
        assert key_info.key_type == "symmetric"
        assert key_info.algorithm == "AES_256_GCM"
        assert key_info.key_usage == "data_encryption"
        assert key_info.is_active is True
        assert key_info.is_expired is False
        assert key_info.days_until_expiry == 365
        assert key_info.created_at == created_at
        assert key_info.expires_at == expires_at

    def test_encryption_key_info_expired(self):
        """Test EncryptionKeyInfo for expired key"""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        expires_at = datetime(2023, 12, 31, 12, 0, 0)

        key_info = EncryptionKeyInfo(
            key_id="key_456",
            key_name="Expired-Key",
            key_type="asymmetric",
            algorithm="RSA_2048",
            key_usage="key_exchange",
            is_active=False,
            is_expired=True,
            days_until_expiry=None,
            created_at=created_at,
            expires_at=expires_at,
        )

        assert key_info.key_id == "key_456"
        assert key_info.is_active is False
        assert key_info.is_expired is True
        assert key_info.days_until_expiry is None

    def test_encryption_key_info_to_dict(self):
        """Test EncryptionKeyInfo to_dict method"""
        created_at = datetime(2024, 1, 1, 12, 0, 0)
        expires_at = datetime(2025, 1, 1, 12, 0, 0)

        key_info = EncryptionKeyInfo(
            key_id="key_789",
            key_name="Test-Key",
            key_type="symmetric",
            algorithm="AES_256_GCM",
            key_usage="data_encryption",
            is_active=True,
            is_expired=False,
            days_until_expiry=365,
            created_at=created_at,
            expires_at=expires_at,
        )

        result = key_info.to_dict()

        assert result["key_id"] == "key_789"
        assert result["key_name"] == "Test-Key"
        assert result["key_type"] == "symmetric"
        assert result["algorithm"] == "AES_256_GCM"
        assert result["key_usage"] == "data_encryption"
        assert result["is_active"] is True
        assert result["is_expired"] is False
        assert result["days_until_expiry"] == 365
        assert result["created_at"] == created_at.isoformat()
        assert result["expires_at"] == expires_at.isoformat()


class TestComplianceReport:
    """Test cases for ComplianceReport"""

    def test_compliance_report_creation(self):
        """Test ComplianceReport creation"""
        period_start = datetime(2024, 1, 1, 0, 0, 0)
        period_end = datetime(2024, 1, 31, 23, 59, 59)
        generated_at = datetime(2024, 2, 1, 12, 0, 0)

        report = ComplianceReport(
            report_id="report_123",
            report_type="HIPAA_MONTHLY",
            period_start=period_start,
            period_end=period_end,
            compliance_score=95.5,
            findings=[
                {
                    "rule_id": "access_control_001",
                    "status": "compliant",
                    "details": "Access controls properly configured",
                },
                {
                    "rule_id": "audit_control_002",
                    "status": "non_compliant",
                    "details": "Missing audit logs for 3 events",
                },
            ],
            recommendations=[
                "Implement comprehensive audit logging",
                "Review access control policies",
            ],
            status="final",
            generated_at=generated_at,
        )

        assert report.report_id == "report_123"
        assert report.report_type == "HIPAA_MONTHLY"
        assert report.period_start == period_start
        assert report.period_end == period_end
        assert report.compliance_score == 95.5
        assert len(report.findings) == 2
        assert len(report.recommendations) == 2
        assert report.status == "final"
        assert report.generated_at == generated_at

    def test_compliance_report_creation_draft(self):
        """Test ComplianceReport creation with draft status"""
        period_start = datetime(2024, 1, 1, 0, 0, 0)
        period_end = datetime(2024, 1, 31, 23, 59, 59)

        report = ComplianceReport(
            report_id="report_456",
            report_type="HIPAA_MONTHLY",
            period_start=period_start,
            period_end=period_end,
            compliance_score=85.0,
            findings=[],
            recommendations=[],
            status="draft",
        )

        assert report.report_id == "report_456"
        assert report.status == "draft"
        assert report.findings == []
        assert report.recommendations == []
        assert isinstance(report.generated_at, datetime)

    def test_compliance_report_to_dict(self):
        """Test ComplianceReport to_dict method"""
        period_start = datetime(2024, 1, 1, 0, 0, 0)
        period_end = datetime(2024, 1, 31, 23, 59, 59)
        generated_at = datetime(2024, 2, 1, 12, 0, 0)

        report = ComplianceReport(
            report_id="report_789",
            report_type="HIPAA_MONTHLY",
            period_start=period_start,
            period_end=period_end,
            compliance_score=90.0,
            findings=[{"rule_id": "test_rule", "status": "compliant"}],
            recommendations=["Test recommendation"],
            status="final",
            generated_at=generated_at,
        )

        result = report.to_dict()

        assert result["report_id"] == "report_789"
        assert result["report_type"] == "HIPAA_MONTHLY"
        assert result["period_start"] == period_start.isoformat()
        assert result["period_end"] == period_end.isoformat()
        assert result["compliance_score"] == 90.0
        assert len(result["findings"]) == 1
        assert len(result["recommendations"]) == 1
        assert result["status"] == "final"
        assert result["generated_at"] == generated_at.isoformat()
