"""
Shared Test Fixtures and Configuration for Abena IHR System

This module provides common fixtures, mocks, and utilities used across
all test modules in the Abena IHR test suite.
"""

import pytest
import asyncio
import os
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any
from fastapi.testclient import TestClient

# Import core system components
from src.core.data_models import (
    PatientProfile, 
    TreatmentPlan, 
    PredictionResult, 
    TreatmentOutcome,
    create_sample_patient,
    create_sample_treatment
)


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_patient():
    """Sample patient data for testing"""
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
    """Sample treatment plan for testing"""
    return TreatmentPlan(
        treatment_id="TEST_TX_001",
        treatment_type="combined",
        medications=['pregabalin', 'cbd_oil'],
        dosages={'pregabalin': '150mg_bid', 'cbd_oil': '25mg_daily'},
        duration_weeks=12,
        lifestyle_interventions=['mindfulness', 'physical_therapy', 'sleep_hygiene']
    )


@pytest.fixture
def sample_outcome():
    """Sample treatment outcome for testing"""
    return TreatmentOutcome(
        patient_id="TEST_PATIENT_001",
        treatment_id="TEST_TX_001",
        outcome_success=True,
        recovery_time=21,
        side_effects_observed=[],
        patient_satisfaction=8.5,
        readmission_required=False,
        outcome_date=datetime.now(),
        pain_improvement=3.2,
        functional_improvement=25.0,
        quality_of_life_score=7.8
    )


@pytest.fixture
def realistic_patient_cohort():
    """Create realistic patient cohort for testing"""
    patients = []
    
    for i in range(10):  # Smaller cohort for faster tests
        age = int(np.random.normal(55, 15))
        age = max(18, min(90, age))
        
        patient = PatientProfile(
            patient_id=f"COHORT_PATIENT_{i:03d}",
            age=age,
            gender=np.random.choice(['male', 'female']),
            genomics_data={
                'CYP2C9_activity': max(0.1, np.random.normal(1.0, 0.3)),
                'OPRM1_variant': np.random.randint(0, 2),
                'COMT_activity': max(0.1, np.random.normal(1.0, 0.2)),
                'CB1_receptor_density': max(0.1, np.random.normal(1.0, 0.25))
            },
            biomarkers={
                'inflammatory_markers': max(0.1, np.random.normal(1.0, 0.5)),
                'endocannabinoid_levels': max(0.1, np.random.normal(0.8, 0.2)),
                'cortisol_baseline': max(5.0, np.random.normal(12.0, 3.0)),
                'gaba_activity': max(0.1, np.random.normal(1.0, 0.3))
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
        patients.append(patient)
    
    return patients


@pytest.fixture
def mock_training_data():
    """Mock training data for ML models"""
    training_data = []
    for i in range(50):  # Smaller dataset for faster tests
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


# ============================================================================
# API TEST FIXTURES
# ============================================================================

@pytest.fixture
def app_client():
    """FastAPI test client"""
    from src.api.main import app
    return TestClient(app)


@pytest.fixture
def mock_emr_config():
    """Mock EMR configuration for testing"""
    return {
        'type': 'epic',
        'base_url': 'https://test-fhir.epic.com',
        'client_id': 'test_client',
        'client_secret': 'test_secret',
        'access_token': 'test_token'
    }


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_ml_models():
    """Mock ML models to avoid training overhead in tests"""
    with patch('joblib.load') as mock_load:
        mock_model = Mock()
        mock_model.predict.return_value = [0.75]
        mock_model.predict_proba.return_value = [[0.25, 0.75]]
        mock_model.feature_importances_ = np.random.random(10)
        
        mock_scaler = Mock()
        mock_scaler.transform.return_value = np.random.random((1, 10))
        
        mock_load.return_value = {
            'treatment_models': {'random_forest': mock_model},
            'treatment_scalers': {'response': mock_scaler},
            'adverse_event_models': {'severe_side_effects': mock_model},
            'adverse_event_thresholds': {'severe_side_effects': 0.5}
        }
        yield mock_load


@pytest.fixture
def mock_emr_responses():
    """Mock EMR API responses"""
    with patch('requests.Session.get') as mock_get, \
         patch('requests.Session.post') as mock_post:
        
        # Mock patient data response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'resourceType': 'Patient',
            'id': 'test_patient_123',
            'name': [{'family': 'Test', 'given': ['Patient']}],
            'birthDate': '1978-05-15',
            'gender': 'female'
        }
        
        # Mock note creation response
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            'resourceType': 'DocumentReference',
            'id': 'new_note_123'
        }
        
        yield {'get': mock_get, 'post': mock_post}


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    mock_session = Mock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    return mock_session


# ============================================================================
# INTEGRATION TEST FIXTURES
# ============================================================================

@pytest.fixture
def integrated_system(mock_training_data):
    """Create integrated system for testing"""
    from src.core.integrated_system import AbenaIntegratedSystem
    
    system = AbenaIntegratedSystem()
    
    # Mock the initialization to avoid heavy ML operations
    with patch.object(system.predictive_engine, 'initialize_models') as mock_init:
        mock_init.return_value = True
        
        # Mock training data for adverse events
        adverse_event_data = []
        for patient, treatment, outcome in mock_training_data[:25]:
            adverse_outcomes = {
                'severe_side_effects': np.random.randint(0, 2),
                'treatment_discontinuation': np.random.randint(0, 2),
                'hospitalization': np.random.randint(0, 2)
            }
            adverse_event_data.append((patient, treatment, adverse_outcomes))
        
        # Initialize with mock data
        system.predictive_engine.initialize_models(mock_training_data, adverse_event_data)
    
    return system


# ============================================================================
# PERFORMANCE TEST FIXTURES
# ============================================================================

@pytest.fixture
def performance_metrics():
    """Initialize performance tracking"""
    return {
        'start_time': None,
        'end_time': None,
        'latencies': [],
        'throughput': 0,
        'memory_usage': []
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def temp_directory(tmp_path):
    """Create temporary directory for file operations"""
    return tmp_path


@pytest.fixture
def test_logger():
    """Create test logger"""
    import logging
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def random_seed():
    """Set random seed for reproducible tests"""
    np.random.seed(42)
    import random
    random.seed(42)
    yield
    # Reset random state after test
    np.random.seed(None)


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_prediction_result(result):
    """Validate prediction result structure"""
    required_fields = ['patient_id', 'treatment_id', 'success_probability', 
                      'risk_score', 'key_factors', 'warnings', 'timestamp']
    
    for field in required_fields:
        assert hasattr(result, field), f"Missing required field: {field}"
    
    assert 0 <= result.success_probability <= 1, "Success probability out of range"
    assert 0 <= result.risk_score <= 1, "Risk score out of range"
    assert isinstance(result.key_factors, list), "Key factors should be a list"
    assert isinstance(result.warnings, list), "Warnings should be a list"


def validate_treatment_plan(treatment):
    """Validate treatment plan structure"""
    assert hasattr(treatment, 'treatment_id')
    assert hasattr(treatment, 'treatment_type')
    assert hasattr(treatment, 'medications')
    assert hasattr(treatment, 'duration_weeks')
    assert treatment.duration_weeks > 0


def validate_patient_profile(patient):
    """Validate patient profile structure"""
    assert hasattr(patient, 'patient_id')
    assert hasattr(patient, 'age')
    assert hasattr(patient, 'gender')
    assert 0 <= patient.age <= 120
    assert patient.gender in ['male', 'female', 'other']


# ============================================================================
# TEST CATEGORIES
# ============================================================================

# Mark functions for easy test categorization
pytest_plugins = []

# Custom markers for test organization
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "clinical: Clinical validation tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test"""
    yield
    # Cleanup code would go here if needed
    pass 