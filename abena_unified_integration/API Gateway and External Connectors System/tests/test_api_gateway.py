"""
Tests for the API Gateway module using Abena SDK
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock

from api_gateway import APIGateway, PatientData, ObservationData, APIResponse

class TestAPIGateway:
    """Test cases for the API Gateway"""
    
    @pytest.fixture
    def api_gateway(self):
        """Create a test API Gateway instance"""
        with patch('api_gateway.AbenaSDK') as mock_sdk:
            # Mock the Abena SDK
            mock_sdk_instance = AsyncMock()
            mock_sdk.return_value = mock_sdk_instance
            
            gateway = APIGateway(enable_trusted_hosts=False)  # Disable for testing
            return gateway
    
    @pytest.fixture
    def sample_patient(self):
        """Create a sample patient for testing"""
        return PatientData(
            mrn="TEST123",
            first_name="John",
            last_name="Doe",
            gender="M",
            birth_date="1990-01-01",
            email="john.doe@test.com",
            phone="+1234567890"
        )
    
    @pytest.fixture
    def sample_observation(self):
        """Create a sample observation for testing"""
        return ObservationData(
            patient_id="patient_123",
            observation_type="heart_rate",
            value=75.0,
            unit="bpm",
            timestamp=datetime.now(timezone.utc),
            source_device="test_device"
        )
    
    def test_api_gateway_initialization(self, api_gateway):
        """Test API Gateway initialization"""
        assert api_gateway is not None
        assert hasattr(api_gateway, 'app')
        assert hasattr(api_gateway, 'abena')
        # Verify Abena SDK was initialized
        assert api_gateway.abena is not None
    
    def test_patient_data_validation(self, sample_patient):
        """Test patient data validation"""
        assert sample_patient.mrn == "TEST123"
        assert sample_patient.first_name == "John"
        assert sample_patient.last_name == "Doe"
        assert sample_patient.gender == "M"
    
    def test_observation_data_validation(self, sample_observation):
        """Test observation data validation"""
        assert sample_observation.patient_id == "patient_123"
        assert sample_observation.observation_type == "heart_rate"
        assert sample_observation.value == 75.0
        assert sample_observation.unit == "bpm"
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, api_gateway):
        """Test health check endpoint"""
        from fastapi.testclient import TestClient
        
        client = TestClient(api_gateway.app)
        response = client.get("/health")
        
        print(f"Health check response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_create_patient_endpoint_with_auth(self, api_gateway, sample_patient):
        """Test create patient endpoint with authentication"""
        from fastapi.testclient import TestClient
        from fastapi.encoders import jsonable_encoder
        
        client = TestClient(api_gateway.app)
        
        # Mock successful authentication
        api_gateway.abena.verifyRequest = AsyncMock()
        api_gateway.abena.storePatientData = AsyncMock()
        
        # Test with authentication header
        response = client.post(
            "/api/v1/patients",
            json=jsonable_encoder(sample_patient),
            headers={"Authorization": "Bearer test-token"}
        )
        
        print(f"Create patient response: {response.status_code} - {response.text}")
        # Should return 200 with successful authentication
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "patient_id" in data["data"]
    
    @pytest.mark.asyncio
    async def test_create_patient_endpoint_without_auth(self, api_gateway, sample_patient):
        """Test create patient endpoint without authentication"""
        from fastapi.testclient import TestClient
        from fastapi.encoders import jsonable_encoder
        
        client = TestClient(api_gateway.app)
        
        # Test without authentication header
        response = client.post(
            "/api/v1/patients",
            json=jsonable_encoder(sample_patient)
        )
        
        print(f"Create patient response (no auth): {response.status_code} - {response.text}")
        # Should return 401 without authentication
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_observation_endpoint_with_auth(self, api_gateway, sample_observation):
        """Test create observation endpoint with authentication"""
        from fastapi.testclient import TestClient
        from fastapi.encoders import jsonable_encoder
        
        client = TestClient(api_gateway.app)
        
        # Mock successful authentication
        api_gateway.abena.verifyRequest = AsyncMock()
        api_gateway.abena.storeObservationData = AsyncMock()
        
        # Test with authentication header
        response = client.post(
            "/api/v1/observations",
            json=jsonable_encoder(sample_observation),
            headers={"Authorization": "Bearer test-token"}
        )
        
        print(f"Create observation response: {response.status_code} - {response.text}")
        # Should return 200 with successful authentication
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "observation_id" in data["data"]
    
    @pytest.mark.asyncio
    async def test_get_patient_endpoint_with_auth(self, api_gateway):
        """Test get patient endpoint with authentication"""
        from fastapi.testclient import TestClient
        
        client = TestClient(api_gateway.app)
        
        # Mock successful authentication and data retrieval
        api_gateway.abena.verifyRequest = AsyncMock()
        api_gateway.abena.getPatientData = AsyncMock(return_value={
            "patient_id": "patient_123",
            "mrn": "TEST123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Test with authentication header
        response = client.get(
            "/api/v1/patients/patient_123",
            headers={"Authorization": "Bearer test-token"}
        )
        
        print(f"Get patient response: {response.status_code} - {response.text}")
        # Should return 200 with successful authentication
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "patient_id" in data["data"]
    
    @pytest.mark.asyncio
    async def test_get_observations_endpoint_with_auth(self, api_gateway):
        """Test get observations endpoint with authentication"""
        from fastapi.testclient import TestClient
        
        client = TestClient(api_gateway.app)
        
        # Mock successful authentication and data retrieval
        api_gateway.abena.verifyRequest = AsyncMock()
        api_gateway.abena.getPatientObservations = AsyncMock(return_value=[
            {"observation_id": "obs_1", "type": "heart_rate", "value": 75.0},
            {"observation_id": "obs_2", "type": "blood_pressure", "value": 120.0}
        ])
        
        # Test with authentication header
        response = client.get(
            "/api/v1/observations/patient_123",
            headers={"Authorization": "Bearer test-token"}
        )
        
        print(f"Get observations response: {response.status_code} - {response.text}")
        # Should return 200 with successful authentication
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "observations" in data["data"]
        assert len(data["data"]["observations"]) == 2
    
    def test_api_response_model(self):
        """Test API response model"""
        response = APIResponse(
            success=True,
            message="Test successful",
            data={"test": "data"}
        )
        
        assert response.success == True
        assert response.message == "Test successful"
        assert response.data == {"test": "data"}
        assert response.errors is None
        
        # Test error response
        error_response = APIResponse(
            success=False,
            message="Test failed",
            errors=["Error 1", "Error 2"]
        )
        
        assert error_response.success == False
        assert error_response.message == "Test failed"
        assert error_response.errors == ["Error 1", "Error 2"]
        assert error_response.data is None

    @pytest.mark.asyncio
    async def test_audit_logging(self, api_gateway):
        """Test that audit logging is handled by Abena SDK"""
        from fastapi.testclient import TestClient
        
        client = TestClient(api_gateway.app)
        
        # Mock audit logging
        api_gateway.abena.logAuditEvent = AsyncMock()
        
        # Make a request
        response = client.get("/health")
        
        # Verify audit logging was called
        api_gateway.abena.logAuditEvent.assert_called_once()
        call_args = api_gateway.abena.logAuditEvent.call_args[0][0]
        assert "endpoint" in call_args
        assert "method" in call_args
        assert "status_code" in call_args
        assert "timestamp" in call_args

class TestDeviceData:
    """Test cases for device data models"""
    
    def test_device_data_validation(self):
        """Test device data validation"""
        from api_gateway import DeviceData
        
        device_data = DeviceData(
            device_id="device_123",
            patient_id="patient_123",
            device_type="fitbit",
            measurements=[],
            sync_timestamp=datetime.now(timezone.utc)
        )
        
        assert device_data.device_id == "device_123"
        assert device_data.patient_id == "patient_123"
        assert device_data.device_type == "fitbit"
        assert isinstance(device_data.measurements, list)
        assert isinstance(device_data.sync_timestamp, datetime)

class TestAbenaSDKIntegration:
    """Test cases for Abena SDK integration"""
    
    @pytest.mark.asyncio
    async def test_abena_sdk_initialization(self):
        """Test Abena SDK is properly initialized"""
        with patch('api_gateway.AbenaSDK') as mock_sdk:
            mock_sdk_instance = AsyncMock()
            mock_sdk.return_value = mock_sdk_instance
            
            gateway = APIGateway(enable_trusted_hosts=False)
            
            # Verify AbenaSDK was called with correct configuration
            mock_sdk.assert_called_once_with({
                'authServiceUrl': 'http://localhost:3001',
                'dataServiceUrl': 'http://localhost:8001',
                'privacyServiceUrl': 'http://localhost:8002',
                'blockchainServiceUrl': 'http://localhost:8003'
            })

if __name__ == "__main__":
    pytest.main([__file__]) 