from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult, RiskAssessment, ReadmissionRisk, SepsisRisk, DeteriorationRisk, MedicationPlan, ProgressionPrediction
from config.settings import settings
import logging
from typing import Dict, List, Optional, Union
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import json

class BasePredictor:
    """Base class for all predictors"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.model_version = "1.0.0"
    
    def _validate_input(self, patient: PatientProfile) -> bool:
        """Validate input data"""
        if not patient or not patient.patient_id:
            self.logger.error("Invalid patient data")
            return False
        return True
    
    def _prepare_features(self, patient: PatientProfile, additional_data: Optional[Dict] = None) -> np.ndarray:
        """Prepare feature vector for prediction"""
        raise NotImplementedError("Subclasses must implement _prepare_features")
    
    def _calculate_confidence_interval(self, prediction: float, std_dev: float = 0.1) -> tuple:
        """Calculate confidence interval for prediction"""
        return (max(0, prediction - 1.96 * std_dev), min(1, prediction + 1.96 * std_dev))

class TreatmentResponsePredictor(BasePredictor):
    """Base treatment response predictor"""
    
    def predict_treatment_response(self, patient: PatientProfile, treatment: TreatmentPlan) -> PredictionResult:
        """Base prediction method"""
        if not self._validate_input(patient):
            return PredictionResult(
                patient_id=patient.patient_id,
                treatment_id=treatment.treatment_id,
                success_probability=0.0,
                risk_score=1.0,
                key_factors=["Invalid input data"],
                warnings=["Invalid patient data"],
                timestamp=datetime.now()
            )
        
        features = self._prepare_features(patient)
        success_prob = self._predict_success_probability(features)
        risk_score = self._predict_risk_score(features)
        
        return PredictionResult(
            patient_id=patient.patient_id,
            treatment_id=treatment.treatment_id,
            success_probability=success_prob,
            risk_score=risk_score,
            key_factors=self._get_key_factors(features),
            warnings=self._generate_warnings(patient, success_prob, risk_score),
            timestamp=datetime.now(),
            confidence_interval=self._calculate_confidence_interval(success_prob),
            feature_importance=self.feature_importance,
            model_version=self.model_version
        )
    
    def _predict_success_probability(self, features: np.ndarray) -> float:
        """Predict treatment success probability"""
        if self.model is None:
            return 0.5  # Default if model not trained
        return float(self.model.predict_proba(features)[0][1])
    
    def _predict_risk_score(self, features: np.ndarray) -> float:
        """Predict risk score"""
        if self.model is None:
            return 0.5  # Default if model not trained
        return 1 - self._predict_success_probability(features)
    
    def _get_key_factors(self, features: np.ndarray) -> List[str]:
        """Get key factors influencing prediction"""
        return list(self.feature_importance.keys())
    
    def _generate_warnings(self, patient: PatientProfile, success_prob: float, risk_score: float) -> List[str]:
        """Generate warnings based on prediction"""
        warnings = []
        if success_prob < 0.3:
            warnings.append("LOW SUCCESS PROBABILITY: Consider alternative treatments")
        if risk_score > 0.7:
            warnings.append("HIGH RISK: Close monitoring recommended")
        if patient.age > 65:
            warnings.append("ELDERLY PATIENT: Monitor for increased side effects")
        if len(patient.current_medications) > 3:
            warnings.append("POLYPHARMACY RISK: Check for drug interactions")
        return warnings

class CardiovascularRiskPredictor(BasePredictor):
    """Cardiovascular risk assessment predictor"""
    
    def predict_cardiovascular_risk(self, patient: PatientProfile, realtime_data: Dict) -> RiskAssessment:
        """Predict cardiovascular risk"""
        if not self._validate_input(patient):
            return RiskAssessment(
                patient_id=patient.patient_id,
                risk_score=1.0,
                risk_category="Unknown",
                key_factors=["Invalid input data"],
                warnings=["Invalid patient data"],
                timestamp=datetime.now()
            )
        
        features = self._prepare_features(patient, realtime_data)
        risk_score = self._predict_risk_score(features)
        risk_category = self._categorize_risk(risk_score)
        
        return RiskAssessment(
            patient_id=patient.patient_id,
            risk_score=risk_score,
            risk_category=risk_category,
            key_factors=self._get_key_factors(features),
            warnings=self._generate_warnings(patient, risk_score),
            timestamp=datetime.now(),
            confidence_interval=self._calculate_confidence_interval(risk_score),
            feature_importance=self.feature_importance,
            model_version=self.model_version
        )
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score < 0.2:
            return "Low"
        elif risk_score < 0.4:
            return "Moderate"
        elif risk_score < 0.6:
            return "High"
        else:
            return "Very High"
    
    def _prepare_features(self, patient: PatientProfile, realtime_data: Dict) -> np.ndarray:
        """Prepare features for cardiovascular risk prediction"""
        features = []
        
        # Demographics
        features.extend([
            patient.age / 100.0,  # Normalized age
            1.0 if patient.gender == 'female' else 0.0
        ])
        
        # Vital signs
        if realtime_data and 'vitals' in realtime_data:
            vitals = realtime_data['vitals']
            features.extend([
                vitals.get('systolic_bp', 120) / 200.0,  # Normalized
                vitals.get('diastolic_bp', 80) / 120.0,
                vitals.get('heart_rate', 70) / 200.0,
                vitals.get('oxygen_saturation', 98) / 100.0
            ])
        
        # Lab results
        if realtime_data and 'labs' in realtime_data:
            labs = realtime_data['labs']
            features.extend([
                labs.get('cholesterol', 200) / 300.0,
                labs.get('hdl', 50) / 100.0,
                labs.get('ldl', 100) / 200.0,
                labs.get('triglycerides', 150) / 300.0
            ])
        
        # Lifestyle factors
        if patient.lifestyle_metrics:
            features.extend([
                patient.lifestyle_metrics.get('smoking_status', 0),
                patient.lifestyle_metrics.get('physical_activity', 0) / 10.0,
                patient.lifestyle_metrics.get('bmi', 25) / 50.0
            ])
        
        return np.array(features).reshape(1, -1)

class ReadmissionRiskPredictor(BasePredictor):
    """Readmission risk prediction"""
    
    def predict_readmission_risk(self, patient: PatientProfile, 
                               discharge_data: Dict) -> ReadmissionRisk:
        """Predict readmission risk"""
        if not self._validate_input(patient):
            return ReadmissionRisk(
                patient_id=patient.patient_id,
                risk_30d=1.0,
                risk_60d=1.0,
                risk_90d=1.0,
                key_factors=["Invalid input data"],
                warnings=["Invalid patient data"],
                timestamp=datetime.now()
            )
        
        features = self._prepare_features(patient, discharge_data)
        risk_30d = self._predict_risk_score(features, days=30)
        risk_60d = self._predict_risk_score(features, days=60)
        risk_90d = self._predict_risk_score(features, days=90)
        
        return ReadmissionRisk(
            patient_id=patient.patient_id,
            risk_30d=risk_30d,
            risk_60d=risk_60d,
            risk_90d=risk_90d,
            key_factors=self._get_key_factors(features),
            warnings=self._generate_warnings(patient, max(risk_30d, risk_60d, risk_90d)),
            timestamp=datetime.now(),
            confidence_interval=self._calculate_confidence_interval(risk_30d),
            feature_importance=self.feature_importance,
            model_version=self.model_version
        )
    
    def _predict_risk_score(self, features: np.ndarray, days: int) -> float:
        """Predict risk score for specific time period"""
        if self.model is None:
            return 0.5  # Default if model not trained
        base_prob = float(self.model.predict_proba(features)[0][1])
        # Adjust probability based on time period
        if days == 30:
            return base_prob
        elif days == 60:
            return min(1.0, base_prob * 1.2)
        else:  # 90 days
            return min(1.0, base_prob * 1.4)
    
    def _prepare_features(self, patient: PatientProfile, discharge_data: Dict) -> np.ndarray:
        """Prepare features for readmission risk prediction"""
        features = []
        
        # Clinical factors
        features.extend([
            len(patient.medical_history) / 10.0,  # Normalized
            len(patient.current_medications) / 10.0,
            patient.age / 100.0
        ])
        
        # Discharge factors
        if discharge_data:
            features.extend([
                discharge_data.get('length_of_stay', 5) / 30.0,
                discharge_data.get('discharge_complexity', 0) / 10.0,
                discharge_data.get('follow_up_scheduled', 1)
            ])
        
        # Social determinants
        if patient.social_determinants:
            features.extend([
                patient.social_determinants.get('housing_stability', 1) / 10.0,
                patient.social_determinants.get('social_support', 1) / 10.0,
                patient.social_determinants.get('transportation_access', 1) / 10.0
            ])
        
        return np.array(features).reshape(1, -1)

class EarlyWarningSystem(BasePredictor):
    """Early warning system for clinical deterioration"""
    
    def detect_sepsis_risk(self, patient: PatientProfile, 
                          realtime_data: Dict) -> SepsisRisk:
        """Detect sepsis risk"""
        if not self._validate_input(patient):
            return SepsisRisk(
                patient_id=patient.patient_id,
                risk_score=1.0,
                sirs_criteria_met=0,
                key_factors=["Invalid input data"],
                warnings=["Invalid patient data"],
                timestamp=datetime.now()
            )
        
        features = self._prepare_features(patient, realtime_data)
        risk_score = self._predict_risk_score(features)
        sirs_criteria = self._check_sirs_criteria(realtime_data)
        
        return SepsisRisk(
            patient_id=patient.patient_id,
            risk_score=risk_score,
            sirs_criteria_met=sirs_criteria,
            key_factors=self._get_key_factors(features),
            warnings=self._generate_warnings(patient, risk_score, sirs_criteria),
            timestamp=datetime.now(),
            confidence_interval=self._calculate_confidence_interval(risk_score),
            feature_importance=self.feature_importance,
            model_version=self.model_version
        )
    
    def predict_clinical_deterioration(self, patient: PatientProfile,
                                     realtime_data: Dict) -> DeteriorationRisk:
        """Predict clinical deterioration"""
        if not self._validate_input(patient):
            return DeteriorationRisk(
                patient_id=patient.patient_id,
                mews_score=0,
                icu_transfer_probability=0.0,
                key_factors=["Invalid input data"],
                warnings=["Invalid patient data"],
                timestamp=datetime.now()
            )
        
        features = self._prepare_features(patient, realtime_data)
        mews_score = self._calculate_mews_score(realtime_data)
        icu_prob = self._predict_icu_transfer_probability(features)
        
        return DeteriorationRisk(
            patient_id=patient.patient_id,
            mews_score=mews_score,
            icu_transfer_probability=icu_prob,
            key_factors=self._get_key_factors(features),
            warnings=self._generate_warnings(patient, icu_prob, mews_score),
            timestamp=datetime.now(),
            confidence_interval=self._calculate_confidence_interval(icu_prob),
            feature_importance=self.feature_importance,
            model_version=self.model_version
        )
    
    def _check_sirs_criteria(self, realtime_data: Dict) -> int:
        """Check SIRS criteria"""
        criteria_met = 0
        if realtime_data and 'vitals' in realtime_data:
            vitals = realtime_data['vitals']
            # Temperature
            if vitals.get('temperature', 37) > 38 or vitals.get('temperature', 37) < 36:
                criteria_met += 1
            # Heart rate
            if vitals.get('heart_rate', 70) > 90:
                criteria_met += 1
            # Respiratory rate
            if vitals.get('respiratory_rate', 16) > 20:
                criteria_met += 1
            # WBC
            if realtime_data.get('labs', {}).get('wbc', 7000) > 12000 or realtime_data.get('labs', {}).get('wbc', 7000) < 4000:
                criteria_met += 1
        return criteria_met
    
    def _calculate_mews_score(self, realtime_data: Dict) -> int:
        """Calculate Modified Early Warning Score"""
        score = 0
        if realtime_data and 'vitals' in realtime_data:
            vitals = realtime_data['vitals']
            # Systolic BP
            sbp = vitals.get('systolic_bp', 120)
            if sbp <= 70: score += 3
            elif sbp <= 80: score += 2
            elif sbp <= 100: score += 1
            elif sbp >= 200: score += 2
            # Heart rate
            hr = vitals.get('heart_rate', 70)
            if hr <= 40: score += 3
            elif hr <= 50: score += 1
            elif hr >= 100: score += 1
            elif hr >= 110: score += 2
            elif hr >= 130: score += 3
            # Respiratory rate
            rr = vitals.get('respiratory_rate', 16)
            if rr <= 8: score += 2
            elif rr <= 14: score += 0
            elif rr <= 20: score += 1
            elif rr <= 29: score += 2
            else: score += 3
            # Temperature
            temp = vitals.get('temperature', 37)
            if temp <= 35: score += 2
            elif temp <= 36: score += 1
            elif temp <= 38: score += 0
            elif temp <= 38.5: score += 1
            else: score += 2
            # AVPU
            avpu = vitals.get('avpu', 'A')
            if avpu == 'A': score += 0
            elif avpu == 'V': score += 3
            elif avpu == 'P': score += 3
            elif avpu == 'U': score += 3
        return score
    
    def _predict_icu_transfer_probability(self, features: np.ndarray) -> float:
        """Predict probability of ICU transfer"""
        if self.model is None:
            return 0.5  # Default if model not trained
        return float(self.model.predict_proba(features)[0][1])
    
    def _prepare_features(self, patient: PatientProfile, realtime_data: Dict) -> np.ndarray:
        """Prepare features for early warning prediction"""
        features = []
        
        # Vital signs
        if realtime_data and 'vitals' in realtime_data:
            vitals = realtime_data['vitals']
            features.extend([
                vitals.get('systolic_bp', 120) / 200.0,
                vitals.get('diastolic_bp', 80) / 120.0,
                vitals.get('heart_rate', 70) / 200.0,
                vitals.get('respiratory_rate', 16) / 40.0,
                vitals.get('temperature', 37) / 42.0,
                vitals.get('oxygen_saturation', 98) / 100.0
            ])
        
        # Lab values
        if realtime_data and 'labs' in realtime_data:
            labs = realtime_data['labs']
            features.extend([
                labs.get('wbc', 7000) / 20000.0,
                labs.get('lactate', 2) / 10.0,
                labs.get('creatinine', 1) / 5.0
            ])
        
        # Patient factors
        features.extend([
            patient.age / 100.0,
            len(patient.medical_history) / 10.0,
            len(patient.current_medications) / 10.0
        ])
        
        return np.array(features).reshape(1, -1)

class TreatmentOptimizer(BasePredictor):
    """Treatment optimization predictor"""
    
    def optimize_medication(self, patient: PatientProfile,
                          medication: Dict) -> MedicationPlan:
        """Optimize medication plan"""
        if not self._validate_input(patient):
            return MedicationPlan(
                patient_id=patient.patient_id,
                medication_id=medication.get('id', ''),
                recommended_dose=0.0,
                dosing_schedule=[],
                warnings=["Invalid patient data"],
                timestamp=datetime.now()
            )
        
        features = self._prepare_features(patient, medication)
        optimal_dose = self._predict_optimal_dose(features)
        schedule = self._generate_dosing_schedule(optimal_dose, medication)
        
        return MedicationPlan(
            patient_id=patient.patient_id,
            medication_id=medication.get('id', ''),
            recommended_dose=optimal_dose,
            dosing_schedule=schedule,
            warnings=self._generate_warnings(patient, optimal_dose),
            timestamp=datetime.now(),
            confidence_interval=self._calculate_confidence_interval(optimal_dose),
            feature_importance=self.feature_importance,
            model_version=self.model_version
        )
    
    def predict_disease_progression(self, patient: PatientProfile,
                                  condition: str) -> ProgressionPrediction:
        """Predict disease progression"""
        if not self._validate_input(patient):
            return ProgressionPrediction(
                patient_id=patient.patient_id,
                condition=condition,
                progression_score=0.0,
                key_factors=["Invalid input data"],
                warnings=["Invalid patient data"],
                timestamp=datetime.now()
            )
        
        features = self._prepare_features(patient, {'condition': condition})
        progression_score = self._predict_progression_score(features)
        
        return ProgressionPrediction(
            patient_id=patient.patient_id,
            condition=condition,
            progression_score=progression_score,
            key_factors=self._get_key_factors(features),
            warnings=self._generate_warnings(patient, progression_score),
            timestamp=datetime.now(),
            confidence_interval=self._calculate_confidence_interval(progression_score),
            feature_importance=self.feature_importance,
            model_version=self.model_version
        )
    
    def _predict_optimal_dose(self, features: np.ndarray) -> float:
        """Predict optimal medication dose"""
        if self.model is None:
            return 0.0  # Default if model not trained
        return float(self.model.predict(features)[0])
    
    def _generate_dosing_schedule(self, optimal_dose: float, medication: Dict) -> List[Dict]:
        """Generate dosing schedule"""
        frequency = medication.get('frequency', 'daily')
        schedule = []
        
        if frequency == 'daily':
            schedule.append({
                'time': '08:00',
                'dose': optimal_dose
            })
        elif frequency == 'bid':
            schedule.extend([
                {'time': '08:00', 'dose': optimal_dose},
                {'time': '20:00', 'dose': optimal_dose}
            ])
        elif frequency == 'tid':
            schedule.extend([
                {'time': '08:00', 'dose': optimal_dose},
                {'time': '14:00', 'dose': optimal_dose},
                {'time': '20:00', 'dose': optimal_dose}
            ])
        
        return schedule
    
    def _predict_progression_score(self, features: np.ndarray) -> float:
        """Predict disease progression score"""
        if self.model is None:
            return 0.5  # Default if model not trained
        return float(self.model.predict_proba(features)[0][1])
    
    def _prepare_features(self, patient: PatientProfile, additional_data: Dict) -> np.ndarray:
        """Prepare features for treatment optimization"""
        features = []
        
        # Patient factors
        features.extend([
            patient.age / 100.0,
            len(patient.medical_history) / 10.0,
            len(patient.current_medications) / 10.0
        ])
        
        # Condition-specific features
        condition = additional_data.get('condition', '')
        if condition == 'diabetes':
            if patient.biomarkers:
                features.extend([
                    patient.biomarkers.get('hba1c', 7) / 15.0,
                    patient.biomarkers.get('fasting_glucose', 100) / 300.0
                ])
        elif condition == 'hypertension':
            if patient.biomarkers:
                features.extend([
                    patient.biomarkers.get('systolic_bp', 120) / 200.0,
                    patient.biomarkers.get('diastolic_bp', 80) / 120.0
                ])
        elif condition == 'asthma':
            if patient.biomarkers:
                features.extend([
                    patient.biomarkers.get('fev1', 80) / 100.0,
                    patient.biomarkers.get('peak_flow', 400) / 800.0
                ])
        
        return np.array(features).reshape(1, -1)

# Create instances of predictors
treatment_predictor = TreatmentResponsePredictor()
cardiovascular_predictor = CardiovascularRiskPredictor()
readmission_predictor = ReadmissionRiskPredictor()
early_warning_system = EarlyWarningSystem()
treatment_optimizer = TreatmentOptimizer()