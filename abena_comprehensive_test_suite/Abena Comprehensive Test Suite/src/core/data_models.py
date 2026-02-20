# Mock data models for testing
from dataclasses import dataclass
from typing import Dict, List, Any
from datetime import datetime

@dataclass
class PatientProfile:
    patient_id: str
    age: int
    gender: str
    genomics_data: Dict[str, float]
    biomarkers: Dict[str, float]
    medical_history: List[str]
    current_medications: List[str]
    lifestyle_metrics: Dict[str, float]
    pain_scores: List[float]
    functional_assessments: Dict[str, float]

@dataclass
class TreatmentPlan:
    treatment_id: str
    treatment_type: str
    medications: List[str]
    dosages: Dict[str, str]
    duration_weeks: int
    lifestyle_interventions: List[str]

@dataclass
class PredictionResult:
    patient_id: str
    treatment_id: str
    success_probability: float
    risk_score: float
    key_factors: List[str]
    warnings: List[str]
    timestamp: datetime 