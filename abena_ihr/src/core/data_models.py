"""
Core Data Models

This module contains shared data models and structures used across
the Abena IHR Clinical Outcomes Management System.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
import uuid


class PatientStatus(Enum):
    """Enumeration of patient statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCHARGED = "discharged"
    TRANSFERRED = "transferred"
    DECEASED = "deceased"


class PredictionConfidence(Enum):
    """Enumeration of prediction confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class WorkflowStatus(Enum):
    """Enumeration of workflow statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Patient:
    """Core patient data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    first_name: str = ""
    last_name: str = ""
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    status: PatientStatus = PatientStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class Prediction:
    """Core prediction data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    outcome_name: str = ""
    predicted_value: Any = None
    confidence: PredictionConfidence = PredictionConfidence.MEDIUM
    confidence_score: float = 0.0
    model_version: str = ""
    features_used: List[str] = field(default_factory=list)
    prediction_date: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.prediction_date is None:
            self.prediction_date = datetime.now()


@dataclass
class WorkflowTask:
    """Core workflow task data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str = ""
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    patient_id: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: int = 1
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class BiomarkerData:
    """Core biomarker data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    biomarker_name: str = ""
    value: Any = None
    unit: Optional[str] = None
    measurement_date: datetime = field(default_factory=datetime.now)
    source: str = ""
    is_realtime: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.measurement_date is None:
            self.measurement_date = datetime.now()


@dataclass
class SystemEvent:
    """Core system event data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    patient_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "info"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# Utility functions for data models
def create_patient_id() -> str:
    """Generate a unique patient ID."""
    return f"PAT_{uuid.uuid4().hex[:8].upper()}"


def validate_patient_data(patient: Patient) -> bool:
    """Validate patient data."""
    if not patient.first_name or not patient.last_name:
        return False
    if patient.date_of_birth and patient.date_of_birth > date.today():
        return False
    return True


def calculate_prediction_confidence(score: float) -> PredictionConfidence:
    """Calculate prediction confidence level based on score."""
    if score >= 0.9:
        return PredictionConfidence.VERY_HIGH
    elif score >= 0.7:
        return PredictionConfidence.HIGH
    elif score >= 0.5:
        return PredictionConfidence.MEDIUM
    else:
        return PredictionConfidence.LOW 