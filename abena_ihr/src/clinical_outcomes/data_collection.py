"""
Clinical Data Collection Module

This module handles the collection, validation, and management of clinical outcome data
in the Abena IHR system. It provides classes and functions for data entry, validation,
and storage of clinical measurements and observations.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
import json
import uuid
from enum import Enum
import pandas as pd
from pathlib import Path
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import asyncio

from src.clinical_outcomes.outcome_framework import (
    ClinicalOutcomeRecord, PainScoreAssessment, WOMACAssessment, ODIAssessment,
    MedicationUsageAssessment, HealthcareUtilizationAssessment, QualityOfLifeAssessment,
    WeeklySymptomTracking, TreatmentSatisfactionAssessment,
    MeasurementTiming, OutcomeType, DataQualityLevel, OutcomeDataStandards
)


class DataSource(Enum):
    """Enumeration of different data sources."""
    CLINICAL_ASSESSMENT = "clinical_assessment"
    PATIENT_REPORTED = "patient_reported"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    DEVICE_MEASUREMENT = "device_measurement"
    ADMINISTRATIVE = "administrative"


class DataQuality(Enum):
    """Enumeration of data quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"


@dataclass
class ClinicalMeasurement:
    """Data class representing a single clinical measurement."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    outcome_name: str = ""
    value: Any = None
    unit: Optional[str] = None
    measurement_date: datetime = field(default_factory=datetime.now)
    data_source: DataSource = DataSource.CLINICAL_ASSESSMENT
    data_quality: DataQuality = DataQuality.UNKNOWN
    notes: Optional[str] = None
    collected_by: Optional[str] = None
    validated_by: Optional[str] = None
    validation_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataCollectionForm:
    """Data class representing a data collection form."""
    form_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    form_name: str = ""
    version: str = "1.0"
    description: str = ""
    fields: List[Dict[str, Any]] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class DataCollector:
    """
    Main class for managing clinical data collection.
    
    This class provides methods for:
    - Adding and managing clinical measurements
    - Validating data quality
    - Exporting data to various formats
    - Generating data collection reports
    """
    
    def __init__(self):
        self.measurements: List[ClinicalMeasurement] = []
        self.forms: Dict[str, DataCollectionForm] = {}
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
    
    def add_measurement(self, measurement: ClinicalMeasurement) -> bool:
        """
        Add a new clinical measurement to the collection.
        
        Args:
            measurement: ClinicalMeasurement object to add
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            # Validate measurement
            if not self._validate_measurement(measurement):
                return False
            
            self.measurements.append(measurement)
            return True
        except Exception as e:
            print(f"Error adding measurement: {e}")
            return False
    
    def _validate_measurement(self, measurement: ClinicalMeasurement) -> bool:
        """
        Validate a clinical measurement.
        
        Args:
            measurement: ClinicalMeasurement to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not measurement.patient_id:
            print("Error: Patient ID is required")
            return False
        
        if not measurement.outcome_name:
            print("Error: Outcome name is required")
            return False
        
        if measurement.value is None:
            print("Error: Measurement value is required")
            return False
        
        return True
    
    def get_measurements(self, 
                        patient_id: Optional[str] = None,
                        outcome_name: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[ClinicalMeasurement]:
        """
        Retrieve measurements with optional filtering.
        
        Args:
            patient_id: Optional filter by patient ID
            outcome_name: Optional filter by outcome name
            start_date: Optional filter by start date
            end_date: Optional filter by end date
            
        Returns:
            List of ClinicalMeasurement objects
        """
        filtered_measurements = self.measurements
        
        if patient_id:
            filtered_measurements = [m for m in filtered_measurements 
                                   if m.patient_id == patient_id]
        
        if outcome_name:
            filtered_measurements = [m for m in filtered_measurements 
                                   if m.outcome_name == outcome_name]
        
        if start_date:
            filtered_measurements = [m for m in filtered_measurements 
                                   if m.measurement_date >= start_date]
        
        if end_date:
            filtered_measurements = [m for m in filtered_measurements 
                                   if m.measurement_date <= end_date]
        
        return filtered_measurements
    
    def add_form(self, form: DataCollectionForm) -> bool:
        """
        Add a new data collection form.
        
        Args:
            form: DataCollectionForm object to add
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            self.forms[form.form_id] = form
            return True
        except Exception as e:
            print(f"Error adding form: {e}")
            return False
    
    def get_form(self, form_id: str) -> Optional[DataCollectionForm]:
        """
        Retrieve a data collection form by ID.
        
        Args:
            form_id: ID of the form to retrieve
            
        Returns:
            DataCollectionForm or None if not found
        """
        return self.forms.get(form_id)
    
    def collect_data_from_form(self, form_id: str, form_data: Dict[str, Any]) -> List[ClinicalMeasurement]:
        """
        Collect measurements from form data.
        
        Args:
            form_id: ID of the form to use
            form_data: Dictionary containing form field values
            
        Returns:
            List of ClinicalMeasurement objects created from form data
        """
        form = self.get_form(form_id)
        if not form:
            print(f"Form '{form_id}' not found")
            return []
        
        measurements = []
        
        for field in form.fields:
            field_name = field.get("name")
            if field_name in form_data:
                measurement = ClinicalMeasurement(
                    outcome_name=field_name,
                    value=form_data[field_name],
                    unit=field.get("unit"),
                    data_source=DataSource(field.get("data_source", "clinical_assessment")),
                    notes=form_data.get(f"{field_name}_notes")
                )
                measurements.append(measurement)
        
        return measurements
    
    def export_to_csv(self, filepath: str, 
                     patient_id: Optional[str] = None,
                     outcome_name: Optional[str] = None) -> bool:
        """
        Export measurements to CSV format.
        
        Args:
            filepath: Path to save the CSV file
            patient_id: Optional filter by patient ID
            outcome_name: Optional filter by outcome name
            
        Returns:
            bool: True if successfully exported, False otherwise
        """
        try:
            measurements = self.get_measurements(patient_id, outcome_name)
            
            data = []
            for measurement in measurements:
                data.append({
                    "id": measurement.id,
                    "patient_id": measurement.patient_id,
                    "outcome_name": measurement.outcome_name,
                    "value": measurement.value,
                    "unit": measurement.unit,
                    "measurement_date": measurement.measurement_date.isoformat(),
                    "data_source": measurement.data_source.value,
                    "data_quality": measurement.data_quality.value,
                    "notes": measurement.notes,
                    "collected_by": measurement.collected_by,
                    "validated_by": measurement.validated_by,
                    "validation_date": measurement.validation_date.isoformat() if measurement.validation_date else None,
                    "created_at": measurement.created_at.isoformat(),
                    "updated_at": measurement.updated_at.isoformat()
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, filepath: str,
                      patient_id: Optional[str] = None,
                      outcome_name: Optional[str] = None) -> bool:
        """
        Export measurements to JSON format.
        
        Args:
            filepath: Path to save the JSON file
            patient_id: Optional filter by patient ID
            outcome_name: Optional filter by outcome name
            
        Returns:
            bool: True if successfully exported, False otherwise
        """
        try:
            measurements = self.get_measurements(patient_id, outcome_name)
            
            data = {
                "exported_at": datetime.now().isoformat(),
                "measurements": []
            }
            
            for measurement in measurements:
                data["measurements"].append({
                    "id": measurement.id,
                    "patient_id": measurement.patient_id,
                    "outcome_name": measurement.outcome_name,
                    "value": measurement.value,
                    "unit": measurement.unit,
                    "measurement_date": measurement.measurement_date.isoformat(),
                    "data_source": measurement.data_source.value,
                    "data_quality": measurement.data_quality.value,
                    "notes": measurement.notes,
                    "collected_by": measurement.collected_by,
                    "validated_by": measurement.validated_by,
                    "validation_date": measurement.validation_date.isoformat() if measurement.validation_date else None,
                    "created_at": measurement.created_at.isoformat(),
                    "updated_at": measurement.updated_at.isoformat()
                })
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def generate_data_quality_report(self) -> Dict[str, Any]:
        """
        Generate a data quality report.
        
        Returns:
            Dictionary containing data quality statistics
        """
        if not self.measurements:
            return {"error": "No measurements available"}
        
        total_measurements = len(self.measurements)
        quality_counts = {}
        
        for quality in DataQuality:
            quality_counts[quality.value] = len([m for m in self.measurements 
                                               if m.data_quality == quality])
        
        source_counts = {}
        for source in DataSource:
            source_counts[source.value] = len([m for m in self.measurements 
                                             if m.data_source == source])
        
        outcome_counts = {}
        for measurement in self.measurements:
            outcome_counts[measurement.outcome_name] = outcome_counts.get(measurement.outcome_name, 0) + 1
        
        return {
            "total_measurements": total_measurements,
            "quality_distribution": quality_counts,
            "source_distribution": source_counts,
            "outcome_distribution": outcome_counts,
            "report_generated_at": datetime.now().isoformat()
        }
    
    def validate_data_quality(self, measurement_id: str, 
                            quality: DataQuality,
                            validated_by: str) -> bool:
        """
        Update data quality assessment for a measurement.
        
        Args:
            measurement_id: ID of the measurement to validate
            quality: New data quality assessment
            validated_by: Name of person performing validation
            
        Returns:
            bool: True if successfully validated, False otherwise
        """
        for measurement in self.measurements:
            if measurement.id == measurement_id:
                measurement.data_quality = quality
                measurement.validated_by = validated_by
                measurement.validation_date = datetime.now()
                measurement.updated_at = datetime.now()
                return True
        
        return False


# Utility functions for data collection
def create_pain_assessment_form() -> DataCollectionForm:
    """
    Create a sample pain assessment form.
    
    Returns:
        DataCollectionForm for pain assessment
    """
    form = DataCollectionForm(
        form_name="Pain Assessment Form",
        version="1.0",
        description="Standard pain assessment form for clinical trials",
        fields=[
            {
                "name": "pain_intensity",
                "label": "Pain Intensity (0-10)",
                "type": "numeric",
                "unit": "points",
                "min_value": 0,
                "max_value": 10,
                "data_source": "patient_reported"
            },
            {
                "name": "pain_location",
                "label": "Pain Location",
                "type": "text",
                "data_source": "patient_reported"
            },
            {
                "name": "pain_character",
                "label": "Pain Character",
                "type": "select",
                "options": ["aching", "burning", "sharp", "throbbing", "other"],
                "data_source": "patient_reported"
            },
            {
                "name": "functional_impact",
                "label": "Functional Impact",
                "type": "select",
                "options": ["none", "mild", "moderate", "severe"],
                "data_source": "patient_reported"
            }
        ],
        required_fields=["pain_intensity", "pain_location"]
    )
    
    return form


def create_sample_measurements() -> List[ClinicalMeasurement]:
    """
    Create sample clinical measurements for testing.
    
    Returns:
        List of ClinicalMeasurement objects
    """
    measurements = []
    
    # Sample pain measurements
    for i in range(1, 6):
        measurement = ClinicalMeasurement(
            patient_id=f"PATIENT_{i:03d}",
            outcome_name="pain_intensity",
            value=5 + i,
            unit="points",
            data_source=DataSource.PATIENT_REPORTED,
            data_quality=DataQuality.GOOD,
            collected_by="Dr. Smith",
            notes=f"Baseline pain assessment for patient {i}"
        )
        measurements.append(measurement)
    
    # Sample functional measurements
    for i in range(1, 4):
        measurement = ClinicalMeasurement(
            patient_id=f"PATIENT_{i:03d}",
            outcome_name="functional_ability",
            value="moderate",
            data_source=DataSource.CLINICAL_ASSESSMENT,
            data_quality=DataQuality.EXCELLENT,
            collected_by="Dr. Johnson",
            notes=f"Functional assessment for patient {i}"
        )
        measurements.append(measurement)
    
    return measurements


class OutcomeCollectionService:
    """Service for collecting and managing clinical outcome data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.outcome_records = {}  # In production, this would be a database
        self.collection_schedules = {}  # Patient assessment schedules
        
    def create_patient_assessment_schedule(self, patient_id: str, baseline_date: datetime,
                                         study_duration_weeks: int = 52) -> Dict:
        """Create standardized assessment schedule for patient"""
        
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
            
            # Validate the complete record
            validation_errors = record.validate_record()
            
            if validation_errors:
                self.logger.warning(f"Validation errors for {record.record_id}: {validation_errors}")
            
            # Store the record
            self.outcome_records[record.record_id] = record
            
            # Update assessment schedule
            assessment_info['status'] = 'completed'
            assessment_info['completed_date'] = datetime.now()
            assessment_info['data_quality'] = record.data_quality
            assessment_info['record_id'] = record.record_id
            
            self.logger.info(f"Collected outcome data for {patient_id} at {timing.value}")
            
            return record
            
        except Exception as e:
            self.logger.error(f"Error collecting outcome data: {str(e)}")
            raise
    
    def get_patient_outcomes(self, patient_id: str, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[ClinicalOutcomeRecord]:
        """Get all outcome records for a patient"""
        
        patient_records = [
            record for record in self.outcome_records.values()
            if record.patient_id == patient_id
        ]
        
        # Filter by date range if provided
        if start_date:
            patient_records = [r for r in patient_records if r.assessment_date >= start_date]
        if end_date:
            patient_records = [r for r in patient_records if r.assessment_date <= end_date]
        
        # Sort by assessment date
        patient_records.sort(key=lambda x: x.assessment_date)
        
        return patient_records
    
    def calculate_outcome_changes(self, patient_id: str) -> Dict[str, Any]:
        """Calculate outcome changes from baseline"""
        
        records = self.get_patient_outcomes(patient_id)
        baseline_record = None
        latest_record = None
        
        # Find baseline and latest records
        for record in records:
            if record.measurement_timing == MeasurementTiming.BASELINE:
                baseline_record = record
            if not latest_record or record.assessment_date > latest_record.assessment_date:
                latest_record = record
        
        if not baseline_record or not latest_record or baseline_record == latest_record:
            return {'status': 'insufficient_data'}
        
        changes = {
            'patient_id': patient_id,
            'baseline_date': baseline_record.assessment_date,
            'latest_date': latest_record.assessment_date,
            'follow_up_duration_days': (latest_record.assessment_date - baseline_record.assessment_date).days,
            'changes': {}
        }
        
        # Calculate pain score changes
        if baseline_record.pain_assessment and latest_record.pain_assessment:
            baseline_pain = baseline_record.pain_assessment.average_pain_24h
            latest_pain = latest_record.pain_assessment.average_pain_24h
            pain_change = baseline_pain - latest_pain  # Positive = improvement
            
            changes['changes']['pain_score'] = {
                'baseline': baseline_pain,
                'latest': latest_pain,
                'change': pain_change,
                'percent_change': (pain_change / baseline_pain * 100) if baseline_pain > 0 else 0,
                'clinically_significant': abs(pain_change) >= 2.0  # 2-point change threshold
            }
        
        # Calculate WOMAC changes
        if baseline_record.womac_assessment and latest_record.womac_assessment:
            baseline_womac = baseline_record.womac_assessment.normalized_score
            latest_womac = latest_record.womac_assessment.normalized_score
            womac_change = baseline_womac - latest_womac  # Positive = improvement
            
            changes['changes']['womac_score'] = {
                'baseline': baseline_womac,
                'latest': latest_womac,
                'change': womac_change,
                'percent_change': (womac_change / baseline_womac * 100) if baseline_womac > 0 else 0,
                'clinically_significant': abs(womac_change) >= 12.0  # 12% change threshold
            }
        
        # Calculate ODI changes
        if baseline_record.odi_assessment and latest_record.odi_assessment:
            baseline_odi = baseline_record.odi_assessment.percentage_disability
            latest_odi = latest_record.odi_assessment.percentage_disability
            odi_change = baseline_odi - latest_odi  # Positive = improvement
            
            changes['changes']['odi_score'] = {
                'baseline': baseline_odi,
                'latest': latest_odi,
                'change': odi_change,
                'percent_change': (odi_change / baseline_odi * 100) if baseline_odi > 0 else 0,
                'clinically_significant': abs(odi_change) >= 10.0  # 10% change threshold
            }
        
        # Calculate quality of life changes
        if baseline_record.quality_of_life and latest_record.quality_of_life:
            baseline_qol = baseline_record.quality_of_life.life_satisfaction
            latest_qol = latest_record.quality_of_life.life_satisfaction
            qol_change = latest_qol - baseline_qol  # Positive = improvement
            
            changes['changes']['quality_of_life'] = {
                'baseline': baseline_qol,
                'latest': latest_qol,
                'change': qol_change,
                'percent_change': (qol_change / baseline_qol * 100) if baseline_qol > 0 else 0,
                'clinically_significant': abs(qol_change) >= 1.0  # 1-point change threshold
            }
        
        return changes
    
    def generate_outcome_summary(self, patient_id: str) -> Dict[str, Any]:
        """Generate comprehensive outcome summary for patient"""
        
        records = self.get_patient_outcomes(patient_id)
        schedule = self.collection_schedules.get(patient_id, {})
        changes = self.calculate_outcome_changes(patient_id)
        
        summary = {
            'patient_id': patient_id,
            'baseline_date': schedule.get('baseline_date'),
            'total_assessments': len(records),
            'assessment_compliance': self._calculate_compliance(patient_id),
            'data_quality_summary': self._summarize_data_quality(records),
            'outcome_changes': changes.get('changes', {}),
            'clinical_response': self._assess_clinical_response(changes),
            'generated_at': datetime.now()
        }
        
        return summary
    
    def _calculate_compliance(self, patient_id: str) -> Dict[str, Any]:
        """Calculate assessment compliance"""
        
        schedule = self.collection_schedules.get(patient_id, {})
        if not schedule:
            return {'compliance_rate': 0, 'status': 'no_schedule'}
        
        total_scheduled = len(schedule.get('assessments', []))
        completed = len([a for a in schedule.get('assessments', []) if a.get('status') == 'completed'])
        overdue = len([
            a for a in schedule.get('assessments', [])
            if a.get('status') == 'scheduled' and datetime.now() > a.get('window_end', datetime.now())
        ])
        
        compliance_rate = (completed / total_scheduled * 100) if total_scheduled > 0 else 0
        
        return {
            'compliance_rate': compliance_rate,
            'total_scheduled': total_scheduled,
            'completed': completed,
            'overdue': overdue,
            'status': 'excellent' if compliance_rate >= 90 else 'good' if compliance_rate >= 75 else 'poor'
        }
    
    def _summarize_data_quality(self, records: List[ClinicalOutcomeRecord]) -> Dict[str, Any]:
        """Summarize data quality across records"""
        
        if not records:
            return {'average_quality': 'insufficient', 'quality_distribution': {}}
        
        quality_counts = {}
        for record in records:
            quality = record.data_quality.value
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        # Calculate weighted quality score
        quality_weights = {
            DataQualityLevel.COMPLETE: 4,
            DataQualityLevel.ADEQUATE: 3,
            DataQualityLevel.MINIMAL: 2,
            DataQualityLevel.INSUFFICIENT: 1
        }
        
        total_weight = sum(quality_weights[record.data_quality] for record in records)
        average_weight = total_weight / len(records)
        
        if average_weight >= 3.5:
            average_quality = 'excellent'
        elif average_weight >= 2.5:
            average_quality = 'good'
        elif average_weight >= 1.5:
            average_quality = 'fair'
        else:
            average_quality = 'poor'
        
        return {
            'average_quality': average_quality,
            'quality_distribution': quality_counts,
            'total_records': len(records)
        }
    
    def _assess_clinical_response(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall clinical response based on outcome changes"""
        
        if changes.get('status') == 'insufficient_data':
            return {'response_category': 'insufficient_data'}
        
        outcome_changes = changes.get('changes', {})
        significant_improvements = 0
        total_outcomes = 0
        
        # Check each outcome for clinically significant improvement
        for outcome_name, outcome_data in outcome_changes.items():
            if 'clinically_significant' in outcome_data and 'change' in outcome_data:
                total_outcomes += 1
                
                # Check if improvement is clinically significant
                if outcome_data['clinically_significant'] and outcome_data['change'] > 0:
                    significant_improvements += 1
        
        if total_outcomes == 0:
            response_category = 'insufficient_data'
        elif significant_improvements == total_outcomes:
            response_category = 'excellent_response'
        elif significant_improvements >= total_outcomes * 0.5:
            response_category = 'good_response'
        elif significant_improvements > 0:
            response_category = 'partial_response'
        else:
            response_category = 'no_response'
        
        return {
            'response_category': response_category,
            'significant_improvements': significant_improvements,
            'total_outcomes_assessed': total_outcomes,
            'response_rate': (significant_improvements / total_outcomes * 100) if total_outcomes > 0 else 0
        }

# ============================================================================
# API ENDPOINTS FOR OUTCOME COLLECTION
# ============================================================================

# Create API router
outcome_router = APIRouter()

# Global service instance
outcome_service = OutcomeCollectionService()

@outcome_router.post("/patients/{patient_id}/assessment-schedule")
async def create_assessment_schedule(
    patient_id: str,
    baseline_date: datetime,
    study_duration_weeks: int = 52
):
    """Create assessment schedule for patient"""
    try:
        schedule = outcome_service.create_patient_assessment_schedule(
            patient_id, baseline_date, study_duration_weeks
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
        records = outcome_service.get_patient_outcomes(patient_id, start_date, end_date)
        return [record.dict() for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/patients/{patient_id}/outcome-changes")
async def get_outcome_changes(patient_id: str):
    """Get outcome changes from baseline for patient"""
    try:
        changes = outcome_service.calculate_outcome_changes(patient_id)
        return changes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@outcome_router.get("/patients/{patient_id}/outcome-summary")
async def get_outcome_summary(patient_id: str):
    """Get comprehensive outcome summary for patient"""
    try:
        summary = outcome_service.generate_outcome_summary(patient_id)
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
        all_records = list(outcome_service.outcome_records.values())
        
        quality_summary = {
            'total_records': len(all_records),
            'quality_distribution': {},
            'patients_with_data': len(set(r.patient_id for r in all_records)),
            'average_assessments_per_patient': 0
        }
        
        if all_records:
            # Quality distribution
            for record in all_records:
                quality = record.data_quality.value
                quality_summary['quality_distribution'][quality] = quality_summary['quality_distribution'].get(quality, 0) + 1
            
            # Average assessments per patient
            patient_counts = {}
            for record in all_records:
                patient_counts[record.patient_id] = patient_counts.get(record.patient_id, 0) + 1
            
            quality_summary['average_assessments_per_patient'] = sum(patient_counts.values()) / len(patient_counts)
        
        return quality_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Example usage
    collector = DataCollector()
    
    # Add sample form
    pain_form = create_pain_assessment_form()
    collector.add_form(pain_form)
    
    # Add sample measurements
    sample_measurements = create_sample_measurements()
    for measurement in sample_measurements:
        collector.add_measurement(measurement)
    
    print(f"Created data collector with {len(collector.measurements)} measurements")
    print(f"Added {len(collector.forms)} forms")
    
    # Generate quality report
    quality_report = collector.generate_data_quality_report()
    print(f"Quality report: {quality_report}") 