from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID

from app.models.outcome import PatientOutcome
from app.schemas.outcome import OutcomeCreate, OutcomeUpdate, OutcomeResponse


class OutcomeService:
    """Service for managing patient outcomes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_outcome(self, outcome_data: OutcomeCreate) -> OutcomeResponse:
        """Create a new patient outcome"""
        db_outcome = PatientOutcome(**outcome_data.dict())
        self.db.add(db_outcome)
        self.db.commit()
        self.db.refresh(db_outcome)
        return OutcomeResponse.from_orm(db_outcome)
    
    def get_outcome(self, outcome_id: UUID) -> Optional[OutcomeResponse]:
        """Get a specific outcome by ID"""
        outcome = self.db.query(PatientOutcome).filter(
            PatientOutcome.outcome_id == outcome_id
        ).first()
        return OutcomeResponse.from_orm(outcome) if outcome else None
    
    def get_patient_outcomes(
        self, 
        patient_id: UUID, 
        outcome_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[OutcomeResponse]:
        """Get all outcomes for a specific patient"""
        query = self.db.query(PatientOutcome).filter(
            PatientOutcome.patient_id == patient_id
        )
        
        if outcome_type:
            query = query.filter(PatientOutcome.outcome_type == outcome_type)
        
        outcomes = query.order_by(desc(PatientOutcome.measurement_date)).offset(offset).limit(limit).all()
        return [OutcomeResponse.from_orm(outcome) for outcome in outcomes]
    
    def update_outcome(self, outcome_id: UUID, outcome_data: OutcomeUpdate) -> Optional[OutcomeResponse]:
        """Update an existing outcome"""
        outcome = self.db.query(PatientOutcome).filter(
            PatientOutcome.outcome_id == outcome_id
        ).first()
        
        if not outcome:
            return None
        
        update_data = outcome_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(outcome, field, value)
        
        self.db.commit()
        self.db.refresh(outcome)
        return OutcomeResponse.from_orm(outcome)
    
    def delete_outcome(self, outcome_id: UUID) -> bool:
        """Delete an outcome"""
        outcome = self.db.query(PatientOutcome).filter(
            PatientOutcome.outcome_id == outcome_id
        ).first()
        
        if not outcome:
            return False
        
        self.db.delete(outcome)
        self.db.commit()
        return True
    
    def get_outcome_statistics(self, patient_id: UUID, outcome_type: str) -> dict:
        """Get statistics for a specific outcome type for a patient"""
        outcomes = self.db.query(PatientOutcome).filter(
            PatientOutcome.patient_id == patient_id,
            PatientOutcome.outcome_type == outcome_type
        ).order_by(PatientOutcome.measurement_date).all()
        
        if not outcomes:
            return {
                "count": 0,
                "average": 0,
                "min": 0,
                "max": 0,
                "trend": "no_data"
            }
        
        values = [float(outcome.outcome_value) for outcome in outcomes]
        
        # Calculate trend (simple linear trend)
        if len(values) >= 2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg + 0.5:
                trend = "improving"
            elif second_avg < first_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "count": len(values),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "trend": trend,
            "latest_value": values[-1] if values else None
        } 