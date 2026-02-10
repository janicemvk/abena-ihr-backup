# Unit tests for Workflow Integration - Updated for Abena SDK
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.workflow_integration.workflow_orchestrator import (
    EMRIntegrationManager, 
    IntegrationType, 
    ClinicalNoteGenerator, 
    RealTimeAlertSystem, 
    AlertPriority
)
from src.core.abena_sdk import AbenaSDK

class TestEMRIntegrationManager:
    """Unit tests for EMR Integration using Abena SDK"""
    
    @pytest.fixture
    def mock_abena_sdk(self):
        """Mock Abena SDK for testing"""
        mock_sdk = Mock(spec=AbenaSDK)
        mock_sdk.get_patient_data = AsyncMock()
        mock_sdk.create_alert = AsyncMock()
        return mock_sdk
    
    @pytest.fixture
    def mock_emr_config(self):
        return {
            'type': 'epic',
            'base_url': 'https://test-fhir.epic.com',
            'client_id': 'test_client',
            'client_secret': 'test_secret',
            'access_token': 'test_token'
        }
    
    def test_emr_manager_initialization(self, mock_abena_sdk, mock_emr_config):
        """Test EMR manager initialization with Abena SDK"""
        manager = EMRIntegrationManager(mock_abena_sdk, IntegrationType.EPIC, mock_emr_config)
        
        assert manager.abena == mock_abena_sdk
        assert manager.integration_type == IntegrationType.EPIC
        assert manager.config == mock_emr_config
        assert hasattr(manager, 'logger')
    
    @pytest.mark.asyncio
    async def test_patient_data_retrieval(self, mock_abena_sdk, mock_emr_config):
        """Test patient data retrieval using Abena SDK"""
        # Mock Abena SDK response
        mock_abena_sdk.get_patient_data.return_value = {
            'patient_id': 'test_patient',
            'encrypted_data': 'mock_encrypted_data'
        }
        
        manager = EMRIntegrationManager(mock_abena_sdk, IntegrationType.EPIC, mock_emr_config)
        patient_data = await manager.get_patient_data('test_patient')
        
        # Verify Abena SDK was called
        mock_abena_sdk.get_patient_data.assert_called_once_with('test_patient', 'emr_integration')
        
        assert 'patient' in patient_data
        assert 'observations' in patient_data
        assert 'medications' in patient_data
        assert 'retrieved_at' in patient_data
        assert patient_data['emr_type'] == 'epic'
    
    @pytest.mark.asyncio
    async def test_patient_data_retrieval_failure(self, mock_abena_sdk, mock_emr_config):
        """Test patient data retrieval failure handling"""
        # Mock Abena SDK failure
        mock_abena_sdk.get_patient_data.side_effect = Exception("SDK Error")
        
        manager = EMRIntegrationManager(mock_abena_sdk, IntegrationType.EPIC, mock_emr_config)
        patient_data = await manager.get_patient_data('test_patient')
        
        # Verify error was logged through Abena SDK
        mock_abena_sdk.create_alert.assert_called_once()
        assert patient_data == {}

class TestClinicalNoteGenerator:
    """Unit tests for Clinical Note Generation using Abena SDK"""
    
    @pytest.fixture
    def mock_abena_sdk(self):
        """Mock Abena SDK for testing"""
        mock_sdk = Mock(spec=AbenaSDK)
        mock_sdk.get_patient_data = AsyncMock()
        mock_sdk.save_treatment_plan = AsyncMock()
        mock_sdk.create_alert = AsyncMock()
        return mock_sdk
    
    def test_note_generator_initialization(self, mock_abena_sdk):
        """Test note generator initialization with Abena SDK"""
        generator = ClinicalNoteGenerator(mock_abena_sdk)
        
        assert generator.abena == mock_abena_sdk
        assert hasattr(generator, 'templates')
        assert 'pain_management' in generator.templates
        assert 'adverse_event_alert' in generator.templates
        assert 'treatment_optimization' in generator.templates
    
    @pytest.mark.asyncio
    async def test_pain_management_note_generation(self, mock_abena_sdk):
        """Test pain management note generation using Abena SDK"""
        # Mock Abena SDK responses
        mock_abena_sdk.get_patient_data.return_value = {
            'patient_id': 'TEST_PATIENT_001',
            'name': 'Test Patient'
        }
        mock_abena_sdk.save_treatment_plan.return_value = "note_123"
        
        generator = ClinicalNoteGenerator(mock_abena_sdk)
        
        abena_insights = {
            'clinical_assessment': 'Chronic pain evaluation',
            'success_probability': 0.75,
            'risk_level': 'MODERATE',
            'key_factors': ['High baseline pain', 'Genomic variant present'],
            'recommendations': ['Reduce opioid dose', 'Add CBD therapy'],
            'warnings': ['Monitor for side effects'],
            'genomics': {'CYP2C9_activity': 0.6},
            'treatment_plan': 'Multimodal approach recommended'
        }
        
        note = await generator.generate_pain_management_note(
            'TEST_PATIENT_001', 
            abena_insights, 
            'Dr. Test Provider'
        )
        
        # Verify Abena SDK was called
        mock_abena_sdk.get_patient_data.assert_called_once_with('TEST_PATIENT_001', 'pain_management_note')
        mock_abena_sdk.save_treatment_plan.assert_called_once()
        
        assert 'ABENA IHR CLINICAL ANALYSIS' in note
        assert 'TEST_PATIENT_001' in note
        assert 'Dr. Test Provider' in note
        assert '75.0%' in note  # Success probability
        assert 'Reduce opioid dose' in note
    
    @pytest.mark.asyncio
    async def test_adverse_event_alert_generation(self, mock_abena_sdk):
        """Test adverse event alert generation using Abena SDK"""
        # Mock Abena SDK responses
        mock_abena_sdk.get_patient_data.return_value = {
            'patient_id': 'TEST_PATIENT_001',
            'name': 'Test Patient'
        }
        mock_abena_sdk.create_alert.return_value = "alert_123"
        
        generator = ClinicalNoteGenerator(mock_abena_sdk)
        
        risk_assessment = {
            'overall_risk_level': 'HIGH',
            'risk_scores': {
                'severe_side_effects': {
                    'probability': 0.8,
                    'risk_level': 'HIGH'
                },
                'drug_interaction': {
                    'probability': 0.3,
                    'risk_level': 'LOW'
                }
            }
        }
        
        alert = await generator.generate_adverse_event_alert(
            'TEST_PATIENT_001',
            risk_assessment,
            'Dr. Test Provider'
        )
        
        # Verify Abena SDK was called
        mock_abena_sdk.get_patient_data.assert_called_once_with('TEST_PATIENT_001', 'adverse_event_alert')
        mock_abena_sdk.create_alert.assert_called_once()
        
        assert 'ADVERSE EVENT RISK ALERT' in alert
        assert 'HIGH' in alert
        assert 'Severe Side Effects' in alert
        assert '80.0%' in alert

class TestRealTimeAlertSystem:
    """Unit tests for Real-Time Alert System using Abena SDK"""
    
    @pytest.fixture
    def mock_abena_sdk(self):
        """Mock Abena SDK for testing"""
        mock_sdk = Mock(spec=AbenaSDK)
        mock_sdk.get_patient_data = AsyncMock()
        mock_sdk.save_treatment_plan = AsyncMock()
        mock_sdk.create_alert = AsyncMock()
        return mock_sdk
    
    def test_alert_system_initialization(self, mock_abena_sdk):
        """Test alert system initialization with Abena SDK"""
        alert_system = RealTimeAlertSystem(mock_abena_sdk)
        
        assert alert_system.abena == mock_abena_sdk
        assert hasattr(alert_system, 'active_alerts')
    
    @pytest.mark.asyncio
    async def test_alert_creation(self, mock_abena_sdk):
        """Test alert creation using Abena SDK"""
        # Mock Abena SDK response
        mock_abena_sdk.create_alert.return_value = "alert_123"
        
        alert_system = RealTimeAlertSystem(mock_abena_sdk)
        
        alert_id = await alert_system.create_alert(
            patient_id="TEST_PATIENT_001",
            provider_id="PROVIDER_001",
            alert_type="treatment_warning",
            priority=AlertPriority.HIGH,
            title="High Risk Treatment",
            message="Patient shows high risk for adverse events",
            recommendations=["Consider alternative treatment", "Implement monitoring"],
            duration_hours=24
        )
        
        # Verify Abena SDK was called
        mock_abena_sdk.create_alert.assert_called_once()
        
        assert alert_id in alert_system.active_alerts
        alert = alert_system.active_alerts[alert_id]
        assert alert.patient_id == "TEST_PATIENT_001"
        assert alert.priority == AlertPriority.HIGH
        assert not alert.acknowledged
    
    @pytest.mark.asyncio
    async def test_alert_acknowledgment(self, mock_abena_sdk):
        """Test alert acknowledgment using Abena SDK"""
        alert_system = RealTimeAlertSystem(mock_abena_sdk)
        
        alert_id = await alert_system.create_alert(
            patient_id="TEST_PATIENT_001",
            provider_id="PROVIDER_001",
            alert_type="test_alert",
            priority=AlertPriority.MODERATE,
            title="Test Alert",
            message="Test message",
            recommendations=["Test recommendation"]
        )
        
        # Acknowledge alert
        success = await alert_system.acknowledge_alert(alert_id, "PROVIDER_001")
        
        # Verify Abena SDK was called
        mock_abena_sdk.save_treatment_plan.assert_called_once()
        
        assert success
        assert alert_system.active_alerts[alert_id].acknowledged
    
    @pytest.mark.asyncio
    async def test_active_alerts_retrieval(self, mock_abena_sdk):
        """Test retrieval of active alerts for provider using Abena SDK"""
        alert_system = RealTimeAlertSystem(mock_abena_sdk)
        
        # Create multiple alerts
        await alert_system.create_alert(
            patient_id="PATIENT_001", provider_id="PROVIDER_001",
            alert_type="critical", priority=AlertPriority.CRITICAL,
            title="Critical Alert", message="Critical message", recommendations=[]
        )
        
        await alert_system.create_alert(
            patient_id="PATIENT_002", provider_id="PROVIDER_001",
            alert_type="high", priority=AlertPriority.HIGH,
            title="High Alert", message="High message", recommendations=[]
        )
        
        await alert_system.create_alert(
            patient_id="PATIENT_003", provider_id="PROVIDER_002",
            alert_type="low", priority=AlertPriority.LOW,
            title="Low Alert", message="Low message", recommendations=[]
        )
        
        # Get alerts for PROVIDER_001
        provider_alerts = await alert_system.get_active_alerts_for_provider("PROVIDER_001")
        
        # Verify Abena SDK was called
        mock_abena_sdk.get_patient_data.assert_called()
        
        assert len(provider_alerts) == 2
        # Should be sorted by priority (CRITICAL first)
        assert provider_alerts[0].priority == AlertPriority.CRITICAL
        assert provider_alerts[1].priority == AlertPriority.HIGH 