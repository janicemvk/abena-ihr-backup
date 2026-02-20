# Abena IHR - ML Data Models
# Data structures for the machine learning feedback pipeline

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field

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
class ModelPerformanceMetrics:
    """Model performance tracking"""
    model_id: str
    model_version: str
    evaluation_date: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    mse: float
    mae: float
    false_positive_rate: float
    false_negative_rate: float
    calibration_score: float
    feature_importance: Dict[str, float]
    prediction_confidence: float
    clinical_utility_score: float
    sample_size: int
    population_coverage: Dict[str, float]  # demographic coverage

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