# Data models for the ML Feedback Pipeline
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class PatientProfile:
    """Patient profile data structure"""
    patient_id: str
    age: int
    gender: str
    genomics_data: Dict[str, Any]
    biomarkers: Dict[str, float]
    medical_history: List[str]
    current_medications: List[str]
    lifestyle_metrics: Dict[str, Any]
    pain_scores: List[float]
    functional_assessments: Dict[str, float]
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TreatmentPlan:
    """Treatment plan data structure"""
    treatment_id: str
    treatment_type: str
    medications: List[str]
    dosages: Dict[str, float]
    duration_weeks: int
    lifestyle_interventions: List[str]
    additional_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PredictionResult:
    """Prediction result data structure"""
    patient_id: str
    treatment_id: str
    success_probability: float
    confidence_score: float
    warnings: List[str]
    recommendations: List[str]
    timestamp: datetime
    model_version: str
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OutcomeData:
    """Structure for treatment outcome data"""
    patient_id: str
    treatment_id: str
    prediction_id: str
    actual_outcome: float  # 0-1 scale for success
    outcome_date: datetime
    time_to_outcome: int  # days
    adverse_events: List[str]
    side_effects: List[str]
    patient_satisfaction: float  # 1-10 scale
    provider_assessment: str
    pain_reduction: float  # baseline - current
    functional_improvement: float
    medication_adherence: float  # 0-1 scale
    quality_of_life_change: float
    healthcare_utilization: Dict[str, int]  # visits, ER, hospitalizations
    cost_effectiveness: float
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LearningInsight:
    """Insights derived from outcome analysis"""
    insight_id: str
    insight_type: str  # 'pattern', 'improvement', 'concern', 'opportunity'
    description: str
    affected_population: str
    confidence_level: float
    clinical_significance: str  # 'high', 'moderate', 'low'
    actionable_recommendations: List[str]
    supporting_evidence: Dict[str, Any]
    validation_status: str  # 'pending', 'validated', 'rejected'
    discovered_date: datetime 