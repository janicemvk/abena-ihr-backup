"""
Integrated Architecture Solution for Abena IHR System

This module provides the unified architecture that integrates clinical context analysis,
predictive analytics, dynamic learning, and conflict resolution for comprehensive
treatment planning and continuous improvement.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
from abc import ABC, abstractmethod

from .conflict_resolution import ConflictResolution, ClinicalRecommendation, PredictionResult
from .model_version_manager import ModelVersionManager, ValidationMetrics

logger = logging.getLogger(__name__)


@dataclass
class PatientData:
    """Patient information for analysis"""
    patient_id: str
    age: int
    gender: str
    medical_history: List[str]
    current_medications: List[str]
    vital_signs: Dict[str, float]
    lab_results: Dict[str, float]
    allergies: List[str]
    comorbidities: List[str]


@dataclass
class TreatmentOption:
    """Treatment option with associated metadata"""
    treatment_id: str
    treatment_name: str
    dosage: str
    duration: str
    contraindications: List[str]
    side_effects: List[str]
    cost_estimate: float
    evidence_level: str


@dataclass
class ClinicalContext:
    """Clinical context analysis results"""
    patient_id: str
    primary_diagnosis: str
    severity_score: float
    treatment_options: List[TreatmentOption]
    clinical_guidelines: List[str]
    risk_factors: List[str]
    clinical_notes: str


@dataclass
class PredictiveResult:
    """Predictive analytics result for treatment"""
    treatment_id: str
    success_probability: float
    risk_score: float
    expected_recovery_time: int  # days
    confidence_interval: tuple
    feature_importance: Dict[str, float]
    model_version: str


@dataclass
class TreatmentOutcome:
    """Treatment outcome data for feedback"""
    patient_id: str
    treatment_id: str
    outcome_success: bool
    recovery_time: int  # days
    side_effects_observed: List[str]
    patient_satisfaction: float  # 1-10 scale
    readmission_required: bool
    outcome_date: datetime


@dataclass
class FinalRecommendation:
    """Final treatment recommendation after conflict resolution"""
    patient_id: str
    recommended_treatment: TreatmentOption
    confidence_score: float
    reasoning: str
    alternative_treatments: List[TreatmentOption]
    monitoring_requirements: List[str]
    follow_up_schedule: List[str]
    risk_mitigation: List[str]


class ClinicalContextModule:
    """
    Clinical Context Analysis Module
    Analyzes patient data against clinical guidelines and evidence-based medicine
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.guidelines_db = self._load_clinical_guidelines()
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for clinical context analysis"""
        return {
            'severity_threshold': 0.7,
            'max_treatment_options': 5,
            'evidence_level_priority': ['Level I', 'Level II', 'Level III'],
            'contraindication_strict': True
        }
    
    def _load_clinical_guidelines(self) -> Dict:
        """Load clinical guidelines database"""
        # Placeholder - would load from actual clinical guidelines database
        return {
            'hypertension': {
                'first_line': ['ACE inhibitors', 'ARBs', 'CCBs', 'Thiazide diuretics'],
                'contraindications': {'ACE inhibitors': ['pregnancy', 'angioedema']},
                'monitoring': ['blood_pressure', 'kidney_function', 'electrolytes']
            },
            'diabetes_t2': {
                'first_line': ['Metformin', 'SGLT2 inhibitors'],
                'contraindications': {'Metformin': ['kidney_disease', 'liver_disease']},
                'monitoring': ['HbA1c', 'kidney_function', 'cardiovascular_risk']
            }
        }
    
    def analyze_patient(self, patient_data: PatientData) -> ClinicalContext:
        """
        Analyze patient data to generate clinical context and treatment options
        
        Args:
            patient_data: Patient information for analysis
            
        Returns:
            ClinicalContext with treatment options and clinical guidance
        """
        self.logger.info(f"Analyzing clinical context for patient: {patient_data.patient_id}")
        
        # Determine primary diagnosis and severity
        primary_diagnosis = self._determine_primary_diagnosis(patient_data)
        severity_score = self._calculate_severity_score(patient_data, primary_diagnosis)
        
        # Generate treatment options based on guidelines
        treatment_options = self._generate_treatment_options(patient_data, primary_diagnosis)
        
        # Filter for contraindications
        safe_treatments = self._filter_contraindications(treatment_options, patient_data)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(patient_data)
        
        return ClinicalContext(
            patient_id=patient_data.patient_id,
            primary_diagnosis=primary_diagnosis,
            severity_score=severity_score,
            treatment_options=safe_treatments,
            clinical_guidelines=self._get_relevant_guidelines(primary_diagnosis),
            risk_factors=risk_factors,
            clinical_notes=f"Clinical analysis completed for {primary_diagnosis}"
        )
    
    def _determine_primary_diagnosis(self, patient_data: PatientData) -> str:
        """Determine primary diagnosis from patient data"""
        # Placeholder - would use clinical decision support algorithms
        if 'hypertension' in patient_data.medical_history:
            return 'hypertension'
        elif 'diabetes' in patient_data.medical_history:
            return 'diabetes_t2'
        else:
            return 'general_assessment'
    
    def _calculate_severity_score(self, patient_data: PatientData, diagnosis: str) -> float:
        """Calculate severity score based on patient data and diagnosis"""
        # Placeholder - would use validated clinical severity scoring
        base_score = 0.5
        
        # Age factor
        if patient_data.age > 65:
            base_score += 0.2
        
        # Comorbidity factor
        comorbidity_count = len(patient_data.comorbidities)
        base_score += min(comorbidity_count * 0.1, 0.3)
        
        return min(base_score, 1.0)
    
    def _generate_treatment_options(self, patient_data: PatientData, diagnosis: str) -> List[TreatmentOption]:
        """Generate treatment options based on diagnosis and guidelines"""
        guidelines = self.guidelines_db.get(diagnosis, {})
        first_line = guidelines.get('first_line', [])
        
        treatments = []
        for i, treatment in enumerate(first_line[:self.config['max_treatment_options']]):
            treatments.append(TreatmentOption(
                treatment_id=f"TRT_{diagnosis}_{i+1:03d}",
                treatment_name=treatment,
                dosage="Standard dosage per guidelines",
                duration="As per clinical guidelines",
                contraindications=guidelines.get('contraindications', {}).get(treatment, []),
                side_effects=self._get_side_effects(treatment),
                cost_estimate=self._estimate_cost(treatment),
                evidence_level="Level I"
            ))
        
        return treatments
    
    def _filter_contraindications(self, treatments: List[TreatmentOption], patient_data: PatientData) -> List[TreatmentOption]:
        """Filter treatments based on patient contraindications"""
        safe_treatments = []
        
        for treatment in treatments:
            is_safe = True
            for contraindication in treatment.contraindications:
                if contraindication in patient_data.allergies or contraindication in patient_data.medical_history:
                    is_safe = False
                    break
            
            if is_safe:
                safe_treatments.append(treatment)
            else:
                self.logger.warning(f"Treatment {treatment.treatment_name} contraindicated for patient {patient_data.patient_id}")
        
        return safe_treatments
    
    def _identify_risk_factors(self, patient_data: PatientData) -> List[str]:
        """Identify risk factors from patient data"""
        risk_factors = []
        
        if patient_data.age > 65:
            risk_factors.append("advanced_age")
        
        if len(patient_data.comorbidities) > 2:
            risk_factors.append("multiple_comorbidities")
        
        if len(patient_data.current_medications) > 5:
            risk_factors.append("polypharmacy")
        
        return risk_factors
    
    def _get_relevant_guidelines(self, diagnosis: str) -> List[str]:
        """Get relevant clinical guidelines for diagnosis"""
        return [
            f"Follow {diagnosis} clinical practice guidelines",
            "Monitor for drug interactions",
            "Regular follow-up as per protocol"
        ]
    
    def _get_side_effects(self, treatment: str) -> List[str]:
        """Get common side effects for treatment"""
        # Placeholder - would query side effects database
        side_effects_db = {
            'ACE inhibitors': ['dry_cough', 'hyperkalemia', 'angioedema'],
            'Metformin': ['gastrointestinal', 'lactic_acidosis'],
            'ARBs': ['hyperkalemia', 'dizziness']
        }
        return side_effects_db.get(treatment, ['consult_prescribing_information'])
    
    def _estimate_cost(self, treatment: str) -> float:
        """Estimate treatment cost"""
        # Placeholder - would query cost database
        cost_db = {
            'ACE inhibitors': 25.0,
            'Metformin': 15.0,
            'ARBs': 45.0,
            'SGLT2 inhibitors': 300.0
        }
        return cost_db.get(treatment, 50.0)
    
    def update_recommendation_rules(self, model_updates: Dict) -> None:
        """Update clinical recommendation rules based on model learnings"""
        self.logger.info("Updating clinical recommendation rules based on ML insights")
        # Would update guidelines database with new evidence


class PredictiveAnalyticsEngine:
    """
    Predictive Analytics Engine
    Uses machine learning models to predict treatment outcomes
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.models = self._load_models()
        self.model_version_manager = ModelVersionManager()
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for predictive analytics"""
        return {
            'confidence_threshold': 0.8,
            'feature_importance_threshold': 0.1,
            'prediction_cache_ttl': 3600,  # 1 hour
            'ensemble_voting': 'weighted'
        }
    
    def _load_models(self) -> Dict:
        """Load trained ML models"""
        # Placeholder - would load actual trained models
        return {
            'treatment_response': 'RandomForestClassifier_v1.2',
            'side_effect_prediction': 'XGBoostClassifier_v1.1',
            'recovery_time': 'LinearRegression_v1.0'
        }
    
    def predict_treatment_response(self, patient_data: PatientData, treatment: TreatmentOption) -> PredictiveResult:
        """
        Predict treatment response for patient-treatment combination
        
        Args:
            patient_data: Patient information
            treatment: Treatment option to evaluate
            
        Returns:
            PredictiveResult with prediction metrics
        """
        self.logger.info(f"Predicting treatment response for {treatment.treatment_name}")
        
        # Extract features for prediction
        features = self._extract_features(patient_data, treatment)
        
        # Run ensemble prediction
        success_prob = self._predict_success_probability(features)
        risk_score = self._predict_risk_score(features)
        recovery_time = self._predict_recovery_time(features)
        confidence_interval = self._calculate_confidence_interval(success_prob)
        feature_importance = self._get_feature_importance(features)
        
        return PredictiveResult(
            treatment_id=treatment.treatment_id,
            success_probability=success_prob,
            risk_score=risk_score,
            expected_recovery_time=recovery_time,
            confidence_interval=confidence_interval,
            feature_importance=feature_importance,
            model_version=self.models['treatment_response']
        )
    
    def _extract_features(self, patient_data: PatientData, treatment: TreatmentOption) -> Dict[str, float]:
        """Extract features for ML model prediction"""
        return {
            'age': float(patient_data.age),
            'gender_encoded': 1.0 if patient_data.gender == 'M' else 0.0,
            'comorbidity_count': float(len(patient_data.comorbidities)),
            'medication_count': float(len(patient_data.current_medications)),
            'treatment_cost': treatment.cost_estimate,
            'allergy_count': float(len(patient_data.allergies))
        }
    
    def _predict_success_probability(self, features: Dict[str, float]) -> float:
        """Predict treatment success probability"""
        # Placeholder - would use actual trained model
        base_prob = 0.75
        
        # Age factor
        if features['age'] > 65:
            base_prob -= 0.1
        
        # Comorbidity factor
        base_prob -= features['comorbidity_count'] * 0.05
        
        return max(0.1, min(0.95, base_prob))
    
    def _predict_risk_score(self, features: Dict[str, float]) -> float:
        """Predict treatment risk score"""
        # Placeholder - would use actual trained model
        base_risk = 0.2
        
        # Increase risk with age and comorbidities
        base_risk += features['age'] * 0.005
        base_risk += features['comorbidity_count'] * 0.1
        
        return max(0.05, min(0.9, base_risk))
    
    def _predict_recovery_time(self, features: Dict[str, float]) -> int:
        """Predict expected recovery time in days"""
        # Placeholder - would use actual trained model
        base_time = 14  # 2 weeks
        
        # Adjust for patient factors
        if features['age'] > 65:
            base_time += 7
        
        base_time += int(features['comorbidity_count'] * 3)
        
        return max(7, min(90, base_time))
    
    def _calculate_confidence_interval(self, probability: float) -> tuple:
        """Calculate confidence interval for prediction"""
        margin = 0.1  # ±10% margin
        return (max(0.0, probability - margin), min(1.0, probability + margin))
    
    def _get_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Get feature importance scores"""
        # Placeholder - would get from actual model
        return {
            'age': 0.25,
            'comorbidity_count': 0.30,
            'medication_count': 0.20,
            'gender_encoded': 0.15,
            'treatment_cost': 0.05,
            'allergy_count': 0.05
        }
    
    def update_models(self, model_updates: Dict) -> None:
        """Update ML models with new training data"""
        self.logger.info("Updating predictive models with new training data")
        
        for model_name, update_data in model_updates.items():
            if 'metrics' in update_data:
                # Use model version manager for staged deployment
                validation_metrics = ValidationMetrics(**update_data['metrics'])
                
                deployment_result = self.model_version_manager.deploy_updated_model(
                    new_model=update_data.get('model'),
                    validation_metrics=validation_metrics,
                    model_name=model_name
                )
                
                self.logger.info(f"Model deployment result: {deployment_result}")


class DynamicLearningLoop:
    """
    Dynamic Learning Loop
    Tracks recommendations and outcomes to continuously improve the system
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.recommendation_history = {}
        self.outcome_history = {}
        self.learning_buffer = []
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for dynamic learning"""
        return {
            'learning_window_days': 30,
            'min_outcomes_for_update': 10,
            'performance_improvement_threshold': 0.05,
            'outcome_tracking_enabled': True
        }
    
    def track_recommendation(self, patient_id: str, recommendation: FinalRecommendation, timestamp: datetime) -> None:
        """
        Track a treatment recommendation for future learning
        
        Args:
            patient_id: Patient identifier
            recommendation: Final treatment recommendation
            timestamp: When recommendation was made
        """
        self.logger.info(f"Tracking recommendation for patient: {patient_id}")
        
        self.recommendation_history[patient_id] = {
            'recommendation': recommendation,
            'timestamp': timestamp,
            'treatment_id': recommendation.recommended_treatment.treatment_id,
            'confidence_score': recommendation.confidence_score
        }
    
    def record_outcome(self, patient_id: str, outcome_data: TreatmentOutcome) -> None:
        """
        Record treatment outcome for learning
        
        Args:
            patient_id: Patient identifier
            outcome_data: Treatment outcome information
        """
        self.logger.info(f"Recording outcome for patient: {patient_id}")
        
        self.outcome_history[patient_id] = outcome_data
        
        # Add to learning buffer if we have both recommendation and outcome
        if patient_id in self.recommendation_history:
            learning_sample = {
                'patient_id': patient_id,
                'recommendation': self.recommendation_history[patient_id],
                'outcome': outcome_data,
                'learning_signal': self._calculate_learning_signal(
                    self.recommendation_history[patient_id], 
                    outcome_data
                )
            }
            self.learning_buffer.append(learning_sample)
    
    def _calculate_learning_signal(self, recommendation: Dict, outcome: TreatmentOutcome) -> Dict:
        """Calculate learning signal from recommendation-outcome pair"""
        predicted_confidence = recommendation['confidence_score']
        actual_success = outcome.outcome_success
        
        # Calculate prediction accuracy
        prediction_error = abs(predicted_confidence - (1.0 if actual_success else 0.0))
        
        return {
            'prediction_error': prediction_error,
            'outcome_success': actual_success,
            'recovery_time_actual': outcome.recovery_time,
            'side_effects_count': len(outcome.side_effects_observed),
            'patient_satisfaction': outcome.patient_satisfaction
        }
    
    def check_for_model_updates(self) -> Optional[Dict]:
        """
        Check if sufficient learning has occurred to trigger model updates
        
        Returns:
            Model update information if updates are needed
        """
        if len(self.learning_buffer) < self.config['min_outcomes_for_update']:
            return None
        
        # Analyze learning buffer for improvement opportunities
        recent_outcomes = self._get_recent_outcomes()
        performance_metrics = self._calculate_performance_metrics(recent_outcomes)
        
        if self._should_trigger_update(performance_metrics):
            self.logger.info("Triggering model updates based on learning buffer")
            
            update_data = {
                'treatment_response': {
                    'training_data': recent_outcomes,
                    'metrics': {
                        'accuracy': performance_metrics['accuracy'],
                        'precision': performance_metrics['precision'],
                        'recall': performance_metrics['recall'],
                        'f1_score': performance_metrics['f1_score'],
                        'improvement': performance_metrics['improvement'],
                        'validation_loss': performance_metrics['validation_loss']
                    }
                }
            }
            
            # Clear learning buffer after processing
            self.learning_buffer = []
            
            return update_data
        
        return None
    
    def _get_recent_outcomes(self) -> List[Dict]:
        """Get recent outcomes within learning window"""
        cutoff_date = datetime.now() - timedelta(days=self.config['learning_window_days'])
        
        recent_outcomes = []
        for sample in self.learning_buffer:
            outcome_date = sample['outcome'].outcome_date
            if outcome_date >= cutoff_date:
                recent_outcomes.append(sample)
        
        return recent_outcomes
    
    def _calculate_performance_metrics(self, outcomes: List[Dict]) -> Dict:
        """Calculate performance metrics from outcomes"""
        if not outcomes:
            return {}
        
        total_outcomes = len(outcomes)
        successful_outcomes = sum(1 for o in outcomes if o['outcome'].outcome_success)
        
        # Calculate basic metrics
        accuracy = successful_outcomes / total_outcomes
        
        # Placeholder for more sophisticated metrics
        precision = accuracy  # Would calculate proper precision
        recall = accuracy     # Would calculate proper recall
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate improvement vs baseline
        baseline_accuracy = 0.75  # Historical baseline
        improvement = accuracy - baseline_accuracy
        
        # Calculate validation loss (placeholder)
        validation_loss = 1 - accuracy
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'improvement': improvement,
            'validation_loss': validation_loss
        }
    
    def _should_trigger_update(self, metrics: Dict) -> bool:
        """Determine if model update should be triggered"""
        if not metrics:
            return False
        
        return metrics.get('improvement', 0) > self.config['performance_improvement_threshold']


class ConflictResolutionEngine:
    """
    Conflict Resolution Engine
    Extended version of ConflictResolution for integrated system
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.conflict_resolver = ConflictResolution(config)
        self.logger = logging.getLogger(__name__)
    
    def resolve_conflicts(self, clinical_context: ClinicalContext, prediction_results: List[PredictiveResult]) -> FinalRecommendation:
        """
        Resolve conflicts between clinical recommendations and predictive results
        
        Args:
            clinical_context: Clinical analysis results
            prediction_results: Predictive analytics results for each treatment
            
        Returns:
            FinalRecommendation with final treatment decision
        """
        self.logger.info(f"Resolving conflicts for patient: {clinical_context.patient_id}")
        
        # Find best treatment from predictions
        best_prediction = max(prediction_results, key=lambda x: x.success_probability)
        
        # Convert to format expected by conflict resolver
        clinical_rec = self._convert_to_clinical_recommendation(clinical_context, best_prediction)
        prediction_result = self._convert_to_prediction_result(best_prediction)
        
        # Use existing conflict resolution logic
        resolution_result = self.conflict_resolver.resolve_recommendation_conflict(
            clinical_rec, prediction_result
        )
        
        # Convert back to integrated system format
        return self._create_final_recommendation(
            clinical_context, 
            best_prediction, 
            resolution_result,
            prediction_results
        )
    
    def _convert_to_clinical_recommendation(self, context: ClinicalContext, best_prediction: PredictiveResult) -> ClinicalRecommendation:
        """Convert clinical context to ConflictResolution format"""
        # Find the treatment that matches the best prediction
        best_treatment = None
        for treatment in context.treatment_options:
            if treatment.treatment_id == best_prediction.treatment_id:
                best_treatment = treatment
                break
        
        if not best_treatment:
            best_treatment = context.treatment_options[0]  # Fallback
        
        return ClinicalRecommendation(
            treatment_id=best_treatment.treatment_id,
            treatment_name=best_treatment.treatment_name,
            confidence_score=0.8,  # Default clinical confidence
            evidence_level=best_treatment.evidence_level,
            alternative_treatments=[t.treatment_name for t in context.treatment_options[1:3]],
            contraindications=best_treatment.contraindications
        )
    
    def _convert_to_prediction_result(self, prediction: PredictiveResult) -> PredictionResult:
        """Convert predictive result to ConflictResolution format"""
        return PredictionResult(
            success_probability=prediction.success_probability,
            risk_factors=[f"risk_score_{prediction.risk_score}"],
            confidence_interval=prediction.confidence_interval,
            model_version=prediction.model_version,
            features_used=list(prediction.feature_importance.keys())
        )
    
    def _create_final_recommendation(self, context: ClinicalContext, best_prediction: PredictiveResult, 
                                   resolution: Any, all_predictions: List[PredictiveResult]) -> FinalRecommendation:
        """Create final recommendation from resolution result"""
        
        # Find recommended treatment
        recommended_treatment = None
        for treatment in context.treatment_options:
            if treatment.treatment_id == best_prediction.treatment_id:
                recommended_treatment = treatment
                break
        
        if not recommended_treatment:
            recommended_treatment = context.treatment_options[0]
        
        # Get alternative treatments
        alternative_treatments = []
        for pred in sorted(all_predictions, key=lambda x: x.success_probability, reverse=True)[1:3]:
            for treatment in context.treatment_options:
                if treatment.treatment_id == pred.treatment_id:
                    alternative_treatments.append(treatment)
                    break
        
        return FinalRecommendation(
            patient_id=context.patient_id,
            recommended_treatment=recommended_treatment,
            confidence_score=resolution.confidence_level,
            reasoning=resolution.reason,
            alternative_treatments=alternative_treatments,
            monitoring_requirements=self._get_monitoring_requirements(recommended_treatment),
            follow_up_schedule=self._get_follow_up_schedule(context.severity_score),
            risk_mitigation=self._get_risk_mitigation(context.risk_factors)
        )
    
    def _get_monitoring_requirements(self, treatment: TreatmentOption) -> List[str]:
        """Get monitoring requirements for treatment"""
        monitoring_map = {
            'ACE inhibitors': ['blood_pressure', 'kidney_function', 'potassium'],
            'Metformin': ['kidney_function', 'HbA1c', 'vitamin_B12'],
            'ARBs': ['blood_pressure', 'kidney_function', 'potassium']
        }
        return monitoring_map.get(treatment.treatment_name, ['standard_monitoring'])
    
    def _get_follow_up_schedule(self, severity_score: float) -> List[str]:
        """Get follow-up schedule based on severity"""
        if severity_score > 0.7:
            return ['1_week', '1_month', '3_months']
        elif severity_score > 0.4:
            return ['2_weeks', '1_month', '3_months']
        else:
            return ['1_month', '3_months']
    
    def _get_risk_mitigation(self, risk_factors: List[str]) -> List[str]:
        """Get risk mitigation strategies"""
        mitigations = []
        
        if 'advanced_age' in risk_factors:
            mitigations.append('Lower starting dose consideration')
        
        if 'multiple_comorbidities' in risk_factors:
            mitigations.append('Enhanced monitoring protocol')
        
        if 'polypharmacy' in risk_factors:
            mitigations.append('Drug interaction screening')
        
        return mitigations or ['Standard precautions']


class AbenaIntegratedSystem:
    """
    Main Integrated System for Abena IHR
    Orchestrates clinical context, predictive analytics, dynamic learning, and conflict resolution
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.clinical_context = ClinicalContextModule(self.config.get('clinical'))
        self.predictive_engine = PredictiveAnalyticsEngine(self.config.get('predictive'))
        self.feedback_loop = DynamicLearningLoop(self.config.get('learning'))
        self.conflict_resolver = ConflictResolutionEngine(self.config.get('conflict'))
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Abena Integrated System initialized successfully")
    
    def generate_treatment_plan(self, patient_data: PatientData) -> FinalRecommendation:
        """
        Generate comprehensive treatment plan for patient
        
        Args:
            patient_data: Complete patient information
            
        Returns:
            FinalRecommendation with treatment plan and monitoring
        """
        self.logger.info(f"Generating treatment plan for patient: {patient_data.patient_id}")
        
        try:
            # Step 1: Clinical Context Analysis
            self.logger.info("Step 1: Analyzing clinical context")
            clinical_context = self.clinical_context.analyze_patient(patient_data)
            
            # Step 2: Predictive Analysis of Recommendations
            self.logger.info("Step 2: Running predictive analysis")
            prediction_results = []
            for treatment in clinical_context.treatment_options:
                prediction = self.predictive_engine.predict_treatment_response(
                    patient_data, treatment
                )
                prediction_results.append(prediction)
            
            # Step 3: Conflict Resolution
            self.logger.info("Step 3: Resolving conflicts")
            final_recommendation = self.conflict_resolver.resolve_conflicts(
                clinical_context, 
                prediction_results
            )
            
            # Step 4: Prepare for Feedback Loop
            self.logger.info("Step 4: Setting up feedback tracking")
            self.feedback_loop.track_recommendation(
                patient_data.patient_id, 
                final_recommendation,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Treatment plan generated successfully for patient: {patient_data.patient_id}")
            return final_recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating treatment plan: {str(e)}")
            raise
    
    def process_treatment_outcome(self, patient_id: str, outcome_data: TreatmentOutcome) -> Dict[str, Any]:
        """
        Process treatment outcome and update system learning
        
        Args:
            patient_id: Patient identifier
            outcome_data: Treatment outcome information
            
        Returns:
            Processing status and any system updates
        """
        self.logger.info(f"Processing treatment outcome for patient: {patient_id}")
        
        try:
            # Step 1: Record outcome
            self.feedback_loop.record_outcome(patient_id, outcome_data)
            
            # Step 2: Check for model updates
            model_updates = self.feedback_loop.check_for_model_updates()
            
            result = {
                'status': 'processed',
                'patient_id': patient_id,
                'outcome_recorded': True,
                'model_updates_triggered': bool(model_updates)
            }
            
            if model_updates:
                self.logger.info("Model updates triggered by new outcomes")
                
                # Step 3: Update Predictive Engine
                self.predictive_engine.update_models(model_updates)
                
                # Step 4: Update Clinical Context rules
                self.clinical_context.update_recommendation_rules(model_updates)
                
                result['updates_applied'] = list(model_updates.keys())
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing treatment outcome: {str(e)}")
            return {
                'status': 'error',
                'patient_id': patient_id,
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and metrics"""
        return {
            'system_name': 'Abena IHR Integrated System',
            'version': '1.0.0',
            'status': 'active',
            'modules': {
                'clinical_context': 'active',
                'predictive_engine': 'active',
                'feedback_loop': 'active',
                'conflict_resolver': 'active'
            },
            'learning_buffer_size': len(self.feedback_loop.learning_buffer),
            'recommendation_history_size': len(self.feedback_loop.recommendation_history),
            'timestamp': datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    # Create sample patient data
    patient_data = PatientData(
        patient_id="PAT_001",
        age=65,
        gender="M",
        medical_history=["hypertension", "diabetes"],
        current_medications=["aspirin", "simvastatin"],
        vital_signs={"blood_pressure_systolic": 145, "heart_rate": 72},
        lab_results={"creatinine": 1.2, "HbA1c": 7.5},
        allergies=["penicillin"],
        comorbidities=["coronary_artery_disease"]
    )
    
    # Initialize integrated system
    system = AbenaIntegratedSystem()
    
    # Generate treatment plan
    print("🏥 Generating Treatment Plan")
    print("=" * 50)
    
    recommendation = system.generate_treatment_plan(patient_data)
    
    print(f"Patient ID: {recommendation.patient_id}")
    print(f"Recommended Treatment: {recommendation.recommended_treatment.treatment_name}")
    print(f"Confidence Score: {recommendation.confidence_score:.2f}")
    print(f"Reasoning: {recommendation.reasoning}")
    print(f"Monitoring: {', '.join(recommendation.monitoring_requirements)}")
    print(f"Follow-up: {', '.join(recommendation.follow_up_schedule)}")
    
    # Simulate treatment outcome
    print(f"\n💊 Processing Treatment Outcome")
    print("=" * 50)
    
    outcome_data = TreatmentOutcome(
        patient_id="PAT_001",
        treatment_id=recommendation.recommended_treatment.treatment_id,
        outcome_success=True,
        recovery_time=21,
        side_effects_observed=["mild_nausea"],
        patient_satisfaction=8.5,
        readmission_required=False,
        outcome_date=datetime.now()
    )
    
    outcome_result = system.process_treatment_outcome("PAT_001", outcome_data)
    print(f"Outcome Status: {outcome_result['status']}")
    print(f"Model Updates: {outcome_result['model_updates_triggered']}")
    
    # System status
    print(f"\n🔧 System Status")
    print("=" * 50)
    status = system.get_system_status()
    print(json.dumps(status, indent=2, default=str))
    
    print("\n✅ Integrated system test completed successfully!") 