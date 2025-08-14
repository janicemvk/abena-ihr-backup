"""
Unit tests for Abena Security SDK Client

Tests the main client interface and all its methods.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta

from abena_ihr_security.sdk import (
    AbenaSecurityClient,
    AbenaSecurityConfig,
    SecurityContext,
    AuditEvent,
    AuditAction,
    AuditResourceType,
)
from abena_ihr_security.sdk.exceptions import (
    AbenaSecurityException,
    ComplianceException,
)

datetime.now(timezone.utc)


class TestAbenaSecurityClient:
    """Test cases for AbenaSecurityClient"""

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return AbenaSecurityConfig(
            database_url="sqlite:///test.db",
            redis_url="redis://localhost:6379",
            master_key_path="/tmp/test_master.key",
            debug_mode=True,
        )

    @pytest.fixture
    def client(self, config):
        """Create test client"""
        return AbenaSecurityClient(config)

    @pytest.fixture
    def security_context(self):
        """Create test security context"""
        return SecurityContext(
            user_id="test_user",
            user_role="nurse",
            action="read",
            resource_type="patient",
            source_ip="192.168.1.100",
            permissions=["read_patient"],
        )

    @pytest.fixture
    def test_data(self):
        """Create test patient data"""
        return {
            "id": "patient_123",
            "name": "John Doe",
            "ssn": "123-45-6789",
            "date_of_birth": "1985-03-15",
            "phone": "555-123-4567",
        }

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization"""
        # Mock the module layer initialization
        with patch(
            "abena_ihr_security.sdk.client.ModuleLayer"
        ) as mock_module_layer:
            mock_module_layer.return_value = Mock()

            await client.initialize()

            assert client._initialized is True
            assert client.module_layer is not None

    @pytest.mark.asyncio
    async def test_client_initialization_failure(self, client):
        """Test client initialization failure"""
        with patch(
            "abena_ihr_security.sdk.client.ModuleLayer"
        ) as mock_module_layer:
            mock_module_layer.side_effect = Exception(
                "Database connection failed"
            )

            with pytest.raises(AbenaSecurityException) as exc_info:
                await client.initialize()

            assert "Initialization failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_data_with_security_success(
        self, client, security_context, test_data
    ):
        """Test successful data processing with security"""
        # Mock the module layer
        mock_module_layer = Mock()
        mock_module_layer.process_data_with_security = AsyncMock(
            return_value={
                "processed_data": test_data,
                "compliance_status": "compliant",
                "security_flags": ["data_masked"],
                "processing_time": 0.5,
            }
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.process_data_with_security(
            test_data, security_context, "read"
        )

        assert result["compliance_status"] == "compliant"
        assert "data_masked" in result["security_flags"]
        assert result["processing_time"] == 0.5

    @pytest.mark.asyncio
    async def test_process_data_with_security_not_initialized(
        self, client, security_context, test_data
    ):
        """Test data processing when client not initialized"""
        with pytest.raises(AbenaSecurityException) as exc_info:
            await client.process_data_with_security(
                test_data, security_context, "read"
            )
        assert "Client not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_data_with_security_compliance_violation(
        self, client, security_context, test_data
    ):
        """Test data processing with compliance violation"""
        # Mock the module layer to raise compliance exception
        mock_module_layer = Mock()
        mock_module_layer.process_data_with_security = AsyncMock(
            side_effect=Exception(
                "HIPAA compliance violation: unauthorized access"
            )
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        with pytest.raises(ComplianceException) as exc_info:
            await client.process_data_with_security(
                test_data, security_context, "read"
            )

        assert "Compliance validation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_encrypt_data(self, client):
        """Test data encryption"""
        mock_module_layer = Mock()
        mock_module_layer.encryption_service = Mock()
        mock_module_layer.encryption_service.encrypt_data = AsyncMock()
        mock_module_layer.encryption_service.encrypt_data.return_value = (
            b"encrypted_data"
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.encrypt_data("test_data", "key_123")

        assert await result == b"encrypted_data"
        (
            mock_module_layer.encryption_service
            .encrypt_data
            .assert_called_once_with(
                "test_data",
                "key_123",
            )
        )

    @pytest.mark.asyncio
    async def test_decrypt_data(self, client):
        """Test data decryption"""
        mock_module_layer = Mock()
        mock_module_layer.encryption_service = Mock()
        mock_module_layer.encryption_service.decrypt_data = AsyncMock(
            return_value=b"decrypted_data"
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.decrypt_data(b"encrypted_data", "key_123")

        assert await result == b"decrypted_data"
        (
            mock_module_layer.encryption_service
            .decrypt_data
            .assert_called_once_with(
                b"encrypted_data",
                "key_123",
            )
        )

    @pytest.mark.asyncio
    async def test_mask_data(self, client, test_data):
        """Test data masking"""
        mock_module_layer = Mock()
        mock_module_layer.data_masking_service = Mock()
        masked_data = test_data.copy()
        masked_data["ssn"] = "XXX-XX-6789"
        mock_module_layer.data_masking_service.mask_data = AsyncMock(
            return_value=masked_data
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.mask_data(test_data, "nurse")
        result = await result

        assert result["ssn"] == "XXX-XX-6789"
        (
            mock_module_layer.data_masking_service
            .mask_data
            .assert_called_once_with(
                test_data,
                "nurse",
            )
        )

    @pytest.mark.asyncio
    async def test_log_audit_event(self, client):
        """Test audit event logging"""
        mock_module_layer = Mock()
        mock_module_layer.audit_generator = Mock()
        mock_module_layer.audit_generator.log_event = AsyncMock(
            return_value="event_123"
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        event = AuditEvent(
            event_id="test_event",
            timestamp=datetime.now(timezone.utc),
            user_id="test_user",
            action=AuditAction.READ,
            resource_type=AuditResourceType.PATIENT,
            resource_id="patient_123",
            status="success",
        )

        result = await client.log_audit_event(event)

        assert result == "event_123"
        # mock_module_layer.audit_generator.log_event.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_validate_compliance_success(self, client, security_context):
        """Test successful compliance validation"""
        mock_module_layer = Mock()
        mock_module_layer.hipaa_validator = Mock()
        mock_module_layer.hipaa_validator.validate_compliance = AsyncMock(
            return_value={
                "access_control_001": Mock(status=Mock(value="compliant")),
                "audit_control_001": Mock(status=Mock(value="compliant")),
            }
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.validate_compliance(security_context)

        assert result.compliant is True
        assert len(result.violations) == 0

    @pytest.mark.asyncio
    async def test_validate_compliance_violation(
        self,
        client,
        security_context
    ):
        """Test compliance validation with violations"""
        mock_module_layer = Mock()
        mock_module_layer.hipaa_validator = Mock()
        mock_module_layer.hipaa_validator.validate_compliance = AsyncMock(
            return_value={
                "access_control_001": Mock(status=Mock(value="non_compliant")),
                "audit_control_001": Mock(status=Mock(value="compliant")),
            }
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.validate_compliance(security_context)

        assert result.compliant is False
        assert "access_control_001" in result.violations

    @pytest.mark.asyncio
    async def test_get_configuration(self, client):
        """Test configuration retrieval"""
        mock_module_layer = Mock()
        mock_module_layer.config_manager = Mock()
        mock_config = {
            "integration_name": "Epic_EMR",
            "base_url": "https://fhir.epic.com",
            "timeout": 30,
        }
        mock_module_layer.config_manager.get_integration_config = AsyncMock(
            return_value=mock_config
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.get_configuration("Epic_EMR")

        assert await result == mock_config
        (
            mock_module_layer.config_manager
            .get_integration_config
            .assert_called_once_with(
                "Epic_EMR",
                include_secrets=False,
            )
        )

    @pytest.mark.asyncio
    async def test_apply_business_rules(self, client, test_data):
        """Test business rules application"""
        mock_module_layer = Mock()
        mock_module_layer.business_rules_engine = Mock()
        mock_result = {
            "processed_data": test_data,
            "rules_applied": ["validation_rule_1"],
            "actions_executed": [],
            "errors": [],
        }
        mock_module_layer.business_rules_engine.apply_rules = Mock(
            return_value=mock_result
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.apply_business_rules(test_data, "validation")

        assert result == mock_result
        (
            mock_module_layer.business_rules_engine
            .apply_rules
            .assert_called_once_with(
                test_data,
                "validation",
            )
        )

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, client):
        """Test compliance report generation"""
        mock_module_layer = Mock()
        mock_module_layer.hipaa_validator = Mock()
        mock_report = {
            "report_id": "report_123",
            "compliance_score": 95.5,
            "findings": [],
            "recommendations": [],
        }
        (
            mock_module_layer.hipaa_validator
            .generate_compliance_report
        ) = AsyncMock(
            return_value=mock_report,
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)

        result = await client.generate_compliance_report(start_date, end_date)

        assert result == mock_report
        (
            mock_module_layer.hipaa_validator
            .generate_compliance_report
            .assert_called_once_with(
                start_date,
                end_date,
            )
        )

    @pytest.mark.asyncio
    async def test_get_compliance_dashboard(self, client):
        """Test compliance dashboard generation"""
        mock_module_layer = Mock()
        mock_dashboard = {
            "compliance_summary": {
                "hipaa_compliance_score": 95.5,
                "total_violations": 2,
            },
            "audit_summary": {"total_events": 1000, "failed_events": 5},
        }
        mock_module_layer.generate_compliance_dashboard = AsyncMock(
            return_value=mock_dashboard
        )
        client.module_layer = mock_module_layer
        client._initialized = True

        result = await client.get_compliance_dashboard()

        assert result == mock_dashboard
        mock_module_layer.generate_compliance_dashboard.assert_called_once()

    @pytest.mark.asyncio
    async def test_client_close(self, client):
        """Test client cleanup"""
        mock_module_layer = Mock()
        mock_module_layer.redis_client = AsyncMock()
        client.module_layer = mock_module_layer
        client._initialized = True

        await client.close()

        assert client._initialized is False
        mock_module_layer.redis_client.aclose.assert_called_once()

    def test_context_manager(self, client):
        """Test client as context manager"""
        with patch.object(client, "close", new_callable=AsyncMock):
            with client as ctx_client:
                assert ctx_client == client

            client.close.assert_called_once()


class TestSecurityContext:
    """Test cases for SecurityContext"""

    def test_security_context_creation(self):
        """Test SecurityContext creation"""
        context = SecurityContext(
            user_id="test_user",
            user_role="nurse",
            action="read",
            resource_type="patient",
            source_ip="192.168.1.100",
            permissions=["read_patient"],
            requested_fields=["name", "date_of_birth"],
        )

        assert context.user_id == "test_user"
        assert context.user_role == "nurse"
        assert context.action == "read"
        assert context.resource_type == "patient"
        assert context.source_ip == "192.168.1.100"
        assert context.permissions == ["read_patient"]
        assert context.requested_fields == ["name", "date_of_birth"]

    def test_security_context_to_dict(self):
        """Test SecurityContext to_dict method"""
        context = SecurityContext(
            user_id="test_user",
            user_role="nurse",
            action="read",
            resource_type="patient",
        )

        result = context.to_dict()

        assert result["user_id"] == "test_user"
        assert result["user_role"] == "nurse"
        assert result["action"] == "read"
        assert result["resource_type"] == "patient"
        assert "timestamp" in result


class TestAuditEvent:
    """Test cases for AuditEvent"""

    def test_audit_event_creation(self):
        """Test AuditEvent creation"""
        event = AuditEvent(
            event_id="test_event",
            timestamp=datetime.now(timezone.utc),
            user_id="test_user",
            action=AuditAction.READ,
            resource_type=AuditResourceType.PATIENT,
            resource_id="patient_123",
            status="success",
        )

        assert event.event_id == "test_event"
        assert event.user_id == "test_user"
        assert event.action == AuditAction.READ
        assert event.resource_type == AuditResourceType.PATIENT
        assert event.status == "success"

    def test_audit_event_to_dict(self):
        """Test AuditEvent to_dict method"""
        event = AuditEvent(
            event_id="test_event",
            timestamp=datetime.now(timezone.utc),
            user_id="test_user",
            action=AuditAction.READ,
            resource_type=AuditResourceType.PATIENT,
            resource_id="patient_123",
            status="success",
        )

        result = event.to_dict()

        assert result["event_id"] == "test_event"
        assert result["user_id"] == "test_user"
        assert result["action"] == "read"
        assert result["resource_type"] == "patient"
        assert result["status"] == "success"
