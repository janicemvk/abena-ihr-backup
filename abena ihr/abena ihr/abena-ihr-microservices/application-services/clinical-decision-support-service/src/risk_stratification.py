"""
Risk Stratification for Abena IHR
================================

This module provides patient risk assessment capabilities including:
- Risk stratification algorithms
- Risk scoring models
- Risk-based care recommendations
- Population risk analysis
- Risk factor identification
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
import json
import redis
import httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class RiskCategory(Enum):
    CARDIOVASCULAR = "cardiovascular"
    DIABETES = "diabetes"
    CANCER = "cancer"
    RESPIRATORY = "respiratory"
    RENAL = "renal"
    MENTAL_HEALTH = "mental_health"
    FALLS = "falls"
    MEDICATION = "medication"
    GENERAL = "general"

class StratificationMethod(Enum):
    SIMPLE_SCORING = "simple_scoring"
    MACHINE_LEARNING = "machine_learning"
    CLINICAL_RULES = "clinical_rules"
    HYBRID = "hybrid"

# Pydantic models
class PatientRiskData(BaseModel):
    """Patient risk assessment data model"""
    patient_id: str
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., regex="^(male|female|other)$")
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=1, le=500)
    vital_signs: Dict[str, float] = {}
    lab_results: Dict[str, float] = {}
    medications: List[Dict[str, Any]] = []
    diagnoses: List[str] = []
    procedures: List[str] = []
    allergies: List[str] = []
    family_history: List[str] = []
    social_history: Dict[str, Any] = {}
    lifestyle_factors: Dict[str, Any] = {}
    utilization_history: Dict[str, Any] = {}

class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment"""
    patient_data: PatientRiskData
    risk_categories: List[RiskCategory] = [RiskCategory.GENERAL]
    stratification_method: StratificationMethod = StratificationMethod.HYBRID
    include_recommendations: bool = True
    include_interventions: bool = True

class RiskFactor(BaseModel):
    """Risk factor model"""
    factor_id: str
    name: str
    category: RiskCategory
    value: Any
    weight: float = Field(..., ge=0.0, le=1.0)
    description: str
    evidence_level: str = Field(..., regex="^(A|B|C|D)$")
    modifiable: bool = True

class RiskScore(BaseModel):
    """Risk score model"""
    category: RiskCategory
    score: float = Field(..., ge=0.0, le=1.0)
    level: RiskLevel
    percentile: float = Field(..., ge=0.0, le=100.0)
    factors: List[RiskFactor]
    confidence: float = Field(..., ge=0.0, le=1.0)

class RiskAssessmentResult(BaseModel):
    """Risk assessment result model"""
    patient_id: str
    assessment_id: str
    timestamp: datetime
    overall_risk_score: float = Field(..., ge=0.0, le=1.0)
    overall_risk_level: RiskLevel
    category_scores: List[RiskScore]
    risk_factors: List[RiskFactor]
    recommendations: List[Dict[str, Any]]
    interventions: List[Dict[str, Any]]
    follow_up_schedule: Dict[str, Any]
    next_assessment_date: datetime

class RiskStratificationEngine:
    """Risk stratification and assessment engine"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.risk_models = {}
        self.risk_thresholds = {}
        self.intervention_database = {}
        
    async def load_risk_models(self):
        """Load risk stratification models"""
        try:
            # Load models from Redis or database
            model_keys = self.redis_client.keys("risk_model:*")
            for key in model_keys:
                model_data = self.redis_client.get(key)
                if model_data:
                    model_dict = json.loads(model_data)
                    self.risk_models[model_dict['category']] = model_dict
                    
            logger.info(f"Loaded {len(self.risk_models)} risk models")
            
        except Exception as e:
            logger.error(f"Error loading risk models: {e}")
            # Load default models if Redis is not available
            self._load_default_risk_models()
            
    def assess_risk(self, request: RiskAssessmentRequest) -> RiskAssessmentResult:
        """Perform comprehensive risk assessment"""
        try:
            assessment_id = f"risk_{datetime.now().timestamp()}"
            patient_data = request.patient_data
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(patient_data, request.risk_categories)
            
            # Calculate category scores
            category_scores = []
            for category in request.risk_categories:
                score = self._calculate_category_score(category, risk_factors, request.stratification_method)
                category_scores.append(score)
                
            # Calculate overall risk score
            overall_score = self._calculate_overall_risk_score(category_scores)
            overall_level = self._determine_risk_level(overall_score)
            
            # Generate recommendations
            recommendations = []
            if request.include_recommendations:
                recommendations = self._generate_recommendations(risk_factors, category_scores)
                
            # Generate interventions
            interventions = []
            if request.include_interventions:
                interventions = self._generate_interventions(risk_factors, overall_level)
                
            # Determine follow-up schedule
            follow_up_schedule = self._determine_follow_up_schedule(overall_level, category_scores)
            next_assessment_date = datetime.now() + timedelta(days=follow_up_schedule['next_assessment_days'])
            
            return RiskAssessmentResult(
                patient_id=patient_data.patient_id,
                assessment_id=assessment_id,
                timestamp=datetime.now(),
                overall_risk_score=overall_score,
                overall_risk_level=overall_level,
                category_scores=category_scores,
                risk_factors=risk_factors,
                recommendations=recommendations,
                interventions=interventions,
                follow_up_schedule=follow_up_schedule,
                next_assessment_date=next_assessment_date
            )
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            raise
            
    def _identify_risk_factors(self, patient_data: PatientRiskData, 
                              categories: List[RiskCategory]) -> List[RiskFactor]:
        """Identify risk factors for the patient"""
        risk_factors = []
        
        # Age-related risk factors
        if patient_data.age > 65:
            risk_factors.append(RiskFactor(
                factor_id="age_elderly",
                name="Advanced Age",
                category=RiskCategory.GENERAL,
                value=patient_data.age,
                weight=0.3,
                description="Age 65+ increases risk of multiple conditions",
                evidence_level="A",
                modifiable=False
            ))
            
        # BMI-related risk factors
        if patient_data.height_cm and patient_data.weight_kg:
            bmi = patient_data.weight_kg / ((patient_data.height_cm / 100) ** 2)
            if bmi > 30:
                risk_factors.append(RiskFactor(
                    factor_id="obesity",
                    name="Obesity",
                    category=RiskCategory.CARDIOVASCULAR,
                    value=bmi,
                    weight=0.4,
                    description="BMI > 30 increases cardiovascular risk",
                    evidence_level="A",
                    modifiable=True
                ))
            elif bmi > 25:
                risk_factors.append(RiskFactor(
                    factor_id="overweight",
                    name="Overweight",
                    category=RiskCategory.CARDIOVASCULAR,
                    value=bmi,
                    weight=0.2,
                    description="BMI > 25 increases cardiovascular risk",
                    evidence_level="A",
                    modifiable=True
                ))
                
        # Blood pressure risk factors
        if 'blood_pressure_systolic' in patient_data.vital_signs:
            bp_systolic = patient_data.vital_signs['blood_pressure_systolic']
            if bp_systolic > 140:
                risk_factors.append(RiskFactor(
                    factor_id="hypertension",
                    name="Hypertension",
                    category=RiskCategory.CARDIOVASCULAR,
                    value=bp_systolic,
                    weight=0.5,
                    description="Systolic BP > 140 mmHg",
                    evidence_level="A",
                    modifiable=True
                ))
                
        # Diabetes risk factors
        if 'glucose' in patient_data.lab_results:
            glucose = patient_data.lab_results['glucose']
            if glucose > 126:
                risk_factors.append(RiskFactor(
                    factor_id="diabetes",
                    name="Diabetes",
                    category=RiskCategory.DIABETES,
                    value=glucose,
                    weight=0.6,
                    description="Fasting glucose > 126 mg/dL",
                    evidence_level="A",
                    modifiable=True
                ))
                
        # Medication risk factors
        if len(patient_data.medications) > 5:
            risk_factors.append(RiskFactor(
                factor_id="polypharmacy",
                name="Polypharmacy",
                category=RiskCategory.MEDICATION,
                value=len(patient_data.medications),
                weight=0.4,
                description=f"Taking {len(patient_data.medications)} medications",
                evidence_level="B",
                modifiable=True
            ))
            
        # Family history risk factors
        for condition in patient_data.family_history:
            if condition.lower() in ['heart_disease', 'diabetes', 'cancer']:
                risk_factors.append(RiskFactor(
                    factor_id=f"family_{condition.lower()}",
                    name=f"Family History: {condition}",
                    category=RiskCategory.GENERAL,
                    value=condition,
                    weight=0.3,
                    description=f"Family history of {condition}",
                    evidence_level="B",
                    modifiable=False
                ))
                
        # Lifestyle risk factors
        if patient_data.lifestyle_factors.get('smoking', False):
            risk_factors.append(RiskFactor(
                factor_id="smoking",
                name="Current Smoking",
                category=RiskCategory.CARDIOVASCULAR,
                value=True,
                weight=0.5,
                description="Current tobacco use",
                evidence_level="A",
                modifiable=True
            ))
            
        if patient_data.lifestyle_factors.get('sedentary', False):
            risk_factors.append(RiskFactor(
                factor_id="sedentary",
                name="Sedentary Lifestyle",
                category=RiskCategory.CARDIOVASCULAR,
                value=True,
                weight=0.3,
                description="Low physical activity level",
                evidence_level="B",
                modifiable=True
            ))
            
        return risk_factors
        
    def _calculate_category_score(self, category: RiskCategory, risk_factors: List[RiskFactor], 
                                 method: StratificationMethod) -> RiskScore:
        """Calculate risk score for a specific category"""
        try:
            # Filter risk factors for this category
            category_factors = [rf for rf in risk_factors if rf.category == category]
            
            if method == StratificationMethod.SIMPLE_SCORING:
                score = self._simple_scoring(category_factors)
            elif method == StratificationMethod.MACHINE_LEARNING:
                score = self._ml_scoring(category_factors)
            elif method == StratificationMethod.CLINICAL_RULES:
                score = self._clinical_rules_scoring(category_factors)
            else:  # HYBRID
                score = self._hybrid_scoring(category_factors)
                
            # Determine risk level
            level = self._determine_risk_level(score)
            
            # Calculate percentile (simplified)
            percentile = score * 100
            
            # Calculate confidence
            confidence = self._calculate_confidence(category_factors, method)
            
            return RiskScore(
                category=category,
                score=score,
                level=level,
                percentile=percentile,
                factors=category_factors,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error calculating category score: {e}")
            raise
            
    def _simple_scoring(self, risk_factors: List[RiskFactor]) -> float:
        """Simple weighted scoring method"""
        if not risk_factors:
            return 0.0
            
        total_weight = sum(rf.weight for rf in risk_factors)
        weighted_sum = sum(rf.weight for rf in risk_factors)
        
        return min(1.0, weighted_sum / total_weight) if total_weight > 0 else 0.0
        
    def _ml_scoring(self, risk_factors: List[RiskFactor]) -> float:
        """Machine learning-based scoring (simplified)"""
        # This would typically use a trained ML model
        # For now, use an enhanced version of simple scoring
        if not risk_factors:
            return 0.0
            
        # Apply non-linear transformation
        base_score = self._simple_scoring(risk_factors)
        return min(1.0, base_score ** 1.5)  # Non-linear scaling
        
    def _clinical_rules_scoring(self, risk_factors: List[RiskFactor]) -> float:
        """Clinical rules-based scoring"""
        if not risk_factors:
            return 0.0
            
        # Apply clinical rules
        score = 0.0
        factor_count = len(risk_factors)
        
        # Base score from factor weights
        base_score = self._simple_scoring(risk_factors)
        
        # Apply clinical rules
        if factor_count >= 3:
            score = min(1.0, base_score * 1.2)  # Multiple factors increase risk
        elif factor_count >= 2:
            score = min(1.0, base_score * 1.1)
        else:
            score = base_score
            
        return score
        
    def _hybrid_scoring(self, risk_factors: List[RiskFactor]) -> float:
        """Hybrid scoring combining multiple methods"""
        if not risk_factors:
            return 0.0
            
        # Get scores from different methods
        simple_score = self._simple_scoring(risk_factors)
        ml_score = self._ml_scoring(risk_factors)
        rules_score = self._clinical_rules_scoring(risk_factors)
        
        # Weighted combination
        hybrid_score = (simple_score * 0.4 + ml_score * 0.3 + rules_score * 0.3)
        
        return min(1.0, hybrid_score)
        
    def _calculate_overall_risk_score(self, category_scores: List[RiskScore]) -> float:
        """Calculate overall risk score from category scores"""
        if not category_scores:
            return 0.0
            
        # Weight categories based on clinical importance
        category_weights = {
            RiskCategory.CARDIOVASCULAR: 0.3,
            RiskCategory.DIABETES: 0.25,
            RiskCategory.CANCER: 0.2,
            RiskCategory.MEDICATION: 0.15,
            RiskCategory.GENERAL: 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for score in category_scores:
            weight = category_weights.get(score.category, 0.1)
            weighted_sum += score.score * weight
            total_weight += weight
            
        return weighted_sum / total_weight if total_weight > 0 else 0.0
        
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from score"""
        if score >= 0.8:
            return RiskLevel.VERY_HIGH
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
            
    def _calculate_confidence(self, risk_factors: List[RiskFactor], method: StratificationMethod) -> float:
        """Calculate confidence in the risk assessment"""
        if not risk_factors:
            return 0.0
            
        # Base confidence on number and quality of factors
        factor_count = len(risk_factors)
        evidence_levels = [rf.evidence_level for rf in risk_factors]
        
        # Evidence level scoring
        evidence_scores = {'A': 1.0, 'B': 0.8, 'C': 0.6, 'D': 0.4}
        avg_evidence_score = sum(evidence_scores.get(level, 0.5) for level in evidence_levels) / len(evidence_levels)
        
        # Factor count adjustment
        count_factor = min(1.0, factor_count / 5.0)  # Normalize to 5 factors
        
        # Method adjustment
        method_confidence = {
            StratificationMethod.SIMPLE_SCORING: 0.7,
            StratificationMethod.MACHINE_LEARNING: 0.9,
            StratificationMethod.CLINICAL_RULES: 0.8,
            StratificationMethod.HYBRID: 0.85
        }
        
        method_factor = method_confidence.get(method, 0.7)
        
        # Calculate final confidence
        confidence = (avg_evidence_score * 0.4 + count_factor * 0.3 + method_factor * 0.3)
        
        return min(1.0, confidence)
        
    def _generate_recommendations(self, risk_factors: List[RiskFactor], 
                                category_scores: List[RiskScore]) -> List[Dict[str, Any]]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        # High-risk factor recommendations
        high_risk_factors = [rf for rf in risk_factors if rf.weight >= 0.5]
        for factor in high_risk_factors:
            recommendations.append({
                'type': 'high_risk_factor',
                'factor': factor.name,
                'recommendation': f'Address {factor.name}: {factor.description}',
                'priority': 'high',
                'modifiable': factor.modifiable
            })
            
        # Category-specific recommendations
        for score in category_scores:
            if score.level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                recommendations.append({
                    'type': 'category_risk',
                    'category': score.category.value,
                    'recommendation': f'Implement {score.category.value} risk management',
                    'priority': 'high',
                    'modifiable': True
                })
                
        # Lifestyle recommendations
        lifestyle_factors = [rf for rf in risk_factors if rf.modifiable and 'lifestyle' in rf.description.lower()]
        if lifestyle_factors:
            recommendations.append({
                'type': 'lifestyle',
                'factor': 'lifestyle_modification',
                'recommendation': 'Implement lifestyle modification program',
                'priority': 'medium',
                'modifiable': True
            })
            
        return recommendations
        
    def _generate_interventions(self, risk_factors: List[RiskFactor], 
                              overall_level: RiskLevel) -> List[Dict[str, Any]]:
        """Generate risk-based interventions"""
        interventions = []
        
        # Risk level-based interventions
        if overall_level == RiskLevel.VERY_HIGH:
            interventions.extend([
                {
                    'type': 'intensive_monitoring',
                    'name': 'Intensive Monitoring',
                    'description': 'Daily vital signs and symptom monitoring',
                    'frequency': 'daily',
                    'duration': 'ongoing'
                },
                {
                    'type': 'care_coordination',
                    'name': 'Care Coordination',
                    'description': 'Assign care coordinator for complex case management',
                    'frequency': 'weekly',
                    'duration': 'ongoing'
                }
            ])
        elif overall_level == RiskLevel.HIGH:
            interventions.extend([
                {
                    'type': 'regular_monitoring',
                    'name': 'Regular Monitoring',
                    'description': 'Weekly vital signs and health status check',
                    'frequency': 'weekly',
                    'duration': '3_months'
                },
                {
                    'type': 'preventive_care',
                    'name': 'Preventive Care',
                    'description': 'Enhanced preventive care and screening',
                    'frequency': 'monthly',
                    'duration': 'ongoing'
                }
            ])
        elif overall_level == RiskLevel.MODERATE:
            interventions.append({
                'type': 'standard_monitoring',
                'name': 'Standard Monitoring',
                'description': 'Routine health monitoring and preventive care',
                'frequency': 'monthly',
                'duration': 'ongoing'
            })
        else:  # LOW
            interventions.append({
                'type': 'maintenance_care',
                'name': 'Maintenance Care',
                'description': 'Routine maintenance and preventive care',
                'frequency': 'quarterly',
                'duration': 'ongoing'
            })
            
        # Factor-specific interventions
        for factor in risk_factors:
            if factor.weight >= 0.4:
                interventions.append({
                    'type': 'factor_specific',
                    'name': f'{factor.name} Management',
                    'description': f'Targeted intervention for {factor.name}',
                    'frequency': 'as_needed',
                    'duration': 'ongoing'
                })
                
        return interventions
        
    def _determine_follow_up_schedule(self, overall_level: RiskLevel, 
                                    category_scores: List[RiskScore]) -> Dict[str, Any]:
        """Determine follow-up schedule based on risk level"""
        if overall_level == RiskLevel.VERY_HIGH:
            return {
                'next_assessment_days': 30,
                'monitoring_frequency': 'daily',
                'provider_contact': 'weekly',
                'specialist_referral': 'immediate'
            }
        elif overall_level == RiskLevel.HIGH:
            return {
                'next_assessment_days': 60,
                'monitoring_frequency': 'weekly',
                'provider_contact': 'monthly',
                'specialist_referral': 'as_needed'
            }
        elif overall_level == RiskLevel.MODERATE:
            return {
                'next_assessment_days': 90,
                'monitoring_frequency': 'monthly',
                'provider_contact': 'quarterly',
                'specialist_referral': 'none'
            }
        else:  # LOW
            return {
                'next_assessment_days': 180,
                'monitoring_frequency': 'quarterly',
                'provider_contact': 'semi_annually',
                'specialist_referral': 'none'
            }
            
    def _load_default_risk_models(self):
        """Load default risk stratification models"""
        default_models = {
            'cardiovascular': {
                'category': 'cardiovascular',
                'factors': ['age', 'bmi', 'blood_pressure', 'smoking', 'family_history'],
                'weights': [0.3, 0.4, 0.5, 0.5, 0.3],
                'thresholds': {'low': 0.3, 'moderate': 0.5, 'high': 0.7, 'very_high': 0.8}
            },
            'diabetes': {
                'category': 'diabetes',
                'factors': ['glucose', 'bmi', 'age', 'family_history'],
                'weights': [0.6, 0.4, 0.2, 0.3],
                'thresholds': {'low': 0.3, 'moderate': 0.5, 'high': 0.7, 'very_high': 0.8}
            },
            'medication': {
                'category': 'medication',
                'factors': ['medication_count', 'interactions', 'adherence'],
                'weights': [0.4, 0.6, 0.3],
                'thresholds': {'low': 0.3, 'moderate': 0.5, 'high': 0.7, 'very_high': 0.8}
            }
        }
        
        for category, model in default_models.items():
            self.risk_models[category] = model
            
        logger.info(f"Loaded {len(default_models)} default risk models")

# Initialize risk stratification engine
risk_engine = RiskStratificationEngine()

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Risk Stratification",
    description="Patient risk assessment and stratification",
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

@app.on_event("startup")
async def startup_event():
    """Initialize the risk engine on startup"""
    await risk_engine.load_risk_models()
    logger.info("Risk Stratification Engine initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "risk_stratification",
        "timestamp": datetime.now(),
        "models_count": len(risk_engine.risk_models)
    }

@app.post("/assess-risk")
async def assess_risk(request: RiskAssessmentRequest):
    """Perform risk assessment"""
    try:
        result = risk_engine.assess_risk(request)
        return result
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk-categories")
async def get_risk_categories():
    """Get available risk categories"""
    return {
        "categories": [cat.value for cat in RiskCategory],
        "methods": [method.value for method in StratificationMethod],
        "levels": [level.value for level in RiskLevel]
    }

@app.get("/risk-models")
async def get_risk_models():
    """Get available risk models"""
    try:
        return {
            "models": risk_engine.risk_models,
            "count": len(risk_engine.risk_models)
        }
    except Exception as e:
        logger.error(f"Error getting risk models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8023) 