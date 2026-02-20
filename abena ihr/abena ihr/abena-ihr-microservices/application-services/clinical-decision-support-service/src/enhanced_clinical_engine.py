"""
Enhanced Clinical Decision Support Engine for Abena IHR
======================================================

This module provides an enhanced clinical decision support system that combines:
- Advanced TypeScript reasoning engine for deep context analysis
- Python service layer for API endpoints and integration
- Comprehensive clinical decision support capabilities
- Evidence-based medicine integration
- Clinical workflow support
"""

import asyncio
import logging
import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
import redis
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class ClinicalPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DecisionType(Enum):
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MEDICATION = "medication"
    MONITORING = "monitoring"
    REFERRAL = "referral"
    PREVENTION = "prevention"
    CONTEXTUAL_ANALYSIS = "contextual_analysis"
    TRAJECTORY_PREDICTION = "trajectory_prediction"

# Enhanced Pydantic models
class PatientContext(BaseModel):
    """Enhanced patient clinical context model"""
    patient_id: str
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., regex="^(male|female|other)$")
    primary_diagnosis: Optional[str] = None
    comorbidities: List[str] = []
    current_medications: List[Dict[str, Any]] = []
    vital_signs: Dict[str, float] = {}
    lab_results: Dict[str, float] = {}
    symptoms: List[str] = []
    allergies: List[str] = []
    family_history: List[str] = []
    social_history: Dict[str, Any] = {}
    clinical_notes: List[str] = []
    last_visit_date: Optional[datetime] = None
    
    # Enhanced fields for advanced analysis
    environmental_factors: Optional[Dict[str, Any]] = {}
    temporal_context: Optional[Dict[str, Any]] = {}
    social_context: Optional[Dict[str, Any]] = {}
    psychological_state: Optional[Dict[str, Any]] = {}
    functional_status: Optional[Dict[str, Any]] = {}

class ClinicalDecisionRequest(BaseModel):
    """Enhanced request model for clinical decisions"""
    patient_context: PatientContext
    decision_type: DecisionType
    clinical_question: str
    urgency_level: ClinicalPriority = ClinicalPriority.MEDIUM
    include_evidence: bool = True
    include_alternatives: bool = True
    include_contextual_analysis: bool = True
    include_trajectory_prediction: bool = False

class ClinicalDecision(BaseModel):
    """Enhanced clinical decision model"""
    decision_id: str
    patient_id: str
    decision_type: DecisionType
    recommendation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    priority: ClinicalPriority
    evidence: List[Dict[str, Any]] = []
    alternatives: List[Dict[str, Any]] = []
    contraindications: List[str] = []
    monitoring_requirements: List[str] = []
    follow_up_actions: List[str] = []
    timestamp: datetime
    reasoning: str
    
    # Enhanced fields from TypeScript engine
    contextual_analysis: Optional[Dict[str, Any]] = None
    risk_factors: Optional[List[Dict[str, Any]]] = []
    contextual_insights: Optional[List[Dict[str, Any]]] = []
    clinical_trajectory: Optional[Dict[str, Any]] = None
    contextual_recommendations: Optional[List[Dict[str, Any]]] = []

class ContextualAnalysisRequest(BaseModel):
    """Request model for contextual analysis"""
    patient_context: PatientContext
    analysis_depth: str = Field(default="comprehensive", regex="^(basic|comprehensive|detailed)$")
    include_insights: bool = True
    include_recommendations: bool = True

class TrajectoryPredictionRequest(BaseModel):
    """Request model for trajectory prediction"""
    patient_context: PatientContext
    time_horizon: str = Field(default="30d", regex="^(7d|30d|90d|1y)$")
    include_scenarios: bool = True
    include_interventions: bool = True

class EnhancedClinicalContextEngine:
    """Enhanced clinical context analysis and decision support engine"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.clinical_rules = {}
        self.evidence_base = {}
        self.knowledge_graph = {}
        
        # TypeScript reasoning engine integration
        self.reasoning_engine_url = "http://localhost:3000"  # TypeScript engine service
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def analyze_patient_context(self, patient_context: PatientContext) -> Dict[str, Any]:
        """Enhanced patient clinical context analysis using TypeScript engine"""
        try:
            # Basic Python analysis
            basic_analysis = await self._perform_basic_analysis(patient_context)
            
            # Advanced TypeScript engine analysis
            advanced_analysis = await self._perform_advanced_analysis(patient_context)
            
            # Combine analyses
            combined_analysis = {
                **basic_analysis,
                **advanced_analysis,
                'analysis_timestamp': datetime.now(),
                'analysis_engine': 'hybrid_python_typescript'
            }
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing patient context: {e}")
            # Fallback to basic analysis if TypeScript engine fails
            return await self._perform_basic_analysis(patient_context)
            
    async def _perform_basic_analysis(self, patient_context: PatientContext) -> Dict[str, Any]:
        """Perform basic Python-based analysis"""
        analysis = {
            'risk_factors': [],
            'clinical_indicators': [],
            'treatment_gaps': [],
            'monitoring_needs': [],
            'clinical_priorities': []
        }
        
        # Analyze risk factors
        risk_factors = self._identify_risk_factors(patient_context)
        analysis['risk_factors'] = risk_factors
        
        # Analyze clinical indicators
        clinical_indicators = self._analyze_clinical_indicators(patient_context)
        analysis['clinical_indicators'] = clinical_indicators
        
        # Identify treatment gaps
        treatment_gaps = self._identify_treatment_gaps(patient_context)
        analysis['treatment_gaps'] = treatment_gaps
        
        # Determine monitoring needs
        monitoring_needs = self._determine_monitoring_needs(patient_context)
        analysis['monitoring_needs'] = monitoring_needs
        
        # Set clinical priorities
        clinical_priorities = self._set_clinical_priorities(patient_context, analysis)
        analysis['clinical_priorities'] = clinical_priorities
        
        return analysis
        
    async def _perform_advanced_analysis(self, patient_context: PatientContext) -> Dict[str, Any]:
        """Perform advanced analysis using TypeScript reasoning engine"""
        try:
            # Convert Python context to TypeScript format
            ts_context = self._convert_to_typescript_format(patient_context)
            
            # Call TypeScript reasoning engine
            response = await self.http_client.post(
                f"{self.reasoning_engine_url}/analyze-context",
                json=ts_context
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"TypeScript engine returned {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error calling TypeScript reasoning engine: {e}")
            return {}
            
    def _convert_to_typescript_format(self, patient_context: PatientContext) -> Dict[str, Any]:
        """Convert Python patient context to TypeScript format"""
        return {
            "patientId": patient_context.patient_id,
            "age": patient_context.age,
            "gender": patient_context.gender,
            "primaryDiagnosis": patient_context.primary_diagnosis,
            "comorbidities": patient_context.comorbidities,
            "currentMedications": patient_context.current_medications,
            "vitalSigns": patient_context.vital_signs,
            "labResults": patient_context.lab_results,
            "symptoms": patient_context.symptoms,
            "allergies": patient_context.allergies,
            "familyHistory": patient_context.family_history,
            "socialHistory": patient_context.social_history,
            "clinicalNotes": patient_context.clinical_notes,
            "lastVisitDate": patient_context.last_visit_date.isoformat() if patient_context.last_visit_date else None,
            "environmentalFactors": patient_context.environmental_factors,
            "temporalContext": patient_context.temporal_context,
            "socialContext": patient_context.social_context,
            "psychologicalState": patient_context.psychological_state,
            "functionalStatus": patient_context.functional_status
        }
        
    async def generate_clinical_decision(self, request: ClinicalDecisionRequest) -> ClinicalDecision:
        """Generate enhanced clinical decision using hybrid approach"""
        try:
            # Analyze patient context
            context_analysis = await self.analyze_patient_context(request.patient_context)
            
            # Generate decision based on type
            if request.decision_type == DecisionType.CONTEXTUAL_ANALYSIS:
                decision = await self._generate_contextual_analysis_decision(request, context_analysis)
            elif request.decision_type == DecisionType.TRAJECTORY_PREDICTION:
                decision = await self._generate_trajectory_prediction_decision(request, context_analysis)
            else:
                decision = self._generate_standard_decision(request, context_analysis)
                
            # Add contextual analysis if requested
            if request.include_contextual_analysis:
                decision.contextual_analysis = context_analysis
                decision.contextual_insights = await self._generate_contextual_insights(request.patient_context)
                
            # Add trajectory prediction if requested
            if request.include_trajectory_prediction:
                decision.clinical_trajectory = await self._predict_clinical_trajectory(request.patient_context)
                
            return decision
            
        except Exception as e:
            logger.error(f"Error generating clinical decision: {e}")
            raise
            
    async def _generate_contextual_analysis_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate contextual analysis decision"""
        # Use TypeScript engine for advanced contextual analysis
        try:
            ts_context = self._convert_to_typescript_format(request.patient_context)
            response = await self.http_client.post(
                f"{self.reasoning_engine_url}/contextual-analysis",
                json=ts_context
            )
            
            if response.status_code == 200:
                ts_analysis = response.json()
                recommendation = f"Contextual analysis completed with {len(ts_analysis.get('insights', []))} insights"
                confidence = ts_analysis.get('confidenceLevel', 0.8)
                priority = ClinicalPriority.HIGH if ts_analysis.get('contextualRelevance', 0) > 0.7 else ClinicalPriority.MEDIUM
            else:
                recommendation = "Contextual analysis completed with basic insights"
                confidence = 0.7
                priority = ClinicalPriority.MEDIUM
                
        except Exception as e:
            logger.error(f"Error in contextual analysis: {e}")
            recommendation = "Contextual analysis completed with basic insights"
            confidence = 0.6
            priority = ClinicalPriority.MEDIUM
            
        return ClinicalDecision(
            decision_id=f"ctx_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.CONTEXTUAL_ANALYSIS,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "contextual_analysis", "strength": "moderate"}],
            alternatives=[],
            contraindications=[],
            monitoring_requirements=[],
            follow_up_actions=["review_contextual_insights", "update_care_plan"],
            timestamp=datetime.now(),
            reasoning=f"Based on comprehensive contextual analysis of patient {request.patient_context.patient_id}"
        )
        
    async def _generate_trajectory_prediction_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate trajectory prediction decision"""
        # Use TypeScript engine for trajectory prediction
        try:
            ts_context = self._convert_to_typescript_format(request.patient_context)
            response = await self.http_client.post(
                f"{self.reasoning_engine_url}/predict-trajectory",
                json=ts_context
            )
            
            if response.status_code == 200:
                ts_prediction = response.json()
                recommendation = f"Trajectory prediction completed with {len(ts_prediction.get('scenarios', []))} scenarios"
                confidence = ts_prediction.get('confidenceLevel', 0.8)
                priority = ClinicalPriority.HIGH if len(ts_prediction.get('riskEvents', [])) > 0 else ClinicalPriority.MEDIUM
            else:
                recommendation = "Trajectory prediction completed with basic analysis"
                confidence = 0.7
                priority = ClinicalPriority.MEDIUM
                
        except Exception as e:
            logger.error(f"Error in trajectory prediction: {e}")
            recommendation = "Trajectory prediction completed with basic analysis"
            confidence = 0.6
            priority = ClinicalPriority.MEDIUM
            
        return ClinicalDecision(
            decision_id=f"traj_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.TRAJECTORY_PREDICTION,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "trajectory_prediction", "strength": "moderate"}],
            alternatives=[],
            contraindications=[],
            monitoring_requirements=["trajectory_monitoring"],
            follow_up_actions=["review_trajectory", "adjust_interventions"],
            timestamp=datetime.now(),
            reasoning=f"Based on clinical trajectory prediction for patient {request.patient_context.patient_id}"
        )
        
    def _generate_standard_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate standard clinical decision using existing logic"""
        # Use existing decision generation logic
        if request.decision_type == DecisionType.DIAGNOSIS:
            return self._generate_diagnosis_decision(request, context_analysis)
        elif request.decision_type == DecisionType.TREATMENT:
            return self._generate_treatment_decision(request, context_analysis)
        elif request.decision_type == DecisionType.MEDICATION:
            return self._generate_medication_decision(request, context_analysis)
        elif request.decision_type == DecisionType.MONITORING:
            return self._generate_monitoring_decision(request, context_analysis)
        elif request.decision_type == DecisionType.REFERRAL:
            return self._generate_referral_decision(request, context_analysis)
        elif request.decision_type == DecisionType.PREVENTION:
            return self._generate_prevention_decision(request, context_analysis)
        else:
            raise ValueError(f"Unsupported decision type: {request.decision_type}")
            
    async def _generate_contextual_insights(self, patient_context: PatientContext) -> List[Dict[str, Any]]:
        """Generate contextual insights using TypeScript engine"""
        try:
            ts_context = self._convert_to_typescript_format(patient_context)
            response = await self.http_client.post(
                f"{self.reasoning_engine_url}/generate-insights",
                json=ts_context
            )
            
            if response.status_code == 200:
                return response.json().get('insights', [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error generating contextual insights: {e}")
            return []
            
    async def _predict_clinical_trajectory(self, patient_context: PatientContext) -> Dict[str, Any]:
        """Predict clinical trajectory using TypeScript engine"""
        try:
            ts_context = self._convert_to_typescript_format(patient_context)
            response = await self.http_client.post(
                f"{self.reasoning_engine_url}/predict-trajectory",
                json=ts_context
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error predicting clinical trajectory: {e}")
            return {}
            
    # Reuse existing analysis methods from the original engine
    def _identify_risk_factors(self, patient_context: PatientContext) -> List[Dict[str, Any]]:
        """Identify risk factors for the patient"""
        risk_factors = []
        
        # Age-related risks
        if patient_context.age > 65:
            risk_factors.append({
                'factor': 'advanced_age',
                'value': patient_context.age,
                'risk_level': 'high',
                'description': 'Advanced age increases risk of multiple conditions'
            })
            
        # Vital signs risks
        if 'blood_pressure_systolic' in patient_context.vital_signs:
            bp_systolic = patient_context.vital_signs['blood_pressure_systolic']
            if bp_systolic > 140:
                risk_factors.append({
                    'factor': 'hypertension',
                    'value': bp_systolic,
                    'risk_level': 'high',
                    'description': 'Elevated systolic blood pressure'
                })
                
        if 'heart_rate' in patient_context.vital_signs:
            hr = patient_context.vital_signs['heart_rate']
            if hr > 100:
                risk_factors.append({
                    'factor': 'tachycardia',
                    'value': hr,
                    'risk_level': 'medium',
                    'description': 'Elevated heart rate'
                })
                
        # Lab results risks
        if 'glucose' in patient_context.lab_results:
            glucose = patient_context.lab_results['glucose']
            if glucose > 126:
                risk_factors.append({
                    'factor': 'hyperglycemia',
                    'value': glucose,
                    'risk_level': 'high',
                    'description': 'Elevated blood glucose'
                })
                
        # Medication risks
        for medication in patient_context.current_medications:
            if medication.get('high_risk', False):
                risk_factors.append({
                    'factor': 'high_risk_medication',
                    'value': medication.get('name', 'Unknown'),
                    'risk_level': 'high',
                    'description': f"High-risk medication: {medication.get('name', 'Unknown')}"
                })
                
        return risk_factors
        
    def _analyze_clinical_indicators(self, patient_context: PatientContext) -> List[Dict[str, Any]]:
        """Analyze clinical indicators"""
        indicators = []
        
        # Symptom analysis
        for symptom in patient_context.symptoms:
            severity = self._assess_symptom_severity(symptom, patient_context)
            indicators.append({
                'type': 'symptom',
                'name': symptom,
                'severity': severity,
                'urgency': 'high' if severity == 'severe' else 'medium'
            })
            
        # Vital signs analysis
        for vital_sign, value in patient_context.vital_signs.items():
            status = self._assess_vital_sign_status(vital_sign, value)
            if status != 'normal':
                indicators.append({
                    'type': 'vital_sign',
                    'name': vital_sign,
                    'value': value,
                    'status': status,
                    'urgency': 'high' if status in ['critical', 'severe'] else 'medium'
                })
                
        # Lab results analysis
        for lab_test, value in patient_context.lab_results.items():
            status = self._assess_lab_result_status(lab_test, value)
            if status != 'normal':
                indicators.append({
                    'type': 'lab_result',
                    'name': lab_test,
                    'value': value,
                    'status': status,
                    'urgency': 'high' if status in ['critical', 'severe'] else 'medium'
                })
                
        return indicators
        
    def _identify_treatment_gaps(self, patient_context: PatientContext) -> List[Dict[str, Any]]:
        """Identify gaps in current treatment"""
        gaps = []
        
        # Check for missing preventive care
        if patient_context.age > 50 and not any('screening' in med.get('name', '').lower() for med in patient_context.current_medications):
            gaps.append({
                'type': 'preventive_care',
                'description': 'Missing age-appropriate screenings',
                'priority': 'medium',
                'recommendation': 'Schedule preventive screenings'
            })
            
        # Check for medication adherence
        for medication in patient_context.current_medications:
            if medication.get('adherence_rate', 1.0) < 0.8:
                gaps.append({
                    'type': 'medication_adherence',
                    'description': f"Low adherence to {medication.get('name', 'medication')}",
                    'priority': 'high',
                    'recommendation': 'Address medication adherence issues'
                })
                
        # Check for follow-up needs
        if patient_context.last_visit_date:
            days_since_visit = (datetime.now() - patient_context.last_visit_date).days
            if days_since_visit > 90:
                gaps.append({
                    'type': 'follow_up',
                    'description': 'Overdue for follow-up visit',
                    'priority': 'medium',
                    'recommendation': 'Schedule follow-up appointment'
                })
                
        return gaps
        
    def _determine_monitoring_needs(self, patient_context: PatientContext) -> List[Dict[str, Any]]:
        """Determine monitoring requirements"""
        monitoring_needs = []
        
        # High-risk patients need frequent monitoring
        if len([rf for rf in self._identify_risk_factors(patient_context) if rf['risk_level'] == 'high']) > 2:
            monitoring_needs.append({
                'type': 'vital_signs',
                'frequency': 'daily',
                'parameters': ['blood_pressure', 'heart_rate', 'temperature'],
                'reason': 'Multiple high-risk factors'
            })
            
        # Medication monitoring
        for medication in patient_context.current_medications:
            if medication.get('requires_monitoring', False):
                monitoring_needs.append({
                    'type': 'medication_monitoring',
                    'medication': medication.get('name'),
                    'frequency': medication.get('monitoring_frequency', 'weekly'),
                    'parameters': medication.get('monitoring_parameters', []),
                    'reason': f"Required monitoring for {medication.get('name')}"
                })
                
        # Lab monitoring
        if any(self._assess_lab_result_status(test, value) != 'normal' 
               for test, value in patient_context.lab_results.items()):
            monitoring_needs.append({
                'type': 'lab_monitoring',
                'frequency': 'weekly',
                'parameters': list(patient_context.lab_results.keys()),
                'reason': 'Abnormal lab results require monitoring'
            })
            
        return monitoring_needs
        
    def _set_clinical_priorities(self, patient_context: PatientContext, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Set clinical priorities based on analysis"""
        priorities = []
        
        # Critical indicators get highest priority
        critical_indicators = [ind for ind in analysis['clinical_indicators'] if ind['urgency'] == 'high']
        for indicator in critical_indicators:
            priorities.append({
                'priority': 'critical',
                'type': indicator['type'],
                'description': f"Address {indicator['name']}",
                'reason': f"{indicator['name']} requires immediate attention"
            })
            
        # High-risk factors
        high_risk_factors = [rf for rf in analysis['risk_factors'] if rf['risk_level'] == 'high']
        for factor in high_risk_factors:
            priorities.append({
                'priority': 'high',
                'type': 'risk_management',
                'description': f"Manage {factor['factor']}",
                'reason': factor['description']
            })
            
        # Treatment gaps
        for gap in analysis['treatment_gaps']:
            priorities.append({
                'priority': gap['priority'],
                'type': 'treatment_gap',
                'description': gap['description'],
                'reason': gap['recommendation']
            })
            
        return priorities
        
    def _assess_symptom_severity(self, symptom: str, patient_context: PatientContext) -> str:
        """Assess symptom severity"""
        severe_symptoms = ['chest_pain', 'shortness_of_breath', 'severe_headache', 'loss_of_consciousness']
        moderate_symptoms = ['fever', 'cough', 'fatigue', 'nausea']
        
        if symptom.lower() in severe_symptoms:
            return 'severe'
        elif symptom.lower() in moderate_symptoms:
            return 'moderate'
        else:
            return 'mild'
            
    def _assess_vital_sign_status(self, vital_sign: str, value: float) -> str:
        """Assess vital sign status"""
        normal_ranges = {
            'blood_pressure_systolic': (90, 140),
            'blood_pressure_diastolic': (60, 90),
            'heart_rate': (60, 100),
            'temperature': (36.0, 37.5),
            'oxygen_saturation': (95, 100)
        }
        
        if vital_sign in normal_ranges:
            min_val, max_val = normal_ranges[vital_sign]
            if value < min_val:
                return 'low'
            elif value > max_val:
                return 'high'
            else:
                return 'normal'
        else:
            return 'unknown'
            
    def _assess_lab_result_status(self, lab_test: str, value: float) -> str:
        """Assess lab result status"""
        normal_ranges = {
            'glucose': (70, 126),
            'creatinine': (0.6, 1.2),
            'hemoglobin': (12, 16),
            'platelets': (150, 450),
            'wbc': (4, 11)
        }
        
        if lab_test in normal_ranges:
            min_val, max_val = normal_ranges[lab_test]
            if value < min_val:
                return 'low'
            elif value > max_val:
                return 'high'
            else:
                return 'normal'
        else:
            return 'unknown'
            
    # Reuse existing decision generation methods
    def _generate_diagnosis_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate diagnosis decision"""
        symptoms = request.patient_context.symptoms
        indicators = context_analysis['clinical_indicators']
        
        if 'chest_pain' in symptoms and any(ind['name'] == 'heart_rate' and ind['status'] == 'high' for ind in indicators):
            recommendation = "Consider cardiac evaluation for chest pain with elevated heart rate"
            confidence = 0.8
            priority = ClinicalPriority.HIGH
        elif 'fever' in symptoms and 'cough' in symptoms:
            recommendation = "Consider respiratory infection evaluation"
            confidence = 0.7
            priority = ClinicalPriority.MEDIUM
        else:
            recommendation = "Schedule comprehensive evaluation based on symptoms"
            confidence = 0.6
            priority = ClinicalPriority.MEDIUM
            
        return ClinicalDecision(
            decision_id=f"diag_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.DIAGNOSIS,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "clinical_guidelines", "strength": "moderate"}],
            alternatives=[{"option": "watchful_waiting", "description": "Monitor symptoms"}],
            contraindications=[],
            monitoring_requirements=["vital_signs", "symptom_tracking"],
            follow_up_actions=["schedule_follow_up", "lab_workup"],
            timestamp=datetime.now(),
            reasoning=f"Based on symptoms: {', '.join(symptoms)} and clinical indicators"
        )
        
    def _generate_treatment_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate treatment decision"""
        treatment_gaps = context_analysis['treatment_gaps']
        priorities = context_analysis['clinical_priorities']
        
        if treatment_gaps:
            primary_gap = treatment_gaps[0]
            recommendation = f"Address treatment gap: {primary_gap['description']}"
            confidence = 0.8
            priority = ClinicalPriority.HIGH if primary_gap['priority'] == 'high' else ClinicalPriority.MEDIUM
        else:
            recommendation = "Continue current treatment plan with monitoring"
            confidence = 0.7
            priority = ClinicalPriority.MEDIUM
            
        return ClinicalDecision(
            decision_id=f"treat_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.TREATMENT,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "treatment_guidelines", "strength": "moderate"}],
            alternatives=[],
            contraindications=[],
            monitoring_requirements=["treatment_response", "side_effects"],
            follow_up_actions=["treatment_review", "outcome_assessment"],
            timestamp=datetime.now(),
            reasoning="Based on treatment gap analysis and clinical priorities"
        )
        
    def _generate_medication_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate medication decision"""
        current_meds = request.patient_context.current_medications
        allergies = request.patient_context.allergies
        
        if allergies:
            recommendation = f"Review medication safety given allergies: {', '.join(allergies)}"
            confidence = 0.9
            priority = ClinicalPriority.HIGH
        elif len(current_meds) > 5:
            recommendation = "Consider medication review for polypharmacy"
            confidence = 0.8
            priority = ClinicalPriority.MEDIUM
        else:
            recommendation = "Current medication regimen appears appropriate"
            confidence = 0.7
            priority = ClinicalPriority.LOW
            
        return ClinicalDecision(
            decision_id=f"med_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.MEDICATION,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "medication_safety", "strength": "moderate"}],
            alternatives=[],
            contraindications=allergies,
            monitoring_requirements=["medication_effectiveness", "side_effects"],
            follow_up_actions=["medication_review", "adherence_assessment"],
            timestamp=datetime.now(),
            reasoning="Based on medication safety analysis"
        )
        
    def _generate_monitoring_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate monitoring decision"""
        monitoring_needs = context_analysis['monitoring_needs']
        
        if monitoring_needs:
            primary_need = monitoring_needs[0]
            recommendation = f"Implement {primary_need['type']} monitoring: {primary_need['frequency']}"
            confidence = 0.8
            priority = ClinicalPriority.MEDIUM
        else:
            recommendation = "Routine monitoring schedule is appropriate"
            confidence = 0.7
            priority = ClinicalPriority.LOW
            
        return ClinicalDecision(
            decision_id=f"mon_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.MONITORING,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "monitoring_guidelines", "strength": "moderate"}],
            alternatives=[],
            contraindications=[],
            monitoring_requirements=[],
            follow_up_actions=["monitoring_review", "adjust_frequency"],
            timestamp=datetime.now(),
            reasoning="Based on monitoring needs analysis"
        )
        
    def _generate_referral_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate referral decision"""
        risk_factors = context_analysis['risk_factors']
        clinical_indicators = context_analysis['clinical_indicators']
        
        if any(rf['risk_level'] == 'high' for rf in risk_factors):
            recommendation = "Consider specialist referral for high-risk factors"
            confidence = 0.8
            priority = ClinicalPriority.HIGH
        elif any(ind['urgency'] == 'high' for ind in clinical_indicators):
            recommendation = "Consider specialist referral for urgent clinical indicators"
            confidence = 0.7
            priority = ClinicalPriority.MEDIUM
        else:
            recommendation = "No immediate specialist referral needed"
            confidence = 0.6
            priority = ClinicalPriority.LOW
            
        return ClinicalDecision(
            decision_id=f"ref_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.REFERRAL,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "referral_guidelines", "strength": "moderate"}],
            alternatives=[],
            contraindications=[],
            monitoring_requirements=[],
            follow_up_actions=["referral_coordination", "specialist_consultation"],
            timestamp=datetime.now(),
            reasoning="Based on risk factor and clinical indicator analysis"
        )
        
    def _generate_prevention_decision(self, request: ClinicalDecisionRequest, context_analysis: Dict[str, Any]) -> ClinicalDecision:
        """Generate prevention decision"""
        age = request.patient_context.age
        risk_factors = context_analysis['risk_factors']
        
        if age > 50:
            recommendation = "Schedule age-appropriate preventive screenings"
            confidence = 0.9
            priority = ClinicalPriority.MEDIUM
        elif any(rf['risk_level'] == 'high' for rf in risk_factors):
            recommendation = "Implement risk factor modification strategies"
            confidence = 0.8
            priority = ClinicalPriority.HIGH
        else:
            recommendation = "Continue routine preventive care"
            confidence = 0.7
            priority = ClinicalPriority.LOW
            
        return ClinicalDecision(
            decision_id=f"prev_{datetime.now().timestamp()}",
            patient_id=request.patient_context.patient_id,
            decision_type=DecisionType.PREVENTION,
            recommendation=recommendation,
            confidence=confidence,
            priority=priority,
            evidence=[{"source": "prevention_guidelines", "strength": "moderate"}],
            alternatives=[],
            contraindications=[],
            monitoring_requirements=[],
            follow_up_actions=["preventive_screening", "lifestyle_counseling"],
            timestamp=datetime.now(),
            reasoning="Based on age and risk factor analysis"
        )

# Initialize enhanced clinical context engine
enhanced_clinical_engine = EnhancedClinicalContextEngine()

# Initialize FastAPI app
app = FastAPI(
    title="Abena IHR Enhanced Clinical Decision Support",
    description="Advanced clinical decision support with TypeScript reasoning engine integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "enhanced_clinical_decision_support",
        "version": "2.0.0",
        "timestamp": datetime.now(),
        "features": [
            "hybrid_python_typescript_engine",
            "contextual_analysis",
            "trajectory_prediction",
            "advanced_risk_stratification"
        ]
    }

@app.post("/analyze-context")
async def analyze_context(patient_context: PatientContext):
    """Enhanced patient clinical context analysis"""
    try:
        analysis = await enhanced_clinical_engine.analyze_patient_context(patient_context)
        return {
            "patient_id": patient_context.patient_id,
            "analysis": analysis,
            "timestamp": datetime.now(),
            "engine": "hybrid_python_typescript"
        }
    except Exception as e:
        logger.error(f"Error analyzing context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clinical-decision", response_model=ClinicalDecision)
async def get_clinical_decision(request: ClinicalDecisionRequest):
    """Generate enhanced clinical decision"""
    try:
        decision = await enhanced_clinical_engine.generate_clinical_decision(request)
        return decision
    except Exception as e:
        logger.error(f"Error generating clinical decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/contextual-analysis")
async def contextual_analysis(request: ContextualAnalysisRequest):
    """Perform detailed contextual analysis"""
    try:
        analysis = await enhanced_clinical_engine.analyze_patient_context(request.patient_context)
        insights = await enhanced_clinical_engine._generate_contextual_insights(request.patient_context)
        
        return {
            "patient_id": request.patient_context.patient_id,
            "contextual_analysis": analysis,
            "insights": insights if request.include_insights else [],
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error in contextual analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trajectory-prediction")
async def trajectory_prediction(request: TrajectoryPredictionRequest):
    """Predict clinical trajectory"""
    try:
        trajectory = await enhanced_clinical_engine._predict_clinical_trajectory(request.patient_context)
        
        return {
            "patient_id": request.patient_context.patient_id,
            "trajectory": trajectory,
            "time_horizon": request.time_horizon,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error in trajectory prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/decision-types")
async def get_decision_types():
    """Get available decision types"""
    return {
        "decision_types": [dt.value for dt in DecisionType],
        "priorities": [p.value for p in ClinicalPriority],
        "enhanced_features": [
            "contextual_analysis",
            "trajectory_prediction",
            "hybrid_engine_integration"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020) 