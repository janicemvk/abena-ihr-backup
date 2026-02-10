"""
Core module for Abena IHR System

This module contains core functionality including:
- Conflict resolution between clinical recommendations and predictive analytics
- Model version management with staged deployments
- Integrated architecture solution combining all components
- System reconciliation for regular conflict detection and resolution
- Core data models and structures
- Decision support algorithms
- System utilities
"""

from .conflict_resolution import ConflictResolution, ClinicalRecommendation, PredictionResult
from .model_version_manager import (
    ModelVersionManager, 
    ValidationMetrics, 
    ModelVersion, 
    DeploymentPlan,
    DeploymentStage,
    ModelStatus
)
from .integrated_system import (
    AbenaIntegratedSystem,
    ClinicalContextModule,
    PredictiveAnalyticsEngine,
    DynamicLearningLoop,
    ConflictResolutionEngine,
    PatientData,
    TreatmentOption,
    ClinicalContext,
    PredictiveResult,
    TreatmentOutcome,
    FinalRecommendation
)
from .system_reconciliation import (
    SystemReconciliation,
    ReconciliationConflict,
    LearningPredictionGap,
    ReconciliationReport,
    DiscrepancyType,
    ConflictSeverity
)
from .data_models import (
    PatientProfile,
    TreatmentPlan,
    PredictionResult as PredictionResultModel,
    AdverseEventPrediction,
    ClinicalNote,
    Alert,
    ModelMetrics,
    EMRData,
    TreatmentType,
    RiskLevel,
    validate_patient_data,
    validate_treatment_plan,
    create_sample_patient,
    create_sample_treatment
)

__all__ = [
    # Conflict Resolution
    'ConflictResolution', 
    'ClinicalRecommendation', 
    'PredictionResult',
    
    # Model Version Management
    'ModelVersionManager',
    'ValidationMetrics',
    'ModelVersion',
    'DeploymentPlan',
    'DeploymentStage',
    'ModelStatus',
    
    # Integrated System
    'AbenaIntegratedSystem',
    'ClinicalContextModule',
    'PredictiveAnalyticsEngine',
    'DynamicLearningLoop',
    'ConflictResolutionEngine',
    
    # System Reconciliation
    'SystemReconciliation',
    'ReconciliationConflict',
    'LearningPredictionGap',
    'ReconciliationReport',
    'DiscrepancyType',
    'ConflictSeverity',
    
    # Data Models
    'PatientData',
    'TreatmentOption',
    'ClinicalContext',
    'PredictiveResult',
    'TreatmentOutcome',
    'FinalRecommendation',
    
    # Enhanced Data Models
    'PatientProfile',
    'TreatmentPlan',
    'PredictionResultModel',
    'AdverseEventPrediction',
    'ClinicalNote',
    'Alert',
    'ModelMetrics',
    'EMRData',
    'TreatmentType',
    'RiskLevel',
    
    # Utilities
    'validate_patient_data',
    'validate_treatment_plan',
    'create_sample_patient',
    'create_sample_treatment'
] 