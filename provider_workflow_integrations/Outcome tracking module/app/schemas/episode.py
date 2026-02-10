from datetime import date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID


class EpisodeBase(BaseModel):
    """Base episode schema"""
    patient_id: UUID
    start_date: date
    treatment_plan: Optional[Dict[str, Any]] = None
    provider_id: UUID
    status: str = Field(default="active", max_length=20)
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'completed', 'discontinued']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {valid_statuses}')
        return v


class EpisodeCreate(EpisodeBase):
    """Schema for creating a new episode"""
    pass


class EpisodeUpdate(BaseModel):
    """Schema for updating an episode"""
    start_date: Optional[date] = None
    treatment_plan: Optional[Dict[str, Any]] = None
    provider_id: Optional[UUID] = None
    status: Optional[str] = Field(None, max_length=20)
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['active', 'completed', 'discontinued']
            if v not in valid_statuses:
                raise ValueError(f'status must be one of: {valid_statuses}')
        return v


class EpisodeResponse(EpisodeBase):
    """Schema for episode response"""
    episode_id: UUID
    
    class Config:
        from_attributes = True


class EpisodeList(BaseModel):
    """Schema for list of episodes"""
    episodes: list[EpisodeResponse]
    total: int
    page: int
    size: int 