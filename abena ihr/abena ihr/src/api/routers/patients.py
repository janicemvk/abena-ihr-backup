"""
Patients API Router

This module provides RESTful API endpoints for managing patient data
in the Abena IHR system.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
from pydantic import BaseModel, Field, validator

from ...core.data_models import Patient, PatientStatus
from ...core.data_models import create_patient_id, validate_patient_data

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models for API requests/responses
class PatientRequest(BaseModel):
    """Request model for creating/updating patients."""
    first_name: str = Field(..., description="Patient's first name")
    last_name: str = Field(..., description="Patient's last name")
    date_of_birth: Optional[date] = Field(None, description="Patient's date of birth")
    gender: Optional[str] = Field(None, description="Patient's gender")
    status: PatientStatus = Field(PatientStatus.ACTIVE, description="Patient status")
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class PatientResponse(BaseModel):
    """Response model for patient data."""
    id: str
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[date]
    gender: Optional[str]
    status: PatientStatus
    created_at: datetime
    updated_at: datetime


# Patient Management Endpoints
@router.get("/patients", response_model=List[PatientResponse])
async def list_patients(
    status: Optional[PatientStatus] = Query(None, description="Filter by patient status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of patients to return"),
    offset: int = Query(0, ge=0, description="Number of patients to skip")
) -> List[PatientResponse]:
    """
    List all patients with optional filtering.
    
    Args:
        status: Optional filter by patient status
        limit: Maximum number of patients to return
        offset: Number of patients to skip
        
    Returns:
        List of patients
    """
    try:
        # In a real app, this would query the database
        # For now, return empty list
        patients = []
        
        # Apply pagination
        patients = patients[offset:offset + limit]
        
        return [
            PatientResponse(
                id=patient.id,
                patient_id=patient.patient_id,
                first_name=patient.first_name,
                last_name=patient.last_name,
                date_of_birth=patient.date_of_birth,
                gender=patient.gender,
                status=patient.status,
                created_at=patient.created_at,
                updated_at=patient.updated_at
            )
            for patient in patients
        ]
    except Exception as e:
        logger.error(f"Error listing patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to list patients")


@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str = Path(..., description="ID of the patient to retrieve")
) -> PatientResponse:
    """
    Get a specific patient by ID.
    
    Args:
        patient_id: ID of the patient to retrieve
        
    Returns:
        Patient details
    """
    try:
        # In a real app, this would query the database
        # For now, return 404
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient")


@router.post("/patients", response_model=PatientResponse, status_code=201)
async def create_patient(
    patient_data: PatientRequest
) -> PatientResponse:
    """
    Create a new patient.
    
    Args:
        patient_data: Patient data
        
    Returns:
        Created patient
    """
    try:
        patient = Patient(
            patient_id=create_patient_id(),
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            date_of_birth=patient_data.date_of_birth,
            gender=patient_data.gender,
            status=patient_data.status
        )
        
        if not validate_patient_data(patient):
            raise HTTPException(status_code=400, detail="Invalid patient data")
        
        # In a real app, this would save to database
        
        return PatientResponse(
            id=patient.id,
            patient_id=patient.patient_id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender,
            status=patient.status,
            created_at=patient.created_at,
            updated_at=patient.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to create patient")


@router.put("/patients/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str = Path(..., description="ID of the patient to update")
) -> PatientResponse:
    """
    Update an existing patient.
    
    Args:
        patient_id: ID of the patient to update
        
    Returns:
        Updated patient
    """
    try:
        # In a real app, this would update the database
        # For now, return 404
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update patient")


@router.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: str = Path(..., description="ID of the patient to delete")
) -> Dict[str, Any]:
    """
    Delete a patient.
    
    Args:
        patient_id: ID of the patient to delete
        
    Returns:
        Deletion confirmation
    """
    try:
        # In a real app, this would delete from database
        # For now, return 404
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete patient") 