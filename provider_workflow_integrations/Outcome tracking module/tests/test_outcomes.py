import pytest
from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.outcome import PatientOutcome
from app.schemas.outcome import OutcomeCreate


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autoscope="function")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_patient_id():
    """Sample patient ID for testing"""
    return str(uuid4())


@pytest.fixture
def sample_outcome_data(sample_patient_id):
    """Sample outcome data for testing"""
    return {
        "patient_id": sample_patient_id,
        "measurement_date": "2024-01-15",
        "outcome_type": "pain_score",
        "outcome_value": 7.5,
        "measurement_method": "visual_analog_scale"
    }


class TestOutcomeAPI:
    """Test cases for outcome API endpoints"""
    
    def test_create_outcome(self, setup_database, sample_outcome_data):
        """Test creating a new outcome"""
        response = client.post("/api/v1/outcomes/", json=sample_outcome_data)
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == sample_outcome_data["patient_id"]
        assert data["outcome_type"] == sample_outcome_data["outcome_type"]
        assert data["outcome_value"] == sample_outcome_data["outcome_value"]
        assert "outcome_id" in data
        assert "created_at" in data
    
    def test_create_outcome_invalid_type(self, setup_database, sample_patient_id):
        """Test creating outcome with invalid outcome type"""
        invalid_data = {
            "patient_id": sample_patient_id,
            "measurement_date": "2024-01-15",
            "outcome_type": "invalid_type",
            "outcome_value": 7.5,
            "measurement_method": "visual_analog_scale"
        }
        response = client.post("/api/v1/outcomes/", json=invalid_data)
        assert response.status_code == 422
    
    def test_create_outcome_invalid_value(self, setup_database, sample_patient_id):
        """Test creating outcome with invalid value"""
        invalid_data = {
            "patient_id": sample_patient_id,
            "measurement_date": "2024-01-15",
            "outcome_type": "pain_score",
            "outcome_value": 150,  # Invalid value > 100
            "measurement_method": "visual_analog_scale"
        }
        response = client.post("/api/v1/outcomes/", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_outcome(self, setup_database, sample_outcome_data):
        """Test getting a specific outcome"""
        # Create outcome first
        create_response = client.post("/api/v1/outcomes/", json=sample_outcome_data)
        outcome_id = create_response.json()["outcome_id"]
        
        # Get the outcome
        response = client.get(f"/api/v1/outcomes/{outcome_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["outcome_id"] == outcome_id
        assert data["patient_id"] == sample_outcome_data["patient_id"]
    
    def test_get_outcome_not_found(self, setup_database):
        """Test getting non-existent outcome"""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/outcomes/{fake_id}")
        assert response.status_code == 404
    
    def test_get_patient_outcomes(self, setup_database, sample_patient_id):
        """Test getting all outcomes for a patient"""
        # Create multiple outcomes
        outcome_data_1 = {
            "patient_id": sample_patient_id,
            "measurement_date": "2024-01-15",
            "outcome_type": "pain_score",
            "outcome_value": 7.5,
            "measurement_method": "visual_analog_scale"
        }
        outcome_data_2 = {
            "patient_id": sample_patient_id,
            "measurement_date": "2024-01-16",
            "outcome_type": "functional_assessment",
            "outcome_value": 85.0,
            "measurement_method": "standardized_test"
        }
        
        client.post("/api/v1/outcomes/", json=outcome_data_1)
        client.post("/api/v1/outcomes/", json=outcome_data_2)
        
        # Get patient outcomes
        response = client.get(f"/api/v1/outcomes/patient/{sample_patient_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(outcome["patient_id"] == sample_patient_id for outcome in data)
    
    def test_get_patient_outcomes_filtered(self, setup_database, sample_patient_id):
        """Test getting patient outcomes filtered by type"""
        # Create outcomes with different types
        outcome_data_1 = {
            "patient_id": sample_patient_id,
            "measurement_date": "2024-01-15",
            "outcome_type": "pain_score",
            "outcome_value": 7.5,
            "measurement_method": "visual_analog_scale"
        }
        outcome_data_2 = {
            "patient_id": sample_patient_id,
            "measurement_date": "2024-01-16",
            "outcome_type": "functional_assessment",
            "outcome_value": 85.0,
            "measurement_method": "standardized_test"
        }
        
        client.post("/api/v1/outcomes/", json=outcome_data_1)
        client.post("/api/v1/outcomes/", json=outcome_data_2)
        
        # Get filtered outcomes
        response = client.get(f"/api/v1/outcomes/patient/{sample_patient_id}?outcome_type=pain_score")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["outcome_type"] == "pain_score"
    
    def test_update_outcome(self, setup_database, sample_outcome_data):
        """Test updating an outcome"""
        # Create outcome first
        create_response = client.post("/api/v1/outcomes/", json=sample_outcome_data)
        outcome_id = create_response.json()["outcome_id"]
        
        # Update the outcome
        update_data = {
            "outcome_value": 6.0,
            "measurement_method": "numeric_rating_scale"
        }
        response = client.put(f"/api/v1/outcomes/{outcome_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["outcome_value"] == 6.0
        assert data["measurement_method"] == "numeric_rating_scale"
    
    def test_delete_outcome(self, setup_database, sample_outcome_data):
        """Test deleting an outcome"""
        # Create outcome first
        create_response = client.post("/api/v1/outcomes/", json=sample_outcome_data)
        outcome_id = create_response.json()["outcome_id"]
        
        # Delete the outcome
        response = client.delete(f"/api/v1/outcomes/{outcome_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Outcome deleted successfully"
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/outcomes/{outcome_id}")
        assert get_response.status_code == 404
    
    def test_get_outcome_statistics(self, setup_database, sample_patient_id):
        """Test getting outcome statistics"""
        # Create multiple outcomes for statistics
        outcomes = [
            {"outcome_value": 7.0, "measurement_date": "2024-01-15"},
            {"outcome_value": 6.5, "measurement_date": "2024-01-16"},
            {"outcome_value": 6.0, "measurement_date": "2024-01-17"},
            {"outcome_value": 5.5, "measurement_date": "2024-01-18"},
        ]
        
        for outcome in outcomes:
            outcome_data = {
                "patient_id": sample_patient_id,
                "measurement_date": outcome["measurement_date"],
                "outcome_type": "pain_score",
                "outcome_value": outcome["outcome_value"],
                "measurement_method": "visual_analog_scale"
            }
            client.post("/api/v1/outcomes/", json=outcome_data)
        
        # Get statistics
        response = client.get(f"/api/v1/outcomes/patient/{sample_patient_id}/statistics/pain_score")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 4
        assert data["average"] == 6.25
        assert data["min"] == 5.5
        assert data["max"] == 7.0
        assert data["latest_value"] == 5.5
        assert "trend" in data 