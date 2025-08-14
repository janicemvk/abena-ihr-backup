# Predictive analytics engine for the ML Feedback Pipeline
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator
import logging

from src.core.data_models import PatientProfile, TreatmentPlan, PredictionResult
from datetime import datetime

class TreatmentResponsePredictor:
    """Predicts treatment response probability"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def _extract_features(self, patient: PatientProfile, treatment: TreatmentPlan) -> np.ndarray:
        """Extract features from patient and treatment data"""
        features = []
        
        # Patient features
        features.extend([
            patient.age,
            len(patient.medical_history),
            len(patient.current_medications),
            np.mean(patient.pain_scores) if patient.pain_scores else 0,
            np.mean(list(patient.functional_assessments.values())) if patient.functional_assessments else 0
        ])
        
        # Treatment features
        features.extend([
            treatment.duration_weeks,
            len(treatment.medications),
            len(treatment.lifestyle_interventions)
        ])
        
        # Convert to numpy array
        return np.array(features).reshape(1, -1)
    
    def train_models(self, training_data: List[Tuple[PatientProfile, TreatmentPlan, float]]):
        """Train the prediction models"""
        if not training_data:
            self.logger.warning("No training data provided")
            return
        
        # Extract features and outcomes
        X = []
        y = []
        
        for patient, treatment, outcome in training_data:
            features = self._extract_features(patient, treatment)
            X.append(features.flatten())
            y.append(1 if outcome > 0.6 else 0)  # Binary classification
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train multiple models
        self.models['random_forest'] = RandomForestClassifier(n_estimators=100, random_state=42)
        self.models['gradient_boosting'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.models['logistic_regression'] = LogisticRegression(random_state=42)
        
        for name, model in self.models.items():
            try:
                if name == 'gradient_boosting':
                    # For regression, use outcome directly
                    y_reg = [outcome for _, _, outcome in training_data]
                    model.fit(X_scaled, y_reg)
                else:
                    # For classification, use binary outcome
                    model.fit(X_scaled, y)
                self.logger.info(f"Trained {name} model")
            except Exception as e:
                self.logger.error(f"Failed to train {name} model: {e}")
        
        self.is_trained = True
    
    def _train_with_params(self, training_data: List[Tuple], params: Dict):
        """Train models with specific parameters (for optimization)"""
        if not training_data:
            return
        
        # Extract features and outcomes
        X = []
        y = []
        
        for patient, treatment, outcome in training_data:
            features = self._extract_features(patient, treatment)
            X.append(features.flatten())
            y.append(1 if outcome > 0.6 else 0)
        
        X = np.array(X)
        y = np.array(y)
        X_scaled = self.scaler.fit_transform(X)
        
        # Train with provided parameters
        if 'random_forest' in params:
            rf_params = params['random_forest']
            self.models['random_forest'] = RandomForestClassifier(**rf_params, random_state=42)
            self.models['random_forest'].fit(X_scaled, y)
        
        if 'gradient_boosting' in params:
            gb_params = params['gradient_boosting']
            self.models['gradient_boosting'] = GradientBoostingRegressor(**gb_params, random_state=42)
            y_reg = [outcome for _, _, outcome in training_data]
            self.models['gradient_boosting'].fit(X_scaled, y_reg)
        
        self.is_trained = True
    
    def predict_treatment_response(self, patient: PatientProfile, treatment: TreatmentPlan) -> PredictionResult:
        """Predict treatment response probability"""
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        # Extract features
        features = self._extract_features(patient, treatment)
        features_scaled = self.scaler.transform(features)
        
        # Get predictions from all models
        predictions = {}
        
        if 'random_forest' in self.models:
            predictions['random_forest'] = self.models['random_forest'].predict_proba(features_scaled)[0][1]
        
        if 'gradient_boosting' in self.models:
            pred = self.models['gradient_boosting'].predict(features_scaled)[0]
            predictions['gradient_boosting'] = max(0, min(1, pred))  # Clamp to [0,1]
        
        if 'logistic_regression' in self.models:
            predictions['logistic_regression'] = self.models['logistic_regression'].predict_proba(features_scaled)[0][1]
        
        # Ensemble prediction (average)
        if predictions:
            success_probability = np.mean(list(predictions.values()))
        else:
            success_probability = 0.5  # Default probability
        
        # Calculate confidence based on model agreement
        if len(predictions) > 1:
            confidence_score = 1.0 - np.std(list(predictions.values()))
        else:
            confidence_score = 0.7  # Default confidence
        
        # Generate warnings and recommendations
        warnings = []
        recommendations = []
        
        if success_probability < 0.3:
            warnings.append("Low predicted success probability")
            recommendations.append("Consider alternative treatment options")
        elif success_probability > 0.8:
            recommendations.append("High predicted success - proceed with treatment")
        
        if confidence_score < 0.5:
            warnings.append("Low prediction confidence")
            recommendations.append("Consider additional patient assessment")
        
        return PredictionResult(
            patient_id=patient.patient_id,
            treatment_id=treatment.treatment_id,
            success_probability=success_probability,
            confidence_score=confidence_score,
            warnings=warnings,
            recommendations=recommendations,
            timestamp=datetime.now(),
            model_version="v1.0",
            additional_metrics={'model_predictions': predictions}
        )

class AdverseEventPredictor:
    """Predicts adverse event risks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def _extract_risk_features(self, patient: PatientProfile, treatment: TreatmentPlan) -> np.ndarray:
        """Extract features for adverse event risk prediction"""
        features = []
        
        # Patient risk factors
        features.extend([
            patient.age,
            len(patient.medical_history),
            len(patient.current_medications),
            len([med for med in patient.current_medications if 'opioid' in med.lower()]),
            len([med for med in patient.current_medications if 'anticoagulant' in med.lower()])
        ])
        
        # Treatment risk factors
        features.extend([
            treatment.duration_weeks,
            len(treatment.medications),
            sum(treatment.dosages.values()) if treatment.dosages else 0
        ])
        
        return np.array(features).reshape(1, -1)
    
    def train_risk_model(self, training_data: List[Tuple[PatientProfile, TreatmentPlan, List[str]]]):
        """Train the adverse event risk model"""
        if not training_data:
            self.logger.warning("No training data provided for risk model")
            return
        
        X = []
        y = []
        
        for patient, treatment, adverse_events in training_data:
            features = self._extract_risk_features(patient, treatment)
            X.append(features.flatten())
            y.append(1 if adverse_events else 0)  # Binary: any adverse events
        
        X = np.array(X)
        y = np.array(y)
        X_scaled = self.scaler.fit_transform(X)
        
        self.risk_model.fit(X_scaled, y)
        self.is_trained = True
        self.logger.info("Trained adverse event risk model")
    
    def assess_adverse_event_risk(self, patient: PatientProfile, treatment: TreatmentPlan) -> Dict[str, Any]:
        """Assess risk of adverse events"""
        if not self.is_trained:
            raise ValueError("Risk model must be trained before assessment")
        
        features = self._extract_risk_features(patient, treatment)
        features_scaled = self.scaler.transform(features)
        
        # Get risk probability
        risk_probability = self.risk_model.predict_proba(features_scaled)[0][1]
        
        # Calculate overall risk score
        overall_risk_score = risk_probability
        
        # Risk categories
        if overall_risk_score < 0.2:
            risk_level = "low"
        elif overall_risk_score < 0.5:
            risk_level = "moderate"
        else:
            risk_level = "high"
        
        # Generate risk-specific recommendations
        recommendations = []
        if risk_level == "high":
            recommendations.extend([
                "Enhanced monitoring recommended",
                "Consider dose reduction",
                "Monitor for early warning signs"
            ])
        elif risk_level == "moderate":
            recommendations.extend([
                "Standard monitoring protocol",
                "Watch for adverse reactions"
            ])
        else:
            recommendations.append("Standard care protocol")
        
        return {
            'overall_risk_score': overall_risk_score,
            'risk_level': risk_level,
            'risk_probability': risk_probability,
            'recommendations': recommendations,
            'risk_factors': {
                'age_risk': patient.age > 65,
                'polypharmacy_risk': len(patient.current_medications) > 5,
                'high_dose_risk': sum(treatment.dosages.values()) > 100 if treatment.dosages else False
            }
        } 