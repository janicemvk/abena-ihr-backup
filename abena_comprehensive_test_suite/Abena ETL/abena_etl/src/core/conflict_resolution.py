"""
Conflict Resolution Module for Abena IHR System

This module handles conflicts between clinical context recommendations 
and predictive analytics results to ensure safe and effective treatment decisions.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of recommendation conflicts"""
    CLINICAL_VS_PREDICTION = "clinical_vs_prediction"
    SAFETY_CONCERN = "safety_concern"
    EFFICACY_CONCERN = "efficacy_concern"
    CONTRAINDICATION = "contraindication"


class ActionType(Enum):
    """Recommended actions for conflict resolution"""
    PROCEED = "proceed"
    HOLD = "hold"
    INVESTIGATE = "investigate"
    CLINICAL_REVIEW = "clinical_review"
    EMERGENCY_REVIEW = "emergency_review"


@dataclass
class ClinicalRecommendation:
    """Clinical recommendation data structure"""
    treatment_id: str
    treatment_name: str
    confidence_score: float
    evidence_level: str
    alternative_treatments: List[str]
    contraindications: List[str]
    clinical_notes: Optional[str] = None


@dataclass
class PredictionResult:
    """Predictive analytics result data structure"""
    success_probability: float
    risk_factors: List[str]
    confidence_interval: tuple
    model_version: str
    features_used: List[str]
    explanation: Optional[str] = None


@dataclass
class ConflictResolutionResult:
    """Result of conflict resolution analysis"""
    recommendation: str
    action: ActionType
    reason: str
    confidence_level: float
    alternatives: List[str]
    requires_review: bool
    reviewer_level: str
    additional_data_needed: List[str]
    conflict_type: ConflictType


class ConflictResolution:
    """
    Main conflict resolution class for handling recommendation conflicts
    between clinical context and predictive analytics.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize conflict resolution with configuration parameters.
        
        Args:
            config: Configuration dictionary with thresholds and settings
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for conflict resolution"""
        return {
            'prediction_threshold': 0.4,
            'clinical_confidence_threshold': 0.7,
            'safety_threshold': 0.8,
            'require_review_below': 0.3,
            'emergency_review_below': 0.2
        }
    
    def resolve_recommendation_conflict(
        self, 
        clinical_rec: ClinicalRecommendation, 
        prediction_result: PredictionResult
    ) -> ConflictResolutionResult:
        """
        Resolve conflicts between clinical recommendations and predictive analytics.
        
        Args:
            clinical_rec: Clinical recommendation from healthcare provider
            prediction_result: Result from predictive analytics model
            
        Returns:
            ConflictResolutionResult with recommended action and rationale
        """
        self.logger.info(f"Resolving conflict for treatment: {clinical_rec.treatment_name}")
        
        # Check for low success probability conflict
        if prediction_result.success_probability < self.config['prediction_threshold']:
            return self._handle_low_prediction_conflict(clinical_rec, prediction_result)
        
        # Check for safety concerns
        if self._has_safety_concerns(clinical_rec, prediction_result):
            return self._handle_safety_conflict(clinical_rec, prediction_result)
        
        # Check for clinical confidence vs prediction mismatch
        if self._has_confidence_mismatch(clinical_rec, prediction_result):
            return self._handle_confidence_mismatch(clinical_rec, prediction_result)
        
        # No significant conflict - proceed with clinical recommendation
        return ConflictResolutionResult(
            recommendation=f"PROCEED - {clinical_rec.treatment_name}",
            action=ActionType.PROCEED,
            reason="Clinical recommendation aligns with predictive analytics",
            confidence_level=min(clinical_rec.confidence_score, prediction_result.success_probability),
            alternatives=[],
            requires_review=False,
            reviewer_level="none",
            additional_data_needed=[],
            conflict_type=ConflictType.CLINICAL_VS_PREDICTION
        )
    
    def _handle_low_prediction_conflict(
        self, 
        clinical_rec: ClinicalRecommendation, 
        prediction_result: PredictionResult
    ) -> ConflictResolutionResult:
        """Handle conflicts where prediction shows low success probability"""
        
        if prediction_result.success_probability < self.config['emergency_review_below']:
            action = ActionType.EMERGENCY_REVIEW
            reviewer_level = "senior_clinician"
            recommendation = "EMERGENCY REVIEW - High risk treatment"
        elif prediction_result.success_probability < self.config['require_review_below']:
            action = ActionType.CLINICAL_REVIEW
            reviewer_level = "attending_physician"
            recommendation = "HOLD - Clinical review required"
        else:
            action = ActionType.INVESTIGATE
            reviewer_level = "clinical_pharmacist"
            recommendation = "INVESTIGATE - Consider alternatives"
        
        return ConflictResolutionResult(
            recommendation=recommendation,
            action=action,
            reason=f"Clinical recommendation conflicts with prediction model (success probability: {prediction_result.success_probability:.2f})",
            confidence_level=prediction_result.success_probability,
            alternatives=clinical_rec.alternative_treatments,
            requires_review=True,
            reviewer_level=reviewer_level,
            additional_data_needed=["recent_labs", "medication_history", "comorbidities"],
            conflict_type=ConflictType.CLINICAL_VS_PREDICTION
        )
    
    def _handle_safety_conflict(
        self, 
        clinical_rec: ClinicalRecommendation, 
        prediction_result: PredictionResult
    ) -> ConflictResolutionResult:
        """Handle safety-related conflicts"""
        
        return ConflictResolutionResult(
            recommendation="HOLD - Safety review required",
            action=ActionType.EMERGENCY_REVIEW,
            reason="Safety concerns identified in predictive analysis",
            confidence_level=0.0,
            alternatives=clinical_rec.alternative_treatments,
            requires_review=True,
            reviewer_level="senior_clinician",
            additional_data_needed=["allergy_history", "recent_adverse_events", "drug_interactions"],
            conflict_type=ConflictType.SAFETY_CONCERN
        )
    
    def _handle_confidence_mismatch(
        self, 
        clinical_rec: ClinicalRecommendation, 
        prediction_result: PredictionResult
    ) -> ConflictResolutionResult:
        """Handle mismatches in confidence levels"""
        
        return ConflictResolutionResult(
            recommendation="INVESTIGATE - Confidence mismatch detected",
            action=ActionType.INVESTIGATE,
            reason="Significant difference between clinical confidence and prediction confidence",
            confidence_level=(clinical_rec.confidence_score + prediction_result.success_probability) / 2,
            alternatives=clinical_rec.alternative_treatments[:2],  # Top 2 alternatives
            requires_review=True,
            reviewer_level="clinical_pharmacist",
            additional_data_needed=["evidence_review", "guidelines_check"],
            conflict_type=ConflictType.EFFICACY_CONCERN
        )
    
    def _has_safety_concerns(
        self, 
        clinical_rec: ClinicalRecommendation, 
        prediction_result: PredictionResult
    ) -> bool:
        """Check if there are safety concerns in the prediction"""
        safety_keywords = ["allergic", "toxic", "overdose", "interaction", "contraindicated"]
        
        # Check risk factors for safety issues
        risk_factors_text = " ".join(prediction_result.risk_factors).lower()
        return any(keyword in risk_factors_text for keyword in safety_keywords)
    
    def _has_confidence_mismatch(
        self, 
        clinical_rec: ClinicalRecommendation, 
        prediction_result: PredictionResult
    ) -> bool:
        """Check if there's a significant confidence mismatch"""
        confidence_diff = abs(clinical_rec.confidence_score - prediction_result.success_probability)
        return confidence_diff > 0.3  # 30% difference threshold
    
    def log_conflict_resolution(self, result: ConflictResolutionResult) -> None:
        """Log the conflict resolution result for audit purposes"""
        self.logger.info(f"Conflict Resolution: {result.recommendation}")
        self.logger.info(f"Action: {result.action.value}")
        self.logger.info(f"Reason: {result.reason}")
        self.logger.info(f"Requires Review: {result.requires_review}")
        
        if result.requires_review:
            self.logger.warning(f"Review required by: {result.reviewer_level}")


# Example usage and testing
if __name__ == "__main__":
    # Example clinical recommendation
    clinical_rec = ClinicalRecommendation(
        treatment_id="TRT-001",
        treatment_name="Antibiotic Therapy A",
        confidence_score=0.8,
        evidence_level="Level I",
        alternative_treatments=["Antibiotic Therapy B", "Combination Therapy C"],
        contraindications=["Penicillin allergy"]
    )
    
    # Example prediction result with low success probability
    prediction_result = PredictionResult(
        success_probability=0.3,
        risk_factors=["previous_treatment_failure", "resistant_strain"],
        confidence_interval=(0.2, 0.4),
        model_version="v2.1",
        features_used=["age", "comorbidities", "previous_treatments"]
    )
    
    # Resolve conflict
    resolver = ConflictResolution()
    result = resolver.resolve_recommendation_conflict(clinical_rec, prediction_result)
    
    print(f"Recommendation: {result.recommendation}")
    print(f"Action: {result.action.value}")
    print(f"Reason: {result.reason}")
    print(f"Alternatives: {result.alternatives}") 