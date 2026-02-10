# application-services/predictive-analytics-engine/src/predictive_analytics_engine.py
# Updated to use Abena SDK

import asyncio
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
import json
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    patient_id: str
    prediction_type: str
    risk_score: float
    confidence: float
    contributing_factors: List[str]
    recommendations: List[str]
    timeframe: str
    generated_at: datetime
    model_version: str

@dataclass
class CohortAnalysis:
    cohort_id: str
    patient_count: int
    risk_distribution: Dict[str, int]
    top_risk_factors: List[str]
    population_recommendations: List[str]
    data_quality_score: float

class AbenaSDKPython:
    """Python SDK client for Abena services"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.auth_token = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get auth token"""
        response = await self.client.post(
            f"{self.config['auth_service_url']}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.auth_token = data['token']
        return data
    
    async def get_anonymized_dataset(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get anonymized dataset for analytics"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = await self.client.post(
            f"{self.config['privacy_service_url']}/anonymize",
            json=criteria,
            headers=headers
        )
        response.raise_for_status()
        return response.json()['anonymized_data']
    
    async def get_patient_data(self, patient_id: str, purpose: str) -> Dict[str, Any]:
        """Get complete patient data"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = await self.client.get(
            f"{self.config['data_service_url']}/patients/{patient_id}",
            params={"purpose": purpose},
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    async def log_blockchain_access(self, patient_id: str, action: str, purpose: str, metadata: Dict[str, Any]) -> str:
        """Log access to blockchain"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        try:
            response = await self.client.post(
                f"{self.config['blockchain_service_url']}/records/{patient_id}/access",
                json={"purpose": purpose, "action": action, "metadata": metadata},
                headers=headers
            )
            response.raise_for_status()
            return response.json().get('blockchain_tx_id', '')
        except Exception as e:
            logger.warning(f"Blockchain logging failed: {e}")
            return ''
    
    async def validate_service_access(self, patient_id: str, action: str, service: str) -> Dict[str, Any]:
        """Validate access permissions"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = await self.client.post(
            f"{self.config['auth_service_url']}/auth/validate-access",
            json={"patientId": patient_id, "action": action, "service": service},
            headers=headers
        )
        response.raise_for_status()
        return response.json()


class PredictiveAnalyticsEngine:
    """Enhanced Predictive Analytics Engine using Abena SDK"""
    
    def __init__(self):
        self.abena = AbenaSDKPython({
            'auth_service_url': os.getenv('AUTH_SERVICE_URL', 'http://localhost:3001'),
            'data_service_url': os.getenv('DATA_SERVICE_URL', 'http://localhost:8001'),
            'privacy_service_url': os.getenv('PRIVACY_SERVICE_URL', 'http://localhost:8002'),
            'blockchain_service_url': os.getenv('BLOCKCHAIN_SERVICE_URL', 'http://localhost:8003')
        })
        
        # Model configurations
        self.models = {
            'readmission_risk': {'version': '1.2.3', 'threshold': 0.6},
            'mortality_risk': {'version': '1.1.1', 'threshold': 0.8},
            'length_of_stay': {'version': '1.0.5', 'threshold': 0.5},
            'infection_risk': {'version': '1.3.2', 'threshold': 0.7},
            'medication_adherence': {'version': '1.1.8', 'threshold': 0.6}
        }
    
    async def authenticate(self, email: str, password: str):
        """Authenticate with Abena services"""
        await self.abena.login(email, password)
        logger.info("Successfully authenticated with Abena services")
    
    async def predict_patient_risk(
        self, 
        patient_id: str, 
        prediction_types: List[str],
        timeframe: str = '30d'
    ) -> List[PredictionResult]:
        """Generate predictions for a specific patient"""
        
        # Validate access
        access = await self.abena.validate_service_access(
            patient_id, 'predict', 'predictive_analytics'
        )
        
        if not access.get('granted', False):
            raise PermissionError(f"Access denied: {access.get('reason', 'Unknown')}")
        
        # Get patient data
        patient_data = await self.abena.get_patient_data(patient_id, 'predictive_modeling')
        
        predictions = []
        
        for prediction_type in prediction_types:
            if prediction_type in self.models:
                prediction = await self._generate_single_prediction(
                    patient_data, prediction_type, timeframe
                )
                predictions.append(prediction)
        
        # Log predictions to blockchain
        await self.abena.log_blockchain_access(
            patient_id,
            'PREDICTIONS_GENERATED',
            'predictive_analytics',
            {
                'prediction_types': prediction_types,
                'timeframe': timeframe,
                'prediction_count': len(predictions),
                'model_versions': {pt: self.models[pt]['version'] for pt in prediction_types if pt in self.models}
            }
        )
        
        return predictions
    
    async def analyze_population_cohort(
        self,
        cohort_criteria: Dict[str, Any],
        analysis_type: str = 'risk_stratification'
    ) -> CohortAnalysis:
        """Analyze a population cohort with anonymized data"""
        
        # Get anonymized dataset
        anonymized_data = await self.abena.get_anonymized_dataset({
            'dataset': cohort_criteria.get('patients', []),
            'anonymization_type': 'k-anonymity',
            'quasi_identifiers': ['age', 'gender', 'zip_code'],
            'k_value': 5
        })
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(anonymized_data)
        
        # Perform cohort analysis
        cohort_analysis = CohortAnalysis(
            cohort_id=f"cohort_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            patient_count=len(df),
            risk_distribution=self._calculate_risk_distribution(df),
            top_risk_factors=self._identify_top_risk_factors(df),
            population_recommendations=self._generate_population_recommendations(df),
            data_quality_score=self._assess_cohort_data_quality(df)
        )
        
        # Log cohort analysis
        await self.abena.log_blockchain_access(
            'population_cohort',
            'COHORT_ANALYSIS_PERFORMED',
            'population_health_analytics',
            {
                'cohort_id': cohort_analysis.cohort_id,
                'patient_count': cohort_analysis.patient_count,
                'analysis_type': analysis_type,
                'data_quality_score': cohort_analysis.data_quality_score
            }
        )
        
        return cohort_analysis
    
    async def predict_outbreak_risk(
        self,
        facility_id: str,
        infection_type: str = 'general'
    ) -> Dict[str, Any]:
        """Predict infection outbreak risk for a facility"""
        
        # Get facility data (anonymized)
        facility_data = await self.abena.get_anonymized_dataset({
            'criteria': {'facility_id': facility_id},
            'anonymization_type': 'differential-privacy',
            'epsilon': 1.0
        })
        
        # Analyze infection patterns
        outbreak_risk = self._calculate_outbreak_risk(facility_data, infection_type)
        
        # Generate recommendations
        recommendations = self._generate_outbreak_recommendations(outbreak_risk)
        
        result = {
            'facility_id': facility_id,
            'infection_type': infection_type,
            'risk_score': outbreak_risk['risk_score'],
            'risk_level': outbreak_risk['risk_level'],
            'contributing_factors': outbreak_risk['factors'],
            'recommendations': recommendations,
            'confidence': outbreak_risk['confidence'],
            'timeframe': '14d',
            'generated_at': datetime.now().isoformat()
        }
        
        # Log outbreak prediction
        await self.abena.log_blockchain_access(
            facility_id,
            'OUTBREAK_RISK_PREDICTED',
            'infection_control',
            result
        )
        
        return result
    
    async def generate_treatment_recommendations(
        self,
        patient_id: str,
        condition: str,
        current_treatments: List[str] = None
    ) -> Dict[str, Any]:
        """Generate evidence-based treatment recommendations"""
        
        # Validate access
        access = await self.abena.validate_service_access(
            patient_id, 'treatment_recommend', 'predictive_analytics'
        )
        
        if not access.get('granted', False):
            raise PermissionError(f"Access denied: {access.get('reason', 'Unknown')}")
        
        # Get patient data
        patient_data = await self.abena.get_patient_data(patient_id, 'treatment_optimization')
        
        # Generate recommendations based on condition and patient history
        recommendations = await self._generate_treatment_recommendations(
            patient_data, condition, current_treatments or []
        )
        
        # Log recommendation generation
        await self.abena.log_blockchain_access(
            patient_id,
            'TREATMENT_RECOMMENDATIONS_GENERATED',
            'clinical_decision_support',
            {
                'condition': condition,
                'recommendation_count': len(recommendations['treatments']),
                'evidence_level': recommendations['evidence_level']
            }
        )
        
        return recommendations
    
    async def monitor_patient_deterioration(
        self,
        patient_id: str,
        monitoring_duration: str = '24h'
    ) -> Dict[str, Any]:
        """Real-time patient deterioration monitoring"""
        
        # Get recent patient data
        patient_data = await self.abena.get_patient_data(patient_id, 'deterioration_monitoring')
        
        # Analyze deterioration indicators
        deterioration_score = self._calculate_deterioration_score(patient_data)
        
        # Generate early warning if needed
        if deterioration_score > 0.7:
            early_warning = await self._generate_early_warning(patient_data, deterioration_score)
        else:
            early_warning = None
        
        result = {
            'patient_id': patient_id,
            'deterioration_score': deterioration_score,
            'risk_level': self._categorize_risk_level(deterioration_score),
            'trending': self._calculate_trend(patient_data),
            'early_warning': early_warning,
            'monitoring_recommendations': self._get_monitoring_recommendations(deterioration_score),
            'next_assessment': self._calculate_next_assessment_time(deterioration_score),
            'generated_at': datetime.now().isoformat()
        }
        
        # Log monitoring
        await self.abena.log_blockchain_access(
            patient_id,
            'DETERIORATION_MONITORING',
            'patient_safety',
            {
                'deterioration_score': deterioration_score,
                'early_warning_triggered': early_warning is not None
            }
        )
        
        return result
    
    # ================================
    # PRIVATE PREDICTION METHODS
    # ================================
    
    async def _generate_single_prediction(
        self, 
        patient_data: Dict[str, Any], 
        prediction_type: str, 
        timeframe: str
    ) -> PredictionResult:
        """Generate a single prediction for a patient"""
        
        # Extract features from patient data
        features = self._extract_features(patient_data, prediction_type)
        
        # Apply appropriate model
        if prediction_type == 'readmission_risk':
            risk_score, factors = self._predict_readmission_risk(features)
        elif prediction_type == 'mortality_risk':
            risk_score, factors = self._predict_mortality_risk(features)
        elif prediction_type == 'length_of_stay':
            risk_score, factors = self._predict_length_of_stay(features)
        elif prediction_type == 'infection_risk':
            risk_score, factors = self._predict_infection_risk(features)
        elif prediction_type == 'medication_adherence':
            risk_score, factors = self._predict_medication_adherence(features)
        else:
            raise ValueError(f"Unknown prediction type: {prediction_type}")
        
        # Calculate confidence
        confidence = self._calculate_prediction_confidence(features, prediction_type)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(prediction_type, risk_score, factors)
        
        return PredictionResult(
            patient_id=patient_data['patient']['patient_id'],
            prediction_type=prediction_type,
            risk_score=risk_score,
            confidence=confidence,
            contributing_factors=factors,
            recommendations=recommendations,
            timeframe=timeframe,
            generated_at=datetime.now(),
            model_version=self.models[prediction_type]['version']
        )
    
    def _extract_features(self, patient_data: Dict[str, Any], prediction_type: str) -> Dict[str, Any]:
        """Extract relevant features from patient data"""
        features = {
            'age': self._calculate_age(patient_data['patient']['demographics'].get('birthDate')),
            'gender': patient_data['patient']['demographics'].get('gender'),
            'chronic_conditions': self._extract_chronic_conditions(patient_data['healthRecords']),
            'recent_vitals': self._extract_recent_vitals(patient_data['healthRecords']),
            'lab_values': self._extract_lab_values(patient_data['healthRecords']),
            'medications': self._extract_medications(patient_data['healthRecords']),
            'encounters': self._extract_encounters(patient_data['healthRecords'])
        }
        
        # Add prediction-specific features
        if prediction_type == 'readmission_risk':
            features.update({
                'recent_admissions': self._count_recent_admissions(features['encounters']),
                'comorbidity_count': len(features['chronic_conditions']),
                'polypharmacy': len(features['medications']) > 5
            })
        elif prediction_type == 'infection_risk':
            features.update({
                'wbc_count': self._get_latest_lab_value(features['lab_values'], 'wbc'),
                'temperature': self._get_latest_vital(features['recent_vitals'], 'temperature'),
                'invasive_devices': self._count_invasive_devices(patient_data)
            })
        
        return features
    
    def _predict_readmission_risk(self, features: Dict[str, Any]) -> tuple:
        """Predict 30-day readmission risk"""
        risk_score = 0.1  # Base risk
        factors = []
        
        # Age factor
        age = features.get('age', 0)
        if age > 65:
            risk_score += 0.2
            factors.append('Age > 65 years')
        if age > 80:
            risk_score += 0.1
            factors.append('Age > 80 years')
        
        # Comorbidities
        comorbidity_count = features.get('comorbidity_count', 0)
        if comorbidity_count > 2:
            risk_score += 0.3
            factors.append(f'{comorbidity_count} chronic conditions')
        
        # Recent admissions
        recent_admissions = features.get('recent_admissions', 0)
        if recent_admissions > 0:
            risk_score += 0.4
            factors.append('Recent hospital admission')
        
        # Polypharmacy
        if features.get('polypharmacy', False):
            risk_score += 0.2
            factors.append('Polypharmacy (>5 medications)')
        
        # Specific conditions
        conditions = features.get('chronic_conditions', [])
        if 'heart_failure' in conditions:
            risk_score += 0.3
            factors.append('Chronic heart failure')
        if 'copd' in conditions:
            risk_score += 0.25
            factors.append('COPD')
        
        return min(1.0, risk_score), factors
    
    def _predict_mortality_risk(self, features: Dict[str, Any]) -> tuple:
        """Predict mortality risk"""
        risk_score = 0.05  # Base risk
        factors = []
        
        # Age is a strong predictor
        age = features.get('age', 0)
        if age > 75:
            risk_score += 0.3
            factors.append('Advanced age (>75)')
        
        # Critical vitals
        vitals = features.get('recent_vitals', {})
        if vitals.get('heart_rate', 0) > 120:
            risk_score += 0.2
            factors.append('Tachycardia')
        if vitals.get('blood_pressure_systolic', 0) < 90:
            risk_score += 0.3
            factors.append('Hypotension')
        if vitals.get('oxygen_saturation', 100) < 90:
            risk_score += 0.4
            factors.append('Severe hypoxemia')
        
        # Lab values
        lab_values = features.get('lab_values', {})
        if lab_values.get('creatinine', 0) > 2.0:
            risk_score += 0.25
            factors.append('Elevated creatinine')
        if lab_values.get('troponin', 0) > 0.1:
            risk_score += 0.4
            factors.append('Elevated troponin')
        
        return min(1.0, risk_score), factors
    
    def _predict_length_of_stay(self, features: Dict[str, Any]) -> tuple:
        """Predict length of stay"""
        los_score = 0.2  # Base score (shorter stay)
        factors = []
        
        # Age factor
        age = features.get('age', 0)
        if age > 70:
            los_score += 0.3
            factors.append('Advanced age')
        
        # Comorbidities
        comorbidity_count = len(features.get('chronic_conditions', []))
        if comorbidity_count > 3:
            los_score += 0.4
            factors.append(f'{comorbidity_count} comorbidities')
        
        # Specific conditions that extend stay
        conditions = features.get('chronic_conditions', [])
        if 'diabetes' in conditions:
            los_score += 0.2
            factors.append('Diabetes')
        if 'renal_failure' in conditions:
            los_score += 0.3
            factors.append('Renal failure')
        
        return min(1.0, los_score), factors
    
    def _predict_infection_risk(self, features: Dict[str, Any]) -> tuple:
        """Predict infection risk"""
        risk_score = 0.1  # Base risk
        factors = []
        
        # WBC count
        wbc = features.get('wbc_count', 0)
        if wbc > 12000:
            risk_score += 0.3
            factors.append('Elevated WBC count')
        elif wbc < 4000:
            risk_score += 0.2
            factors.append('Low WBC count')
        
        # Temperature
        temp = features.get('temperature', 98.6)
        if temp > 100.4:
            risk_score += 0.4
            factors.append('Fever')
        
        # Invasive devices
        invasive_devices = features.get('invasive_devices', 0)
        if invasive_devices > 0:
            risk_score += 0.3
            factors.append(f'{invasive_devices} invasive devices')
        
        # Recent surgery
        encounters = features.get('encounters', [])
        if any('surgery' in enc.get('type', '').lower() for enc in encounters):
            risk_score += 0.3
            factors.append('Recent surgery')
        
        return min(1.0, risk_score), factors
    
    def _predict_medication_adherence(self, features: Dict[str, Any]) -> tuple:
        """Predict medication adherence"""
        adherence_score = 0.7  # Base adherence
        factors = []
        
        # Age factor
        age = features.get('age', 0)
        if age > 80:
            adherence_score -= 0.2
            factors.append('Advanced age may affect adherence')
        
        # Number of medications
        med_count = len(features.get('medications', []))
        if med_count > 8:
            adherence_score -= 0.3
            factors.append('High medication burden')
        elif med_count > 5:
            adherence_score -= 0.2
            factors.append('Multiple medications')
        
        # Cognitive conditions
        conditions = features.get('chronic_conditions', [])
        if 'dementia' in conditions:
            adherence_score -= 0.4
            factors.append('Cognitive impairment')
        if 'depression' in conditions:
            adherence_score -= 0.2
            factors.append('Depression')
        
        return max(0.0, adherence_score), factors
    
    def _calculate_prediction_confidence(self, features: Dict[str, Any], prediction_type: str) -> float:
        """Calculate confidence in prediction based on data quality"""
        confidence = 0.8  # Base confidence
        
        # Data completeness
        if len(features.get('recent_vitals', {})) > 0:
            confidence += 0.1
        if len(features.get('lab_values', {})) > 0:
            confidence += 0.1
        
        # Recent data availability
        if features.get('age', 0) > 0:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _generate_recommendations(self, prediction_type: str, risk_score: float, factors: List[str]) -> List[str]:
        """Generate recommendations based on prediction type and risk factors"""
        recommendations = []
        
        if prediction_type == 'readmission_risk':
            if risk_score > 0.7:
                recommendations.extend([
                    'Schedule follow-up appointment within 7 days',
                    'Implement care transition program',
                    'Review medication reconciliation',
                    'Assess social support needs'
                ])
            elif risk_score > 0.5:
                recommendations.extend([
                    'Schedule follow-up appointment within 14 days',
                    'Review discharge instructions',
                    'Ensure medication understanding'
                ])
        
        elif prediction_type == 'mortality_risk':
            if risk_score > 0.8:
                recommendations.extend([
                    'Immediate clinical assessment required',
                    'Consider ICU transfer',
                    'Notify attending physician',
                    'Implement rapid response protocol'
                ])
            elif risk_score > 0.6:
                recommendations.extend([
                    'Increase monitoring frequency',
                    'Review treatment plan',
                    'Consider specialist consultation'
                ])
        
        elif prediction_type == 'infection_risk':
            if risk_score > 0.7:
                recommendations.extend([
                    'Initiate infection control protocols',
                    'Order additional diagnostic tests',
                    'Consider antibiotic prophylaxis',
                    'Implement isolation if indicated'
                ])
        
        elif prediction_type == 'medication_adherence':
            if risk_score < 0.5:
                recommendations.extend([
                    'Implement medication reminder system',
                    'Simplify medication regimen if possible',
                    'Assess barriers to adherence',
                    'Consider pill organizer or blister packs'
                ])
        
        return recommendations
    
    # ================================
    # HELPER METHODS
    # ================================
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date"""
        if not birth_date:
            return 0
        try:
            birth = datetime.strptime(birth_date, '%Y-%m-%d')
            today = datetime.now()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _extract_chronic_conditions(self, health_records: List[Dict]) -> List[str]:
        """Extract chronic conditions from health records"""
        conditions = []
        for record in health_records:
            if 'diagnoses' in record:
                for diagnosis in record['diagnoses']:
                    if diagnosis.get('chronic', False):
                        conditions.append(diagnosis.get('code', ''))
        return list(set(conditions))
    
    def _extract_recent_vitals(self, health_records: List[Dict]) -> Dict[str, float]:
        """Extract recent vital signs"""
        vitals = {}
        for record in health_records:
            if 'vitals' in record:
                for vital in record['vitals']:
                    vitals[vital.get('type', '')] = vital.get('value', 0)
        return vitals
    
    def _extract_lab_values(self, health_records: List[Dict]) -> Dict[str, float]:
        """Extract lab values"""
        labs = {}
        for record in health_records:
            if 'labs' in record:
                for lab in record['labs']:
                    labs[lab.get('test', '')] = lab.get('value', 0)
        return labs
    
    def _extract_medications(self, health_records: List[Dict]) -> List[str]:
        """Extract medications"""
        medications = []
        for record in health_records:
            if 'medications' in record:
                for med in record['medications']:
                    medications.append(med.get('name', ''))
        return medications
    
    def _extract_encounters(self, health_records: List[Dict]) -> List[Dict]:
        """Extract encounters"""
        encounters = []
        for record in health_records:
            if 'encounters' in record:
                encounters.extend(record['encounters'])
        return encounters
    
    def _count_recent_admissions(self, encounters: List[Dict]) -> int:
        """Count recent hospital admissions"""
        recent_date = datetime.now() - timedelta(days=30)
        count = 0
        for encounter in encounters:
            if encounter.get('type') == 'hospitalization':
                encounter_date = datetime.strptime(encounter.get('date', '2000-01-01'), '%Y-%m-%d')
                if encounter_date > recent_date:
                    count += 1
        return count
    
    def _get_latest_lab_value(self, lab_values: Dict[str, float], test: str) -> float:
        """Get latest lab value for specific test"""
        return lab_values.get(test, 0)
    
    def _get_latest_vital(self, vitals: Dict[str, float], vital: str) -> float:
        """Get latest vital sign"""
        return vitals.get(vital, 0)
    
    def _count_invasive_devices(self, patient_data: Dict[str, Any]) -> int:
        """Count invasive devices"""
        count = 0
        if 'devices' in patient_data:
            for device in patient_data['devices']:
                if device.get('invasive', False):
                    count += 1
        return count
    
    # ================================
    # COHORT ANALYSIS METHODS
    # ================================
    
    def _calculate_risk_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calculate risk distribution for cohort"""
        return {
            'low': len(df[df.get('risk_score', 0) < 0.3]),
            'medium': len(df[(df.get('risk_score', 0) >= 0.3) & (df.get('risk_score', 0) < 0.7)]),
            'high': len(df[df.get('risk_score', 0) >= 0.7])
        }
    
    def _identify_top_risk_factors(self, df: pd.DataFrame) -> List[str]:
        """Identify top risk factors in cohort"""
        # This would analyze the most common risk factors across the cohort
        return ['Age > 65', 'Multiple comorbidities', 'Recent hospitalization', 'Polypharmacy']
    
    def _generate_population_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate population-level recommendations"""
        return [
            'Implement care transition programs for high-risk patients',
            'Develop medication management protocols',
            'Establish early warning systems',
            'Create targeted intervention programs'
        ]
    
    def _assess_cohort_data_quality(self, df: pd.DataFrame) -> float:
        """Assess data quality score for cohort"""
        # Calculate completeness and quality metrics
        completeness = df.notna().mean().mean()
        return min(1.0, completeness)
    
    # ================================
    # OUTBREAK PREDICTION METHODS
    # ================================
    
    def _calculate_outbreak_risk(self, facility_data: List[Dict], infection_type: str) -> Dict[str, Any]:
        """Calculate outbreak risk for facility"""
        # Analyze infection patterns and calculate risk
        risk_score = 0.3  # Base risk
        factors = []
        
        # Count recent infections
        recent_infections = sum(1 for record in facility_data if record.get('infection_type') == infection_type)
        if recent_infections > 5:
            risk_score += 0.4
            factors.append(f'{recent_infections} recent infections')
        
        # Analyze transmission patterns
        if any(record.get('transmission_risk', 0) > 0.7 for record in facility_data):
            risk_score += 0.3
            factors.append('High transmission risk identified')
        
        return {
            'risk_score': min(1.0, risk_score),
            'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
            'factors': factors,
            'confidence': 0.8
        }
    
    def _generate_outbreak_recommendations(self, outbreak_risk: Dict[str, Any]) -> List[str]:
        """Generate outbreak prevention recommendations"""
        recommendations = []
        
        if outbreak_risk['risk_level'] == 'high':
            recommendations.extend([
                'Implement enhanced infection control protocols',
                'Increase environmental cleaning frequency',
                'Consider visitor restrictions',
                'Activate outbreak response team'
            ])
        elif outbreak_risk['risk_level'] == 'medium':
            recommendations.extend([
                'Review infection control procedures',
                'Monitor infection rates closely',
                'Reinforce hand hygiene protocols'
            ])
        
        return recommendations
    
    # ================================
    # TREATMENT RECOMMENDATION METHODS
    # ================================
    
    async def _generate_treatment_recommendations(
        self, 
        patient_data: Dict[str, Any], 
        condition: str, 
        current_treatments: List[str]
    ) -> Dict[str, Any]:
        """Generate treatment recommendations"""
        recommendations = {
            'treatments': [],
            'evidence_level': 'moderate',
            'contraindications': [],
            'monitoring_requirements': []
        }
        
        # Generate condition-specific recommendations
        if condition.lower() == 'diabetes':
            recommendations['treatments'] = [
                'Metformin (first-line therapy)',
                'Lifestyle modifications',
                'Regular blood glucose monitoring'
            ]
            recommendations['monitoring_requirements'] = [
                'HbA1c every 3-6 months',
                'Annual eye exam',
                'Foot examination'
            ]
        
        elif condition.lower() == 'hypertension':
            recommendations['treatments'] = [
                'ACE inhibitor or ARB',
                'Thiazide diuretic',
                'Lifestyle modifications'
            ]
            recommendations['monitoring_requirements'] = [
                'Blood pressure monitoring',
                'Renal function tests',
                'Electrolyte monitoring'
            ]
        
        return recommendations
    
    # ================================
    # DETERIORATION MONITORING METHODS
    # ================================
    
    def _calculate_deterioration_score(self, patient_data: Dict[str, Any]) -> float:
        """Calculate patient deterioration score"""
        score = 0.1  # Base score
        
        # Analyze vital signs trends
        vitals = patient_data.get('recent_vitals', {})
        if vitals.get('heart_rate', 0) > 100:
            score += 0.2
        if vitals.get('blood_pressure_systolic', 0) < 100:
            score += 0.3
        if vitals.get('oxygen_saturation', 100) < 95:
            score += 0.3
        
        # Analyze lab trends
        labs = patient_data.get('lab_values', {})
        if labs.get('creatinine', 0) > 1.5:
            score += 0.2
        if labs.get('lactate', 0) > 2.0:
            score += 0.4
        
        return min(1.0, score)
    
    async def _generate_early_warning(self, patient_data: Dict[str, Any], deterioration_score: float) -> Dict[str, Any]:
        """Generate early warning alert"""
        return {
            'alert_level': 'high' if deterioration_score > 0.8 else 'medium',
            'message': 'Patient showing signs of clinical deterioration',
            'recommended_actions': [
                'Immediate clinical assessment',
                'Consider rapid response team activation',
                'Review current treatment plan'
            ],
            'escalation_required': deterioration_score > 0.8
        }
    
    def _categorize_risk_level(self, score: float) -> str:
        """Categorize risk level based on score"""
        if score > 0.8:
            return 'critical'
        elif score > 0.6:
            return 'high'
        elif score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_trend(self, patient_data: Dict[str, Any]) -> str:
        """Calculate trend direction"""
        # Analyze recent data trends
        return 'stable'  # Placeholder
    
    def _get_monitoring_recommendations(self, score: float) -> List[str]:
        """Get monitoring recommendations based on score"""
        if score > 0.8:
            return ['Continuous monitoring', 'Hourly vital signs', 'Consider ICU transfer']
        elif score > 0.6:
            return ['Frequent monitoring', '4-hourly vital signs', 'Close observation']
        else:
            return ['Routine monitoring', 'Daily vital signs']
    
    def _calculate_next_assessment_time(self, score: float) -> str:
        """Calculate next assessment time"""
        if score > 0.8:
            return '1 hour'
        elif score > 0.6:
            return '4 hours'
        else:
            return '24 hours'


# Example usage
async def main():
    """Example usage of the Predictive Analytics Engine"""
    engine = PredictiveAnalyticsEngine()
    
    # Authenticate
    await engine.authenticate('analyst@healthcare.org', 'secure_password')
    
    # Generate predictions for a patient
    predictions = await engine.predict_patient_risk(
        patient_id='P12345',
        prediction_types=['readmission_risk', 'mortality_risk'],
        timeframe='30d'
    )
    
    print(f"Generated {len(predictions)} predictions")
    for pred in predictions:
        print(f"{pred.prediction_type}: {pred.risk_score:.2f} risk score")


if __name__ == "__main__":
    asyncio.run(main()) 