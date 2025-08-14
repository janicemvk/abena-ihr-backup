from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pydantic import BaseModel, validator, Field
import logging

class OutcomeType(Enum):
    """Types of clinical outcomes"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    PATIENT_REPORTED = "patient_reported"
    SAFETY = "safety"
    ECONOMIC = "economic"

class MeasurementTiming(Enum):
    """Standardized measurement timepoints"""
    BASELINE = "baseline"
    WEEK_2 = "week_2"
    WEEK_4 = "week_4"
    WEEK_8 = "week_8"
    WEEK_12 = "week_12"
    WEEK_24 = "week_24"
    WEEK_52 = "week_52"
    UNSCHEDULED = "unscheduled"

class DataQualityLevel(Enum):
    """Data quality levels for outcomes"""
    COMPLETE = "complete"
    ADEQUATE = "adequate"
    MINIMAL = "minimal"
    INSUFFICIENT = "insufficient"

# ============================================================================
# PRIMARY OUTCOMES - Pain and Functional Assessment
# ============================================================================

class PainScoreAssessment(BaseModel):
    """Numerical Rating Scale (NRS) for pain - Primary Outcome"""
    
    patient_id: str
    assessment_date: datetime
    measurement_timing: MeasurementTiming
    
    # Pain scores (0-10 scale)
    current_pain: float = Field(..., ge=0, le=10, description="Current pain level (0-10)")
    average_pain_24h: float = Field(..., ge=0, le=10, description="Average pain last 24 hours")
    worst_pain_24h: float = Field(..., ge=0, le=10, description="Worst pain last 24 hours")
    least_pain_24h: float = Field(..., ge=0, le=10, description="Least pain last 24 hours")
    
    # Pain characteristics
    pain_location: List[str] = Field(default_factory=list, description="Primary pain locations")
    pain_quality: List[str] = Field(default_factory=list, description="Pain descriptors")
    pain_interference: float = Field(..., ge=0, le=10, description="Pain interference with activities")
    
    # Activity-specific pain
    pain_at_rest: Optional[float] = Field(None, ge=0, le=10)
    pain_with_movement: Optional[float] = Field(None, ge=0, le=10)
    pain_with_exercise: Optional[float] = Field(None, ge=0, le=10)
    
    # Assessment metadata
    assessment_method: str = Field(default="self_report", description="How pain was assessed")
    assessor_type: str = Field(default="patient", description="Who performed assessment")
    data_quality: DataQualityLevel = DataQualityLevel.COMPLETE
    notes: Optional[str] = None

class WOMACAssessment(BaseModel):
    """Western Ontario and McMaster Universities Arthritis Index - Primary Outcome"""
    
    patient_id: str
    assessment_date: datetime
    measurement_timing: MeasurementTiming
    
    # WOMAC Pain Subscale (5 items, 0-4 scale each)
    pain_walking: int = Field(..., ge=0, le=4, description="Pain walking on flat surface")
    pain_stairs: int = Field(..., ge=0, le=4, description="Pain going up/down stairs")
    pain_night_bed: int = Field(..., ge=0, le=4, description="Pain at night in bed")
    pain_sitting: int = Field(..., ge=0, le=4, description="Pain sitting or lying")
    pain_standing: int = Field(..., ge=0, le=4, description="Pain standing upright")
    
    # WOMAC Stiffness Subscale (2 items, 0-4 scale each)
    stiffness_waking: int = Field(..., ge=0, le=4, description="Morning stiffness")
    stiffness_later_day: int = Field(..., ge=0, le=4, description="Stiffness later in day")
    
    # WOMAC Physical Function Subscale (17 items, 0-4 scale each)
    function_stairs_down: int = Field(..., ge=0, le=4, description="Descending stairs")
    function_stairs_up: int = Field(..., ge=0, le=4, description="Ascending stairs")
    function_rising_sitting: int = Field(..., ge=0, le=4, description="Rising from sitting")
    function_standing: int = Field(..., ge=0, le=4, description="Standing")
    function_bending: int = Field(..., ge=0, le=4, description="Bending to floor")
    function_walking_flat: int = Field(..., ge=0, le=4, description="Walking on flat")
    function_getting_in_out_car: int = Field(..., ge=0, le=4, description="Getting in/out car")
    function_shopping: int = Field(..., ge=0, le=4, description="Going shopping")
    function_socks: int = Field(..., ge=0, le=4, description="Putting on socks")
    function_rising_bed: int = Field(..., ge=0, le=4, description="Rising from bed")
    function_socks_off: int = Field(..., ge=0, le=4, description="Taking off socks")
    function_lying_bed: int = Field(..., ge=0, le=4, description="Lying in bed")
    function_bath_shower: int = Field(..., ge=0, le=4, description="Getting in/out bath")
    function_sitting: int = Field(..., ge=0, le=4, description="Sitting")
    function_toilet: int = Field(..., ge=0, le=4, description="Getting on/off toilet")
    function_heavy_domestic: int = Field(..., ge=0, le=4, description="Heavy domestic duties")
    function_light_domestic: int = Field(..., ge=0, le=4, description="Light domestic duties")
    
    # Computed scores
    @property
    def pain_score(self) -> float:
        """WOMAC Pain subscale score (0-20)"""
        return self.pain_walking + self.pain_stairs + self.pain_night_bed + self.pain_sitting + self.pain_standing
    
    @property
    def stiffness_score(self) -> float:
        """WOMAC Stiffness subscale score (0-8)"""
        return self.stiffness_waking + self.stiffness_later_day
    
    @property
    def function_score(self) -> float:
        """WOMAC Physical Function subscale score (0-68)"""
        return sum([
            self.function_stairs_down, self.function_stairs_up, self.function_rising_sitting,
            self.function_standing, self.function_bending, self.function_walking_flat,
            self.function_getting_in_out_car, self.function_shopping, self.function_socks,
            self.function_rising_bed, self.function_socks_off, self.function_lying_bed,
            self.function_bath_shower, self.function_sitting, self.function_toilet,
            self.function_heavy_domestic, self.function_light_domestic
        ])
    
    @property
    def total_score(self) -> float:
        """Total WOMAC score (0-96)"""
        return self.pain_score + self.stiffness_score + self.function_score
    
    @property
    def normalized_score(self) -> float:
        """Normalized WOMAC score (0-100)"""
        return (self.total_score / 96) * 100

class ODIAssessment(BaseModel):
    """Oswestry Disability Index - Primary Outcome for Back Pain"""
    
    patient_id: str
    assessment_date: datetime
    measurement_timing: MeasurementTiming
    
    # ODI Sections (0-5 scale each)
    pain_intensity: int = Field(..., ge=0, le=5, description="Pain intensity")
    personal_care: int = Field(..., ge=0, le=5, description="Personal care")
    lifting: int = Field(..., ge=0, le=5, description="Lifting")
    walking: int = Field(..., ge=0, le=5, description="Walking")
    sitting: int = Field(..., ge=0, le=5, description="Sitting")
    standing: int = Field(..., ge=0, le=5, description="Standing")
    sleeping: int = Field(..., ge=0, le=5, description="Sleeping")
    sex_life: int = Field(..., ge=0, le=5, description="Sex life")
    social_life: int = Field(..., ge=0, le=5, description="Social life")
    traveling: int = Field(..., ge=0, le=5, description="Traveling")
    
    @property
    def total_score(self) -> int:
        """Total ODI score (0-50)"""
        return sum([
            self.pain_intensity, self.personal_care, self.lifting, self.walking,
            self.sitting, self.standing, self.sleeping, self.sex_life,
            self.social_life, self.traveling
        ])
    
    @property
    def percentage_disability(self) -> float:
        """ODI percentage disability (0-100%)"""
        return (self.total_score / 50) * 100
    
    @property
    def disability_category(self) -> str:
        """ODI disability category"""
        percentage = self.percentage_disability
        if percentage <= 20:
            return "Minimal disability"
        elif percentage <= 40:
            return "Moderate disability"
        elif percentage <= 60:
            return "Severe disability"
        elif percentage <= 80:
            return "Crippled"
        else:
            return "Bed-bound or exaggerating"

# ============================================================================
# SECONDARY OUTCOMES - Medication Usage, Healthcare Utilization, QoL
# ============================================================================

class MedicationUsageAssessment(BaseModel):
    """Medication usage tracking - Secondary Outcome"""
    
    patient_id: str
    assessment_date: datetime
    measurement_timing: MeasurementTiming
    assessment_period_days: int = Field(default=30, description="Assessment period in days")
    
    # Current medications
    current_medications: List[Dict[str, Any]] = Field(default_factory=list, description="Current medication list")
    
    # Pain medication usage
    opioid_usage: Dict[str, Any] = Field(default_factory=dict, description="Opioid medication details")
    nsaid_usage: Dict[str, Any] = Field(default_factory=dict, description="NSAID medication details")
    adjuvant_usage: Dict[str, Any] = Field(default_factory=dict, description="Adjuvant medication details")
    
    # Usage metrics
    total_medication_count: int = Field(default=0, description="Total number of medications")
    pain_medication_count: int = Field(default=0, description="Number of pain medications")
    
    # Adherence metrics
    adherence_percentage: float = Field(default=100.0, ge=0, le=100, description="Medication adherence %")
    missed_doses_count: int = Field(default=0, ge=0, description="Missed doses in period")
    
    # Side effects
    side_effects: List[str] = Field(default_factory=list, description="Reported side effects")
    side_effect_severity: Dict[str, int] = Field(default_factory=dict, description="Side effect severity scores")
    
    # Effectiveness
    medication_effectiveness: float = Field(default=5.0, ge=0, le=10, description="Patient-rated effectiveness")
    satisfaction_with_medication: float = Field(default=5.0, ge=0, le=10, description="Patient satisfaction")

class HealthcareUtilizationAssessment(BaseModel):
    """Healthcare utilization tracking - Secondary Outcome"""
    
    patient_id: str
    assessment_date: datetime
    measurement_timing: MeasurementTiming
    assessment_period_days: int = Field(default=30, description="Assessment period in days")
    
    # Healthcare visits
    primary_care_visits: int = Field(default=0, ge=0, description="Primary care visits")
    specialist_visits: int = Field(default=0, ge=0, description="Specialist visits")
    pain_clinic_visits: int = Field(default=0, ge=0, description="Pain clinic visits")
    physical_therapy_visits: int = Field(default=0, ge=0, description="Physical therapy visits")
    
    # Emergency utilization
    emergency_room_visits: int = Field(default=0, ge=0, description="ER visits")
    urgent_care_visits: int = Field(default=0, ge=0, description="Urgent care visits")
    hospitalizations: int = Field(default=0, ge=0, description="Hospital admissions")
    hospital_days: int = Field(default=0, ge=0, description="Total hospital days")
    
    # Procedures and tests
    imaging_studies: int = Field(default=0, ge=0, description="Imaging studies")
    laboratory_tests: int = Field(default=0, ge=0, description="Lab tests")
    procedures: int = Field(default=0, ge=0, description="Medical procedures")
    
    # Costs (if available)
    estimated_total_cost: Optional[float] = Field(None, ge=0, description="Estimated total cost")
    out_of_pocket_cost: Optional[float] = Field(None, ge=0, description="Patient out-of-pocket cost")
    
    # Utilization reasons
    pain_related_visits: int = Field(default=0, ge=0, description="Pain-related visits")
    treatment_related_visits: int = Field(default=0, ge=0, description="Treatment-related visits")

class QualityOfLifeAssessment(BaseModel):
    """Quality of Life assessment - Secondary Outcome"""
    
    patient_id: str
    assessment_date: datetime
    measurement_timing: MeasurementTiming
    
    # SF-12 Health Survey (simplified)
    general_health: int = Field(..., ge=1, le=5, description="General health rating")
    physical_functioning: int = Field(..., ge=1, le=3, description="Physical functioning")
    role_physical: int = Field(..., ge=1, le=5, description="Role limitations due to physical health")
    bodily_pain: int = Field(..., ge=1, le=6, description="Bodily pain")
    vitality: int = Field(..., ge=1, le=6, description="Vitality/energy")
    social_functioning: int = Field(..., ge=1, le=5, description="Social functioning")
    role_emotional: int = Field(..., ge=1, le=5, description="Role limitations due to emotional problems")
    mental_health: int = Field(..., ge=1, le=6, description="Mental health")
    
    # Additional QoL measures
    sleep_quality: float = Field(..., ge=0, le=10, description="Sleep quality (0-10)")
    work_productivity: float = Field(default=5.0, ge=0, le=10, description="Work productivity (0-10)")
    relationship_satisfaction: float = Field(default=5.0, ge=0, le=10, description="Relationship satisfaction")
    life_satisfaction: float = Field(..., ge=0, le=10, description="Overall life satisfaction")
    
    # Physical activity
    days_per_week_exercise: int = Field(default=0, ge=0, le=7, description="Exercise days per week")
    minutes_per_day_exercise: int = Field(default=0, ge=0, description="Exercise minutes per day")
    
    @property
    def physical_component_score(self) -> float:
        """Simplified Physical Component Score"""
        # This is a simplified calculation - real SF-12 uses complex algorithms
        return (self.general_health + self.physical_functioning + self.role_physical + self.bodily_pain) / 4
    
    @property
    def mental_component_score(self) -> float:
        """Simplified Mental Component Score"""
        # This is a simplified calculation - real SF-12 uses complex algorithms
        return (self.vitality + self.social_functioning + self.role_emotional + self.mental_health) / 4

# ============================================================================
# PATIENT-REPORTED OUTCOMES - Weekly Symptom Tracking, Treatment Satisfaction
# ============================================================================

class WeeklySymptomTracking(BaseModel):
    """Weekly patient-reported symptom tracking"""
    
    patient_id: str
    report_date: datetime
    week_number: int = Field(..., ge=1, description="Week number since baseline")
    
    # Symptom tracking
    average_pain_week: float = Field(..., ge=0, le=10, description="Average pain this week")
    worst_pain_week: float = Field(..., ge=0, le=10, description="Worst pain this week")
    pain_free_days: int = Field(..., ge=0, le=7, description="Days with minimal/no pain")
    
    # Functional status
    activity_limitation_days: int = Field(..., ge=0, le=7, description="Days with activity limitations")
    missed_work_days: int = Field(default=0, ge=0, le=7, description="Missed work days")
    
    # Symptom burden
    fatigue_level: float = Field(default=5.0, ge=0, le=10, description="Fatigue level")
    mood_rating: float = Field(default=5.0, ge=0, le=10, description="Mood rating")
    anxiety_level: float = Field(default=5.0, ge=0, le=10, description="Anxiety level")
    
    # Treatment response
    treatment_helpfulness: float = Field(default=5.0, ge=0, le=10, description="Treatment helpfulness")
    side_effects_this_week: List[str] = Field(default_factory=list, description="Side effects experienced")
    
    # Global impression
    global_improvement: int = Field(..., ge=1, le=7, description="Patient Global Impression of Change")

class TreatmentSatisfactionAssessment(BaseModel):
    """Treatment satisfaction assessment - Patient-Reported Outcome"""
    
    patient_id: str
    assessment_date: datetime
    measurement_timing: MeasurementTiming
    
    # Overall satisfaction
    overall_satisfaction: float = Field(..., ge=0, le=10, description="Overall treatment satisfaction")
    would_recommend: bool = Field(..., description="Would recommend treatment to others")
    would_continue: bool = Field(..., description="Would continue current treatment")
    
    # Specific satisfaction domains
    pain_relief_satisfaction: float = Field(..., ge=0, le=10, description="Satisfaction with pain relief")
    function_improvement_satisfaction: float = Field(..., ge=0, le=10, description="Satisfaction with function improvement")
    side_effect_tolerance: float = Field(..., ge=0, le=10, description="Tolerance of side effects")
    
    # Treatment burden
    treatment_burden: float = Field(default=5.0, ge=0, le=10, description="Treatment burden (0=no burden)")
    convenience: float = Field(default=5.0, ge=0, le=10, description="Treatment convenience")
    
    # Communication and care
    provider_communication: float = Field(default=8.0, ge=0, le=10, description="Provider communication quality")
    care_coordination: float = Field(default=8.0, ge=0, le=10, description="Care coordination quality")
    
    # Expectations
    expectations_met: float = Field(..., ge=0, le=10, description="How well expectations were met")
    
    # Open feedback
    most_helpful_aspect: Optional[str] = Field(None, description="Most helpful aspect of treatment")
    least_helpful_aspect: Optional[str] = Field(None, description="Least helpful aspect of treatment")
    suggestions_for_improvement: Optional[str] = Field(None, description="Suggestions for improvement")

# ============================================================================
# DATA COLLECTION STANDARDS AND VALIDATION
# ============================================================================

class OutcomeDataStandards:
    """Data collection standards and validation rules"""
    
    # Measurement timing windows (days from baseline)
    TIMING_WINDOWS = {
        MeasurementTiming.BASELINE: (0, 0),
        MeasurementTiming.WEEK_2: (10, 18),  # 14 ± 4 days
        MeasurementTiming.WEEK_4: (24, 32),  # 28 ± 4 days
        MeasurementTiming.WEEK_8: (52, 60),  # 56 ± 4 days
        MeasurementTiming.WEEK_12: (80, 88), # 84 ± 4 days
        MeasurementTiming.WEEK_24: (164, 172), # 168 ± 4 days
        MeasurementTiming.WEEK_52: (358, 372)  # 365 ± 7 days
    }
    
    # Minimum data requirements
    MINIMUM_DATA_REQUIREMENTS = {
        OutcomeType.PRIMARY: {
            'pain_score': ['current_pain', 'average_pain_24h'],
            'functional_assessment': ['total_score'],
            'required_timepoints': [MeasurementTiming.BASELINE, MeasurementTiming.WEEK_12]
        },
        OutcomeType.SECONDARY: {
            'medication_usage': ['current_medications', 'adherence_percentage'],
            'healthcare_utilization': ['total_visits'],
            'quality_of_life': ['life_satisfaction'],
            'required_timepoints': [MeasurementTiming.BASELINE, MeasurementTiming.WEEK_24]
        },
        OutcomeType.PATIENT_REPORTED: {
            'weekly_tracking': ['average_pain_week', 'treatment_helpfulness'],
            'treatment_satisfaction': ['overall_satisfaction'],
            'required_timepoints': [MeasurementTiming.WEEK_12]
        }
    }
    
    @classmethod
    def validate_timing(cls, assessment_date: datetime, baseline_date: datetime, 
                       measurement_timing: MeasurementTiming) -> bool:
        """Validate if assessment falls within acceptable timing window"""
        days_from_baseline = (assessment_date - baseline_date).days
        min_days, max_days = cls.TIMING_WINDOWS.get(measurement_timing, (0, 999))
        return min_days <= days_from_baseline <= max_days
    
    @classmethod
    def assess_data_quality(cls, outcome_data: Dict[str, Any], outcome_type: OutcomeType) -> DataQualityLevel:
        """Assess data quality level based on completeness"""
        requirements = cls.MINIMUM_DATA_REQUIREMENTS.get(outcome_type, {})
        
        total_required = sum(len(fields) for fields in requirements.values() if isinstance(fields, list))
        completed_fields = 0
        
        for field_group in requirements.values():
            if isinstance(field_group, list):
                for field in field_group:
                    if field in outcome_data and outcome_data[field] is not None:
                        completed_fields += 1
        
        if total_required == 0:
            return DataQualityLevel.COMPLETE
        
        completeness_ratio = completed_fields / total_required
        
        if completeness_ratio >= 0.9:
            return DataQualityLevel.COMPLETE
        elif completeness_ratio >= 0.7:
            return DataQualityLevel.ADEQUATE
        elif completeness_ratio >= 0.5:
            return DataQualityLevel.MINIMAL
        else:
            return DataQualityLevel.INSUFFICIENT

# ============================================================================
# OUTCOME DATA SCHEMA AND STORAGE
# ============================================================================

class ClinicalOutcomeRecord(BaseModel):
    """Comprehensive clinical outcome record"""
    
    # Record metadata
    record_id: str = Field(..., description="Unique record identifier")
    patient_id: str = Field(..., description="Patient identifier")
    study_id: Optional[str] = Field(None, description="Study/trial identifier")
    site_id: Optional[str] = Field(None, description="Clinical site identifier")
    
    # Assessment details
    assessment_date: datetime = Field(..., description="Date of assessment")
    measurement_timing: MeasurementTiming = Field(..., description="Measurement timepoint")
    baseline_date: datetime = Field(..., description="Patient baseline date")
    
    # Outcome data
    pain_assessment: Optional[PainScoreAssessment] = None
    womac_assessment: Optional[WOMACAssessment] = None
    odi_assessment: Optional[ODIAssessment] = None
    medication_usage: Optional[MedicationUsageAssessment] = None
    healthcare_utilization: Optional[HealthcareUtilizationAssessment] = None
    quality_of_life: Optional[QualityOfLifeAssessment] = None
    weekly_symptoms: Optional[WeeklySymptomTracking] = None
    treatment_satisfaction: Optional[TreatmentSatisfactionAssessment] = None
    
    # Data quality and validation
    data_quality: DataQualityLevel = Field(..., description="Overall data quality level")
    validation_errors: List[str] = Field(default_factory=list, description="Data validation errors")
    data_source: str = Field(default="clinical_assessment", description="Source of data")
    assessor_id: Optional[str] = Field(None, description="ID of person conducting assessment")
    
    # Administrative
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1, description="Record version")
    
    def validate_record(self) -> List[str]:
        """Validate the complete outcome record"""
        errors = []
        
        # Check timing validity
        if not OutcomeDataStandards.validate_timing(
            self.assessment_date, self.baseline_date, self.measurement_timing
        ):
            errors.append(f"Assessment date outside acceptable window for {self.measurement_timing.value}")
        
        # Check minimum data requirements
        has_primary_outcome = bool(self.pain_assessment or self.womac_assessment or self.odi_assessment)
        if not has_primary_outcome and self.measurement_timing in [MeasurementTiming.BASELINE, MeasurementTiming.WEEK_12]:
            errors.append("Missing required primary outcome data")
        
        # Update validation errors
        self.validation_errors = errors
        
        # Update data quality
        if not errors:
            if self.pain_assessment and (self.womac_assessment or self.odi_assessment):
                self.data_quality = DataQualityLevel.COMPLETE
            elif self.pain_assessment or self.womac_assessment or self.odi_assessment:
                self.data_quality = DataQualityLevel.ADEQUATE
            else:
                self.data_quality = DataQualityLevel.MINIMAL
        else:
            self.data_quality = DataQualityLevel.INSUFFICIENT
        
        return errors 