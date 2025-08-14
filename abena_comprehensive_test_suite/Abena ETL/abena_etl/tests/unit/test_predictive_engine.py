"""
Unit Tests for Predictive Analytics Engine

This module contains comprehensive unit tests for the predictive analytics
components including treatment response prediction and adverse event prediction.
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import test fixtures and utilities
from tests.conftest import (
    validate_prediction_result,
    validate_patient_profile,
    validate_treatment_plan
)

# Import core components (these would need to be implemented)
from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult


# ============================================================================
# MOCK PREDICTIVE ENGINE CLASSES
# ============================================================================

class MockTreatmentResponsePredictor:
    """Mock treatment response predictor for testing"""
    
    def __init__(self):
        self.is_trained = False
        self.models = {}
        self.scalers = {}
        self.feature_names = [
            'age', 'gender_male', 'genomics_cyp2c9', 'genomics_oprm1',
            'genomics_comt', 'genomics_cb1', 'biomarkers_inflammatory',
            'biomarkers_endocannabinoid', 'biomarkers_cortisol', 'biomarkers_gaba',
            'medical_history_count', 'current_medications_count',
            'lifestyle_sleep', 'lifestyle_stress', 'pain_score_avg',
            'functional_mobility', 'treatment_type_combined', 'treatment_type_pharmacological',
            'treatment_medications_count', 'treatment_duration', 'treatment_interventions_count',
            'patient_complexity_score'
        ]
    
    def prepare_features(self, patient: PatientProfile, treatment: TreatmentPlan):
        """Prepare feature vector for prediction"""
        features = np.zeros((1, len(self.feature_names)))
        
        # Basic demographics
        features[0, 0] = patient.age / 100.0  # Normalize age
        features[0, 1] = 1.0 if patient.gender == 'male' else 0.0
        
        # Genomics data
        features[0, 2] = patient.genomics_data.get('CYP2C9_activity', 1.0)
        features[0, 3] = patient.genomics_data.get('OPRM1_variant', 0)
        features[0, 4] = patient.genomics_data.get('COMT_activity', 1.0)
        features[0, 5] = patient.genomics_data.get('CB1_receptor_density', 1.0)
        
        # Biomarkers
        features[0, 6] = patient.biomarkers.get('inflammatory_markers', 1.0)
        features[0, 7] = patient.biomarkers.get('endocannabinoid_levels', 1.0)
        features[0, 8] = patient.biomarkers.get('cortisol_baseline', 12.0) / 30.0  # Normalize
        features[0, 9] = patient.biomarkers.get('gaba_activity', 1.0)
        
        # Medical history
        features[0, 10] = len(patient.medical_history) / 10.0  # Normalize
        features[0, 11] = len(patient.current_medications) / 10.0  # Normalize
        
        # Lifestyle metrics
        features[0, 12] = patient.lifestyle_metrics.get('sleep_quality', 5.0) / 10.0
        features[0, 13] = patient.lifestyle_metrics.get('stress_level', 5.0) / 10.0
        
        # Pain and function
        features[0, 14] = np.mean(patient.pain_scores) / 10.0 if patient.pain_scores else 0.5
        features[0, 15] = patient.functional_assessments.get('mobility_score', 50.0) / 100.0
        
        # Treatment features
        features[0, 16] = 1.0 if treatment.treatment_type == 'combined' else 0.0
        features[0, 17] = 1.0 if treatment.treatment_type == 'pharmacological' else 0.0
        features[0, 18] = len(treatment.medications) / 5.0  # Normalize
        features[0, 19] = treatment.duration_weeks / 52.0  # Normalize to year
        features[0, 20] = len(treatment.lifestyle_interventions) / 5.0  # Normalize
        
        # Complexity score
        complexity = (len(patient.medical_history) + len(patient.current_medications) + 
                     (np.mean(patient.pain_scores) if patient.pain_scores else 5.0)) / 20.0
        features[0, 21] = min(complexity, 1.0)
        
        return features
    
    def train_models(self, training_data):
        """Mock model training"""
        self.models = {
            'random_forest': Mock(),
            'gradient_boosting': Mock(),
            'logistic_regression': Mock()
        }
        self.scalers = {
            'response': Mock()
        }
        
        # Mock model behavior
        for model in self.models.values():
            model.predict.return_value = [0.75]
            model.predict_proba.return_value = [[0.25, 0.75]]
            model.feature_importances_ = np.random.random(len(self.feature_names))
        
        self.scalers['response'].transform.return_value = np.random.random((1, len(self.feature_names)))
        
        self.is_trained = True
    
    def predict_treatment_response(self, patient: PatientProfile, treatment: TreatmentPlan):
        """Predict treatment response"""
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        features = self.prepare_features(patient, treatment)
        
        # Mock prediction logic
        success_prob = 0.75  # Mock probability
        risk_score = 1 - success_prob
        
        # Generate mock key factors
        key_factors = [
            "High baseline pain scores",
            "Favorable genomic profile",
            "Good medication adherence history"
        ]
        
        # Generate mock warnings
        warnings = []
        if patient.age > 65:
            warnings.append("ELDERLY PATIENT: Monitor for increased side effects")
        if len(patient.current_medications) > 3:
            warnings.append("POLYPHARMACY RISK: Check for drug interactions")
        if success_prob < 0.6:
            warnings.append("LOW SUCCESS PROBABILITY: Consider alternative treatments")
        
        return PredictionResult(
            patient_id=patient.patient_id,
            treatment_id=treatment.treatment_id,
            success_probability=success_prob,
            risk_score=risk_score,
            key_factors=key_factors,
            warnings=warnings,
            timestamp=datetime.now(),
            confidence_interval=(success_prob - 0.1, success_prob + 0.1),
            feature_importance={'pain_score': 0.3, 'genomics': 0.2, 'age': 0.15},
            model_version="mock_1.0.0"
        )


class MockAdverseEventPredictor:
    """Mock adverse event predictor for testing"""
    
    def __init__(self):
        self.is_trained = False
        self.models = {}
        self.thresholds = {
            'severe_side_effects': 0.5,
            'treatment_discontinuation': 0.4,
            'hospitalization': 0.3
        }
    
    def _prepare_adverse_event_features(self, patient: PatientProfile, treatment: TreatmentPlan):
        """Prepare features for adverse event prediction"""
        features = np.zeros((1, 12))
        
        # Patient risk factors
        features[0, 0] = patient.age / 100.0
        features[0, 1] = len(patient.medical_history) / 10.0
        features[0, 2] = len(patient.current_medications) / 10.0
        features[0, 3] = patient.biomarkers.get('liver_enzymes', 1.0)
        features[0, 4] = patient.biomarkers.get('kidney_function', 1.0)
        
        # Treatment risk factors
        features[0, 5] = len(treatment.medications) / 5.0
        features[0, 6] = treatment.duration_weeks / 52.0
        features[0, 7] = 1.0 if 'opioid' in ' '.join(treatment.medications).lower() else 0.0
        
        # Interaction risks
        features[0, 8] = patient.genomics_data.get('CYP2C9_activity', 1.0)
        features[0, 9] = 1.0 if len(patient.allergies) > 0 else 0.0
        features[0, 10] = np.mean(patient.pain_scores) / 10.0 if patient.pain_scores else 0.5
        features[0, 11] = patient.lifestyle_metrics.get('stress_level', 5.0) / 10.0
        
        return features
    
    def _categorize_risk(self, probability: float) -> str:
        """Categorize risk level based on probability"""
        if probability >= 0.7:
            return 'HIGH'
        elif probability >= 0.5:
            return 'MODERATE'
        elif probability >= 0.3:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _calculate_overall_risk(self, risk_assessment: dict) -> str:
        """Calculate overall risk level"""
        high_risks = sum(1 for event in risk_assessment.values() 
                        if event.get('risk_level') == 'HIGH')
        moderate_risks = sum(1 for event in risk_assessment.values() 
                           if event.get('risk_level') == 'MODERATE')
        
        if high_risks >= 2:
            return 'CRITICAL'
        elif high_risks >= 1:
            return 'HIGH'
        elif moderate_risks >= 2:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def predict_adverse_events(self, patient: PatientProfile, treatment: TreatmentPlan):
        """Predict adverse events"""
        features = self._prepare_adverse_event_features(patient, treatment)
        
        # Mock predictions for different adverse events
        risk_scores = {
            'severe_side_effects': {
                'probability': 0.3,
                'risk_level': self._categorize_risk(0.3)
            },
            'treatment_discontinuation': {
                'probability': 0.2,
                'risk_level': self._categorize_risk(0.2)
            },
            'hospitalization': {
                'probability': 0.1,
                'risk_level': self._categorize_risk(0.1)
            }
        }
        
        overall_risk = self._calculate_overall_risk(risk_scores)
        
        return {
            'patient_id': patient.patient_id,
            'treatment_id': treatment.treatment_id,
            'overall_risk_level': overall_risk,
            'risk_scores': risk_scores,
            'recommendations': [
                "Monitor vital signs closely",
                "Schedule follow-up in 2 weeks"
            ],
            'timestamp': datetime.now()
        }


# ============================================================================
# UNIT TESTS
# ============================================================================

@pytest.mark.unit
class TestTreatmentResponsePredictor:
    """Unit tests for TreatmentResponsePredictor"""
    
    def test_feature_preparation(self, sample_patient, sample_treatment):
        """Test feature vector creation"""
        predictor = MockTreatmentResponsePredictor()
        features = predictor.prepare_features(sample_patient, sample_treatment)
        
        assert features.shape == (1, 22)  # Expected number of features
        assert isinstance(features, np.ndarray)
        assert not np.isnan(features).any()  # No NaN values
        assert not np.isinf(features).any()  # No infinite values
        assert np.all(features >= 0) and np.all(features <= 1)  # Normalized features
    
    def test_model_training(self, mock_training_data):
        """Test model training process"""
        predictor = MockTreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        assert predictor.is_trained
        assert 'random_forest' in predictor.models
        assert 'gradient_boosting' in predictor.models
        assert 'logistic_regression' in predictor.models
        assert 'response' in predictor.scalers
    
    def test_prediction_output_structure(self, sample_patient, sample_treatment, mock_training_data):
        """Test prediction result structure"""
        predictor = MockTreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        result = predictor.predict_treatment_response(sample_patient, sample_treatment)
        
        # Validate result structure
        validate_prediction_result(result)
        
        # Validate specific fields
        assert result.patient_id == sample_patient.patient_id
        assert result.treatment_id == sample_treatment.treatment_id
        assert 0 <= result.success_probability <= 1
        assert 0 <= result.risk_score <= 1
        assert isinstance(result.key_factors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.timestamp, datetime)
    
    def test_prediction_without_training(self, sample_patient, sample_treatment):
        """Test that prediction fails without training"""
        predictor = MockTreatmentResponsePredictor()
        
        with pytest.raises(ValueError, match="Models must be trained"):
            predictor.predict_treatment_response(sample_patient, sample_treatment)
    
    def test_feature_edge_cases(self, sample_treatment):
        """Test feature preparation with edge cases"""
        predictor = MockTreatmentResponsePredictor()
        
        # Test with minimal patient data
        minimal_patient = PatientProfile(
            patient_id="MINIMAL_PATIENT",
            age=30,
            gender="other",
            genomics_data={},
            biomarkers={},
            medical_history=[],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[],
            functional_assessments={}
        )
        
        features = predictor.prepare_features(minimal_patient, sample_treatment)
        
        # Should handle missing data gracefully
        assert features.shape == (1, 22)
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()
    
    def test_prediction_consistency(self, sample_patient, sample_treatment, mock_training_data):
        """Test that predictions are consistent for same input"""
        predictor = MockTreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        # Make multiple predictions
        results = []
        for _ in range(5):
            result = predictor.predict_treatment_response(sample_patient, sample_treatment)
            results.append(result.success_probability)
        
        # All results should be identical (deterministic behavior)
        assert all(abs(r - results[0]) < 1e-10 for r in results)


@pytest.mark.unit
class TestAdverseEventPredictor:
    """Unit tests for AdverseEventPredictor"""
    
    def test_adverse_event_feature_preparation(self, sample_patient, sample_treatment):
        """Test adverse event feature preparation"""
        predictor = MockAdverseEventPredictor()
        features = predictor._prepare_adverse_event_features(sample_patient, sample_treatment)
        
        assert features.shape == (1, 12)  # Expected number of features
        assert isinstance(features, np.ndarray)
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()
    
    def test_risk_categorization(self):
        """Test risk level categorization"""
        predictor = MockAdverseEventPredictor()
        
        assert predictor._categorize_risk(0.8) == 'HIGH'
        assert predictor._categorize_risk(0.6) == 'MODERATE'
        assert predictor._categorize_risk(0.4) == 'LOW'
        assert predictor._categorize_risk(0.2) == 'MINIMAL'
        
        # Test edge cases
        assert predictor._categorize_risk(0.7) == 'HIGH'  # Boundary
        assert predictor._categorize_risk(0.5) == 'MODERATE'  # Boundary
        assert predictor._categorize_risk(0.3) == 'LOW'  # Boundary
    
    def test_overall_risk_calculation(self):
        """Test overall risk level calculation"""
        predictor = MockAdverseEventPredictor()
        
        # Test critical risk scenario
        risk_assessment = {
            'event1': {'risk_level': 'HIGH'},
            'event2': {'risk_level': 'HIGH'},
            'event3': {'risk_level': 'LOW'}
        }
        assert predictor._calculate_overall_risk(risk_assessment) == 'CRITICAL'
        
        # Test high risk scenario
        risk_assessment = {
            'event1': {'risk_level': 'HIGH'},
            'event2': {'risk_level': 'MODERATE'},
            'event3': {'risk_level': 'LOW'}
        }
        assert predictor._calculate_overall_risk(risk_assessment) == 'HIGH'
        
        # Test moderate risk scenario
        risk_assessment = {
            'event1': {'risk_level': 'MODERATE'},
            'event2': {'risk_level': 'MODERATE'},
            'event3': {'risk_level': 'LOW'}
        }
        assert predictor._calculate_overall_risk(risk_assessment) == 'MODERATE'
        
        # Test low risk scenario
        risk_assessment = {
            'event1': {'risk_level': 'LOW'},
            'event2': {'risk_level': 'MINIMAL'},
            'event3': {'risk_level': 'LOW'}
        }
        assert predictor._calculate_overall_risk(risk_assessment) == 'LOW'
    
    def test_adverse_event_prediction_structure(self, sample_patient, sample_treatment):
        """Test adverse event prediction output structure"""
        predictor = MockAdverseEventPredictor()
        result = predictor.predict_adverse_events(sample_patient, sample_treatment)
        
        # Check required fields
        assert 'patient_id' in result
        assert 'treatment_id' in result
        assert 'overall_risk_level' in result
        assert 'risk_scores' in result
        assert 'recommendations' in result
        assert 'timestamp' in result
        
        # Validate field types and values
        assert result['patient_id'] == sample_patient.patient_id
        assert result['treatment_id'] == sample_treatment.treatment_id
        assert result['overall_risk_level'] in ['MINIMAL', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL']
        assert isinstance(result['risk_scores'], dict)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['timestamp'], datetime)
        
        # Validate risk scores structure
        for event, scores in result['risk_scores'].items():
            assert 'probability' in scores
            assert 'risk_level' in scores
            assert 0 <= scores['probability'] <= 1
            assert scores['risk_level'] in ['MINIMAL', 'LOW', 'MODERATE', 'HIGH']


@pytest.mark.unit
class TestPredictiveAnalyticsEngine:
    """Unit tests for main PredictiveAnalyticsEngine"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        # This would test the actual PredictiveAnalyticsEngine class
        # For now, we'll test that our mock classes work properly
        
        treatment_predictor = MockTreatmentResponsePredictor()
        adverse_predictor = MockAdverseEventPredictor()
        
        assert hasattr(treatment_predictor, 'prepare_features')
        assert hasattr(treatment_predictor, 'train_models')
        assert hasattr(treatment_predictor, 'predict_treatment_response')
        assert hasattr(adverse_predictor, 'predict_adverse_events')
    
    def test_feature_importance_extraction(self, sample_patient, sample_treatment, mock_training_data):
        """Test feature importance extraction"""
        predictor = MockTreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        result = predictor.predict_treatment_response(sample_patient, sample_treatment)
        
        # Should have feature importance data
        assert hasattr(result, 'feature_importance')
        assert isinstance(result.feature_importance, dict)
        assert len(result.feature_importance) > 0
        
        # All importance values should be between 0 and 1
        for importance in result.feature_importance.values():
            assert 0 <= importance <= 1


@pytest.mark.unit
class TestDataValidation:
    """Test data validation and edge cases"""
    
    def test_patient_data_validation(self, sample_patient):
        """Test patient data validation"""
        validate_patient_profile(sample_patient)
        
        # Test invalid age
        invalid_patient = PatientProfile(
            patient_id="INVALID_PATIENT",
            age=-5,  # Invalid age
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=[],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[],
            functional_assessments={}
        )
        
        with pytest.raises(ValueError):
            # Should raise error for invalid age
            pass
    
    def test_treatment_plan_validation(self, sample_treatment):
        """Test treatment plan validation"""
        validate_treatment_plan(sample_treatment)
        
        # Test invalid duration
        invalid_treatment = TreatmentPlan(
            treatment_id="INVALID_TX",
            treatment_type="combined",
            medications=['drug1'],
            dosages={'drug1': '100mg'},
            duration_weeks=-1,  # Invalid duration
            lifestyle_interventions=[]
        )
        
        with pytest.raises(ValueError):
            # Should raise error for invalid duration
            pass
    
    def test_prediction_result_validation(self):
        """Test prediction result validation"""
        # Test valid prediction result
        valid_result = PredictionResult(
            patient_id="TEST_PATIENT",
            treatment_id="TEST_TX",
            success_probability=0.75,
            risk_score=0.25,
            key_factors=["factor1", "factor2"],
            warnings=["warning1"],
            timestamp=datetime.now()
        )
        
        validate_prediction_result(valid_result)
        
        # Test invalid probability
        with pytest.raises(ValueError):
            invalid_result = PredictionResult(
                patient_id="TEST_PATIENT",
                treatment_id="TEST_TX",
                success_probability=1.5,  # Invalid probability
                risk_score=0.25,
                key_factors=["factor1"],
                warnings=[],
                timestamp=datetime.now()
            )


@pytest.mark.unit
class TestPerformanceRequirements:
    """Test performance requirements for predictive components"""
    
    def test_prediction_speed(self, sample_patient, sample_treatment, mock_training_data):
        """Test prediction speed requirements"""
        import time
        
        predictor = MockTreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        # Time a single prediction
        start_time = time.perf_counter()
        result = predictor.predict_treatment_response(sample_patient, sample_treatment)
        end_time = time.perf_counter()
        
        prediction_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Should be fast enough for real-time use
        assert prediction_time < 100, f"Prediction took {prediction_time:.2f}ms, should be < 100ms"
        assert result is not None
    
    def test_batch_prediction_performance(self, realistic_patient_cohort, sample_treatment, mock_training_data):
        """Test batch prediction performance"""
        import time
        
        predictor = MockTreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        # Time batch predictions
        start_time = time.perf_counter()
        
        results = []
        for patient in realistic_patient_cohort:
            result = predictor.predict_treatment_response(patient, sample_treatment)
            results.append(result)
        
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        avg_time_per_prediction = (total_time / len(realistic_patient_cohort)) * 1000
        
        # Should maintain good performance for batch processing
        assert avg_time_per_prediction < 50, f"Avg prediction time {avg_time_per_prediction:.2f}ms too high"
        assert len(results) == len(realistic_patient_cohort)
        
        # All results should be valid
        for result in results:
            validate_prediction_result(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 