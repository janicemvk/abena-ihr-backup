from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
import asyncio

from src.clinical_outcomes.outcome_framework import (
    ClinicalOutcomeRecord, PainScoreAssessment, WOMACAssessment, ODIAssessment,
    MedicationUsageAssessment, HealthcareUtilizationAssessment, QualityOfLifeAssessment,
    WeeklySymptomTracking, TreatmentSatisfactionAssessment,
    MeasurementTiming, OutcomeType, DataQualityLevel, OutcomeDataStandards
)
from src.abena_sdk import AbenaSDK, AbenaSDKConfig

class OutcomeCollectionService:
    """Service for collecting and managing clinical outcome data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Abena SDK for centralized services
        self.abena = AbenaSDK(AbenaSDKConfig(
            auth_service_url='http://localhost:3001',
            data_service_url='http://localhost:8001',
            privacy_service_url='http://localhost:8002',
            blockchain_service_url='http://localhost:8003'
        ))
        
        # In-memory cache for collection schedules (in production, this would be in the data service)
        self.collection_schedules = {}
        
    async def create_patient_assessment_schedule(self, patient_id: str, baseline_date: datetime,
                                         study_duration_weeks: int = 52) -> Dict:
        """Create standardized assessment schedule for patient"""
        
        # 1. Auto-handled auth & permissions
        patient_data = await self.abena.get_patient_data(patient_id, 'assessment_scheduling')
        
        schedule = {
            'patient_id': patient_id,
            'baseline_date': baseline_date,
            'study_duration_weeks': study_duration_weeks,
            'assessments': []
        }
        
        # Define assessment schedule
        assessment_timepoints = [
            (MeasurementTiming.BASELINE, 0),
            (MeasurementTiming.WEEK_2, 14),
            (MeasurementTiming.WEEK_4, 28),
            (MeasurementTiming.WEEK_8, 56),
            (MeasurementTiming.WEEK_12, 84),
            (MeasurementTiming.WEEK_24, 168),
            (MeasurementTiming.WEEK_52, 365)
        ]
        
        for timing, days_offset in assessment_timepoints:
            if days_offset <= (study_duration_weeks * 7):
                assessment_date = baseline_date + timedelta(days=days_offset)
                
                # Define required assessments for each timepoint
                required_assessments = self._get_required_assessments(timing)
                
                schedule['assessments'].append({
                    'timing': timing,
                    'scheduled_date': assessment_date,
                    'window_start': assessment_date - timedelta(days=4),
                    'window_end': assessment_date + timedelta(days=4),
                    'required_assessments': required_assessments,
                    'status': 'scheduled',
                    'completed_assessments': [],
                    'data_quality': None
                })
        
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        await self.abena.save_outcome_data(patient_id, {
            'type': 'assessment_schedule',
            'schedule': schedule,
            'created_at': datetime.now().isoformat()
        }, 'assessment_scheduling')
        
        self.collection_schedules[patient_id] = schedule
        self.logger.info(f"Created assessment schedule for patient {patient_id}")
        
        return schedule
    
    def _get_required_assessments(self, timing: MeasurementTiming) -> List[str]:
        """Get required assessments for specific timepoint"""
        
        baseline_assessments = [
            'pain_assessment',
            'functional_assessment',  # WOMAC or ODI
            'medication_usage',
            'healthcare_utilization',
            'quality_of_life'
        ]
        
        follow_up_assessments = [
            'pain_assessment',
            'functional_assessment',
            'medication_usage',
            'treatment_satisfaction'
        ]
        
        comprehensive_assessments = baseline_assessments + [
            'treatment_satisfaction',
            'weekly_symptoms'
        ]
        
        if timing == MeasurementTiming.BASELINE:
            return baseline_assessments
        elif timing in [MeasurementTiming.WEEK_4, MeasurementTiming.WEEK_8]:
            return follow_up_assessments
        elif timing in [MeasurementTiming.WEEK_12, MeasurementTiming.WEEK_24, MeasurementTiming.WEEK_52]:
            return comprehensive_assessments
        else:
            return follow_up_assessments
    
    async def collect_outcome_data(self, patient_id: str, timing: MeasurementTiming,
                                 assessment_data: Dict[str, Any]) -> ClinicalOutcomeRecord:
        """Collect and validate outcome data"""
        
        # 1. Auto-handled auth & permissions
        patient_data = await self.abena.get_patient_data(patient_id, 'clinical_assessment')
        
        # Get patient schedule
        schedule = self.collection_schedules.get(patient_id)
        if not schedule:
            raise ValueError(f"No assessment schedule found for patient {patient_id}")
        
        # Find the assessment timepoint
        assessment_info = None
        for assessment in schedule['assessments']:
            if assessment['timing'] == timing:
                assessment_info = assessment
                break
        
        if not assessment_info:
            raise ValueError(f"Assessment timing {timing} not found in schedule")
        
        # Create outcome record
        record = ClinicalOutcomeRecord(
            record_id=f"{patient_id}_{timing.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            patient_id=patient_id,
            assessment_date=datetime.now(),
            measurement_timing=timing,
            baseline_date=schedule['baseline_date'],
            data_source=assessment_data.get('data_source', 'clinical_assessment'),
            assessor_id=assessment_data.get('assessor_id')
        )
        
        # Process each type of assessment data
        try:
            # Pain Assessment
            if 'pain_assessment' in assessment_data:
                record.pain_assessment = PainScoreAssessment(
                    patient_id=patient_id,
                    assessment_date=record.assessment_date,
                    measurement_timing=timing,
                    **assessment_data['pain_assessment']
                )
            
            # WOMAC Assessment
            if 'womac_assessment' in assessment_data:
                record.womac_assessment = WOMACAssessment(
                    patient_id=patient_id,
                    assessment_date=record.assessment_date,
                    measurement_timing=timing,
                    **assessment_data['womac_assessment']
                )
            
            # ODI Assessment
            if 'odi_assessment' in assessment_data:
                record.odi_assessment = ODIAssessment(
                    patient_id=patient_id,
                    assessment_date=record.assessment_date,
                    measurement_timing=timing,
                    **assessment_data['odi_assessment']
                )
            
            # Medication Usage
            if 'medication_usage' in assessment_data:
                record.medication_usage = MedicationUsageAssessment(
                    patient_id=patient_id,
                    assessment_date=record.assessment_date,
                    measurement_timing=timing,
                    **assessment_data['medication_usage']
                )
            
            # Healthcare Utilization
            if 'healthcare_utilization' in assessment_data:
                record.healthcare_utilization = HealthcareUtilizationAssessment(
                    patient_id=patient_id,
                    assessment_date=record.assessment_date,
                    measurement_timing=timing,
                    **assessment_data['healthcare_utilization']
                )
            
            # Quality of Life
            if 'quality_of_life' in assessment_data:
                record.quality_of_life = QualityOfLifeAssessment(
                    patient_id=patient_id,
                    assessment_date=record.assessment_date,
                    measurement_timing=timing,
                    **assessment_data['quality_of_life']
                )
            
            # Weekly Symptoms
            if 'weekly_symptoms' in assessment_data:
                record.weekly_symptoms = WeeklySymptomTracking(
                    patient_id=patient_id,
                    report_date=record.assessment_date,
                    **assessment_data['weekly_symptoms']
                )
            
            # Treatment Satisfaction
            if 'treatment_satisfaction' in assessment_data:
                record.treatment_satisfaction = TreatmentSatisfactionAssessment(
                    patient_id=patient_id,
                    assessment_date=record.assessment_date,
                    measurement_timing=timing,
                    **assessment_data['treatment_satisfaction']
                )
            
            # 2. Auto-handled privacy & encryption
            # 3. Auto-handled audit logging
            
            # 4. Focus on your business logic
            return self.process_data(record)
            
        except Exception as e:
            self.logger.error(f"Error processing outcome data: {str(e)}")
            raise
    
    def process_data(self, record: ClinicalOutcomeRecord) -> ClinicalOutcomeRecord:
        """Process and validate the outcome record"""
        # Validate record
        validation_errors = record.validate_record()
        if validation_errors:
            record.validation_errors = validation_errors
            record.data_quality = DataQualityLevel.INSUFFICIENT
        else:
            record.data_quality = DataQualityLevel.COMPLETE
        
        return record
    
    async def get_patient_outcomes(self, patient_id: str, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[ClinicalOutcomeRecord]:
        """Get patient outcome history"""
        
        # 1. Auto-handled auth & permissions
        patient_data = await self.abena.get_patient_data(patient_id, 'clinical_care')
        
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        
        # 4. Focus on your business logic
        outcome_history = await self.abena.get_outcome_history(patient_id, start_date, end_date)
        
        # Convert to ClinicalOutcomeRecord objects
        records = []
        for outcome_data in outcome_history:
            try:
                record = ClinicalOutcomeRecord(**outcome_data)
                records.append(record)
            except Exception as e:
                self.logger.warning(f"Failed to parse outcome record: {str(e)}")
        
        return records
    
    async def calculate_outcome_changes(self, patient_id: str) -> Dict[str, Any]:
        """Calculate outcome changes over time"""
        
        # 1. Auto-handled auth & permissions
        patient_data = await self.abena.get_patient_data(patient_id, 'clinical_analysis')
        
        # Get outcome history
        records = await self.get_patient_outcomes(patient_id)
        
        if not records:
            return {"error": "No outcome data available"}
        
        # Sort by assessment date
        records.sort(key=lambda x: x.assessment_date)
        
        baseline_record = None
        latest_record = records[-1]
        
        # Find baseline record
        for record in records:
            if record.measurement_timing == MeasurementTiming.BASELINE:
                baseline_record = record
                break
        
        if not baseline_record:
            return {"error": "No baseline assessment found"}
        
        changes = {
            'patient_id': patient_id,
            'baseline_date': baseline_record.assessment_date,
            'latest_date': latest_record.assessment_date,
            'time_span_days': (latest_record.assessment_date - baseline_record.assessment_date).days,
            'changes': {}
        }
        
        # Calculate pain score changes
        if baseline_record.pain_assessment and latest_record.pain_assessment:
            changes['changes']['pain'] = {
                'current_pain': {
                    'baseline': baseline_record.pain_assessment.current_pain,
                    'latest': latest_record.pain_assessment.current_pain,
                    'change': latest_record.pain_assessment.current_pain - baseline_record.pain_assessment.current_pain,
                    'percent_change': ((latest_record.pain_assessment.current_pain - baseline_record.pain_assessment.current_pain) / baseline_record.pain_assessment.current_pain) * 100 if baseline_record.pain_assessment.current_pain > 0 else 0
                },
                'average_pain_24h': {
                    'baseline': baseline_record.pain_assessment.average_pain_24h,
                    'latest': latest_record.pain_assessment.average_pain_24h,
                    'change': latest_record.pain_assessment.average_pain_24h - baseline_record.pain_assessment.average_pain_24h,
                    'percent_change': ((latest_record.pain_assessment.average_pain_24h - baseline_record.pain_assessment.average_pain_24h) / baseline_record.pain_assessment.average_pain_24h) * 100 if baseline_record.pain_assessment.average_pain_24h > 0 else 0
                }
            }
        
        # Calculate WOMAC changes
        if baseline_record.womac_assessment and latest_record.womac_assessment:
            changes['changes']['womac'] = {
                'total_score': {
                    'baseline': baseline_record.womac_assessment.total_score,
                    'latest': latest_record.womac_assessment.total_score,
                    'change': latest_record.womac_assessment.total_score - baseline_record.womac_assessment.total_score,
                    'percent_change': ((latest_record.womac_assessment.total_score - baseline_record.womac_assessment.total_score) / baseline_record.womac_assessment.total_score) * 100 if baseline_record.womac_assessment.total_score > 0 else 0
                },
                'normalized_score': {
                    'baseline': baseline_record.womac_assessment.normalized_score,
                    'latest': latest_record.womac_assessment.normalized_score,
                    'change': latest_record.womac_assessment.normalized_score - baseline_record.womac_assessment.normalized_score
                }
            }
        
        # Calculate ODI changes
        if baseline_record.odi_assessment and latest_record.odi_assessment:
            changes['changes']['odi'] = {
                'total_score': {
                    'baseline': baseline_record.odi_assessment.total_score,
                    'latest': latest_record.odi_assessment.total_score,
                    'change': latest_record.odi_assessment.total_score - baseline_record.odi_assessment.total_score,
                    'percent_change': ((latest_record.odi_assessment.total_score - baseline_record.odi_assessment.total_score) / baseline_record.odi_assessment.total_score) * 100 if baseline_record.odi_assessment.total_score > 0 else 0
                },
                'percentage_disability': {
                    'baseline': baseline_record.odi_assessment.percentage_disability,
                    'latest': latest_record.odi_assessment.percentage_disability,
                    'change': latest_record.odi_assessment.percentage_disability - baseline_record.odi_assessment.percentage_disability
                }
            }
        
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        
        return changes
    
    async def generate_outcome_summary(self, patient_id: str) -> Dict[str, Any]:
        """Generate comprehensive outcome summary"""
        
        # 1. Auto-handled auth & permissions
        patient_data = await self.abena.get_patient_data(patient_id, 'clinical_summary')
        
        # Get outcome changes
        changes = await self.calculate_outcome_changes(patient_id)
        
        # Get data quality metrics
        quality_metrics = await self.abena.get_data_quality_metrics(patient_id)
        
        # Calculate compliance
        compliance = self._calculate_compliance(patient_id)
        
        # Assess clinical response
        clinical_response = self._assess_clinical_response(changes)
        
        summary = {
            'patient_id': patient_id,
            'generated_at': datetime.now().isoformat(),
            'outcome_changes': changes,
            'data_quality': quality_metrics,
            'compliance': compliance,
            'clinical_response': clinical_response,
            'recommendations': self._generate_recommendations(changes, clinical_response)
        }
        
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        
        return summary
    
    def _calculate_compliance(self, patient_id: str) -> Dict[str, Any]:
        """Calculate patient compliance with assessment schedule"""
        schedule = self.collection_schedules.get(patient_id)
        if not schedule:
            return {"compliance_percentage": 0, "missed_assessments": 0}
        
        total_assessments = len(schedule['assessments'])
        completed_assessments = sum(1 for assessment in schedule['assessments'] 
                                  if assessment['status'] == 'completed')
        
        compliance_percentage = (completed_assessments / total_assessments) * 100 if total_assessments > 0 else 0
        
        return {
            'compliance_percentage': compliance_percentage,
            'total_assessments': total_assessments,
            'completed_assessments': completed_assessments,
            'missed_assessments': total_assessments - completed_assessments
        }
    
    def _assess_clinical_response(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Assess clinical response based on outcome changes"""
        if 'error' in changes:
            return {"response": "insufficient_data", "reason": changes['error']}
        
        response_indicators = []
        
        # Pain response
        if 'pain' in changes['changes']:
            pain_changes = changes['changes']['pain']
            if pain_changes['current_pain']['change'] <= -2:  # 2-point reduction
                response_indicators.append("significant_pain_reduction")
            elif pain_changes['current_pain']['change'] <= -1:
                response_indicators.append("moderate_pain_reduction")
        
        # Functional response
        if 'womac' in changes['changes']:
            womac_changes = changes['changes']['womac']
            if womac_changes['normalized_score']['change'] >= 10:  # 10% improvement
                response_indicators.append("significant_functional_improvement")
            elif womac_changes['normalized_score']['change'] >= 5:
                response_indicators.append("moderate_functional_improvement")
        
        # Determine overall response
        if len(response_indicators) >= 2:
            response = "excellent"
        elif len(response_indicators) == 1:
            response = "good"
        else:
            response = "minimal"
        
        return {
            'response': response,
            'indicators': response_indicators,
            'assessment_date': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, changes: Dict[str, Any], clinical_response: Dict[str, Any]) -> List[str]:
        """Generate clinical recommendations based on outcomes"""
        recommendations = []
        
        if clinical_response['response'] == 'excellent':
            recommendations.append("Continue current treatment plan")
            recommendations.append("Consider gradual dose reduction if appropriate")
        elif clinical_response['response'] == 'good':
            recommendations.append("Continue current treatment plan")
            recommendations.append("Monitor for further improvement")
        elif clinical_response['response'] == 'minimal':
            recommendations.append("Consider treatment modification")
            recommendations.append("Reassess patient goals and expectations")
            recommendations.append("Consider additional interventions")
        
        return recommendations
    
    async def get_recent_outcomes(self, days: int = 7) -> List[ClinicalOutcomeRecord]:
        """Get recent outcomes across all patients"""
        
        # 1. Auto-handled auth & permissions
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        
        # 4. Focus on your business logic
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # This would typically query the data service for recent outcomes
        # For now, return empty list as this would require additional data service endpoints
        return []

# ============================================================================
# API ENDPOINTS FOR OUTCOME COLLECTION
# ============================================================================

# Create API router
outcome_router = APIRouter()

# Global service instance
outcome_service = OutcomeCollectionService()

class AssessmentScheduleRequest(BaseModel):
    baseline_date: datetime
    study_duration_weeks: int = 52

@outcome_router.post("/patients/{patient_id}/assessment-schedule")
async def create_assessment_schedule(
    patient_id: str,
    request: AssessmentScheduleRequest
):
    """Create assessment schedule for patient"""
    try:
        schedule = await outcome_service.create_patient_assessment_schedule(
            patient_id, request.baseline_date, request.study_duration_weeks
        )
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.post("/patients/{patient_id}/outcomes/{timing}")
async def collect_outcomes(
    patient_id: str,
    timing: MeasurementTiming,
    assessment_data: Dict[str, Any]
):
    """Collect outcome data for patient at specific timepoint"""
    try:
        record = await outcome_service.collect_outcome_data(patient_id, timing, assessment_data)
        return {
            "status": "success",
            "record_id": record.record_id,
            "data_quality": record.data_quality.value,
            "validation_errors": record.validation_errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/patients/{patient_id}/outcomes")
async def get_patient_outcomes(
    patient_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get all outcome records for patient"""
    try:
        records = await outcome_service.get_patient_outcomes(patient_id, start_date, end_date)
        return [record.dict() for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/patients/{patient_id}/outcome-changes")
async def get_outcome_changes(patient_id: str):
    """Get outcome changes from baseline for patient"""
    try:
        changes = await outcome_service.calculate_outcome_changes(patient_id)
        return changes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/patients/{patient_id}/outcome-summary")
async def get_outcome_summary(patient_id: str):
    """Get comprehensive outcome summary for patient"""
    try:
        summary = await outcome_service.generate_outcome_summary(patient_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/patients/{patient_id}/assessment-schedule")
async def get_assessment_schedule(patient_id: str):
    """Get assessment schedule for patient"""
    try:
        schedule = outcome_service.collection_schedules.get(patient_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Assessment schedule not found")
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/data-quality-report")
async def generate_data_quality_report():
    """Generate overall data quality report"""
    try:
        # This would typically query the data service for quality metrics
        # For now, return a placeholder structure
        quality_summary = {
            'total_records': 0,
            'quality_distribution': {},
            'patients_with_data': 0,
            'average_assessments_per_patient': 0
        }
        
        return quality_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder for learning system integration
class OutcomeData(BaseModel):
    patient_id: str
    actual_outcome: float
    outcome_date: datetime
    # ... other fields as needed

def calculate_composite_outcome(outcome_record: ClinicalOutcomeRecord) -> float:
    """Calculate a composite outcome score from a ClinicalOutcomeRecord (stub)."""
    # Example: average of available scores (pain, function, satisfaction)
    scores = []
    if outcome_record.pain_assessment:
        scores.append(outcome_record.pain_assessment.average_pain_24h)
    if outcome_record.womac_assessment:
        scores.append(outcome_record.womac_assessment.normalized_score)
    if outcome_record.odi_assessment:
        scores.append(outcome_record.odi_assessment.percentage_disability)
    if outcome_record.treatment_satisfaction:
        scores.append(outcome_record.treatment_satisfaction.overall_satisfaction)
    if scores:
        return sum(scores) / len(scores)
    return 0.0

# Placeholder for continuous learning system
class ContinuousLearningSystem:
    """Placeholder for continuous learning system integration"""
    
    def add_outcome_data(self, learning_outcome: OutcomeData):
        """Add outcome data to the learning system"""
        # This would integrate with your actual learning system
        print(f"Learning system: Added outcome data for patient {learning_outcome.patient_id}")

# Global instance for learning system
continuous_learning = ContinuousLearningSystem()

def process_new_outcomes():
    """Process new outcomes for daily learning cycle"""
    # Get recent outcome data
    recent_outcomes = outcome_service.get_recent_outcomes(days=7)
    
    # Convert to learning format
    for outcome_record in recent_outcomes:
        learning_outcome = OutcomeData(
            patient_id=outcome_record.patient_id,
            actual_outcome=calculate_composite_outcome(outcome_record),
            outcome_date=outcome_record.assessment_date,
            # ... other fields
        )
        
        # Add to learning system
        continuous_learning.add_outcome_data(learning_outcome)
    
    return {
        "processed_records": len(recent_outcomes),
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }

@outcome_router.post("/learning/process-outcomes")
async def trigger_daily_learning():
    """Trigger daily learning cycle processing"""
    try:
        result = process_new_outcomes()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/learning/recent-outcomes")
async def get_recent_outcomes_for_learning(days: int = 7):
    """Get recent outcomes for learning system integration"""
    try:
        recent_outcomes = outcome_service.get_recent_outcomes(days)
        learning_data = []
        
        for outcome_record in recent_outcomes:
            learning_data.append({
                "patient_id": outcome_record.patient_id,
                "record_id": outcome_record.record_id,
                "assessment_date": outcome_record.assessment_date.isoformat(),
                "composite_outcome": calculate_composite_outcome(outcome_record),
                "data_quality": outcome_record.data_quality.value,
                "measurement_timing": outcome_record.measurement_timing.value
            })
        
        return {
            "total_records": len(learning_data),
            "days_processed": days,
            "learning_data": learning_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_clinical_workflow_data(patient_id: str) -> Dict[str, Any]:
    """Generate clinical workflow integration data for a patient"""
    try:
        # Get patient outcomes and changes
        records = outcome_service.get_patient_outcomes(patient_id)
        changes = outcome_service.calculate_outcome_changes(patient_id)
        schedule = outcome_service.collection_schedules.get(patient_id, {})
        
        # Get current outcomes (from latest record)
        current_outcomes = {}
        if records:
            latest_record = max(records, key=lambda x: x.assessment_date)
            
            if latest_record.pain_assessment:
                current_outcomes["pain_score"] = latest_record.pain_assessment.average_pain_24h
            
            if latest_record.womac_assessment:
                current_outcomes["functional_score"] = latest_record.womac_assessment.normalized_score
            elif latest_record.odi_assessment:
                current_outcomes["functional_score"] = latest_record.odi_assessment.percentage_disability
            
            if latest_record.treatment_satisfaction:
                current_outcomes["treatment_satisfaction"] = latest_record.treatment_satisfaction.overall_satisfaction
        
        # Get changes from baseline
        changes_from_baseline = {}
        if changes.get('changes'):
            outcome_changes = changes['changes']
            
            if 'pain_score' in outcome_changes:
                changes_from_baseline["pain_reduction"] = outcome_changes['pain_score']['change']
            
            if 'womac_score' in outcome_changes:
                changes_from_baseline["functional_improvement"] = outcome_changes['womac_score']['change']
            elif 'odi_score' in outcome_changes:
                changes_from_baseline["functional_improvement"] = outcome_changes['odi_score']['change']
            
            # Determine if changes are clinically significant
            significant_changes = [
                change_data.get('clinically_significant', False) 
                for change_data in outcome_changes.values()
            ]
            changes_from_baseline["clinically_significant"] = any(significant_changes)
        
        # Get upcoming assessments
        upcoming_assessments = []
        if schedule.get('assessments'):
            for assessment in schedule['assessments']:
                if assessment.get('status') == 'scheduled':
                    upcoming_assessments.append({
                        "timing": assessment['timing'].value,
                        "due_date": assessment['scheduled_date'].isoformat(),
                        "status": assessment['status']
                    })
        
        return {
            "patient_id": patient_id,
            "current_outcomes": current_outcomes,
            "changes_from_baseline": changes_from_baseline,
            "upcoming_assessments": upcoming_assessments
        }
        
    except Exception as e:
        return {
            "patient_id": patient_id,
            "error": str(e),
            "current_outcomes": {},
            "changes_from_baseline": {},
            "upcoming_assessments": []
        }

@outcome_router.get("/patients/{patient_id}/workflow-integration")
async def get_clinical_workflow_data(patient_id: str):
    """Get clinical workflow integration data for a patient"""
    try:
        workflow_data = generate_clinical_workflow_data(patient_id)
        return workflow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 