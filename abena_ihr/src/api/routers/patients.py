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
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from ...core.data_models import Patient, PatientStatus
from ...core.utils import create_patient_id, validate_patient_data

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL", "postgresql://abena_user:abena_password@postgres:5432/abena_ihr"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

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
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Build query based on filters
            query = """
                SELECT 
                    patient_id,
                    first_name,
                    last_name,
                    date_of_birth,
                    gender,
                    CASE WHEN is_active THEN 'active' ELSE 'inactive' END as status,
                    created_at,
                    updated_at
                FROM patients
            """
            params = []
            
            if status:
                if status == PatientStatus.ACTIVE:
                    query += " WHERE is_active = true"
                elif status == PatientStatus.INACTIVE:
                    query += " WHERE is_active = false"
            
            query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, params)
            patients = cur.fetchall()
        conn.close()
        
        logger.info(f"✅ Real patient data loaded from database: {len(patients)} patients")
        
        return [
            PatientResponse(
                id=str(patient['patient_id']),
                patient_id=str(patient['patient_id']),
                first_name=patient['first_name'],
                last_name=patient['last_name'],
                date_of_birth=patient['date_of_birth'],
                gender=patient['gender'],
                status=PatientStatus(patient['status']),
                created_at=patient['created_at'],
                updated_at=patient['updated_at']
            )
            for patient in patients
        ]
    except Exception as e:
        logger.error(f"Error listing patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to list patients")

@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str = Path(..., description="Patient ID")) -> PatientResponse:
    """
    Get a specific patient by ID.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Patient data
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    patient_id,
                    first_name,
                    last_name,
                    date_of_birth,
                    gender,
                    CASE WHEN is_active THEN 'active' ELSE 'inactive' END as status,
                    created_at,
                    updated_at
                FROM patients 
                WHERE patient_id = %s
            """, (patient_id,))
            patient = cur.fetchone()
        conn.close()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        logger.info(f"✅ Real patient data loaded from database: {patient_id}")
        
        return PatientResponse(
            id=str(patient['patient_id']),
            patient_id=str(patient['patient_id']),
            first_name=patient['first_name'],
            last_name=patient['last_name'],
            date_of_birth=patient['date_of_birth'],
            gender=patient['gender'],
            status=PatientStatus(patient['status']),
            created_at=patient['created_at'],
            updated_at=patient['updated_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient")

@router.post("/patients", response_model=PatientResponse)
async def create_patient(patient_request: PatientRequest) -> PatientResponse:
    """
    Create a new patient.
    
    Args:
        patient_request: Patient data
        
    Returns:
        Created patient data
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO patients (
                    first_name,
                    last_name,
                    date_of_birth,
                    gender,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING 
                    patient_id,
                    first_name,
                    last_name,
                    date_of_birth,
                    gender,
                    is_active,
                    created_at,
                    updated_at
            """, (
                patient_request.first_name,
                patient_request.last_name,
                patient_request.date_of_birth,
                patient_request.gender,
                patient_request.status == PatientStatus.ACTIVE,
                datetime.now(),
                datetime.now()
            ))
            patient = cur.fetchone()
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Patient created in database: {patient['patient_id']}")
        
        return PatientResponse(
            id=str(patient['patient_id']),
            patient_id=str(patient['patient_id']),
            first_name=patient['first_name'],
            last_name=patient['last_name'],
            date_of_birth=patient['date_of_birth'],
            gender=patient['gender'],
            status=PatientStatus.ACTIVE if patient['is_active'] else PatientStatus.INACTIVE,
            created_at=patient['created_at'],
            updated_at=patient['updated_at']
        )
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to create patient")

@router.put("/patients/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str = Path(..., description="Patient ID"),
    patient_request: PatientRequest = None
) -> PatientResponse:
    """
    Update a patient.
    
    Args:
        patient_id: Patient ID
        patient_request: Updated patient data
        
    Returns:
        Updated patient data
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE patients 
                SET 
                    first_name = %s,
                    last_name = %s,
                    date_of_birth = %s,
                    gender = %s,
                    is_active = %s,
                    updated_at = %s
                WHERE patient_id = %s
                RETURNING 
                    patient_id,
                    first_name,
                    last_name,
                    date_of_birth,
                    gender,
                    is_active,
                    created_at,
                    updated_at
            """, (
                patient_request.first_name,
                patient_request.last_name,
                patient_request.date_of_birth,
                patient_request.gender,
                patient_request.status == PatientStatus.ACTIVE,
                datetime.now(),
                patient_id
            ))
            patient = cur.fetchone()
            conn.commit()
        conn.close()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        logger.info(f"✅ Patient updated in database: {patient_id}")
        
        return PatientResponse(
            id=str(patient['patient_id']),
            patient_id=str(patient['patient_id']),
            first_name=patient['first_name'],
            last_name=patient['last_name'],
            date_of_birth=patient['date_of_birth'],
            gender=patient['gender'],
            status=PatientStatus.ACTIVE if patient['is_active'] else PatientStatus.INACTIVE,
            created_at=patient['created_at'],
            updated_at=patient['updated_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update patient")

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str = Path(..., description="Patient ID")):
    """
    Delete a patient (soft delete by setting is_active to false).
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Success message
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE patients 
                SET is_active = false, updated_at = %s
                WHERE patient_id = %s
            """, (datetime.now(), patient_id))
            
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Patient not found")
            
            conn.commit()
        conn.close()
        
        logger.info(f"✅ Patient soft deleted in database: {patient_id}")
        
        return {"message": "Patient deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete patient") 