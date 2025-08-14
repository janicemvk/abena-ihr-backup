"""
Clinical Outcomes API Router

This module provides RESTful API endpoints for managing clinical outcomes,
measurements, data collection forms, and outcome frameworks.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
from pydantic import BaseModel, Field, validator
import uuid

# Import clinical outcomes modules
from ...clinical_outcomes.outcome_framework import (
    OutcomeFramework, OutcomeDefinition, OutcomeType, MeasurementScale,
    MeasurementTiming, DataQualityLevel,
    PainScoreAssessment, WOMACAssessment, ODIAssessment,
    MedicationUsageAssessment, HealthcareUtilizationAssessment,
    QualityOfLifeAssessment, WeeklySymptomTracking
)
from ...clinical_outcomes.data_collection import (
    DataCollector, ClinicalMeasurement, DataCollectionForm, 
    DataSource, DataQuality
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services (in a real app, these would be dependency injected)
data_collector = DataCollector()


# Pydantic models for API requests/responses
class OutcomeDefinitionRequest(BaseModel):
    """Request model for creating/updating outcome definitions."""
    name: str = Field(..., description="Unique name for the outcome")
    description: str = Field(..., description="Description of the outcome")
    outcome_type: OutcomeType = Field(..., description="Type of outcome")
    measurement_scale: MeasurementScale = Field(..., description="Measurement scale")
    unit_of_measurement: Optional[str] = Field(None, description="Unit of measurement")
    target_value: Optional[float] = Field(None, description="Target value")
    min_value: Optional[float] = Field(None, description="Minimum valid value")
    max_value: Optional[float] = Field(None, description="Maximum valid value")
    categories: Optional[List[str]] = Field(None, description="Valid categories for categorical outcomes")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @validator('target_value', 'min_value', 'max_value')
    def validate_values(cls, v, values):
        if v is not None:
            if 'min_value' in values and values['min_value'] is not None and v < values['min_value']:
                raise ValueError("Target value cannot be less than minimum value")
            if 'max_value' in values and values['max_value'] is not None and v > values['max_value']:
                raise ValueError("Target value cannot be greater than maximum value")
        return v


class OutcomeDefinitionResponse(BaseModel):
    """Response model for outcome definitions."""
    id: str
    name: str
    description: str
    outcome_type: OutcomeType
    measurement_scale: MeasurementScale
    unit_of_measurement: Optional[str]
    target_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    categories: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class ClinicalMeasurementRequest(BaseModel):
    """Request model for creating clinical measurements."""
    patient_id: str = Field(..., description="Patient identifier")
    outcome_name: str = Field(..., description="Name of the outcome being measured")
    value: Any = Field(..., description="Measurement value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    measurement_date: Optional[datetime] = Field(None, description="Date of measurement")
    data_source: DataSource = Field(DataSource.CLINICAL_ASSESSMENT, description="Source of data")
    notes: Optional[str] = Field(None, description="Additional notes")
    collected_by: Optional[str] = Field(None, description="Person who collected the data")
    form_id: Optional[str] = Field(None, description="Associated form ID")


class ClinicalMeasurementResponse(BaseModel):
    """Response model for clinical measurements."""
    id: str
    patient_id: str
    outcome_name: str
    value: Any
    unit: Optional[str]
    measurement_date: datetime
    data_source: DataSource
    data_quality: DataQuality
    notes: Optional[str]
    collected_by: Optional[str]
    validated_by: Optional[str]
    validation_date: Optional[datetime]
    form_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class DataCollectionFormRequest(BaseModel):
    """Request model for creating data collection forms."""
    form_name: str = Field(..., description="Name of the form")
    version: str = Field("1.0", description="Form version")
    description: Optional[str] = Field(None, description="Form description")
    fields: List[Dict[str, Any]] = Field(..., description="Form field definitions")
    required_fields: List[str] = Field([], description="Required field names")
    validation_rules: Dict[str, Any] = Field({}, description="Validation rules")


class DataCollectionFormResponse(BaseModel):
    """Response model for data collection forms."""
    id: str
    form_name: str
    version: str
    description: Optional[str]
    fields: List[Dict[str, Any]]
    required_fields: List[str]
    validation_rules: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class OutcomeEvaluationRequest(BaseModel):
    """Request model for evaluating outcomes."""
    measurement_id: str = Field(..., description="ID of the measurement to evaluate")
    outcome_name: str = Field(..., description="Name of the outcome to evaluate against")


class OutcomeEvaluationResponse(BaseModel):
    """Response model for outcome evaluations."""
    id: str
    measurement_id: str
    outcome_name: str
    is_valid: bool
    evaluation_results: Dict[str, Any]
    evaluated_at: datetime
    evaluated_by: Optional[str]


# Outcome Definition Endpoints
@router.get("/outcomes", response_model=List[OutcomeDefinitionResponse])
async def list_outcomes(
    outcome_type: Optional[OutcomeType] = Query(None, description="Filter by outcome type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of outcomes to return"),
    offset: int = Query(0, ge=0, description="Number of outcomes to skip")
) -> List[OutcomeDefinitionResponse]:
    """
    List all outcome definitions with optional filtering.
    
    Args:
        outcome_type: Optional filter by outcome type
        limit: Maximum number of outcomes to return
        offset: Number of outcomes to skip
        
    Returns:
        List of outcome definitions
    """
    try:
        outcomes = data_collector.outcome_framework.list_outcomes(outcome_type)
        
        # Apply pagination
        outcomes = outcomes[offset:offset + limit]
        
        return [
            OutcomeDefinitionResponse(
                id=str(uuid.uuid4()),  # In real app, get from database
                name=outcome.name,
                description=outcome.description,
                outcome_type=outcome.outcome_type,
                measurement_scale=outcome.measurement_scale,
                unit_of_measurement=outcome.unit_of_measurement,
                target_value=outcome.target_value,
                min_value=outcome.min_value,
                max_value=outcome.max_value,
                categories=outcome.categories,
                created_at=outcome.created_at,
                updated_at=outcome.updated_at
            )
            for outcome in outcomes
        ]
    except Exception as e:
        logger.error(f"Error listing outcomes: {e}")
        raise HTTPException(status_code=500, detail="Failed to list outcomes")


@router.get("/outcomes/{outcome_name}", response_model=OutcomeDefinitionResponse)
async def get_outcome(
    outcome_name: str = Path(..., description="Name of the outcome to retrieve")
) -> OutcomeDefinitionResponse:
    """
    Get a specific outcome definition by name.
    
    Args:
        outcome_name: Name of the outcome to retrieve
        
    Returns:
        Outcome definition details
    """
    try:
        outcome = data_collector.outcome_framework.get_outcome(outcome_name)
        if not outcome:
            raise HTTPException(status_code=404, detail=f"Outcome '{outcome_name}' not found")
        
        return OutcomeDefinitionResponse(
            id=str(uuid.uuid4()),  # In real app, get from database
            name=outcome.name,
            description=outcome.description,
            outcome_type=outcome.outcome_type,
            measurement_scale=outcome.measurement_scale,
            unit_of_measurement=outcome.unit_of_measurement,
            target_value=outcome.target_value,
            min_value=outcome.min_value,
            max_value=outcome.max_value,
            categories=outcome.categories,
            created_at=outcome.created_at,
            updated_at=outcome.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting outcome {outcome_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get outcome")


@router.post("/outcomes", response_model=OutcomeDefinitionResponse, status_code=201)
async def create_outcome(
    outcome_data: OutcomeDefinitionRequest
) -> OutcomeDefinitionResponse:
    """
    Create a new outcome definition.
    
    Args:
        outcome_data: Outcome definition data
        
    Returns:
        Created outcome definition
    """
    try:
        outcome = data_collector.outcome_framework.OutcomeDefinition(
            name=outcome_data.name,
            description=outcome_data.description,
            outcome_type=outcome_data.outcome_type,
            measurement_scale=outcome_data.measurement_scale,
            unit_of_measurement=outcome_data.unit_of_measurement,
            target_value=outcome_data.target_value,
            min_value=outcome_data.min_value,
            max_value=outcome_data.max_value,
            categories=outcome_data.categories
        )
        
        success = data_collector.outcome_framework.add_outcome(outcome)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create outcome")
        
        return OutcomeDefinitionResponse(
            id=str(uuid.uuid4()),  # In real app, get from database
            name=outcome.name,
            description=outcome.description,
            outcome_type=outcome.outcome_type,
            measurement_scale=outcome.measurement_scale,
            unit_of_measurement=outcome.unit_of_measurement,
            target_value=outcome.target_value,
            min_value=outcome.min_value,
            max_value=outcome.max_value,
            categories=outcome.categories,
            created_at=outcome.created_at,
            updated_at=outcome.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating outcome: {e}")
        raise HTTPException(status_code=500, detail="Failed to create outcome")


# Clinical Measurement Endpoints
@router.get("/measurements", response_model=List[ClinicalMeasurementResponse])
async def list_measurements(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    outcome_name: Optional[str] = Query(None, description="Filter by outcome name"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of measurements to return"),
    offset: int = Query(0, ge=0, description="Number of measurements to skip")
) -> List[ClinicalMeasurementResponse]:
    """
    List clinical measurements with optional filtering.
    
    Args:
        patient_id: Optional filter by patient ID
        outcome_name: Optional filter by outcome name
        start_date: Optional filter by start date
        end_date: Optional filter by end date
        limit: Maximum number of measurements to return
        offset: Number of measurements to skip
        
    Returns:
        List of clinical measurements
    """
    try:
        measurements = data_collector.get_measurements(
            patient_id=patient_id,
            outcome_name=outcome_name,
            start_date=start_date,
            end_date=end_date
        )
        
        # Apply pagination
        measurements = measurements[offset:offset + limit]
        
        return [
            ClinicalMeasurementResponse(
                id=measurement.id,
                patient_id=measurement.patient_id,
                outcome_name=measurement.outcome_name,
                value=measurement.value,
                unit=measurement.unit,
                measurement_date=measurement.measurement_date,
                data_source=measurement.data_source,
                data_quality=measurement.data_quality,
                notes=measurement.notes,
                collected_by=measurement.collected_by,
                validated_by=measurement.validated_by,
                validation_date=measurement.validation_date,
                form_id=measurement.form_id,
                created_at=measurement.created_at,
                updated_at=measurement.updated_at
            )
            for measurement in measurements
        ]
    except Exception as e:
        logger.error(f"Error listing measurements: {e}")
        raise HTTPException(status_code=500, detail="Failed to list measurements")


@router.post("/measurements", response_model=ClinicalMeasurementResponse, status_code=201)
async def create_measurement(
    measurement_data: ClinicalMeasurementRequest
) -> ClinicalMeasurementResponse:
    """
    Create a new clinical measurement.
    
    Args:
        measurement_data: Clinical measurement data
        
    Returns:
        Created clinical measurement
    """
    try:
        measurement = ClinicalMeasurement(
            patient_id=measurement_data.patient_id,
            outcome_name=measurement_data.outcome_name,
            value=measurement_data.value,
            unit=measurement_data.unit,
            measurement_date=measurement_data.measurement_date or datetime.now(),
            data_source=measurement_data.data_source,
            notes=measurement_data.notes,
            collected_by=measurement_data.collected_by
        )
        
        success = data_collector.add_measurement(measurement)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create measurement")
        
        return ClinicalMeasurementResponse(
            id=measurement.id,
            patient_id=measurement.patient_id,
            outcome_name=measurement.outcome_name,
            value=measurement.value,
            unit=measurement.unit,
            measurement_date=measurement.measurement_date,
            data_source=measurement.data_source,
            data_quality=measurement.data_quality,
            notes=measurement.notes,
            collected_by=measurement.collected_by,
            validated_by=measurement.validated_by,
            validation_date=measurement.validation_date,
            form_id=measurement.form_id,
            created_at=measurement.created_at,
            updated_at=measurement.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating measurement: {e}")
        raise HTTPException(status_code=500, detail="Failed to create measurement")


@router.get("/measurements/{measurement_id}", response_model=ClinicalMeasurementResponse)
async def get_measurement(
    measurement_id: str = Path(..., description="ID of the measurement to retrieve")
) -> ClinicalMeasurementResponse:
    """
    Get a specific clinical measurement by ID.
    
    Args:
        measurement_id: ID of the measurement to retrieve
        
    Returns:
        Clinical measurement details
    """
    try:
        # In real app, get from database
        measurements = data_collector.get_measurements()
        measurement = next((m for m in measurements if m.id == measurement_id), None)
        
        if not measurement:
            raise HTTPException(status_code=404, detail=f"Measurement '{measurement_id}' not found")
        
        return ClinicalMeasurementResponse(
            id=measurement.id,
            patient_id=measurement.patient_id,
            outcome_name=measurement.outcome_name,
            value=measurement.value,
            unit=measurement.unit,
            measurement_date=measurement.measurement_date,
            data_source=measurement.data_source,
            data_quality=measurement.data_quality,
            notes=measurement.notes,
            collected_by=measurement.collected_by,
            validated_by=measurement.validated_by,
            validation_date=measurement.validation_date,
            form_id=measurement.form_id,
            created_at=measurement.created_at,
            updated_at=measurement.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting measurement {measurement_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get measurement")


# Data Collection Form Endpoints
@router.get("/forms", response_model=List[DataCollectionFormResponse])
async def list_forms(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of forms to return"),
    offset: int = Query(0, ge=0, description="Number of forms to skip")
) -> List[DataCollectionFormResponse]:
    """
    List all data collection forms.
    
    Args:
        limit: Maximum number of forms to return
        offset: Number of forms to skip
        
    Returns:
        List of data collection forms
    """
    try:
        forms = list(data_collector.forms.values())
        
        # Apply pagination
        forms = forms[offset:offset + limit]
        
        return [
            DataCollectionFormResponse(
                id=form.form_id,
                form_name=form.form_name,
                version=form.version,
                description=form.description,
                fields=form.fields,
                required_fields=form.required_fields,
                validation_rules=form.validation_rules,
                created_at=form.created_at,
                updated_at=form.updated_at
            )
            for form in forms
        ]
    except Exception as e:
        logger.error(f"Error listing forms: {e}")
        raise HTTPException(status_code=500, detail="Failed to list forms")


@router.post("/forms", response_model=DataCollectionFormResponse, status_code=201)
async def create_form(
    form_data: DataCollectionFormRequest
) -> DataCollectionFormResponse:
    """
    Create a new data collection form.
    
    Args:
        form_data: Form definition data
        
    Returns:
        Created data collection form
    """
    try:
        form = DataCollectionForm(
            form_name=form_data.form_name,
            version=form_data.version,
            description=form_data.description,
            fields=form_data.fields,
            required_fields=form_data.required_fields,
            validation_rules=form_data.validation_rules
        )
        
        success = data_collector.add_form(form)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create form")
        
        return DataCollectionFormResponse(
            id=form.form_id,
            form_name=form.form_name,
            version=form.version,
            description=form.description,
            fields=form.fields,
            required_fields=form.required_fields,
            validation_rules=form.validation_rules,
            created_at=form.created_at,
            updated_at=form.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating form: {e}")
        raise HTTPException(status_code=500, detail="Failed to create form")


# Outcome Evaluation Endpoints
@router.post("/evaluate", response_model=Dict[str, Any])
async def evaluate_outcome(
    outcome_name: str = Query(..., description="Name of the outcome to evaluate"),
    value: Any = Query(..., description="Value to evaluate")
) -> Dict[str, Any]:
    """
    Evaluate an outcome value against its definition.
    
    Args:
        outcome_name: Name of the outcome to evaluate
        value: Value to evaluate
        
    Returns:
        Evaluation results
    """
    try:
        result = data_collector.outcome_framework.evaluate_outcome(outcome_name, value)
        return result
    except Exception as e:
        logger.error(f"Error evaluating outcome {outcome_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate outcome")


# Data Quality Endpoints
@router.put("/measurements/{measurement_id}/quality")
async def update_data_quality(
    measurement_id: str = Path(..., description="ID of the measurement"),
    quality: DataQuality = Query(..., description="New data quality level"),
    validated_by: str = Query(..., description="Person performing validation")
) -> Dict[str, Any]:
    """
    Update data quality assessment for a measurement.
    
    Args:
        measurement_id: ID of the measurement
        quality: New data quality level
        validated_by: Person performing validation
        
    Returns:
        Update confirmation
    """
    try:
        success = data_collector.validate_data_quality(measurement_id, quality, validated_by)
        if not success:
            raise HTTPException(status_code=404, detail=f"Measurement '{measurement_id}' not found")
        
        return {
            "message": "Data quality updated successfully",
            "measurement_id": measurement_id,
            "new_quality": quality.value,
            "validated_by": validated_by,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating data quality for {measurement_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update data quality")


# Reporting Endpoints
@router.get("/reports/quality")
async def get_data_quality_report() -> Dict[str, Any]:
    """
    Generate a data quality report.
    
    Returns:
        Data quality statistics
    """
    try:
        report = data_collector.generate_data_quality_report()
        return report
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quality report")


@router.get("/reports/measurements")
async def get_measurement_summary(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    outcome_name: Optional[str] = Query(None, description="Filter by outcome name")
) -> Dict[str, Any]:
    """
    Generate a measurement summary report.
    
    Args:
        patient_id: Optional filter by patient ID
        outcome_name: Optional filter by outcome name
        
    Returns:
        Measurement summary statistics
    """
    try:
        measurements = data_collector.get_measurements(patient_id, outcome_name)
        
        if not measurements:
            return {
                "message": "No measurements found",
                "filters": {
                    "patient_id": patient_id,
                    "outcome_name": outcome_name
                },
                "summary": {
                    "total_measurements": 0,
                    "unique_patients": 0,
                    "unique_outcomes": 0
                }
            }
        
        unique_patients = len(set(m.patient_id for m in measurements))
        unique_outcomes = len(set(m.outcome_name for m in measurements))
        
        return {
            "filters": {
                "patient_id": patient_id,
                "outcome_name": outcome_name
            },
            "summary": {
                "total_measurements": len(measurements),
                "unique_patients": unique_patients,
                "unique_outcomes": unique_outcomes,
                "date_range": {
                    "earliest": min(m.measurement_date for m in measurements).isoformat(),
                    "latest": max(m.measurement_date for m in measurements).isoformat()
                }
            },
            "by_outcome": {
                outcome: len([m for m in measurements if m.outcome_name == outcome])
                for outcome in set(m.outcome_name for m in measurements)
            },
            "by_quality": {
                quality.value: len([m for m in measurements if m.data_quality == quality])
                for quality in DataQuality
            }
        }
    except Exception as e:
        logger.error(f"Error generating measurement summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate measurement summary")


# Export Endpoints
@router.get("/export/measurements")
async def export_measurements(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    outcome_name: Optional[str] = Query(None, description="Filter by outcome name")
) -> Dict[str, Any]:
    """
    Export measurements in specified format.
    
    Args:
        format: Export format (json or csv)
        patient_id: Optional filter by patient ID
        outcome_name: Optional filter by outcome name
        
    Returns:
        Export file information
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"measurements_{timestamp}.json"
            success = data_collector.export_to_json(filename, patient_id, outcome_name)
        else:  # csv
            filename = f"measurements_{timestamp}.csv"
            success = data_collector.export_to_csv(filename, patient_id, outcome_name)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to export measurements")
        
        return {
            "message": "Export completed successfully",
            "filename": filename,
            "format": format,
            "filters": {
                "patient_id": patient_id,
                "outcome_name": outcome_name
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting measurements: {e}")
        raise HTTPException(status_code=500, detail="Failed to export measurements") 