import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import numpy as np

# Import your application components
from src.api.main import app
from src.core.data_models import PatientProfile, TreatmentPlan

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def app_client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def sample_patient():
    """Load sample patient from fixtures"""
    try:
        with open('tests/fixtures/sample_patients.json', 'r') as f:
            patient_data = json.load(f)[0]  # First patient
        return PatientProfile(**patient_data)
    except (FileNotFoundError, KeyError):
        # Fallback to inline data if fixture file not found
        return PatientProfile(
            patient_id="TEST_PATIENT_001",
            age=45,
            gender="female",
            genomics_data={
                'CYP2C9_activity': 0.7,
                'OPRM1_variant': 1,
                'COMT_activity': 1.2,
                'CB1_receptor_density': 0.9
            },
            biomarkers={
                'inflammatory_markers': 1.8,
                'endocannabinoid_levels': 0.6,
                'cortisol_baseline': 15.2,
                'gaba_activity': 0.8,
                'liver_enzymes': 1.2,
                'kidney_function': 0.9
            },
            medical_history=['chronic_pain', 'anxiety', 'fibromyalgia'],
            current_medications=['gabapentin', 'sertraline'],
            lifestyle_metrics={
                'sleep_quality': 4.0,
                'stress_level': 7.0
            },
            pain_scores=[8.0, 7.5, 8.2, 7.8],
            functional_assessments={'mobility_score': 35.0}
        )

@pytest.fixture
def sample_treatment():
    """Load sample treatment from fixtures"""
    try:
        with open('tests/fixtures/sample_treatments.json', 'r') as f:
            treatment_data = json.load(f)[0]  # First treatment
        return TreatmentPlan(**treatment_data)
    except (FileNotFoundError, KeyError):
        # Fallback to inline data if fixture file not found
        return TreatmentPlan(
            treatment_id="TEST_TX_001",
            treatment_type="combined",
            medications=['pregabalin', 'cbd_oil'],
            dosages={'pregabalin': '150mg_bid', 'cbd_oil': '25mg_daily'},
            duration_weeks=12,
            lifestyle_interventions=['mindfulness', 'physical_therapy', 'sleep_hygiene']
        )

@pytest.fixture
def mock_emr_responses():
    """Load mock EMR responses"""
    try:
        with open('tests/fixtures/mock_emr_responses.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to inline data if fixture file not found
        return {
            "patient_response": {
                "resourceType": "Patient",
                "id": "test_patient_123",
                "active": True,
                "name": [{"use": "official", "family": "Test", "given": ["Patient", "Example"]}],
                "gender": "female",
                "birthDate": "1978-05-15"
            },
            "observations_response": {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 3,
                "entry": [{
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs_001",
                        "status": "final",
                        "code": {"coding": [{"system": "http://loinc.org", "code": "72133-2", "display": "Pain severity"}]},
                        "valueQuantity": {"value": 7, "unit": "score", "system": "http://unitsofmeasure.org"}
                    }
                }]
            }
        }

@pytest.fixture
def mock_training_data():
    """Mock training data for ML models"""
    from src.core.data_models import PatientProfile, TreatmentPlan
    
    training_data = []
    for i in range(100):
        patient = PatientProfile(
            patient_id=f"TRAIN_PATIENT_{i:03d}",
            age=np.random.randint(18, 80),
            gender=np.random.choice(['male', 'female']),
            genomics_data={
                'CYP2C9_activity': np.random.normal(1.0, 0.3),
                'OPRM1_variant': np.random.randint(0, 2),
                'COMT_activity': np.random.normal(1.0, 0.2),
                'CB1_receptor_density': np.random.normal(1.0, 0.25)
            },
            biomarkers={
                'inflammatory_markers': np.random.normal(1.0, 0.5),
                'endocannabinoid_levels': np.random.normal(0.8, 0.2),
                'cortisol_baseline': np.random.normal(12.0, 3.0),
                'gaba_activity': np.random.normal(1.0, 0.3)
            },
            medical_history=np.random.choice(['chronic_pain', 'anxiety', 'depression'], 
                                           size=np.random.randint(1, 4)).tolist(),
            current_medications=np.random.choice(['gabapentin', 'sertraline', 'ibuprofen'], 
                                               size=np.random.randint(0, 3)).tolist(),
            lifestyle_metrics={
                'sleep_quality': np.random.uniform(1, 10),
                'stress_level': np.random.uniform(1, 10)
            },
            pain_scores=[np.random.uniform(1, 10) for _ in range(4)],
            functional_assessments={'mobility_score': np.random.uniform(10, 90)}
        )
        
        treatment = TreatmentPlan(
            treatment_id=f"TRAIN_TX_{i:03d}",
            treatment_type=np.random.choice(['pharmacological', 'behavioral', 'combined']),
            medications=np.random.choice(['pregabalin', 'gabapentin', 'cbd_oil'], 
                                       size=np.random.randint(1, 3)).tolist(),
            dosages={},
            duration_weeks=np.random.randint(4, 24),
            lifestyle_interventions=np.random.choice(['mindfulness', 'exercise', 'therapy'], 
                                                   size=np.random.randint(0, 3)).tolist()
        )
        
        # Simulate outcome (0 = poor, 1 = excellent)
        outcome = np.random.beta(2, 2)  # Beta distribution for realistic outcomes
        
        training_data.append((patient, treatment, outcome))
    
    return training_data 