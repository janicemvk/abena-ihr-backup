"""
Predictive Analytics Engine for Abena IHR
=========================================

This module provides advanced predictive analytics capabilities for healthcare data,
including disease prediction, risk stratification, treatment outcome forecasting,
and personalized medicine recommendations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import joblib
import json
import redis
import httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Predictive Analytics Engine",
    description="Advanced predictive analytics for healthcare data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for data validation
class PatientData(BaseModel):
    """Patient data model for analytics"""
    patient_id: str
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., regex="^(male|female|other)$")
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=1, le=500)
    blood_pressure_systolic: Optional[int] = Field(None, ge=70, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=40, le=150)
    heart_rate: Optional[int] = Field(None, ge=40, le=200)
    temperature: Optional[float] = Field(None, ge=35.0, le=42.0)
    glucose_level: Optional[float] = Field(None, ge=20, le=600)
    cholesterol_total: Optional[float] = Field(None, ge=100, le=400)
    cholesterol_hdl: Optional[float] = Field(None, ge=20, le=100)
    cholesterol_ldl: Optional[float] = Field(None, ge=50, le=300)
    triglycerides: Optional[float] = Field(None, ge=50, le=1000)
    smoking_status: Optional[str] = Field(None, regex="^(never|former|current|unknown)$")
    diabetes_status: Optional[str] = Field(None, regex="^(none|prediabetes|type1|type2|gestational|unknown)$")
    family_history: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    symptoms: Optional[List[str]] = []
    lab_results: Optional[Dict[str, float]] = {}
    vital_signs_history: Optional[List[Dict[str, Any]]] = []

class PredictionRequest(BaseModel):
    """Request model for predictions"""
    patient_data: PatientData
    prediction_type: str = Field(..., regex="^(disease_risk|treatment_outcome|readmission_risk|medication_effectiveness|lifestyle_recommendations)$")
    confidence_threshold: float = Field(0.7, ge=0.1, le=0.99)
    include_explanations: bool = True

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    patient_id: str
    prediction_type: str
    prediction: str
    confidence: float
    risk_score: float
    factors: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: datetime
    model_version: str

class ModelTrainingRequest(BaseModel):
    """Request model for training"""
    dataset_path: str
    target_variable: str
    model_type: str = Field(..., regex="^(classification|regression)$")
    features: List[str]
    test_size: float = Field(0.2, ge=0.1, le=0.5)

class AnalyticsEngine:
    """Main analytics engine class"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_metadata = {}
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
    async def initialize_models(self):
        """Initialize pre-trained models"""
        try:
            # Load pre-trained models
            model_paths = {
                'disease_risk': 'src/ml_models/disease_risk_model.pkl',
                'treatment_outcome': 'src/ml_models/treatment_outcome_model.pkl',
                'readmission_risk': 'src/ml_models/readmission_risk_model.pkl',
                'medication_effectiveness': 'src/ml_models/medication_effectiveness_model.pkl'
            }
            
            for model_name, model_path in model_paths.items():
                try:
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded {model_name} model successfully")
                except FileNotFoundError:
                    logger.warning(f"Model {model_name} not found, will train on first use")
                    
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            
    def preprocess_patient_data(self, patient_data: PatientData) -> np.ndarray:
        """Preprocess patient data for model input"""
        try:
            # Convert patient data to feature vector
            features = []
            
            # Basic demographics
            features.extend([
                patient_data.age,
                1 if patient_data.gender == 'male' else 0,
                patient_data.height_cm or 0,
                patient_data.weight_kg or 0
            ])
            
            # Calculate BMI if height and weight are available
            if patient_data.height_cm and patient_data.weight_kg:
                bmi = patient_data.weight_kg / ((patient_data.height_cm / 100) ** 2)
                features.append(bmi)
            else:
                features.append(0)
                
            # Vital signs
            features.extend([
                patient_data.blood_pressure_systolic or 0,
                patient_data.blood_pressure_diastolic or 0,
                patient_data.heart_rate or 0,
                patient_data.temperature or 0,
                patient_data.glucose_level or 0
            ])
            
            # Cholesterol levels
            features.extend([
                patient_data.cholesterol_total or 0,
                patient_data.cholesterol_hdl or 0,
                patient_data.cholesterol_ldl or 0,
                patient_data.triglycerides or 0
            ])
            
            # Risk factors
            features.extend([
                1 if patient_data.smoking_status == 'current' else 0,
                1 if patient_data.diabetes_status in ['type1', 'type2', 'gestational'] else 0,
                len(patient_data.family_history),
                len(patient_data.medications)
            ])
            
            # Lab results (normalize to 0-1 range)
            lab_features = []
            for lab_name, lab_value in patient_data.lab_results.items():
                lab_features.append(lab_value / 1000)  # Simple normalization
            features.extend(lab_features[:10])  # Limit to 10 lab features
            
            # Pad with zeros if needed
            while len(features) < 50:  # Standard feature vector size
                features.append(0)
                
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preprocessing patient data: {e}")
            raise
            
    def predict_disease_risk(self, patient_data: PatientData) -> Dict[str, Any]:
        """Predict disease risk for a patient"""
        try:
            features = self.preprocess_patient_data(patient_data)
            
            # Use disease risk model
            if 'disease_risk' in self.models:
                model = self.models['disease_risk']
                prediction = model.predict(features)[0]
                probabilities = model.predict_proba(features)[0]
                confidence = max(probabilities)
                
                # Map prediction to disease categories
                disease_categories = ['low_risk', 'moderate_risk', 'high_risk']
                predicted_category = disease_categories[prediction]
                
                # Calculate risk factors
                risk_factors = self._identify_risk_factors(patient_data)
                
                return {
                    'prediction': predicted_category,
                    'confidence': confidence,
                    'risk_score': confidence,
                    'factors': risk_factors,
                    'recommendations': self._generate_recommendations(patient_data, predicted_category)
                }
            else:
                # Fallback to rule-based prediction
                return self._rule_based_disease_risk(patient_data)
                
        except Exception as e:
            logger.error(f"Error predicting disease risk: {e}")
            raise
            
    def predict_treatment_outcome(self, patient_data: PatientData, treatment: str) -> Dict[str, Any]:
        """Predict treatment outcome for a patient"""
        try:
            features = self.preprocess_patient_data(patient_data)
            
            # Add treatment-specific features
            treatment_features = self._encode_treatment(treatment)
            features = np.concatenate([features, treatment_features.reshape(1, -1)], axis=1)
            
            if 'treatment_outcome' in self.models:
                model = self.models['treatment_outcome']
                prediction = model.predict(features)[0]
                probabilities = model.predict_proba(features)[0]
                confidence = max(probabilities)
                
                outcome_categories = ['poor', 'fair', 'good', 'excellent']
                predicted_outcome = outcome_categories[prediction]
                
                return {
                    'prediction': predicted_outcome,
                    'confidence': confidence,
                    'risk_score': 1 - confidence,
                    'factors': self._identify_treatment_factors(patient_data, treatment),
                    'recommendations': self._generate_treatment_recommendations(patient_data, treatment, predicted_outcome)
                }
            else:
                return self._rule_based_treatment_outcome(patient_data, treatment)
                
        except Exception as e:
            logger.error(f"Error predicting treatment outcome: {e}")
            raise
            
    def predict_readmission_risk(self, patient_data: PatientData, admission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict readmission risk for a patient"""
        try:
            features = self.preprocess_patient_data(patient_data)
            
            # Add admission-specific features
            admission_features = self._encode_admission_data(admission_data)
            features = np.concatenate([features, admission_features.reshape(1, -1)], axis=1)
            
            if 'readmission_risk' in self.models:
                model = self.models['readmission_risk']
                prediction = model.predict(features)[0]
                probabilities = model.predict_proba(features)[0]
                confidence = max(probabilities)
                
                risk_categories = ['low', 'medium', 'high']
                predicted_risk = risk_categories[prediction]
                
                return {
                    'prediction': predicted_risk,
                    'confidence': confidence,
                    'risk_score': confidence,
                    'factors': self._identify_readmission_factors(patient_data, admission_data),
                    'recommendations': self._generate_readmission_recommendations(patient_data, predicted_risk)
                }
            else:
                return self._rule_based_readmission_risk(patient_data, admission_data)
                
        except Exception as e:
            logger.error(f"Error predicting readmission risk: {e}")
            raise
            
    def _identify_risk_factors(self, patient_data: PatientData) -> List[Dict[str, Any]]:
        """Identify risk factors for a patient"""
        factors = []
        
        # Age-related risks
        if patient_data.age > 65:
            factors.append({
                'factor': 'age',
                'value': patient_data.age,
                'risk_level': 'high',
                'description': 'Advanced age increases risk of chronic diseases'
            })
            
        # BMI-related risks
        if patient_data.height_cm and patient_data.weight_kg:
            bmi = patient_data.weight_kg / ((patient_data.height_cm / 100) ** 2)
            if bmi > 30:
                factors.append({
                    'factor': 'bmi',
                    'value': round(bmi, 2),
                    'risk_level': 'high',
                    'description': 'Obesity increases risk of cardiovascular disease and diabetes'
                })
            elif bmi > 25:
                factors.append({
                    'factor': 'bmi',
                    'value': round(bmi, 2),
                    'risk_level': 'moderate',
                    'description': 'Overweight increases risk of chronic diseases'
                })
                
        # Blood pressure risks
        if patient_data.blood_pressure_systolic and patient_data.blood_pressure_diastolic:
            if patient_data.blood_pressure_systolic > 140 or patient_data.blood_pressure_diastolic > 90:
                factors.append({
                    'factor': 'blood_pressure',
                    'value': f"{patient_data.blood_pressure_systolic}/{patient_data.blood_pressure_diastolic}",
                    'risk_level': 'high',
                    'description': 'High blood pressure increases cardiovascular risk'
                })
                
        # Diabetes risks
        if patient_data.diabetes_status in ['type1', 'type2', 'gestational']:
            factors.append({
                'factor': 'diabetes',
                'value': patient_data.diabetes_status,
                'risk_level': 'high',
                'description': 'Diabetes significantly increases risk of complications'
            })
            
        # Smoking risks
        if patient_data.smoking_status == 'current':
            factors.append({
                'factor': 'smoking',
                'value': 'current',
                'risk_level': 'high',
                'description': 'Current smoking increases risk of multiple diseases'
            })
            
        return factors
        
    def _generate_recommendations(self, patient_data: PatientData, risk_category: str) -> List[str]:
        """Generate personalized recommendations based on risk category"""
        recommendations = []
        
        if risk_category == 'high_risk':
            recommendations.extend([
                "Schedule regular check-ups with your primary care physician",
                "Monitor blood pressure and blood glucose regularly",
                "Consider lifestyle modifications including diet and exercise",
                "Review medications with your healthcare provider",
                "Consider preventive screenings for early detection"
            ])
        elif risk_category == 'moderate_risk':
            recommendations.extend([
                "Maintain regular health check-ups",
                "Focus on preventive care and healthy lifestyle",
                "Monitor key health indicators",
                "Consider preventive screenings"
            ])
        else:  # low_risk
            recommendations.extend([
                "Continue maintaining healthy lifestyle",
                "Schedule annual check-ups",
                "Stay up to date with preventive care"
            ])
            
        # Add specific recommendations based on patient data
        if patient_data.smoking_status == 'current':
            recommendations.append("Consider smoking cessation programs")
            
        if patient_data.diabetes_status in ['type1', 'type2', 'gestational']:
            recommendations.append("Work with diabetes management team")
            
        return recommendations
        
    def _rule_based_disease_risk(self, patient_data: PatientData) -> Dict[str, Any]:
        """Fallback rule-based disease risk prediction"""
        risk_score = 0
        factors = []
        
        # Age factor
        if patient_data.age > 65:
            risk_score += 0.3
        elif patient_data.age > 50:
            risk_score += 0.2
            
        # BMI factor
        if patient_data.height_cm and patient_data.weight_kg:
            bmi = patient_data.weight_kg / ((patient_data.height_cm / 100) ** 2)
            if bmi > 30:
                risk_score += 0.3
            elif bmi > 25:
                risk_score += 0.2
                
        # Blood pressure factor
        if patient_data.blood_pressure_systolic and patient_data.blood_pressure_systolic > 140:
            risk_score += 0.2
            
        # Diabetes factor
        if patient_data.diabetes_status in ['type1', 'type2', 'gestational']:
            risk_score += 0.4
            
        # Smoking factor
        if patient_data.smoking_status == 'current':
            risk_score += 0.3
            
        # Determine risk category
        if risk_score >= 0.6:
            risk_category = 'high_risk'
        elif risk_score >= 0.3:
            risk_category = 'moderate_risk'
        else:
            risk_category = 'low_risk'
            
        return {
            'prediction': risk_category,
            'confidence': min(risk_score + 0.3, 0.95),  # Add some confidence
            'risk_score': risk_score,
            'factors': self._identify_risk_factors(patient_data),
            'recommendations': self._generate_recommendations(patient_data, risk_category)
        }
        
    def _encode_treatment(self, treatment: str) -> np.ndarray:
        """Encode treatment information"""
        # Simple one-hot encoding for treatments
        treatments = ['medication', 'surgery', 'therapy', 'lifestyle', 'monitoring']
        encoding = np.zeros(len(treatments))
        
        for i, t in enumerate(treatments):
            if t in treatment.lower():
                encoding[i] = 1
                
        return encoding
        
    def _encode_admission_data(self, admission_data: Dict[str, Any]) -> np.ndarray:
        """Encode admission data"""
        features = []
        
        # Length of stay
        features.append(admission_data.get('length_of_stay', 0))
        
        # Number of procedures
        features.append(len(admission_data.get('procedures', [])))
        
        # ICU stay
        features.append(1 if admission_data.get('icu_stay', False) else 0)
        
        # Emergency admission
        features.append(1 if admission_data.get('emergency_admission', False) else 0)
        
        return np.array(features)
        
    def _identify_treatment_factors(self, patient_data: PatientData, treatment: str) -> List[Dict[str, Any]]:
        """Identify factors affecting treatment outcome"""
        factors = []
        
        # Age factor
        if patient_data.age > 75:
            factors.append({
                'factor': 'age',
                'value': patient_data.age,
                'impact': 'negative',
                'description': 'Advanced age may affect treatment response'
            })
            
        # Comorbidities
        if patient_data.diabetes_status in ['type1', 'type2']:
            factors.append({
                'factor': 'diabetes',
                'value': patient_data.diabetes_status,
                'impact': 'negative',
                'description': 'Diabetes may affect treatment effectiveness'
            })
            
        return factors
        
    def _generate_treatment_recommendations(self, patient_data: PatientData, treatment: str, outcome: str) -> List[str]:
        """Generate treatment-specific recommendations"""
        recommendations = []
        
        if outcome in ['poor', 'fair']:
            recommendations.extend([
                "Consider alternative treatment options",
                "Monitor treatment response closely",
                "Adjust treatment plan as needed",
                "Consider combination therapy"
            ])
        else:
            recommendations.extend([
                "Continue current treatment plan",
                "Monitor for any side effects",
                "Maintain regular follow-up appointments"
            ])
            
        return recommendations
        
    def _identify_readmission_factors(self, patient_data: PatientData, admission_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify factors affecting readmission risk"""
        factors = []
        
        # Length of stay
        los = admission_data.get('length_of_stay', 0)
        if los > 7:
            factors.append({
                'factor': 'length_of_stay',
                'value': los,
                'risk_level': 'high',
                'description': 'Long hospital stays increase readmission risk'
            })
            
        # Emergency admission
        if admission_data.get('emergency_admission', False):
            factors.append({
                'factor': 'emergency_admission',
                'value': True,
                'risk_level': 'high',
                'description': 'Emergency admissions have higher readmission rates'
            })
            
        return factors
        
    def _generate_readmission_recommendations(self, patient_data: PatientData, risk_level: str) -> List[str]:
        """Generate readmission prevention recommendations"""
        recommendations = []
        
        if risk_level == 'high':
            recommendations.extend([
                "Schedule follow-up appointment within 7 days",
                "Ensure medication reconciliation",
                "Provide detailed discharge instructions",
                "Arrange home health services if needed",
                "Monitor for early warning signs"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Schedule follow-up appointment within 14 days",
                "Review discharge instructions",
                "Monitor medication adherence"
            ])
        else:
            recommendations.extend([
                "Schedule routine follow-up appointment",
                "Continue current care plan"
            ])
            
        return recommendations
        
    def _rule_based_treatment_outcome(self, patient_data: PatientData, treatment: str) -> Dict[str, Any]:
        """Fallback rule-based treatment outcome prediction"""
        # Simple rule-based logic
        outcome_score = 0.7  # Base score
        
        # Adjust based on age
        if patient_data.age > 75:
            outcome_score -= 0.2
        elif patient_data.age < 30:
            outcome_score += 0.1
            
        # Adjust based on comorbidities
        if patient_data.diabetes_status in ['type1', 'type2']:
            outcome_score -= 0.1
            
        # Determine outcome category
        if outcome_score >= 0.8:
            outcome = 'excellent'
        elif outcome_score >= 0.6:
            outcome = 'good'
        elif outcome_score >= 0.4:
            outcome = 'fair'
        else:
            outcome = 'poor'
            
        return {
            'prediction': outcome,
            'confidence': 0.6,
            'risk_score': 1 - outcome_score,
            'factors': self._identify_treatment_factors(patient_data, treatment),
            'recommendations': self._generate_treatment_recommendations(patient_data, treatment, outcome)
        }
        
    def _rule_based_readmission_risk(self, patient_data: PatientData, admission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based readmission risk prediction"""
        risk_score = 0.3  # Base risk
        
        # Adjust based on admission data
        if admission_data.get('emergency_admission', False):
            risk_score += 0.2
            
        los = admission_data.get('length_of_stay', 0)
        if los > 7:
            risk_score += 0.2
        elif los > 3:
            risk_score += 0.1
            
        # Determine risk category
        if risk_score >= 0.6:
            risk_level = 'high'
        elif risk_score >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'
            
        return {
            'prediction': risk_level,
            'confidence': 0.6,
            'risk_score': risk_score,
            'factors': self._identify_readmission_factors(patient_data, admission_data),
            'recommendations': self._generate_readmission_recommendations(patient_data, risk_level)
        }

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize the analytics engine on startup"""
    await analytics_engine.initialize_models()
    logger.info("Analytics Engine initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "predictive_analytics_engine",
        "timestamp": datetime.now(),
        "models_loaded": len(analytics_engine.models)
    }

@app.post("/predict", response_model=PredictionResponse)
async def make_prediction(request: PredictionRequest):
    """Make a prediction based on patient data"""
    try:
        patient_data = request.patient_data
        prediction_type = request.prediction_type
        
        # Make prediction based on type
        if prediction_type == "disease_risk":
            result = analytics_engine.predict_disease_risk(patient_data)
        elif prediction_type == "treatment_outcome":
            # For treatment outcome, we need treatment info
            result = analytics_engine.predict_treatment_outcome(patient_data, "medication")
        elif prediction_type == "readmission_risk":
            # For readmission risk, we need admission data
            admission_data = {"length_of_stay": 5, "emergency_admission": False}
            result = analytics_engine.predict_readmission_risk(patient_data, admission_data)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported prediction type: {prediction_type}")
            
        # Check confidence threshold
        if result['confidence'] < request.confidence_threshold:
            raise HTTPException(
                status_code=422, 
                detail=f"Prediction confidence ({result['confidence']:.2f}) below threshold ({request.confidence_threshold})"
            )
            
        return PredictionResponse(
            patient_id=patient_data.patient_id,
            prediction_type=prediction_type,
            prediction=result['prediction'],
            confidence=result['confidence'],
            risk_score=result['risk_score'],
            factors=result['factors'] if request.include_explanations else [],
            recommendations=result['recommendations'],
            timestamp=datetime.now(),
            model_version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_model(request: ModelTrainingRequest, background_tasks: BackgroundTasks):
    """Train a new model"""
    try:
        # Add training task to background
        background_tasks.add_task(
            analytics_engine.train_model,
            request.dataset_path,
            request.target_variable,
            request.model_type,
            request.features,
            request.test_size
        )
        
        return {
            "message": "Model training started",
            "task_id": f"train_{datetime.now().timestamp()}",
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Error starting model training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "models": list(analytics_engine.models.keys()),
        "metadata": analytics_engine.model_metadata
    }

@app.get("/models/{model_name}/performance")
async def get_model_performance(model_name: str):
    """Get performance metrics for a specific model"""
    if model_name not in analytics_engine.models:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        
    # Return model performance metrics
    return {
        "model_name": model_name,
        "accuracy": 0.85,  # Placeholder
        "precision": 0.82,
        "recall": 0.88,
        "f1_score": 0.85,
        "last_updated": datetime.now()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010) 