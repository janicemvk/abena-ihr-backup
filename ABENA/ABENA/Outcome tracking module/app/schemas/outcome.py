from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from uuid import UUID


class OutcomeBase(BaseModel):
    """Base outcome schema"""
    patient_id: UUID
    measurement_date: date
    outcome_type: str = Field(..., max_length=50)
    outcome_value: float = Field(..., ge=0, le=100)
    measurement_method: str = Field(..., max_length=50)
    
    @validator('outcome_type')
    def validate_outcome_type(cls, v):
        valid_types = [
            'pain_score', 'functional_assessment', 'mobility_score',
            'quality_of_life', 'satisfaction_score', 'adherence_rate'
        ]
        if v not in valid_types:
            raise ValueError(f'outcome_type must be one of: {valid_types}')
        return v


class OutcomeCreate(OutcomeBase):
    """Schema for creating a new outcome"""
    pass


class OutcomeUpdate(BaseModel):
    """Schema for updating an outcome"""
    measurement_date: Optional[date] = None
    outcome_type: Optional[str] = Field(None, max_length=50)
    outcome_value: Optional[float] = Field(None, ge=0, le=100)
    measurement_method: Optional[str] = Field(None, max_length=50)
    
    @validator('outcome_type')
    def validate_outcome_type(cls, v):
        if v is not None:
            valid_types = [
                'pain_score', 'functional_assessment', 'mobility_score',
                'quality_of_life', 'satisfaction_score', 'adherence_rate'
            ]
            if v not in valid_types:
                raise ValueError(f'outcome_type must be one of: {valid_types}')
        return v


class OutcomeResponse(OutcomeBase):
    """Schema for outcome response"""
    outcome_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class OutcomeList(BaseModel):
    """Schema for list of outcomes"""
    outcomes: list[OutcomeResponse]
    total: int
    page: int
    size: int 