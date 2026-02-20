import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class PatientOutcome(Base):
    """Patient outcome measurement model"""
    
    __tablename__ = "patient_outcomes"
    
    outcome_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    measurement_date = Column(Date, nullable=False)
    outcome_type = Column(String(50), nullable=False, index=True)
    outcome_value = Column(Numeric(precision=10, scale=2), nullable=False)
    measurement_method = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PatientOutcome(outcome_id={self.outcome_id}, patient_id={self.patient_id}, outcome_type={self.outcome_type})>" 