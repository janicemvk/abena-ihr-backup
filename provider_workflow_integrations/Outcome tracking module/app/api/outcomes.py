from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.services.outcome_service import OutcomeService
from app.schemas.outcome import OutcomeCreate, OutcomeUpdate, OutcomeResponse, OutcomeList

router = APIRouter(prefix="/outcomes", tags=["outcomes"])


@router.post("/", response_model=OutcomeResponse)
def create_outcome(
    outcome_data: OutcomeCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient outcome"""
    service = OutcomeService(db)
    return service.create_outcome(outcome_data)


@router.get("/{outcome_id}", response_model=OutcomeResponse)
def get_outcome(
    outcome_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific outcome by ID"""
    service = OutcomeService(db)
    outcome = service.get_outcome(outcome_id)
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return outcome


@router.get("/patient/{patient_id}", response_model=List[OutcomeResponse])
def get_patient_outcomes(
    patient_id: UUID,
    outcome_type: Optional[str] = Query(None, description="Filter by outcome type"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get all outcomes for a specific patient"""
    service = OutcomeService(db)
    return service.get_patient_outcomes(patient_id, outcome_type, limit, offset)


@router.put("/{outcome_id}", response_model=OutcomeResponse)
def update_outcome(
    outcome_id: UUID,
    outcome_data: OutcomeUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing outcome"""
    service = OutcomeService(db)
    outcome = service.update_outcome(outcome_id, outcome_data)
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return outcome


@router.delete("/{outcome_id}")
def delete_outcome(
    outcome_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an outcome"""
    service = OutcomeService(db)
    success = service.delete_outcome(outcome_id)
    if not success:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return {"message": "Outcome deleted successfully"}


@router.get("/patient/{patient_id}/statistics/{outcome_type}")
def get_outcome_statistics(
    patient_id: UUID,
    outcome_type: str,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific outcome type for a patient"""
    service = OutcomeService(db)
    return service.get_outcome_statistics(patient_id, outcome_type) 