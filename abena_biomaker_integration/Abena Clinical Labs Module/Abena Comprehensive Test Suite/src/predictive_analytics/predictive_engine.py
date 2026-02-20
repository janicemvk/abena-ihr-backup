# Mock predictive engine for testing - Updated to use Abena SDK
import numpy as np
from datetime import datetime
from typing import List, Tuple, Dict, Any
from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult
import hashlib
from sklearn.base import BaseEstimator
from src.core.abena_sdk import AbenaSDK

class DeterministicPredictor(BaseEstimator):
    def fit(self, X, y):
        self.y_fit = np.array(y)
        return self
    def predict(self, X):
        # Repeat the fit labels as needed to match the number of predictions
        reps = int(np.ceil(X.shape[0] / len(self.y_fit)))
        return np.tile(self.y_fit, reps)[:X.shape[0]]

class TreatmentResponsePredictor:
    def __init__(self, abena_sdk: AbenaSDK):
        self.abena = abena_sdk
        self.is_trained = False
        self.models = {}
        self.scalers = {}
    
    def prepare_features(self, patient: PatientProfile, treatment: TreatmentPlan) -> np.ndarray:
        # Deterministic feature vector based on patient_id and treatment_id
        key = f"{patient.patient_id}-{treatment.treatment_id}"
        h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        np.random.seed(h % (2**32))
        return np.random.rand(1, 22)
    
    def train_models(self, training_data: List[Tuple[PatientProfile, TreatmentPlan, float]]):
        self.is_trained = True
        self.models = {
            'random_forest': DeterministicPredictor(),
            'gradient_boosting': DeterministicPredictor(),
            'logistic_regression': DeterministicPredictor()
        }
        self.scalers = {'response': MockScaler()}
    
    async def predict_treatment_response(self, patient_id: str, treatment: TreatmentPlan) -> PredictionResult:
        if not self.is_trained:
            raise ValueError("Models must be trained")
        
        # Use Abena SDK to get patient data
        patient_data = await self.abena.get_patient_data(patient_id, 'treatment_prediction')
        
        # Deterministic probability based on patient_id and treatment_id
        key = f"{patient_id}-{treatment.treatment_id}"
        h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        base_prob = 0.7 if h % 10 < 7 else 0.2  # 70% of cases are high prob, 30% low
        success_probability = base_prob
        risk_score = 1.0 - success_probability
        
        return PredictionResult(
            patient_id=patient_id,
            treatment_id=treatment.treatment_id,
            success_probability=success_probability,
            risk_score=risk_score,
            key_factors=["Test factor"],
            warnings=["Test warning"],
            timestamp=datetime.now()
        )

class AdverseEventPredictor:
    def __init__(self, abena_sdk: AbenaSDK):
        self.abena = abena_sdk
    
    def _prepare_adverse_event_features(self, patient: PatientProfile, treatment: TreatmentPlan) -> np.ndarray:
        """Mock adverse event feature preparation"""
        return np.random.rand(1, 12)
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Mock risk categorization"""
        if risk_score >= 0.7:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MODERATE'
        elif risk_score >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _calculate_overall_risk(self, risk_assessment: Dict[str, Dict[str, str]]) -> str:
        """Mock overall risk calculation"""
        high_count = sum(1 for event in risk_assessment.values() if event['risk_level'] == 'HIGH')
        if high_count >= 2:
            return 'CRITICAL'
        elif high_count >= 1:
            return 'HIGH'
        else:
            return 'MODERATE'
    
    async def _generate_warnings(self, patient_id: str, treatment: TreatmentPlan, success_probability: float) -> List[str]:
        """Mock warning generation using Abena SDK"""
        # Get patient data through Abena SDK
        patient_data = await self.abena.get_patient_data(patient_id, 'adverse_event_assessment')
        
        warnings = []
        
        if success_probability < 0.3:
            warnings.append("LOW SUCCESS PROBABILITY - Consider alternative treatment")
        
        # Mock age check based on patient data
        if 'age' in patient_data and patient_data['age'] > 70:
            warnings.append("ELDERLY PATIENT - Monitor for adverse effects")
        
        # Mock medication check
        if 'medications' in patient_data and len(patient_data['medications']) > 5:
            warnings.append("POLYPHARMACY - High risk of drug interactions")
        
        # Mock medical history check
        if 'medical_history' in patient_data and 'heart_disease' in patient_data['medical_history']:
            warnings.append("CARDIOVASCULAR RISK - Monitor cardiac function")
        
        return warnings

class PredictiveAnalyticsEngine:
    def __init__(self, abena_sdk: AbenaSDK):
        self.abena = abena_sdk
        self.treatment_predictor = TreatmentResponsePredictor(abena_sdk)
        self.adverse_event_predictor = AdverseEventPredictor(abena_sdk)
        self.logger = Mock()
    
    def initialize_models(self, training_data, adverse_event_data):
        """Mock model initialization"""
        self.treatment_predictor.train_models(training_data)
    
    async def generate_treatment_recommendation(self, patient_id: str, treatments: List[TreatmentPlan]) -> Dict[str, Any]:
        """Mock treatment recommendation generation using Abena SDK"""
        # Get patient data through Abena SDK
        patient_data = await self.abena.get_patient_data(patient_id, 'treatment_recommendation')
        
        return {
            'patient_id': patient_id,
            'recommended_treatment': treatments[0] if treatments else None,
            'alternative_treatments': treatments[1:] if len(treatments) > 1 else [],
            'clinical_decision_support': "Mock decision support"
        }

class MockScaler:
    """Mock scaler with transform method"""
    def transform(self, X):
        """Mock transform method"""
        return X  # Return as-is for testing

class Mock:
    """Simple mock class for testing"""
    pass 