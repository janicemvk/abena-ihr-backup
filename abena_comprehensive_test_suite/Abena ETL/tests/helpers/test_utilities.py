"""
Test Utilities and Helper Functions

This module contains utility functions and helper classes
commonly used across the test suite.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock


class TestDataGenerator:
    """Helper class for generating test data"""
    
    @staticmethod
    def generate_patient_id(prefix: str = "TEST_PATIENT") -> str:
        """Generate unique patient ID for testing"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}"
    
    @staticmethod
    def generate_treatment_id(prefix: str = "TEST_TX") -> str:
        """Generate unique treatment ID for testing"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}"
    
    @staticmethod
    def create_mock_patient_data(patient_id: str = None) -> Dict[str, Any]:
        """Create mock patient data for testing"""
        if not patient_id:
            patient_id = TestDataGenerator.generate_patient_id()
        
        return {
            'patient_id': patient_id,
            'age': 45,
            'gender': 'female',
            'genomics_data': {
                'CYP2C9_activity': 0.8,
                'OPRM1_variant': 1,
                'COMT_activity': 1.1
            },
            'biomarkers': {
                'inflammatory_markers': 1.5,
                'endocannabinoid_levels': 0.7,
                'cortisol_baseline': 12.0
            },
            'medical_history': ['chronic_pain', 'anxiety'],
            'current_medications': ['gabapentin', 'sertraline'],
            'lifestyle_metrics': {
                'sleep_quality': 5.0,
                'stress_level': 6.0
            },
            'pain_scores': [7.0, 6.5, 7.5, 7.0],
            'functional_assessments': {
                'mobility_score': 65.0
            },
            'allergies': ['penicillin'],
            'lab_results': {
                'creatinine': 1.0,
                'liver_function': 0.9
            },
            'vital_signs': {
                'blood_pressure_systolic': 130,
                'blood_pressure_diastolic': 80,
                'heart_rate': 72
            },
            'comorbidities': ['anxiety_disorder']
        }
    
    @staticmethod
    def create_mock_treatment_data(treatment_id: str = None) -> Dict[str, Any]:
        """Create mock treatment data for testing"""
        if not treatment_id:
            treatment_id = TestDataGenerator.generate_treatment_id()
        
        return {
            'treatment_id': treatment_id,
            'treatment_type': 'combined',
            'medications': ['pregabalin', 'cbd_oil'],
            'dosages': {
                'pregabalin': '150mg_bid',
                'cbd_oil': '25mg_daily'
            },
            'duration_weeks': 12,
            'lifestyle_interventions': ['physical_therapy', 'mindfulness'],
            'contraindications': [],
            'side_effects': ['dizziness', 'dry_mouth'],
            'cost_estimate': 850.0,
            'evidence_level': 'Level I',
            'monitoring_requirements': ['pain_scores', 'side_effects']
        }


class MockAPIClient:
    """Mock API client for testing API interactions"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.requests_made = []
    
    def post(self, endpoint: str, data: Dict = None, json: Dict = None) -> Mock:
        """Mock POST request"""
        request_data = {
            'method': 'POST',
            'endpoint': endpoint,
            'data': data,
            'json': json,
            'timestamp': datetime.now()
        }
        self.requests_made.append(request_data)
        
        # Return appropriate mock response based on endpoint
        if 'patients' in endpoint:
            return Mock(
                status_code=201,
                json=lambda: {'patient_id': 'TEST_PATIENT_001', 'status': 'created'}
            )
        elif 'predictions' in endpoint:
            return Mock(
                status_code=200,
                json=lambda: {
                    'success_probability': 0.75,
                    'risk_score': 0.25,
                    'treatment_id': 'TEST_TX_001'
                }
            )
        else:
            return Mock(
                status_code=200,
                json=lambda: {'status': 'success'}
            )
    
    def get(self, endpoint: str, params: Dict = None) -> Mock:
        """Mock GET request"""
        request_data = {
            'method': 'GET',
            'endpoint': endpoint,
            'params': params,
            'timestamp': datetime.now()
        }
        self.requests_made.append(request_data)
        
        return Mock(
            status_code=200,
            json=lambda: {'data': [], 'status': 'success'}
        )
    
    def get_request_history(self) -> List[Dict]:
        """Get history of requests made"""
        return self.requests_made.copy()


class PerformanceTimer:
    """Helper class for measuring test performance"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.measurements = []
    
    def start(self):
        """Start timing"""
        self.start_time = time.perf_counter()
    
    def stop(self):
        """Stop timing"""
        self.end_time = time.perf_counter()
        if self.start_time:
            duration = (self.end_time - self.start_time) * 1000  # Convert to ms
            self.measurements.append(duration)
            return duration
        return None
    
    def get_average_time_ms(self) -> float:
        """Get average execution time in milliseconds"""
        if not self.measurements:
            return 0.0
        return sum(self.measurements) / len(self.measurements)
    
    def get_total_time_ms(self) -> float:
        """Get total execution time in milliseconds"""
        return sum(self.measurements)
    
    def reset(self):
        """Reset all measurements"""
        self.measurements = []
        self.start_time = None
        self.end_time = None


class TestAssertions:
    """Custom assertion helpers for healthcare data"""
    
    @staticmethod
    def assert_valid_patient_id(patient_id: str):
        """Assert patient ID is valid format"""
        assert isinstance(patient_id, str), "Patient ID must be string"
        assert len(patient_id) > 0, "Patient ID cannot be empty"
        assert not patient_id.isspace(), "Patient ID cannot be whitespace"
    
    @staticmethod
    def assert_valid_probability(value: float, field_name: str = "probability"):
        """Assert value is valid probability (0-1)"""
        assert isinstance(value, (int, float)), f"{field_name} must be numeric"
        assert 0 <= value <= 1, f"{field_name} must be between 0 and 1, got {value}"
    
    @staticmethod
    def assert_valid_pain_score(score: float):
        """Assert pain score is valid (0-10 scale)"""
        assert isinstance(score, (int, float)), "Pain score must be numeric"
        assert 0 <= score <= 10, f"Pain score must be between 0 and 10, got {score}"
    
    @staticmethod
    def assert_valid_age(age: int):
        """Assert age is valid"""
        assert isinstance(age, int), "Age must be integer"
        assert 0 <= age <= 150, f"Age must be between 0 and 150, got {age}"
    
    @staticmethod
    def assert_valid_timestamp(timestamp):
        """Assert timestamp is valid datetime"""
        assert isinstance(timestamp, datetime), "Timestamp must be datetime object"
        
        # Check timestamp is not too far in the future or past
        now = datetime.now()
        one_year_ago = now - timedelta(days=365)
        one_day_future = now + timedelta(days=1)
        
        assert one_year_ago <= timestamp <= one_day_future, \
            f"Timestamp {timestamp} is outside reasonable range"
    
    @staticmethod
    def assert_medication_list(medications: List[str]):
        """Assert medication list is valid"""
        assert isinstance(medications, list), "Medications must be a list"
        for med in medications:
            assert isinstance(med, str), f"Medication {med} must be string"
            assert len(med.strip()) > 0, f"Medication name cannot be empty"
    
    @staticmethod
    def assert_genomics_data(genomics_data: Dict[str, float]):
        """Assert genomics data is valid"""
        assert isinstance(genomics_data, dict), "Genomics data must be dictionary"
        
        for gene, value in genomics_data.items():
            assert isinstance(gene, str), f"Gene name {gene} must be string"
            assert isinstance(value, (int, float)), f"Gene value for {gene} must be numeric"
            assert value >= 0, f"Gene value for {gene} must be non-negative"


class MockDatabaseConnection:
    """Mock database connection for testing"""
    
    def __init__(self):
        self.is_connected = False
        self.transactions = []
        self.data_store = {}
    
    def connect(self):
        """Mock database connection"""
        self.is_connected = True
        return True
    
    def disconnect(self):
        """Mock database disconnection"""
        self.is_connected = False
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Mock query execution"""
        transaction = {
            'query': query,
            'params': params,
            'timestamp': datetime.now(),
            'success': True
        }
        self.transactions.append(transaction)
        
        # Return mock data based on query type
        if 'SELECT' in query.upper():
            return [{'id': 1, 'data': 'mock_result'}]
        elif 'INSERT' in query.upper():
            return [{'affected_rows': 1}]
        elif 'UPDATE' in query.upper():
            return [{'affected_rows': 1}]
        elif 'DELETE' in query.upper():
            return [{'affected_rows': 1}]
        else:
            return []
    
    def get_transaction_history(self) -> List[Dict]:
        """Get history of database transactions"""
        return self.transactions.copy()


def load_test_fixtures(fixture_name: str) -> Dict:
    """Load test fixtures from JSON files"""
    import os
    
    fixture_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 'fixtures', 
        f'{fixture_name}.json'
    )
    
    try:
        with open(fixture_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def compare_patient_data(patient1: Dict, patient2: Dict, ignore_fields: List[str] = None) -> bool:
    """Compare two patient data dictionaries"""
    if ignore_fields is None:
        ignore_fields = ['timestamp', 'created_at', 'updated_at']
    
    # Remove ignored fields
    p1_filtered = {k: v for k, v in patient1.items() if k not in ignore_fields}
    p2_filtered = {k: v for k, v in patient2.items() if k not in ignore_fields}
    
    return p1_filtered == p2_filtered


def validate_api_response_structure(response_data: Dict, required_fields: List[str]) -> bool:
    """Validate API response has required structure"""
    for field in required_fields:
        if field not in response_data:
            return False
    return True


def create_test_context(test_name: str) -> Dict[str, Any]:
    """Create test context with common testing utilities"""
    return {
        'test_name': test_name,
        'start_time': datetime.now(),
        'data_generator': TestDataGenerator(),
        'api_client': MockAPIClient(),
        'performance_timer': PerformanceTimer(),
        'assertions': TestAssertions(),
        'db_connection': MockDatabaseConnection()
    } 