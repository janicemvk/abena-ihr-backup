from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.services.episode_service import EpisodeService
from app.schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse, EpisodeList

router = APIRouter(prefix="/episodes", tags=["episodes"])


class DiscontinuationRequest(BaseModel):
    reason: Optional[str] = None


class TreatmentPlanUpdate(BaseModel):
    treatment_plan: dict


@router.post("/", response_model=EpisodeResponse)
def create_episode(
    episode_data: EpisodeCreate,
    db: Session = Depends(get_db)
):
    """Create a new treatment episode"""
    service = EpisodeService(db)
    return service.create_episode(episode_data)


@router.get("/{episode_id}", response_model=EpisodeResponse)
def get_episode(
    episode_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific episode by ID"""
    service = EpisodeService(db)
    episode = service.get_episode(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


@router.get("/patient/{patient_id}", response_model=List[EpisodeResponse])
def get_patient_episodes(
    patient_id: UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get all episodes for a specific patient"""
    service = EpisodeService(db)
    return service.get_patient_episodes(patient_id, status, limit, offset)


@router.get("/patient/{patient_id}/active", response_model=EpisodeResponse)
def get_active_episode(
    patient_id: UUID,
    db: Session = Depends(get_db)
):
    """Get the currently active episode for a patient"""
    service = EpisodeService(db)
    episode = service.get_active_episode(patient_id)
    if not episode:
        raise HTTPException(status_code=404, detail="No active episode found")
    return episode


@router.put("/{episode_id}", response_model=EpisodeResponse)
def update_episode(
    episode_id: UUID,
    episode_data: EpisodeUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing episode"""
    service = EpisodeService(db)
    episode = service.update_episode(episode_id, episode_data)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


@router.delete("/{episode_id}")
def delete_episode(
    episode_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an episode"""
    service = EpisodeService(db)
    success = service.delete_episode(episode_id)
    if not success:
        raise HTTPException(status_code=404, detail="Episode not found")
    return {"message": "Episode deleted successfully"}


@router.post("/{episode_id}/complete", response_model=EpisodeResponse)
def complete_episode(
    episode_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark an episode as completed"""
    service = EpisodeService(db)
    episode = service.complete_episode(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


@router.post("/{episode_id}/discontinue", response_model=EpisodeResponse)
def discontinue_episode(
    episode_id: UUID,
    discontinuation_request: DiscontinuationRequest,
    db: Session = Depends(get_db)
):
    """Discontinue an episode"""
    service = EpisodeService(db)
    episode = service.discontinue_episode(episode_id, discontinuation_request.reason)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


@router.put("/{episode_id}/treatment-plan", response_model=EpisodeResponse)
def update_treatment_plan(
    episode_id: UUID,
    treatment_plan_update: TreatmentPlanUpdate,
    db: Session = Depends(get_db)
):
    """Update the treatment plan for an episode"""
    service = EpisodeService(db)
    episode = service.update_treatment_plan(episode_id, treatment_plan_update.treatment_plan)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode 