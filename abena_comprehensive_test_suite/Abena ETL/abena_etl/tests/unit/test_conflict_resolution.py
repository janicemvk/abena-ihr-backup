"""
Unit Tests for Conflict Resolution Engine

This module contains comprehensive unit tests for the conflict resolution
system including escalation logic, safety checks, and decision validation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

# Import core components
from src.core.conflict_resolution import (
    ConflictResolution, 
    ClinicalRecommendation, 
    PredictionResult
)
from src.core.data_models import PatientProfile, TreatmentPlan


# ============================================================================
# UNIT TESTS FOR CONFLICT RESOLUTION
# ============================================================================

@pytest.mark.unit
class TestConflictResolution:
    """Unit tests for ConflictResolution class"""
    
    @pytest.fixture
    def conflict_resolver(self):
        """Create conflict resolver instance"""
        return ConflictResolution()
    
    @pytest.fixture
    def high_confidence_clinical_rec(self):
        """High confidence clinical recommendation"""
        return ClinicalRecommendation(
            treatment_id="CLINICAL_TX_001",
            recommendation="Increase gabapentin to 300mg TID",
            confidence_level=0.85,
            evidence_level="Level I",
            contraindications=[],
            warnings=[]
        )
    
    @pytest.fixture
    def low_confidence_clinical_rec(self):
        """Low confidence clinical recommendation"""
        return ClinicalRecommendation(
            treatment_id="CLINICAL_TX_002", 
            recommendation="Consider CBD oil therapy",
            confidence_level=0.35,
            evidence_level="Level III",
            contraindications=[],
            warnings=["Limited clinical evidence"]
        )
    
    @pytest.fixture
    def high_confidence_prediction(self):
        """High confidence prediction result"""
        return PredictionResult(
            treatment_id="PRED_TX_001",
            predicted_outcome="SUCCESS",
            confidence_level=0.82,
            success_probability=0.78,
            risk_factors=[],
            warnings=[]
        )
    
    @pytest.fixture
    def low_confidence_prediction(self):
        """Low confidence prediction result"""
        return PredictionResult(
            treatment_id="PRED_TX_002",
            predicted_outcome="MODERATE_SUCCESS", 
            confidence_level=0.25,
            success_probability=0.45,
            risk_factors=["High baseline pain", "Multiple comorbidities"],
            warnings=["Low confidence prediction", "Consider alternatives"]
        )
    
    @pytest.fixture
    def safety_risk_prediction(self):
        """Prediction with safety concerns"""
        return PredictionResult(
            treatment_id="PRED_TX_003",
            predicted_outcome="HIGH_RISK",
            confidence_level=0.75,
            success_probability=0.30,
            risk_factors=["Drug interaction risk", "Liver enzyme elevation"],
            warnings=["DRUG INTERACTION ALERT", "ALLERGIC REACTION RISK"]
        )
    
    def test_conflict_resolver_initialization(self, conflict_resolver):
        """Test conflict resolver initialization"""
        assert conflict_resolver.threshold == 0.4
        assert hasattr(conflict_resolver, 'escalation_levels')
        assert hasattr(conflict_resolver, 'safety_keywords')
        assert hasattr(conflict_resolver, 'logger')
        
        # Check escalation levels
        expected_levels = [
            "Clinical Pharmacist",
            "Attending Physician", 
            "Senior Clinician"
        ]
        assert conflict_resolver.escalation_levels == expected_levels
    
    def test_no_conflict_high_confidence(self, conflict_resolver, high_confidence_clinical_rec, high_confidence_prediction):
        """Test no conflict when both recommendations have high confidence"""
        result = conflict_resolver.resolve_recommendation_conflict(
            high_confidence_clinical_rec, 
            high_confidence_prediction
        )
        
        assert result['conflict_detected'] == False
        assert result['recommendation'] == 'PROCEED'
        assert result['escalation_required'] == False
        assert 'high confidence' in result['rationale'].lower()
    
    def test_conflict_detected_low_confidence(self, conflict_resolver, low_confidence_clinical_rec, low_confidence_prediction):
        """Test conflict detection when both have low confidence"""
        result = conflict_resolver.resolve_recommendation_conflict(
            low_confidence_clinical_rec,
            low_confidence_prediction
        )
        
        assert result['conflict_detected'] == True
        assert result['recommendation'] == 'INVESTIGATE'
        assert result['escalation_required'] == True
        assert result['escalated_to'] == "Clinical Pharmacist"
    
    def test_safety_override(self, conflict_resolver, high_confidence_clinical_rec, safety_risk_prediction):
        """Test safety concerns override confidence levels"""
        result = conflict_resolver.resolve_recommendation_conflict(
            high_confidence_clinical_rec,
            safety_risk_prediction
        )
        
        assert result['conflict_detected'] == True
        assert result['recommendation'] == 'HOLD'
        assert result['escalation_required'] == True
        assert result['escalated_to'] == "Senior Clinician"  # Highest escalation for safety
        assert 'safety' in result['rationale'].lower()
    
    def test_threshold_configuration(self):
        """Test custom threshold configuration"""
        custom_resolver = ConflictResolution(threshold=0.6)
        assert custom_resolver.threshold == 0.6
        
        # Test with recommendations that would conflict with higher threshold
        clinical_rec = ClinicalRecommendation(
            treatment_id="TX_001",
            recommendation="Test recommendation",
            confidence_level=0.55,  # Below 0.6 threshold
            evidence_level="Level II",
            contraindications=[],
            warnings=[]
        )
        
        prediction = PredictionResult(
            treatment_id="TX_001",
            predicted_outcome="SUCCESS",
            confidence_level=0.55,  # Below 0.6 threshold
            success_probability=0.65,
            risk_factors=[],
            warnings=[]
        )
        
        result = custom_resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        assert result['conflict_detected'] == True  # Should conflict with 0.6 threshold
    
    def test_safety_keyword_detection(self, conflict_resolver):
        """Test safety keyword detection"""
        # Test clinical recommendation with safety keywords
        safety_clinical = ClinicalRecommendation(
            treatment_id="SAFETY_TX",
            recommendation="Proceed with caution",
            confidence_level=0.8,
            evidence_level="Level I",
            contraindications=["KNOWN ALLERGIC REACTION to gabapentin"],
            warnings=["Monitor for DRUG INTERACTION"]
        )
        
        prediction = PredictionResult(
            treatment_id="SAFETY_TX",
            predicted_outcome="SUCCESS",
            confidence_level=0.8,
            success_probability=0.75,
            risk_factors=[],
            warnings=[]
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(safety_clinical, prediction)
        
        # Safety keywords should trigger conflict regardless of confidence
        assert result['conflict_detected'] == True
        assert result['recommendation'] in ['HOLD', 'EMERGENCY_REVIEW']
        assert result['escalation_required'] == True
    
    def test_escalation_hierarchy(self, conflict_resolver):
        """Test escalation hierarchy levels"""
        # Test different severity levels
        
        # Low severity - Clinical Pharmacist
        low_severity_clinical = ClinicalRecommendation(
            treatment_id="LOW_SEV",
            recommendation="Minor dosage adjustment",
            confidence_level=0.3,  # Low confidence
            evidence_level="Level III",
            contraindications=[],
            warnings=[]
        )
        
        low_severity_prediction = PredictionResult(
            treatment_id="LOW_SEV",
            predicted_outcome="MODERATE_SUCCESS",
            confidence_level=0.3,
            success_probability=0.5,
            risk_factors=["Minor concerns"],
            warnings=[]
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(
            low_severity_clinical, 
            low_severity_prediction
        )
        assert result['escalated_to'] == "Clinical Pharmacist"
        
        # High severity - Senior Clinician
        high_severity_prediction = PredictionResult(
            treatment_id="HIGH_SEV",
            predicted_outcome="HIGH_RISK",
            confidence_level=0.8,
            success_probability=0.2,
            risk_factors=["SEVERE DRUG INTERACTION", "ALLERGIC REACTION RISK"],
            warnings=["CRITICAL SAFETY ALERT"]
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(
            low_severity_clinical,
            high_severity_prediction
        )
        assert result['escalated_to'] == "Senior Clinician"
    
    def test_audit_trail_creation(self, conflict_resolver, high_confidence_clinical_rec, low_confidence_prediction):
        """Test audit trail creation"""
        result = conflict_resolver.resolve_recommendation_conflict(
            high_confidence_clinical_rec,
            low_confidence_prediction
        )
        
        assert 'audit_trail' in result
        audit = result['audit_trail']
        
        assert 'timestamp' in audit
        assert 'clinical_confidence' in audit
        assert 'prediction_confidence' in audit
        assert 'decision_rationale' in audit
        assert 'escalation_level' in audit
        
        # Verify timestamp is recent
        assert isinstance(audit['timestamp'], datetime)
    
    def test_conflicting_treatment_ids(self, conflict_resolver):
        """Test handling of different treatment IDs"""
        clinical_rec = ClinicalRecommendation(
            treatment_id="CLINICAL_TX_001",
            recommendation="Treatment A",
            confidence_level=0.8,
            evidence_level="Level I",
            contraindications=[],
            warnings=[]
        )
        
        prediction = PredictionResult(
            treatment_id="PREDICTION_TX_002",  # Different treatment ID
            predicted_outcome="SUCCESS",
            confidence_level=0.8,
            success_probability=0.75,
            risk_factors=[],
            warnings=[]
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        # Should detect ID mismatch as a conflict
        assert result['conflict_detected'] == True
        assert 'treatment id mismatch' in result['rationale'].lower()
    
    def test_edge_case_confidence_levels(self, conflict_resolver):
        """Test edge cases for confidence levels"""
        # Test exactly at threshold
        threshold_clinical = ClinicalRecommendation(
            treatment_id="THRESHOLD_TX",
            recommendation="Threshold test",
            confidence_level=0.4,  # Exactly at threshold
            evidence_level="Level II",
            contraindications=[],
            warnings=[]
        )
        
        threshold_prediction = PredictionResult(
            treatment_id="THRESHOLD_TX",
            predicted_outcome="SUCCESS",
            confidence_level=0.4,  # Exactly at threshold
            success_probability=0.6,
            risk_factors=[],
            warnings=[]
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(
            threshold_clinical,
            threshold_prediction
        )
        
        # At threshold should not conflict (>=)
        assert result['conflict_detected'] == False
        assert result['recommendation'] == 'PROCEED'
    
    def test_missing_data_handling(self, conflict_resolver):
        """Test handling of missing or incomplete data"""
        # Test with minimal data
        minimal_clinical = ClinicalRecommendation(
            treatment_id="MINIMAL_TX",
            recommendation="Minimal recommendation",
            confidence_level=0.5,
            evidence_level="Unknown",
            contraindications=[],
            warnings=[]
        )
        
        minimal_prediction = PredictionResult(
            treatment_id="MINIMAL_TX",
            predicted_outcome="UNKNOWN",
            confidence_level=0.1,  # Very low confidence
            success_probability=0.5,
            risk_factors=[],
            warnings=[]
        )
        
        result = conflict_resolver.resolve_recommendation_conflict(
            minimal_clinical,
            minimal_prediction
        )
        
        # Should handle gracefully
        assert 'recommendation' in result
        assert 'conflict_detected' in result
        assert result['conflict_detected'] == True  # Low confidence should trigger conflict


@pytest.mark.unit
class TestClinicalRecommendation:
    """Unit tests for ClinicalRecommendation data structure"""
    
    def test_clinical_recommendation_creation(self):
        """Test clinical recommendation creation"""
        rec = ClinicalRecommendation(
            treatment_id="TEST_TX",
            recommendation="Test recommendation",
            confidence_level=0.75,
            evidence_level="Level I",
            contraindications=["Drug allergy"],
            warnings=["Monitor closely"]
        )
        
        assert rec.treatment_id == "TEST_TX"
        assert rec.confidence_level == 0.75
        assert "Drug allergy" in rec.contraindications
        assert "Monitor closely" in rec.warnings
    
    def test_clinical_recommendation_validation(self):
        """Test clinical recommendation validation"""
        # Test invalid confidence level
        with pytest.raises(ValueError):
            ClinicalRecommendation(
                treatment_id="INVALID_TX",
                recommendation="Invalid rec",
                confidence_level=1.5,  # Invalid > 1.0
                evidence_level="Level I",
                contraindications=[],
                warnings=[]
            )
        
        with pytest.raises(ValueError):
            ClinicalRecommendation(
                treatment_id="INVALID_TX2", 
                recommendation="Invalid rec",
                confidence_level=-0.1,  # Invalid < 0.0
                evidence_level="Level I",
                contraindications=[],
                warnings=[]
            )


@pytest.mark.unit
class TestPredictionResult:
    """Unit tests for PredictionResult data structure"""
    
    def test_prediction_result_creation(self):
        """Test prediction result creation"""
        pred = PredictionResult(
            treatment_id="TEST_PRED",
            predicted_outcome="SUCCESS",
            confidence_level=0.8,
            success_probability=0.75,
            risk_factors=["Factor 1", "Factor 2"],
            warnings=["Warning 1"]
        )
        
        assert pred.treatment_id == "TEST_PRED"
        assert pred.confidence_level == 0.8
        assert pred.success_probability == 0.75
        assert len(pred.risk_factors) == 2
        assert len(pred.warnings) == 1
    
    def test_prediction_result_validation(self):
        """Test prediction result validation"""
        # Test invalid confidence level
        with pytest.raises(ValueError):
            PredictionResult(
                treatment_id="INVALID_PRED",
                predicted_outcome="SUCCESS",
                confidence_level=2.0,  # Invalid > 1.0
                success_probability=0.5,
                risk_factors=[],
                warnings=[]
            )
        
        # Test invalid success probability
        with pytest.raises(ValueError):
            PredictionResult(
                treatment_id="INVALID_PRED2",
                predicted_outcome="SUCCESS", 
                confidence_level=0.8,
                success_probability=-0.1,  # Invalid < 0.0
                risk_factors=[],
                warnings=[]
            )


@pytest.mark.unit
class TestConflictResolutionIntegration:
    """Integration tests within the conflict resolution module"""
    
    def test_real_world_scenario_1(self):
        """Test real-world conflict scenario: Elderly patient with polypharmacy"""
        resolver = ConflictResolution()
        
        # Clinical recommendation for elderly patient
        clinical_rec = ClinicalRecommendation(
            treatment_id="ELDERLY_TX_001",
            recommendation="Start low-dose pregabalin 75mg BID",
            confidence_level=0.7,
            evidence_level="Level I",
            contraindications=[],
            warnings=["Elderly patient - start low and go slow"]
        )
        
        # Prediction indicates higher risk due to age and medications
        prediction = PredictionResult(
            treatment_id="ELDERLY_TX_001",
            predicted_outcome="MODERATE_RISK",
            confidence_level=0.65,
            success_probability=0.55,
            risk_factors=["Age > 65", "Multiple medications", "Kidney function decline"],
            warnings=["Reduced dose recommended", "Monitor renal function"]
        )
        
        result = resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        # Should proceed with caution due to reasonable confidence levels
        assert result['recommendation'] in ['PROCEED', 'INVESTIGATE']
        assert 'elderly' in result['rationale'].lower() or 'age' in result['rationale'].lower()
    
    def test_real_world_scenario_2(self):
        """Test real-world conflict scenario: High-risk drug interaction"""
        resolver = ConflictResolution()
        
        # Clinical recommendation without awareness of specific interaction
        clinical_rec = ClinicalRecommendation(
            treatment_id="INTERACTION_TX_001",
            recommendation="Add tramadol 50mg QID for breakthrough pain",
            confidence_level=0.8,
            evidence_level="Level I",
            contraindications=[],
            warnings=[]
        )
        
        # Prediction detects dangerous interaction
        prediction = PredictionResult(
            treatment_id="INTERACTION_TX_001",
            predicted_outcome="HIGH_RISK",
            confidence_level=0.9,
            success_probability=0.2,
            risk_factors=["DANGEROUS DRUG INTERACTION with sertraline", "Serotonin syndrome risk"],
            warnings=["CRITICAL: Potential serotonin syndrome", "DRUG INTERACTION ALERT"]
        )
        
        result = resolver.resolve_recommendation_conflict(clinical_rec, prediction)
        
        # Should definitely halt due to safety concerns
        assert result['recommendation'] in ['HOLD', 'EMERGENCY_REVIEW']
        assert result['escalation_required'] == True
        assert result['escalated_to'] == "Senior Clinician"
        assert 'safety' in result['rationale'].lower()
    
    def test_performance_requirements(self):
        """Test that conflict resolution meets performance requirements"""
        import time
        
        resolver = ConflictResolution()
        
        clinical_rec = ClinicalRecommendation(
            treatment_id="PERF_TX",
            recommendation="Performance test",
            confidence_level=0.6,
            evidence_level="Level II",
            contraindications=[],
            warnings=[]
        )
        
        prediction = PredictionResult(
            treatment_id="PERF_TX",
            predicted_outcome="SUCCESS",
            confidence_level=0.8,
            success_probability=0.75,
            risk_factors=[],
            warnings=[]
        )
        
        # Time multiple resolutions
        times = []
        for _ in range(100):
            start = time.perf_counter()
            result = resolver.resolve_recommendation_conflict(clinical_rec, prediction)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
            
            assert 'recommendation' in result  # Ensure it works
        
        avg_time = sum(times) / len(times)
        
        # Should be very fast (< 10ms average)
        assert avg_time < 10, f"Average resolution time {avg_time:.2f}ms too slow"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 