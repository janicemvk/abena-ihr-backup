# Unit tests for Predictive Analytics Engine
import pytest
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch
from src.predictive_analytics.predictive_engine import (
    TreatmentResponsePredictor, 
    AdverseEventPredictor, 
    PredictiveAnalyticsEngine
)

class TestTreatmentResponsePredictor:
    """Unit tests for TreatmentResponsePredictor"""
    
    def test_feature_preparation(self, sample_patient, sample_treatment):
        """Test feature vector creation"""
        predictor = TreatmentResponsePredictor()
        features = predictor.prepare_features(sample_patient, sample_treatment)
        
        assert features.shape == (1, 22)  # Expected number of features
        assert isinstance(features, np.ndarray)
        assert not np.isnan(features).any()  # No NaN values 

    def test_model_training(self, mock_training_data):
        """Test model training process"""
        predictor = TreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        assert predictor.is_trained
        assert 'random_forest' in predictor.models
        assert 'gradient_boosting' in predictor.models
        assert 'logistic_regression' in predictor.models
        assert 'response' in predictor.scalers
    
    def test_prediction_output(self, sample_patient, sample_treatment, mock_training_data):
        """Test prediction result structure"""
        predictor = TreatmentResponsePredictor()
        predictor.train_models(mock_training_data)
        
        result = predictor.predict_treatment_response(sample_patient, sample_treatment)
        
        assert result.patient_id == sample_patient.patient_id
        assert result.treatment_id == sample_treatment.treatment_id
        assert 0 <= result.success_probability <= 1
        assert 0 <= result.risk_score <= 1
        assert isinstance(result.key_factors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.timestamp, datetime)
    
    def test_prediction_without_training(self, sample_patient, sample_treatment):
        """Test that prediction fails without training"""
        predictor = TreatmentResponsePredictor()
        
        with pytest.raises(ValueError, match="Models must be trained"):
            predictor.predict_treatment_response(sample_patient, sample_treatment)

class TestAdverseEventPredictor:
    """Unit tests for AdverseEventPredictor"""
    
    def test_adverse_event_feature_preparation(self, sample_patient, sample_treatment):
        """Test adverse event feature preparation"""
        predictor = AdverseEventPredictor()
        features = predictor._prepare_adverse_event_features(sample_patient, sample_treatment)
        
        assert features.shape == (1, 12)  # Expected number of features for adverse events
        assert isinstance(features, np.ndarray)
        assert not np.isnan(features).any()
    
    def test_risk_categorization(self):
        """Test risk level categorization"""
        predictor = AdverseEventPredictor()
        
        assert predictor._categorize_risk(0.8) == 'HIGH'
        assert predictor._categorize_risk(0.5) == 'MODERATE'
        assert predictor._categorize_risk(0.3) == 'LOW'
        assert predictor._categorize_risk(0.1) == 'MINIMAL'
    
    def test_overall_risk_calculation(self):
        """Test overall risk level calculation"""
        predictor = AdverseEventPredictor()
        
        # Test high risk scenario
        risk_assessment = {
            'event1': {'risk_level': 'HIGH'},
            'event2': {'risk_level': 'HIGH'},
            'event3': {'risk_level': 'LOW'}
        }
        assert predictor._calculate_overall_risk(risk_assessment) == 'CRITICAL'
        
        # Test moderate risk scenario
        risk_assessment = {
            'event1': {'risk_level': 'MODERATE'},
            'event2': {'risk_level': 'MODERATE'},
            'event3': {'risk_level': 'LOW'}
        }
        assert predictor._calculate_overall_risk(risk_assessment) == 'MODERATE'

class TestPredictiveAnalyticsEngine:
    """Unit tests for main PredictiveAnalyticsEngine"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = PredictiveAnalyticsEngine()
        
        assert hasattr(engine, 'treatment_predictor')
        assert hasattr(engine, 'adverse_event_predictor')
        assert hasattr(engine, 'logger')
    
    def test_treatment_recommendation_generation(self, sample_patient, sample_treatment, mock_training_data):
        """Test treatment recommendation generation"""
        engine = PredictiveAnalyticsEngine()
        
        # Mock training data for adverse events
        adverse_event_data = []
        for patient, treatment, outcome in mock_training_data[:50]:
            adverse_outcomes = {
                'severe_side_effects': np.random.randint(0, 2),
                'treatment_discontinuation': np.random.randint(0, 2),
                'hospitalization': np.random.randint(0, 2)
            }
            adverse_event_data.append((patient, treatment, adverse_outcomes))
        
        engine.initialize_models(mock_training_data, adverse_event_data)
        
        recommendations = engine.generate_treatment_recommendation(
            sample_patient, 
            [sample_treatment]
        )
        
        assert 'patient_id' in recommendations
        assert 'recommended_treatment' in recommendations
        assert 'alternative_treatments' in recommendations
        assert 'clinical_decision_support' in recommendations
        assert recommendations['patient_id'] == sample_patient.patient_id 