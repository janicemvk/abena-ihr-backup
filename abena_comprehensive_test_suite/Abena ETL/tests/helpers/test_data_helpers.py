"""
Test Data Helpers

Common utilities for generating test data and mock objects
"""

from datetime import datetime
from typing import Dict, Any


def generate_test_patient_id(prefix: str = "TEST_PT") -> str:
    """Generate unique test patient ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}"


def create_minimal_patient_data(patient_id: str = None) -> Dict[str, Any]:
    """Create minimal patient data for testing"""
    if not patient_id:
        patient_id = generate_test_patient_id()
    
    return {
        'patient_id': patient_id,
        'age': 45,
        'gender': 'female',
        'genomics_data': {},
        'biomarkers': {},
        'medical_history': ['chronic_pain'],
        'current_medications': [],
        'lifestyle_metrics': {},
        'pain_scores': [7.0],
        'functional_assessments': {}
    }


def create_minimal_treatment_data(treatment_id: str = None) -> Dict[str, Any]:
    """Create minimal treatment data for testing"""
    if not treatment_id:
        treatment_id = f"TEST_TX_{datetime.now().strftime('%H%M%S')}"
    
    return {
        'treatment_id': treatment_id,
        'treatment_type': 'pharmacological',
        'medications': ['test_medication'],
        'dosages': {'test_medication': 'test_dose'},
        'duration_weeks': 8,
        'lifestyle_interventions': []
    } 