"""
Tests for the API Gateway module
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
        with patch('api_gateway.create_engine'), \
             patch('api_gateway.redis.from_url'):
            gateway = APIGateway(
                db_url="postgresql://test:test@localhost/test",
                redis_url="redis://localhost:6379",
                enable_trusted_hosts=False  # Disable for testing
            )
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
        assert hasattr(api_gateway, 'redis_client')
        assert hasattr(api_gateway, 'rate_limiter')
    
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
    async def test_create_patient_endpoint(self, api_gateway, sample_patient):
        """Test create patient endpoint"""
        from fastapi.testclient import TestClient
        from fastapi.encoders import jsonable_encoder
        
        client = TestClient(api_gateway.app)
        
        # Test without authentication - should return 403
        response = client.post(
            "/api/v1/patients",
            json=jsonable_encoder(sample_patient)
        )
        
        print(f"Create patient response: {response.status_code} - {response.text}")
        # Should return 403 without proper authentication
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_create_observation_endpoint(self, api_gateway, sample_observation):
        """Test create observation endpoint"""
        from fastapi.testclient import TestClient
        from fastapi.encoders import jsonable_encoder
        
        client = TestClient(api_gateway.app)
        
        # Test without authentication - should return 403
        response = client.post(
            "/api/v1/observations",
            json=jsonable_encoder(sample_observation)
        )
        
        print(f"Create observation response: {response.status_code} - {response.text}")
        # Should return 403 without proper authentication
        assert response.status_code == 403
    
    def test_rate_limiter(self, api_gateway):
        """Test rate limiting functionality"""
        # Mock Redis pipeline
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = [0, 5]  # 5 current requests
        api_gateway.redis_client.pipeline.return_value = mock_pipeline
        
        # Test rate limiting
        is_allowed = api_gateway.rate_limiter.is_allowed("test_key", 10)
        assert is_allowed == True
        
        # Test rate limit exceeded
        mock_pipeline.execute.return_value = [0, 15]  # 15 current requests
        is_allowed = api_gateway.rate_limiter.is_allowed("test_key", 10)
        assert is_allowed == False
    
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

if __name__ == "__main__":
    pytest.main([__file__]) 