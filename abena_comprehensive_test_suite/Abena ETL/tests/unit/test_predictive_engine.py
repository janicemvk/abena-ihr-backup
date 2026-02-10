"""
Unit Tests for Predictive Engine Components

This module contains unit tests for the core predictive analytics
components of the Abena IHR System.
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult
from tests.conftest import validate_prediction_result, validate_patient_profile, validate_treatment_plan


# ============================================================================
# MOCK PREDICTIVE ENGINE CLASSES
# ============================================================================

class MockTreatmentResponsePredictor:
    """Mock treatment response predictor for testing"""
    
    def __init__(self, model_accuracy=0.85):
        self.model_accuracy = model_accuracy
        self.feature_weights = {
            'age': 0.15,
            'genomics_cyp2c9': 0.25,
            'pain_severity': 0.20,
            'comorbidities': 0.18,
            'previous_treatments': 0.22
        }
        self.is_trained = True
    
    def predict_treatment_response(self, patient: PatientProfile, treatment: TreatmentPlan) -> PredictionResult:
        """Mock prediction based on patient and treatment characteristics"""
        # Calculate mock success probability based on patient factors
        base_probability = 0.6
        
        # Age factor (younger patients generally respond better)
        age_factor = max(0, (70 - patient.age) / 70) * 0.1
        
        # Genomics factor
        genomics_factor = 0
        if hasattr(patient, 'genomics_data') and patient.genomics_data:
            cyp2c9_activity = patient.genomics_data.get('CYP2C9_activity', 1.0)
            genomics_factor = (cyp2c9_activity - 0.5) * 0.15
        
        # Pain severity factor (moderate pain responds better than severe)
        pain_factor = 0
        if patient.pain_scores:
            avg_pain = sum(patient.pain_scores) / len(patient.pain_scores)
            if 4 <= avg_pain <= 7:  # Moderate pain
                pain_factor = 0.1
            elif avg_pain > 8:  # Severe pain is harder to treat
                pain_factor = -0.05
        
        # Comorbidity factor
        comorbidity_factor = -len(patient.medical_history) * 0.02
        
        # Treatment type factor
        treatment_factor = 0
        if treatment.treatment_type == 'combined':
            treatment_factor = 0.1
        elif treatment.treatment_type == 'behavioral':
            treatment_factor = 0.05
        
        # Calculate final probability
        success_probability = base_probability + age_factor + genomics_factor + pain_factor + comorbidity_factor + treatment_factor
        success_probability = max(0.1, min(0.95, success_probability))
        
        # Generate warnings based on risk factors
        warnings = []
        if patient.age > 65:
            warnings.append("ELDERLY PATIENT: Consider dose adjustment")
        
        if len(patient.current_medications) > 5:
            warnings.append("POLYPHARMACY: Review drug interactions")
        
        if patient.pain_scores and max(patient.pain_scores) >= 9:
            warnings.append("SEVERE PAIN: May require multimodal approach")
        
        return PredictionResult(
            patient_id=patient.patient_id,
            treatment_id=treatment.treatment_id,
            success_probability=success_probability,
            risk_score=1 - success_probability,
            key_factors=['age', 'genomics', 'pain_severity', 'comorbidities'],
            warnings=warnings,
            timestamp=datetime.now()
        )
    
    def get_feature_importance(self) -> dict:
        """Return feature importance weights"""
        return self.feature_weights.copy()
    
    def update_model(self, training_data: list) -> dict:
        """Mock model update"""
        return {
            'samples_processed': len(training_data),
            'accuracy_improvement': 0.02,
            'model_version': '2.1.0',
            'updated_at': datetime.now()
        }

    def prepare_features(self, patient: PatientProfile, treatment: TreatmentPlan) -> np.ndarray:
        """Prepare feature vector for prediction"""
        # Create comprehensive feature vector (22 features)
        features = [
            # Patient demographics (2 features)
            min(patient.age / 100.0, 1.0),  # Normalized age (capped at 1.0)
            1.0 if patient.gender == 'female' else 0.0,
            
            # Genomics features (3 features)
            min(patient.genomics_data.get('CYP2C9_activity', 1.0), 1.0) if patient.genomics_data else 1.0,
            min(patient.genomics_data.get('OPRM1_variant', 0.0), 1.0) if patient.genomics_data else 0.0,
            min(patient.genomics_data.get('COMT_activity', 1.0), 1.0) if patient.genomics_data else 1.0,
            
            # Pain and medical history features (4 features)
            min(sum(patient.pain_scores) / len(patient.pain_scores) / 10.0, 1.0) if patient.pain_scores else 0.0,
            min(len(patient.medical_history) / 5.0, 1.0),  # Normalized medical history count
            min(len(patient.current_medications) / 10.0, 1.0),  # Normalized medication count
            1.0 if 'chronic_pain' in patient.medical_history else 0.0,
            
            # Treatment features (5 features)
            1.0 if treatment.treatment_type == 'combined' else 0.0,
            1.0 if treatment.treatment_type == 'behavioral' else 0.0,
            1.0 if treatment.treatment_type == 'pharmacological' else 0.0,
            min(len(treatment.medications) / 5.0, 1.0),  # Normalized medication count
            min(treatment.duration_weeks / 52.0, 1.0),  # Normalized weeks (max 1 year)
            
            # Biomarkers and lifestyle (4 features)
            min(len(patient.biomarkers) / 10.0, 1.0) if patient.biomarkers else 0.0,
            min(len(patient.lifestyle_metrics) / 10.0, 1.0) if patient.lifestyle_metrics else 0.0,
            min(len(patient.functional_assessments) / 10.0, 1.0) if patient.functional_assessments else 0.0,
            min(len(treatment.lifestyle_interventions) / 5.0, 1.0),
            
            # Risk factors (4 features)
            min(patient.age / 100.0, 1.0),  # Age risk factor
            min(len(patient.current_medications) / 10.0, 1.0),  # Polypharmacy risk
            min(len(patient.medical_history) / 5.0, 1.0),  # Comorbidity risk
            min(max(patient.pain_scores) / 10.0, 1.0) if patient.pain_scores else 0.0  # Max pain score normalized
        ]
        
        return np.array(features).reshape(1, -1)


class MockAdverseEventPredictor:
    """Mock adverse event predictor for testing"""
    
    def __init__(self):
        self.risk_thresholds = {
            'low': 0.1,
            'medium': 0.3,
            'high': 0.6
        }
    
    def predict_adverse_events(self, patient: PatientProfile, treatment: TreatmentPlan) -> dict:
        """Predict adverse event risks"""
        # Base risk calculation
        base_risk = 0.05
        
        # Age-related risk
        age_risk = max(0, (patient.age - 40) / 60) * 0.2
        
        # Medication interaction risk
        interaction_risk = 0
        if len(patient.current_medications) > 3:
            interaction_risk = len(patient.current_medications) * 0.03
        
        # Comorbidity risk
        comorbidity_risk = len(patient.medical_history) * 0.02
        
        # Treatment-specific risks
        treatment_risk = 0
        if 'opioid' in ' '.join(treatment.medications).lower():
            treatment_risk = 0.15
        elif 'nsaid' in ' '.join(treatment.medications).lower():
            treatment_risk = 0.08
        
        overall_risk = base_risk + age_risk + interaction_risk + comorbidity_risk + treatment_risk
        overall_risk = min(0.8, overall_risk)
        
        # Specific adverse event predictions
        adverse_events = {
            'overall_risk': overall_risk,
            'specific_risks': {
                'gastrointestinal': min(0.6, overall_risk * 0.8),
                'cardiovascular': min(0.4, age_risk * 2),
                'neurological': min(0.5, treatment_risk * 1.2),
                'allergic_reaction': 0.02
            },
            'risk_level': self._categorize_risk(overall_risk),
            'monitoring_recommendations': self._generate_monitoring_recommendations(overall_risk, patient)
        }
        
        return adverse_events
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score < self.risk_thresholds['low']:
            return 'LOW'
        elif risk_score < self.risk_thresholds['medium']:
            return 'MEDIUM'
        elif risk_score < self.risk_thresholds['high']:
            return 'HIGH'
        else:
            return 'VERY_HIGH'
    
    def _generate_monitoring_recommendations(self, risk_score: float, patient: PatientProfile) -> list:
        """Generate monitoring recommendations based on risk"""
        recommendations = []
        
        if risk_score > 0.3:
            recommendations.append("Monitor for side effects weekly for first month")
        
        if patient.age > 65:
            recommendations.append("Enhanced monitoring for elderly patient")
        
        if len(patient.current_medications) > 5:
            recommendations.append("Review all medications for interactions")
        
        if risk_score > 0.5:
            recommendations.append("Consider specialist consultation")
        
        return recommendations


# ============================================================================
# UNIT TESTS
# ============================================================================

@pytest.mark.unit
class TestTreatmentResponsePredictor:
    """Unit tests for treatment response prediction"""
    
    @pytest.fixture
    def predictor(self):
        """Create mock predictor for testing"""
        return MockTreatmentResponsePredictor()
    
    def test_basic_prediction_functionality(self, predictor, sample_patient, sample_treatment):
        """Test basic prediction functionality"""
        result = predictor.predict_treatment_response(sample_patient, sample_treatment)
        
        # Validate result structure
        validate_prediction_result(result)
        
        # Check result values
        assert 0.1 <= result.success_probability <= 0.95
        assert 0.05 <= result.risk_score <= 0.9
        assert result.patient_id == sample_patient.patient_id
        assert result.treatment_id == sample_treatment.treatment_id
        assert isinstance(result.key_factors, list)
        assert len(result.key_factors) > 0
    
    def test_age_based_predictions(self, predictor, sample_treatment):
        """Test predictions vary appropriately with patient age"""
        # Young patient
        young_patient = PatientProfile(
            patient_id="YOUNG_001",
            age=25,
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        # Elderly patient
        elderly_patient = PatientProfile(
            patient_id="ELDERLY_001",
            age=75,
            gender="male",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        young_result = predictor.predict_treatment_response(young_patient, sample_treatment)
        elderly_result = predictor.predict_treatment_response(elderly_patient, sample_treatment)
        
        # Young patients should generally have better predicted outcomes
        assert young_result.success_probability >= elderly_result.success_probability
        
        # Elderly patient should have appropriate warnings
        elderly_warnings = [w.upper() for w in elderly_result.warnings]
        assert any('ELDERLY' in warning for warning in elderly_warnings)
    
    def test_genomics_influence_on_predictions(self, predictor, sample_treatment):
        """Test genomics data influences predictions appropriately"""
        # High CYP2C9 activity (fast metabolizer)
        fast_metabolizer = PatientProfile(
            patient_id="FAST_001",
            age=45,
            gender="female",
            genomics_data={'CYP2C9_activity': 1.5},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        # Low CYP2C9 activity (slow metabolizer)
        slow_metabolizer = PatientProfile(
            patient_id="SLOW_001",
            age=45,
            gender="female",
            genomics_data={'CYP2C9_activity': 0.3},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        fast_result = predictor.predict_treatment_response(fast_metabolizer, sample_treatment)
        slow_result = predictor.predict_treatment_response(slow_metabolizer, sample_treatment)
        
        # Both should be valid predictions
        validate_prediction_result(fast_result)
        validate_prediction_result(slow_result)
        
        # Results should differ based on genomics
        assert fast_result.success_probability != slow_result.success_probability
    
    def test_pain_severity_impact(self, predictor, sample_treatment):
        """Test pain severity impacts predictions"""
        # Moderate pain patient
        moderate_pain_patient = PatientProfile(
            patient_id="MODERATE_001",
            age=45,
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[5.0, 6.0, 5.5, 6.5],
            functional_assessments={}
        )
        
        # Severe pain patient
        severe_pain_patient = PatientProfile(
            patient_id="SEVERE_001",
            age=45,
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[9.0, 9.5, 8.5, 9.0],
            functional_assessments={}
        )
        
        moderate_result = predictor.predict_treatment_response(moderate_pain_patient, sample_treatment)
        severe_result = predictor.predict_treatment_response(severe_pain_patient, sample_treatment)
        
        # Severe pain should trigger warnings
        severe_warnings = [w.upper() for w in severe_result.warnings]
        assert any('SEVERE PAIN' in warning for warning in severe_warnings)
    
    def test_polypharmacy_warnings(self, predictor, sample_treatment):
        """Test polypharmacy generates appropriate warnings"""
        polypharmacy_patient = PatientProfile(
            patient_id="POLY_001",
            age=65,
            gender="male",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain", "diabetes", "hypertension"],
            current_medications=["metformin", "lisinopril", "amlodipine", "gabapentin", "sertraline", "omeprazole"],
            lifestyle_metrics={},
            pain_scores=[7.0],
            functional_assessments={}
        )
        
        result = predictor.predict_treatment_response(polypharmacy_patient, sample_treatment)
        
        # Should generate polypharmacy warning
        warnings = [w.upper() for w in result.warnings]
        assert any('POLYPHARMACY' in warning for warning in warnings)
    
    def test_treatment_type_influence(self, predictor, sample_patient):
        """Test different treatment types influence predictions"""
        # Combined treatment
        combined_treatment = TreatmentPlan(
            treatment_id="COMBINED_001",
            treatment_type="combined",
            medications=["pregabalin", "cbd_oil"],
            dosages={"pregabalin": "150mg_bid", "cbd_oil": "25mg_daily"},
            duration_weeks=12,
            lifestyle_interventions=["physical_therapy"]
        )
        
        # Behavioral treatment
        behavioral_treatment = TreatmentPlan(
            treatment_id="BEHAVIORAL_001",
            treatment_type="behavioral",
            medications=[],
            dosages={},
            duration_weeks=16,
            lifestyle_interventions=["cognitive_behavioral_therapy", "meditation"]
        )
        
        # Pharmacological treatment
        pharma_treatment = TreatmentPlan(
            treatment_id="PHARMA_001",
            treatment_type="pharmacological",
            medications=["duloxetine"],
            dosages={"duloxetine": "60mg_daily"},
            duration_weeks=8,
            lifestyle_interventions=[]
        )
        
        combined_result = predictor.predict_treatment_response(sample_patient, combined_treatment)
        behavioral_result = predictor.predict_treatment_response(sample_patient, behavioral_treatment)
        pharma_result = predictor.predict_treatment_response(sample_patient, pharma_treatment)
        
        # All should be valid predictions
        validate_prediction_result(combined_result)
        validate_prediction_result(behavioral_result)
        validate_prediction_result(pharma_result)
        
        # Combined treatment should generally have highest success probability
        assert combined_result.success_probability >= behavioral_result.success_probability
        assert combined_result.success_probability >= pharma_result.success_probability
    
    def test_feature_importance_access(self, predictor):
        """Test feature importance can be accessed"""
        importance = predictor.get_feature_importance()
        
        assert isinstance(importance, dict)
        assert len(importance) > 0
        
        # Check expected features are present
        expected_features = ['age', 'genomics_cyp2c9', 'pain_severity', 'comorbidities', 'previous_treatments']
        for feature in expected_features:
            assert feature in importance
            assert 0 <= importance[feature] <= 1
    
    def test_model_update_functionality(self, predictor):
        """Test model update functionality"""
        # Mock training data
        training_data = [
            {'patient_id': 'P001', 'outcome': 'success'},
            {'patient_id': 'P002', 'outcome': 'partial'},
            {'patient_id': 'P003', 'outcome': 'failure'}
        ]
        
        update_result = predictor.update_model(training_data)
        
        assert 'samples_processed' in update_result
        assert 'accuracy_improvement' in update_result
        assert 'model_version' in update_result
        assert 'updated_at' in update_result
        
        assert update_result['samples_processed'] == len(training_data)
        assert update_result['accuracy_improvement'] >= 0

    def test_feature_preparation(self, sample_patient, sample_treatment):
        """Test feature vector creation"""
        predictor = MockTreatmentResponsePredictor()
        features = predictor.prepare_features(sample_patient, sample_treatment)
        
        assert features.shape == (1, 22)  # Expected number of features
        assert isinstance(features, np.ndarray)
        assert not np.isnan(features).any()  # No NaN values
        assert not np.isinf(features).any()  # No infinite values
        assert np.all(features >= 0)  # Non-negative features

    def test_patient_data_validation(self, sample_patient):
        """Test patient data validation"""
        validate_patient_profile(sample_patient)
        
        # Test invalid age
        with pytest.raises(ValueError, match="Invalid age"):
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

    def test_treatment_plan_validation(self, sample_treatment):
        """Test treatment plan validation"""
        validate_treatment_plan(sample_treatment)
        
        # Test invalid duration
        with pytest.raises(ValueError, match="Invalid duration"):
            invalid_treatment = TreatmentPlan(
                treatment_id="INVALID_TX",
                treatment_type="combined",
                medications=['drug1'],
                dosages={'drug1': '100mg'},
                duration_weeks=-1,  # Invalid duration
                lifestyle_interventions=[]
            )


@pytest.mark.unit
class TestAdverseEventPredictor:
    """Unit tests for adverse event prediction"""
    
    @pytest.fixture
    def adverse_predictor(self):
        """Create adverse event predictor for testing"""
        return MockAdverseEventPredictor()
    
    def test_basic_adverse_event_prediction(self, adverse_predictor, sample_patient, sample_treatment):
        """Test basic adverse event prediction functionality"""
        result = adverse_predictor.predict_adverse_events(sample_patient, sample_treatment)
        
        # Validate result structure
        assert 'overall_risk' in result
        assert 'specific_risks' in result
        assert 'risk_level' in result
        assert 'monitoring_recommendations' in result
        
        # Validate risk values
        assert 0 <= result['overall_risk'] <= 1
        assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
        
        # Validate specific risks
        specific_risks = result['specific_risks']
        for risk_type, risk_value in specific_risks.items():
            assert 0 <= risk_value <= 1
    
    def test_age_related_adverse_event_risk(self, adverse_predictor, sample_treatment):
        """Test age influences adverse event risk"""
        # Young patient
        young_patient = PatientProfile(
            patient_id="YOUNG_AE_001",
            age=30,
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        # Elderly patient
        elderly_patient = PatientProfile(
            patient_id="ELDERLY_AE_001",
            age=80,
            gender="male",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=[],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        young_result = adverse_predictor.predict_adverse_events(young_patient, sample_treatment)
        elderly_result = adverse_predictor.predict_adverse_events(elderly_patient, sample_treatment)
        
        # Elderly patient should have higher overall risk
        assert elderly_result['overall_risk'] >= young_result['overall_risk']
        
        # Elderly patient should have enhanced monitoring recommendations
        elderly_recommendations = ' '.join(elderly_result['monitoring_recommendations']).lower()
        assert 'elderly' in elderly_recommendations or 'enhanced' in elderly_recommendations
    
    def test_polypharmacy_interaction_risk(self, adverse_predictor, sample_treatment):
        """Test polypharmacy increases adverse event risk"""
        # Patient with few medications
        low_medication_patient = PatientProfile(
            patient_id="LOW_MED_001",
            age=50,
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=["ibuprofen"],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        # Patient with many medications
        high_medication_patient = PatientProfile(
            patient_id="HIGH_MED_001",
            age=50,
            gender="female",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain"],
            current_medications=["metformin", "lisinopril", "amlodipine", "gabapentin", "sertraline", "omeprazole", "metoprolol"],
            lifestyle_metrics={},
            pain_scores=[6.0],
            functional_assessments={}
        )
        
        low_result = adverse_predictor.predict_adverse_events(low_medication_patient, sample_treatment)
        high_result = adverse_predictor.predict_adverse_events(high_medication_patient, sample_treatment)
        
        # High medication patient should have higher risk
        assert high_result['overall_risk'] > low_result['overall_risk']
        
        # Should include interaction monitoring recommendation
        high_recommendations = ' '.join(high_result['monitoring_recommendations']).lower()
        assert 'interaction' in high_recommendations or 'medications' in high_recommendations
    
    def test_treatment_specific_risks(self, adverse_predictor, sample_patient):
        """Test treatment-specific adverse event risks"""
        # High-risk treatment (simulated opioid)
        high_risk_treatment = TreatmentPlan(
            treatment_id="HIGH_RISK_001",
            treatment_type="pharmacological",
            medications=["opioid_medication"],
            dosages={"opioid_medication": "test_dose"},
            duration_weeks=4,
            lifestyle_interventions=[]
        )
        
        # Lower-risk treatment
        low_risk_treatment = TreatmentPlan(
            treatment_id="LOW_RISK_001",
            treatment_type="behavioral",
            medications=[],
            dosages={},
            duration_weeks=12,
            lifestyle_interventions=["cognitive_behavioral_therapy"]
        )
        
        high_risk_result = adverse_predictor.predict_adverse_events(sample_patient, high_risk_treatment)
        low_risk_result = adverse_predictor.predict_adverse_events(sample_patient, low_risk_treatment)
        
        # High-risk treatment should have higher overall risk
        assert high_risk_result['overall_risk'] > low_risk_result['overall_risk']
    
    def test_risk_level_categorization(self, adverse_predictor):
        """Test risk level categorization logic"""
        # Test the private method through different risk scenarios
        assert adverse_predictor._categorize_risk(0.05) == 'LOW'
        assert adverse_predictor._categorize_risk(0.25) == 'MEDIUM'
        assert adverse_predictor._categorize_risk(0.45) == 'HIGH'
        assert adverse_predictor._categorize_risk(0.75) == 'VERY_HIGH'
    
    def test_monitoring_recommendations_generation(self, adverse_predictor, sample_treatment):
        """Test monitoring recommendations are generated appropriately"""
        # High-risk elderly patient with polypharmacy
        high_risk_patient = PatientProfile(
            patient_id="HIGH_RISK_MON_001",
            age=75,
            gender="male",
            genomics_data={},
            biomarkers={},
            medical_history=["chronic_pain", "diabetes", "hypertension", "heart_disease"],
            current_medications=["metformin", "insulin", "lisinopril", "metoprolol", "aspirin", "gabapentin"],
            lifestyle_metrics={},
            pain_scores=[8.0],
            functional_assessments={}
        )
        
        result = adverse_predictor.predict_adverse_events(high_risk_patient, sample_treatment)
        
        recommendations = result['monitoring_recommendations']
        assert len(recommendations) > 0
        
        # Should include multiple types of monitoring
        recommendations_text = ' '.join(recommendations).lower()
        expected_terms = ['monitor', 'elderly', 'medications', 'specialist']
        
        # At least some monitoring terms should be present
        found_terms = sum(1 for term in expected_terms if term in recommendations_text)
        assert found_terms >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 